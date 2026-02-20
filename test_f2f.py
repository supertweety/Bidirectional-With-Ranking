import numpy as np
from AI_Bidirectional import BidirectionalF2FSearch
from SokobanGame import SokobanGame
import time

def load_simple_puzzle():
    # A very simple 5x5 Sokoban puzzle (walls=0, floor=1, goal=2, player=3, box=4)
    # 0 0 0 0 0
    # 0 1 2 1 0
    # 0 3 4 1 0
    # 0 1 1 1 0
    # 0 0 0 0 0
    # Resized to 10x10 as expected by SokobanGame
    puzzle = np.zeros((10, 10), dtype=int)
    puzzle[1:4, 1:4] = [
        [1, 2, 1],
        [3, 4, 1],
        [1, 1, 1]
    ]
    return puzzle

def test_f2f():
    puzzle = load_simple_puzzle()
    print("Initial Puzzle:")
    print(puzzle)
    
    searcher = BidirectionalF2FSearch(puzzle)
    start_time = time.time()
    path = searcher.search(max_iterations=1000)
    end_time = time.time()
    
    if path:
        print(f"Success! Found path of length {len(path)} in {end_time - start_time:.4f} seconds.")
        print(f"Iterations: {searcher.iteration}")
        # print("Path:")
        # for step in path:
        #     print(SokobanGame.decodeMap(step))
    else:
        print("Failed to find a path.")

if __name__ == "__main__":
    test_f2f()
