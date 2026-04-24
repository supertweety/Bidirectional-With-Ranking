# Example file showing a basic pygame "game loop"
import pygame
from pygame_files.drawGame import draw_game, draw_finish_screen, draw_bidirectional_screen, draw_side_by_side, redrawText
from getData import get_data
from astar import Astar
import sys
import argparse
from tqdm import tqdm
import time
from nn import NN
import os
import numpy as np
from SokobanGame import SokobanGame
import torch
import csv
from AnchorSearch import SearchFrontier
from AI_Bidirectional import BidirectionalF2FSearch
from typing import Literal
import json


def parse_arguments():
    """
    Sets up and parses command-line arguments.
    
    Returns:
        argparse.Namespace: Parsed arguments.
    """
    parser = argparse.ArgumentParser(
        description="Sokoban Solver - Bidirectional A* Search with Learning",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    # --- Visualization & Control ---
    gui_group = parser.add_argument_group("GUI & Execution Control")
    gui_group.add_argument(
        '--visual', '--with_pygame', '--with_or_without_pygame',
        dest='visual',
        default="False",
        choices=["True", "False"],
        help="Enable pygame visualization"
    )
    gui_group.add_argument(
        '--iteration_type',
        type=str,
        default="auto",
        choices=["auto", "step"],
        help="Execution mode: 'auto' for automatic, 'step' for manual step-by-step"
    )

    # --- Search Settings ---
    search_group = parser.add_argument_group("Search Algorithm Settings")
    search_group.add_argument(
        '--mode', '--forward_or_bidirectional',
        dest='mode',
        type=str,
        default="bidirectional",
        choices=["forward", "bidirectional"],
        help="Search mode: 'forward' or 'bidirectional'"
    )
    search_group.add_argument(
        '--learning', '--with_learning',
        dest='learning',
        type=str,
        default="off",
        choices=["on", "off"],
        help="Enable neural network learning"
    )

    search_group.add_argument(
        '--with_training',
        type=str,
        default="no",
        choices=["yes", "no"],
        help="Enable neural network training"
    )
    search_group.add_argument(
        "--front_to_front",
        type=str,
        default="no",
        choices=["yes", "no"],
        help="Use Front-to-Front learning instead of Meet-in-the-Middle"
    )
    search_group.add_argument(
        "--anchor_search",
        type=str,
        default="no",
        choices=["yes", "no"],
        help="Use Anchor Search"
    )
    search_group.add_argument(
        "--ttbs",
        type=str,
        default="no",
        choices=["yes", "no"],
        help="Use Top-to-Top Bidirectional Search (TTBS) from IJCAI 2020"
    )

    # --- Experiment & Environment ---
    exp_group = parser.add_argument_group("Experiment & Environment Settings")
    exp_group.add_argument(
        "--noise", "--with_noise",
        dest='noise',
        type=str,
        default="off",
        choices=["off", "additive", "multiplicative"],
        help="Type of noise to add to heuristic scores"
    )
    exp_group.add_argument(
        "--dummy_data", "--with_dummy_data",
        dest='dummy_data',
        type=str,
        default="No",
        choices=["Yes", "No"],
        help="Use simple puzzles from test_box.txt for development"
    )

    return parser.parse_args()


def baseRun(states, with_noise, aStar):
    """
    Core loop for standard A* search over multiple states and epochs.
    
    Args:
        states (list): List of initial game states.
        with_noise (bool): Whether to add noise to the heuristic.
        aStar (Astar): Initial A* search object.
    """
    total = 0
    csv_file = open("search_results.csv", "a")
    results = []
    for epoch in range(10):
        for state in range(1, len(states)):
            start_time = time.time()
            completed = False
            end_Map = None
            it = 0
            # with tqdm(total=None, desc="Searching ", unit="states") as pbar:
            # i = 0
            while not completed:
                elapsed_time = time.time() - start_time
                # if elapsed_time > 600:
                #     print("too long")
                #     break
                
                is_solution, next_map, _ = aStar.stepAstar("BaseHeuristic", {
                    "with_noise": with_noise
                })
                if is_solution:
                    print("made it")
                    completed = True
                    end_Map = next_map
                # pbar.update(1) # Increment the counter by 1
                # i += 1
                it+=1

            #print("Number of Nodes Expanded: ", i)
            aStar = Astar(states[state], "Sokoban")
            aStar.initAstar()
            total += it
        results.append(str(it))
    
    final = ["A*", with_noise]
    final = final + results
    writer = csv.writer(csv_file, delimiter='\t')
    writer.writerow(final)
    print(f"After 10 epochs, average with {with_noise} noise")
            #pygame.display.flip()

            #clock.tick(60)  # limits FPS to 60
    # print("end player area", np.where(end_Map == 3))
    # path = aStar.reconstructSuccessfulPath(end_Map)
    # index = len(path) - 1
    # #draw_game(end_Map, screen)
    # pygame.display.flip()
    # while True:
    #     for event in pygame.event.get():
    #         if event.type == pygame.QUIT:
    #             break

    #         if event.type == pygame.MOUSEBUTTONDOWN and is_completed == False and index >= 0:
    #             mouse = pygame.mouse.get_pos()
    #             if button.command(mouse[0], mouse[1]) == True:
    #                 draw_game(aStar.game.decodeMap(path[index]), screen)
    #                 index -= 1

    #     pygame.display.flip()
    #     clock.tick(60)
    # pygame.quit()

def autoGUIRun(running, is_completed):
    """
    Automated GUI execution of standard A* search.
    
    Args:
        running (bool): Flag indicating if the game is running.
        is_completed (bool): Flag indicating if the search is completed.
    """
    while running:
        # poll for events
        # pygame.QUIT event means the user clicked X to close your window
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        is_solution, next_map, _ = aStar.stepAstar()
        if is_solution:
            is_completed= True
            draw_finish_screen(next_map, screen)
            continue
        draw_game(next_map, screen)
        pygame.time.delay(500)

    # next_map = aStar.stepAstar()
    # draw_game(next_map)
    # fill the screen with a color to wipe away anything from last frame
    

    # RENDER YOUR GAME HERE

    # flip() the display to put your work on screen
        pygame.display.flip()

        clock.tick(60)  # limits FPS to 60

    pygame.quit()


def stepGUIRun(running, is_completed):
    """
    Manual step-by-step GUI execution of standard A* search.
    
    Args:
        running (bool): Flag indicating if the game is running.
        is_completed (bool): Flag indicating if the search is completed.
    """
    while running:
        # poll for events
        # pygame.QUIT event means the user clicked X to close your window
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN and is_completed == False:
                mouse = pygame.mouse.get_pos()
                if button.command(mouse[0], mouse[1]) == True:
                    is_solution, next_map, scoring = aStar.stepAstar()
                    if is_solution:
                        is_completed= True
                        draw_finish_screen(next_map, screen)
                        continue
                    draw_game(next_map, screen)

    # next_map = aStar.stepAstar()
    # draw_game(next_map)
    # fill the screen with a color to wipe away anything from last frame
    

    # RENDER YOUR GAME HERE

    # flip() the display to put your work on screen
        pygame.display.flip()

        clock.tick(60)  # limits FPS to 60

    pygame.quit()


### bidirectional


def biBaseFF(states, with_noise, forwardAStar, backwardAStar):
    """
    Bidirectional Front-to-Front (FF) A* search.
    
    Args:
        states (list): List of initial game states.
        with_noise (bool): Whether to add noise to the heuristic.
        forwardAStar (Astar): Forward search object.
        backwardAStar (Astar): Backward search object.
    """
    total = 0
    csv_file = open("search_results.csv", "a")
    results = []
    for epoch in range(10):
        for state in range(1, len(states)):
            
            start_time = time.time()
            completed = False
            is_front_solution = False
            is_backward_solution = False
            it=0
            # with tqdm(total=None, desc="Searching ", unit="states") as pbar:
            while not completed:
                elapsed_time = time.time() - start_time
                if elapsed_time > 600:
                    print("too long")
                    break
                if backwardAStar.heap.length() == 0 or forwardAStar.heap.length() == 0:
                    print("Invalid")
                    break
                bottom_openset_front = backwardAStar.heap.peek()
                is_front_solution, current_forward_map, scoring = forwardAStar.stepAstar("FF", updateObject={
                    "oppositeAstar": bottom_openset_front,
                    "opposite_visited": backwardAStar.visited_parsed,
                    "with_noise": with_noise
                })
                top_openset_front = forwardAStar.heap.peek()
                is_backward_solution, current_backward_map, scoring_ = backwardAStar.stepAstar("FF", updateObject={
                    "oppositeAstar": top_openset_front,
                    "opposite_visited": forwardAStar.visited_parsed,
                    "with_noise": with_noise
                })
                if scoring == -1 or scoring_ == -1:
                    print("Converged")
                    completed = True 
                    break
                # is_backward_solution, current_backward_map, scoring_ = backwardAStar.stepAstar()
                # 
                # if len(forwardAStar.heap.getSet(forwardAStar.game.encodeMap).intersection(backwardAStar.heap.getSet(backwardAStar.game.encodeMap))) > 0:
                #     print("Converged")
                #     completed = True
                if is_front_solution == True or is_backward_solution == True:
                    print("Did not Converge")
                    completed = True
                    converged = True
                    # draw_finish_screen(current_backward_map, screen)
                    break
                    # pbar.update(1)
                it+=1
            # print("Number of Nodes expanded: ", it)
            forwardAStar = Astar(states[state], "Sokoban")
            backward_puzzle = forwardAStar.game.initializeBackwardPuzzle(states[state])
            backwardAStar = Astar(backward_puzzle, "Sokoban", True)
            forwardAStar.initAstar()
            backwardAStar.initAstar()
        total += it
        results.append(str(it))
    
    final = ["Front-to-Front", with_noise]
    final = final + results
    writer = csv.writer(csv_file, delimiter='\t')
    writer.writerow(final)
    print(f"After 10 epochs, average with {with_noise} noise")
    # print("Number of States: " it)

    # print("end player area", np.where(end_Map == 3))
    # print(is_backward_solution, is_front_solution)
    current_doneAStar = forwardAStar if is_front_solution else backwardAStar
    current_end_map = current_forward_map if is_front_solution == True else current_backward_map
    path = current_doneAStar.reconstructSuccessfulPath(current_end_map)
    other_star = forwardAStar if not is_front_solution else backwardAStar
    main_path = other_star.reconstructSuccessfulPath(other_star.game.flipGame(current_end_map))
    if is_front_solution:
        ## main path is backward
        new_path = path[::-1]
        for decodeMap in main_path[::-1][1:]:
            new_path.append(decodeMap)
        path = new_path
    else: 
        ## main path is forward
        new_path = main_path[::-1]
        for decodeMap in path[1:]:
            new_path.append(other_star.game.encodeMap(other_star.game.flipGame(other_star.game.decodeMap(decodeMap))))
        path = new_path
    ## one end of the path 
    index = 0
    #draw_game(end_Map, screen)
    pygame.display.flip()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                break

            if event.type == pygame.MOUSEBUTTONDOWN and is_completed == False and index <= len(path) - 1:
                mouse = pygame.mouse.get_pos()
                if button.command(mouse[0], mouse[1]) == True:
                    draw_game(backwardAStar.game.decodeMap(path[index]), screen)
                    index += 1

        pygame.display.flip()
        clock.tick(60)
    pygame.quit()


def biBaseTTBS(states, withLearning, withTraining):
    """
    Run Top-to-Top Bidirectional Search (TTBS) over all states.

    Mirrors biBaseAnchorSearch: iterates through each puzzle state,
    runs BidirectionalF2FSearch.search(), and reports results per puzzle.

    Args:
        states (list): List of puzzle boards (np.ndarray).
    """
    print("=== TTBS (Top-to-Top Bidirectional Search) ===")
   
    nn = None
    if withLearning: 
        nn = NN(10)
        my_device = "cuda:0" if torch.cuda.is_available() else "cpu"
        print(f"Current Device is: {my_device}")
        criterion, optimizer = nn.initialize_cr_opt()
        print("--- Pre Learning Scores --- ")
    if withTraining:
        for epoch in range(5): 
            for state_idx in range(len(states)):
                puzzle = states[state_idx]
                searcher = BidirectionalF2FSearch(puzzle, None)

                start_time = time.time()
                path = searcher.search(max_iterations=50000)
                elapsed = time.time() - start_time

                if path:
                    result = "SUCCESS"
                    path_len = len(path)
                    print(
                        f"[{state_idx:>3d}] SUCCESS  "
                        f"path={path_len:>4d}  "
                        f"iters={searcher.iteration:>6d}  "
                        f"time={elapsed:.3f}s"
                    )
                else:
                    result = "FAILED"
                    path_len = 0
                    # print(
                    #     f"[{state_idx:>3d}] FAILED   "
                    #     f"iters={searcher.iteration:>6d}  "
                    #     f"time={elapsed:.3f}s"
                    # )

                if withLearning:
                    nn_costs = []
                    optimal_costs = []
                    optimizer.zero_grad()
                    for encoded_state in path:

                        nn_value = nn.inference(searcher.forward_game.decodeMap(encoded_state), searcher.forward_game.target, searcher.forward_game.goal_map)
                        # print(f"NN Value: {nn_value.item():.4f}")
                        optimal_value = searcher.forward_game.evaluateBoard((searcher.forward_game.decodeMap(encoded_state)))
                        nn_costs.append(nn_value)
                        optimal_costs.append(optimal_value)
                        # optimal_costs.append(1.0)
                    
                    output_nn_value_tensor =  torch.stack(nn_costs).to(my_device)
                    output_nn_value_tensor= output_nn_value_tensor.squeeze()  # Remove extra dimensions if needed
                    output_optimal_value_tensor =  torch.tensor(optimal_costs,dtype=torch.float32, device=my_device)
                    # print(output_nn_value_tensor.shape, output_optimal_value_tensor.shape)
                    loss = criterion(output_nn_value_tensor, output_optimal_value_tensor)
                    # print(f"Loss: {loss.item():.4f}")
                    loss.backward()
                    optimizer.step()

    if withLearning and withTraining:
        torch.save(nn.state_dict(), "model_weights.pth")
    csv_file = open("ttbs_results.csv", "a")
    writer   = csv.writer(csv_file, delimiter='\t')
    writer.writerow(["puzzle_index", "iterations", "path_length", "time_s", "result"])

    if os.path.exists("model_weights.pth"):
        print("Loading model weights from model_weights.pth")
        state_dict = torch.load("model_weights.pth", weights_only=True)
        nn.load_state_dict(state_dict, strict=False)
    print("--- Testing with Learning ---")
    for state_idx in range(len(states)):
        puzzle = states[state_idx]
        searcher = BidirectionalF2FSearch(puzzle, nn)

        start_time = time.time()
        path = searcher.search(max_iterations=50000)
        elapsed = time.time() - start_time

        if path:
            result = "SUCCESS"
            path_len = len(path)
            print(
                f"[{state_idx:>3d}] SUCCESS  "
                f"path={path_len:>4d}  "
                f"iters={searcher.iteration:>6d}  "
                f"time={elapsed:.3f}s"
            )
        else:
            result = "FAILED"
            path_len = 0
            print(
                f"[{state_idx:>3d}] FAILED   "
                f"iters={searcher.iteration:>6d}  "
                f"time={elapsed:.3f}s"
            )

        writer.writerow([state_idx, searcher.iteration, path_len,
                        f"{elapsed:.4f}", result])

    csv_file.close()
    print("Results written to ttbs_results.csv")


##

def biBaseAnchorSearch(states, forward_puzzle, backwardPuzzle, withLearning):
    """
    Bidirectional Anchor Search.
    
    Args:
        states (list): List of initial game states.
        forward_puzzle (np.ndarray): Forward puzzle board.
        backwardPuzzle (np.ndarray): Backward puzzle board.
        withLearning (bool): Whether to use neural network learning for heuristics.
    """
    
    frontAnchorSearch = SearchFrontier(forward_puzzle, False)
    
    backwardAnchorSearch = SearchFrontier(backwardPuzzle, True)
    if withLearning:
        
        nn = NN(10)
        if os.path.exists("model_weights.pth"):
            state_dict = torch.load("model_weights.pth", weights_only=True)
            nn.load_state_dict(state_dict)
        my_device = "cuda:0" if torch.cuda.is_available() else "cpu"
        print(f"Current Device is: {my_device}")
        criterion, optimizer = nn.initialize_cr_opt()
        print("--- Pre Learning Scores --- ")
    # If 'states' represents levels or sub-problems, this loop is fine.
    # If this is one single search, ensure you aren't resetting unnecessarily.
    
    for state in range(1, len(states)):
        completed = False
        alternate = True
        status = ""
        status2 = ""
        step_counter = 0
        path = []
        
        while not completed:
            if alternate:
                # Expand Forward towards Backward's Anchor
                status = frontAnchorSearch.step(backwardAnchorSearch)
                alternate = False
            else:
                # Expand Backward towards Forward's Anchor (FIXED)
                status2 = backwardAnchorSearch.step(frontAnchorSearch)
                alternate = True

            # Check the status of the step JUST taken
            if status == "SUCCESS" or status2 == "SUCCESS":
                print("Converged!", step_counter)
                # front_path = frontAnchorSearch.reconstructPath()
                # back_path = backwardAnchorSearch.reconstructPath()
                # # print(len(front_path), len(back_path)) 
                # back_path_f_oriented = frontAnchorSearch.flipPath(back_path)
                # path = front_path + back_path_f_oriented

                completed = True
                break

            if status == "FINISHED_EARLY" or status2 == "FINISHED_EARLY":
                # Check if BOTH have now failed
                if status == "FINISHED_EARLY":
                    print("Front finished first")
                else:
                    print("Back Finished First")
                #if frontAnchorSearch.heap.length() == 0 and backwardAnchorSearch.heap.length() == 0:
                print("Did not Converge: One side finished and did not meet")
                completed = True
                break 
            if status == "FAILED" or status2 == "FAILED":
                # Check if BOTH have now failed
                #if frontAnchorSearch.heap.length() == 0 and backwardAnchorSearch.heap.length() == 0:
                print("Did not Converge: Search space exhausted on both sides.")
                completed = True
                break
            step_counter += 1

        if withLearning:
            nn_costs = []
            optimal_costs = []
            optimizer.zero_grad()
            for encoded_state in path:
                nn_value = nn.inference(frontAnchorSearch.game.decodeMap(encoded_state), frontAnchorSearch.game.target, frontAnchorSearch.game.goal_map)
                optimal_value = frontAnchorSearch.game.evaluateBoard((frontAnchorSearch.game.decodeMap(encoded_state)))
                nn_costs.append(nn_value)
                optimal_costs.append(optimal_value)
                
            loss = criterion(torch.tensor(nn_costs, requires_grad=True, device=my_device), torch.tensor(optimal_costs, requires_grad=True,device=my_device))
            loss.backward()
            optimizer.step()

        frontAnchorSearch = SearchFrontier(states[state], False)
        backwardAnchorSearch = SearchFrontier(frontAnchorSearch.game.initializeBackwardPuzzle(states[state]), True)

    ## Evaluation function to see how the model does
    if withLearning:
        
        print("--- Post Learning Scores --- ")
        frontAnchorSearch = SearchFrontier(forward_puzzle, False, nn=nn)
        backwardAnchorSearch = SearchFrontier(backwardPuzzle, True, nn=nn)
        if os.path.exists('./frontAnchorSearchParentMap.json') and os.path.exists('./backwardAnchorSearchParentMap.json') and os.path.exists('./frontrendezvous.txt') and os.path.exists('./backrendezvous.txt'):
            print("--- Already discovered Paths --- ")
            frontAnchorSearch.parentMap = json.loads(open('./frontAnchorSearchParentMap.json').read())
            backwardAnchorSearch.parentMap = json.loads(open('./backwardAnchorSearchParentMap.json').read())
            frontAnchorSearch.rendezvous = frontAnchorSearch.game.decodeMap(open('./frontrendezvous.txt').read())
            backwardAnchorSearch.rendezvous = backwardAnchorSearch.game.decodeMap(open('./backrendezvous.txt').read())
            front_path = frontAnchorSearch.reconstructPath()
            front_path.reverse()
            back_path = backwardAnchorSearch.reconstructPath()

            # # print(len(front_path), len(back_path)) 
            back_path_f_oriented = frontAnchorSearch.flipPath(back_path)
            path = front_path + back_path_f_oriented


        else: 
            with torch.no_grad():
                for state in range(1, len(states)):
                    completed = False
                    alternate = True
                    status = ""
                    status2 = ""
                    step_counter = 0
                    path = []
                    
                    while not completed:
                        if alternate:
                            # Expand Forward towards Backward's Anchor
                            status = frontAnchorSearch.step(backwardAnchorSearch)
                            alternate = False
                        else:
                            # Expand Backward towards Forward's Anchor (FIXED)
                            status2 = backwardAnchorSearch.step(frontAnchorSearch)
                            alternate = True

                        # Check the status of the step JUST taken
                        if status == "SUCCESS" or status2 == "SUCCESS":
                            print("Learning Converged!", step_counter)
                            with open('frontAnchorSearchParentMap.json', 'w') as f:
                                json.dump(frontAnchorSearch.parentMap, f)
                            with open('backwardAnchorSearchParentMap.json', 'w') as f:
                                json.dump(backwardAnchorSearch.parentMap, f)
                            with open('frontrendezvous.txt', 'w') as f:
                                json.dump(frontAnchorSearch.game.encodeMap(frontAnchorSearch.rendezvous), f) 
                            with open('backrendezvous.txt', 'w') as f:
                                json.dump(backwardAnchorSearch.game.encodeMap(backwardAnchorSearch.rendezvous), f) 
                            front_path = frontAnchorSearch.reconstructPath()
                            back_path = backwardAnchorSearch.reconstructPath()
                            # # print(len(front_path), len(back_path)) 
                            back_path_f_oriented = frontAnchorSearch.flipPath(back_path)
                            path = front_path + back_path_f_oriented

                            completed = True
                            break

                        if status == "FINISHED_EARLY" or status2 == "FINISHED_EARLY":
                            # Check if BOTH have now failed
                            if status == "FINISHED_EARLY":
                                print("Front finished first")
                            else:
                                print("Back Finished First")
                            #if frontAnchorSearch.heap.length() == 0 and backwardAnchorSearch.heap.length() == 0:
                            print("Did not Converge: One side finished and did not meet")
                            completed = True
                            break 
                        if status == "FAILED" or status2 == "FAILED":
                            # Check if BOTH have now failed
                            #if frontAnchorSearch.heap.length() == 0 and backwardAnchorSearch.heap.length() == 0:
                            print("Did not Converge: Search space exhausted on both sides.")
                            completed = True
                            break
                        step_counter += 1

        

                    frontAnchorSearch = SearchFrontier(states[state], False, nn=nn)
                    backwardAnchorSearch = SearchFrontier(frontAnchorSearch.game.initializeBackwardPuzzle(states[state]), True, nn=nn)
        index = 0
        #draw_game(end_Map, screen)
        pygame.display.flip()
        draw_game(frontAnchorSearch.game.decodeMap(path[index]), screen)
        while True:
            if index <= len(path):
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        break

                    keys = pygame.key.get_pressed()
                    if (keys[pygame.K_RIGHT]): 
                        index += 1   
                        draw_game(frontAnchorSearch.game.decodeMap(path[index]), screen)
                        

                pygame.display.flip()
                clock.tick(60)
        pygame.quit()

def biBaseAnchorSearchStep(forward_puzzle, backwardPuzzle, withLearning):
    """
    Manual step-by-step GUI execution of Bidirectional Anchor Search.
    
    Args:
        forward_puzzle (np.ndarray): Forward puzzle board.
        backwardPuzzle (np.ndarray): Backward puzzle board.
        withLearning (bool): Whether to use neural network learning for heuristics.
    """
    
    frontAnchorSearch = SearchFrontier(forward_puzzle, False)
    backwardAnchorSearch = SearchFrontier(backwardPuzzle, True)
    if withLearning:
        state_dict = torch.load("model_weights.pth", weights_only=True)
        nn = NN(10)
        nn.load_state_dict(state_dict)
        my_device = "cuda:0" if torch.cuda.is_available() else "cpu"
        print(f"Current Device is: {my_device}")
        criterion, optimizer = nn.initialize_cr_opt()
        print("--- Pre Learning Scores --- ")

    running = True
    alternate = True
    status1 = ""
    status2 = ""
    epochs = 5
    for i in range(epochs):
        for state in range(1, len(states)):
            completed = False
            alternate = True
            status = ""
            status2 = ""
            step_counter = 0
            path = []
            
            while not completed:
                if alternate:
                    # Expand Forward towards Backward's Anchor
                    status = frontAnchorSearch.step(backwardAnchorSearch)
                    alternate = False
                else:
                    # Expand Backward towards Forward's Anchor (FIXED)
                    status2 = backwardAnchorSearch.step(frontAnchorSearch)
                    alternate = True

                # Check the status of the step JUST taken
                if status == "SUCCESS" or status2 == "SUCCESS":
                    print("Converged!", step_counter)
                    # front_path = frontAnchorSearch.reconstructPath()
                    # back_path = backwardAnchorSearch.reconstructPath()
                    # # print(len(front_path), len(back_path)) 
                    # back_path_f_oriented = frontAnchorSearch.flipPath(back_path)
                    # path = front_path + back_path_f_oriented

                    completed = True
                    break

                if status == "FINISHED_EARLY" or status2 == "FINISHED_EARLY":
                    # Check if BOTH have now failed
                    if status == "FINISHED_EARLY":
                        print("Front finished first")
                    else:
                        print("Back Finished First")
                    #if frontAnchorSearch.heap.length() == 0 and backwardAnchorSearch.heap.length() == 0:
                    print("Did not Converge: One side finished and did not meet")
                    completed = True
                    break 
                if status == "FAILED" or status2 == "FAILED":
                    # Check if BOTH have now failed
                    #if frontAnchorSearch.heap.length() == 0 and backwardAnchorSearch.heap.length() == 0:
                    print("Did not Converge: Search space exhausted on both sides.")
                    completed = True
                    break
                step_counter += 1

            if withLearning:
                nn_costs = []
                optimal_costs = []
                optimizer.zero_grad()
                for encoded_state in path:
                    nn_value = nn.inference(frontAnchorSearch.game.decodeMap(encoded_state), frontAnchorSearch.game.target, frontAnchorSearch.game.goal_map)
                    optimal_value = frontAnchorSearch.game.evaluateBoard((frontAnchorSearch.game.decodeMap(encoded_state)))
                    nn_costs.append(nn_value)
                    optimal_costs.append(optimal_value)
                    
                loss = criterion(torch.tensor(nn_costs, requires_grad=True, device=my_device), torch.tensor(optimal_costs, requires_grad=True,device=my_device))
                loss.backward()
                optimizer.step()

            frontAnchorSearch = SearchFrontier(states[state], False)
            backwardAnchorSearch = SearchFrontier(frontAnchorSearch.game.initializeBackwardPuzzle(states[state]), True)

    # PATH = "model_weights.pth"
    # torch.save(nn.state_dict(), PATH)
    # sys.exit(0)
    if withLearning:
        print("--- Post Learning Scores --- ")
        frontAnchorSearch = SearchFrontier(forward_puzzle, False, nn=nn)
        backwardAnchorSearch = SearchFrontier(backwardPuzzle, True, nn=nn)
    draw_side_by_side(frontAnchorSearch.anchor, backwardAnchorSearch.anchor, screen)
    # sys.exit(0)
    while running:
        # poll for events
        # pygame.QUIT event means the user clicked X to close your window
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            # mouse = pygame.mouse.get_pos()

            keys = pygame.key.get_pressed()
            if (keys[pygame.K_RIGHT]):    
                if alternate:
                    # print("MOVED")
                    # Expand Forward towards Backward's Anchor
                    status1 = frontAnchorSearch.step(backwardAnchorSearch)
                    # draw_game(frontAnchorSearch.anchor, screen)
                    alternate = False
                else:
                    # Expand Backward towards Forward's Anchor (FIXED)
                    status2 = backwardAnchorSearch.step(frontAnchorSearch)
                    # draw_game(backwardAnchorSearch.anchor, screen)
                    alternate = True

                # Check the status of the step JUST taken
                if status1 == "SUCCESS" or status2 == "SUCCESS":
                    print("Converged!")
                    # You can now access the rendezvous_node from the search that succeeded
                    meeting_point = frontAnchorSearch.rendezvous_node or backwardAnchorSearch.rendezvous_node
                    completed = True
                    break

                if status1 == "FINISHED_EARLY" or status2 == "FINISHED_EARLY":                       
                    if status1 == "FINISHED_EARLY":
                        print("Front finished first")
                    else:
                        print("Back Finished First")
                    #if frontAnchorSearch.heap.length() == 0 and backwardAnchorSearch.heap.length() == 0:

                    print("Did not Converge: One side finished and did not meet")
                    completed = True
                    break 
                if status1 == "FAILED" or status2 == "FAILED":
                    # Check if BOTH have now failed
                    #if frontAnchorSearch.heap.length() == 0 and backwardAnchorSearch.heap.length() == 0:
                    print("Did not Converge: Search space exhausted on both sides.")
                    completed = True
                    break
                draw_side_by_side(frontAnchorSearch.anchor, backwardAnchorSearch.anchor, screen)
            # pygame.time.delay(3000)

                

    # next_map = aStar.stepAstar()
    # draw_game(next_map)
    # fill the screen with a color to wipe away anything from last frame
    

    # RENDER YOUR GAME HERE

    # flip() the display to put your work on screen
        pygame.display.flip()

        clock.tick(60)  # limits FPS to 60

    pygame.quit()

def biBaseRun(states, with_noise, forwardAStar, backwardAStar):
    """
    Standard bidirectional A* search.
    
    Args:
        states (list): List of initial game states.
        with_noise (bool): Whether to add noise to the heuristic.
        forwardAStar (Astar): Forward search object.
        backwardAStar (Astar): Backward search object.
    """
    total = 0
    csv_file = open("search_results.csv", "a")
    results = []
    for epoch in range(10):
        for state in range(1, len(states)):
            
            start_time = time.time()
            completed = False
            is_front_solution = False
            is_backward_solution = False
            it = 0
            #with tqdm(total=None, desc="Searching ", unit="states") as pbar:
            while not completed:
                elapsed_time = time.time() - start_time
                if elapsed_time > 600:
                    print("too long")
                    break
                is_front_solution, current_forward_map, scoring = forwardAStar.stepAstar("BaseHeuristic", {
                    "with_noise": with_noise,
                    "opposite_visited": backwardAStar.visited_parsed,
                })
                is_backward_solution, current_backward_map, scoring_ = backwardAStar.stepAstar("BaseHeuristic", {
                    "with_noise": with_noise,
                    "opposite_visited": forwardAStar.visited_parsed,
                })
                # print(is_front_solution, is_backward_solution)
                ### check if visited in forward is in backward visited
                # if forwardAStar.game.compareGames(current_forward_map, current_backward_map):
                #         break
                # for first_open in forwardAStar.heap.elements:
                #     for second_open in backwardAStar.heap:
                #         first_decoded = forwardAStar.game.decodeMap(first_open)
                #         second_decoded = backwardAStar.game.decodeMap(second_open)
                # if len(forwardAStar.visited.intersection(backwardAStar.visited)) > 0 or len(forwardAStar.heap.getSet(forwardAStar.game.encodeMap).intersection(backwardAStar.heap.getSet(backwardAStar.game.encodeMap))) > 0:
                #     print("Converged")
                if scoring == -1 or scoring_ == -1:
                    print("Converged")
                    completed = True 
                    break

                if is_front_solution == True or is_backward_solution == True:
                    print("Did not Converge")
                    completed = True
                    converged = True
                    # draw_finish_screen(current_backward_map, screen)
                    break
                #pbar.update(1)
                it += 1

        #print("Number of Nodes expanded: ", it)
            forwardAStar = Astar(states[state], "Sokoban")
            backward_puzzle = forwardAStar.game.initializeBackwardPuzzle(states[state])
            backwardAStar = Astar(backward_puzzle, "Sokoban", True)
            forwardAStar.initAstar()
            backwardAStar.initAstar()

        total += it
        results.append(str(it))
    
    final = ["Standard Bidirectional", with_noise]
    final = final + results
    writer = csv.writer(csv_file, delimiter='\t')
    writer.writerow(final)
    print(f"After 10 epochs, average with {with_noise} noise")
    # print("end player area", np.where(end_Map == 3))
    current_doneAStar = forwardAStar if is_front_solution else backwardAStar
    current_end_map = current_forward_map if is_front_solution == True else current_backward_map
    path = current_doneAStar.reconstructSuccessfulPath(current_end_map)
    other_star = forwardAStar if not is_front_solution else backwardAStar
    main_path = other_star.reconstructSuccessfulPath(other_star.game.flipGame(current_end_map))
    if is_front_solution:
        ## main path is backward
        new_path = path[::-1]
        for decodeMap in main_path[::-1][1:]:
            new_path.append(decodeMap)
        path = new_path
    else: 
        ## main path is forward
        new_path = main_path[::-1]
        for decodeMap in path[1:]:
            new_path.append(other_star.game.encodeMap(other_star.game.flipGame(other_star.game.decodeMap(decodeMap))))
        path = new_path
    ## one end of the path 
    index = 0
    #draw_game(end_Map, screen)
    pygame.display.flip()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                break

            if event.type == pygame.MOUSEBUTTONDOWN and is_completed == False and index <= len(path) - 1:
                mouse = pygame.mouse.get_pos()
                if button.command(mouse[0], mouse[1]) == True:
                    draw_game(backwardAStar.game.decodeMap(path[index]), screen)
                    index += 1

        pygame.display.flip()
        clock.tick(60)
    pygame.quit()


def biBaseRunGuarenteed():
    """
    Bidirectional A* search with guaranteed optimality using the MM algorithm.
    """
    start_time = time.time()
    completed = False
    converged = False
    current_forward_map = None
    current_backward_map = None
    front_called = 0
    back_called = 0
    is_front_solution = False
    is_back_solution = False
    U = float('inf')
    with tqdm(total=None, desc="Searching ", unit="states") as pbar:
        i = 0
        while not completed:
            elapsed_time = time.time() - start_time
            if elapsed_time > 600:
                print("too long")
                break
            # print(forwardAStar.calculatePriority(), backwardAStar.calculatePriority())
            C = min(forwardAStar.calculatePriority(), backwardAStar.calculatePriority())
            
            if U <= max(C,forwardAStar.calculateOpenSetMaxorMinValue("f_value", "min"),backwardAStar.calculateOpenSetMaxorMinValue("f_value", "min"), forwardAStar.calculateOpenSetMaxorMinValue("g_value", "min") + backwardAStar.calculateOpenSetMaxorMinValue("g_value", "min") + 1):
                completed = True
                print("CONVERGED")

            if C == forwardAStar.calculatePriority():
                is_front_solution, current_forward_map, scoring = forwardAStar.stepAstar("MM", updateObject={
                    "oppositeAstar": backwardAStar.inOpenSet,
                    "U": U,
                    "getGScore": backwardAStar.getBestGScore
                })
                if is_front_solution:
                    print("Did not converge front")
                    completed = True
                    break
                _, __, U_value = scoring
                U = U_value
                front_called += 1

            else:
                is_back_solution, current_backward_map, scoring = backwardAStar.stepAstar("MM", updateObject={
                    "oppositeAstar": forwardAStar.inOpenSet,
                    "U": U,
                    "getGScore": forwardAStar.getBestGScore
                })
                if is_back_solution:
                    print("Did not converge back")
                    completed = True
                    break
                _, __, U_value = scoring
                U = U_value
                back_called += 1
            
            # if i > 1000:
            #     break
            # print("U value", U)
            # is_front_solution, current_forward_map, forward_score = forwardAStar.stepAstar("MM")
            # is_back_solution, current_backward_map, backward_score = backwardAStar.stepAstar("MM")
            # encoded_forward_map = forwardAStar.game.encodeMap(current_forward_map) 
            # encoded_backward_map = backwardAStar.game.encodeMap(current_backward_map)
            # if encoded_backward_map == encoded_forward_map:
            #     print("made it")
            #     completed = True
            #     #draw_finish_screen(current_forward_map, screen)
            #     continue 

            pbar.update(1) # Increment the counter by 1
            i += 1

    backward_path = backwardAStar.reconstructSuccessfulPath(current_backward_map)
    flipped_path = []
    for i in reversed(range(len(backward_path))):
        flipped_path.append(forwardAStar.game.flipGame(forwardAStar.game.decodeMap(backward_path[i])))
    forward_path = forwardAStar.reconstructSuccessfulPath(current_forward_map)
    decoded_forward_path = []
    forward_path.reverse()
    print(forward_path)
    combined_path = np.concatenate((forward_path, flipped_path))


    print(backwardAStar.game.encodeMap(current_backward_map) == backwardAStar.game.encodeMap(current_forward_map))
    # print(backwardAStar.game.encodeMap(current_backward_map))
    pygame.display.flip()
    path_index = 0
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                break

            if event.type == pygame.MOUSEBUTTONDOWN and is_completed == False and path_index < len(combined_path):
                mouse = pygame.mouse.get_pos()
                if button.command(mouse[0], mouse[1]) == True:
                    draw_game(aStar.game.decodeMap(combined_path[path_index]), screen)
                    path_index += 1

        pygame.display.flip()
        clock.tick(60)
    pygame.quit()

def bi_neural_run():
    """
    Bidirectional search using neural network heuristics.
    """

    start_time = time.time()
    completed = False
    converged = False
    current_forward_map = None
    current_backward_map = None
    #h = calculateNextAction(current_forward_map, forwardAStar.game.target, forward_goal, nn)
    with tqdm(total=None, desc="Searching ", unit="states") as pbar:
        i = 0
        # print("here", completed)
        while not completed:
            elapsed_time = time.time() - start_time
            if elapsed_time > 5000:
                print("too long")
                break
            is_front_solution, current_forward_map, forward_score = forwardAStar.stepAstar("MM_Neural")
            is_back_solution, current_backward_map, backward_score = backwardAStar.stepAstar("MM_Neural")
            encoded_forward_map = forwardAStar.game.encodeMap(current_forward_map) 
            encoded_backward_map = backwardAStar.game.encodeMap(current_backward_map)
            if encoded_backward_map == encoded_forward_map:
                print("made it")
                completed = True
                ## reconstruct success path
                forward_path = forwardAStar.reconstructSuccessfulPath(encoded_forward_map)
                backward_path = backwardAStar.reconstructSuccessfulPath(encoded_backward_map)
                forward_path.remove(encoded_forward_map)
                backward_path.remove(encoded_backward_map)
                final_path = np.concatenate((forward_path, backward_path))
                X_train, Y_train = forwardAStar.create_one_hot(final_path, forwardAStar.game.target, forwardAStar.game.goal_map)
                
                # h_matrix = c
                # draw_finish_screen(current_forward_map, screen)
                # continue 
            elif is_front_solution == True or is_back_solution == True:
                print("Did not Converge")
                completed = True
                converged = True
                # draw_finish_screen(current_backward_map, screen)
                break
            pbar.update(1) # Increment the counter by 1
            i += 1

def neural_run():
    """
    Standard A* search using neural network heuristics.
    
    Returns:
        tuple: (nn_costs, optimal_costs) for loss calculation.
    """
    start_time = time.time()
    completed = False
    end_Map = None
    with tqdm(total=None, desc="Searching ", unit="states") as pbar:
        i = 0
        while not completed:
            elapsed_time = time.time() - start_time
            # if elapsed_time > 600:
            #     print("too long")
            #     break
            
            is_solution, next_map, _ = aStar.stepAstar("Neural")
            if is_solution:
                print("made it")
                completed = True
                end_Map = next_map
            pbar.update(1) # Increment the counter by 1
            i += 1
            #pygame.display.flip()

            #clock.tick(60)  # limits FPS to 60
    path = aStar.reconstructSuccessfulPath(end_Map)
    nn_costs, optimal_costs = aStar.loss(path)
    return nn_costs, optimal_costs 
    # loss = criterion(outputs, labels)
    # X_train, Y_train = forwardAStar.create_one_hot(path, aStar.game.target, aStar.game.goal_map)



def baseWithLearning(states):
    """
    Standard A* search with online learning from neural network heuristics.
    
    Args:
        states (list): List of initial game states.
    """
    nn = NN(10)
    criterion, optimizer = nn.initialize_cr_opt()
    if "finalSok3" in os.listdir("."):
        nn.model.load_weights('finalSok3')
    aStar.nn = nn
    for i in range(0,1):
        with torch.no_grad():
            nn_costs, optimal_costs = neural_run()
            loss = criterion(nn_costs, optimal_costs)
            loss.backward()
            optimizer.step()
        break
        forwardAStar = Astar(states[i], "Sokoban")
        backward_puzzle = forwardAStar.game.initializeBackwardPuzzle(states[i])
        backwardAStar = Astar(backward_puzzle, "Sokoban", True)
    
def biBaseWithLearning(games):
    """
    Bidirectional search with online learning from neural network heuristics.
    
    Args:
        games (list): List of initial game states.
    """

    nn = NN(10)
    forwardAStar.nn = nn
    backwardAStar.nn = nn
    if "finalSok3" in os.listdir("."):
        nn.model.load_weights('finalSok3')
        ### NOTES: while training current puzzle, call neural network with predict. when we terminate we train/update neural network based on successful set
    for i in range(0,1):
        X_train, Y_train, h_matrix, path_cost = bi_neural_run()
        update_model(x_train=X_train, y_train=Y_train, h_matrix=h_matrix, path_cost=path_cost, nn=nn)
        break
        forwardAStar = Astar(states[i], "Sokoban")
        backward_puzzle = forwardAStar.game.initializeBackwardPuzzle(states[i])
        backwardAStar = Astar(backward_puzzle, "Sokoban", True)
    
    #h = find
    pass



def bidirectionalAutoRun(running, is_completed):
    """
    Automated GUI execution of bidirectional search.
    
    Args:
        running (bool): Flag indicating if the game is running.
        is_completed (bool): Flag indicating if the search is completed.
    """
    current_forward_map = forwardAStar.puzzle
    current_backward_map = backwardAStar.puzzle
    isForward = True
    while running:
        # poll for events
        # pygame.QUIT event means the user clicked X to close your window
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN and is_completed == False:
                mouse = pygame.mouse.get_pos()
                if flip_button.command(mouse[0], mouse[1]) == True:
                    if isForward:
                        draw_bidirectional_screen(current_backward_map, screen, isForward)
                    else:
                        draw_bidirectional_screen(current_forward_map, screen, isForward)
                    isForward = not isForward
            
            is_front_solution, current_forward_map = forwardAStar.stepAstar()
            is_back_solution, current_backward_map = backwardAStar.stepAstar()
            encoded_forward_map = forwardAStar.game.encodeMap(current_forward_map) 
            encoded_backward_map = backwardAStar.game.encodeMap(current_backward_map)
            # if encoded_backward_map == encoded_forward_map:
                
            #     is_completed= True
            #     draw_finish_screen(current_forward_map, screen)
            #     continue 
            # elif is_front_solution == True or is_back_solution == True:
                
            #     is_completed= True
            #     print("Did not Converge")
            #     draw_finish_screen(current_backward_map, screen)
            #     continue
            if isForward:
                draw_bidirectional_screen(current_forward_map, screen, isForward)
            else:
                draw_bidirectional_screen(current_backward_map, screen, isForward)
            pygame.time.delay(10)

    # next_map = aStar.stepAstar()
    # draw_game(next_map)
    # fill the screen with a color to wipe away anything from last frame
    

    # RENDER YOUR GAME HERE

    # flip() the display to put your work on screen
        pygame.display.flip()

        clock.tick(60)  # limits FPS to 60

    pygame.quit()



def bidirectionalStepRun(running, is_completed):
    """
    Manual step-by-step GUI execution of bidirectional search.
    
    Args:
        running (bool): Flag indicating if the game is running.
        is_completed (bool): Flag indicating if the search is completed.
    """
    current_forward_map = forwardAStar.puzzle
    current_backward_map = backwardAStar.puzzle
    isForward = True
    while running:
        # poll for events
        # pygame.QUIT event means the user clicked X to close your window
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN and is_completed == False:
                mouse = pygame.mouse.get_pos()
                if button.command(mouse[0], mouse[1]) == True:
                    is_front_solution, current_forward_map = forwardAStar.stepAstar()
                    is_back_solution, current_backward_map = backwardAStar.stepAstar()
                    encoded_forward_map = forwardAStar.game.encodeMap(current_forward_map) 
                    encoded_backward_map = backwardAStar.game.encodeMap(current_backward_map)
                    if encoded_backward_map == encoded_forward_map:
                        
                        is_completed= True
                        draw_finish_screen(current_forward_map, screen)
                        continue 
                    elif is_front_solution == True or is_back_solution == True:
                        
                        is_completed= True
                        print("Did not Converge")
                        draw_finish_screen(current_backward_map, screen)
                        continue
                    
                    if isForward:
                        draw_bidirectional_screen(current_forward_map, screen, isForward)
                    else:
                        draw_bidirectional_screen(current_backward_map, screen, isForward)
                    
                    
                elif flip_button.command(mouse[0], mouse[1]) == True:
                    isForward = not isForward
                    if isForward:
                        draw_bidirectional_screen(current_forward_map, screen, isForward)
                    else:
                        draw_bidirectional_screen(current_backward_map, screen, isForward)
                    
    # next_map = aStar.stepAstar()
    # draw_game(next_map)
    # fill the screen with a color to wipe away anything from last frame
    

    # RENDER YOUR GAME HERE

    # flip() the display to put your work on screen
        pygame.display.flip()

        clock.tick(60)  # limits FPS to 60

    pygame.quit()


if __name__ == "__main__":
    args = parse_arguments()
    
    # Mapping new argument names to old names for compatibility with the rest of the script
    # (Or I can update the rest of the script, but mapping is safer for a quick refactor)
    args.with_or_without_pygame = args.visual
    args.forward_or_bidirectional = args.mode
    args.with_learning = args.learning
    args.with_noise = args.noise
    args.with_dummy_data = args.dummy_data

    states = get_data(args.with_dummy_data == "Yes")
    only_one_state = states[0]





    if args.forward_or_bidirectional == "forward":
        
        pygame.init()
        screen = pygame.display.set_mode((640, 640))
        clock = pygame.time.Clock()
        running = True
        is_completed = False
        backward_game = SokobanGame.initializeBackwardPuzzle(only_one_state)
        button = draw_game(only_one_state, screen)
        aStar = Astar(only_one_state, "Sokoban")
        aStar.initAstar()
        if args.with_or_without_pygame == 'False':
            if args.with_learning == "on":
                baseWithLearning(states)
                sys.exit(1)
            baseRun(states, args.with_noise, aStar=aStar)
            sys.exit(0)
        
        
        if args.iteration_type == "auto":
            autoGUIRun(running, is_completed)
        elif args.iteration_type == "step" :
            stepGUIRun(running, is_completed)

    elif args.forward_or_bidirectional == "bidirectional":
        pygame.init()
        pygame.font.init()
        screen = pygame.display.set_mode((1280, 640))
        clock = pygame.time.Clock()
        running = True
        is_completed = False
        
        forwardAStar = Astar(only_one_state, "Sokoban")
        backward_puzzle = forwardAStar.game.initializeBackwardPuzzle(only_one_state)
        backwardAStar = Astar(backward_puzzle, "Sokoban", True)
        forwardAStar.initAstar()
        backwardAStar.initAstar()


        if args.with_or_without_pygame == 'False':
            if args.front_to_front == "yes":
                biBaseFF(states, args.with_noise, forwardAStar, backwardAStar)
                sys.exit(0)
            if args.anchor_search == "yes":
                biBaseAnchorSearch(states, only_one_state, backward_puzzle, args.with_learning=="on", args.with_training=="yes")
                sys.exit(0)
            if args.ttbs == "yes":
                biBaseTTBS(states, args.with_learning=="on", args.with_training=="yes")
                sys.exit(0)
            biBaseRun(states, args.with_noise, forwardAStar, backwardAStar)
            sys.exit(0)
        if args.with_or_without_pygame == 'True':
            if args.anchor_search == "yes":
                biBaseAnchorSearchStep(only_one_state, backward_puzzle, args.with_learning=="on")
                sys.exit(0)
        if args.iteration_type == "auto":
            bidirectionalAutoRun(running, is_completed)
        elif args.iteration_type == "step":
            bidirectionalStepRun(running, is_completed)