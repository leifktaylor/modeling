# Entities are objects that exist in the world, they can be blocks, lifeforms, trees.
# All entities have co-ordinates, and collision settings.
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
