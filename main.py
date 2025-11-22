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
from learn import update_model
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

def baseRun():
    start_time = time.time()
    completed = False
    end_Map = None
    with tqdm(total=None, desc="Searching ", unit="states") as pbar:
        i = 0
        while not completed:
            elapsed_time = time.time() - start_time
            if elapsed_time > 600:
                print("too long")
                break
            
            is_solution, next_map, _ = aStar.stepAstar()
            if is_solution:
                print("made it")
                completed = True
                end_Map = next_map
            pbar.update(1) # Increment the counter by 1
            i += 1
            #pygame.display.flip()

            #clock.tick(60)  # limits FPS to 60
    path = aStar.reconstructSuccessfulPath(end_Map)
    index = len(path) - 1
    print(len(path))
    #draw_game(end_Map, screen)
    pygame.display.flip()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                break

            if event.type == pygame.MOUSEBUTTONDOWN and is_completed == False and index >= 0:
                mouse = pygame.mouse.get_pos()
                if button.command(mouse[0], mouse[1]) == True:
                    draw_game(aStar.game.decodeMap(path[index]), screen)
                    index -= 1

        pygame.display.flip()
        clock.tick(60)
    pygame.quit()

def autoGUIRun(running, is_completed):
    while running:
        # poll for events
        # pygame.QUIT event means the user clicked X to close your window
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        is_solution, next_map = aStar.stepAstar()
        if is_solution:
            is_completed= True
            draw_finish_screen(next_map, screen)
            continue
        draw_game(next_map, screen)
        pygame.time.delay(10)

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

def biBaseMM(game_states):
    # print(game_states)
    i = 0
    global forwardAStar, backwardAStar
    for state in game_states:
        biBaseRun()
        forwardAStar = Astar(state, "Sokoban")
        backward_puzzle = forwardAStar.game.initializeBackwardPuzzle(state)
        backwardAStar = Astar(backward_puzzle, "Sokoban", True)
        forwardAStar.initAstar()
        backwardAStar.initAstar()
        if i > 4:
            break

def biBaseRun():
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
            # print(front_called, back_called)
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

def neural_run():

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
    
def biBaseWithLearning(games):

    nn = NN(10)
    forwardAStar.nn = nn
    backwardAStar.nn = nn
    if "finalSok3" in os.listdir("."):
        nn.model.load_weights('finalSok3')
        ### NOTES: while training current puzzle, call neural network with predict. when we terminate we train/update neural network based on successful set
    for i in range(0,1):
        X_train, Y_train, h_matrix, path_cost = neural_run()
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
        help="learning using the nn.py"
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
        button = draw_game(only_one_state, screen)
        aStar = Astar(only_one_state, "Sokoban")
        aStar.initAstar()
        if args.with_or_without_pygame == 'False':
            if args.with_learning == "on":
                print("Forward search with learning not supported for now")
                sys.exit(1)
            baseRun()
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
        #print(forwardAStar.game.encodeMap(backward_puzzle))
        backwardAStar = Astar(backward_puzzle, "Sokoban", True)
        forwardAStar.initAstar()
        backwardAStar.initAstar()
        if args.with_or_without_pygame == 'False':
            if args.with_learning == "on":
                biBaseWithLearning(states)

                sys.exit(0)
            biBaseMM(states)
            sys.exit(0)


        if args.iteration_type == "auto":
            bidirectionalAutoRun(running, is_completed)
        elif args.iteration_type == "step":
            bidirectionalStepRun(running, is_completed)