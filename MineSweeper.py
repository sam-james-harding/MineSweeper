# modules
import pygame
import random
import datetime

# options
name = 'MineSweeper' # window title
tiles_x = 10 # number of tiles horizontally
tiles_y = 8 # number of tiles vertically
mine_no = 10 # number of mines on board
        # colours
base_colour1, base_colour2 = (75,82,251), (45,62,250) # colours for uncleared tiles
cleared_colour = (109, 242, 46) # colour for non_mined, cleared tiles
text_colour = (255,70,70) # colour for tile numbers

# setup
pygame.init()
pygame.font.init()
myfont = pygame.font.SysFont(None, 60)
screenx = 50*tiles_x
screeny = 50*tiles_y
screen = pygame.display.set_mode((screenx, screeny))
pygame.display.set_caption(name)
clock = pygame.time.Clock()

# resources
boom = pygame.mixer.Sound('Resources/boom.wav')
ding = pygame.mixer.Sound('Resources/ding.wav')
dead_face = pygame.transform.scale(pygame.image.load('Resources/dead.png'), (200,200))
win_face = pygame.transform.scale(pygame.image.load('Resources/win.png'), (200,200))

# classes
class Tile():
        '''x and y both start at 1'''
        def __init__(self,x,y, mined=False):
                # basic variables
                self.x = x
                self.y = y
                self.mined = mined
                self.prox_mines = 0
                self.cleared = False
                self.flagged = False
                # uncleared colour
                if (x+y)%2 == 0: self.base_colour = base_colour1
                else: self.base_colour = base_colour2
                self.colour = self.base_colour
                # rect
                self.rec = pygame.Rect((x-1)*50, (y-1)*50, 50, 50)
        def mine_me(self):
                self.mined = True
        def get_pos(self):
                return self.x, self.y
        def clear(self):
                self.cleared = True
                if self.mined: self.colour = (0,0,0)
                else: self.colour = cleared_colour
                self.no_text = myfont.render(str(self.prox_mines), False, text_colour)
                self.no_text_rect = self.no_text.get_rect()
                self.no_text_rect.center = ((self.x-1)*50)+25, ((self.y-1)*50)+25
        def number(self, no):
                self.prox_mines = no
        def flag(self):
                if not self.cleared and not self.flagged:
                        self.colour = (255,0,0)
                if self.flagged and not self.cleared: self.colour = self.base_colour
                self.flagged = not self.flagged
        
def do_game_setup():
        global tile_list
        # lists/arrays and use of them in setup

                # creating main array
        tile_array = []
        temp_row = []
        for i in range(1,tiles_y+1):
                for w in range(1,tiles_x+1):
                        temp_row.append(Tile(w,i))
                tile_array.append(temp_row)
                temp_row = []

                # creating tile list (not array)
        tile_list = []
        for i in range(tiles_y):
                tile_list += tile_array[i]
                
                # mining random tile sample
        bombed_tiles = random.sample(tile_list, mine_no)
        for tile in bombed_tiles:
                tile.mine_me()

                # adjacent tiles
        

                # numbering tiles
        for tile in tile_list:
                prox_tiles = 0
                for sq in adj_tiles(tile):
                        if sq.mined: prox_tiles += 1
                tile.number(prox_tiles)

# other functions

def adj_tiles(tile):
                global tile_list
                x,y = tile.get_pos()
                adj_tiles = []
                for sq in tile_list:
                        if ((sq.get_pos()[0]-x) in (-1,0,1)) and ((sq.get_pos()[1]-y) in (-1,0,1)):
                                if not tile == sq: adj_tiles.append(sq)
                return adj_tiles
        
def clearfrom(tile):
        tile.clear()
        if tile.prox_mines == 0 and not tile.mined:
                for sq in adj_tiles(tile):
                        if not sq.cleared:
                                clearfrom(sq)

def clearspace(tile):
        if tile.prox_mines != 0 or tile.mined: return 0
        checked_tiles = [tile]
        done = False
        while not done:
                clears_found = 0
                for sq in checked_tiles:
                        for near_sq in adj_tiles(sq):
                                if not near_sq in checked_tiles and not near_sq.mined and near_sq.prox_mines == 0:
                                        checked_tiles.append(near_sq)
                                        clears_found += 1
                if clears_found == 0: done = True
        return len(checked_tiles)

def reveal_mines():
        for tile in tile_list:
                if tile.mined: tile.clear()
                       
### start of main looped code (screen classes) ###

class menu():
        def __init__(self):
                self.done = False
                self.title = myfont.render('MineSweeper', False, (0,0,0))
                self.start_text = myfont.render('START', False, (0,0,0))
                self.quit_text = myfont.render('QUIT', False, (0,0,0))
                self.start = pygame.Rect(170,150,160,60)
                self.quit = pygame.Rect(170,260,160,60)
        def Input(self):
                for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                                self.done = True
                        if event.type == pygame.MOUSEBUTTONDOWN:
                                a,b = event.pos
                                if self.start.collidepoint(a,b):
                                        self.done = True
                                        do_game_setup()
                                        game().Play()
                                if self.quit.collidepoint(a,b):
                                        self.done = True
        def Render(self):
                screen.fill((100,100,255))
                screen.blit(self.title,(120,30))
                pygame.draw.rect(screen, (0,255,0), self.start)
                pygame.draw.rect(screen, (255,0,0), self.quit)
                screen.blit(self.start_text,(180,160))
                screen.blit(self.quit_text,(195,270))
                pygame.display.flip()
                clock.tick(60)
        def Play(self):
                while not self.done:
                        self.Input()
                        self.Render()

class game():
        def __init__(self):
                self.done = False
                self.finished = False
                self.dead = False
                self.win = False
        # takes inputs
        def Input(self):
                for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                                self.done = True
                        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                                a,b = event.pos
                                for tile in tile_list:
                                        if tile.rec.collidepoint(a,b) and not tile.flagged:
                                                clearfrom(tile)
                                                if tile.mined:
                                                        reveal_mines()
                                                        boom.play()
                                                        self.dead = True
                                                        self.deathstart = datetime.datetime.now()
                                                else:
                                                        tiles_left = 0
                                                        for tile in tile_list:
                                                                if not tile.cleared:
                                                                        tiles_left += 1
                                                        if tiles_left == mine_no:
                                                                self.win = True
                                                                ding.play()
                                                                self.winstart = datetime.datetime.now()
                                                
                        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
                                a,b = event.pos
                                for tile in tile_list:
                                        if tile.rec.collidepoint(a,b):
                                                tile.flag()
                                                break

        # updates objects
        def Update(self):
                # starting game with largest open area
                highest_clear = 0
                highest_clear_tile = None
                for tile in tile_list:
                        if clearspace(tile) > highest_clear:
                                highest_clear = clearspace(tile)
                                highest_clear_tile = tile
                clearfrom(highest_clear_tile)

                if self.finished:
                        self.done = True
                        menu().Play()
                        

        # renders objects and surfaces
        def Render(self):
                screen.fill((255,255,255))
                for tile in tile_list:
                                pygame.draw.rect(screen, tile.colour, tile.rec)
                                if tile.cleared and tile.prox_mines != 0 and not tile.mined:
                                        screen.blit(tile.no_text, tile.no_text_rect)
                if self.dead:
                        screen.blit(dead_face, (int((50*tiles_x)/2)-100,int((50*tiles_y)/2)-100))
                        if (datetime.datetime.now() - self.deathstart).seconds > 2:
                                self.dead = False
                                self.finished = True
                if self.win:
                        screen.blit(win_face, (int((50*tiles_x)/2)-100,int((50*tiles_y)/2)-100))
                        if (datetime.datetime.now() - self.winstart).seconds > 2:
                                self.win = False
                                self.finished = True

                # frame end setup
                pygame.display.flip()
                clock.tick(60)
        def Play(self):
                while not self.done:
                        self.Input()
                        self.Update()
                        self.Render()
                
menu().Play()
        
pygame.quit()
