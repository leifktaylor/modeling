from template_parser import TemplateParser
from functions.game_math import point_distance


class AIController(object):
    """ Requires data initialized from AI template to initialize """
    def __init__(self, lifeform):
        self.lifeform = lifeform
        self.state = 'idle'
        self.running = True

        tp = TemplateParser()
        self.data = tp.load_data(lifeform.ai)
        self._range = 100

        self.target = None
        self.target_coords = None

        # Set condition timers

        # TODO: Compatibility list:
        #   Timers
        #   Status
        #   Random

    @property
    def range(self):
        if self.state == 'combat':
            return self._range * 4
        else:
            return self._range

    def run(self, dt):
        # TODO: Control everything in game loop here
        pass

    def set_state(self, state, **kwargs):
        if state == 'stick':
            self.target = kwargs['target']
            # TODO : Here's where you finished off
        if state == 'idle':
            self.target = None
            self.target_coords = None
        if state == 'combat':
            pass
        self.state = state

    def combat_check(self):
        """
        For each possible combat choice, see if we meet the conditions to act, if we do,
        perform the action and return, otherwise keep iterating through our choices.  If
        we reach the end of our choices, and no conditions were met,
        return to idle (non-combat) state

        A gambit consists of:
            a 'precondition'
            a 'action'
            a 'target'
            a 'condition'
        """
        for gambit in self.data['combat']:
            if self.check_condition(gambit['precondition'], self.lifeform):
                if gambit['target']:
                    # If target provided in gambits, see if there is an eligible target
                    target = self.find_target(gambit['target'])
                    if target:
                        if self.check_condition(gambit['condition'], target):
                            action = gambit['action'][0]
                            args = gambit['action'][1:]
                            return self.perform_action(action, args, target)
                else:
                    # If no target given, assume we're referring to self
                    target = self.lifeform
                    action = gambit['action'][0]
                    args = gambit['action'][1:]
                    return self.perform_action(action, args, target)
        return None

    def find_target(self):
        # TODO: This is required, finish this
        return 'WIP'

    def perform_action(self, action, args=None, target=None):
        if action == 'attack':
            # Enter AI attacking state (stick + attack) [will end when an attack is executed] / timeout optional
            self.set_state('stick', target=target, attack=True, timeout=300)
        if action == 'cast':
            # Enter AI casting state (stick + cast) [will end when a cast is executed] / timeout optional
            pass
        if action == 'use':
            # Use item by uniquename, if it is in inventory (Do not raise error)
            pass
        if action == 'flee':
            # Flee from combat until timeout
            pass
        if action == 'move':
            # Move to target co-ordinates
            pass
        if action == 'say':
            # Speak dialogue to target, if no target, to general chat
            pass
        if action == 'wait':
            # Wait until timeout
            pass
        if action == 'wander':
            # Wander randomly until timeout
            pass

    def check_condition(self, precondition, target=None):
        """
        :param target: lifeform gameobject
        :param precondition: ['stat', 'N>X'], ['random', int], ['timer', int], ['status', 'uniquename']
        :return: True / False
        """
        # If None is passed in, return True (essentially passing the precondition)
        if not precondition:
            return True
        kw = precondition[0]
        arg = precondition[1]
        if kw == 'stat':
            # parse arg string like 'HP>10' or 'MP<20' (the ints refer to percentages)
            if '<' in arg:
                stat = arg.split('<')[0]
                oper = '<'
                value = arg.split('<')[1]
            elif '>' in arg:
                stat = arg.split('>')[0]
                oper = '>'
                value = arg.split('>')[1]
            else:
                raise RuntimeError('Missing operator > or < in expression')
            stat_value = getattr(target, stat)
            if stat in ['HP', 'MP']:
                # If we're comparing HP or MP, compare based on percentage
                max_stat_value = getattr(target, 'MAX{0}'.format(stat))
                percent = float(max_stat_value) * (.01 * int(value))
                expression = '{0}{1}{2}'.format(stat_value, oper, percent)
                print(expression)
                return eval(expression)
            else:
                # If any other stat, use flat value
                expression = '{0}{1}{2}'.format(stat_value, oper, value)
                print(expression)
                return eval(expression)

        if kw == 'status':
            pass
        if kw == 'random':
            pass
        if kw == 'timer':
            pass

    def idle_check(self):
        # Perform sequence of actions

        # Look for target in range
        pass

    def stick(self, dt, target, attack=False, timeout=None):
        """ Will stick to target, if autoattack is enabled, will return from function when attack is attempted """
        if attack:
            if point_distance(self.lifeform.coords, self.target.coords) < self.lifeform.weapon_range:
                return self.lifeform.attack(target.id)
        if timeout:
            self.stick_timer -= dt / 100.
            if self.stick_timer < 0:
                return None
        return 'continue'
