# Life form classes
import entities
import stats as sts


class Lifeform(entities.Entity):
    def __init__(self, name='unnamed_lifeform', stats=sts.Stats(), x=0, y=0, solid=True):
        """
        Lifeform is composed of:
        .stats = A Stat object which contains the stats (HP, MP, etc) for the lifeform
        .q = LifeformQuery libary of queries.

        :param name: name of the lifeform
        :param stats: a stats object which holds stat objects
        :param x: x-coordinate in 2d space
        :param y: y-coordinate in 2d space
        :param solid: has collisions if True
        """
        super(Lifeform, self).__init__(name=name, x=x, y=y, solid=solid)
        self.stats = stats
        self.q = LifeformQuery(self)

        # Dynamically generate all stat changing methods
        for stat_class in self.stats.stat_list:
            method_name = 'set_{0}'.format(stat_class.stat_name)

            # Create method (for each stat) that returns sets its value
            def set_method(value=0, set_type='current', attr_to_set=stat_class.stat_name):
                """
                This method is dynamically generated for each stat that the lifeform has.
                This method can be accessed by: self.<set_STATNAME(value, ...optional args...)>

                :param value: value to set stat to
                :param set_type: query types include 'current', 'max', 'min'
                :param attr_to_query:
                :return:
                """
                stat_to_change = getattr(self.stats, attr_to_set)
                stat_attribute_to_change = 'stat_{0}'.format(set_type)
                assert isinstance(value, int), 'Should be integer'
                assert isinstance(set_type, str), 'Should be string, like "HP" or "MP"'
                assert hasattr(stat_to_change, stat_attribute_to_change), 'Cannot change attribute that does not exist'

                # If specific method exists to change this specific stat, use that, otherwise change directly
                if hasattr(self, '_set_{0}_{1}'.format(set_type, attr_to_set)):
                    return getattr(self, '_set_{0}_{1}'.format(set_type, attr_to_set))(value)
                else:
                    setattr(stat_to_change, stat_attribute_to_change, value)

            setattr(self, method_name, set_method)

    def _set_current_HP(self, value):
        """
        Example of method which overwrides dynamically generated method
        :param value:
        :return:
        """
        print('YOU DID IT! you passed in {0}'.format(value))


# Query Class
class LifeformQuery(object):
    """
    Runs queries on Lifeform object and Stats object

    __init__ will dynamically generate methods for querying stats
        example use:
            skeleton = Lifeform()
            # return skeleton's current HP
            skeleton.q.HP()
            # return skeleton's max HP
            skeleton.q.HP('max')

    LifeformQuery is also a Library of many other queries:
        is_alive()
        is_dead()
    """
    def __init__(self, lifeform_object):
        """
        :param lifeform_object:
        :param stats_object:
        """
        self.lifeform = lifeform_object
        self.stats = self.lifeform.stats

        # Dynamically generate all stat queries
        for stat_class in self.stats.stat_list:
            method_name = '{0}'.format(stat_class.stat_name)

            # Create method (for each stat) that returns its current value
            def query_method(query_type='current', attr_to_query=stat_class.stat_name):
                """
                This method is dynamically generated for each stat that the lifeform has.
                This method can be accessed by: self.<STAT_NAME()>

                :param query_type: query types include 'current', 'max', 'min'
                :param attr_to_query:
                :return:
                """
                assert isinstance(query_type, str)
                stat_obj = getattr(self.stats, attr_to_query)
                if query_type.lower() == 'current':
                    return stat_obj.stat_current
                elif query_type.lower() == 'max' or query_type == 'maximum':
                    return stat_obj.stat_max
                elif query_type.lower() == 'min' or query_type == 'minimum':
                    return stat_obj.stat_min
                else:
                    return None

            setattr(self, method_name, query_method)

    def is_alive(self):
        return self.HP() > 0

    def is_dead(self):
        return self.HP() <= 0

    def is_out_of_MP(self):
        return self.MP() <= 0

    def is_full_HP(self):
        return self.HP() == self.HP('max')

    def is_injured(self):
        return self.HP() < self.HP('max')

    def is_above_max_HP(self):
        return self.HP() > self.HP('max')



        #
        # def get_distance(entity1, entity2, distance):
        #     assert isinstance(entity1, Entity) and isinstance(entity2, Entity), 'Expects two Entity objects and a distance'
        #     return vc.vec_distance(entity1.x, entity1.y, entity2.x, entity2.y)

# Task Functions

def change_stat(lifeform, stat, value):
    """
    Changes the current_value of an Lifeform.stats.stat.  This is the only method that should be directly called
    to change an Lifeform's stat. Do not change a Lifeform's stat directly.
    """
    return entity.change_stat(stat, value)
