import numpy as np
import heapq
from typing import Tuple, Dict, List, Optional, Set
from SokobanGame import SokobanGame

class BidirectionalF2FSearch:
    """
    Implementation of Top-to-Top Bidirectional Search (TTBS) for Sokoban.
    Based on the IJCAI 2020 paper by Kuroiwa and Fukunaga.
    """
    def __init__(self, puzzle: np.ndarray, game_name: str = "Sokoban"):
        self.game_name = game_name
        self.puzzle = puzzle
        
        # Initialize games
        self.forward_game = SokobanGame(puzzle, isBackward=False)
        backward_puzzle = self.forward_game.initializeBackwardPuzzle(puzzle)
        self.backward_game = SokobanGame(backward_puzzle, isBackward=True)
        
        # Search structures
        # elements: list of (f_score, g_score, state_hash)
        self.open_f = []
        self.open_b = []
        
        # Maps to store g-values and parent pointers
        self.g_f: Dict[str, int] = {}
        self.g_b: Dict[str, int] = {}
        self.parent_f: Dict[str, Optional[str]] = {}
        self.parent_b: Dict[str, Optional[str]] = {}
        
        # To handle re-evaluation (TTBS specifics)
        # Store the 'target' node used for the last f-score calculation
        self.last_target_f: Dict[str, str] = {}
        self.last_target_b: Dict[str, str] = {}
        
        # Best solution found so far
        self.U = float('inf')
        self.meeting_point: Optional[str] = None
        
        self.iteration = 0

    def get_best_node(self, open_list: List, g_map: Dict[str, int]) -> Optional[str]:
        """Returns the node with the minimum g-value in the open list."""
        if not open_list:
            return None
        # In TTBS, the "top" node is often the one with the min h or g.
        # The paper mentions using the node with the minimum g-value as the target.
        best_node = None
        min_g = float('inf')
        for _, g, node_hash in open_list:
            if g < min_g:
                min_g = g
                best_node = node_hash
        return best_node

    def get_f_score(self, node_hash: str, g_val: int, target_node_hash: str, game: SokobanGame) -> float:
        """Calculates the front-to-front f-score: f(s) = g(s) + h(s, d*)."""
        node_map = game.decodeMap(node_hash)
        target_map = game.decodeMap(target_node_hash)
        # We need to flip the target_map if it's from the opposite search to align box/target positions
        # However, SokobanGame.evaluateBoard(s, d*) already handles comparison if both are just box/player states.
        # But wait, backward_game uses targets as boxes and vice versa.
        # Let's align them: the heuristic should estimate moves to reach the configuration of the other frontier.
        h_val = game.evaluateBoard(node_map, target_map)
        return g_val + h_val

    def init_search(self):
        """Initializes the search frontiers."""
        start_hash = self.forward_game.encodeMap(self.puzzle)
        goal_hash = self.backward_game.encodeMap(self.backward_game.puzzle)
        
        self.g_f[start_hash] = 0
        self.g_b[goal_hash] = 0
        self.parent_f[start_hash] = None
        self.parent_b[goal_hash] = None
        
        # Initial f-score uses the other side's initial node as target
        f_start = self.get_f_score(start_hash, 0, goal_hash, self.forward_game)
        f_goal = self.get_f_score(goal_hash, 0, start_hash, self.backward_game)
        
        heapq.heappush(self.open_f, (f_start, 0, start_hash))
        heapq.heappush(self.open_b, (f_goal, 0, goal_hash))
        
        self.last_target_f[start_hash] = goal_hash
        self.last_target_b[goal_hash] = start_hash

    def step(self) -> Tuple[bool, Optional[List[str]]]:
        """Performs one expansion step (alternating between forward and backward)."""
        if not self.open_f or not self.open_b:
            return False, None
            
        # Select side with smaller open list
        if len(self.open_f) <= len(self.open_b):
            is_forward = True
            open_list = self.open_f
            opp_open = self.open_b
            g_map = self.g_f
            opp_g_map = self.g_b
            parent_map = self.parent_f
            last_target_map = self.last_target_f
            game = self.forward_game
            opp_game = self.backward_game
        else:
            is_forward = False
            open_list = self.open_b
            opp_open = self.open_f
            g_map = self.g_b
            opp_g_map = self.g_f
            parent_map = self.parent_b
            last_target_map = self.last_target_b
            game = self.backward_game
            opp_game = self.forward_game
            
        # TTBS Re-evaluation Mechanism
        best_opp_node = self.get_best_node(opp_open, opp_g_map)
        if not best_opp_node:
            return False, None

        while True:
            if not open_list:
                return False, None
                
            f, g, u_hash = heapq.heappop(open_list)
            
            # If U is already better than the current f, we might prune, but TTBS is satisficing
            # In satisficing search, we usually just continue until they meet.
            
            # Re-evaluation check
            if last_target_map.get(u_hash) != best_opp_node:
                new_f = self.get_f_score(u_hash, g, best_opp_node, game)
                last_target_map[u_hash] = best_opp_node
                heapq.heappush(open_list, (new_f, g, u_hash))
                # Update best_opp_node in case pop/push cycle is needed? 
                # No, just re-insert and pick the new min.
                f, g, u_hash = heapq.heappop(open_list)
                if last_target_map.get(u_hash) != best_opp_node:
                    # Still not matching? Re-push and try again
                    heapq.heappush(open_list, (f, g, u_hash))
                    continue
            
            # If we reached here, u_hash is evaluated against the current best_opp_node
            break
            
        # Expand u
        u_map = game.decodeMap(u_hash)
        player_loc = game.getPlayerLocation(u_map)
        
        for direction, action in game.availableStates(player_loc):
            v_map = action.moveAndUpdateBoard(player_loc, u_map)
            if v_map is None:
                continue
                
            v_hash = game.encodeMap(v_map)
            new_g = g + 1
            
            if v_hash not in g_map or new_g < g_map[v_hash]:
                g_map[v_hash] = new_g
                parent_map[v_hash] = u_hash
                
                # Check for intersection
                # Note: In bidirectional Sokoban, states are aligned if their box positions match.
                # The backward_game's box positions correspond to the forward_game's target fulfillment.
                # However, SokobanGame uses 4 for boxes on both.
                # We need to flip back if we want to compare with the other side.
                # Actually, the implementation of compareGames/getStateHash should be consistent.
                v_hash_for_opp = v_hash
                if is_forward:
                    # forward uses 4 for boxes. backward uses 4 for boxes (which are targets in forward).
                    # To compare, we need to know if the configuration of boxes in forward matches the reconfiguration of boxes in backward.
                    # SokobanGame.flipGame helps align them.
                    v_flipped = game.flipGame(v_map)
                    v_hash_for_opp = game.encodeMap(v_flipped)
                else:
                    # backward to forward align
                    v_flipped = game.flipGame(v_map)
                    v_hash_for_opp = game.encodeMap(v_flipped)

                if v_hash_for_opp in opp_g_map:
                    # Intersection found!
                    current_cost = new_g + opp_g_map[v_hash_for_opp]
                    if current_cost < self.U:
                        self.U = current_cost
                        self.meeting_point = v_hash if is_forward else v_hash_for_opp
                        # For simplicity, return on first intersection in satisficing search
                        return True, self.reconstruct_path()
                
                # Push to open list
                v_f = self.get_f_score(v_hash, new_g, best_opp_node, game)
                heapq.heappush(open_list, (v_f, new_g, v_hash))
                last_target_map[v_hash] = best_opp_node
                
        self.iteration += 1
        return False, None

    def reconstruct_path(self) -> List[str]:
        """Reconstructs the path from start to goal through the meeting point."""
        if not self.meeting_point:
            return []
            
        # Path from start to meeting point (forward)
        path_f = []
        curr = self.meeting_point
        # If the meeting point was found by backward search, it's already flipped for comparison.
        # But meeting_point logic above might need care.
        # Let's ensure meeting_point is always a forward_game hash.
        
        # If meeting point is in g_f, we can trace back
        if self.meeting_point in self.g_f:
            curr = self.meeting_point
            while curr is not None:
                path_f.append(curr)
                curr = self.parent_f.get(curr)
            path_f.reverse()
        else:
            # Should not happen with current logic
            pass
            
        # Path from meeting point to goal (backward)
        path_b = []
        # We need the flipped version of the meeting point in backward_game's space
        meeting_flipped = self.backward_game.encodeMap(self.forward_game.flipGame(self.forward_game.decodeMap(self.meeting_point)))
        curr = meeting_flipped
        while curr is not None:
            # flip back to forward space for the final path
            decoded = self.backward_game.decodeMap(curr)
            flipped_back = self.forward_game.flipGame(decoded)
            path_b.append(self.forward_game.encodeMap(flipped_back))
            curr = self.parent_b.get(curr)
            
        # Merge (path_b[0] is meeting point, same as path_f[-1])
        return path_f + path_b[1:]

    def search(self, max_iterations: int = 10000) -> Optional[List[str]]:
        """Executes the full search."""
        self.init_search()
        for _ in range(max_iterations):
            success, path = self.step()
            if success:
                return path
        return None
