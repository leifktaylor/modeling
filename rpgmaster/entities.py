# Entities are objects that exist in the world, they can be blocks, lifeforms, trees.
# All entities have co-ordinates, and collision settings.
import stats as sts
import spacial as vc


class Entity(object):
    def __init__(self, name='unnamed_entity', x=0, y=0, solid=True):
        self.name = name
        self.x = x
        self.y = y
        self.solid = solid

    def move(self, dir, amount):
        """
        Instantly moves entity a direction for the given amount of spaces

        Directions: {0: up, 1: upright, 2: right, 3: downright, 4: down, 5: downleft, 6: left, 7: upleft}
        :param dir: direction (0 through 7)
        :param amount: amount of co-ords to move in direction
        :return: (alters self.x and self.y directly)
        """
        directions = {0: (0, -1), 1: (1, -1), 2: (1, 0), 3: (1, 1),
                      4: (1, 0), 5: (-1, 1), 6: (-1, 0), 7: (-1, -1)}
        self.x += directions[dir][0] * amount
        self.y += directions[dir][1] * amount

    def point_distance(self, entity2):
        """
        Returns the distance in units between self and another entity.
        :param entity2: instance of Entity class, or a child class
        :return: distance in units
        """
        assert isinstance(entity2, Entity), 'Instances given must be Entity class'
        return vc.vec_distance(self.x, self.y, entity2.x, entity2.y)

    def point_direction(self, entity2):
        """
        Returns the direction in units between self and another entity.
        :param entity2: instance of Entity class, or a child class
        :return: direction in degrees
        """
        # TODO: Ask sam.. this isn't working
        assert isinstance(entity2, Entity), 'Instances given must be Entity class'
        return vc.vec_direction(self.x, self.y, entity2.x, entity2.y)


class Lifeform(Entity):
    def __init__(self, name='unnamed_lifeform', stats=sts.Stats(), x=0, y=0, solid=True):
        super(Lifeform, self).__init__(name=name, x=x, y=y, solid=solid)
        self.stats = stats

    def stat_current(self, stat):
        """
        Returns current value of stat

        Assumes stat has an uppercase name, e.g. STR, HP, MP
        :param stat:
        :return: integer value of stat
        """
        try:
            return eval('self.stats.{0}.stat_current'.format(stat))
        except AttributeError:
            raise RuntimeError('{0} has no {1} stat'.format(self.name, stat))

    def stat_min(self, stat):
        """
        Returns min value of stat

        Assumes stat has an uppercase name, e.g. STR, HP, MP
        :param stat:
        :return: integer value of stat
        """
        try:
            return eval('self.stats.{0}.stat_min'.format(stat))
        except AttributeError:
            raise RuntimeError('{0} has no {1} stat'.format(self.name, stat))

    def stat_max(self, stat):
        """
        Returns max value of stat

        Assumes stat has an uppercase name, e.g. STR, HP, MP
        :param stat:
        :return: integer value of stat
        """
        try:
            return eval('self.stats.{0}.stat_max'.format(stat))
        except AttributeError:
            raise RuntimeError('{0} has no {1} stat'.format(self.name, stat))

    def change_stat(self, stat, amount):
        if hasattr(self.stats, stat) and hasattr(self, '_change_{0}'.format(stat)):
            change_method = getattr(self, '_change_{0}'.format(stat))
            return change_method(amount)
        else:
            stat_to_change = getattr(self.stats, stat)
            stat_to_change.stat_current = amount


# Query Functions

def is_alive(lifeform):
    return lifeform.stat_current('HP') > 0

def is_dead(lifeform):
    return lifeform.stat_current('HP') < 1

def is_out_of_MP(lifeform):
    return lifeform.stat_current('MP') < 1

def has_enough_MP(lifeform, amount):
    return lifeform.stat_current('MP') >= amount

def has_enough_HP(lifeform, amount):
    return lifeform.stat_current('HP') >= amount

def has_enough_MIND(lifeform, amount):
    return lifeform.stat_current('MIND') >= amount

def has_enough_STR(lifeform, amount):
    return lifeform.stat_current('STR') >= amount

def has_stat(lifeform, stat):
    return hasattr(lifeform.stats, stat)

def get_distance(entity1, entity2, distance):
    assert isinstance(entity1, Entity) and isinstance(entity2, Entity), 'Expects two Entity objects and a distance'
    return vc.vec_distance(entity1.x, entity1.y, entity2.x, entity2.y)

# Task Functions

def change_stat(lifeform, stat, value):
    """
    Changes the current_value of an Lifeform.stats.stat.  This is the only method that should be directly called
    to change an Lifeform's stat. Do not change a Lifeform's stat directly.
    """
    return entity.change_stat(stat, value)
