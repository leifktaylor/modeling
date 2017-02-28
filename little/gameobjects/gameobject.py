"""
Test based mushy fun!
"""
import logging
from template_parser import TemplateParser

import pickle
import json

import pytmx

from pathfinding.core.diagonal_movement import DiagonalMovement
from pathfinding.finder.a_star import AStarFinder
from pathfinding.core.grid import Grid


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
        :param room: modifies current_room value on gameobject
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
        """
        Add room dictionary
        :param template: room template file (.rm)
        :return:
        """
        input_data = self.tp.load_data(template)
        room = Room(**input_data)
        self._rooms[room.uniquename] = room
        return room

    def remove_gameobject(self, id):
        self._gameobjects[id] = None

    def get_object(self, id):
        """ Returns gameobject instance """
        return self._gameobjects[id]

    @property
    def gameobjects(self):
        return self._gameobjects

    @property
    def lifeforms(self):
        return {id: go for id, go in enumerate(self._gameobjects) if isinstance(go, LifeForm)}

    @property
    def props(self):
        pass

    @property
    def rooms(self):
        """ ['uniquename', 'uniquename', 'uniquename'] """
        return self._rooms

    @property
    def players(self):
        """ All player's gameobjects """
        return {id: go for id, go in enumerate(self.lifeforms) if go.player}

    @property
    def npcs(self):
        """ All non-player lifeforms """
        return {id: go for id, go in enumerate(self.lifeforms) if not go.player}

    @property
    def treasure(self):
        pass

    @property
    def destroyed(self):
        """ All destroyed game objects """
        return {id: go for id, go in enumerate(self._gameobjects) if go.destroyed}

    # File handling

    @staticmethod
    def save_gameobject(gameobject, filename):
        """ Save gameobject to pickle """
        with open(filename, 'wb') as f:
            pickle.dump(gameobject, f, protocol=pickle.HIGHEST_PROTOCOL)
            f.close()

    @staticmethod
    def load_gameobject(filename):
        """ Instantiate gameobject from pickle """
        with open(filename, 'rb') as f:
            gameobject = pickle.load(f)
            f.close()
        return gameobject

    # Internal methods, not to be called directly

    def _create_gameobject(self, type='GameObject', **input_data):
        if self._gameobjects:
            id = max(self._gameobjects) + 1
        else:
            id = 0
        gameobject = eval(type)(id, **input_data)
        gameobject.id = id
        return gameobject, id

    def load_user(self, character, username, password, users_file='users.json'):
        with open('mp/users/{0}'.format(users_file), 'r') as f:
            userdata = json.load(f)
            f.close()
        current_user = userdata[username]
        if current_user['password'] != password:
            raise RuntimeError('Incorrect password')
        filename = current_user['characters'][character]
        return self.load_gameobject('mp/users/{0}'.format(filename))


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


class Item(GameObject):
    def __init__(self, id, goc=None, coords=[0, 0], current_room=None,
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


class LifeForm(GameObject):
    def __init__(self, id, coords=[0, 0], goc=None, settings=None, sprites=None, stats=None,
                 inventory=None, factions=None, dialogue=None, target=None, current_room=None):
        super(LifeForm, self).__init__(id=id, current_room=current_room, coords=coords, goc=goc)
        # Settings like ai, and other metadata
        self.settings = settings
        self.sprites = sprites
        self.stats = stats
        self.inventory = Inventory(inventory)
        self.factions = factions

        a = TemplateParser()
        self.dialogue = [a.load_data(line) for line in dialogue]
        self.current_dialogue = 0

        # List of status objects
        self.status = []

        # Target points to a gameobject id (not an object instance)
        self.target = target
        self.state = 'idle'

    @property
    def ai(self):
        return self._value(self.settings['ai'])

    @property
    def dead(self):
        return self.stats['HP'] < 1

    @property
    def alive(self):
        return self.stats['HP'] > 0

    # Actions

    def change_room(self, roomname):
        pass

    def change_target(self, targetid):
        self.target = targetid

    def cast(self, spellid=None, targetid=None):
        pass

    def attack(self, targetid):
        pass

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
        # TODO finish this
        route = self._path(self.coords, coords, self.current_room.grid)
        pass

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


class Inventory(object):
    def __init__(self, owner, max_slots=20):
        self.owner = owner
        self.slots = [None]*max_slots
        self.equip_slots = {'head': None, 'mask': None, 'neck': None,
                            'chest': None, 'wrist1': None, 'wrist2': None,
                            'ring1': None, 'ring2': None, 'idol': None,
                            'belt': None, 'legs': None, 'boots': None,
                            'right_hand': None, 'left_hand': None,
                            'ranged': None, 'ammo': None}
        self.max_slots = max_slots
        self.weight = 0

    def get_object(self, id):
        return self.owner.get_object(id)

    def get_weight(self):
        weight = 0
        for item in self.slots:
            if item.stats.weight:
                weight += item.stats.weight
        return weight

    def add_item(self, id):
        # If inventory is full
        if None not in self.slots:
            raise RuntimeError('Inventory is full, cannot add item')

        # Add item to first available slot in inventory
        item_to_add = self.get_object(id)
        for i, slot in enumerate(self.slots):
            if slot is None:
                self.slots.insert(i, item_to_add)
                break

    def item_in_inventory(self, id):
        return self.get_object(id) in self.slots

    def item_name_in_inventory(self, name):
        for item in self.slots:
            if item:
                if item.name == name:
                    return True
        return False

    def get_itemid_in_inventory_by_name(self, name):
        for item in self.slots:
            if item:
                if item.name == name:
                    return item.id
        return None

    def is_equipped(self, id=None, instance=None):
        if instance:
            item_slot = instance.equippable_slot
        else:
            instance = self.get_object(id)
            item_slot = instance.equippable_slot
        if item_slot:
            return self.equip_slots[item_slot] == instance
        else:
            return False

    def equip_item(self, id):
        new_item = self.get_object(id)
        equip_slot = new_item.equippable_slot

        # If item isn't in inventory
        if not self.item_in_inventory(id):
            raise RuntimeError('{0} is not in inventory'.format(new_item))

        # If item doesn't have an equippable slot
        if not new_item.equippable_slot:
            raise RuntimeError('{0} is not equipabble'.format(new_item.name))

        # Confirm object is equippable in given slot
        if new_item.equippable_slot != equip_slot:
            logging.info('Tried to equip item in improper slot')
            raise RuntimeError('{0} only equippable in {1} slot'.format(new_item.name, new_item.equippable_slot))

        if self.equip_slots[equip_slot] and self.equip_slots[equip_slot] != new_item:
            # If a different item already equipped, unequip it
            item_id = self.equip_slots[equip_slot].id
            self.unequip_item(item_id)
        elif self.equip_slots[equip_slot] and self.equip_slots[equip_slot] == new_item:
            # If this item already equipped do nothing
            logging.debug('Trying to equip item that is already equipped, doing nothing')
            return

        self.equip_slots[equip_slot] = new_item

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


def regression_tests():
    import pprint
    a = TemplateParser()
    print(' TEST 1 : Lifeform ')
    pprint.pprint(a.load_data('gameobjects/lifeform/zaxim.lfm'))
    print(' TEST 2 : Item ')
    pprint.pprint(a.load_data('gameobjects/weapon/long_sword.itm'))
    print(' TEST 3 : Room ')
    pprint.pprint(a.load_data('gameobjects/room/template.rm'))
    print(' TEST 4 : Faction ')
    pprint.pprint(a.load_data('gameobjects/faction/chand_baori.fct'))
    print(' TEST 5 : AI ')
    pprint.pprint(a.load_data('gameobjects/ai/healer.ai'))
    print(' TEST 6 : DIALOGUE ')
    pprint.pprint(a.load_data('gameobjects/dialogue/template.dlg'))

    # GameObjectController Tests
    GOC = GameObjectController()
    GOC.add_room('gameobjects/room/template.rm')




