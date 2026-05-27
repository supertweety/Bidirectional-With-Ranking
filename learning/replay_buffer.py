import os
import pickle
import random
from collections import deque

import numpy as np


class ReplayBuffer:
    """Flat transition buffer for heuristic learning.

    Each entry is (state, target, other_state, distance, puzzle_id) where
    ``puzzle_id`` is an optional tag identifying which puzzle this pair was
    mined from (used for re-mining). ``sample()`` strips the tag, so training
    code sees 4-element tuples.
    """

    def __init__(self, capacity=50000):
        self.buffer = deque(maxlen=capacity)

    def add(self, state, target, other, distance, puzzle_id=None):
        self.buffer.append((
            np.array(state, copy=True),
            target,
            np.array(other, copy=True),
            float(distance),
            puzzle_id,
        ))

    def add_pairs_from_path(self, decoded_path, target,
                            num_random_pairs=None, symmetric=True,
                            include_endpoints=True, rng=None,
                            puzzle_id=None):
        """Pair-based labeling: store (s_i, s_j, |i-j|) tuples from a path.

        - ``num_random_pairs`` random (i, j) pairs are sampled.
        - Pairs involving the start (i=0) and goal (i=L-1) are always
          included when ``include_endpoints`` is True.
        - If ``symmetric``, each pair is added in both orderings.
        - All entries are tagged with ``puzzle_id``.
        Returns the number of entries added.
        """
        rng = rng or random
        L = len(decoded_path)
        if L < 2:
            return 0
        if num_random_pairs is None:
            num_random_pairs = 2 * L

        pairs = set()
        if include_endpoints:
            for k in range(1, L):
                pairs.add((0, k))
            for k in range(0, L - 1):
                pairs.add((k, L - 1))
        for _ in range(num_random_pairs):
            i, j = rng.randrange(L), rng.randrange(L)
            if i != j:
                pairs.add((min(i, j), max(i, j)))

        added = 0
        for i, j in pairs:
            dist = j - i
            self.add(decoded_path[i], target, decoded_path[j], dist, puzzle_id)
            added += 1
            if symmetric:
                self.add(decoded_path[j], target, decoded_path[i], dist, puzzle_id)
                added += 1
        return added

    def sample(self, batch_size):
        """Return a random minibatch WITHOUT the puzzle_id tag."""
        n = min(batch_size, len(self.buffer))
        return [e[:4] for e in random.sample(self.buffer, n)]

    def remove_by_tag(self, puzzle_id):
        """Drop every entry tagged with ``puzzle_id``. Returns count dropped."""
        kept = [e for e in self.buffer if e[-1] != puzzle_id]
        dropped = len(self.buffer) - len(kept)
        if dropped:
            self.buffer = deque(kept, maxlen=self.buffer.maxlen)
        return dropped

    def oldest_tag(self):
        """puzzle_id of the front (oldest) entry, or None if empty."""
        return self.buffer[0][-1] if self.buffer else None

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
