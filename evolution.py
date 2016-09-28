import random


class Individual(object):
    def __init__(self, species='', sex='', survivability=0, reproductive_likelihood=0, phenotype=[], genotype=[]):
        self.species = species
        self.sex = sex
        self.survivability = survivability
        self.reproductive_likelihood = reproductive_likelihood
        self.phenotype = phenotype
        self.genotype = genotype
        self.alive = True


def create_population(amount):
    population = []
    species_index = {'test_bird': {'species': 'test_bird'}}
<<<<<<< HEAD
    sex_list = ('male', 'female')
    for i in range(0, amount):
        species = 'test_bird'
        sex = random.choice(sex_list)
        survivability = random.randint(0, 100)*.01
#        print(survivability)
        reproductive_likelihood = random.randint(0 , 100)*.01
#        print(reproductive_likelihood)
        population.append(Individual(species, sex, survivability, reproductive_likelihood))
    return(population)

def create_adult_population(population):
    adult_population = []
    for individual in population:
        if individualndividual.survivablity < 0.5:
            individual.alive = False
    return(adult_population)

def create_next_generation(adult_population):
    next_generation = []
    selection_mode = female
    for individual in adult_population:
        if individual.alive = True:
            if selection_mode = female:
                
=======


>>>>>>> 08745b030bf873806a6680b73b5344f1a3ca9ec9
