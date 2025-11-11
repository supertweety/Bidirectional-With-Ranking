from astar import Astar
from getData import get_data
import numpy as np
import copy 


def experiment_with_astar():
    states = get_data()
    only_one_state = states[0]
    for puzzle in [only_one_state]:
        aStar = Astar(puzzle, "Sokoban")

    aStar.trainAstar()
def initialize():
    states = get_data()
    only_one_state = states[0]
    aStar = Astar(only_one_state, "Sokoban")
    return ([only_one_state], )
def step(astar: Astar):
    astar.stepAstar()

if __name__ == "__main__":
    experiment_with_astar()
