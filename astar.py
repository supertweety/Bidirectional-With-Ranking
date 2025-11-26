import numpy as np
from typing import Tuple, Set, Optional
from SokobanGame import SokobanGame
import heapq
from to_categorical_tensor import to_categorical_tensor
from typing import Literal
from collections import OrderedDict
GameMap = {
    "Sokoban": SokobanGame
}

class Astar():
    def __init__(self, puzzle, game_name, isBackward = False, alpha=1, beta=1):
        self.dim = 10
        self.game = GameMap[game_name](puzzle, isBackward)
        self.alpha = alpha
        self.beta = beta
        self.puzzle = puzzle
        self.nn = None
        # Instance variables to hold the state of the A* search
        self.visited: Set[str] = set()
        self.parentMap = {}
        self.heap: PriorityQ = PriorityQ(self.game)
        self.current_loc: Optional[Tuple[int, int]] = None
        self.current_map: Optional[list] = None # Will store the map/puzzle corresponding to current_loc
        self.iteration = 0
        self.isBackward=isBackward
        self.best_gscore = {}
    def isComplete(self):
        return not (self.heap.length() > 0)
    def initAstar(self):
        """Initializes the A* search state."""
        self.visited.clear()
        #self.heap = type(self.heap)()  # Re-initialize the priority queue (assuming it has a clear-like method or can be re-instantiated)
        
        initial_encoded_map = self.game.encodeMap(self.game.puzzle)
        #self.visited.add(initial_encoded_map)
        
        self.current_loc = self.game.getPlayerLocation(self.puzzle)
        
        # Insert initial state: path 0, location, and the initial map
        self.heap.insert(0,0,(self.current_loc, self.game.puzzle))
        self.best_gscore[initial_encoded_map] = 0
        self.current_map = self.game.puzzle
        
        return self.current_map
    
    def stepAstar(self, score_calc_type: Literal["BaseHeuristic", "MM", "Neural", "MM_Neural"]="BaseHeuristic", updateObject=None) -> Tuple[bool, Optional[list]]:

        """
        Executes one step of the A* search algorithm.
        
        Returns:
            The new map/puzzle state after the step, or None if the search is complete 
            (goal reached or heap is empty).
        """
        if self.heap.length() == 0:
            return (False, self.game.puzzle, 0)

        ma = self.heap.getMin()

        current_map_score = ma[0][0]
        current_priority_score = ma[0][1]

        map_location_tuple = ma[1]
        encodedMap = self.game.encodeMap(map_location_tuple[1])
        self.visited.add(encodedMap)
        current_loc = map_location_tuple[0]

        current_puzzle_encoded = self.game.encodeMap(self.game.puzzle)

        # print(self.heap.length())
                
               # print("lol")
            ### then we know we are still in the depth search, otherwise we popped off a 
            ### a node higher up, meaning we got to backtrack
        self.game.puzzle = map_location_tuple[1]

        # if current_puzzle_encoded in self.parentMap and self.parentMap[recusedMap] != current_puzzle_encoded:
        #     # print("made it")

        #     while self.parentMap[recusedMap] != current_puzzle_encoded:
        #         parent_encoded_map = self.parentMap[recusedMap]
        #         multiple_maps_for_backwards.append(parent_encoded_map)
        #         current_puzzle_encoded = parent_encoded_map
                
        #print(current_loc) 
        directions = self.game.availableStates(current_loc)
        #print(ma[1])
        # current_rank_heap = []
        push_count = 0
        for direction_and_movement in directions:
            direction = direction_and_movement[0]
            new_map = self.game.move(current_loc, direction_and_movement)
            # print(self.game.hasDeadlock(new_map))
            if new_map is None  or self.game.encodeMap(new_map) in self.visited:
                ## we dont watn cycles
                # print("here")
                continue
            # if self.isBackward:
            #     print(self.game.encodeMap(new_map))
            #print("new _amp", new_map)
            #print("dir test", self.game.encodeMap(new_map), visited, self.game.encodeMap(new_map) in visited , new_map)
            # if self.game.encodeMap(new_map) in self.visited:
            #     continue
            if self.game.isGoal(new_map) == True:
                self.parentMap[self.game.encodeMap(new_map)] = encodedMap
                return (True, new_map, current_map_score + 1)
            
            score = 0
            aStarScore = 0
            match score_calc_type:
                case "BaseHeuristic":
                    score = self.game.evaluateBoard(new_map)
                    aStarScore = current_map_score + score+ 1
                case "MM":
                    score = self.game.evaluateBoard(new_map)
                    gScore = 0
                    # if self.game.encodeMap(new_map) in self.best_gscore:
                    #     gScore = self.best_gscore[self.game.encodeMap(new_map)]
                    # else:
                    gScore = current_map_score + 1
                    aStarScore = gScore + score
                case "Neural":
                    score = self.calculateNextAction(new_map, self.game.target, self.game.goal_map, self.nn)
                    aStarScore = current_map_score + score+ 1
                case "MM_Neural":
                    score = self.calculateNextAction(new_map, self.game.target, self.game.goal_map, self.nn)
                    gScore = 0
                    if self.game.encodeMap(new_map) in self.best_gscore:
                        gScore = self.best_gscore[self.game.encodeMap(new_map)]
                    else:
                        gScore = current_map_score + 1
                    aStarScore = gScore + score
            
            if score_calc_type == "BaseHeuristic" or score_calc_type == "Neural":
                if self.heap.contains(self.game.encodeMap(new_map)) == False:
                    self.parentMap[self.game.encodeMap(new_map)] = encodedMap
                    self.best_gscore[self.game.encodeMap(new_map)] = current_map_score + 1
                    self.heap.insert(current_map_score + 1, aStarScore, ((current_loc[0]+direction[0], current_loc[1] + direction[1]),new_map))
                elif self.game.encodeMap(new_map) in self.best_gscore and current_map_score + 1 < self.best_gscore[self.game.encodeMap(new_map)]:
                    self.best_gscore[self.game.encodeMap(new_map)] = current_map_score + 1
                    self.parentMap[self.game.encodeMap(new_map)] = encodedMap
            else:
                ## Do Meet in the middle guarenteed

                ## if the new child from this path is worse than the prior
                if (self.heap.contains(self.game.encodeMap(new_map)) == True or self.game.encodeMap(new_map) in self.visited) and self.best_gscore[self.game.encodeMap(new_map)] <= current_map_score + 1:
                    continue
                if (self.heap.contains(self.game.encodeMap(new_map)) == True or self.game.encodeMap(new_map) in self.visited):
                    if self.heap.contains(self.game.encodeMap(new_map)) == True:
                        self.heap.remove(self.game.encodeMap(new_map))
                    else:
                        self.visited.remove(self.game.encodeMap(new_map))
                self.best_gscore[self.game.encodeMap(new_map)] = current_map_score + 1
                self.parentMap[self.game.encodeMap(new_map)] = encodedMap
                self.heap.insert(current_map_score + 1, aStarScore, ((current_loc[0]+direction[0], current_loc[1] + direction[1]),new_map))
                # heapq.heappush(current_rank_heap,[aStarScore, push_count, ((current_loc[0]+direction[0], current_loc[1] + direction[1]),new_map)])
                # print("made it", updateObject["oppositeAstar"](self.game.encodeMap(new_map)))
                if updateObject["oppositeAstar"](self.game.encodeMap(new_map)) != (None, None):
                    _, opposite_game_gscore = updateObject["oppositeAstar"](self.game.encodeMap(new_map))
                    updateObject["U"] = min(updateObject["U"], opposite_game_gscore + self.best_gscore[self.game.encodeMap(new_map)])

                pass

            #calculateNextAction(current_forward_map, forwardAStar.game.target, forward_goal, nn)
            # if nn_heuristic != None:
            #     score = self.calculateNextAction(new_map, self.game.target, self.game.goal_map, nn_heuristic)
            # else:    
            
            
            #aStarScore = current_map_score + score+ 1
            #self.alpha * current_map_score + self.beta * score + 1
            # if len(current_rank_heap) == 0 or (len(current_rank_heap) > 0 and current_map_score < current_priority_score + 1):
           
                #print("score", score)
                #print((current_loc[0]+direction[0], current_loc[1] + direction[1]))
                #self.heap.insert(score,((current_loc[0]+direction[0], current_loc[1] + direction[1]),new_map))
            push_count += 1
        self.iteration += 1

        #print(encodedMap in self.parentMap)
        #self.parentMap[self.game.encodeMap(self.heap.peek()[1])] = encodedMap
        #print(multiple_maps_for_backwards)
        #self.game.puzzle = self.heap.peek()[1]
        #print(np.where(self.game.puzzle == 3))
        if score_calc_type == "BaseHeuristic" or score_calc_type == "Neural":
            return (False, self.game.puzzle, (current_priority_score, current_map_score))
        else: 
            return (False, self.game.puzzle, (current_priority_score, current_map_score, updateObject["U"]))
    #(False, self.heap.peek()[1])

    def calculatePriority(self) -> int:
        minimum_priority = float('inf')

        for f_value, g_value, _,  __ in self.heap.elements:
            # if self.game.isBackward == True:
                # print("g value", g_value)
            current_priority = max(2*g_value, f_value)
            minimum_priority = min(minimum_priority, current_priority)
        # print()
        # print()
        return minimum_priority
    
    def calculateOpenSetMaxorMinValue(self, value_type: Literal["g_value", "f_value"]="f_value" ,cutoff: Literal["max", "min"]="min"):
        value = float('inf')
        for f_value, g_value, counter,  element in self.heap.elements:
            current_value = f_value if value_type == "f_value" else g_value
            cutoff_fn = min if cutoff == "min" else max
            value = cutoff_fn(value, current_value)
        return value

    
    def checkGameInHeap(self, encoded_current_game):
        # print(encoded_current_game)
        flipped_game = self.game.flipGame(self.game.decodeMap(encoded_current_game))

        encoded_front_game = self.game.encodeMap(flipped_game)
        # print(encoded_front_game)
        # print()
        for encoded_game in self.heap.elements:
            # print(encoded_front_game)
            # print(encoded_game)
            # print()
            # print()
            if encoded_game == encoded_front_game:
                return encoded_game, self.heap.getCurrentGScore(encoded_game)
        return None, None

    def trainAstar(self):
        # visited = set()
        # visited.add(self.game.encodeMap(self.game.puzzle))
        # player_location: Tuple[int,int] = self.game.getPlayerLocation(self.puzzle)
        # current_loc = player_location
        # heap=PriorityQ()
        # heap.insert(0, (player_location,self.game.puzzle))
        # while heap.length() > 0:
        #     if self.game.isGoal():
        #         break
        #     #print(heap)
        #     ma = heap.getMin()
        #     current_loc = ma[0]
        #     self.game.puzzle = ma[1]
        #     #print(current_loc) 
        #     directions = self.game.availableStates(current_loc)
        #     for direction in directions:
        #         new_map = self.game.move(current_loc, direction)
        #         #print("new _amp", new_map)
        #         #print("dir test", self.game.encodeMap(new_map), visited, self.game.encodeMap(new_map) in visited , new_map)
        #         if self.game.encodeMap(new_map) in visited:
        #             continue
        #         if new_map is not None:
        #             score = self.game.evaluateBoard(new_map)
        #             #print("score", score)
        #             #print((current_loc[0]+direction[0], current_loc[1] + direction[1]))
        #             heap.insert(score,((current_loc[0]+direction[0], current_loc[1] + direction[1]),new_map))
        #     visited.add(self.game.encodeMap(ma[1]))
            
            

        pass       
    def calculateNextAction(self, state, box_tar, goal_state, nn):#Strips state

        box_on_T=[]

        current_box_locations =  list(zip(*(np.where(state == 4))))

        # for i in range(len(box_tar)):
        #     ## where the boxes are
        #     if state[box_tar[i][0]][box_tar[i][1]] == 4:
        #         box_on_T.append([box_tar[i][0],box_tar[i][1]])
        ## if completed
        if len(box_on_T) == len(box_tar):
            return 0

        old_state = state
        ## splits up the state into (10,10,5) for each x in 1-5 is a one hot encoding of each category (walls, player, ...)
        categorical_state = to_categorical_tensor(old_state,box_tar,10,10)
        
        categorical_goal_state = to_categorical_tensor(goal_state, box_tar, 10, 10)

        val = nn.model.predict([categorical_state.reshape(1,10,10,5),categorical_goal_state.reshape(1,10,10,5)], verbose=0)[1][0][0]
        return val
    
    def reconstructSuccessfulPath(self, final_puzzle):
        current_game = self.game.encodeMap(final_puzzle)
        path = [current_game]
        encoded_inital_state = self.game.encodeMap(self.puzzle)
        visit = []
        while current_game != encoded_inital_state:
            if current_game in visit:
                print("cycle")
                visit.append(current_game)
                return visit
            res = self.parentMap[current_game]
            path.append(res)
            visit.append(current_game)
            current_game = res
            
        print("done")
        return path
    
    def getBestGScore(self, encoded_map):
        return self.best_gscore[encoded_map]
    
    def inOpenSet(self, encodedMap):
        return self.checkGameInHeap(encodedMap)
    
    def create_one_hot(self, key_states, box_tar, goal_state):
        X_Train = []
        Y_Train = []
        for k in key_states:
            X_Train.append(to_categorical_tensor(k,box_tar, 10,10))
            Y_Train.append(goal_state)
        return np.array(X_Train), np.array(Y_Train)  #minibatch

class PriorityQ:
    def __init__(self, game):
        self.elements = []
        self.lookupDict = {}
        self.game: SokobanGame = game
        self.counter = 0
    def insert(self,value: int, priority: int, element): 
        heapq.heappush(self.elements, (priority, value, self.counter,  element))
        self.lookupDict[self.game.encodeMap(element[1])] = value
        #self.elements.append([(value,priority), element])
        #heapq.heappush(self.elements, [value, self.counter, element])
        self.counter += 1
    def remove(self,encoded_map):
        self.elements.remove(encoded_map)
        self.lookupDict.pop(encoded_map, None)

    def contains(self, encoded_map):
        if encoded_map in self.lookupDict:
            return True
            
        return False
    def getCurrentGScore(self, encoded_map):
        return self.lookupDict[encoded_map]
    def getMin(self):
        popped_item = heapq.heappop(self.elements)
        priority, value, _,  map_tuple = popped_item
        # print(popped_item)
        ## returns ((map_score, priority_score), (direction, decoded_map))
        restructured = ((value, priority), (map_tuple[0], map_tuple[1]))
        return restructured
        #return heapq.heappop(self.elements)[2]
    def length(self):
        return len(self.elements)  
    def peek(self):
            if not self.elements:
                raise IndexError("peek from empty priority queue")
            return self.elements[0][1]
            #return self.elements[0][2]
    def getSet(self, encode):
        new_set = set()
        for priority, value, counter, element in self.elements:
            new_set.add(encode(element[1]))

        return new_set

    def __str__(self):
        """
        Provides a string representation of the queue, showing elements 
        in their current heap structure (priority, item).
        """
        # Format each tuple (value, element) as "(P: value, Item: element)"
        formatted_elements = [
            f"(P:{value}, Item:{element})" 
            for value, element in self.elements
        ]
        return "PriorityQ [" + ", ".join(formatted_elements) + "]"