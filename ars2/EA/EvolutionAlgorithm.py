import numpy as np

class EvolutionAlgorithm:

    def __init__(self, agent, population_size, bounds_left_wheel, bounds_right_wheel):
        population_size = 100
        l, r = initial_population(population_size, bounds_left_wheel, bounds_right_wheel)
        self.generation[0] = l
        self.generation[1] = r
        self.fitness = []


    def initial_population(self, population_size, bounds_left_wheel, bounds_right_wheel):
        # Uniformly choose elements on a given interval on bounded phenotype
        vl = np.random.uniform(bounds_left_wheel[0], bounds_left_wheel[1], size=population_size)
        vr = np.random.uniform(bounds_right_wheel[0], bounds_right_wheel[1], size=population_size)
        return vl, vr

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
            probability = value/fitness_sum
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
        # TODO: define p_m_char for the velocities
        # Randomly select the char to mutate
        # Mutation with probability p_m_char
        return None