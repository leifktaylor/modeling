""" Quest - An epic journey.

Simple demo that demonstrates PyTMX and pyscroll.

requires pygame and pytmx.

https://github.com/bitcraft/pytmx

pip install pytmx
"""
import os.path

import pygame
from pygame.locals import *
from pytmx.util_pygame import load_pygame

import pyscroll
import pyscroll.data
from pyscroll.group import PyscrollGroup

import graphics.eztext as eztext

from graphics.graphictext import draw_lines, draw_text, InputLog


# define configuration variables here
ROOM_DIR = 'gameobjects/room'
SPRITE_DIR = 'graphics/sprites'
TILESET_DIR = 'graphics/tilesets'


MAP_FILENAME = 'grasslands.tmx'


# simple wrapper to keep the screen resizeable
def init_screen(width, height):
    screen = pygame.display.set_mode((width, height), pygame.RESIZABLE)
    return screen


# make loading maps a little easier
def get_map(filename):
    return os.path.join(ROOM_DIR, filename)


# make loading sprites a little easier
def load_sprite(filename):
    return pygame.image.load(os.path.join(SPRITE_DIR, filename))


# make loading tilesets a little easier
def load_tileset(filename):
    return pygame.image.load(os.path.join(TILESET_DIR, filename))


class Hero(pygame.sprite.Sprite):
    """ Our Hero

    The Hero has three collision rects, one for the whole sprite "rect" and
    "old_rect", and another to check collisions with walls, called "feet".

    The position list is used because pygame rects are inaccurate for
    positioning sprites; because the values they get are 'rounded down'
    as integers, the sprite would move faster moving left or up.

    Feet is 1/2 as wide as the normal rect, and 8 pixels tall.  This size size
    allows the top of the sprite to overlap walls.  The feet rect is used for
    collisions, while the 'rect' rect is used for drawing.

    There is also an old_rect that is used to reposition the sprite if it
    collides with level walls.
    """

    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = load_sprite('5.png').convert_alpha()
        self.velocity = [0, 0]
        self._position = [0, 0]
        self._old_position = self.position
        self.rect = self.image.get_rect()
        self.feet = pygame.Rect(0, 0, self.rect.width * .5, 8)
        self.grid_pos = [0, 0]
        self.grid_x = self.grid_pos[0]
        self.grid_y = self.grid_pos[1]

        # move_timer is determined by speed stat, dictates how often you can move on the map
        self.move_timer = 0
        self.move_speed = 30
        self.target_coords = None

    @property
    def position(self):
        return list(self._position)

    @position.setter
    def position(self, value):
        self._position = list(value)

    def update(self, dt):
        self._old_position = self._position[:]
        self._position[0] += self.velocity[0] * dt
        self._position[1] += self.velocity[1] * dt
        self.rect.topleft = self._position
        self.feet.midbottom = self.rect.midbottom
        self.grid_pos = [coord / 16 for coord in self.position]

        # Subtract from move timer
        # if self.move_timer > 0:
        #     self.move_timer -= 1

    def move_back(self, dt):
        """ If called after an update, the sprite can move back
        """
        self._position = self._old_position
        self.rect.topleft = self._position
        self.feet.midbottom = self.rect.midbottom


class QuestGame(object):
    """ This class is a basic game.

    This class will load data, create a pyscroll group, a hero object.
    It also reads input and moves the Hero around the map.
    Finally, it uses a pyscroll group to render the map and Hero.
    """
    filename = get_map(MAP_FILENAME)

    def __init__(self):

        # true while running
        self.running = False

        # load data from pytmx
        tmx_data = load_pygame(self.filename)

        # setup level geometry with simple pygame rects, loaded from pytmx
        self.walls = list()
        for object in tmx_data.objects:
            self.walls.append(pygame.Rect(
                object.x, object.y,
                object.width, object.height))

        # create new data source for pyscroll
        map_data = pyscroll.data.TiledMapData(tmx_data)

        # create new renderer (camera)
        self.map_layer = pyscroll.BufferedRenderer(map_data, screen.get_size())
        self.map_layer.zoom = 5

        # pyscroll supports layered rendering.  our map has 3 'under' layers
        # layers begin with 0, so the layers are 0, 1, and 2.
        # since we want the sprite to be on top of layer 1, we set the default
        # layer for sprites as 2
        self.group = PyscrollGroup(map_layer=self.map_layer, default_layer=2)

        self.hero = Hero()

        # put the hero in the center of the map
        self.hero.position = [160, 160]
        # self.hero.position = self.map_layer.map_rect.center

        # add our hero to the group
        self.group.add(self.hero)

        # self.text_box = eztext.Input(maxlength=90, color=(255, 255, 255), x=30, y=860,
        #                              font=pygame.font.Font(None, 30), prompt=': ')

        self.text_box = eztext.Input(maxlength=90, color=(255, 255, 255), x=30, y=860,
                                     font=pygame.font.Font(None, 30), prompt=': ')

        # Create InputLog
        self.inputlog = InputLog(coords=(30, 840), max_length=10, size=28, spacing=18)
        # Create Combatlog
        self.combatlog = InputLog(coords=(1050, 860), max_length=10, size=28, spacing=18)

    def draw(self, surface):

        # center the map/screen on our Hero
        self.group.center(self.hero.rect.center)

        # draw the map and all sprites
        self.group.draw(surface)

    def handle_input(self):
        """ Handle pygame input events
        """
        # poll = pygame.event.poll

        # event = poll()
        events = pygame.event.get()

        # while event:
        for event in events:
            # update text_box

            if event.type == QUIT:
                self.running = False
                break

            # This is where key press events go
            elif event.type == KEYDOWN:

                msgvalue = self.text_box.update(events)
                if msgvalue:
                    # r = a.send(msgvalue)
                    self.inputlog.add_line(msgvalue)

                if event.key == K_ESCAPE:
                    self.running = False
                    break

                # elif event.key == K_EQUALS:
                #     self.map_layer.zoom += .25
                #
                # elif event.key == K_MINUS:
                #     value = self.map_layer.zoom - .25
                #     if value > 0:
                #         self.map_layer.zoom = value

            # this will be handled if the window is resized
            elif event.type == VIDEORESIZE:
                init_screen(event.w, event.h)
                self.map_layer.set_size((event.w, event.h))

            elif event.type == KEYUP:
                if event.key == K_LSHIFT or event.key == K_RSHIFT:
                    self.text_box.shifted = False
            # event = poll()

        # using get_pressed is slightly less accurate than testing for events
        # but is much easier to use.
        pressed = pygame.key.get_pressed()

        # Move timer is determined by SPD stat
        if 1 == 1:
            # Reset move timer based on SPD stat.
            if pressed[K_UP]:
                # self.hero.target_coords = [current_x, current_y - 16]
                # self.hero._position[1] -= 16
                # self.hero.move_timer = self.hero.move_speed
                self.hero.velocity[1] = -self.hero.move_speed
            elif pressed[K_DOWN]:
                # self.hero._position[1] += 16
                # self.hero.move_timer = self.hero.move_speed
                self.hero.velocity[1] = self.hero.move_speed
            else:
                self.hero.velocity[1] = 0

            if pressed[K_LEFT]:
                # self.hero._position[0] -= 16
                # self.hero.move_timer = self.hero.move_speed
                self.hero.velocity[0] = -self.hero.move_speed
            elif pressed[K_RIGHT]:
                # self.hero._position[0] += 16
                # self.hero.move_timer = self.hero.move_speed
                self.hero.velocity[0] = self.hero.move_speed
            else:
                self.hero.velocity[0] = 0

    def update(self, dt):
        """ Tasks that occur over time should be handled here
        """
        self.group.update(dt)

        # check if the sprite's feet are colliding with wall
        # sprite must have a rect called feet, and move_back method,
        # otherwise this will fail
        for sprite in self.group.sprites():
            if sprite.feet.collidelist(self.walls) > -1:
                sprite.move_back(dt)

    def run(self):
        """ Run the game loop
        """
        clock = pygame.time.Clock()
        self.running = True

        from collections import deque
        times = deque(maxlen=30)

        try:
            while self.running:
                dt = clock.tick(60) / 1000.
                times.append(clock.get_fps())
                # print(sum(times) / len(times))

                self.handle_input()
                self.update(dt)
                self.draw(screen)

                # debug draw co-ordinates
                # pos = [coord/16 for coord in self.hero.position]
                draw_text(str(self.hero.position), screen, coords=(10, 10))

                # blit text_box on the sceen
                self.text_box.draw(screen)

                # blit InputLog to screen
                self.inputlog.draw(screen)
                self.combatlog.draw(screen)
                self.combatlog.add_line('tesssstingggg wow it is working horaaaaa!!!!!!!!')

                # debug draw current properties of tile
                # props = txmdata.get_tile_properties(x, y, layer)

                pygame.display.flip()

        except KeyboardInterrupt:
            self.running = False


if __name__ == "__main__":
    pygame.init()
    pygame.font.init()
    screen = init_screen(1600, 900)
    pygame.display.set_caption('Little v0.0.1')

    try:
        game = QuestGame()
        game.run()
    except:
        pygame.quit()
        raise
