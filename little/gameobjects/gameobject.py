"""
Test based mushy fun!
"""
import logging
import template_constants
import gc
import itm_parser
import lfm_parser
import rm_parser


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


def create_gameobject(type='GameObject', **kwargs):
    id_list = [o.id for o in gc.get_objects() if isinstance(o, eval('GameObject'))]
    if id_list:
        id = max(id_list) + 1
    else:
        id = 1
    return eval(type)(id, **kwargs)


def get_stat_from_equipment(id, stat):
    """
    Returns total stat bonuses from equipment of given stat from given id
    """
    slots = get_object_by_id(id).inventory.equip_slots
    values = [slots[k].stats.__getattribute__(stat) for k, v in slots.items() if slots[k]]
    if values:
        return sum(values)
    else:
        return 0


def dict_rooms(type='Room'):
    return {o.name: o for o in gc.get_objects() if isinstance(o, eval(type))}


def list_rooms():
    return [o for o in gc.get_objects() if isinstance(o, eval('Room'))]


def get_room_from_lifeform(id):
    """
    Returns reference to room where given id (lifeform) dwells, will return None if lifeform not in a room
    """
    for room in list_rooms():
        for k, lifeform in room.lifeforms.items():
            if lifeform.id == id:
                return room
    return None


def dict_gameobjects(type='GameObject'):
    return {o.id: o for o in gc.get_objects() if isinstance(o, eval(type))}


def get_object_by_id(id, type='GameObject'):
    try:
        game_object = dict_gameobjects(type=type)[id]
        return game_object
    except KeyError:
        raise RuntimeError('Game object {0} does not exist'.format(id))


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
    inventory = Inventory()
    for i, item in enumerate(properties['inventory']):
        if item:
            inventory.slots[i] = create_item_from_template(item['path'])
            if item['equipped']:
                inventory.equip_item(inventory.slots[i].id)

    # Drop rate TODO

    lifeform = create_gameobject(type='LifeForm', name=properties['name'], stats=stats, inventory=inventory)
    return lifeform


def create_room_from_template(filename):
    properties = rm_parser.dict_lines(filename)
    lifeforms = [create_lifeform_from_template(path) for path in properties['lifeforms']]
    items = [create_item_from_template(path) for path in properties['items']]
    # TODO linking
    links = properties['links']
    settings = properties['settings']
    room = Room(name=settings['name'], atenter=settings['atenter'], atexit=settings['atexit'], look=settings['look'],
                listen=settings['listen'], lifeforms=lifeforms, items=items, links=links)
    return room


# Classes


class Room(object):
    """
    This is a room class.
    """
    def __init__(self, name='unnamed_room', atenter='', atexit='', look='', listen='',
                 lifeforms=None, items=None, links=None):
        self.name = name
        self.atenter = atenter
        self.atexit = atexit
        self.look = look
        self.listen = listen
        self.lifeforms = {i: lifeform for i, lifeform in enumerate(lifeforms)} if lifeforms else {}
        next_i = len(self.lifeforms)
        self.items = {i+next_i: item for i, item in enumerate(items)} if items else {}
        next_i = len(self.items) + len(self.lifeforms)
        self.links = {i+next_i: link for i, link in enumerate(links)} if links else {}

    def remove_gameobject_by_id(self, id):
        for k, lifeform in self.lifeforms.items():
            if lifeform.id == id:
                del self.lifeforms[k]


class GameObject(object):
    def __init__(self, id, name='unnamed_gameobject', **kwargs):
        self.id = id
        self.name = name
        self.destroyed = False

        # Update all attributes with kwargs
        self.__dict__.update(kwargs)

        # If no name is given, give default name
        if 'name' not in self.__dict__.keys():
            self.name = 'unnamed'


class LifeForm(GameObject):
    def __init__(self, id, name='unnamed_lifeform', stats=None, inventory=None, **kwargs):
        super(LifeForm, self).__init__(id=id, name=name, **kwargs)
        if not stats:
            self.stats = Stats()
        else:
            self.stats = stats
        if not inventory:
            self.inventory = Inventory()
        else:
            self.inventory = inventory


class Inventory(object):
    def __init__(self, max_slots=8):
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

    def drop_item(self, id):
        # Confirm item is in inventory
        # Confirm item is not equipped
        # Drop item from inventory (replace with None) | later put on ground?
        pass

    def trade_item(self, item_id, target_id):
        pass

    def item_in_inventory(self, id):
        return get_object_by_id(id) in self.slots

    def is_equipped(self, id):
        item_slot = get_object_by_id(id).equippable_slot
        if item_slot:
            return self.equip_slots[item_slot] == get_object_by_id(id)
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

    def use_item(self):
        # Check if item has 'OnUse'
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
    def __init__(self, id, name='unnamed_generic_item', description='', equippable_slot=None):
        super(ItemGeneric, self).__init__(id=id)
        self.name = name
        self.description = description
        self.equippable_slot = equippable_slot
        self.anchored = False


class ItemWeapon(ItemGeneric):
    def __init__(self, id, name='unnamed_weapon', item_stats=None, description='', equippable_slot=None):
        super(ItemWeapon, self).__init__(id=id, name=name, description=description, equippable_slot=equippable_slot)
        self.stats = item_stats


class ItemIngredient(ItemGeneric):
    def __init__(self, id, name='unnamed_ingredient', item_stats=None, description='', equippable_slot=None):
        super(ItemIngredient, self).__init__(id=id, name=name, description=description, equippable_slot=equippable_slot)
        self.stats = item_stats


class ItemApparel(ItemGeneric):
    def __init__(self, id, name='unnamed_apparel', item_stats=None, description='', equippable_slot=None):
        super(ItemApparel, self).__init__(id=id, name=name, description=description, equippable_slot=equippable_slot)
        self.stats = item_stats


class ItemPotion(ItemGeneric):
    def __init__(self, id, name='unnamed_potion', item_stats=None, description='', equippable_slot=None):
        super(ItemPotion, self).__init__(id=id, name=name, description=description, equippable_slot=equippable_slot)
        self.stats = item_stats


class ItemMisc(ItemGeneric):
    def __init__(self, id, name='unnamed_misc', item_stats=None, description='', equippable_slot=None):
        super(ItemMisc, self).__init__(id=id, name=name, description=description, equippable_slot=equippable_slot)
        self.stats = item_stats


class ItemProp(ItemGeneric):
    def __init__(self, id, name='unnamed_misc', item_stats=None, description='', equippable_slot=None):
        super(ItemProp, self).__init__(id=id, name=name, description=description, equippable_slot=equippable_slot)
        self.stats = item_stats
        self.anchored = True
