# Example file showing a basic pygame "game loop"
import pygame
from pygame_files.drawGame import draw_game, draw_finish_screen, draw_bidirectional_screen, redrawText
from getData import get_data
from astar import Astar
import sys
import argparse
from tqdm import tqdm
import time
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
            
            is_solution, next_map = aStar.stepAstar()
            if is_solution:
                print("made it")
                completed = True
                end_Map = next_map
            pbar.update(1) # Increment the counter by 1
            i += 1
            #pygame.display.flip()

            #clock.tick(60)  # limits FPS to 60
    draw_game(end_Map, screen)
    pygame.display.flip()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                break
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
                    is_solution, next_map = aStar.stepAstar()
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

def biBaseRun():
    start_time = time.time()
    completed = False
    converged = False
    current_forward_map = None
    current_backward_map = None
    with tqdm(total=None, desc="Searching ", unit="states") as pbar:
        i = 0
        while not completed:
            elapsed_time = time.time() - start_time
            if elapsed_time > 600:
                print("too long")
                break
            is_front_solution, current_forward_map = forwardAStar.stepAstar()
            is_back_solution, current_backward_map = backwardAStar.stepAstar()
            encoded_forward_map = forwardAStar.game.encodeMap(current_forward_map) 
            encoded_backward_map = backwardAStar.game.encodeMap(current_backward_map)
            if encoded_backward_map == encoded_forward_map:
                print("made it")
                completed = True
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
    draw_game(current_forward_map)
    pygame.display.flip()
    isForward = True
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                break
            if event.type == pygame.MOUSEBUTTONDOWN and is_completed == False:
                mouse = pygame.mouse.get_pos()
                if flip_button.command(mouse[0], mouse[1]) == True:
                    if isForward:
                        draw_bidirectional_screen(current_backward_map, screen, isForward)
                    else:
                        draw_bidirectional_screen(current_forward_map, screen, isForward)
                    isForward = not isForward
        pygame.display.flip()
        clock.tick(60)


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
                    
                    
                elif flip_button.command(mouse[0], mouse[1]) == True:
                    if isForward:
                        draw_bidirectional_screen(current_backward_map, screen, isForward)
                    else:
                        draw_bidirectional_screen(current_forward_map, screen, isForward)
                    isForward = not isForward

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

    args = parser.parse_args()
    states = get_data()
    only_one_state = states[0]




    pygame.init()
    screen = pygame.display.set_mode((640, 640))
    clock = pygame.time.Clock()
    running = True
    is_completed = False
    if args.forward_or_bidirectional == "forward":
        
        button = draw_game(only_one_state, screen)
        aStar = Astar(only_one_state, "Sokoban")
        aStar.initAstar()
        if args.with_or_without_pygame == 'False':
            baseRun()
            sys.exit(0)
        if args.iteration_type == "auto":
            autoGUIRun(running, is_completed)
        elif args.iteration_type == "step" :
            stepGUIRun(running, is_completed)

    elif args.forward_or_bidirectional == "bidirectional":
        pygame.font.init()
        
        button, flip_button = draw_bidirectional_screen(only_one_state, screen, True)
        forwardAStar = Astar(only_one_state, "Sokoban")
        backward_puzzle = forwardAStar.game.initializeBackwardPuzzle(only_one_state)
        backwardAStar = Astar(backward_puzzle, "Sokoban")
        forwardAStar.initAstar()
        backwardAStar.initAstar()
        if args.with_or_without_pygame == 'False':
            biBaseRun()
            sys.exit(0)
        if args.iteration_type == "auto":
            bidirectionalAutoRun(running, is_completed)
        elif args.iteration_type == "step":
            bidirectionalStepRun(running, is_completed)