import random
import names

# Lottery test.  Will you win with x iterations?

class Sucker(object):
    """
    A sucker has a bank account.  Playing the lottery costs x dollars.
    They play the lottery every day.
    """
    def __init__(self, bank_account, winner=False):
        self.bank_account = bank_account
        self.winner = winner
        self.name = ''

    def play_lottery(self, numbers, ticket_cost=1.0):
        """
        Play the lottery with as many numbers as you want.
        Just input a string of numbers, if you input a string of 20, numbers, the lottery will
        be a 20 number lottery.

        :param numbers: Your numbers
        :return:
        """
        choice = [int(x) for x in str(numbers)]
        length = len(choice)

        set = []
        self.bank_account -= ticket_cost
        for place in range(0, length):
            set.append(random.randint(0, 9))
        if set == choice:
            self.winner = True
        # if set != choice:
            #print('You lost')


class MoneyCity(object):
    """
    Money city contains suckers who play the lottery

    """
    def __init__(self, players=100, payout_pot=1000000.0, taxes=.5):
        self.players = players
        self.taxes = taxes
        self.payout_pot = payout_pot
        # Populate city with list of 'Suckers'
        self.sucker_list = []
        for i in range(0, self.players):
            self.sucker_list.append(Sucker(100000.0))

    def city_day(self):
        winner_list = []
        for sucker in self.sucker_list:
            # TODO: Fix random number generation
            # Randomly Choose Loterry Numbers
            choice = [int(x) for x in str(numbers)]
            length = len(choice)
            numbers = random.randint(100000, 999999)
            sucker.play_lottery(numbers)
            if sucker.winner:
                winner_list.append(sucker)
                sucker.winner = False
        if len(winner_list) > 0:
            individual_payout = (self.payout_pot * self.taxes) / len(winner_list)
            for winner in winner_list:
                winner.bank_account += individual_payout
            print('The day has ended, {0} suckers have won the lottery'.format(len(winner_list)))
            print('Each recieved a payout of {0} dollars'.format(individual_payout))
        else:
            print('NOBODY WON TODAY!')


def run_simulation(players, iterations=20):
    city = MoneyCity(players)
    for i in range(0, iterations):
        city.city_day()




