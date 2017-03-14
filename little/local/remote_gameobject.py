import pygame
from local.camera import Camera
from graphics.graphictext import draw_text
from local.input import Cursor
from functions.game_math import point_distance

from mp.client import ServerResponseError

import logging

TARGET_RANGE = 105
FONT = 'graphics/fonts/november.ttf'
TILE_SIZE = 8
MOVE_TIME = 8


class RemoteInventory(object):
    def __init__(self, client):
        self.client = client
        self.inventory = None

    def update_inventory(self):
        """ Update inventory from server, response like:
        {'response': [{'name': 'Big Sword', 'graphic': 'sword.png', 'equipped': True}, ... ] }"""
        r = self.client.send('inventory_update')
        self.inventory = [RemoteItem(item['name'], item['graphic'], item['equipped']) for item in r['response']]
        logging.info('Updated inventory from server: {0}'.format(self.inventory))
        return self.inventory

    def equipped_graphics(self):
        """ Return list of the graphics of all equipped items """
        return [item.graphic for item in self.get_equipped_items()]

    def get_equipped_items(self):
        """ Return list of RemoteItems that represent equipped Items on server side """
        return [item for item in self.inventory if item.equipped]

    def equip_item(self, index):
        """ Send request to equip item on serverside """
        try:
            r = self.client.send('inventory_equip', index)
        except ServerResponseError:
            return 'Could not equip item'
        self.update_inventory()
        return r['response']['message']

    def unequip_item(self, index):
        """ Send request to unequip item on serverside """
        try:
            r = self.client.send('inventory_unequip', index)
        except ServerResponseError:
            return 'Could not unequip item'
        self.update_inventory()
        return r['response']['message']

    def give_item(self, index, target):
        """ Send request to give item to selected target lifeform on serverside (by ID) """
        r = self.client.send('inventory_give', {'index': index, 'targetid': target})
        self.update_inventory()


class VisualEquipment(object):
    def __init__(self, remotesprite, group):
        self.remotesprite = remotesprite
        self.group = group
        self.sprites = [None, None, None, None]

    def update_sprites(self, graphics):
        """ Gets graphics of equipped items from server and updates sprites """
        # Clear old sprites
        for sprite in self.sprites:
            if sprite:
                sprite.kill()
        for i, graphic in enumerate(graphics):
            self.sprites[i] = pygame.sprite.Sprite()
            self.sprites[i].image = pygame.image.load(graphic)
            self.sprites[i].rect = self.sprites[i].image.get_rect()
            self.group.add(self.sprites[i], layer='over0')
        if self.remotesprite.facing == 'left':
            self.flip()

    def update(self):
        """ Update co-ordinates of all image rects to match parent remotesprite's coordinates """
        for sprite in self.sprites:
            if sprite:
                sprite.rect.topleft = self.remotesprite.coords

    def flip(self):
        """ Sprite flips horizontaly when remotesprite object flips horizontally """
        for sprite in self.sprites:
            if sprite:
                sprite.image = pygame.transform.flip(sprite.image, True, False)


class RemoteItem(object):
    def __init__(self, name, graphic, equipped):
        """
        :param name: display name of item
        :param graphic: path to graphic file
        :param equipped: boolean
        """
        self.name = name
        self.graphic = graphic
        self.equipped = equipped


class TargetHandler(object):
    def __init__(self, hero):
        self.hero = hero
        self.target = None

        # Create HUD display object
        self.display = TargetDisplay(self)
        # Create Targetting Reticle Sprite
        self.reticle = TargetReticle(self)

    def set_target(self, id, name, stats):
        """ takes a name, and a dictionary of stats """
        self.target = {'id': id, 'name': name, 'stats': stats}
        # Make target reticle visible
        if self.hero.attacking:
            self.reticle.image = self.reticle.images['red']
        else:
            self.reticle.image = self.reticle.images['grey']

    def drop_target(self):
        self.target = None
        # Make target reticle invisible
        self.reticle.image = self.reticle.images['none']
        # Turn off auto attack if no target
        self.hero.attacking = False

    def update_target(self, dt=None):
        if self.target:
            try:
                r = self.hero.game.client.send('get_target', [self.target['id']])
                name, stats = r['response']['name'], r['response']['stats']
                self.target = {'id': self.target['id'], 'name': name, 'stats': stats}
            except ServerResponseError:
                self.drop_target()
            # Change reticle to red or grey depending on attacking or not
            if self.hero.attacking:
                self.reticle.image = self.reticle.images['red']
            else:
                self.reticle.image = self.reticle.images['grey']
        else:
            self.reticle.image = self.reticle.images['none']

    @property
    def level(self):
        if self.target:
            stats = [self.target['stats'][stat] for stat in ['STR', 'SPD', 'MND', 'STA']]
            level = int(sum(stats)) / 10
            return level

    @property
    def id(self):
        if self.target:
            return self.target['id']

    @property
    def coords(self):
        if self.target:
            try:
                coords = self.hero.game.rsc.remotesprites[self.target['id']].coords
                return coords[0] - 1, coords[1] - 1
            except KeyError:
                # TODO: This could be an issue
                # Perhaps it the hero?
                coords = self.hero.coords
                return coords[0] - 1, coords[1] - 1
    @property
    def name(self):
        if self.target:
            return self.target['name']

    @property
    def stats(self):
        if self.target:
            return self.target['stats']

    @property
    def HP(self):
        if self.target:
            thp = self.target['stats']['HP']
            if thp < 0:
                thp = 0
            return thp

    @property
    def MAXHP(self):
        if self.target:
            return self.target['stats']['MAXHP']

    @property
    def MP(self):
        if self.target:
            tmp = self.target['stats']['MP']
            if tmp < 0:
                tmp = 0
            return tmp

    @property
    def MAXMP(self):
        if self.target:
            return self.target['stats']['MAXMP']


class TargetReticle(pygame.sprite.Sprite):
    """ Targetting reticle sprite """
    def __init__(self, targethandler):
        pygame.sprite.Sprite.__init__(self)
        self.solid = False

        self.th = targethandler
        image_map = {'red': 'graphics/sprites/hud/target/red.png',
                     'dblue': 'graphics/sprites/hud/target/dblue.png',
                     'grey': 'graphics/sprites/hud/target/grey.png',
                     'lblue': 'graphics/sprites/hud/target/lblue.png',
                     'yellow': 'graphics/sprites/hud/target/yellow.png',
                     'none': 'graphics/sprites/hud/target/none.png'}
        self.images = {color: pygame.image.load(image_map[color]).convert_alpha() for color, path in image_map.items()}
        self.image = self.images['none']
        self.rect = self.image.get_rect()
        self._coords = self.th.coords
        self.th.hero.game.group.add(self, layer='under0')

    def update(self, dt=None):
        if self.th.target:
            self.coords = self.th.coords
            self.rect.topleft = self.coords

    @property
    def coords(self):
        return list(self._coords)

    @coords.setter
    def coords(self, value):
        self._coords = list(value)


class TargetDisplay(object):
    """
    This class will display gui hud data about target.

    Display this data:
    {'id': <id>, 'name': <name>, 'stats': <stats dictionary>}
    """
    def __init__(self, targethandler, coords=(850, 10), size=18, font=FONT):
        self.th = targethandler

        self.font = font
        self.size = size
        self.coords = coords

    def draw(self, surface):
        if self.th.target:
            # Draw GUI Elements
            y = self.coords[1]
            x = self.coords[0]
            draw_text(string=self.th.name, surface=surface, size=self.size, coords=(x, y), font=self.font)
            draw_text(string='HP: {0}/{1}'.format(self.th.HP, self.th.MAXHP),
                      surface=surface, size=self.size, coords=(x, y+20), font=self.font)
            draw_text(string='LV: {0}'.format(self.th.level), surface=surface, size=self.size,
                      coords=(x, y+40), font=self.font)
            draw_text(string=str(self.th.target['id']), surface=surface, size=self.size, coords=(x, y+60), font=self.font)


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
        self.charactername = self.game.client.charactername

        # RemoteSprite object
        print('PASSING!!!')
        print(self.game.group)
        self.remotesprite = RemoteSprite(id=id, sprite=sprite, coords=coords, group=self.game.group)

        # Visual equipment and inventory
        self.remoteinventory = RemoteInventory(client=self.game.client)
        self.remoteinventory.update_inventory()
        equipment_graphics = self.remoteinventory.equipped_graphics()
        self.remotesprite.visualequipment.update_sprites(equipment_graphics)

        # Camera which will follow the hero's remotesprite
        self.camera = Camera(self.remotesprite)

        # 'move_time' is determined by speed stat, the lower this is, the faster you can move from tile to tile
        self.move_time = MOVE_TIME
        self.move_timer = self.move_time
        self.moving = False
        self.target_coords = None

        # Target data like: {'remotesprite': <object>, 'name': <gameobject.name>, 'stats': <stats dict>}
        self.tgh = TargetHandler(self)

        # Autoattack / Casting Code
        self.attacking = False
        self.casting = False

        # TODO get the correct attack timer from hero stats
        self.attack_time = 50
        self.attack_timer = self.attack_time

        self.casting = False
        self.firing = False
        self.particle = None

    @property
    def nearby_lifeforms(self):
        return {rs.id: rs for id, rs in self.game.rsc.remotesprites.items()
                if point_distance(self.coords, rs.coords) < TARGET_RANGE}

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
    def coords(self):
        return self.remotesprite.coords

    @coords.setter
    def coords(self, value):
        self.remotesprite.coords = list(value)

    def update(self, dt):
        pass

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
        collide = False
        # First check for unit collision
        if [s for s in self.game.group if s.rect.collidepoint(position) and s.solid]:
            return True
        # Check for map / geometry collision
        if not layers:
            layers = [0, 1]
        else:
            layers = layers
        # Get all tiles at this position, in all layers and check for 'wall' == 'true'

        tile_pos_x = position[0] / TILE_SIZE
        tile_pos_y = position[1] / TILE_SIZE
        tiles = [self.game.map_data.get_tile_properties(tile_pos_x, tile_pos_y, layer) for layer in layers]
        tiles = [tile['wall'] for tile in tiles if tile]
        for wall in tiles:
            if wall == 'true':
                return True
        return False


class RemoteSpriteController(object):
    def __init__(self, game):
        """
        :param game: Game object instance
        :param id: id of current logged in player gameobject
        :param group: pyscroll sprite group
        """
        # Access to game object is required to add sprites to group
        self.game = game

        # Dictionary like {<id>: <RemoteSprite>, <id>: <RemoteSprite>, ... }
        self._remotesprites = {}
        # Create sprite group (pygame)

        self.initialized = False
        self.id = None
        self.group = None

    def initialize(self):
        self.id = self.game.hero.id
        self.group = self.game.group

    def add_remotesprite(self, id, sprite, coords):
        remotesprite = RemoteSprite(id=id, sprite=sprite, coords=coords)
        self._remotesprites[id] = remotesprite
        return remotesprite

    def remove_remotesprite(self, id):
        del self._remotesprites[id]

    @property
    def visible(self):
        """ Return all dict {<id>: sprite, ... } of remotesprites which are not stealthed / invisible """
        pass

    @property
    def remotesprites(self):
        return self._remotesprites

    def update_coords(self, coords_dict):
        """ Takes a dictionary of coords like {<id>: (<sprite>, <coords>), <id>: <coords>, ... } """
        for id, spritecoords in coords_dict.items():
            # If this remote sprite is rendered already
            if id in self.remotesprites.keys():
                self.remotesprites[id].coords = spritecoords[1]
            # If this sprite is not yet known to client, create it
            else:
                if id != self.id:
                    remote_sprite = self.add_remotesprite(id=id, sprite=spritecoords[0], coords=spritecoords[1])
                    self.group.add(remote_sprite)
        # If we have a remote sprite locally that no longer exists on remote, remove it
        for id in self.remotesprites.keys():
            if id not in coords_dict.keys():
                remote_sprite = self.remotesprites[id]
                self.group.remove(remote_sprite)
                self.remove_remotesprite(id)

    def update(self):
        pass

    def clear_sprites(self):
        """ Delete all remotesprite objects """
        self._remotesprites = {}
        self.group = pygame.sprite.Group()


class RemoteSprite(pygame.sprite.Sprite):
    """
    This object is the counterpart of a gameobject on the server side.  It holds a limited amount
    of information about its sister game object.  This allows the server to expose a limited amount
    of information to the client, and the client to render a representation of all the gameobjects
    in the game world.
    """
    def __init__(self, id, sprite, coords, group=None):
        """
        :param id: id of sister gameobject on server side
        :param sprite: image
        :param coords: pixel coordinates to render on screen (from remote gameobject)
        :param group: pyscroll sprite group
        """
        pygame.sprite.Sprite.__init__(self)
        self.id = id
        self.solid = True
        self.facing = 'right'
        self.image = pygame.image.load(sprite).convert_alpha()
        self.rect = self.image.get_rect()
        self._coords = coords
        self.group = group

        # Inventory Classes
        if self.group is not None:
            self.visualequipment = VisualEquipment(remotesprite=self, group=self.group)
        else:
            self.visualequipment = None

    def update(self, dt=None):
        self.rect.topleft = self._coords
        if self.visualequipment:
            self.visualequipment.update()

    @property
    def x(self):
        return self._coords[0]

    @x.setter
    def x(self, value):
        self._coords[0] = value

    @property
    def y(self):
        return self._coords[1]

    @y.setter
    def y(self, value):
        self._coords[1] = value

    @property
    def coords(self):
        return list(self._coords)

    @coords.setter
    def coords(self, value):
        self._coords = list(value)