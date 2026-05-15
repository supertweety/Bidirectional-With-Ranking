"""Reproduce the online run up to puzzle 24, then solve puzzle 25 with
the trained NN and print the full solution path.
"""
import numpy as np
import torch

from getData import get_data
from nn import SmallCNN
from AI_Bidirectional import BidirectionalF2FSearch
from replay_buffer import ReplayBuffer

# Match online_run.py exactly
torch.manual_seed(0)
np.random.seed(0)

BATCH_SIZE = 64
UPDATES_PER_SOLVE = 8
WARMUP = 200
MAX_ITERS = 10000

states = get_data(False)

nn_model = SmallCNN(32)
criterion, optimizer = nn_model.initialize_cr_opt()
buffer = ReplayBuffer(capacity=20000)


def solve(puzzle, nn_model=None):
    s = BidirectionalF2FSearch(puzzle, nn_model)
    path = s.search(max_iterations=MAX_ITERS)
    return path, s


# Replay the online loop for puzzles 0..24 (same as online_run.py)
for n in range(25):
    use_nn = (len(buffer) >= WARMUP)
    path, s = solve(states[n], nn_model if use_nn else None)
    if path:
        decoded = [s.forward_game.decodeMap(h) for h in path]
        buffer.add_pairs_from_path(
            decoded, s.forward_game.target,
            num_random_pairs=2 * len(decoded),
            symmetric=True, include_endpoints=True,
        )
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

print(f"Buffer size after training on 0..24: {len(buffer)}")

# Now solve puzzle 25 WITH the trained NN
nn_path, nn_s = solve(states[25], nn_model)
print(f"Puzzle 25 with NN  : path_len={len(nn_path)}  iters={nn_s.iteration}")

# For reference, also solve without NN
base_path, base_s = solve(states[25], None)
print(f"Puzzle 25 baseline : path_len={len(base_path)}  iters={base_s.iteration}")

GLYPHS = {0: '#', 1: ' ', 2: '.', 3: 'P', 4: '$'}
def render(g):
    return '\n'.join(''.join(GLYPHS[int(v)] for v in row) for row in g)

decoded = [nn_s.forward_game.decodeMap(h) for h in nn_path]
print("\nLegend: # wall, . target, $ box, P player")
for i, g in enumerate(decoded):
    print(f"\nStep {i}:")
    print(render(g))
