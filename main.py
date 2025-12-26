# Example file showing a basic pygame "game loop"
import pygame
from pygame_files.drawGame import draw_game, draw_finish_screen, draw_bidirectional_screen, redrawText
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
# pygame setup
# pygame.init()

# screen = pygame.display.set_mode((640, 640))
# clock = pygame.time.Clock()
# running = True
# states = get_data()
# only_one_state = states[0]
# button = draw_game(only_one_state, screen)
# aStar = Astar(only_one_state, "Sokoban")
# aStar.initAstar()

# is_completed = False

def baseRun(states, with_noise, aStar):
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

def biBaseRun(states, with_noise, forwardAStar, backwardAStar):
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
    ## arg parsing
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--with_or_without_pygame',
        default="True",
        type=str,
        help="True if they want visual, False then it just runs auto without visuals"
    )
    parser.add_argument(
        '--iteration_type',
        type=str,
        default="auto",
        help="auto for automatic, step for clicking arrow"
    )
    parser.add_argument(
        '--forward_or_bidirectional',
        type=str,
        default="forward",
        help="forward for forward search and bidirectional for bidirectional search"
    )
    parser.add_argument(
        '--with_learning',
        type=str,
        default="off",
        help="on for learning using the nn.py, otherwise off for standard aStar"
    )
    parser.add_argument(
        "--front_to_front",
        type=str,
        default="no",
        help="if yes then to front to front learning. otherwise to meet in the middle learning"
    )

    parser.add_argument(
        "--with_noise",
        type=str,
        default="off",
        help="if additive, then add random sample from normal distribution to score. if multiplicative,then multiply the noise"
    )


    parser.add_argument(
        "--with_dummy_data",
        type=str,
        default="No",
        help="If Yes, then get very simple puzzles from test_box.txt. Created in order to make sure convergence during intial development on learning"
    )

    

    args = parser.parse_args()
    states = get_data(args.with_dummy_data == "Yes")
    only_one_state = states[0]





    if args.forward_or_bidirectional == "forward":
        
        pygame.init()
        screen = pygame.display.set_mode((640, 640))
        clock = pygame.time.Clock()
        running = True
        is_completed = False
        # print(SokobanGame.decodeMap("0000000000000000000000000000000000000000000000111000024124000003211110000001141000001111100000000000"))
        backward_game = SokobanGame.initializeBackwardPuzzle(SokobanGame.decodeMap("0000000000000000000000000000000000000000000000111000024124000003211110000001141000001111100000000000"))
        # print(backward_game)
        print(SokobanGame.encodeMap(backward_game))
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
        screen = pygame.display.set_mode((640, 640))
        clock = pygame.time.Clock()
        running = True
        is_completed = False
        button, flip_button = draw_bidirectional_screen(only_one_state, screen, True)
        forwardAStar = Astar(only_one_state, "Sokoban")
        backward_puzzle = forwardAStar.game.initializeBackwardPuzzle(only_one_state)
        backwardAStar = Astar(backward_puzzle, "Sokoban", True)
        forwardAStar.initAstar()
        backwardAStar.initAstar()
        if args.with_or_without_pygame == 'False':
            if args.with_learning == "on":
                biBaseWithLearning(states)

                sys.exit(0)
            if args.front_to_front == "yes":
                biBaseFF(states, args.with_noise, forwardAStar, backwardAStar)
                sys.exit(0)
            biBaseRun(states, args.with_noise, forwardAStar, backwardAStar)
            sys.exit(0)


        if args.iteration_type == "auto":
            bidirectionalAutoRun(running, is_completed)
        elif args.iteration_type == "step":
            bidirectionalStepRun(running, is_completed)