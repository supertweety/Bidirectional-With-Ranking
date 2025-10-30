# Example file showing a basic pygame "game loop"
import pygame
from pygame_files.drawGame import draw_game, draw_finish_screen
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
    with tqdm(total=None, desc="Searching ", unit="states") as pbar:
        i = 0
        while True:
            elapsed_time = time.time() - start_time
            if elapsed_time > 600:
                print("too long")
                break
            is_solution, next_map = aStar.stepAstar()
            if is_solution:
                print("made it", aStar.game.encodeMap(next_map))
                break
                
            pbar.update(1) # Increment the counter by 1
            i += 1


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

def bidirectionalAutoRun():
    combined_queue = set()
    pass

def bidirectionalStepRun(running, is_completed):
    combined_queue = set()
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


    pass

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

    if args.with_or_without_pygame == 'False':
        aStar = Astar(only_one_state, "Sokoban")
        aStar.initAstar()
        baseRun()
        sys.exit(0)


    pygame.init()
    screen = pygame.display.set_mode((640, 640))
    clock = pygame.time.Clock()
    running = True
    button = draw_game(only_one_state, screen)
    if args.forward_or_bidirectional == "forward":
        aStar = Astar(only_one_state, "Sokoban")
        aStar.initAstar()
        is_completed = False
        if args.iteration_type == "auto":
            autoGUIRun(running, is_completed)
        elif args.iteration_type == "step" :
            stepGUIRun(running, is_completed)
        else:
            print("no wrong iteration type")
            sys.exit(1)
    elif args.forward_or_bidirectional == "bidirectional":
        forwardAStar = Astar(only_one_state, "Sokoban")
        backward_puzzle = Astar.game.initializeBackwardPuzzle(only_one_state)
        backwardAStar = Astar(backward_puzzle, "Sokoban")