from typing import Tuple
import copy
import numpy as np
class SokobanGame:
    def __init__(self, puzzle, isBackward = False):
        self.puzzle = puzzle
        self.target = list(zip(*(np.where(puzzle == 2))))
        # if isBackward:
        #     self.actions = [self.Up(self.target), self.Down(self.target), self.Left(self.target),self.Right(self.target), self.PullUp(self.target), self.PullDown(self.target), self.PullLeft(self.target), self.PullRight(self.target)]
        # else:
        #     self.actions = [self.Up(self.target), self.Down(self.target), self.Left(self.target),self.Right(self.target)]
        self.action_map = {
            (-1, 0): self.Up(self.target, isBackward),      # Up
            (1, 0): self.Down(self.target, isBackward),    # Down
            (0, -1): self.Left(self.target, isBackward),   # Left (Note: Changed from (0, 1) in your original logic)
            (0, 1): self.Right(self.target, isBackward),   # Right (Note: Changed from (0, -1) in your original logic)
        }
        self.isBackward = isBackward
        # If backward search, add the 'Pull' actions to the map
        if isBackward:
            # Note: Assuming Pull actions use the same directional tuples for their 'move' logic
            self.pull_action_map = {
                (-1, 0): self.PullUp(self.target),    # PullUp (Overrides Up)
                (1, 0): self.PullDown(self.target),  # PullDown (Overrides Down)
                (0, -1): self.PullLeft(self.target), # PullLeft (Overrides Left)
                (0, 1): self.PullRight(self.target), # PullRight (Overrides Right)
            }
        # if isBidrectional == True:
        #     self.back_targets = list(zip(*(np.where(puzzle == 4))))
        #     self.backwardPuzzle = self.initializeBackwardPuzzle(self.puzzle)

    @staticmethod
    def initializeBackwardPuzzle(board):
        new_copy = copy.deepcopy(board)
        for row in range(len(board)):
            for col in range(len(board[0])):
                if new_copy[row][col] == 4:
                    new_copy[row][col] = 2
                elif new_copy[row][col] == 2:
                    new_copy[row][col] = 4
        return new_copy
    
    def hasDeadlock(self, board):
        ### To Be Implemented
        box_locs = list(zip(*(np.where(board == 4))))
        surround = [(-1, 0), (0, 1), (1,0), (0,-1) ]
        rows, cols = board.shape

        for r, c in box_locs:
            blocked_count = 0
            
            # Check the four surrounding positions
            for dr, dc in surround:
                nr, nc = r + dr, c + dc  # New row, new column
                
                # Check for boundary issues (this box is next to the board edge)
                if not (0 <= nr < rows and 0 <= nc < cols):
                    # Count the boundary as a blocked side
                    blocked_count += 1
                    continue
                
                # Check if the surrounding cell contains an immovable object:
                # Wall (1), or another Box/Box-on-Target (4 or 5)
                if board[nr, nc] == 0:
                    blocked_count += 1
            
            # If 3 or 4 sides are blocked, it's a three-sided trap.
            if blocked_count >= 3:
                # We found a box that is trapped
                return True
                
        # No boxes were found to be trapped on three or more sides
        return False

    @staticmethod
    def decodeMap(map_string):
        int_list = [int(digit) for digit in map_string]
            
        # 2. Convert the list to a 1D NumPy array
        flat_numpy_array = np.array(int_list)
        
        # 3. Reshape the 1D array back to the original dimensions
        decoded_map = flat_numpy_array.reshape((10,10))
        # You might want to convert it back to a standard Python list of lists 
        # if that was the original format:
        # decoded_map_list = decoded_map.tolist()
        return decoded_map
    def encodeMap(self,map):
        numpyMap = np.array(map)
        flattened = np.ravel(numpyMap)
        board_string = "".join(str(x) for x in flattened)
        return board_string
    def isGoal(self, board):
        boxes = list(zip(*(np.where(board == 4))))
        for box_loc in boxes:
            if box_loc not in self.target:
                return False
        return True
    def evaluateBoard(self, board):
        block_locations = list(zip(*np.where(board == 4)))
        distances = 0
        for loc_tuple in block_locations:
            min_distance_for_box = float('inf')
            for targ_tuple in self.target:
                distance = abs(targ_tuple[0] - loc_tuple[0]) + abs(targ_tuple[1] - loc_tuple[1])
                if distance < min_distance_for_box:
                    min_distance_for_box = distance
            distances += min_distance_for_box
        return distances
        # min_
        # for block in 


    def availableStates(self, current_location: Tuple[int,int]):
        # do a grid of surrounding 8 check
        surrounding_blocks = [(-1, 0), (0, 1), (1,0), (0,-1) ]
        availableTuples = []
        for block in surrounding_blocks:
            new_tuple = (current_location[0] + block[0], current_location[1] + block[1])
            new_loc = self.puzzle[new_tuple[0]][new_tuple[1]]
            if new_loc != 0:
                availableTuples.append(block)
        tuple_map = []
        for tuple in availableTuples:
            tuple_map.append((tuple, self.action_map[tuple]))
        if self.isBackward:
            for tuple in surrounding_blocks:
                tuple_map.append((tuple, self.pull_action_map[tuple]))
        return tuple_map
    def getPlayerLocation(self, board):
        loc = np.where(board == 3)
        player_location: Tuple[int,int] = (loc[0][0], loc[1][0])
        return player_location
    def move(self,current_loc, direction_and_movement):
        movement = direction_and_movement[1]
        #action_object = self.action_map.get(direction)
        
        # 3. Execute the move
        new_board = movement.moveAndUpdateBoard(current_loc, self.puzzle)
    
        if new_board is None:
            return None
        return new_board

    class Move:
        def __init__(self, target_locations, isBackward):
            self.target_locations = target_locations
            self.isBackward = isBackward
            pass
        def canMove(self, currentLocation, board): #bool to see if moving in that direction is possible
            raise NotImplementedError
        def moveAndUpdateBoard(self, currentLocation, board) -> Tuple[list[list[int]], Tuple[int,int]]: # tuple is for if a target was hit, otherwise just None
            raise NotImplementedError
        def resetTargetSpots(self,board):
            for target_loc in self.target_locations:
                if board[target_loc[0]][target_loc[1]] != 4 and board[target_loc[0]][target_loc[1]] != 3:
                    board[target_loc[0]][target_loc[1]]= 2
            return board
    class Up(Move):
        def canMove(self, currentLocation, board) -> bool:
            new_loc = (currentLocation[0] -1, currentLocation[1])
            res = True
            if board[new_loc[0]][new_loc[1]] == 0: # if wall is there
                res = False
            ## next check if its a block
            if self.isBackward and board[new_loc[0]][new_loc[1]] == 4:
                return False
            if board[new_loc[0]][new_loc[1]] == 4 and (board[new_loc[0] -1][new_loc[1]] == 0 or board[new_loc[0] - 1][new_loc[1]] == 4):
                res = False # because it means it wants to move the block but the block cant move and cant move two blocks at once
            return res
        def moveAndUpdateBoard(self, currentLocation, board):
            if not self.canMove(currentLocation, board):
                return None
            new_loc = (currentLocation[0] - 1, currentLocation[1])
            new_copy = copy.deepcopy(board)
            res = None
            if new_copy[new_loc[0]][new_loc[1]] == 1 or new_copy[new_loc[0]][new_loc[1]] == 2: # open space
                new_copy[new_loc[0]][new_loc[1]] = 3
                new_copy[currentLocation[0]][currentLocation[1]] = 1
                res =  new_copy
            ## next check if its a block
            if new_copy[new_loc[0]][new_loc[1]] == 4:
                new_copy[new_loc[0] - 1][new_loc[1]] = 4
                new_copy[new_loc[0]][new_loc[1]] = 3
                new_copy[currentLocation[0]][currentLocation[1]] = 1
                res = new_copy
            res = self.resetTargetSpots(new_copy)
            return res

    class Down(Move):
        def canMove(self, currentLocation, board):
            new_loc = (currentLocation[0] + 1, currentLocation[1])
            res = True
            if board[new_loc[0]][new_loc[1]] == 0: # if wall is there
                res =  False
            ## next check if its a block
            if self.isBackward and board[new_loc[0]][new_loc[1]] == 4:
                return False
            if board[new_loc[0]][new_loc[1]] == 4 and (board[new_loc[0] + 1][new_loc[1]] == 0 or board[new_loc[0] + 1][new_loc[1]] == 4):
                res =  False # because it means it wants to move the block but the block cant move and cant move two blocks at once
            return res
        def moveAndUpdateBoard(self, currentLocation, board):
            if not self.canMove(currentLocation, board):
                return None
            new_loc = (currentLocation[0] + 1, currentLocation[1])
            new_copy = copy.deepcopy(board)
            res = None
            if board[new_loc[0]][new_loc[1]] == 1 or new_copy[new_loc[0]][new_loc[1]] == 2: # open space
                new_copy[new_loc[0]][new_loc[1]] = 3
                new_copy[currentLocation[0]][currentLocation[1]] = 1
                res = new_copy
            ## next check if its a block
            if board[new_loc[0]][new_loc[1]] == 4:
                new_copy[new_loc[0] + 1][new_loc[1]] = 4
                new_copy[new_loc[0]][new_loc[1]] = 3
                new_copy[currentLocation[0]][currentLocation[1]] = 1
                res = new_copy
            res = self.resetTargetSpots(new_copy)
            return res
    class Left(Move):
        def canMove(self, currentLocation, board):
            new_loc = (currentLocation[0], currentLocation[1] -1)
            res = True
            if board[new_loc[0]][new_loc[1]] == 0: # if wall is there
                res = False
            ## next check if its a block
            if self.isBackward and board[new_loc[0]][new_loc[1]] == 4:
                return False
            if board[new_loc[0]][new_loc[1]] == 4 and (board[new_loc[0]][new_loc[1] - 1] == 0 or board[new_loc[0]][new_loc[1] - 1] == 4):
                res = False # because it means it wants to move the block but the block cant move and cant move two blocks at once
            return res
        def moveAndUpdateBoard(self, currentLocation, board):
            if not self.canMove(currentLocation, board):
                return None
            new_loc = (currentLocation[0], currentLocation[1] - 1)
            new_copy = copy.deepcopy(board)
            res = None
            if board[new_loc[0]][new_loc[1]] == 1 or new_copy[new_loc[0]][new_loc[1]] == 2: # open space
                new_copy[new_loc[0]][new_loc[1]] = 3
                new_copy[currentLocation[0]][currentLocation[1]] = 1
                res =  new_copy
            ## next check if its a block
            if board[new_loc[0]][new_loc[1]] == 4:
                new_copy[new_loc[0]][new_loc[1] - 1] = 4
                new_copy[new_loc[0]][new_loc[1]] = 3
                new_copy[currentLocation[0]][currentLocation[1]] = 1
                res = new_copy
            res = self.resetTargetSpots(new_copy)
            return res

    class Right(Move):
        def canMove(self, currentLocation, board):
            new_loc = (currentLocation[0], currentLocation[1] + 1)
            res = True
            if board[new_loc[0]][new_loc[1]] == 0: # if wall is there
                res = False
            ## next check if its a block
            if self.isBackward and board[new_loc[0]][new_loc[1]] == 4:
                return False
            if board[new_loc[0]][new_loc[1]] == 4 and (board[new_loc[0]][new_loc[1] + 1] == 0 or board[new_loc[0]][new_loc[1] + 1] == 4):
                res = False # because it means it wants to move the block but the block cant move and cant move two blocks at once
            return res
        def moveAndUpdateBoard(self, currentLocation, board):

            if not self.canMove(currentLocation, board):
                return None
            new_loc = (currentLocation[0], currentLocation[1] + 1)
            new_copy = copy.deepcopy(board)
            res = None
            if board[new_loc[0]][new_loc[1]] == 1 or new_copy[new_loc[0]][new_loc[1]] == 2: # open space

                new_copy[new_loc[0]][new_loc[1]] = 3
                new_copy[currentLocation[0]][currentLocation[1]] = 1
                res = new_copy
            ## next check if its a block
            if board[new_loc[0]][new_loc[1]] == 4:
                new_copy[new_loc[0]][new_loc[1] + 1] = 4
                new_copy[new_loc[0]][new_loc[1]] = 3
                new_copy[currentLocation[0]][currentLocation[1]] = 1
                res = new_copy
            res = self.resetTargetSpots(new_copy)
            return res
    class Pull:
        def __init__(self, target_locations):
            self.target_locations = target_locations
            pass
        def canPull(self, currentLocation, board): #bool to see if moving in that direction is possible
            raise NotImplementedError
        def moveAndUpdateBoard(self, currentLocation, board) -> Tuple[list[list[int]], Tuple[int,int]]: # tuple is for if a target was hit, otherwise just None
            raise NotImplementedError
        def resetTargetSpots(self,board):
            for target_loc in self.target_locations:
                if board[target_loc[0]][target_loc[1]] != 4 and board[target_loc[0]][target_loc[1]] != 3:
                    board[target_loc[0]][target_loc[1]]= 2
            return board
        
    class PullUp(Pull):
        def canPull(self, currentLocation, board): #bool to see if moving in that direction is possible
            ## first check if there is a block to pull
            res = True
            block_location = (currentLocation[0] + 1, currentLocation[1])

            if board[block_location[0]][block_location[1]] != 4:
                res =  False
            ## next see if there is a block above us
            move_to_spot = (currentLocation[0] - 1, currentLocation[1])
            if board[move_to_spot[0]][move_to_spot[1]] != 1 and board[move_to_spot[0]][move_to_spot[1]] != 2:
                res = False
            return res
            
        def moveAndUpdateBoard(self, currentLocation, board) -> Tuple[list[list[int]], Tuple[int,int]]: # tuple is for if a target was hit, otherwise just None
            if not self.canPull(currentLocation, board):
                return None
            new_copy = copy.deepcopy(board)
            new_loc = (currentLocation[0] - 1, currentLocation[1])
            
            new_copy[new_loc[0]][new_loc[1]] = 3
            new_copy[currentLocation[0]][currentLocation[1]] = 4
            new_copy[currentLocation[0] + 1][currentLocation[1]] = 1
            new_copy = self.resetTargetSpots(new_copy)
            return new_copy
        
    class PullDown(Pull):
        def canPull(self, currentLocation, board): #bool to see if moving in that direction is possible
            block_location = (currentLocation[0] - 1, currentLocation[1])
            if board[block_location[0]][block_location[1]] != 4:
                return False
            move_to_spot = (currentLocation[0] + 1, currentLocation[1])
            if board[move_to_spot[0]][move_to_spot[1]] != 1 and board[move_to_spot[0]][move_to_spot[1]] != 2:
                return False
            return True
        
        def moveAndUpdateBoard(self, currentLocation, board) -> Tuple[list[list[int]], Tuple[int,int]]: # tuple is for if a target was hit, otherwise just None
            if not self.canPull(currentLocation, board):
                return None
            new_copy = copy.deepcopy(board)
            new_loc = (currentLocation[0] + 1, currentLocation[1])

            new_copy[new_loc[0]][new_loc[1]] = 3
            new_copy[currentLocation[0]][currentLocation[1]] = 4
            new_copy[currentLocation[0] - 1][currentLocation[1]] = 1
            new_copy = self.resetTargetSpots(new_copy)
            return new_copy
        
    class PullLeft(Pull):
        def canPull(self, currentLocation, board): #bool to see if moving in that direction is possible
            block_location = (currentLocation[0], currentLocation[1] +1)
            if board[block_location[0]][block_location[1]] != 4:
                return False
            move_to_spot = (currentLocation[0], currentLocation[1] - 1)
            if board[move_to_spot[0]][move_to_spot[1]] != 1 and board[move_to_spot[0]][move_to_spot[1]] != 2:
                return False
            return True
        
        def moveAndUpdateBoard(self, currentLocation, board) -> Tuple[list[list[int]], Tuple[int,int]]: # tuple is for if a target was hit, otherwise just None
            if not self.canPull(currentLocation, board):
                return None
            new_copy = copy.deepcopy(board)
            new_loc = (currentLocation[0], currentLocation[1] - 1)

            new_copy[new_loc[0]][new_loc[1]] = 3
            new_copy[currentLocation[0]][currentLocation[1]] = 4
            new_copy[currentLocation[0]][currentLocation[1] + 1] = 1
            new_copy = self.resetTargetSpots(new_copy)
            return new_copy
        
    class PullRight(Pull):
        def canPull(self, currentLocation, board): #bool to see if moving in that direction is possible
            block_location = (currentLocation[0], currentLocation[1] -1)
            if board[block_location[0]][block_location[1]] != 4:
                return False
            move_to_spot = (currentLocation[0], currentLocation[1] + 1)
            if board[move_to_spot[0]][move_to_spot[1]] != 1 and board[move_to_spot[0]][move_to_spot[1]] != 2:
                return False
            return True
        
        def moveAndUpdateBoard(self, currentLocation, board) -> Tuple[list[list[int]], Tuple[int,int]]: # tuple is for if a target was hit, otherwise just None
            if not self.canPull(currentLocation, board):
                return None
            new_copy = copy.deepcopy(board)
            new_loc = (currentLocation[0], currentLocation[1] + 1)
            new_copy[new_loc[0]][new_loc[1]] = 3
            new_copy[currentLocation[0]][currentLocation[1]] = 4
            new_copy[currentLocation[0]][currentLocation[1] - 1] = 1
            new_copy = self.resetTargetSpots(new_copy)
            return new_copy