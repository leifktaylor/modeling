import random

def run(amount):
    num = 0
    num2 = 0
    rand = 0
    correct = 0
    wrong = 0
    for i in range(0, amount):
        num = int(random.randint(0, 99))
        num2 = int(random.randint(0, 99))
##        rand = float(49.5)
        rand = int(random.randint(0, 99))
        if num < rand:
            if num2 > num:
                correct += 1
            else:
                wrong += 1
        if num > rand:
            if num2 < num:
                correct += 1
            else:
                wrong += 1
    print('Guess was correct: {0} | Guess was Wrong: {1}'.format(correct, wrong))

