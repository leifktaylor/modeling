#import logging
from __future__ import print_function
from colorama import init
from colorama import Fore, Back, Style
import random
import logging
import sys
import os
import subprocess
init()

#TODO: Move this to a place that makes sense.
room_delim = ' '

def start_game(**kwargs):
    width = 10
    height = 10
    if 'width' in kwargs: width = kwargs['width']
    if 'height' in kwargs: height = kwargs['height']


# def control_player(player):
#     player.look_around()
#     current_room = player.current_room
#     result = ''
#     move_commands = ['left', 'right', 'up', 'down']
#     interact_commands = ['look', 'inspect', 'speak']
#     menu_commands = ['quit', 'help']
#     commandlist = [move_commands, interact_commands, menu_commands]
#     while result != 'quit':
#         print('\n')
#         result = raw_input('Choose Action: ')
#         if result in commandlist[0] or result in commandlist[1] or result in commandlist[2]:
#             if result == 'left': player.move('left')
#             if result == 'right': player.move('right')
#             if result == 'down': player.move('down')
#             if result == 'up': player.move('up')
#             if result == 'help': print(commandlist)
#             if result == 'look': player.look_around()
#         else:
#             print_colored('Not a valid choice: Enter "help" for a list of commands', Fore.BLUE, Back.WHITE)


class LifeFormController(object):
    def __init__(self, player):
        #Exchange 'certificates' with player
        self.player = player
        self.player.controller = self
        self.current_room = player.current_room

        #Initialize list of commands for user
        self.commandlist = [['left', 'right', 'up', 'down'],
                            ['attack', 'inspect', 'speak', 'use'],
                            ['save', 'load', 'quit']]

    def control_player(self):
        """
        Take input from player and cause the player's LifeForm object
        to perform the given action.

        :return:
        """
        #Load commandlist and metadata from player LifeForm object
        commandlist = self.commandlist
        player = self.player
        #Take player input
        result = 'repeat'
        while result == 'repeat':
            print('\n')
            result = raw_input('Choose Action: ')
            if result in commandlist[0] or result in commandlist[1] or result in commandlist[2]:
                if result == 'left': player.move('left')
                if result == 'right': player.move('right')
                if result == 'down': player.move('down')
                if result == 'up': player.move('up')
                if result == 'help': print(commandlist)
                if result == 'look': player.look_around()
            else:
                print_colored('Not a valid choice: Enter "help" for a list of commands', Fore.BLUE, Back.WHITE)
                result = 'repeat'
        return result

    def control_enemies(self):
        """
        Controls the enemies in the room.

        :return:
        """
        current_room = self.current_room
        for enemies in current_room.room_contents['enemies']:
            current_enemy = current_room.room_contents['enemies'][enemies]
            current_enemy.normal_ai()



def print_colored(string, color=Fore.WHITE, backdrop=Back.BLACK, **kwargs):
    """
    Prints colored text with foreground and/or background colors.

    Usage Example:
    print('Hello there!', Fore.BLUE, Back.RED)

    :param string: string to print
    :param color: Fore.COLOR (e.g. WHITE, BLUE, RED)
    :param backdrop: Back.COLOR (e.g. WHITE, BLUE, RED)
    :return:
    """
    if 'end' in kwargs:
        print(color + backdrop + str(string) + Style.RESET_ALL, end="")
    else:
        print(color + backdrop + str(string) + Style.RESET_ALL)

class Dungeon(object):
    """
    Dungeon -> Floor -> Room

    """
    def __init__(self):
        self.floors = []
        self.rooms = []

    def draw_floor(self):
        """
        Draws the floor map.
        :return:
        """
        for i in range(0, len(self.floor1)):
            print(self.floor1[i])

    def create_room(self, width, height):
        room = []
        for row in range(height):
            room.append([])
            for column in range(width):
                room[row].append(room_delim)
        new_room = Room(room)
        print('Creating room with width of {} and height of {}'.format(width, height))
        return new_room

class Room(object):
    """
    Room can be populated with treasure, enemies, and npcs.

    """
    def __init__(self, room_map=[0]):
        self.room_map = room_map
        self.init_room_map = room_map
        self.enemies = []
        self.treasure = []
        self.npcs = []
        self.players = []
        self.stairs = []
        self.room_contents = {'enemies' : self.enemies, 'treasure' : self.treasure,
                              'npcs' : self.npcs, 'players' : self.players, 'stairs' : self.stairs}



    def update_room(self):
        for row in range(len(self.room_map)):
            for column in range(len(self.room_map[row])):
                self.room_map[row][column] = room_delim
        self.populate_room()


    def populate_room(self):
        """
        Populates room with enemies, treasure, players, and npcs that are in the
        room_contents dictionary.
        :return:
        """
        clear_screen()
        #populate room with enemies
        total_enemies = len(self.room_contents['enemies'])
        for i in range(0, total_enemies):
            enemy_number = i
            x_pos = self.room_contents['enemies'][i].x
            y_pos = self.room_contents['enemies'][i].y
            logging.info('Placing Enemy {0}/{1} at {2},{3}'.format(enemy_number, total_enemies, x_pos, y_pos))
            #Determine Sprite to draw
            enemy_name = self.room_contents['enemies'][i].stats['name']
            enemy_sprite = LifeForm.bestiary[enemy_name]['sprite']
            self.room_map[y_pos][x_pos] = enemy_sprite
        #populate room with players
        for i in range(0, len(self.room_contents['players'])):
            self.room_map[self.room_contents['players'][i].y][self.room_contents['players'][i].x] = 'P'
        #populate room with stairs
        total_stairs = len(self.room_contents['stairs'])
        for i in range(0, total_stairs):
            stairs_number = i
            x_pos = self.room_contents['stairs'][i].x
            y_pos = self.room_contents['stairs'][i].y
            logging.info('Placing Stairs {0}/{1} at {2},{3}'.format(stairs_number, total_stairs, x_pos, y_pos))
            self.room_map[y_pos][x_pos] = 'S'

    def add_stairs_down(self):
        """
        Adds stairs which progress the player to the next room.

        :return:
        """
        room_width = len(self.room_map[0]) - 1
        room_height = len(self.room_map) - 1
        x_pos = random.randint(0, room_width)
        y_pos = random.randint(0, room_height)
        self.room_contents['stairs'].append(Stairs(x_pos, y_pos, self))

    def draw_room(self):
        """
        Draws the room map.
        :return:
        """
        #Get all possible enemy sprites
        enemy_tiles = []
        for key, value in LifeForm.bestiary.items():
            enemy_tiles.append(LifeForm.bestiary[key]['sprite'])
        #Draw sprites on screen
        for row in range(len(self.room_map)):
            print('\n')
            for column in range(len(self.room_map[row])):
                current_tile = str(self.room_map[row][column])
                if current_tile == 'P': print_colored(" " + current_tile + " ", Fore.YELLOW, Back.BLUE, end="")
                if current_tile in enemy_tiles:
                    print_colored(" " + current_tile + " ", Fore.BLACK, Back.RED, end="")
                if current_tile == 'S': print_colored(" " + current_tile + " ", Fore.BLUE, Back.BLACK, end="")
                if current_tile == room_delim: print_colored(" " + current_tile + " ", Fore.BLACK, Back.WHITE, end="")


    def add_enemies_to_room(self, enemies=0, name='unnamed', damage=1, hp=10, x=0, y=0):
        """
        Add enemies to list of enemies in room.  Does not spawn them though.

        :param enemies: number of enemies to populate room with
        :param name: name of enemies to create
        :param damage: damage stat
        :param hp: health stat
        :return:
        """
        for i in range(enemies):
            current_enemy = LifeForm(name, damage, hp, x, y)
            self.enemies.append(current_enemy)
            print('Created {0} with {2} hp and {1} attack damage.'.format(current_enemy.stats['name'],
                                                                          current_enemy.stats['damage'],
                                                                          current_enemy.stats['hp']))
        pass

    def add_player_to_room(self, name='unnamed', damage=1, hp=10):
        """
        Adds a player to the room. Must populate room for him to appear on map

        :param name:
        :param damage:
        :param hp:
        :return:
        """
        print('Populating room with {0}'.format(name))
        self.players.insert(0, LifeForm(name, damage, hp))
        self.players[0].current_room = self
        print('Created {0} with {2} hp and {1} attack damage.'.format(self.players[0].stats['name'],
                                                                    self.players[0].stats['damage'],
                                                                    self.players[0].stats['hp']))
        return self.players[0]

    def _list_enemy_stats(self):
        """
        Used for debugging. Lists all enemies in room and their stats.

        :return:
        """

        enemy_list = self.room_contents['enemies']
        for enemy in enemy_list:
            print(enemy.stats)

class Stairs(object):
    """
    Entrances and exits.  Connects rooms together.

    """
    def __init__(self, x=0, y=0, current_room=0):
        self.x = x
        self.y = y
        self.current_room = current_room


class LifeForm(object):
    """
    Players, enemies, and NPCs can be lifeforms.  This is a parent class.

    """
    #Stores data for all enemies
    bestiary = {'Goblin': {'behaviors': ('pokes', 'sneers', 'I will bring you to Nig-Nok!', 'melts into gobliny gore'),
                           'stats': (1, 1, 1),
                           'info': ['Goblin', 'green and snarly'],
                           'sprite': 'g'},
                'Griffon': {'behaviors': ('claws', 'roar', 'Raaaaar!', 'falls into a pile of feathers'),
                            'stats': (2, 2, 2),
                            'info': ['Griffon', 'glorious and feathered'],
                            'sprite': 'G'},
                'Serpent': {'behaviors': ('bites', 'hisses', 'hisssssss', 'coils into death'),
                            'stats': (1, 2, 1),
                            'info': ['Serpent', 'reminiscent of bad choices...'],
                            'sprite': 's'},
                'Fire Mephit': {'behaviors' : ('scorches', 'cackles', 'Burn in the fires of Scoro!', 'fizzles out'),
                                'stats': (1, 2, 2),
                                'info': ['Fire Mephit', 'a small winged fiery little devil!'],
                                'sprite': 'F'},
                'Sludge Lord': {'behaviors' : ('envelopes', 'groans', 'Forrr Gorrrrloooxxx!', 'melts into goo'),
                                'stats': (2, 1, 2),
                                'info': ['Sludge Lord', 'grotesque and smells horrible'],
                                'sprite': 'L'},
                'Skeleton': {'behaviors': ('slashes', 'shriek', 'For the skeleton king!', 'falls into a pile'),
                             'stats': (1, 1, 1),
                             'info': ['Skeleton', 'stereotypically skeleton-like'],
                             'sprite': 'k'},
                'Arch Demon': {'behaviors': ('eviscerates', 'laughs', 'You will face the Dark One', 'is vanquished'),
                               'stats': (3, 3, 3),
                               'info': ['Arch Demon', 'kinda like the Baal Roc in lord of the rings!'],
                               'sprite': 'D'},
                'Rat': {'behaviors': ('bites', 'squeeks', 'cchhchchchch!', 'poofs into scarps of fur'),
                        'stats': (1, 1, 1),
                        'info': ['Rat', 'just one mean looking rat!'],
                        'sprite': 'r'}}

    def __init__(self, name='unnamed', damage=1, hp=10, x=0, y=0, current_room=0):
        self.stats = {'name': name, 'damage': damage, 'hp': hp}
        self.x = x
        self.y = y
        self.current_room = current_room
        self.controller = ''

    def attack(self, target):
        """
        Attack another LifeForm instance.  Reduces target.stats['hp'] by calling instance's stats['damage']
        Can also attack self.

        :param target: Reference to another LifeForm instance.
        :return:
        """
        target.stats['hp'] -= self.stats['damage']
        print('{0} attacked {1} for {2} damage.'.format(self.stats['name'], target.stats['name'], self.stats['damage']))
        pass

    def search_room(self, room=''):
        """
        Displays the contents of a room, enemies, treasure, etc.

        :param room: The room to search
        :return:
        """
        if not room:
            print('No room to search in')
        else:
            print(room.room_contents)

    def move(self, dir=''):
        """
        Moves the player while checking for collisions with enemies, boundaries, treasure, and other objects.

        :param dir:
        :return:
        """
        if not dir:
            print('{} stands still.'.format(self.stats['name']))
        else:
            #self.current_room.room_map[self.y][self.x] = 0
            if dir == 'down':
                self.check_collision(self.x, self.y + 1)
            if dir == 'up':
                self.check_collision(self.x, self.y - 1)
            if dir == 'left':
                self.check_collision(self.x - 1, self.y)
            if dir == 'right':
                self.check_collision(self.x + 1, self.y)
            self.look_around()

    def check_collision(self, x, y):
        """
        Checks to see if moving would collide with a solid object, enemy, or move outside
        the boundary of the room.

        :param x: x location object will attempt to move to
        :param y: y location object will attempt to move to
        :return:
        """
        #check room boundary
        if x in range(0, len(self.current_room.room_map[0])) and y in range(0, len(self.current_room.room_map)):
            self.x = x
            self.y = y
        else:
            print('{} cannot break the boundary of the room'.format(self.stats['name']))
        #check if on stairs
        if self.current_room.room_map[self.y][self.x] == 'S':
            print(str(self.stats['name']) + ' has ventured deeper into the depths!')
            #Gets the index of the room from the current dungeon
            current_floor = self.current_room.creator.rooms.index(self.current_room)
            print('{0} is {1} floors deep'.format(self.stats['name'], current_floor + 1))
            #Move the player up a room
            self.current_room = self.current_room.creator.rooms[current_floor+1]
            #TODO: check if the player is still in the old room
            #Insert the player into the new room
            self.current_room.players.insert(0, self)
            self.controller.current_room = self.current_room
            self.x = 0
            self.y = 0

    def look_around(self):
        self.current_room.update_room()
        self.current_room.draw_room()

def generate_dungeon(room_number, maxwidth=20, maxheight=20):
    """
    Generates a dungeon filled with rooms within a given size range.
    Also populates the each room of the dungeon with enemies, treasure and stairs.

    :param room_number: the amount of rooms in the dungeon
    :param maxwidth: the maximum width a room can be
    :param maxheight: the maximum height a room can be
    :return: the dungeon instance
    """
    dungeon = Dungeon()
    print('Generating dungeon with {} rooms'.format(room_number))
    current_room = 0
    for i in range(0, room_number):

        #create room
        print_colored('Room {}'.format(i), Fore.BLUE, Back.WHITE)
        width = random.randint(5, maxwidth)
        height = random.randint(5, maxheight)
        current_room = dungeon.create_room(width, height)
        current_room.level = i
        current_room.creator = dungeon

        #create enemies
        enemy_amount = random.randint(1, 5)
        for enemies in range(0, enemy_amount):
            #Randomly choose an enemy from the LifeForm bestiary
            monster_name = random.choice(LifeForm.bestiary.keys())
            health_scaler = LifeForm.bestiary[monster_name]['stats'][0]
            damage_scaler = LifeForm.bestiary[monster_name]['stats'][1]
            defense_scaler = LifeForm.bestiary[monster_name]['stats'][2]
            current_room.add_enemies_to_room(1, monster_name,
                                             random.randint(1+(2*current_room.level*damage_scaler), #min damage
                                                            1+(3*current_room.level*damage_scaler)), #max damage
                                            random.randint(1+(2*current_room.level*health_scaler), #min health
                                                           1+(4*current_room.level*health_scaler)), #max health
                                             random.randint(0, width-1),  #x coordinate
                                            random.randint(0, height-1))  #y coordinate

        #add stairs and finish populating room
        current_room.add_stairs_down()
        current_room.populate_room()
        dungeon.rooms.append(current_room)
    return dungeon

def intro_screen():
    """
    The intro screen.  Displays the logo etc.
    Asks player what options he would like to select before starting.

    :return:
    """
    print('\n')
    print(Fore.BLUE + Back.WHITE + 'THAT SAME OLE DUNGEON ADVENTURE!' + Style.RESET_ALL)
    print('=- A Horribly Generic, Extremely Sub-Par Rogue-Like -=')
    print('\n')
    print('Reach the bottom of this Dungeon and win glorious fame!')
    print('You have only one life to live; death is not an option!')
    print('\n')
    floors = raw_input('How many floors deep shall your voyage be? (10) :')
    width = raw_input('How wide can a room be? (20) :')
    height = raw_input('...and what height? (20 :')
    name = raw_input('Lastly, what is thine name? :')
    if floors < 1: floors = 1
    if width < 5: width = 5
    if height < 5: height = 5
    if not name:
        print('Ye have no name? Then thou shalt be "The Dude"')
        name = "The Dude"
    return int(floors), int(width), int(height), str(name)

def clear_screen():
    """
    Clears the screen.
    :return:
    """
    #Determine if windows or linux
    r = determine_os()
    if r == 'win32':
        tmp = subprocess.call('cls', shell=True)
    else:
        tmp = subprocess.call('clear', shell=True)

def determine_os():
    """
    Attemps to determine if the system is windows.

    :return: 'win32' or 'linux32' or 'darwin' etc
    """
    r = sys.platform
    return r


def game_start():
    logging.info('Initializing Game')
    clear_screen()
    try:
        dungeon_floors, dungeon_width, dungeon_height, player_name = intro_screen()
    except ValueError:
        print('Okay wise guy... Not going to give me a straight answer?')
        print('Enjoy a 100 floor deep dungeon then!')
        raw_input('Press Enter...')
        dungeon_floors = 1000
        dungeon_width = 20
        dungeon_height = 20
        player_name = 'Smartass'
    #Main
    dungeon = generate_dungeon(dungeon_floors, dungeon_width, dungeon_height)
    me = dungeon.rooms[0].add_player_to_room(player_name)
    controller = LifeFormController(me)
    me.look_around()
    return dungeon, controller

def game_step(controller):
    r = ''
    while r != 'quit':
        r = controller.control_player()


dungeon, controller = game_start()
game_step(controller)







