

from AnchorSearch import SearchFrontier


class TTBS(SearchFrontier):
    """
    Implements the TTBS algorithm for bidirectional search in Sokoban.
    """
    def __init__(self, start_state, isBackward, nn=None):
        super().__init__(start_state, isBackward, nn)