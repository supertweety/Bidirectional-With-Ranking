import numpy as np
from typing import Tuple, Set, Optional
from SokobanGame import SokobanGame
import heapq
GameMap = {
    "Sokoban": SokobanGame
}

class Astar():
    def __init__(self, puzzle, game_name):
        self.dim = 10
        self.game = GameMap[game_name](puzzle)
        self.puzzle = puzzle
        # Instance variables to hold the state of the A* search
        self.visited: Set[str] = set()
        self.parentMap = {}
        self.heap: PriorityQ = PriorityQ()
        self.current_loc: Optional[Tuple[int, int]] = None
        self.current_map: Optional[list] = None # Will store the map/puzzle corresponding to current_loc
        self.iteration = 0
    def isComplete(self):
        return not (self.heap.length() > 0)
    def initAstar(self):
        """Initializes the A* search state."""
        self.visited.clear()
        self.heap = type(self.heap)()  # Re-initialize the priority queue (assuming it has a clear-like method or can be re-instantiated)
        
        initial_encoded_map = self.game.encodeMap(self.game.puzzle)
        #self.visited.add(initial_encoded_map)
        
        self.current_loc = self.game.getPlayerLocation(self.puzzle)
        
        # Insert initial state: score 0, location, and the initial map
        self.heap.insert(0, (self.current_loc, self.game.puzzle))
        self.current_map = self.game.puzzle
        
        return self.current_map
    
    def stepAstar(self) -> Tuple[bool, Optional[list]]:
        """
        Executes one step of the A* search algorithm.
        
        Returns:
            The new map/puzzle state after the step, or None if the search is complete 
            (goal reached or heap is empty).
        """
        if self.heap.length() == 0:
            return (False, None)
        notVisited = False
        while not notVisited:
            ma = self.heap.getMin()
            if self.game.encodeMap(ma[1]) not in self.visited:
                    notVisited = True
        encodedMap = self.game.encodeMap(ma[1])
        self.visited.add(encodedMap)
        current_loc = ma[0]
        self.game.puzzle = ma[1]
        #print(current_loc) 
        directions = self.game.availableStates(current_loc)
        #print(ma[1])
        for direction in directions:
            new_map = self.game.move(current_loc, direction)
            #print("new _amp", new_map)
            #print("dir test", self.game.encodeMap(new_map), visited, self.game.encodeMap(new_map) in visited , new_map)
            # if self.game.encodeMap(new_map) in self.visited:
            #     continue
            if new_map is not None:
                if self.game.isGoal(new_map) == True:
                    return (True, new_map)
                score = self.game.evaluateBoard(new_map)
                #print("score", score)
                #print((current_loc[0]+direction[0], current_loc[1] + direction[1]))
                self.parentMap[self.game.encodeMap(new_map)] = encodedMap
                self.heap.insert(score,((current_loc[0]+direction[0], current_loc[1] + direction[1]),new_map))
        
        self.iteration += 1
        return (False, self.heap.peek()[1])

    def trainAstar(self):
        visited = set()
        visited.add(self.game.encodeMap(self.game.puzzle))
        player_location: Tuple[int,int] = self.game.getPlayerLocation(self.puzzle)
        current_loc = player_location
        heap=PriorityQ()
        heap.insert(0, (player_location,self.game.puzzle))
        while heap.length() > 0:
            if self.game.isGoal():
                break
            #print(heap)
            ma = heap.getMin()
            current_loc = ma[0]
            self.game.puzzle = ma[1]
            #print(current_loc) 
            directions = self.game.availableStates(current_loc)
            for direction in directions:
                new_map = self.game.move(current_loc, direction)
                #print("new _amp", new_map)
                #print("dir test", self.game.encodeMap(new_map), visited, self.game.encodeMap(new_map) in visited , new_map)
                if self.game.encodeMap(new_map) in visited:
                    continue
                if new_map is not None:
                    score = self.game.evaluateBoard(new_map)
                    #print("score", score)
                    #print((current_loc[0]+direction[0], current_loc[1] + direction[1]))
                    heap.insert(score,((current_loc[0]+direction[0], current_loc[1] + direction[1]),new_map))
            visited.add(self.game.encodeMap(ma[1]))
            
            

        pass       

class PriorityQ:
    def __init__(self):
        self.elements = []  
        self.counter = 0
    def insert(self,value,element):
        heapq.heappush(self.elements, [value, self.counter, element])
        self.counter += 1
    def getMin(self):
        return heapq.heappop(self.elements)[2]
    def length(self):
        return len(self.elements)  
    def peek(self):
            if not self.elements:
                raise IndexError("peek from empty priority queue")
            return self.elements[0][2]
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