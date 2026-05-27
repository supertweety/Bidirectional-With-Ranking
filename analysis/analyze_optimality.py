"""Absolute-number analysis: expanded nodes vs path length vs theoretical
minimum. The theoretical minimum #expansions to discover a path of length L
is ~L (each node on the found path must be expanded, split across the two
frontiers). expanded/L is the distance-from-optimal-efficiency factor.
"""
import numpy as np
from game.getData import get_data
from search.AI_Bidirectional import BidirectionalF2FSearch

N = 400
states = get_data(False)

expanded, path_len, ratio = [], [], []
for i in range(N):
    s = BidirectionalF2FSearch(states[i], None)  # baseline, no NN
    path = s.search(max_iterations=10000)
    if not path:
        continue
    exp = s.first_meeting_iter if s.first_meeting_iter is not None else s.iteration
    L = len(path)
    expanded.append(exp)
    path_len.append(L)
    ratio.append(exp / max(L, 1))

expanded = np.array(expanded)
path_len = np.array(path_len)
ratio = np.array(ratio)

print(f"Baseline (no NN), {len(expanded)} solved puzzles of {N}:\n")
print(f"{'metric':<28}{'mean':>10}{'median':>10}")
print(f"{'expanded nodes':<28}{expanded.mean():>10.1f}{np.median(expanded):>10.1f}")
print(f"{'path length (theo. min)':<28}{path_len.mean():>10.1f}{np.median(path_len):>10.1f}")
print(f"{'expanded / path_length':<28}{ratio.mean():>10.2f}{np.median(ratio):>10.2f}")
print()
print(f"  → baseline expands ~{np.median(ratio):.1f}× the path length (median)")
