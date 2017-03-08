from template_parser import TemplateParser
from functions.game_math import point_distance

TILE_SIZE = 8


class AIController(object):
    """ Requires data initialized from AI template to initialize """
    def __init__(self, lifeform):
        self.lifeform = lifeform
        self.mode = 'idle'
        self.state = None
        # TODO: Should probably be False by default, and enabled if players are in room
        self.running = True

        tp = TemplateParser()
        self.data = tp.load_data(lifeform.ai)

        self.base_sight = self.lifeform.sight

        self.target = None
        self.target_coords = None

        self.action_timer = None
        self.attack_timer = self.lifeform.attack_time

        self.cancel_time = 400
        self.cancel_timer = self.cancel_time

        # Set condition timers

        # TODO: Compatibility list:
        #   Timers
        #   Status
        #   Random

    def run(self, dt):
        if self.state:
            self.tick(dt)
            self.state()
            self.cancel_check()
        else:
            print('run: Performing combat check')
            check = self.combat_check()
            if check:
                self.set_mode('combat')
                self.state = check
            else:
                print('run: Performing idle check')
                self.set_mode('idle')
                self.state = self.idle_check()

    def tick(self, dt):
        self.action_timer -= dt / 50.
        self.cancel_timer -= dt / 50.
        self.attack_timer -= dt / 50.

    def cancel_check(self):
        if self.cancel_timer < 0:
            print('cancel_check: Timer reached 0. Cancelling current state')
            self.cancel_timer = self.cancel_time
            self.state = None

    def set_mode(self, mode):
        if mode == 'idle':
            print('set_mode: "idle"')
            self.mode = 'idle'
            self.lifeform.sight = self.base_sight
        else:
            print('set_mode: "combat"')
            self.mode = 'combat'
            self.lifeform.sight = self.base_sight * 2

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
            print('combat_check: Starting check for gambit: {0}'.format(gambit))
            if self.check_condition(gambit['precondition'], self.lifeform):
                print('combat_check: Precondition met, checking for target')
                if gambit['target'] and gambit['target'][0] is not 'self':
                    # If target provided in gambits, see if there is an eligible target
                    target = self.find_target(gambit['target'])
                    if target:
                        print('combat_check: Target found: {0}'.format(target))
                        if self.check_condition(gambit['condition'], target):
                            print('combat_check: Target condition met')
                            action = gambit['action'][0]
                            args = gambit['action'][1:]
                            return self.perform_action(action, args, target)
                    else:
                        print('combat_check: Target not found, moving to next gambit')
                else:
                    # If no target given, assume we're referring to self
                    print('combat_check: No target given, assuming self')
                    target = self.lifeform
                    action = gambit['action'][0]
                    args = gambit['action'][1:]
                    return self.perform_action(action, args, target)
        print('combat_check: No gambits met their conditions, returning None')
        return None

    def find_target(self, gambit_target):
        """
        Target types allowed in gambit_target:
            ['nearest', '<enemy/ally/player>']
            ['farthest', '<enemy/ally/player>']
            ['any', '<enemy/ally/player>']
        :param gambit_target: list with valid items, see above
        :return: lifeform gameobject
        """
        condition = gambit_target[0]
        target_type = gambit_target[1]
        return getattr(self.lifeform, '{0}_{1}'.format(condition, target_type))

    def perform_action(self, action, args=None, target=None):
        print('perform_action: Entering state: {0}'.format(action))
        if action == 'attack':
            self.target = target
            self.action_timer = self.lifeform.move_time
            self.attack_timer = self.lifeform.attack_time
            return self.attack
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
            self.target_coords = args
            return self.move
        if action == 'say':
            # Speak dialogue to target, if no target, to general chat
            pass
        if action == 'wait':
            # Wait until timeout
            self.action_timer = args * 60
            return self.wait
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
                print('{0}: {1}'.format(eval(expression), expression))
                return eval(expression)
            else:
                # If any other stat, use flat value
                expression = '{0}{1}{2}'.format(stat_value, oper, value)
                print('{0}: {1}'.format(eval(expression), expression))
                return eval(expression)

        if kw == 'status':
            pass
        if kw == 'random':
            pass
        if kw == 'timer':
            pass

    def idle_check(self):
        # Perform sequence of actions
        # TODO: Finish this
        # Look for target in range
        return self.perform_action('wait', 10)

    def attack(self):
        # Attack target if in range, otherwise move toward it
        if point_distance(self.lifeform.coords, self.target.coords) < (1.7 * TILE_SIZE):
            if self.attack_timer < 0:
                print('attack: Target in range, attacking')
                self.lifeform.attack(self.target.id)
                self.state = None
                return
        else:
            if self.action_timer < 0:
                print('attack: Target not in range, pathing towards target')
                self.action_timer = self.lifeform.move_time
                self.lifeform.move(self.target.coords)
                return

    def wait(self):
        if self.action_timer < 0:
            print('wait: waiting complete')
            self.state = None




