"""Online learning curve for a learned TTBS heuristic.

For each puzzle n = 1, 2, ..., N (in order):
  1. Solve puzzle n with the current NN as the front-to-front heuristic.
     This is a held-out evaluation point — the model has never seen it.
  2. Mine (state_i, state_j, |i-j|) training pairs from the solved path
     and add them to the replay buffer (tagged with puzzle_id n).
  3. Run K minibatch gradient updates on the buffer (MSE + margin-ranking).
  4. Once the buffer is saturated, periodically re-mine an old puzzle with
     the now-better model to refresh stale labels.

Training can run on CPU (default) or MPS; search-time inference always runs
on a CPU twin (batch-1 inference is GPU-hostile). Compared against a no-NN
baseline pass over the same puzzles.

Key env knobs (all optional):
  N_TOTAL, MODEL_CHANNELS, BATCH_SIZE, UPDATES_PER_SOLVE, BUFFER_CAP,
  LOSS={mse,rank,both}, REG_LOSS={mae,mse}, RANK_MARGIN, USE_G={yes,no},
  TRAIN_DEVICE={cpu,mps}, K_REMINE, REMINE_RANDOM_FRAC
"""
import os
import random
import time
from collections import deque

import numpy as np
import torch

from game.getData import get_data
from learning.nn import SmallCNN
from search.AI_Bidirectional import BidirectionalF2FSearch
from learning.replay_buffer import ReplayBuffer

torch.manual_seed(0)
np.random.seed(0)
_rng = random.Random(0)

# ── Configuration ────────────────────────────────────────────────────────
N_TOTAL = int(os.environ.get("N_TOTAL", "1000"))
MAX_ITERS = 10000
MODEL_CHANNELS = int(os.environ.get("MODEL_CHANNELS", "32"))
BATCH_SIZE = int(os.environ.get("BATCH_SIZE", "64"))
UPDATES_PER_SOLVE = int(os.environ.get("UPDATES_PER_SOLVE", "8"))
WARMUP = 200
BUFFER_CAP = int(os.environ.get("BUFFER_CAP", "20000"))
WINDOW = 25
LOG_EVERY = 25
MILESTONE = 100

# Loss: "mse" (regression only), "rank" (margin-ranking only), or "both".
LOSS = os.environ.get("LOSS", "both").lower()
# Regression-term flavor for "mse"/"both": "mae" (L1) or "mse" (L2).
REG_LOSS = os.environ.get("REG_LOSS", "mse").lower()
RANK_MARGIN = float(os.environ.get("RANK_MARGIN", "1.0"))
# If "no", drop g from the f-score (GBFS instead of A*-style).
USE_G = os.environ.get("USE_G", "yes").lower() == "yes"
# Training device. Search always runs on a CPU twin regardless.
TRAIN_DEVICE = os.environ.get("TRAIN_DEVICE", "cpu").lower()
# Periodic re-mining: re-solve & re-mine 1 old puzzle every K_REMINE solves
# once the buffer is saturated. 0 disables.
K_REMINE = int(os.environ.get("K_REMINE", "5"))
REMINE_RANDOM_FRAC = float(os.environ.get("REMINE_RANDOM_FRAC", "0.1"))


# ── Search + training helpers ─────────────────────────────────────────────
def run_search(puzzle, nn_model=None):
    s = BidirectionalF2FSearch(puzzle, nn_model)
    s.use_g_in_f = USE_G
    t0 = time.time()
    path = s.search(max_iterations=MAX_ITERS)
    return path, s, time.time() - t0


def solve_and_collect(puzzle, puzzle_id, nn_model, buffer, rng):
    """Solve a puzzle and add its solved-path pairs to the buffer (tagged).

    Returns (path, search, dt, n_pairs_added).
    """
    path, s, dt = run_search(puzzle, nn_model)
    n_pairs = 0
    if path:
        decoded = [s.forward_game.decodeMap(h) for h in path]
        n_pairs = buffer.add_pairs_from_path(
            decoded, s.forward_game.target,
            num_random_pairs=2 * len(decoded),
            symmetric=True, include_endpoints=True,
            puzzle_id=puzzle_id, rng=rng,
        )
    return path, s, dt, n_pairs


def rolling_mean(xs, w):
    return float(np.mean(xs[-w:])) if xs else float("nan")


# ── Load puzzles ───────────────────────────────────────────────────────────
puzzles = get_data(False)[:N_TOTAL]
print(f"Using {N_TOTAL} puzzles from the dataset.")


# ── Phase A: baseline (no NN) ──────────────────────────────────────────────
print("\n[Baseline] Solving all puzzles without NN for reference …")
base_iters, base_times = [], []
t0 = time.time()
for p in puzzles:
    _, s, dt = run_search(p, None)
    base_iters.append(s.iteration)
    base_times.append(dt)
print(f"  done in {time.time()-t0:.1f}s  mean iters={np.mean(base_iters):.1f}  "
      f"median iters={np.median(base_iters):.1f}")


# ── Model(s): training model on TRAIN_DEVICE, CPU twin for search ──────────
print(f"\n[Online] batch={BATCH_SIZE} K={UPDATES_PER_SOLVE} warmup={WARMUP} "
      f"buffer={BUFFER_CAP} loss={LOSS} reg_loss={REG_LOSS} use_g={USE_G} "
      f"train_device={TRAIN_DEVICE} K_remine={K_REMINE}")
torch.manual_seed(100)
train_model = SmallCNN(MODEL_CHANNELS)
if TRAIN_DEVICE != "cpu":
    train_model = train_model.to(TRAIN_DEVICE)
criterion, optimizer = train_model.initialize_cr_opt(loss_type=REG_LOSS)
torch.manual_seed(0)
print(f"  params={sum(p.numel() for p in train_model.parameters()):,}")

# Search runs on a CPU twin (same object if training is already CPU).
if TRAIN_DEVICE == "cpu":
    search_model = train_model
else:
    search_model = SmallCNN(MODEL_CHANNELS)


def sync_search_model():
    if TRAIN_DEVICE != "cpu":
        search_model.load_state_dict(
            {k: v.cpu() for k, v in train_model.state_dict().items()})


sync_search_model()
buffer = ReplayBuffer(capacity=BUFFER_CAP)


# ── Phase B: online solve-then-train ───────────────────────────────────────
online_iters, online_times = [], []
loss_hist = []
total_updates = 0
nn_active_from = None
first_saturated_n = None
seen = deque()
remine_count = 0

t_online0 = time.time()
for n, p in enumerate(puzzles):
    use_nn = len(buffer) >= WARMUP
    if use_nn and nn_active_from is None:
        nn_active_from = n
        print(f"  >>> buffer warm at puzzle {n}; NN goes live <<<")

    path, s, dt, n_pairs = solve_and_collect(
        p, n, search_model if use_nn else None, buffer, _rng)
    solve_iters = s.first_meeting_iter if s.first_meeting_iter is not None else s.iteration
    online_iters.append(solve_iters)
    online_times.append(dt)
    if n_pairs > 0:
        seen.append(n)
    if first_saturated_n is None and len(buffer) == buffer.buffer.maxlen:
        first_saturated_n = n

    # Training.
    if len(buffer) >= WARMUP:
        for _ in range(UPDATES_PER_SOLVE):
            samples = buffer.sample(BATCH_SIZE)
            optimizer.zero_grad()
            states, targets, others, tars = [], [], [], []
            for st, tgt, gm, ctg in samples:
                states.append(st); targets.append(tgt); others.append(gm)
                tars.append(ctg)
            pt = train_model.forward_batch(states, targets, others)
            tt = torch.tensor(tars, dtype=torch.float32, device=pt.device)
            if pt.ndim == 0:
                pt = pt.unsqueeze(0); tt = tt.unsqueeze(0)

            mse = criterion(pt, tt)
            rank_loss = torch.tensor(0.0, device=pt.device)
            half = pt.shape[0] // 2
            if half >= 1 and LOSS in ("rank", "both"):
                a, b = pt[:half], pt[half:2 * half]
                y = torch.sign(tt[:half] - tt[half:2 * half])
                mask = y != 0
                if mask.any():
                    rank_loss = torch.nn.functional.margin_ranking_loss(
                        a[mask], b[mask], y[mask], margin=RANK_MARGIN)
            if LOSS == "mse":
                loss = mse
            elif LOSS == "rank":
                loss = rank_loss
            else:
                loss = 0.5 * mse + 0.5 * rank_loss

            loss.backward()
            optimizer.step()
            loss_hist.append(float(loss.item()))
            total_updates += 1
        sync_search_model()

    # Periodic re-mining of an old puzzle with the current model.
    if (K_REMINE > 0 and use_nn and first_saturated_n is not None
            and (n - first_saturated_n) > 0
            and (n - first_saturated_n) % K_REMINE == 0 and seen):
        if _rng.random() < REMINE_RANDOM_FRAC and len(seen) > 1:
            idx = _rng.randrange(len(seen)); old_idx = seen[idx]; del seen[idx]
        else:
            old_idx = seen.popleft()
        buffer.remove_by_tag(old_idx)
        solve_and_collect(puzzles[old_idx], old_idx, search_model, buffer, _rng)
        seen.append(old_idx)
        remine_count += 1

    if (n + 1) % LOG_EVERY == 0:
        b_it = rolling_mean(base_iters[:n + 1], WINDOW)
        o_it = rolling_mean(online_iters, WINDOW)
        speed = b_it / o_it if o_it > 0 else float("nan")
        oldest = buffer.oldest_tag()
        age = (n - oldest) if oldest is not None else 0
        print(f"  n={n+1:>4d}  buf={len(buffer):>6d}  upd={total_updates:>5d}  "
              f"loss={rolling_mean(loss_hist, 50):>6.2f}  "
              f"solve_iters={solve_iters:>5d}  win{WINDOW}=x{speed:.2f}  "
              f"age={age:>4d} remined={remine_count:>4d}  "
              f"dt={dt:.2f}s {'NN' if use_nn else '--'}")

    if (n + 1) % MILESTONE == 0:
        sl = slice(n + 1 - MILESTONE, n + 1)
        bw, ow = base_iters[sl], online_iters[sl]
        bm, bmd = np.mean(bw), np.median(bw)
        om, omd = np.mean(ow), np.median(ow)
        if nn_active_from is not None and nn_active_from <= n:
            cb, co = base_iters[nn_active_from:n + 1], online_iters[nn_active_from:n + 1]
            cum_m = np.mean(cb) / max(np.mean(co), 1)
            cum_md = np.median(cb) / max(np.median(co), 1)
        else:
            cum_m = cum_md = float("nan")
        print(f"\n    ── milestone n={n+1} (last {MILESTONE}) ──")
        print(f"    iters   baseline mean={bm:>7.1f} median={bmd:>7.1f}")
        print(f"    iters   online   mean={om:>7.1f} median={omd:>7.1f}")
        print(f"    speedup x_mean={bm/max(om,1):>5.2f}  x_median={bmd/max(omd,1):>5.2f}")
        print(f"    cumulative since NN live: x_mean={cum_m:.2f}  x_median={cum_md:.2f}\n")

t_online_total = time.time() - t_online0


# ── Summary ─────────────────────────────────────────────────────────────────
print(f"\n[Done] online wall time: {t_online_total:.1f}s  "
      f"updates={total_updates}  remined={remine_count}")
if nn_active_from is not None:
    b = np.array(base_iters[nn_active_from:])
    o = np.array(online_iters[nn_active_from:])
    print(f"\nFrom puzzle {nn_active_from} onward ({len(b)} puzzles):")
    print(f"  mean   solve_iters baseline={b.mean():.1f} online={o.mean():.1f} "
          f"speedup x{b.mean()/max(o.mean(),1):.2f}")
    print(f"  median solve_iters baseline={np.median(b):.1f} online={np.median(o):.1f} "
          f"speedup x{np.median(b)/max(np.median(o),1):.2f}")

print(f"\nLearning curve (window={MILESTONE}, mean and median):")
print(f"  {'puzzle':>6}  {'base_mn':>8} {'base_md':>8}  {'on_mn':>7} {'on_md':>7}"
      f"  {'x_mn':>5}  {'x_md':>5}")
for end in range(MILESTONE, N_TOTAL + 1, MILESTONE):
    bw = base_iters[end - MILESTONE:end]
    ow = online_iters[end - MILESTONE:end]
    bm, bmd = np.mean(bw), np.median(bw)
    om, omd = np.mean(ow), np.median(ow)
    mark = "  <- NN live" if (nn_active_from is not None
                              and end - MILESTONE < nn_active_from <= end) else ""
    print(f"  {end:>6d}  {bm:>8.1f} {bmd:>8.1f}  {om:>7.1f} {omd:>7.1f}  "
          f"x{bm/max(om,1):>4.2f}  x{bmd/max(omd,1):>4.2f}{mark}")
