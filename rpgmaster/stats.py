class Stats(object):
    """
    This class can be composited with a Lifeform, it holds instances of the Stat class.
    """
    def __init__(self, stat_list=''):
        # Default stats if a stat list isn't provided
        if not stat_list:
            self.stat_list = [StatSTR(), StatMP(), StatHP(), StatDEF(), StatATK(), StatSPD(), StatMIND()]
        else:
            self.stat_list = stat_list
        # Custom stat list is provided
        for stat in stat_list:
            exec('self.{0} = {1}'.format(stat.stat_name, stat))

    def stat_dict(self):
        """
        Returns a dictionary of statnames and their current and max values
        :return: {'HP': (current_value, max value), 'MP': (current_value, max_value), ... etc}
        """
        return {stat.stat_name: (stat.stat_current, stat.stat_max) for stat in self.stat_list}


class Stat(object):
    def __init__(self, stat_name='unnamed_stat', stat_min=0, stat_max=255, stat_current=1):
        self.stat_name = stat_name
        self.stat_min = stat_min
        self.stat_max = stat_max
        self.stat_current = stat_current


class StatSTR(Stat):
    def __init__(self):
        super(StatSTR, self).__init__(stat_name='STR', stat_min=1, stat_max=255, stat_current=1)
        self.stat_desc = ['Governs physical damage, defense and health',
                          'Warriors of ancient times were known for their legendary strength']


class StatMP(Stat):
    def __init__(self):
        super(StatMP, self).__init__(stat_name='MP', stat_min=0, stat_max=9999, stat_current=1)
        self.stat_desc = ['Resource used for casting of magicks',
                          'Mana can be restored through deep meditation, or by more nefarious means']


class StatHP(Stat):
    def __init__(self):
        super(StatHP, self).__init__(stat_name='HP', stat_min=0, stat_max=9999, stat_current=1)
        self.stat_desc = ['Measure of vitality. If reduced to 0, death will follow',
                          'The ancient turtle of Buleria was said to have infinite vitality']


class StatDEF(Stat):
    def __init__(self):
        super(StatDEF, self).__init__(stat_name='DEF', stat_min=1, stat_max=255, stat_current=1)
        self.stat_desc = ['Measure of defense against all attack',
                          'Will reduce incoming damage from all attacks']


class StatATK(Stat):
    def __init__(self):
        super(StatATK, self).__init__(stat_name='ATK', stat_min=1, stat_max=255, stat_current=1)
        self.stat_desc = ['Measure of attack damage from equipped weapon',
                          'Attack damage can scale from many factors, mainly STR']


class StatSPD(Stat):
    def __init__(self):
        super(StatSPD, self).__init__(stat_name='SPD', stat_min=1, stat_max=100, stat_current=1)
        self.stat_desc = ['Measures movement speed and attack speed',
                          'The fastest runner in history was Hisu of the city of Mist']


class StatMIND(Stat):
    def __init__(self):
        super(StatMIND, self).__init__(stat_name='MIND', stat_min=1, stat_max=255, stat_current=1)
        self.stat_desc = ['Governs the damage of magical attacks',
                          'The greatest mind in the world was Amerith of Telaria']