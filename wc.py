import random
import sys


def easy_run():
    choice0, choice1, choice2, bestof = input_params()
    run(choice0, choice1, choice2, bestof)


def input_params():
    print('Choose a series of three coin flips, i.e. heads, heads, tails.  The computer will try to choose better than you such that its pattern will occur first in a set of coin flips.')
    choice0 = int(input('First choice; Heads = 1, Tails = 0: '))
    choice1 = int(input('Second choice; Heads = 1, Tails = 0: '))
    choice2 = int(input('Third choie; Heads = 1, Tails = 0: '))
    bestof = int(input('Best out of how many rounds? '))

    return choice0, choice1, choice2, bestof


def run(choice0, choice1, choice2, bestof):
    # Computer choice based on player choice
    cc0 = 0
    cc1 = choice0
    cc2 = choice1
    if choice1 == 0:
        cc0 = 1
    won = int(bestof / 2) + 1
    player_count = 0
    computer_count = 0
    stop = 1
    s = 0
    f = []

    print('Players choice 1: {0}, 2: {1}, 3: {2} || Computer choice 1: {3}, 2: {4} 3: {5}'.format(choice0, choice1, choice2,
                                                                                            cc0, cc1, cc2))

    for x in range(0, bestof):
        if computer_count == won:
            print('You have lost to the computer you stupid idiot!')
            break
        if player_count == won:
            print('You beat the computer you lucky duck!')
            break
        for y in range(0, stop):
            s = int(random.randint(0, 1))
            f.append(s)
            print(f)
            if stop >= 2:
                if f[y - 2] == choice0 and f[y - 1] == choice1 and f[y] == choice2:
                    player_count += 1
                    print('Player has won a round')
##                    f.clear()
##                    stop = 1
                    break
                if f[y - 2] == cc0 and f[y - 1] == cc1 and f[y] == cc2:
                    computer_count += 1
                    print('Computer has won a round')
##                    f.clear()
##                    stop = 1
                    break
                else:
                    stop += 1
            stop += 1


if __name__ == '__main__':
    run(int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]))
