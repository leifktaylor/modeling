

import random


class Individual(object):
    def __init__(self, species='', sex='', survivability = 0, reproductive_likelihood = 0, phenotype = [], genotype = []):
        self.species = species
        self.sex = sex
        self.survivability = survivability
        self.reproductive_likelihood = reproductive_likelihood
        self.phenotype = phenotype
        self.genotype = genotype
        self.alive = True
        self.hadsex = 0


def create_population(amount):
    population = []
    species_index = {'test_bird': {'species': 'test_bird'}}
    sex_list = ('male', 'female')
    for i in range(0, amount):
        species = 'test_bird'
        sex = random.choice(sex_list)
        survivability = round(random.uniform(0, 1), 2)
#        print(survivability)
        reproductive_likelihood = round(random.uniform(0, 1), 2)
#        print(reproductive_likelihood)
        population.append(Individual(species, sex, survivability, reproductive_likelihood))
    return population


def create_adult_population(population):
    adult_population = []
    death_rate = float(.5)
    death_count = int(len(population)*death_rate)
    max = float(0)
    pix = float(0)
    for individual in population:
        max += individual.survivability
        individual.surv_toprange = max
        individual.surv_botrange = max - individual.survivability
        print('Max: {0}, Top Range: {1}, Bot Range {2}'.format(max, individual.surv_toprange, individual.surv_botrange))
    for i in range(0, death_count):
        pix = round(random.uniform(0,max), 2)
        print(pix)
        print(i)
        for individual in population:
            if individual.surv_botrange < pix and pix < individual.surv_toprange:
                individual.alive = False
                print('ded')
    return population

def create_weighted_sex():
    max_s = float(0)
    for individual in population:
        if individual.alive:
            if selection_mode == female:
                if individual.sex = male:
                    max_s += individual.reproductive_likelihood
                    individual.sex_toprange = max_s
                    individual.sex_botrange = max_s - individual.reproductive_likelihood




def create_next_generation(population):
    next_generation = []
    selection_mode = female
    for individual in adult_population:
        if individual.alive == True:
            if selection_mode == female:
                while individual.sex == female:








def print_population_statistics(population):
    """
    Prints the species, sex, survability, reproductive_likelyhood and
    other stats of the members of a population.

    :param population: population list object
    :return:
    """
    for individual in population:
        print_individual_statistics(individual)
        if individual.alive:
            print('alive')


def print_individual_statistics(individual):
    """
    Prints the statistics of an individual.

    :param individual: Individual class object
    :return:
    """
    species = individual.species
    sex = individual.sex
    survivability = individual.survivability
    reproductive_likelihood = individual.reproductive_likelihood
    print('Species: {0} | Sex: {1} | Survivability {2} | Reproductive_Chance {3}'.format(species, sex, survivability, reproductive_likelihood))


def print_adult_population_statistics(adult_population):
    for individual in population:
        print_individual_statistics(individual)
        if individual.alive:
            print('Alive')

def test():
    a = create_population(20)
##    print_population_statistics(a)
    b = create_adult_population(a)
    print_population_statistics(b)
