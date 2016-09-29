#This program seeks to aid in developing a battle engine by testing the effectiveness of stats and equipment
#Use the battle_test function to iterate over thousands of battles between different characters to see
#Which stats/equipment result in a disproportionate amount of victories.

#The Program will then attempt to balance the selected stat until all 4 battlers have a similiar amount
#of victories.

#1) Fight about 4000 battles, if character loses, increase specified stat by an increment, if wins, reduce stat by increment
#2) After 4000 battles, fight 1000 battles with new stats. See results.

import collections
import random
import logging
logging.basicConfig(filename='combat.log', filemode='w', level=logging.INFO)
#More Randomness
sys_random = random.SystemRandom()

class Item(object):
    pass

class Arena(object):
    lifeforms = []

class Player(object):
    def __init__(self, alive=True, **kwargs):
        self.stats = kwargs
        self.alive = alive
        # Assign player name and remove from stats
        if 'Name' in self.stats:
            self.name = kwargs['Name']
            del self.stats['Name']
        if 'name' in self.stats:
            self.name = kwargs['name']
            del self.stats['name']

    def print_character_sheet(self):
        print('CHARACTER SHEET:')
        print('Name: {}'.format(self.name))
        for items in self.stats:
            if items != 'Name':
                value = self.stats[items]
                print('{0}: {1}'.format(items, value))

    def attack(self, target, **kwargs):
        if target.stat_check('STA') and self.stat_check('STR'):
            #calculate damage
            damage = self.stats['STR']
            if self.critical_hit():
                damage *= 2
            defense = target.stats['STA']
            final_damage = damage - defense
            #display damage
            logging.info('{0} attacks {1} for {2} damage.'.format(self.name, target.name, final_damage))
            #apply damage
            self.do_damage(target, final_damage)

    def critical_hit(self):
        if self.stat_check('CRT'):
            crit_chance = self.stats['CRT']
            if random.randint(0, 100) < crit_chance:
                crit = True
            else:
                crit = False
        else:
            crit = False
        return crit

    def do_damage(self, target, final_damage):
        target.stats['HP'] -= final_damage
        if target.stats['HP'] <= 0:
            logging.info('{0} has slain {1}'.format(self.name, target.name))
            target.die()
        else:
            logging.info('{0} has {1} HP remaining.'.format(target.name, target.stats['HP']))

    def die(self):
        self.alive = False

    def stat_check(self, *args):
        for item in args:
            if item in self.stats:
                passed = True
            else:
                logging.info('Character has no {0} stat'.format(item))
                passed = False
                break
        #Check if dead or not
        if not self.alive:
            passed = False
            logging.info('The dead cannot fight...')
        return passed


def input_create_player():
    """
    Creates a Player object with whatever stats you can dream of.
    """
    stats = {}
    stats['Name'] = str(raw_input('Player name: '))
    amount = int(input('How many stats? '))
    for i in range(0, amount):
        stat_name = raw_input('Stat name: ')
        stat_value = raw_input('Stat value: ')
        stats[stat_name] = stat_value
    this_player = Player(**stats)
    return this_player


def battle(*args):
    #TODO: Finish combat log to report battle statistics
    combatlog = {}
    if not args:
        raise Exception('No combatants selected')
    if len(args) == 1:
        raise Exception('Requires at least two combatants')

    combatants = sorted(args, key=lambda combatant: combatant.stats['SPD'], reverse=True)

    #Iterate through turns:
    while len(combatants) > 1:
        for fighter in combatants:
            if not fighter.alive:
                combatants.remove(fighter)
            else:
                #TODO: Choose move from move list
                #TODO: Determine if move should be used on self or target
                #Choose Target, make sure not self
                target = fighter
                while target == fighter:
                    target = sys_random.choice(combatants)
                fighter.attack(target)
                #Use move
    try:
        logging.info('{0} stands as the victor!'.format(combatants[0].name))
        victor = combatants[0].name
    except NameError:
        logging.info('Everyone killed each other!')
        victor = 'Nobody'
    return victor, combatlog


#Test to see if Erod can lose

#TODO: Use Machine learning to balance stats

#TODO: Things to Log:
#Kill Counter, Victories, Damage Counter (Average Damage Per Fight), Critical Hits
def battle_test(amount_of_battles):
    scoreboard = {'Dirk' : 0, 'Slin' : 0, 'Hawk': 0, 'Erod': 0}
    for i in range(amount_of_battles):
        a = Player(Name='Dirk', HP=115, STR=10, STA=4, SPD=6, CRT=10)
        b = Player(Name='Slin', HP=110, STR=10, STA=3, SPD=9, CRT=35)
        c = Player(Name='Hawk', HP=120, STR=9, STA=4, SPD=8, CRT=7)
        d = Player(Name='Erod', HP=150, STR=6, STA=5, SPD=4, CRT=4)
        victor, combatlog = battle(a,b,c,d)
        scoreboard[victor] += 1
    print('Victories over {0} battles:'.format(amount_of_battles))
    logging.critical('Victories over {0} battles:'.format(amount_of_battles))
    #Print Scoreboard, sort by most wins
    #TODO: Sort by most wins
    for key, value in scoreboard.items():
        print(key, value)
        logging.critical('{0} : {1}'.format(key, value))


battle_test(1000)
#Conclusion: Speed is horribly underpowered.
