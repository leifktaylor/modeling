# Monty Hall Problem Test
# Author: Leif Taylor
# Date: September 2016
# ***********************************
import argparse
import random
import logging
logging.basicConfig(filename='goatdoor.log', filemode='w', level=logging.INFO)
import __future__
from itertools import cycle

class Doors(object):
    """
    There are x amount of doors.
    One door will always have a car, the rest will have goats.

    """
    def __init__(self, number_of_doors=3):
        self.doors = []
        self.car_door = random.randint(0, number_of_doors-1)
        for i in range(number_of_doors):
            if i == self.car_door:
                self.doors.append('car')
            else:
                self.doors.append('goat')


def play_game(number_of_doors=3, alwayschange=True):
    """
    The player will choose a door, hoping for a car.  The host will choose a door.
    The host must always choose a goat door.
    The player is then asked, if he wants to see what is behind his initial choice,
    or change his choice to another door.

    The player may have one of two behaviors:
    Always change door after host has chosen
    Always stick to his original choice.

    :param alwayschange: boolean, True or False.
    :param number_of_doors: number of doors to choose from
    :return:
    """
    if number_of_doors < 3:
        logging.info('Must have at least 3 doors, changing input to 3')
        number_of_doors = 3
    a = Doors(number_of_doors)
    doors = a.doors
    # Player randomly chooses door
    pl_random_door = random.randint(0, len(doors)-1)
    player_choice = doors.pop(pl_random_door)
    logging.info('Player chooses door {0} with a {1}'.format(pl_random_door, player_choice))
    # Host must choose door with goat
    while True:
        random_index = random.randint(0, len(doors)-1)
        host_choice = doors[random_index]
        if host_choice == 'goat':
            logging.info('Host chooses a {0}'.format(host_choice))
            doors.pop(random_index)
            break
    #Only untouched doors remain
    if alwayschange:
        logging.info('Player must change door')
        # Fix for more than 3 doors
        if len(doors) > 1:
            logging.info('More than 3 initial doors')
            new_choice = doors[random.randint(0, len(doors)-1)]
            logging.info('Player changes choice and gets a {0}'.format(new_choice))
            return new_choice
        else:
            logging.info('Player changes choice and gets a {0}'.format(doors[0]))
            return doors[0]
    else:
        logging.info('Player goes with original choice')
        return player_choice

def run_analysis(number_of_iterations, number_of_doors=3, **kwargs):
    """
    Runs the goat door test x times and logging.infos results.

    :param number_of_iterations: Number of times to run the test
    :param number_of_doors: How many doors to choose from
    :param alwayschange: (KV argument) Always change door after host chooses his
    :return:
    """
    if 'alwayschange' in kwargs:
        alwayschange = kwargs['alwayschange']
    else:
        alwayschange = True

    logging.info('---------------------------------------------')
    if alwayschange:
        logging.info('TEST 1: Player always changes choice')
        print('TEST 1: Player always changes choice')
    else:
        logging.info('TEST 2: Player always stays on first choice')
        print('TEST 2: Player always stays on first choice')
    logging.info('---------------------------------------------')

    scoreboard = {'Wins': 0, 'Losses': 0}

    for i in range(number_of_iterations):
        logging.info('-----Try {0}-----'.format(i))
        result = play_game(number_of_doors, alwayschange)
        if result == 'car':
            logging.info('WIN! Ride home in new car!')
            scoreboard['Wins'] += 1
        else:
            logging.info('LOSS! Ride home on a goat!')
            scoreboard['Losses'] += 1
    logging.info(scoreboard)
    print('SCOREBOARD:')
    print(scoreboard)
    print('----------------')

def parseArguments():
    """
    Parses arguments given at commandline.
    :return:
    """
    parser = argparse.ArgumentParser()
    #Optional Ar
    parser.add_argument("-n", "--iterations", help="Number of iterations.", type=int, default=100)
    parser.add_argument("-d", "--doors", help="Number of doors.", type=int, default=3)
    args = parser.parse_args()
    return args

if __name__ == '__main__':
    # Get arguments
    args = parseArguments()
    iterations = args.iterations
    doors = args.doors

    # Run and Log Test
    print('*')*60
    run_analysis(iterations, doors, alwayschange=True)
    run_analysis(iterations, doors, alwayschange=False)
    print('-------------------------')
    print('Log Created: goatdoor.log')
    print('-------------------------')
    print('*')*60