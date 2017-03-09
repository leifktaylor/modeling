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

from functions.game_math import negpos, point_distance, map_pos
from mp.client import PacketSizeMismatch
from mp.client import GameClient

from local.remotesprite import Hero
from local.input import PlayerController
from local.remotesprite import RemoteSpriteController, RemoteSprite

from particles import PyIgnition

from game_locals import *


def init_screen(width, height):
    """Simple wrapper to keep the screen resizeable"""
    # screen = pygame.display.set_mode((width, height), pygame.RESIZABLE)
    screen = pygame.display.set_mode((width, height))
    return screen


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

        # GUI ELEMENTS
        # Create text box
        text_box_x, text_box_y = self.screen_coords((3, 95))
        self.text_box = eztext.Input(maxlength=90, color=(255, 255, 255), x=text_box_x, y=text_box_y,
                                     font=pygame.font.Font(FONT, 22), prompt=': ')
        # Create InputLog
        self.inputlog = InputLog(coords=self.screen_coords((3, 88)), max_length=10, size=18, spacing=18, font=FONT)
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

    @property
    def map_size(self):
        return self.map_data.width, self.map_data.height

    @property
    def charactername(self):
        return self.client.charactername

    def screen_coords(self, coords):
        """
        :param coords: percentage of each axis.  i.e. (50, 50) based on MAP position.
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
            # Update target if hero has one
            self.hero.tgh.update_target()

    def update_lifeforms(self):
        """Update co-ordinates of all remote sprites with new information from server, also updates chat que and other
        important information from the server """
        # Update data on all lifeforms in room
        r = self.client.send('get_coords')
        coords_dict = r['response']['coords']
        if coords_dict:
            self.rsc.update_coords(coords_dict)

        # Update chat messages
        messages = r['response']['messages']
        for message in messages:
            self.inputlog.add_line(string=message['message'], color=message['color'])

    def update(self, dt):
        """ Tasks that occur over time should be handled here"""
        # update all sprites in game world
        self.group.update(dt)
        # update camera position (follows player)
        self.hero.camera.update(dt)
        # move player (including animation) if we're moving
        self.move(dt)
        # perform auto attack if we're autoattacking
        self.autoattack(dt)

    def move(self, dt):
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
                r = self.client.send('update_coords', [self.hero.x, self.hero.y])
                self.hero.move_time = r['response']['move_time']
                self.hero.attack_time = r['response']['attack_time']

    def autoattack(self, dt):
        if self.hero.attacking:
            self.hero.attack_timer -= dt / 100.
            if self.hero.attack_timer <= 0:
                self.hero.attack_timer = self.hero.attack_time
                if self.hero.tgh.target:
                    if point_distance(self.hero.coords, self.hero.tgh.coords) < 14:
                        self.client.send('attack', self.hero.tgh.id)

    def draw(self, surface):
        # center the map/screen on our Hero
        self.group.center(self.hero.camera.rect.center)

        # draw the Pyscroll map group
        self.group.draw(surface)

    def run(self):
        """ Run the game loop"""
        clock = pygame.time.Clock()
        self.running = True

        pygame.mouse.set_visible(False)

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

                if self.hero.particle:
                    self.hero.particle.update()

                # blit GUI objects to screen
                self.text_box.draw(screen)
                self.inputlog.draw(screen)
                self.combatlog.draw(screen)
                self.hero.tgh.display.draw(screen)

                # debug draw co-ordinates
                if DEBUG_MODE:

                    # # pos = [coord/16 for coord in self.hero.position]
                    # draw_text('hero.position:. . . . {0}'.format(str(self.hero.position)), screen, coords=(10, 10))
                    # draw_text('delta t:. . . . . . . {0}'.format(str(dt)), screen, coords=(10, 40))
                    # draw_text('server poll:. . . . . {0}'.format(str(self.poll_timer)), screen, coords=(10, 55))
                    # draw_text('moving: . . . . . . . {0}'.format(str(self.hero.moving)), screen, coords=(10, 70))
                    # draw_text('target_coords:. . . . {0}'.format(str(self.hero.target_coords)), screen, coords=(10, 85))
                    # draw_text('map_zoom: . . . . . . {0}'.format(str(self.map_layer.zoom)), screen, coords=(10, 100))
                    # draw_text('screen size:. . . . . {0}'.format(str(self.screen_size)), screen, coords=(10, 115))
                    # draw_text(str(pygame.display.Info().current_w), screen, coords=(10, 130))
                    #
                    # draw_text('Target ID: ', screen, coords=(10, 10))
                    # draw_text('Name: ', screen, coords=(10, 25))
                    # draw_text('Stats: ', screen, coords=(10, 40))

                    # draw_text('Center Offset: {0}'.format(offset), screen, coords=(10, 55))
                    # draw_text('MousePos: {0}'.format(pygame.mouse.get_pos()), screen, coords=(10, 70))
                    # draw_text('MousePosC: {0},{1}'.format(new_x, new_y), screen, coords=(10, 85))
                    # draw_text('PlayerCoords: {0}'.format(self.hero.coords), screen, coords=(10, 100))
                    # draw_text('CursorCoords: {0}'.format(cursor_coords), screen, coords=(10, 115))
                    # draw_text('Zoom: {0}'.format(zoom), screen, coords=(10, 130))

                    #draw_text('Nearby Lifeforms: {0}'.format(self.hero.nearby_lifeforms), screen, coords=(10, 130))

                    # if self.hero.tgh.target:
                    #     distance = point_distance(self.hero.coords, self.hero.tgh.coords)
                    #     draw_text('Target Distance: {0}'.format(distance), screen, coords=(10, 145))
                    #
                    # draw_text('Attacking: {0}'.format(self.hero.attacking), screen, coords=(10, 160))
                    pass

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
        game.screen = screen
        game.run()
    except:
        pygame.quit()
        raise