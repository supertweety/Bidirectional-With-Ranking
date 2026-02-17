import pygame
from getData import get_data
import numpy as np
class Button:
    def __init__(self, obj, x, y, onClick):
        self.obj = obj
        self.onClick = onClick
        self.x = x
        self.y = y
    def command(self, mouse_width, mouse_height):
        return self.onClick(self.obj, mouse_width, mouse_height, self.x, self.y)

def draw_game(board, screen, input = None):
    screen.fill("black")
    wall = pygame.image.load("pygame_files/wall.png")
    wall_width = wall.get_width()
    wall_height = wall.get_height()

    block = pygame.image.load("pygame_files/block.png")
    floor = pygame.image.load("pygame_files/floor.png")
    target = pygame.image.load("pygame_files/target.png")
    player = None
    if input == None:
        ## start down
        player = pygame.image.load("pygame_files/player_sprites/player_down.png")
    else:
        if input == "left":
            player = pygame.image.load("pygame_files/player_sprites/player_left.png")
        elif input == "right":
            player = pygame.image.load("pygame_files/player_sprites/player_right.png")
        elif input == "up":
            player = pygame.image.load("pygame_files/player_sprites/player_up.png")
        else:
            player = pygame.image.load("pygame_files/player_sprites/player_down.png")
    for i in range(len(board)):
        for j in range(len(board[i])):
            if board[j][i] == 0:
                screen.blit(wall, (wall_width*i, wall_height*j))
            elif board[j][i] == 1:
                screen.blit(floor, (floor.get_width()*i, floor.get_height()*j))
            elif board[j][i] == 2:
                screen.blit(target, (target.get_width()*i, target.get_height()*j))
            elif board[j][i] == 4:
                screen.blit(block, (block.get_width()*i, block.get_height()*j))
            elif board[j][i] == 3:
                screen.blit(player, (player.get_width()*i, player.get_height()*j)) 
   
    arrow = pygame.image.load("pygame_files/arrow.png")
    screen.blit(arrow, (640 - arrow.get_width(),640 - arrow.get_height()))
    def click(obj, mouse_x, mouse_y, x ,y):
        if (x  <= mouse_x <= 640) and (y <= mouse_y <= 640):
            return True
        return False
    arrow_btn = Button(arrow, 640 - arrow.get_width(),640 - arrow.get_height(), click  )
    return arrow_btn

def draw_side_by_side(board_left, board_right, screen, input_left=None, input_right=None):
    # 1. Clear the main screen
    screen.fill("black")
    
    # 2. Define the size for each half
    # Assuming your screen is, for example, 1280x640
    width, height = screen.get_width() // 2, screen.get_height()
    
    # 3. Create two temporary surfaces (sub-screens)
    left_surface = pygame.Surface((width, height))
    right_surface = pygame.Surface((width, height))
    
    # 4. Use your existing logic to draw on the sub-surfaces
    # Note: You should modify draw_game to accept a surface instead of the main screen
    btn_left = draw_game(board_left, left_surface, input_left)
    btn_right = draw_game(board_right, right_surface, input_right)
    
    # 5. Blit the two surfaces onto the main screen
    screen.blit(left_surface, (0, 0))          # Left half
    screen.blit(right_surface, (width, 0))       # Right half
    
    return btn_left, btn_right

def draw_bidirectional_screen(board,screen, direction, input = None):
    screen.fill("black")
    wall = pygame.image.load("pygame_files/wall.png")
    wall_width = wall.get_width()
    wall_height = wall.get_height()

    block = pygame.image.load("pygame_files/block.png")
    floor = pygame.image.load("pygame_files/floor.png")
    target = pygame.image.load("pygame_files/target.png")
    player = None
    if input == None:
        ## start down
        player = pygame.image.load("pygame_files/player_sprites/player_down.png")
    else:
        if input == "left":
            player = pygame.image.load("pygame_files/player_sprites/player_left.png")
        elif input == "right":
            player = pygame.image.load("pygame_files/player_sprites/player_right.png")
        elif input == "up":
            player = pygame.image.load("pygame_files/player_sprites/player_up.png")
        else:
            player = pygame.image.load("pygame_files/player_sprites/player_down.png")
    for i in range(len(board)):
        for j in range(len(board[i])):
            if board[j][i] == 0:
                screen.blit(wall, (wall_width*i, wall_height*j))
            elif board[j][i] == 1:
                screen.blit(floor, (floor.get_width()*i, floor.get_height()*j))
            elif board[j][i] == 2:
                screen.blit(target, (target.get_width()*i, target.get_height()*j))
            elif board[j][i] == 4:
                screen.blit(block, (block.get_width()*i, block.get_height()*j))
            elif board[j][i] == 3:
                screen.blit(player, (player.get_width()*i, player.get_height()*j)) 
   
    arrow = pygame.image.load("pygame_files/arrow.png")
    screen.blit(arrow, (640 - arrow.get_width(),640 - arrow.get_height()))
    def click(obj, mouse_x, mouse_y, x ,y):
        if (x  <= mouse_x <= 640) and (y <= mouse_y <= 640):
            return True
        return False
    arrow_btn = Button(arrow, 640 - arrow.get_width(),640 - arrow.get_height(), click  )

    reverse = pygame.image.load("pygame_files/reverse.png")
    screen.blit(reverse, (640 - reverse.get_width(), 0))
    reverse_btn = Button(reverse, 640 - reverse.get_width(), 0, click  )
    if direction == True:
        redrawText("Forward", screen)
    else:
        redrawText("Backward", screen)
    return arrow_btn ,reverse_btn

def redrawText(text,screen):
    my_font = pygame.font.SysFont('Comic Sans MS', 30)
    text_surface = my_font.render(text, False, (0, 0, 0))
    screen.blit(text_surface, (0,0))

def draw_finish_screen(board, screen, input = None):
    screen.fill("black")
    wall = pygame.image.load("pygame_files/wall.png")
    wall_width = wall.get_width()
    wall_height = wall.get_height()

    block = pygame.image.load("pygame_files/block.png")
    floor = pygame.image.load("pygame_files/floor.png")
    target = pygame.image.load("pygame_files/target.png")
    player = None
    if input == None:
        ## start down
        player = pygame.image.load("pygame_files/player_sprites/player_down.png")
    else:
        if input == "left":
            player = pygame.image.load("pygame_files/player_sprites/player_left.png")
        elif input == "right":
            player = pygame.image.load("pygame_files/player_sprites/player_right.png")
        elif input == "up":
            player = pygame.image.load("pygame_files/player_sprites/player_up.png")
        else:
            player = pygame.image.load("pygame_files/player_sprites/player_down.png")
    for i in range(len(board)):
        for j in range(len(board[i])):
            if board[i][j] == 0:
                screen.blit(wall, (wall_width*i, wall_height*j))
            elif board[i][j] == 1:
                screen.blit(floor, (floor.get_width()*i, floor.get_height()*j))
            elif board[i][j] == 2:
                screen.blit(target, (target.get_width()*i, target.get_height()*j))
            elif board[i][j] == 4:
                screen.blit(block, (block.get_width()*i, block.get_height()*j))
            elif board[i][j] == 3:
                screen.blit(player, (player.get_width()*i, player.get_height()*j)) 
   
    print("DONE")