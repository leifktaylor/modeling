"""
Test based mushy fun!
"""
import logging
from template_parser import TemplateParser

import pickle

import pytmx

from pathfinding.core.diagonal_movement import DiagonalMovement
from pathfinding.finder.a_star import AStarFinder
from pathfinding.core.grid import Grid

from stat_calc import calc_stat
from functions.game_math import clamp, point_distance

from gameobjects.aicontroller import AIController

import copy

START_ROOM = 'gameobjects/room/template.rm'
START_COORDS = [160, 160]

TILE_SIZE = 8


class GameObjectController(object):
    """
    Contain list of active lifeform instances, and the room they are in
    Can generate lifeforms and add room
    Can create rooms from tmx files
    Can terminate gameobjects from its list
    """
    def __init__(self):
        self.tp = TemplateParser()

        # Dictionary like {<id>: <gameobject instance>, <id>: <gameobject instance>, ...}
        self._gameobjects = {}

        # Dictionary like {<room_unique_name>: <room_instance>, <room_unique_name>: <room_instance>, ... }
        self._rooms = {}

    def add_gameobject(self, template, room=None, coords=None):
        """
        :param template: template file
        :param room: room uniquename
        :param coords: modifies co-ords of gameobject
        :return: gameobject id
        """
        # Dictionary like {'settings': [{key: value}, {key: value}], 'othersection': [{key ... }
        input_data = self.tp.load_data(template)
        gameobject, id = self._create_gameobject(self.tp.class_type, **input_data)

        # Update gameobject from input params, and return id
        gameobject.current_room = room
        gameobject.coords = coords
        gameobject.goc = self
        self._gameobjects[id] = gameobject
        return gameobject, id

    def add_room(self, template):
        """ Add room to game """
        input_data = self.tp.load_data(template)
        room = Room(**input_data)
        self._rooms[room.uniquename] = room
        # Instantiate all lifeforms required by tmxmap data
        self._spawn_room_lifeforms(room)
        return room

    def remove_gameobject(self, id):
        """ Delete gameobject from game, will not err if object does not exist """
        try:
            del self._gameobjects[id]
        except KeyError:
            print('Gameobject with ID: {0}, did not exist, so could not delete'.format(id))

    def get_object(self, id):
        """ Returns gameobject instance from id """
        return self.gameobjects[id]

    @property
    def gameobjects(self):
        """ Dictionary like { <id>: <gameobject>, <id>: <gameobject>, <id>: <gameobject>, ... } """
        return self._gameobjects

    @property
    def coords_map(self):
        """ All objects and their coordinates {1: [30,40], 2: [56,43], ... } """
        return {go.id: go.coords for id, go in self.gameobjects.items()}

    @property
    def lifeforms(self):
        """ Only lifeforms { <id>: <gameobject>, <id>: <gameobject>, <id>: <gameobject>, ... } """
        return {id: go for id, go in self._gameobjects.items() if isinstance(go, LifeForm)}

    @property
    def props(self):
        """ Non-item, Non-lifeforms { <id>: <gameobject>, <id>: <gameobject>, <id>: <gameobject>, ... } """
        pass

    @property
    def rooms(self):
        """ Dictionary like {<uniquename>: <room_instance>, <uniquename>: <room_instance> ... } """
        return self._rooms

    @property
    def players(self):
        """ All player gameobjects { <id>: <gameobject>, <id>: <gameobject> """
        return {id: go for id, go in self.lifeforms.items() if go.player}

    @property
    def playernames(self):
        """ Players by name { <playername>: <gameobject>, <playername>: <gameobject>, ... } """
        return [go.name for id, go in self.lifeforms.items() if go.player]

    @property
    def npcs(self):
        """ All non-player lifeforms { <id>: <lifeform>, <id>: <lifeform>, ...} """
        return {id: go for id, go in self.lifeforms.items() if not go.player}

    @property
    def treasure(self):
        """ All Item type objects in room and not in inventory { <id>: <Item>, <id>, <Item>, ... } """
        pass

    @property
    def destroyed(self):
        """ All destroyed game objects { <id>: <gameobject>, <id>: <gameobject>, ... } """
        return {id: go for id, go in self._gameobjects.items() if go.destroyed}

    def coordsmap_for_room(self, uniquename):
        """ Returns: {<id>: [x, y], <id>: [x, y], ... } for each object in current room """
        coords_map = self.coords_map
        room_coords = {}
        for id, coords in coords_map.items():
            if self.gameobjects[id].current_room == uniquename:
                room_coords[id] = coords
        return room_coords

    def coords_sprite_map_for_room(self, uniquename):
        """ Returns: {<id>:(<sprite>,[<coords>]), <id>:(<sprite>,[<coords>]), ... } for each object in current room """
        coords_map = self.coords_map
        room_coords = {}
        for id, coords in coords_map.items():
            if self.gameobjects[id].current_room == uniquename:
                room_coords[id] = (self.gameobjects[id].graphic, coords)
        return room_coords

    def dead_check(self):
        """ Cleanup dead lifeforms """
        for id, lifeform in self.lifeforms.items():
            if lifeform.dead:
                self.remove_gameobject(id=id)

    def update(self, dt):
        """
        Updates all lifeforms
        :param dt: deltatime must be passed in from GameController instance
        :return:
        """
        self.dead_check()
        # Update all game objects
        for id, lifeform in self.lifeforms.items():
            lifeform.update(dt)

    # File handling

    @staticmethod
    def save_gameobject(gameobject, filename):
        """ Save gameobject to pickle """
        with open(filename, 'wb') as f:
            pickle.dump(gameobject, f, protocol=pickle.HIGHEST_PROTOCOL)
            f.close()

    def load_gameobject(self, filename, room=None, coords=None):
        """ Instantiate gameobject from pickle """
        with open(filename, 'rb') as f:
            gameobject = pickle.load(f)
            f.close()
        if self._gameobjects:
            id = max(self._gameobjects) + 1
        else:
            id = 0
        gameobject.id = id
        gameobject.current_room = room
        gameobject.coords = coords
        gameobject.goc = self
        self._gameobjects[id] = gameobject
        return gameobject, id

    # Internal methods, not to be called directly

    def _create_gameobject(self, type='GameObject', **input_data):
        if self._gameobjects:
            id = max(self._gameobjects) + 1
        else:
            id = 0
        gameobject = eval(type)(id, **input_data)
        gameobject.id = id
        return gameobject, id

    def _spawn_room_lifeforms(self, room_instance):
        """
        Instantiates all lifeform objects by reading Tiled tmx map
        :param room_instance: instantiated room object
        :param tiledtmx: pytmx TiledMap instance
        :return:
        """
        lifeforms = room_instance.lifeforms
        print('Lifeforms loaded from tmx: {0}'.format(lifeforms))
        for lifeform in lifeforms:
            # Instantiate each lifeform and add to room
            coords = [lifeform['x'] * TILE_SIZE, lifeform['y'] * TILE_SIZE]
            lifeform, id = self.add_gameobject(lifeform['template'], room_instance.uniquename, coords)
            print('Spawned: {0}'.format(lifeform.name))


class Room(object):
    """
    This is a room class.
    """
    def __init__(self, settings=None):
        self.settings = settings
        try:
            self.tmxfile = settings['tmx_map']
        except KeyError:
            raise RuntimeError('All rooms must have an assosciated tmx_map!')
        self.tmx_data = pytmx.TiledMap(settings['tmx_map'])
        self.grid = self.generate_grid()

    @property
    def uniquename(self):
        try:
            return self.settings['uniquename']
        except KeyError:
            raise RuntimeError('Every room requires a uniquename!')

    @property
    def lifeforms(self):
        """ List of lifeforms in map [ {'x': x, 'y': y, 'template': <templatefile>, 'spawn_time': 60} ]
            These lifeforms are not instantiated yet,
            rather this is the data on the map for what TO instantiate, using what template, at what coords.
        """
        return self.get_lifeforms(self.tmx_data)

    def get_lifeforms(self, tiledtmx, layer=2):
        """
        Searches each tile of the map and grabs lifeforms from given layer

        Lifeforms require these specific custom properties (make them in Tiled editor):
            template: string: path to .lfm template
            spawn_time: int: length of respawn timer when killed, if set to None, will not respawn

        :param tiledtmx: pytmx TiledMap instance
        :param layer: map layer to search for lifeforms (default is 1)
        :return: list of dictionaries
        """
        lifeforms = []
        for y in range(0, tiledtmx.height):
            for x in range(0, tiledtmx.width):
                lifeform = tiledtmx.get_tile_properties(x, y, layer)
                if lifeform:
                    try:
                        # TODO: Give the whole properties dictionary
                        lifeforms.append({'x': x, 'y': y, 'template': lifeform['template'],
                                         'spawn_time': lifeform['spawn_time']})
                    except KeyError:
                        print('Lifeform in tmx map missing required custom properties')
        return lifeforms

    def generate_grid(self, layers=None):
        tmx = self.tmx_data
        if not layers:
            layers = [0, 1]
        matrix = [[0] * tmx.width for row in range(0, tmx.height)]
        for layer in layers:
            for row in range(0, tmx.height):
                for column in range(0, tmx.width):
                    tile = tmx.get_tile_properties(column, row, layer)
                    if tile:
                        if tile['wall'] == 'true':
                            matrix[column][row] = 1
        grid = Grid(matrix=matrix)
        return grid


class GameObject(object):
    def __init__(self, id, goc=None, coords=[0, 0], current_room=None, settings=None, sprites=None):

        # Core stats
        self.id = id
        self.goc = goc
        self.coords = coords
        self.current_room = current_room

        # Direct mappings from template
        self.settings = settings
        self.sprites = sprites

        # Other attributes
        self.destroyed = False

    @property
    def graphic(self):
        return self._value(self.sprites['main'])

    @property
    def name(self):
        return self._value(self.settings['name'])

    @staticmethod
    def _value(value):
        try:
            return value
        except KeyError:
            return None

    def get_object(self, id):
        return self.goc.get_object(id)


class LifeForm(GameObject):
    def __init__(self, id, coords=[0, 0], goc=None, settings=None, sprites=None, stats=None,
                 inventory=None, factions=None, dialogue=None, target=None, current_room=None):
        super(LifeForm, self).__init__(id=id, current_room=current_room, coords=coords, goc=goc)

        # Settings like ai, and other metadata
        self.settings = settings
        self.sprites = sprites
        if self.ai:
            self.aic = AIController(self)

        # Handle stats
        self.stats = stats
        self.stats['MAXHP'] = self.stats['HP']
        self.stats['MAXMP'] = self.stats['MP']

        self.inventory = Inventory(inventory, self)
        self.factions = factions

        if dialogue:
            tp = TemplateParser()
            self.dialogue = [tp.load_data(line) for line in dialogue]
        self.current_dialogue = 0

        # List of status objects
        self.status = []

        # Target is a gameobject instance
        self.target = target
        self.state = 'idle'

        # Get target sight range from templatedata if it's there, otherwise use default
        if 'sight' in self.settings.keys():
            self.sight = self.settings['sight']
        else:
            self.sight = 100

    @property
    def ai(self):
        return self._value(self.settings['ai'])

    @property
    def dead(self):
        return self.stats['HP'] < 1

    @property
    def alive(self):
        return self.stats['HP'] > 0

    @property
    def weapon_range(self):
        # TODO : If using a ranged weapon return blah, if physical blah
        return 14

    @property
    def player(self):
        if self.settings['ai']:
            return False
        else:
            return True

    @property
    def nearby_lifeforms(self):
        return {lf.id: lf for id, lf in self.goc.lifeforms.items()
                if point_distance(self.coords, lf.coords) < self.sight}

    @property
    def move_time(self):
        """ Rate at which hero moves """
        mv_rate = 20 - calc_stat(self.SPD, tier1=20, tier2=40, denom1=2, denom2=2.5)
        return clamp(mv_rate, 2, 14)

    @property
    def attack_time(self):
        """ Rate it which hero can attack.
        Determined by SPD stat and equipment stats """
        atk_spd = 40 - calc_stat(self.SPD)
        return clamp(atk_spd, 2, 80)

    @property
    def level(self):
        stats = [self.stats[stat] for stat in ['STR', 'SPD', 'MND', 'STA']]
        level = int(sum(stats)) / 10
        return level

    # TODO FINISH STATS / Make useful inventory functions for getting aggregate bonuses

    @property
    def ATTACK(self):
        """ Result of STR and equipment stats """
        return self.STR

    @property
    def DEFENSE(self):
        """ Result of STA/SPD and equipment stats """
        return self.STA

    @property
    def MATTACK(self):
        """ Result of MND and equipment stats """
        return self.MND

    @property
    def MDEFENSE(self):
        """ Result of MND/STA and equipment stats """
        return self.MND

    @property
    def HP(self):
        """ Current HP """
        return self.stats['HP']

    @property
    def MAXHP(self):
        """ Result of stats['HP'] and equipment stats """
        return self.stats['MAXHP']

    @property
    def MP(self):
        """ Current MP """
        return self.stats['MP']

    @property
    def MAXMP(self):
        """ Result of stats['MP'] and equipment stats """
        return self.stats['MAXMP']

    @property
    def STR(self):
        """ Result of stats['STR'] and equipment stats """
        return self.stats['STR']

    @property
    def STA(self):
        """ Result of stats['STA'] and equipment stats """
        return self.stats['STA']

    @property
    def MND(self):
        """ Result of stats['MND'] and equipment stats """
        return self.stats['MND']

    @property
    def SPD(self):
        """ Result of stats['SPD'] and equipment stats """
        return self.stats['SPD']

    # Actions

    def change_room(self, roomname):
        pass

    def change_target(self, targetid):
        self.target = targetid

    def cast(self, spellid=None, targetid=None):
        pass

    def attack(self, targetid):
        if targetid == self.id:
            return 0
        target = self.goc.lifeforms[targetid]
        damage = (self.ATTACK - target.DEFENSE)
        if damage < 1:
            damage = 1
        target.stats['HP'] -= damage
        return damage

    def equip_item(self, id):
        return self.inventory.equip_item(id)

    def unequip_item(self, equip_slot):
        return self.inventory.unequip_item(equip_slot)

    def add_item(self, id):
        return self.inventory.add_item(id)

    def drop_item(self, id):
        return self.inventory.drop_item(id)

    def use_item(self, id):
        return self.inventory.use_item(id)

    def give_item(self, id, targetid):
        pass

    def say(self, dialogue, targetid):
        other = self.get_object(targetid)
        try:
            response = other.respond([self.id, dialogue])
        except AttributeError:
            response = 'Cannot speak to that!'
        return response

    def move(self, coords):
        """ Move to given coordinates """
        start = self.coords[0] / 8, self.coords[1] / 8
        end = coords[0] / 8, coords[1] / 8
        grid = copy.deepcopy(self.goc.rooms[self.current_room].grid)
        route = self._path(start, end, grid)
        if len(route) > 2:
            new_x, new_y = route[1][0] * 8, route[1][1] * 8
            print('newx/newy {0},{1}'.format(new_x, new_y))
            self.coords = [new_x, new_y]
        return route

    @staticmethod
    def _path(start, end, grid):
        """
        Use A* pathing algorythm to return a list of sequential tuples where each tuple is the
            co-ordinates of the tile along the path.  Will avoid tiles with 'wall' property == 'true'
        :param start: (x1, y1)
        :param end: (x2, y2)
        :param grid: Room.grid object
        :return: list of tuples like [(0, 0), (0, 1), (0, 2)]
        """
        start = grid.node(*start)  # format (30, 30)
        end = grid.node(*end)
        finder = AStarFinder(diagonal_movement=DiagonalMovement.always)
        path, runs = finder.find_path(start, end, grid)
        return path

    def update(self, dt):
        """
        Events which occur over time go here
        :param dt: delta time (from pygame clock)
        :return:
        """
        pass

    # Dialogue Methods

    def respond(self, dialogue_command):
        """
        Parse dialogue command and respond with conversation string as well as perform any required actions
        :param dialogue_command: list like: [<playerid>, 'hello how are you?']
        :return: respone dialogue string
        """
        if not self.dialogue:
            return None
        dialogue_dict = self.dialogue[self.current_dialogue]
        otherid = dialogue_command[0]
        dialogue = dialogue_command[1]
        response_list = []
        for word in dialogue.split():
            if word[-1] == '?' or word[-1] == '.':
                word = word[:-1]
            if word in dialogue.keys():
                response_list = dialogue_dict[word]
                break
        if response_list:
            dialogue_actions = [line for line in response_list if line[0] == '{' and line[-1] == '}']
            dialogue_actions = [line.replace('{', '').replace('}', '') for line in dialogue_actions]
            # Check if there is a prerequisite (need) block in the actions and abort if not satisfied
            for i, action in enumerate(dialogue_actions):
                if action.split()[0] == 'need':
                    required_item = action.split()[1]
                    if self.get_object(otherid).inventory.item_name_in_inventory(required_item.name):
                        dialogue_actions.pop(i)
            # Now confirm if all needed items are popped from list, if not, don't allow conversation
            for action in dialogue_actions:
                if action.split()[0] == 'need':
                    return 'You lack a required item'

            # If this block is reached, all 'need' checks have passed, perform required actions
            err = self.parse_and_execute_dialogue_actions(dialogue_actions, otherid)
            if err:
                return 'Something went wrong'

            # Lastly, return dialogue response
            return [line for line in response_list if line[0] != '{' and line[-1] != '}']
        else:
            return None

    def parse_and_execute_dialogue_actions(self, dialogue_actions, targetid):
        for action in dialogue_actions:
            try:
                targetplayer = self.get_object(targetid)
                command = action.split()[0]
                params = action.split()[1:]

                if command == 'give':
                    # Create item and give to target player
                    pass

                elif command == 'take':
                    # If player has item in inventory, take it, if item is equipped, unequip it first
                    pass

                elif command == 'teleport':
                    # Teleport player to target room and coords
                    pass

                elif command == 'cast':
                    # Cast spell on player
                    self.cast(targetplayer.id, params[0])

                elif command == 'dialogue':
                    # Switch to new dialogue script
                    self.current_dialogue = params[0]

                elif command == 'remove self':
                    # Remove self from game
                    pass

                elif command == 'spawn':
                    # Spawn lifeform in room
                    pass
            except:
                return -1
        return 0


class Item(GameObject):
    def __init__(self, id=None, goc=None, coords=[0, 0], current_room=None,
                 settings=None, sprites=None, stats=None, scripts=None):
        super(Item, self).__init__(id=id, goc=goc, coords=coords, current_room=current_room)
        self.settings = settings
        self.sprites = sprites
        self.stats = stats
        self.scripts = scripts

    @property
    def weight(self):
        return self._value(self.settings['weight'])

    @property
    def fullname(self):
        return self._value(self.settings['fullname'])

    @property
    def item_type(self):
        return self._value(self.settings['item_type'])

    @property
    def equippable_slot(self):
        return self._value(self.settings['equippable_slot'])


class Inventory(object):
    def __init__(self, inventory_data, owner):
        """
        Inventory data is created from .lfm template
        :param inventory_data: dictionary of key values
        :param owner: Lifeform who owns this inventory
        """
        self.owner = owner
        self.slots = [None]*inventory_data['slots']
        self.equip_slots = {'head': None, 'mask': None, 'neck': None,
                            'chest': None, 'wrist1': None, 'wrist2': None,
                            'ring1': None, 'ring2': None, 'idol': None,
                            'belt': None, 'legs': None, 'boots': None,
                            'right_hand': None, 'left_hand': None,
                            'ranged': None, 'ammo': None}
        self.max_slots = inventory_data['slots']
        # Populate Slots with item instances, and equip if required by template
        a = TemplateParser()
        for slot, item_data in inventory_data.items():
            if slot == 'slots':
                pass
            else:
                self.slots[slot] = Item(**a.load_data(item_data[0]))
                if item_data[1]:
                    self.equip_item(self.slots[slot])

    @property
    def weight(self):
        weight = 0
        for item in self.slots:
            if item.stats.weight:
                weight += item.stats.weight
        return weight

    def add_item(self, item):
        # If inventory is full
        if None not in self.slots:
            raise RuntimeError('Inventory is full, cannot add item')

        # Add item to first available slot in inventory
        for i, slot in enumerate(self.slots):
            if slot is None:
                self.slots.insert(i, item)
                break

    def item_in_inventory(self, item):
        return item in self.slots

    def item_name_in_inventory(self, name):
        for item in self.slots:
            if item:
                if item.name == name:
                    return True
        return False

    def is_equipped(self, item):
        item_slot = item.equippable_slot
        if item_slot:
            return self.equip_slots[item_slot] == item
        else:
            return False

    def equip_item(self, item):
        equip_slot = item.equippable_slot

        # If item isn't in inventory
        if not self.item_in_inventory(item):
            raise RuntimeError('{0} is not in inventory'.format(item))

        # If item doesn't have an equippable slot
        if not item.equippable_slot:
            raise RuntimeError('{0} is not equipabble'.format(item.name))

        # Confirm object is equippable in given slot
        if item.equippable_slot != equip_slot:
            logging.info('Tried to equip item in improper slot')
            raise RuntimeError('{0} only equippable in {1} slot'.format(item.name, item.equippable_slot))

        if self.equip_slots[equip_slot] and self.equip_slots[equip_slot] != item:
            # If a different item already equipped, unequip it
            self.unequip_item(equip_slot)
        elif self.equip_slots[equip_slot] and self.equip_slots[equip_slot] == item:
            # If this item already equipped do nothing
            logging.debug('Trying to equip item that is already equipped, doing nothing')
            return

        self.equip_slots[equip_slot] = item

    def unequip_item(self, equip_slot):
        equipped_item = self.equip_slots[equip_slot]
        # If nothing is equipped in slot, or item not even in inventory, raise
        if not equipped_item:
            raise RuntimeError('No item equipped in {0} slot'.format(equip_slot))
        if not self.item_in_inventory(equipped_item.id):
            raise RuntimeError('{0} is not in inventory'.format(equipped_item.name))
        # Remove item from equipped slot
        self.equip_slots[equip_slot] = None

    def use_item(self, id):
        # Check if item has 'OnUse'
        pass

    def drop_item(self, id):
        # Confirm item is in inventory
        # Confirm item is not equipped
        # Drop item from inventory (replace with None) | later put on ground?
        pass

    def give_item(self, item_id, target_id):
        pass

