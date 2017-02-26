"""
Test based mushy fun!
"""
import logging
import template_constants
import gc
import itm_parser
import lfm_parser
import rm_parser
import dlg_parser
import pickle
import json
import os
# import pytmx

# gc.collect()   -- this will garbage collect actively


def print_room_contents(room):
    """
    Rooms do not have ids, use a reference to room instance as argument
    """
    roomitems = room.items
    for k, v in room.lifeforms.items():
        print('[{0}]: {1}'.format(k, v.name))
    for k, v in roomitems.items():
        print('[{0}]: {1}'.format(k, v.name))
    for k, v in room.links.items():
        print('[{0}]: {1}'.format(k, v))


def print_lifeform_inventory(id):
    slots = get_object_by_id(id).inventory.slots
    inventory = get_object_by_id(id).inventory
    for i, item in enumerate(slots):
        if item:
            if inventory.is_equipped(item.id):
                equip_slot = item.equippable_slot
                print('{0}: {1} [{2}]'.format(i, item.name, equip_slot))
            else:
                print('{0}: {1}'.format(i, item.name))


def print_name(id):
    print('Name: {0}'.format(get_object_by_id(id).name))


def print_lifeform_stats(id):
    """
    Print all stats (base and from items) of given lifeform from id
    """
    for stat in template_constants.all_stats:
        print_lifeform_stat(id, stat)


def print_lifeform_stat(id, stat):
    base_stats = get_object_by_id(id).stats.__getattribute__(stat)
    stats_from_equip = get_stat_from_equipment(id, stat)
    total_stats = base_stats + stats_from_equip
    print('{0}: {1} ({2}+{3})'.format(stat, total_stats, base_stats, stats_from_equip))


# Core Commands


def dict_rooms(type='Room'):
    return {o.name: o for o in gc.get_objects() if isinstance(o, eval(type))}


def list_rooms():
    return [o for o in gc.get_objects() if isinstance(o, eval('Room'))]


def dict_gameobjects(type='GameObject'):
    return {o.id: o for o in gc.get_objects() if isinstance(o, eval(type))}


def get_object_by_id(id, type='GameObject'):
    id = int(id)
    try:
        game_object = dict_gameobjects(type=type)[id]
        return game_object
    except KeyError:
        raise RuntimeError('Game object {0} does not exist'.format(id))


def get_room_from_lifeform(id):
    """
    Returns reference to room where given id (lifeform) dwells, will return None if lifeform not in a room
    """
    for room in list_rooms():
        for k, lifeform in room.lifeforms.items():
            if lifeform.id == id:
                return room
    return None


def get_room_from_uniquename(uniquename):
    for room in list_rooms():
        if room.uniquename == uniquename:
            return room
    return None


def get_stat_from_equipment(id, stat):
    """
    Returns total stat bonuses from equipment of given stat from given id
    """
    slots = get_object_by_id(id).inventory.equip_slots
    values = [v.stats.__getattribute__(stat) for k, v in slots.items() if v]
    values = [item for item in values if item is not None]
    if values:
        return sum(values)
    else:
        return 0


def create_gameobject(type='GameObject', **kwargs):
    id_list = [o.id for o in gc.get_objects() if isinstance(o, eval('GameObject'))]
    if id_list:
        id = max(id_list) + 1
    else:
        id = 1
    return eval(type)(id, **kwargs)


def create_item_from_template(filename):
    properties = itm_parser.dict_lines(filename)

    # create ItemStats class to compose with Item created
    # TODO: OnHit effects and such
    item_stats = ItemStats(HP=properties['HP'], MP=properties['MP'], MND=properties['MND'],
                           STA=properties['STA'], STR=properties['STR'], SPD=properties['SPD'],
                           PDMG=properties['PDMG'], PDEF=properties['PDEF'], MDEF=properties['MDEF'],
                           MDMG=properties['MDMG'], weight=properties['weight'])

    # create item of correct class from response object
    classes = template_constants.item_classes
    item = create_gameobject(type=classes[properties['item_type']], name=properties['name'],
                             description=properties['description'], equippable_slot=properties['equippable_slot'],
                             item_stats=item_stats)
    return item


def create_lifeform_from_template(filename):
    properties = lfm_parser.dict_lines(filename)
    stats = Stats(HP=properties['HP'], MP=properties['MP'], MND=properties['MND'],
                  STA=properties['STA'], STR=properties['STR'], SPD=properties['SPD'],
                  PDEF=properties['PDEF'], MDEF=properties['MDEF'])

    # Update inventory from response
    inventory = Inventory(max_slots=properties['slots'])
    for i, item in enumerate(properties['inventory']):
        if item:
            inventory.slots[i] = create_item_from_template(item['path'])
            if item['equipped']:
                inventory.equip_item(inventory.slots[i].id)

    # Drop rate TODO

    # Dialogue fix if no dialogue
    try:
        dialogue = properties['dialogue']
    except KeyError:
        dialogue = None

    lifeform = create_gameobject(type='LifeForm', name=properties['name'], stats=stats, inventory=inventory,
                                 dialogue=dialogue, graphic=properties['graphic'])
    return lifeform


def create_room_from_template(filename):
    properties = rm_parser.dict_lines(filename)
    lifeforms = [create_lifeform_from_template(path) for path in properties['lifeforms']]
    items = [create_item_from_template(path) for path in properties['items']]
    # TODO linking
    links = properties['links']
    settings = properties['settings']
    room = Room(name=settings['name'], atenter=settings['atenter'], atexit=settings['atexit'], look=settings['look'],
                listen=settings['listen'], tmx_map=settings['tmx_map'], lifeforms=lifeforms, items=items, links=links,
                uniquename=settings['uniquename'])
    return room


def create_dialogue_from_template(filename):
    return dlg_parser.dict_lines(filename)


def save_lifeform(lifeform, filename):
    with open(filename, 'wb') as f:
        pickle.dump(lifeform, f, protocol=pickle.HIGHEST_PROTOCOL)
        f.close()


def load_lifeform(filename):
    with open(filename, 'rb') as f:
        lifeform = pickle.load(f)
        f.close()

    # Assign unique id to lifeform
    id_list = [o.id for o in gc.get_objects() if isinstance(o, eval('GameObject'))]
    if id_list:
        id = max(id_list) + 1
    else:
        id = 1
    lifeform.id = id
    return lifeform


def load_user(character, username, password, users_file='users.json'):
    #location = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
    #filename = os.path.join(location, users_file)
    with open('mp/users/{0}'.format(users_file), 'r') as f:
        userdata = json.load(f)
        f.close()
    current_user = userdata[username]
    if current_user['password'] != password:
        raise RuntimeError('Incorrect password')
    filename = current_user['characters'][character]
    return load_lifeform('mp/users/{0}'.format(filename))


def add_lifeform_to_room(lifeformid, room_instance, coords=(0, 0)):
    # lifeform = get_object_by_id(lifeformid)
    # new_lifeform_key = max(room_instance.lifeforms.keys()) + 1
    # room_instance.lifeforms[new_lifeform_key] = lifeform
    # lifeform.coords = coords
    lifeform = get_object_by_id(lifeformid)
    lifeform.coords = coords
    room_instance.add_lifeform_by_id(lifeformid, coords)


# Classes
class Room(object):
    """
    This is a room class.
    """
    def __init__(self, name='unnamed_room', atenter='', atexit='', look='', listen='',
                 lifeforms=None, items=None, links=None, uniquename=None, tmx_map=None):
        self.name = name
        self.uniquename = uniquename
        self.atenter = atenter
        self.atexit = atexit
        self.look = look
        self.listen = listen
        # Path to tmx map (not an instance of a pytmx)
        self.tmx_map = tmx_map
        self.lifeforms = {i: lifeform for i, lifeform in enumerate(lifeforms)} if lifeforms else {}
        next_i = len(self.lifeforms)
        self.lifeforms = {lifeform.id: lifeform for rm_index, lifeform in self.lifeforms.items()}
        self.items = {i+next_i: item for i, item in enumerate(items)} if items else {}
        next_i = len(self.items) + len(self.lifeforms)
        self.links = {i+next_i: link for i, link in enumerate(links)} if links else {}

    def remove_gameobject_by_id(self, id):
        # TODO: Make this work for items and links
        for k, lifeform in self.lifeforms.items():
            if lifeform.id == id:
                del self.lifeforms[k]

    def remove_lifeform_by_id(self, id):
        for k, lifeform in self.lifeforms.items():
            if lifeform.id == id:
                del self.lifeforms[k]

    def add_lifeform_by_id(self, id, coords):
        lifeform = get_object_by_id(id)
        lifeform.current_room = self
        # new_lifeform_key = max(self.lifeforms.keys()) + 1
        # self.lifeforms[new_lifeform_key] = lifeform
        self.lifeforms[lifeform.id] = lifeform
        lifeform.coords = coords

    def add_item_by_id(self, id, coords):
        item = get_object_by_id(id)
        new_item_key = max(self.items.keys()) + 1
        self.items[new_item_key] = item
        item.coords = coords

    def add_link(self, filename):
        new_link_key = max(self.links.keys()) + 1
        self.links[new_link_key] = filename


class GameObject(object):
    def __init__(self, id, name='unnamed_gameobject', coords=[0, 0], graphic=None, dialogue=None,
                 current_room=None, **kwargs):

        self.id = id
        self.name = name
        self.destroyed = False
        self.coords = coords
        self.graphic = graphic
        self.dialogue = create_dialogue_from_template(dialogue) if dialogue else None
        self.current_room = current_room

        # Update all attributes with kwargs
        self.__dict__.update(kwargs)


class LifeForm(GameObject):
    def __init__(self, id, name='unnamed_lifeform', coords=[0, 0], stats=None, inventory=None, graphic=None,
                 dialogue=None, target=None, current_room=None,  **kwargs):
        super(LifeForm, self).__init__(id=id, name=name, current_room=current_room, coords=coords,
                                       graphic=graphic, dialogue=dialogue, **kwargs)
        if not stats:
            self.stats = Stats()
        else:
            self.stats = stats
        if not inventory:
            self.inventory = Inventory()
        else:
            self.inventory = inventory

        # Target points to an gameobject id (not an object instance)
        self.target = target

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
        other = get_object_by_id(targetid)
        try:
            response = other.respond([self.id, dialogue])
        except AttributeError:
            response = 'Cannot speak to that!'
        return response

    def respond(self, dialogue_command):
        """
        Parse dialogue command and respond with conversation string as well as perform any required actions
        :param dialogue_command: list like: [<playerid>, 'hello how are you?']
        :return: respone dialogue string
        """
        if not self.dialogue:
            return None
        otherid = dialogue_command[0]
        dialogue = dialogue_command[1]
        response_list = []
        for word in dialogue.split():
            if word[-1] == '?' or word[-1] == '.':
                word = word[:-1]
            if word in self.dialogue.keys():
                response_list = self.dialogue[word]
                break
        if response_list:
            dialogue_actions = [line for line in response_list if line[0] == '{' and line[-1] == '}']
            dialogue_actions = [line.replace('{', '').replace('}', '') for line in dialogue_actions]
            # Check if there is a prerequisite (need) block in the actions and abort if not satisfied
            for i, action in enumerate(dialogue_actions):
                if action.split()[0] == 'need':
                    required_item_template = action.split()[1]
                    required_item = create_item_from_template(required_item_template)
                    if get_object_by_id(otherid).inventory.item_name_in_inventory(required_item.name):
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
                targetplayer = get_object_by_id(targetid)
                command = action.split()[0]
                params = action.split()[1:]

                if command == 'give':
                    # Create item and give to target player
                    item = create_item_from_template(params[0])
                    targetplayer.add_item(item.id)

                elif command == 'take':
                    # If player has item in inventory, take it, if item is equipped, unequip it first
                    required_item_template = params[0]
                    required_item = create_item_from_template(required_item_template)
                    if targetplayer.inventory.item_name_in_inventory(required_item.name):
                        itemid = targetplayer.inventory.get_itemid_in_inventory_by_name(required_item.name)
                        if itemid:
                            if targetplayer.inventory.is_equipped(itemid):
                                targetplayer.unequip_item(itemid)
                            targetplayer.drop_item(itemid)
                        else:
                            pass

                elif command == 'teleport':
                    # Teleport player to target room and coords
                    room = get_room_from_uniquename(params[0])
                    coords = [int(params[1]), int(params[2])]
                    targetplayer.teleport(room, coords)

                elif command == 'cast':
                    # Cast spell on player
                    self.cast(targetplayer.id, params[0])

                elif command == 'dialogue':
                    # Switch to new dialogue script
                    dialogue = create_dialogue_from_template(params[0])
                    self.dialogue = dialogue

                elif command == 'remove self':
                    # Remove self from game
                    room = get_room_from_lifeform(self.id)
                    room.remove_gameobject_by_id(self.id)

                elif command == 'spawn':
                    # Spawn lifeform in room
                    lifeform = create_lifeform_from_template(params[0])
                    coords = [int(params[1]), int(params[2])]
                    room = get_room_from_lifeform(self.id)
                    room.add_lifeform_by_id(lifeform.id, coords)
            except:
                return 1
        return 0


class Inventory(object):
    def __init__(self, max_slots=20):
        self.slots = [None]*max_slots
        self.equip_slots = {'head': None, 'mask': None, 'neck': None,
                            'chest': None, 'wrist1': None, 'wrist2': None,
                            'ring1': None, 'ring2': None, 'idol': None,
                            'belt': None, 'legs': None, 'boots': None,
                            'right_hand': None, 'left_hand': None,
                            'ranged': None, 'ammo': None}
        self.max_slots = max_slots
        self.weight = 0

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
        item_to_add = get_object_by_id(id)
        for i, slot in enumerate(self.slots):
            if slot is None:
                self.slots.insert(i, item_to_add)
                break

    def item_in_inventory(self, id):
        return get_object_by_id(id) in self.slots

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
            instance = get_object_by_id(id)
            item_slot = item.equippable_slot
        if item_slot:
            return self.equip_slots[item_slot] == instance
        else:
            return False

    def equip_item(self, id):
        new_item = get_object_by_id(id)
        equip_slot = new_item.equippable_slot

        # If item has no equip slot, or has an invalid equip slot
        if equip_slot not in template_constants.all_equip_slots:
            raise RuntimeError('{0} is not a valid equip_slot'.format(equip_slot))

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


class Stats(object):
    def __init__(self, **kwargs):
        # Make sure only kwargs passed in are valid stats
        for k, v in kwargs.items():
            if k not in template_constants.all_stats:
                raise RuntimeError('{0} is not a valid stat'.format(k))
        # Create dict of all stat names and set default values to 0, update, and set as class attributes
        base_dict = {stat_name: 0 for stat_name in template_constants.all_stats}
        base_dict.update(kwargs)
        self.__dict__.update(base_dict)


class ItemStats(object):
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


class ItemGeneric(GameObject):
    def __init__(self, id, name='unnamed_generic_item', coords=(0, 0), description='', graphic=None,
                 equippable_slot=None):
        super(ItemGeneric, self).__init__(id=id, coords=coords, graphic=graphic)
        self.name = name
        self.description = description
        self.equippable_slot = equippable_slot
        self.anchored = False
        # Only if the object is in the room will the coords and graphic will be displayed.
        self.coords = coords


class ItemWeapon(ItemGeneric):
    def __init__(self, id, name='unnamed_weapon', item_stats=None, description='', equippable_slot=None,
                 coords=(0, 0), graphic=None):
        super(ItemWeapon, self).__init__(id=id, name=name, description=description, equippable_slot=equippable_slot,
                                         coords=coords, graphic=graphic)
        self.stats = item_stats


class ItemIngredient(ItemGeneric):
    def __init__(self, id, name='unnamed_ingredient', item_stats=None, description='', equippable_slot=None,
                 coords=(0, 0), graphic=None):
        super(ItemIngredient, self).__init__(id=id, name=name, description=description, equippable_slot=equippable_slot,
                                             coords=coords, graphic=graphic)
        self.stats = item_stats


class ItemApparel(ItemGeneric):
    def __init__(self, id, name='unnamed_apparel', item_stats=None, description='', equippable_slot=None,
                 coords=(0, 0), graphic=None):
        super(ItemApparel, self).__init__(id=id, name=name, description=description, equippable_slot=equippable_slot,
                                          coords=coords, graphic=graphic)
        self.stats = item_stats


class ItemPotion(ItemGeneric):
    def __init__(self, id, name='unnamed_potion', item_stats=None, description='', equippable_slot=None,
                 coords=(0, 0), graphic=None):
        super(ItemPotion, self).__init__(id=id, name=name, description=description, equippable_slot=equippable_slot,
                                         coords=coords, graphic=graphic)
        self.stats = item_stats


class ItemMisc(ItemGeneric):
    def __init__(self, id, name='unnamed_misc', item_stats=None, description='', equippable_slot=None,
                 coords=(0, 0), graphic=None):
        super(ItemMisc, self).__init__(id=id, name=name, description=description, equippable_slot=equippable_slot,
                                       coords=coords, graphic=graphic)
        self.stats = item_stats


class ItemProp(ItemGeneric):
    def __init__(self, id, name='unnamed_prop', item_stats=None, description='', equippable_slot=None,
                 coords=(0, 0), graphic=None):
        super(ItemProp, self).__init__(id=id, name=name, description=description, equippable_slot=equippable_slot,
                                       coords=coords, graphic=graphic)
        self.stats = item_stats
        self.anchored = True


class Graphic(object):
    def __init__(self, images=None):
        """
        :param images: list of paths to images
        """
        self.images = images
        if images:
            self.image = images[0]
        else:
            self.image = None


# Character Gen


def calculate_stats(STR, MND, STA, SPD):
    # Base values
    HP = 5
    MP = 5
    PDEF = 1
    MDEF = 1

    HP = int(HP + (.75 * STA))
    MP = int(MP + (.75 * MND))
    MDEF = int(MDEF + ((.5 * MND) + .25 * SPD))
    PDEF = int(PDEF + ((.5 * STR) + .25 * SPD))
    return HP, MP, PDEF, MDEF


def character_gen():
    print('Generate Player Template from input')

    # Input name and description
    while True:
        lifeform_type = 'lifeform_type:LifeForm'
        name = 'name:' + raw_input('Player name: ')
        description = 'description:' + raw_input('Description: ')
        choice = raw_input('Confirm choices? y/n: ')
        if choice.lower() == 'y':
            break

    while True:
        proposal = int(raw_input('Power level (determines stat_points to spend): 1-100: '))
        if proposal > 100:
            proposal = 100
        elif proposal < 0:
            proposal = 1
        stat_points = proposal * 5

        re_run = False
        print('')
        print('Choose stat allocation for STR, MND, STA and SPD.  These core stats will effect auxilliary stats')
        print('Total Points: {0}'.format(stat_points))
        try:
            stat_dict = {}
            for item in ['STR', 'MND', 'STA', 'SPD']:
                stat_dict[item] = int(raw_input('{0}: '.format(item)))
                stat_points -= stat_dict[item]
                print('Remaining points: {0}'.format(stat_points))
        except ValueError:
            print('Must enter numerical value!')
            re_run = True
        if stat_points < 0:
            re_run = True
            print('Used too many stat points! Try again')
        elif stat_points > 0:
            re_run = True
            print('You still have {0} unspent stat points! Try again'.format(stat_points))
        if re_run:
            pass
        else:
            HP, MP, PDEF, MDEF = calculate_stats(stat_dict['STR'], stat_dict['MND'], stat_dict['STA'], stat_dict['SPD'])
            print('Calculating stats...')
            print('')
            print('HP: {0}'.format(HP))
            print('MP: {0}'.format(MP))
            print('PDEF: {0}'.format(PDEF))
            print('MDEF: {0}'.format(MDEF))
            choice = raw_input('Confirm stat allocation? y/n: ')
            if choice.lower() == 'y':
                STR = 'STR:{0}'.format(stat_dict['STR'])
                MND = 'MND:{0}'.format(stat_dict['MND'])
                STA = 'STA:{0}'.format(stat_dict['STA'])
                SPD = 'SPD:{0}'.format(stat_dict['SPD'])
                HP = 'HP:{0}'.format(HP)
                MP = 'MP:{0}'.format(MP)
                MDEF = 'MDEF:{0}'.format(MDEF)
                PDEF = 'PDEF:{0}'.format(PDEF)
                break

    while True:
        filename = raw_input('Character Filename to create: ')
        if '.lfm' not in filename:
            filename = '{0}.lfm'.format(filename)
        choice = raw_input('Confirm filename? y/n: ')
        if choice.lower() == 'y':
            break

    cwd = os.getcwd()
    filepath = '{0}/mp/users/{1}'.format(cwd, filename)
    with open(filepath, 'w') as f:
        for line in [name, lifeform_type, description, STR, STA, MND, SPD, HP, MP, MDEF, PDEF]:
            f.write('{0}\n'.format(line))
        f.close()

    lifeform_instance = create_lifeform_from_template(filepath)
    save_lifeform(lifeform_instance, '{0}/mp/users/{1}.sav'.format(cwd, name.replace('name:', '')))
