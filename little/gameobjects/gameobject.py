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

from functions.game_math import clamp, point_distance, calc_stat

from gameobjects.aicontroller import AIController

from pathfinding.astar2 import *
import numpy

import random
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
    def __init__(self, gc):
        self.tp = TemplateParser()
        self.gc = gc

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
        grid = numpy.array(matrix)
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
        self.route = []

        # Get target sight range from templatedata if it's there, otherwise use default
        if 'sight' in self.settings.keys():
            self.sight = self.settings['sight']
        else:
            self.sight = 100

        if self.ai:
            self.aic = AIController(self)
        else:
            self.aic = None

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

    # TODO :: None of these seem to work .. ? Fix them - Generators would be ideal

    @property
    def nearby_lifeforms(self):
        return {lf.id: lf for id, lf in self.goc.lifeforms.items()
                if point_distance(self.coords, lf.coords) < self.sight and lf != self}

    @property
    def nearby_allies(self):
        return {lf.id: lf for id, lf in self.nearby_lifeforms.items() if self.is_ally(lf)}

    @property
    def nearby_enemies(self):
        return {lf.id: lf for id, lf in self.nearby_lifeforms.items() if self.is_enemy(lf)}

    @property
    def nearby_players(self):
        return {lf.id: lf for id, lf in self.nearby_lifeforms.items() if lf.player}

    @property
    def nearest_lifeform(self):
        try:
            return min({point_distance(self.coords, lifeform.coords): lifeform
                        for key, lifeform in self.nearby_lifeforms.items()}.values())
        except ValueError:
            return {}

    @property
    def farthest_lifeform(self):
        try:
            return min({point_distance(self.coords, lifeform.coords): lifeform
                        for key, lifeform in self.nearby_lifeforms.items()}.values())
        except ValueError:
            return {}

    @property
    def nearest_player(self):
        try:
            return min({point_distance(self.coords, lifeform.coords): lifeform
                        for key, lifeform in self.nearby_players.items()}.values())
        except ValueError:
            return {}

    @property
    def farthest_player(self):
        try:
            return max({point_distance(self.coords, lifeform.coords): lifeform
                        for key, lifeform in self.nearby_players.items()}.values())
        except ValueError:
            return {}

    @property
    def nearest_enemy(self):
        try:
            return min({point_distance(self.coords, lifeform.coords): lifeform
                        for key, lifeform in self.nearby_enemies.items()}.values())
        except ValueError:
            return {}

    @property
    def farthest_enemy(self):
        try:
            return max({point_distance(self.coords, lifeform.coords): lifeform
                        for key, lifeform in self.nearby_enemies.items()}.values())
        except ValueError:
            return {}

    @property
    def nearest_ally(self):
        try:
            return min({point_distance(self.coords, lifeform.coords): lifeform
                        for key, lifeform in self.nearby_allies.items()}.values())
        except ValueError:
            return {}

    @property
    def farthest_ally(self):
        try:
            return max({point_distance(self.coords, lifeform.coords): lifeform
                        for key, lifeform in self.nearby_allies.items()}.values())
        except ValueError:
            return {}

    @property
    def any_ally(self):
        # This is written in this convoluted way because random.choice(Dict) is currently broken
        nearby_allies = self.nearby_allies
        if nearby_allies:
            keys = nearby_allies.keys()
            return nearby_allies[random.choice(keys)]
        else:
            return {}

    @property
    def any_player(self):
        # This is written in this convoluted way because random.choice(Dict) is currently broken
        nearby_players = self.nearby_players
        if nearby_players:
            keys = nearby_players.keys()
            return nearby_players[random.choice(keys)]
        else:
            return {}

    @property
    def any_enemy(self):
        # This is written in this convoluted way because random.choice(Dict) is currently broken
        nearby_enemies = self.nearby_enemies
        if nearby_enemies:
            keys = nearby_enemies.keys()
            return nearby_enemies[random.choice(keys)]
        else:
            return {}

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

    @property
    def primary_faction(self):
        """ Returns lifeform's highest faction """
        return max(self.factions, key=lambda key: self.factions[key])

    @property
    def hated_factions(self):
        """ Returns list of hated factions ['antiquarian_society', 'stamp_collectors', 'food_network'] """
        return [faction for faction, value in self.factions.items() if value == 0]

    @property
    def friendly_factions(self):
        """ Returns list of liked factions """
        return [faction for faction, value in self.factions.items() if value != 0]

    # Queries

    def is_enemy(self, lifeform):
        if lifeform.primary_faction in self.hated_factions:
            return True
        else:
            return False

    def is_ally(self, lifeform):
        if not self.is_enemy(lifeform):
            return True
        else:
            return False

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
        print('{0} attacking {1} for {2} damage'.format(self.name, target.name, damage))
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

    def move_to_lifeform(self, coords):
        """ Move to given coordinates and stop right in front of them """
        start = self.coords[0] / TILE_SIZE, self.coords[1] / TILE_SIZE
        end = coords[0] / TILE_SIZE, coords[1] / TILE_SIZE
        updated_grid = self.goc.rooms[self.current_room].grid
        route = astar(updated_grid, start, end)
        if point_distance(self.coords, coords) > 12:
            try:
                new_x, new_y = route[1][0] * TILE_SIZE, route[1][1] * TILE_SIZE
                print('newx/newy {0},{1}'.format(new_x, new_y))
                self.coords = [new_x, new_y]
                return route
            except IndexError:
                return None
        # Return None if we have arrived at our destination
        return None

    def move_to_coords(self, coords):
        """ Move to given coordinates """
        start = self.coords[0] / TILE_SIZE, self.coords[1] / TILE_SIZE
        end = coords[0] / TILE_SIZE, coords[1] / TILE_SIZE
        updated_grid = self.goc.rooms[self.current_room].grid
        if not self.route:
            self.route = astar(updated_grid, start, end)
        try:
            new_x, new_y = self.route[1][0] * TILE_SIZE, self.route[1][1] * TILE_SIZE
            print('newx/newy {0},{1}'.format(new_x, new_y))
            self.coords = [new_x, new_y]
            return self.route
        except IndexError:
            self.route = []
            return None
        # Return None if we have arrived at our destination
        self.route = []
        return None

    def update_grid(self, grid):
        coord_list = [(go.coords[0] / 8, go.coords[1] / 8) for go in self.goc.lifeforms.values()]
        print(coord_list)
        for coords in coord_list:
            grid[coords[1]][coords[0]] = 1
        return grid

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
        if self.ai:
            if self.aic.running:
                self.aic.run(dt)

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


class Item(object):
    def __init__(self, templatefile):
        tp = TemplateParser()
        data = tp.load_data(templatefile)
        print(data)
        self.settings = data['settings']
        try:
            self.sprites = data['sprites']
        except KeyError:
            self.sprites = None
        try:
            self.stats = data['stats']
        except KeyError:
            self.stats = None
        try:
            self.scripts = data['scripts']
        except KeyError:
            self.scripts = None

    @property
    def sprite(self):
        try:
            return self._value(self.sprites['main'])
        except KeyError:
            return None

    @property
    def name(self):
        return self.uniquename

    @property
    def uniquename(self):
        return self.settings['uniquename']

    @property
    def weight(self):
        try:
            return self._value(self.settings['weight'])
        except KeyError:
            return None

    @property
    def fullname(self):
        return self._value(self.settings['fullname'])

    @property
    def item_type(self):
        try:
            return self.settings['item_type']
        except KeyError:
            return None

    @property
    def equippable_slot(self):
        try:
            return self.settings['equippable_slot']
        except KeyError:
            return None


class Inventory(object):
    def __init__(self, inventory_data, lifeform):
        """ Inventory class, stores items and equipped items of LifeForm instance
        inventory_data: refers to parsed inventory dictionary from lifeform template file
        """
        self.lifeform = lifeform
        self.slots = []
        self.equip_slots = {'head': None, 'neck': None, 'chest': None, 'wrists': None,
                            'ring1': None, 'ring2': None, 'idol': None, 'belt': None,
                            'legs': None, 'feet': None, 'weapon': None, 'offhand': None,
                            'ranged': None, 'ammo': None}

        # Populate Slots with item instances, equipped item if equipped is True
        # item[0]:template, item[1]:equipped?
        for item_info in inventory_data.values():
            item_template = item_info[0]
            try:
                equipped = item_info[1]
            except IndexError:
                equipped = False
            index = self.add_item(item_template)
            if equipped:
                print(equipped)
                self.equip_item(index)

    @property
    def weight(self):
        weight = 0
        for item in self.slots:
            if item.stats.weight:
                weight += item.stats.weight
        return weight

    def add_item(self, itemtemplate):
        """ Add item to inventory """
        item = Item(itemtemplate)
        self.slots.append(item)
        return len(self.slots) - 1

    def item_in_inventory(self, uniquename):
        """ Returns index of first item with given uniquename, if item not in inventory returns None """
        for i, item in enumerate(self.slots):
            if item.uniquename == uniquename:
                return i
        return None

    def is_equipped(self, uniquename):
        """ Returns True or False if given item (by uniquename) is equipped """
        for slot, item in self.equip_slots.items():
            if item.uniquename == uniquename:
                return True
        return False

    def equip_item(self, index):
        """ Equips item of given index into its equippable slot, if it cannot be equipped will raise """
        try:
            item = self.slots[index]
        except IndexError:
            raise RuntimeError('No item in inventory with given index {0}'.format(index))

        # If item isn't in inventory
        if self.item_in_inventory(item.uniquename) is None:
            raise RuntimeError('{0} is not in inventory'.format(item))

        # If item doesn't have an equippable slot
        if not item.equippable_slot:
            raise RuntimeError('{0} is not equipabble'.format(item.name))

        equip_slot = item.equippable_slot

        if self.equip_slots[equip_slot] and self.equip_slots[equip_slot] != item:
            # If a different item already equipped, unequip it
            self.unequip_item(equip_slot)
        elif self.equip_slots[equip_slot] and self.equip_slots[equip_slot] == item:
            # If this item already equipped do nothing
            logging.debug('Trying to equip item that is already equipped, doing nothing')
            return

        self.equip_slots[equip_slot] = item

    def unequip_slot(self, equip_slot):
        """ Unequips item in given slot """
        equipped_item = self.equip_slots[equip_slot]
        # If nothing is equipped in slot, or item not even in inventory, raise
        if not equipped_item:
            raise RuntimeError('No item equipped in {0} slot'.format(equip_slot))
        # Remove item from equipped slot
        self.equip_slots[equip_slot] = None

    def unequip_item(self, index):
        """ Unequips item by index, if given index does not refer to equipped item, will raise """
        try:
            item = self.slots[index]
        except IndexError:
            raise RuntimeError('No item in inventory with given index {0}'.format(index))
        equip_slot = item.equippable_slot
        if self.equip_slots[equip_slot] == item:
            self.equip_slots[equip_slot] = None
        else:
            raise RuntimeError('Item with index {0} is not equipped in {1}'.format(index, equip_slot))

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

