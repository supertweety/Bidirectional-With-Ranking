"""Diagnostic driver: train the heuristic NN with the replay buffer and
compare predicted distances to true cost-to-go before vs. after training.

Also reports periodic validation MAE during training and whether the NN
makes the search faster once it is wired into _f_score_nn.
"""
import time
import numpy as np
import torch

from getData import get_data
from nn import SmallCNN
from AI_Bidirectional import BidirectionalF2FSearch
from replay_buffer import ReplayBuffer

torch.manual_seed(0)
np.random.seed(0)

N_TRAIN = 400
N_EVAL = 5
MAX_ITERS = 10000
BATCH_SIZE = 64
UPDATES_PER_SOLVE = 16
WARMUP = 200
VAL_EVERY = 50  # report validation MAE every N solves

states = get_data(False)
print(f"Loaded {len(states)} puzzles. Using {N_TRAIN} train + {N_EVAL} eval.")
train_states = states[:N_TRAIN]
eval_states = states[N_TRAIN:N_TRAIN + N_EVAL]


def solve(puzzle, nn_model=None):
    s = BidirectionalF2FSearch(puzzle, nn_model)
    t0 = time.time()
    path = s.search(max_iterations=MAX_ITERS)
    return path, s, time.time() - t0


def decode_path(path, game):
    return [game.decodeMap(h) for h in path]


def predict_h(nn_model, decoded_states, target, goal_map):
    out = []
    with torch.no_grad():
        for st in decoded_states:
            out.append(float(nn_model(st, target, goal_map).item()))
    return out


# ── Phase 0: ground truth on eval set (no NN) ───────────────────────────
print("\n[Phase 0] Solving eval puzzles WITHOUT NN for ground truth …")
eval_ground = []
baseline_iters, baseline_times = [], []
for i, p in enumerate(eval_states):
    path, s, dt = solve(p, None)
    if not path:
        print(f"  eval[{i}] FAILED")
        continue
    decoded = decode_path(path, s.forward_game)
    L = len(decoded)
    true_costs = [L - j - 1 for j in range(L)]
    eval_ground.append((decoded, s.forward_game.target,
                        s.forward_game.goal_map, true_costs))
    baseline_iters.append(s.iteration)
    baseline_times.append(dt)
    print(f"  eval[{i}] path={L:>3d}  iters={s.iteration:>6d}  t={dt:.2f}s")


def report_predictions(nn_model, tag, verbose=True, n_pair_samples=30):
    """Evaluate the pairwise heuristic on the held-out eval paths.

    Two metrics:
      (a) state -> goal (state at index i vs. final state on the same path)
      (b) random pairs (s_i, s_j) with true distance |i - j|
    """
    rng = np.random.default_rng(123)
    se_errs, se_preds, se_true = [], [], []
    pp_errs, pp_preds, pp_true = [], [], []
    if verbose:
        print(f"\n  ─ {tag} (state→goal sample) ─")
        print(f"  {'puzzle':>6}  {'idx':>3}  {'pred':>7}  {'true':>5}  {'err':>6}")
    for i, (decoded, tgt, gm, true_costs) in enumerate(eval_ground):
        L = len(decoded)
        # (a) state -> goal: second arg is the final state on this path
        goal_state = decoded[-1]
        preds = predict_h(nn_model, decoded, tgt, goal_state)
        errs = [abs(p - t) for p, t in zip(preds, true_costs)]
        se_errs.extend(errs); se_preds.extend(preds); se_true.extend(true_costs)
        if verbose:
            idxs = np.linspace(0, L - 1, min(5, L)).astype(int)
            for j in idxs:
                print(f"  {i:>6d}  {j:>3d}  {preds[j]:>7.2f}  "
                      f"{true_costs[j]:>5d}  {errs[j]:>6.2f}")

        # (b) random pair distances on this path
        for _ in range(n_pair_samples):
            a = int(rng.integers(0, L))
            b = int(rng.integers(0, L))
            if a == b:
                continue
            true_d = abs(a - b)
            with torch.no_grad():
                pred_d = float(nn_model(decoded[a], tgt, decoded[b]).item())
            pp_preds.append(pred_d); pp_true.append(true_d)
            pp_errs.append(abs(pred_d - true_d))

    def stats(preds, true_, errs):
        if not errs:
            return float('nan'), 0.0, 0.0
        mae = float(np.mean(errs))
        std = float(np.std(preds))
        if len(preds) > 1 and std > 1e-6:
            corr = float(np.corrcoef(preds, true_)[0, 1])
        else:
            corr = 0.0
        return mae, std, corr

    mae_se, std_se, corr_se = stats(se_preds, se_true, se_errs)
    mae_pp, std_pp, corr_pp = stats(pp_preds, pp_true, pp_errs)
    if verbose:
        print(f"  state->goal: MAE={mae_se:.3f}  std={std_se:.3f}  "
              f"corr={corr_se:+.3f}  (n={len(se_errs)})")
        print(f"  pair      : MAE={mae_pp:.3f}  std={std_pp:.3f}  "
              f"corr={corr_pp:+.3f}  (n={len(pp_errs)})")
    return mae_se, std_se, corr_se, mae_pp, std_pp, corr_pp


# ── Phase 1: pre-training predictions ───────────────────────────────────
nn_model = SmallCNN(32)
print(f"Model params: {sum(p.numel() for p in nn_model.parameters()):,}")
criterion, optimizer = nn_model.initialize_cr_opt()
device = "cuda:0" if torch.cuda.is_available() else "cpu"
print(f"\n[Phase 1] Pre-training predictions (device={device})")
pre = report_predictions(nn_model, "PRE-TRAIN")


# ── Phase 2: train with replay buffer + periodic val MAE ────────────────
print(f"\n[Phase 2] Training (batch={BATCH_SIZE}, K={UPDATES_PER_SOLVE}, "
      f"warmup={WARMUP}, puzzles={N_TRAIN}) …")
buffer = ReplayBuffer(capacity=20000)
loss_hist = []
val_mae_hist = []
total_updates = 0
t_train0 = time.time()
for i, p in enumerate(train_states):
    path, s, dt = solve(p, None)
    if not path:
        continue
    decoded = decode_path(path, s.forward_game)
    buffer.add_pairs_from_path(
        decoded,
        s.forward_game.target,
        num_random_pairs=2 * len(decoded),
        symmetric=True,
        include_endpoints=True,
    )

    losses = []
    if len(buffer) >= WARMUP:
        for _ in range(UPDATES_PER_SOLVE):
            samples = buffer.sample(BATCH_SIZE)
            optimizer.zero_grad()
            preds, tars = [], []
            for st, tgt, gm, ctg in samples:
                preds.append(nn_model(st, tgt, gm))
                tars.append(ctg)
            pt = torch.stack(preds).squeeze()
            tt = torch.tensor(tars, dtype=torch.float32)
            if pt.ndim == 0:
                pt = pt.unsqueeze(0); tt = tt.unsqueeze(0)
            loss = criterion(pt, tt)
            loss.backward()
            optimizer.step()
            losses.append(float(loss.item()))
            total_updates += 1
        loss_hist.extend(losses)

    if (i + 1) % VAL_EVERY == 0 and total_updates > 0:
        mae_se, std_se, corr_se, mae_pp, std_pp, corr_pp = report_predictions(
            nn_model, f"step {i+1}", verbose=False)
        val_mae_hist.append((i + 1, mae_se, corr_se, mae_pp, corr_pp))
        recent_loss = np.mean(loss_hist[-50:]) if loss_hist else float('nan')
        print(f"  solve {i+1:>3d}/{N_TRAIN}  buf={len(buffer):>5d}  "
              f"updates={total_updates:>4d}  loss={recent_loss:>6.2f}  "
              f"s→g MAE={mae_se:>5.2f} corr={corr_se:>+.2f}  "
              f"pair MAE={mae_pp:>5.2f} corr={corr_pp:>+.2f}")

print(f"  train wall time: {time.time()-t_train0:.1f}s  "
      f"total gradient steps: {total_updates}")

if len(loss_hist) >= 4:
    half = len(loss_hist) // 2
    print(f"  loss: first-half mean={np.mean(loss_hist[:half]):.3f}  "
          f"second-half mean={np.mean(loss_hist[half:]):.3f}")


# ── Phase 3: post-training predictions ──────────────────────────────────
print("\n[Phase 3] Post-training predictions")
post = report_predictions(nn_model, "POST-TRAIN")
mae_se_b, std_se_b, corr_se_b, mae_pp_b, std_pp_b, corr_pp_b = pre
mae_se_a, std_se_a, corr_se_a, mae_pp_a, std_pp_a, corr_pp_a = post
print(f"\n  state→goal  MAE  : before={mae_se_b:.3f}  after={mae_se_a:.3f}")
print(f"  state→goal  corr : before={corr_se_b:+.3f}  after={corr_se_a:+.3f}")
print(f"  pair        MAE  : before={mae_pp_b:.3f}  after={mae_pp_a:.3f}")
print(f"  pair        corr : before={corr_pp_b:+.3f}  after={corr_pp_a:+.3f}")
if val_mae_hist:
    print("  val trajectory (step: s→g MAE/corr | pair MAE/corr):")
    for i, mse, cse, mpp, cpp in val_mae_hist:
        print(f"    @{i:>3d}  s→g {mse:>5.2f}/{cse:+.2f}   "
              f"pair {mpp:>5.2f}/{cpp:+.2f}")


# ── Phase 4: re-solve eval puzzles WITH trained NN ──────────────────────
print("\n[Phase 4] Re-solving eval puzzles WITH trained NN")
print(f"  {'puzzle':>6}  {'base_iters':>10}  {'nn_iters':>9}  "
      f"{'base_t':>7}  {'nn_t':>7}")
trained_iters, trained_times = [], []
for i, p in enumerate(eval_states):
    path, s, dt = solve(p, nn_model)
    it = s.iteration
    trained_iters.append(it)
    trained_times.append(dt)
    print(f"  {i:>6d}  {baseline_iters[i]:>10d}  {it:>9d}  "
          f"{baseline_times[i]:>7.2f}  {dt:>7.2f}")

if baseline_iters and trained_iters:
    print(f"\n  mean iters  baseline: {np.mean(baseline_iters):.1f}  "
          f"trained: {np.mean(trained_iters):.1f}")
    print(f"  mean time   baseline: {np.mean(baseline_times):.2f}s  "
          f"trained: {np.mean(trained_times):.2f}s")
