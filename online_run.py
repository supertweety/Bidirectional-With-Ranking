"""Online learning curve.

For each puzzle n = 1, 2, ..., N:
  1. Solve puzzle n using the CURRENT (already-trained-on-0..n-1) model.
     This is the held-out evaluation point — the model has never seen it.
  2. Add the solved path of n into the replay buffer (pair-based).
  3. Run K gradient steps on the buffer.

We compare the online iteration counts to a baseline pass that solves
the same puzzles in the same order with no NN. A rolling window over
recent puzzles shows whether the search is improving with experience.
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

N_TOTAL = 200
MAX_ITERS = 10000
BATCH_SIZE = 64
UPDATES_PER_SOLVE = 8
WARMUP = 200
WINDOW = 25  # rolling-window size for moving averages
LOG_EVERY = 10


def solve(puzzle, nn_model=None):
    s = BidirectionalF2FSearch(puzzle, nn_model)
    t0 = time.time()
    path = s.search(max_iterations=MAX_ITERS)
    return path, s, time.time() - t0


def decode_path(path, game):
    return [game.decodeMap(h) for h in path]


def rolling_mean(xs, w):
    if not xs:
        return float('nan')
    sub = xs[-w:]
    return float(np.mean(sub))


# ── Load puzzles ────────────────────────────────────────────────────────
all_states = get_data(False)
puzzles = all_states[:N_TOTAL]
print(f"Using {N_TOTAL} puzzles from the dataset.")


# ── Phase A: baseline pass (no NN) ──────────────────────────────────────
print("\n[Baseline] Solving all puzzles without NN to get reference …")
base_iters, base_times, base_paths_len = [], [], []
t0 = time.time()
for i, p in enumerate(puzzles):
    path, s, dt = solve(p, None)
    base_iters.append(s.iteration)
    base_times.append(dt)
    base_paths_len.append(len(path) if path else 0)
print(f"  done in {time.time()-t0:.1f}s  "
      f"mean iters={np.mean(base_iters):.1f}  "
      f"mean time={np.mean(base_times):.3f}s")


# ── Phase B: online learning + evaluation ───────────────────────────────
print(f"\n[Online] Solve-then-train, in order, "
      f"(batch={BATCH_SIZE}, K={UPDATES_PER_SOLVE}, warmup={WARMUP})")
nn_model = SmallCNN(32)
print(f"  Model params: {sum(p.numel() for p in nn_model.parameters()):,}")
criterion, optimizer = nn_model.initialize_cr_opt()
buffer = ReplayBuffer(capacity=20000)

online_iters, online_times = [], []
loss_hist = []
total_updates = 0
nn_active_from = None

t_online0 = time.time()
for n, p in enumerate(puzzles):
    # 1. Solve with current model (the buffer holds only puzzles 0..n-1).
    use_nn = (len(buffer) >= WARMUP)
    if use_nn and nn_active_from is None:
        nn_active_from = n
        print(f"  >>> buffer warm at puzzle {n}; NN goes live in search <<<")
    path, s, dt = solve(p, nn_model if use_nn else None)
    online_iters.append(s.iteration)
    online_times.append(dt)

    # 2. Add this puzzle's solved path to the buffer.
    if path:
        decoded = decode_path(path, s.forward_game)
        buffer.add_pairs_from_path(
            decoded, s.forward_game.target,
            num_random_pairs=2 * len(decoded),
            symmetric=True, include_endpoints=True,
        )

    # 3. Train K gradient steps (once warm).
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

    if (n + 1) % LOG_EVERY == 0:
        b_it = rolling_mean(base_iters[:n + 1], WINDOW)
        o_it = rolling_mean(online_iters, WINDOW)
        b_t = rolling_mean(base_times[:n + 1], WINDOW)
        o_t = rolling_mean(online_times, WINDOW)
        recent_loss = rolling_mean(loss_hist, 50)
        speed = (b_it / o_it) if o_it > 0 else float('nan')
        print(f"  n={n+1:>3d}  buf={len(buffer):>5d}  upd={total_updates:>4d}  "
              f"loss={recent_loss:>6.2f}  "
              f"win{WINDOW}_iters base={b_it:>7.1f} online={o_it:>7.1f} "
              f"(x{speed:.2f})  "
              f"time base={b_t:.2f}s online={o_t:.2f}s  "
              f"{'NN' if use_nn else '-- '}")

t_online_total = time.time() - t_online0


# ── Summary ─────────────────────────────────────────────────────────────
print(f"\n[Done] online wall time: {t_online_total:.1f}s  "
      f"total updates: {total_updates}")

# Compare iteration savings on the second half (after NN went live).
if nn_active_from is not None:
    sl = slice(nn_active_from, N_TOTAL)
    b_mean = float(np.mean([base_iters[i] for i in range(*sl.indices(N_TOTAL))]))
    o_mean = float(np.mean([online_iters[i] for i in range(*sl.indices(N_TOTAL))]))
    bt_mean = float(np.mean([base_times[i] for i in range(*sl.indices(N_TOTAL))]))
    ot_mean = float(np.mean([online_times[i] for i in range(*sl.indices(N_TOTAL))]))
    print(f"\nFrom puzzle {nn_active_from} onward "
          f"({N_TOTAL - nn_active_from} puzzles):")
    print(f"  mean iters  baseline={b_mean:.1f}   online={o_mean:.1f}   "
          f"speedup x{b_mean / max(o_mean, 1):.2f}")
    print(f"  mean time   baseline={bt_mean:.3f}s online={ot_mean:.3f}s")

# Print a small table of windowed means so the learning curve is visible.
print(f"\nLearning curve (rolling mean over window={WINDOW}):")
print(f"  {'puzzle':>6}  {'base_iters':>10}  {'online_iters':>12}  {'ratio':>6}")
for end in range(WINDOW, N_TOTAL + 1, WINDOW):
    b = float(np.mean(base_iters[end - WINDOW:end]))
    o = float(np.mean(online_iters[end - WINDOW:end]))
    ratio = b / max(o, 1)
    marker = ""
    if nn_active_from is not None and end - WINDOW < nn_active_from <= end:
        marker = "  <- NN went live in this window"
    print(f"  {end:>6d}  {b:>10.1f}  {o:>12.1f}  x{ratio:>5.2f}{marker}")
