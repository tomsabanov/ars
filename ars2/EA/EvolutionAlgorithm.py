import numpy as np


class EvolutionAlgorithm:

    def __init__(self, max_fitness_val, population_size, bounds_left_wheel, bounds_right_wheel):
        self.max_fitness_val = max_fitness_val
        self.best_fitness = 0
        population_size = 100
        self.current_generation = initial_population(population_size, bounds_left_wheel, bounds_right_wheel)
        self.generations = [].append(current_generation)
        self.generation_index = 0


    def initial_population(self, population_size, bounds_left_wheel, bounds_right_wheel):
        # Uniformly choose elements on a given interval on bounded phenotype
        vl = np.random.uniform(bounds_left_wheel[0], bounds_left_wheel[1], size=population_size)
        vr = np.random.uniform(bounds_right_wheel[0], bounds_right_wheel[1], size=population_size)
        individuals = []
        for i in range(population_size):
            individual = Individual(generation_index, vl[i], vr[i])
            individuals.append(individual)
        return individuals

    # Results come from how many collisions occurred and cleaned area
    def evaluation(self, results):
        # TODO: Fitness criteria: weight properly to make it collision-free & clean as much area as possible
        # Assign fitness value to an individual

        return None

    def selection(self):
        # Probabilities for each agent's speeds
        fitness_sum = sum(self.fitness_values)
        likelihood_selection = []
        for value in fitness_values:
            probability = value / fitness_sum
            likelihood_selection.append(probability)
        return likelihood_selection

    def reproduction(self):
        n_best = 10
        all_individuals = np.array(self.fitness)
        indices = (-all_individuals).argsort()[:n_best]
        best_individuals = list(itemgetter(*indices)(self.generation))
        ## TO DO
        # Choose individuals to cross-over
        # Choose individual for mutation
        # new_generation =
        self.generation
        return None

    # ind_1 = [vl1, vr1]
    # ind_2 = [vl2, vr2]
    # -> new individuals => [vl1, vr2] & [vl2, vr1]
    def cross_over(self, individual_1, individual_2):
        child_1 = [individual_1[0], individual_2[1]]
        child_2 = [individual_2[0], individual_1[1]]
        return child_1, child_2

    def mutation(self, individual):
        # Randomly select the char to mutate
        mutation_index = random.randint(0, len(individual.genotype))
        individual_genotype = individual.genotype

        # Mutate genotype
        individual_genotype[mutation_index] = np.random.uniform(bounds_left_wheel, bounds_right_wheel, size=1)
        new_individual = Individual(individual.generation + 1, individual_genotype[0], individual_genotype[1])
        return new_individual
