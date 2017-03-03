""" Quest - An epic journey.

Simple demo that demonstrates PyTMX and pyscroll.

requires pygame and pytmx.

https://github.com/bitcraft/pytmx

pip install pytmx
"""
from __future__ import division

import pygame
from pygame.locals import *
from pytmx.util_pygame import load_pygame

import pyscroll
import pyscroll.data
from pyscroll.group import PyscrollGroup

import graphics.eztext as eztext
from graphics.graphictext import draw_lines, draw_text, InputLog, InventoryBox

from functions.math import negpos
from mp.client import PacketSizeMismatch
from mp.client import GameClient

from local.camera import Camera
from local.input import PlayerController
from local.remotesprite import RemoteSpriteController, RemoteSprite


# Player starting room
STARTING_ROOM = 'gameobjects/room/test8.tmx'
# Player starting position
STARTING_POSITION = [160, 160]
# Default run speed
MOVE_TIME = 8

# Default Resolution
DEFAULT_RESOLUTION = [900, 506]
# Map camera zoom
MAP_ZOOM = 4.5
# Default Font
FONT = None

# size of walkable tile
TILE_SIZE = 8
# define rate that the server is polled, lower number means more polling
POLL_RATE = 10
# debug messages displayed on screen
DEBUG_MODE = True
# Pyscroll default layer
DEFAULT_LAYER = 2


def init_screen(width, height):
    """Simple wrapper to keep the screen resizeable"""
    # screen = pygame.display.set_mode((width, height), pygame.RESIZABLE)
    screen = pygame.display.set_mode((width, height))
    return screen


class Hero(object):
    """ Our Hero """

    def __init__(self, game, id, sprite, coords):
        """
        :param id: should be same as lifeform.id on server-side
        :param sprite: should be same as lifeform.sprite on server-side
        :param coords: should be same as lifeform.coords in server-side
        """
        # Game object
        self.game = game

        # RemoteSprite object
        self.remotesprite = RemoteSprite(id=id, sprite=sprite, coords=coords)

        # Camera which will follow the hero's remotesprite
        self.camera = Camera(self.remotesprite)

        # 'move_time' is determined by speed stat, the lower this is, the faster you can move from tile to tile
        self.move_time = MOVE_TIME
        self.move_timer = self.move_time
        self.moving = False
        self.target_coords = None

    @property
    def id(self):
        return self.remotesprite.id

    @property
    def rect(self):
        return self.remotesprite.rect

    @property
    def x(self):
        return self.remotesprite.x

    @x.setter
    def x(self, value):
        self.remotesprite.x = value

    @property
    def y(self):
        return self.remotesprite.y

    @y.setter
    def y(self, value):
        self.remotesprite.y = value

    @property
    def position(self):
        return self.remotesprite.position

    @position.setter
    def position(self, value):
        self.remotesprite.position = list(value)

    def update(self, dt):
        self.rect.topleft = self._position

    def move_lifeform(self, coords):
        """
        moves lifeform on grid while checking for collision
        :param coords: [x, y] to move to
        :return:
        """
        if not self.collision_check(coords):
            # Set new coords as target for sprite animation to move to
            self.target_coords = [int(coords[0]), int(coords[1])]
            self.moving = True

            # Update server that we are moving
            # TODO Add this server update
            # self.client.send('move', [self.hero.target_coords])

    def collision_check(self, position, layers=None):
        """
        Checks if given coordinates are occupied by a tile marked 'wall'
        :param position:
        :return:
        """
        if not layers:
            layers = [0, 1]
        else:
            layers = layers
        # Get all tiles at this position, in all layers and check for 'wall' == 'true'
        collide = False
        tile_pos_x = position[0] / TILE_SIZE
        tile_pos_y = position[1] / TILE_SIZE
        tiles = [self.game.map_data.get_tile_properties(tile_pos_x, tile_pos_y, layer) for layer in layers]
        tiles = [tile['wall'] for tile in tiles if tile]
        for wall in tiles:
            if wall == 'true':
                collide = True
        return collide


class Game(object):
    """This class is essentially the Wizard of Oz"""
    def __init__(self, charactername='Zaxim', username='ken', password='mypw', ip='127.0.0.1',
                 current_room=None):
        # Client for issuing requests to server and receiving responses
        self.client = GameClient(charactername=charactername, username=username, password=password, ip=ip)

        # Remote sprite controller
        self.rsc = RemoteSpriteController(self)

        # Rate that chat polls are sent to server
        self.poll_frequency = POLL_RATE
        self.poll_timer = self.poll_frequency
        self.out_going_message = None

        # true while running
        self.running = False

        # load data from pytmx
        if not current_room:
            current_room = STARTING_ROOM
        tmx_data = load_pygame(current_room)
        self.map_data = tmx_data

        # create new data source for pyscroll
        map_data = pyscroll.data.TiledMapData(tmx_data)

        # create new renderer (camera)
        self.map_layer = pyscroll.BufferedRenderer(map_data, screen.get_size())
        self.map_layer.zoom = MAP_ZOOM

        # pyscroll supports layered rendering.
        self.group = PyscrollGroup(map_layer=self.map_layer, default_layer=DEFAULT_LAYER)

        # Add text screen elements
        # Create text box
        text_box_x, text_box_y = self.screen_coords((3, 95))
        self.text_box = eztext.Input(maxlength=90, color=(255, 255, 255), x=text_box_x, y=text_box_y,
                                     font=pygame.font.Font(FONT, 26), prompt=': ')
        # Create InputLog
        self.inputlog = InputLog(coords=self.screen_coords((3, 92)), max_length=10, size=22, spacing=18, font=FONT)
        # Create Combatlog
        self.combatlog = InputLog(coords=(1050, 860), max_length=10, size=22, spacing=18, font=FONT)

        # Login to server:
        # Get room instance and player object id
        response = self.client.login()
        id = response['response']['id']
        sprite = response['response']['sprite']
        coords = response['response']['coords']
        self.hero = Hero(game=self, id=id, sprite=sprite, coords=coords)

        # Player input module
        self.input = PlayerController(game=self)

        # This is late -- ??? TODO This is garbage, current room needs to be discovered way earlier from login()
        self.current_room = response['response']['current_room']
        self.hero.position = STARTING_POSITION
        self.group.add(self.hero.remotesprite)

        self.rsc.initialize()

    @property
    def screen_size(self):
        return pygame.display.Info().current_w, pygame.display.Info().current_h

    def screen_coords(self, coords):
        """
        :param coords: percentage of each axis.  i.e. (50, 50) will put an object in the center of the screen
        :return: Actual co-ords per resolution
        """
        screen_x, screen_y = self.screen_size
        new_x = (coords[0]/100) * screen_x
        new_y = (coords[1]/100) * screen_y
        return new_x, new_y

    def poll_server(self, dt=60):
        """ get remotesprite coordinate updates from server and pass to remotesprite controller """
        self.poll_timer -= dt / 50.
        if self.poll_timer <= 0:
            self.poll_timer = self.poll_frequency
            # Interface with RemoteSpriteController and update all lifeform coords
            self.update_lifeforms()

    def update_lifeforms(self):
        """Update co-ordinates of all remote sprites with new information from server"""
        # Update data on all lifeforms in room
        # TODO: Create remotesprite controller class that is similiar to GOC but for remote sprites
        r = self.client.send('get_coords')
        coords_dict = r['response']
        if coords_dict:
            self.rsc.update_coords(coords_dict)

    def update(self, dt):
        """ Tasks that occur over time should be handled here"""
        self.group.update(dt)
        # update camera
        self.hero.camera.update(dt)

        # STATE: 'moving'
        # (If we are moving to another tile)
        self.hero.move_timer -= dt / 100.
        if self.hero.moving:
            distance_x, distance_y = (self.hero.target_coords[0] - self.hero.x,
                                      self.hero.target_coords[1] - self.hero.y)
            stepx, stepy = (negpos(distance_x), negpos(distance_y))

            self.hero.x += stepx
            self.hero.y += stepy

            if self.hero.move_timer <= 0:
                self.hero.moving = False
                self.hero.position = self.hero.target_coords
                self.hero.position = self.hero.target_coords
                self.client.send('update_coords', [self.hero.x, self.hero.y])

    def draw(self, surface):
        # center the map/screen on our Hero
        self.group.center(self.hero.camera.rect.center)

        # draw the Pyscroll map group
        self.group.draw(surface)

    def run(self):
        """ Run the game loop"""
        clock = pygame.time.Clock()
        self.running = True

        from collections import deque
        times = deque(maxlen=30)

        try:
            while self.running:
                dt = clock.tick(60)
                times.append(clock.get_fps())

                # Update From Server
                try:
                    self.poll_server(dt)
                except PacketSizeMismatch:
                    self.inputlog.add_line('Packet size mismatch!! Ignoring')

                # Handle input and render
                self.input.handle_input(dt)
                self.update(dt)
                self.draw(screen)

                # debug draw co-ordinates
                if DEBUG_MODE:
                    # pos = [coord/16 for coord in self.hero.position]
                    draw_text('hero.position:. . . . {0}'.format(str(self.hero.position)), screen, coords=(10, 10))
                    draw_text('delta t:. . . . . . . {0}'.format(str(dt)), screen, coords=(10, 40))
                    draw_text('server poll:. . . . . {0}'.format(str(self.poll_timer)), screen, coords=(10, 55))
                    draw_text('moving: . . . . . . . {0}'.format(str(self.hero.moving)), screen, coords=(10, 70))
                    draw_text('target_coords:. . . . {0}'.format(str(self.hero.target_coords)), screen, coords=(10, 85))
                    draw_text('map_zoom: . . . . . . {0}'.format(str(self.map_layer.zoom)), screen, coords=(10, 100))
                    draw_text('screen size:. . . . . {0}'.format(str(self.screen_size)), screen, coords=(10, 115))
                    draw_text(str(pygame.display.Info().current_w), screen, coords=(10, 130))

                # blit text objects to screen
                self.text_box.draw(screen)
                self.inputlog.draw(screen)
                self.combatlog.draw(screen)

                pygame.display.flip()

        except KeyboardInterrupt:
            self.running = False


if __name__ == "__main__":
    print('Testing Client::: PREALPHA')
    charactername = raw_input('charactername: ')
    username = raw_input('Username: ')
    password = raw_input('Password: ')

    pygame.init()
    pygame.font.init()
    screen = init_screen(*DEFAULT_RESOLUTION)
    pygame.display.set_caption('Little v0.0.1')

    try:
        game = Game(charactername=charactername, username=username, password=password)
        game.run()
    except:
        pygame.quit()
        raise