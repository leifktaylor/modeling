import random

class Indiv(object):
    def __init__(self, name = '',  num = float(0)):
        self.name = ''
        self.num = float(0)

def create_pop(amount):
    population = []
    for i in range(0, amount):
        name = i
        num = round(random.uniform(0, 100), 2)
        print(name, num)
        population.append(Indiv(name, num))
    return population


def make_choice(population):
    for indiv in population:
        print(indiv.name)
        print(indiv.num)
    max = float(0)
    for Indiv in population:
        print(Indiv.num)
        max += Indiv.num
        print(max)

def test():
    amount = 10
    a = create_pop(amount)
    make_choice(a)
