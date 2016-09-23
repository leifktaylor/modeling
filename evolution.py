import random


class Individual(object):
    def __init__(self, species='', sex='', survival_fitness=0, reproductive_fitness=0, phenotype=[], genotype=[]):
        self.species = species
        self.sex = sex
        self.survival_fitness = survival_fitness
        self.reproductive_fitness = reproductive_fitness
        self.phenotype = phenotype
        self.genotype = genotype


def create_individuals(amount):
    species_index = {'test_bird': {'species': 'test_bird'}}


