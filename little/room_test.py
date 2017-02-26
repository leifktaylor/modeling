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
from mp.client import GameClient

from gameobjects.gameobject import load_lifeform, get_object_by_id

# define tile size
TILE_SIZE = 8

# define configuration variables here
ROOM_DIR = 'gameobjects/room'
SPRITE_DIR = 'graphics/sprites'
TILESET_DIR = 'graphics/tilesets'

MAP_FILENAME = 'grasslands.tmx'
screen = None

def negpos(number):
    if number < 0:
        return -1
    elif number > 0:
        return 1
    else:
        return 0


# simple wrapper to keep the screen resizeable
def init_screen(width, height):
    screen = pygame.display.set_mode((width, height), pygame.RESIZABLE)
    return screen


# make loading maps a little easier
def get_map(filename):
    return filename


# make loading sprites a little easier
def load_sprite(filename):
    return pygame.image.load(filename)


# make loading tilesets a little easier
def load_tileset(filename):
    return pygame.image.load(filename)


def isclose(a, b, allowed_error=.05):
    return abs(a - b) <= allowed_error


class RemoteSprite(pygame.sprite.Sprite):
    def __init__(self, lifeformid, sprite, screen):
        pygame.sprite.Sprite.__init__(self)
        self.image = load_sprite(sprite).convert_alpha()
        self.lifeform = get_object_by_id(lifeformid)
        # self._position = self.lifeform.coords
        self.position = self.lifeform.coords
        self.rect = self.image.get_rect()
        self.screen = screen

    def update(self, dt):
        self.position = self.lifeform.coords
        self.rect.topleft = self.position
        # self.rect.x = self.position[0]
        # self.rect.y = self.position[1]

    @property
    def position(self):
        return list(self._position)

    @position.setter
    def position(self, value):
        self._position = list(value)


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

    def __init__(self, lifeform):
        """
        :param lifeform: .sav file of lifeform class
        """
        # TODO
        # This will be done on server and then added to hero object, but for now just create here
        self.lifeform = lifeform

        pygame.sprite.Sprite.__init__(self)
        self.image = load_sprite('graphics/sprites/humans/23.png').convert_alpha()

        self.velocity = [0, 0]

        self.position = self.lifeform.coords
        self._position = self.position
        self.x = self.position[0]
        self.y = self.position[1]
        self.rect = self.image.get_rect()

        # 'move_time' is determined by speed stat, the lower this is, the faster you can move from tile to tile
        self.move_time = 20
        self.move_timer = self.move_time
        self.moving = False
        self.target_coords = None

    @property
    def x(self):
        return self._position[0]

    @x.setter
    def x(self, value):
        self._position[0] = value

    @property
    def y(self):
        return self._position[1]

    @y.setter
    def y(self, value):
        self._position[1] = value

    @property
    def position(self):
        return list(self._position)

    @position.setter
    def position(self, value):
        self._position = list(value)

    def update(self, dt):
        self.rect.topleft = self._position


class QuestGame(object):
    """ This class is a basic game.

    This class will load data, create a pyscroll group, a hero object.
    It also reads input and moves the Hero around the map.
    Finally, it uses a pyscroll group to render the map and Hero.
    """

    def __init__(self, charactername='Mike', username='leif', password='mypw', ip='127.0.0.1',
                 current_room='gameobjects/room/test8.tmx'):
        self.client = GameClient(charactername=charactername, username=username, password=password, ip=ip)

        # List of other lifeform Other objects
        self.others = {}

        # Rate that chat polls are sent to server
        self.poll_frequency = 10
        self.poll_timer = self.poll_frequency
        self.out_going_message = None

        # Rate that coords are sent to server
        self.coord_frequency = 30
        self.coord_timer = self.coord_frequency

        # true while running
        self.running = False

        # load data from pytmx
        tmx_data = load_pygame(current_room)
        self.map_data = tmx_data

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

        # Login to server:
        # Get room instance and player object id
        response = self.client.login()
        playerid = response['response']['playerid']
        self.hero = Hero(lifeform=get_object_by_id(playerid))
        self.current_room = response['response']['current_room']

        # put the hero in the center of the map
        # TODO: Put here in coords on hero object
        self.hero.position = [160, 160]
        self.hero.lifeform.coords = self.hero.position

        # add our hero to the group
        self.group.add(self.hero)

        # Create text box
        self.text_box = eztext.Input(maxlength=90, color=(255, 255, 255), x=30, y=860,
                                     font=pygame.font.Font(None, 30), prompt=': ')

        # Create InputLog
        self.inputlog = InputLog(coords=(30, 840), max_length=10, size=28, spacing=18)
        # Create Combatlog
        self.combatlog = InputLog(coords=(1050, 860), max_length=10, size=28, spacing=18)

        # Create Inventory
        # self.inventorybox = InventoryBox(self.hero.lifeform.inventory, (1000, 200))

    def draw(self, surface):

        # center the map/screen on our Hero
        self.group.center(self.hero.rect.center)

        # draw the map and all sprites
        self.group.draw(surface)

    def populate_room(self):
        """
        Reads 'lifeforms' layer of current room's tileset and instantiates objects from templates
        :return:
        """
        self.map_data

    def handle_input(self):
        """ Handle pygame input events
        """
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
                    self.out_going_message = msgvalue
                    if 'set' in msgvalue:
                        if len(msgvalue.split()) == 3:
                            attribute = msgvalue.split()[1]
                            value = msgvalue.split()[2]
                            if value.isdigit():
                                value = int(value)
                            if hasattr(self.hero, attribute):
                                setattr(self.hero, attribute, value)
                                self.inputlog.add_line('System: Set {0} to {1}'.format(attribute, value))
                            else:
                                self.inputlog.add_line('System: {0} unknown attribute'.format(attribute))
                        else:
                            self.inputlog.add_line('Help: set <attribute> <value>')

                if event.key == K_ESCAPE:
                    self.running = False
                    break

                elif event.key == K_EQUALS:
                    self.map_layer.zoom += .25

                elif event.key == K_MINUS:
                    value = self.map_layer.zoom - .25
                    if value > 0:
                        self.map_layer.zoom = value

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
        moved = False
        self.hero.move_timer -= 1
        if self.hero.move_timer <= 0:
            if not self.hero.moving:
                pressed = pygame.key.get_pressed()
                target_coords = [None, None]
                if pressed[K_UP]:
                    # This is a diagonal fix, pre-checking for collision on one of the axis
                    if not self.collision_check([self.hero.x, self.hero.y - TILE_SIZE]):
                        moved = True
                        target_coords[1] = self.hero.y - TILE_SIZE
                elif pressed[K_DOWN]:
                    if not self.collision_check([self.hero.x, self.hero.y + TILE_SIZE]):
                        target_coords[1] = self.hero.y + TILE_SIZE
                        moved = True

                if pressed[K_LEFT]:
                    target_coords[0] = self.hero.x - TILE_SIZE
                    moved = True
                elif pressed[K_RIGHT]:
                    target_coords[0] = self.hero.x + TILE_SIZE
                    moved = True

                if moved:
                    target_coords = [self.hero.position[i] if item is None else
                                     item for i, item in enumerate(target_coords)]
                    self.move_timer_reset()
                    self.move_lifeform(target_coords)

        else:
            return

    def move_timer_reset(self):
        self.hero.move_timer = self.hero.move_time

    def move_lifeform(self, position):
        """
        moves lifeform on grid while checking for collision
        :param position: position to move to
        :return:
        """
        if not self.collision_check(position):
            # Immediately set actual lifeform co-ordinates to new position
            self.hero.lifeform.coords = position

            # Set new coords as target for sprite animation to move to
            self.hero.target_coords = [int(position[0]), int(position[1])]
            self.hero.moving = True

            # Update server that we are moving
            self.client.send_command('move', [self.hero.target_coords])

    def collision_check(self, position):
        """
        Checks if given coordinates are occupied by a tile marked 'wall'
        :param position:
        :return:
        """
        # TODO: Fix diagonal
        tile_pos_x = position[0] / TILE_SIZE
        tile_pos_y = position[1] / TILE_SIZE
        try:
            if self.map_data.get_tile_properties(tile_pos_x, tile_pos_y, 0)['wall'] == 'true':
                return True
            else:
                return False
        except ValueError:
            # If off the map
            return True

    def update(self, dt):
        """ Tasks that occur over time should be handled here
        """
        self.group.update(dt)

        # STATE: 'moving'
        # (If we are moving to another tile)
        if self.hero.moving:
            distance_x, distance_y = (self.hero.target_coords[0] - self.hero.x,
                                      self.hero.target_coords[1] - self.hero.y)
            stepx, stepy = (negpos(distance_x), negpos(distance_y))

            self.hero.x += stepx
            self.hero.y += stepy

            if self.hero.move_timer <= 0:
                self.hero.moving = False
                self.hero.position = self.hero.target_coords
                self.hero.lifeform.coords = self.hero.target_coords

    def poll_server(self, request=None):
        # Count down to next contact with server
        self.poll_timer -= 1
        if self.poll_timer <= 0:
            self.poll_timer = self.poll_frequency
            r = self.client.send_command('update_coords', [])
            self.update_room(r['response'])

    def update_room(self, new_room):
        """
        Update room with new information gleaned from server
        :param new_room:
        :return:
        """
        # TODO SHOW OTHER PLAYERS!
        self.client.current_room.lifeforms.update(new_room.lifeforms)

        # self.hero.lifeform = self.client.current_room.lifeforms[self.client.playerid]

        # for id, lifeform in self.client.current_room.lifeforms.items():
        #     if id not in self.others.keys():
        #         sprite = RemoteSprite(id, 'graphics/sprites/goblins/sprites1140.png', screen)
        #         self.group.add(sprite)
        #
        # for id, sprite in self.others.items():
        #     sprite._position = sprite.lifeform.coords

        for id, lifeform in self.client.current_room.lifeforms.items():
            if lifeform.name == 'Mike' and id not in self.others.keys():
                sprite = RemoteSprite(id, 'graphics/sprites/goblins/sprites1140.png', screen)
                self.others[id] = sprite
                self.group.add(sprite)

    def get_lifeforms(self, layer=1):
        """
        Searches each tile of the map and grabs lifeforms from given layer

        Lifeforms require these specific custom properties (make them in Tiled editor):
            template: string: path to .lfm template
            spawn_time: int: length of respawn timer when killed, if set to None, will not respawn

        :param layer: map layer to search for lifeforms (default is 1)
        :return: list of dictionaries
        """
        lifeforms = []
        for y in range(0, self.map_data.height):
            for x in range(0, self.map_data.width):
                lifeform = self.map_data.get_tile_properties(x, y, layer)
                if lifeform:
                    try:
                        lifeforms.append({'x': x, 'y': y, 'template': lifeform['template'],
                                         'spawn_time': lifeform['spawn_time']})
                    except KeyError:
                        print('Lifeform in tmx map missing required custom properties')
        return lifeforms

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

                # Update From Server
                self.poll_server()

                # Handle input and render
                self.handle_input()
                self.update(dt)
                self.draw(screen)

                # debug draw co-ordinates
                # pos = [coord/16 for coord in self.hero.position]
                draw_text('hero.position:. . . . {0}'.format(str(self.hero.position)), screen, coords=(10, 12))
                draw_text('lifeform.position:. . {0}'.format(str(self.hero.lifeform.coords)), screen, coords=(10, 24))
                draw_text('moving: . . . . . . . {0}'.format(str(self.hero.moving)), screen, coords=(10, 36))
                draw_text('target_coords . . . . {0}'.format(str(self.hero.target_coords)), screen, coords=(10, 48))
                draw_text(str(self.client.current_room), screen, coords=(2, 80))
                draw_text(str(len(self.client.current_room.lifeforms)), screen, coords=(2, 90))

                # blit text_box on the sceen
                self.text_box.draw(screen)

                # blit InputLog to screen
                self.inputlog.draw(screen)
                self.combatlog.draw(screen)

                pygame.display.flip()

        except KeyboardInterrupt:
            self.running = False


def init_room():
    pygame.init()
    pygame.font.init()
    pygame.display.set_caption('Little v0.0.1')
    game = QuestGame(charactername='Mike', username='leif', password='mypw')
    return game

screen = init_screen(1600, 900)

# if __name__ == "__main__":
#     print('Testing Client::: PREALPHA')
#     charactername = raw_input('charactername: ')
#     username = raw_input('Username: ')
#     password = raw_input('Password: ')
#
#     pygame.init()
#     pygame.font.init()
#     screen = init_screen(1600, 900)
#     pygame.display.set_caption('Little v0.0.1')
#     #
#     # try:
#     #     game = QuestGame(charactername=charactername, username=username, password=password)
#     #     game.run()
#     # except:
#     #     pygame.quit()
#     #     raise
