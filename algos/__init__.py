
from algos import TTBS
from algos.AnchorSearch import AnchorSearch
from algos.astar import AStar


ALGO_REGISTRY = {
    "anchor": AnchorSearch,
    "astar": AStar,
    "ttbs": TTBS
}