import pygame
from getData import get_data

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
   
    arrow = pygame.image.load("pygame_files/arrow.png")
    screen.blit(arrow, (640 - arrow.get_width(),480 - arrow.get_height()))
    def click(obj, mouse_x, mouse_y, x ,y):
        if (x  <= mouse_x <= 640) and (y <= mouse_y <= 480):
            return True
        return False
    arrow_btn = Button(arrow, 640 - arrow.get_width(),480 - arrow.get_height(), click  )
    return arrow_btn

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