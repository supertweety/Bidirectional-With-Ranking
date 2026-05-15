import os
import pickle
import random
from collections import deque

import numpy as np


class ReplayBuffer:
    """Flat transition buffer for heuristic learning.

    Each entry is (state, target_locations, goal_map, cost_to_go) where
    cost_to_go is the true remaining path length on a solved path.
    """

    def __init__(self, capacity=50000):
        self.buffer = deque(maxlen=capacity)

    def add(self, state, target, goal_map, cost_to_go):
        self.buffer.append((
            np.array(state, copy=True),
            target,
            np.array(goal_map, copy=True),
            float(cost_to_go),
        ))

    def add_path(self, decoded_path, target, goal_map):
        """Legacy single-goal labeling (state -> final goal)."""
        L = len(decoded_path)
        for i, state in enumerate(decoded_path):
            self.add(state, target, goal_map, L - i - 1)

    def add_pairs_from_path(self, decoded_path, target,
                            num_random_pairs=None, symmetric=True,
                            include_endpoints=True, rng=None):
        """Pair-based labeling: store (s_i, s_j, |i-j|) tuples.

        - ``num_random_pairs`` random (i, j) pairs are sampled.
        - All pairs that involve the start (i=0) and the goal (i=L-1) are
          always included when ``include_endpoints`` is True.
        - If ``symmetric``, each pair is added in both orderings.
        """
        import random as _random
        rng = rng or _random

        L = len(decoded_path)
        if L < 2:
            return 0
        if num_random_pairs is None:
            num_random_pairs = 2 * L

        pairs = set()

        # Endpoint pairs: every state paired with start and goal
        if include_endpoints:
            for k in range(1, L):
                pairs.add((0, k))
            for k in range(0, L - 1):
                pairs.add((k, L - 1))

        # Random interior pairs
        for _ in range(num_random_pairs):
            i = rng.randrange(L)
            j = rng.randrange(L)
            if i == j:
                continue
            pairs.add((min(i, j), max(i, j)))

        added = 0
        for i, j in pairs:
            dist = j - i
            self.add(decoded_path[i], target, decoded_path[j], dist)
            added += 1
            if symmetric:
                self.add(decoded_path[j], target, decoded_path[i], dist)
                added += 1
        return added

    def sample(self, batch_size):
        n = min(batch_size, len(self.buffer))
        return random.sample(self.buffer, n)

    def __len__(self):
        return len(self.buffer)

    def save(self, path):
        with open(path, "wb") as f:
            pickle.dump((list(self.buffer), self.buffer.maxlen), f)

    def load(self, path):
        if not os.path.exists(path):
            return False
        with open(path, "rb") as f:
            data, maxlen = pickle.load(f)
        self.buffer = deque(data, maxlen=maxlen)
        return True
