from typing import Tuple
import copy
import numpy as np
class SokobanGame:
    def __init__(self, puzzle, isBidrectional = False):
        self.puzzle = puzzle
        self.target = list(zip(*(np.where(puzzle == 2))))
        self.actions = [self.Up(self.target), self.Down(self.target), self.Left(self.target),self.Right(self.target)]
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
        return availableTuples
    def getPlayerLocation(self, board):
        loc = np.where(board == 3)
        player_location: Tuple[int,int] = (loc[0][0], loc[1][0])
        return player_location
    def move(self,current_loc, direction):
        new_board, cleared_spot = None, None
        #print(direction)
        if direction == (-1, 0): # up
             
            new_board, cleared_spot = self.actions[0].moveAndUpdateBoard(current_loc, self.puzzle)
        elif direction == (1,0): # down
              
             new_board, cleared_spot = self.actions[1].moveAndUpdateBoard(current_loc, self.puzzle)
        elif direction == (0,1): # right
              
             new_board, cleared_spot = self.actions[3].moveAndUpdateBoard(current_loc, self.puzzle)
        else: # left
             
             new_board, cleared_spot = self.actions[2].moveAndUpdateBoard(current_loc, self.puzzle)
    
        if new_board is None:
            return None
        if cleared_spot != None:
            self.target = self.target[self.target != cleared_spot]
        return new_board

    class Move:
        def __init__(self, target_locations):
            self.target_locations = target_locations
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
            if board[new_loc[0]][new_loc[1]] == 4 and (board[new_loc[0] -1][new_loc[1]] == 0 or board[new_loc[0] - 1][new_loc[1]] == 4):
                res = False # because it means it wants to move the block but the block cant move and cant move two blocks at once
            return res
        def moveAndUpdateBoard(self, currentLocation, board):
            if not self.canMove(currentLocation, board):
                
                return [None, None]
            new_loc = (currentLocation[0] - 1, currentLocation[1])
            new_copy = copy.deepcopy(board)
            res = None
            if new_copy[new_loc[0]][new_loc[1]] == 1 or new_copy[new_loc[0]][new_loc[1]] == 2: # open space
                new_copy[new_loc[0]][new_loc[1]] = 3
                new_copy[currentLocation[0]][currentLocation[1]] = 1
                res =  [new_copy,None]
            ## next check if its a block
            if new_copy[new_loc[0]][new_loc[1]] == 4:
                if new_copy[new_loc[0] - 1][new_loc[1]] == 3:
                    new_copy[new_loc[0] - 1][new_loc[1]] = 1
                    new_copy[new_loc[0]][new_loc[1]] = 3
                    new_copy[currentLocation[0]][currentLocation[1]] = 1
                    res = [new_copy, (new_loc[0] - 1,new_loc[1])]
                else:
                    new_copy[new_loc[0] - 1][new_loc[1]] = 4
                    new_copy[new_loc[0]][new_loc[1]] = 3
                    new_copy[currentLocation[0]][currentLocation[1]] = 1
                    res = [new_copy, None]
            res[0] = self.resetTargetSpots(new_copy)
            return res

    class Down(Move):
        def canMove(self, currentLocation, board):
            new_loc = (currentLocation[0] + 1, currentLocation[1])
            res = True
            if board[new_loc[0]][new_loc[1]] == 0: # if wall is there
                res =  False
            ## next check if its a block
            if board[new_loc[0]][new_loc[1]] == 4 and (board[new_loc[0] + 1][new_loc[1]] == 0 or board[new_loc[0] + 1][new_loc[1]] == 4):
                res =  False # because it means it wants to move the block but the block cant move and cant move two blocks at once
            return res
        def moveAndUpdateBoard(self, currentLocation, board):
            if not self.canMove(currentLocation, board):
                return [None, None]
            new_loc = (currentLocation[0] + 1, currentLocation[1])
            new_copy = copy.deepcopy(board)
            res = None
            if board[new_loc[0]][new_loc[1]] == 1 or new_copy[new_loc[0]][new_loc[1]] == 2: # open space
                new_copy[new_loc[0]][new_loc[1]] = 3
                new_copy[currentLocation[0]][currentLocation[1]] = 1
                res = [new_copy,None]
            ## next check if its a block
            if board[new_loc[0]][new_loc[1]] == 4:
                if new_copy[new_loc[0] + 1][new_loc[1]] == 3:
                    new_copy[new_loc[0] + 1][new_loc[1]] = 1
                    new_copy[new_loc[0]][new_loc[1]] = 3
                    new_copy[currentLocation[0]][currentLocation[1]] = 1
                    res = [new_copy, (new_loc[0] + 1,new_loc[1])]
                else:
                    new_copy[new_loc[0] + 1][new_loc[1]] = 4
                    new_copy[new_loc[0]][new_loc[1]] = 3
                    new_copy[currentLocation[0]][currentLocation[1]] = 1
                    res = [new_copy, None]
            res[0] = self.resetTargetSpots(new_copy)
            return res
    class Left(Move):
        def canMove(self, currentLocation, board):
            new_loc = (currentLocation[0], currentLocation[1] -1)
            res = True
            if board[new_loc[0]][new_loc[1]] == 0: # if wall is there
                res = False
            ## next check if its a block
            if board[new_loc[0]][new_loc[1]] == 4 and (board[new_loc[0]][new_loc[1] - 1] == 0 or board[new_loc[0]][new_loc[1] - 1] == 4):
                res = False # because it means it wants to move the block but the block cant move and cant move two blocks at once
            return res
        def moveAndUpdateBoard(self, currentLocation, board):
            if not self.canMove(currentLocation, board):
                return [None, None]
            new_loc = (currentLocation[0], currentLocation[1] - 1)
            new_copy = copy.deepcopy(board)
            res = None
            if board[new_loc[0]][new_loc[1]] == 1 or new_copy[new_loc[0]][new_loc[1]] == 2: # open space
                new_copy[new_loc[0]][new_loc[1]] = 3
                new_copy[currentLocation[0]][currentLocation[1]] = 1
                res =  [new_copy,None]
            ## next check if its a block
            if board[new_loc[0]][new_loc[1]] == 4:
                if new_copy[new_loc[0]][new_loc[1] - 1] == 3:
                    new_copy[new_loc[0]][new_loc[1] - 1] = 1
                    new_copy[new_loc[0]][new_loc[1]] = 3
                    new_copy[currentLocation[0]][currentLocation[1]] = 1
                    res = [new_copy, (new_loc[0],new_loc[1] - 1)]
                else:
                    new_copy[new_loc[0]][new_loc[1] - 1] = 4
                    new_copy[new_loc[0]][new_loc[1]] = 3
                    new_copy[currentLocation[0]][currentLocation[1]] = 1
                    res = [new_copy, None]
            res[0] = self.resetTargetSpots(new_copy)
            return res

    class Right(Move):
        def canMove(self, currentLocation, board):
            new_loc = (currentLocation[0], currentLocation[1] + 1)
            res = True
            if board[new_loc[0]][new_loc[1]] == 0: # if wall is there
                res = False
            ## next check if its a block
            if board[new_loc[0]][new_loc[1]] == 4 and (board[new_loc[0]][new_loc[1] + 1] == 0 or board[new_loc[0]][new_loc[1] + 1] == 4):
                res = False # because it means it wants to move the block but the block cant move and cant move two blocks at once
            return res
        def moveAndUpdateBoard(self, currentLocation, board):

            if not self.canMove(currentLocation, board):
                return [None, None]
            new_loc = (currentLocation[0], currentLocation[1] + 1)
            new_copy = copy.deepcopy(board)
            res = None
            if board[new_loc[0]][new_loc[1]] == 1 or new_copy[new_loc[0]][new_loc[1]] == 2: # open space

                new_copy[new_loc[0]][new_loc[1]] = 3
                new_copy[currentLocation[0]][currentLocation[1]] = 1
                res = [new_copy,None]
            ## next check if its a block
            if board[new_loc[0]][new_loc[1]] == 4:
                if new_copy[new_loc[0]][new_loc[1] + 1] == 3:
                    new_copy[new_loc[0]][new_loc[1] + 1] = 1
                    new_copy[new_loc[0]][new_loc[1]] = 3
                    new_copy[currentLocation[0]][currentLocation[1]] = 1
                    res = [new_copy, (new_loc[0],new_loc[1] + 1)]
                else:
                    new_copy[new_loc[0]][new_loc[1] + 1] = 4
                    new_copy[new_loc[0]][new_loc[1]] = 3
                    new_copy[currentLocation[0]][currentLocation[1]] = 1
                    res = [new_copy, None]
            res[0] = self.resetTargetSpots(new_copy)
            return res