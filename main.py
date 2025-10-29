# Example file showing a basic pygame "game loop"
import pygame
from pygame_files.drawGame import draw_game, draw_finish_screen
from getData import get_data
from astar import Astar
# pygame setup
pygame.init()
screen = pygame.display.set_mode((640, 480))
clock = pygame.time.Clock()
running = True
states = get_data()
only_one_state = states[0]
button = draw_game(only_one_state, screen)
aStar = Astar(only_one_state, "Sokoban")
aStar.initAstar()
is_completed = False
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