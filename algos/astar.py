
from AnchorSearch import SearchFrontier


class AStar(SearchFrontier):
    """
    Implements the A* search algorithm for Sokoban.
    """
    def __init__(self, start_state, isBackward, nn=None):
        super().__init__(start_state, isBackward, nn)