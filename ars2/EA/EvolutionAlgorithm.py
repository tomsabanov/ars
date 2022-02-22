import numpy as np
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.colors import LogNorm
from matplotlib import cm
import matplotlib.pyplot as plt
import math
import random as rnd
import numpy as np
import matplotlib.animation as animation
import random


def rosenbrock(*X):
    a = 0
    b = 1

    x = X[0]
    y = X[1]
    return (a-x)**2 + b*((y-x**2)**2)

def rastrigin(*X):
    A = 10
    result = A * len(X) + sum([(x ** 2 - A * np.cos(2 * math.pi * x)) for x in X])
    return result



class Function:
    def __init__(self, fnc, *X):
        self.call = fnc
        self.dim = len(X)
        self.X = X
        self.value = fnc(*X)

    def get_dimension_intervals(self):
        # Returns a list of tuples of specified intervals on which the function is defined
        # Interval is specified with (min,max)
        intervals = list()
        for x in self.X:
            intervals.append((min(map(min, x)), max(map(max, x))))
        return intervals

    def plot_function(self, show=True):
        self.fig = plt.figure()
        self.ax = Axes3D(self.fig, azim=-128, elev=43)

        # Sidenote: rastrigin looks better without lognorm
        # cmap jet for rastrigin, plasma for rosenbrock with lognorm
        self.ax.plot_surface(self.X[0], self.X[1], self.value, rstride=1, cstride=1, norm=LogNorm(), cmap=cm.jet,
                             linewidth=0, edgecolor='none', alpha=0.5)
        plt.xlabel("x")
        plt.ylabel("y")

        if show:
            plt.show()



class Individual:
    def __init__(self, generation, vl, vr):
        self.fitness = 0
        self.genotype = [vl, vr]
        self.generation = generation



class EvolutionAlgorithm:

    def __init__(self, max_fitness_val, population_size, bounds_left_wheel, bounds_right_wheel, fnc, cprob, mprob):
        self.max_fitness_val = max_fitness_val
        self.best_fitness = 0
        self.population_size = population_size
        self.eval = fnc

        self.bounds_left_wheel = bounds_left_wheel
        self.bounds_right_wheel = bounds_right_wheel

        self.cross_over_prob = cprob
        self.mutation_prob = mprob

        self.generation_index = 0
        self.current_generation = self.initial_population(population_size, bounds_left_wheel, bounds_right_wheel)
        self.generations = []
        self.fitness_values = []

        self.max = -100000

    def initial_population(self, population_size, bounds_left_wheel, bounds_right_wheel):
        # Uniformly choose elements on a given interval on bounded phenotype
        vl = np.random.uniform(bounds_left_wheel[0], bounds_left_wheel[1], size=population_size)
        vr = np.random.uniform(bounds_right_wheel[0], bounds_right_wheel[1], size=population_size)
        individuals = []
        for i in range(population_size):
            individual = Individual(self.generation_index, vl[i], vr[i])
            individuals.append(individual)
        return individuals

    def evaluate_fittness(self):
        # Iterate over each individual in generation and evaluate it
        
        for p in self.current_generation:
            val = - self.eval.call(*p.genotype)

            if not isinstance(val, float):
                val = val[0]

            # Two ways of encoding the fitness: the distance to minimum value 
            # and the distance to the point of the global minima
            p.fitness = val

            self.fitness_values.append(p.fitness)
            if val > self.max:
                self.max = val

     
        
    def reproduction(self):
        # Perform selection 
        # Tournament selection + TODO: roullete wheel selection
        parents = [self.tournament_selection() for i in range(self.population_size)]

        new_gen = []
        for i in range(0, self.population_size, 2):
            p1 = parents[i]
            p2 = parents[i+1]
            # Perform crossover and then mutation
            for child in self.cross_over(p1, p2):
                new_c = self.mutation(child)
                new_gen.append(new_c)

        return new_gen

    def roulette_wheel_selection(self):
        # Probabilities for each agent's speeds
        fitness_sum = sum(self.fitness_values)
        likelihood_selection = []
        for value in self.fitness_values:
            probability = value / fitness_sum
            likelihood_selection.append(probability)
        return likelihood_selection   

    def tournament_selection(self):
        # first random selection
        k = 3
        selected = np.random.randint(len(self.current_generation))
        for i in np.random.randint(0, len(self.current_generation), k-1):
            if self.fitness_values[i] > self.fitness_values[selected]:
                selected = i
        return self.current_generation[selected]


    # ind_1 = [vl1, vr1]
    # ind_2 = [vl2, vr2]
    # -> new individuals => [vl1, vr2] & [vl2, vr1]
    def cross_over(self, individual_1, individual_2):
        child_1 = individual_1
        child_2 = individual_2
        if random.uniform(0,1) < self.cross_over_prob:
            child_1 = Individual(child_1.generation,individual_1.genotype[0], individual_2.genotype[1])
            child_2 = Individual(child_2.generation,individual_2.genotype[0], individual_1.genotype[1])

        return child_1, child_2

    def mutation(self, individual):
        new_individual = individual
        if random.uniform(0,1) < self.mutation_prob:
            # Randomly select the char to mutate
            mutation_index = random.randint(0, len(individual.genotype)-1)
            individual_genotype = individual.genotype

            bounds = self.bounds_left_wheel
            if mutation_index == 1:
                bounds = self.bounds_right_wheel

            # Mutate genotype
            individual_genotype[mutation_index] = np.random.uniform(bounds[0], bounds[1], size=1)
            new_individual = Individual(individual.generation + 1, individual_genotype[0], individual_genotype[1])
        return new_individual


    def run_ea(self, iter=10):
        for i in range(iter):
            # First, evaluate fitness of the current generation
            self.evaluate_fittness()

            # Then add it to generations
            self.generations.append(self.current_generation)

            # Stop if diff between max and max_fitness_value is less than 10e-5
            if abs(self.max_fitness_val - self.max) < 0.00001:
                return (self.max, i, self.generations)

            # Selection -> Crossover -> Mutation -> new population
            new_gen = self.reproduction()
            self.current_generation = new_gen
            self.generation_index = self.generation_index + 1
            self.fitness_values = []
        
        return (self.max,i,self.generations)




def update_3D(i, data, graph):
    graph._offsets3d = (data[i][0], data[i][1], data[i][2])


def visualize_3D(data, fnc,max_iter, save=False, alpha=0.5, file_name='3d_animation'):
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')

    X = fnc.X[0]
    Y = fnc.X[1]
    Z = fnc.value


    ax.plot_surface(X, Y, Z, alpha=alpha, cmap=cm.plasma)
    

    graph = ax.scatter(data[0][0], data[0][1], data[0][2], c='black',  alpha=alpha)

    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')

    animat = animation.FuncAnimation(fig, 
                        update_3D, 
                        max_iter,
                        fargs=(data, graph),
                        interval=100
                        )

    if save:
        Writer = animation.writers['ffmpeg']
        writer = Writer(fps=30, 
                        extra_args=['-vcodec', 'libx264'])
        animat.save(f'{file_name}.mp4', writer=writer)
    
    plt.show()




def get_rastrigin():
    x = np.linspace(-4, 4, 50)
    y = np.linspace(-4, 4, 50)
    X, Y = np.meshgrid(x, y)
    rastrigin_fnc = Function(rastrigin, X, Y)
    return rastrigin_fnc

def get_rosenbrock():
    x = np.arange(-1.5, 2.0, 0.05)
    y = np.arange(-0.5, 3.0, 0.05)
    X, Y = np.meshgrid(x, y)

    rosenbrock_fnc = Function(rosenbrock, X, Y)
    return rosenbrock_fnc

def prepare_data(generations, fnc):
    data = []

    for i in range(len(generations)):
        g = generations[i]
        X = list()
        Y = list()
        Z = list()
        for j in range(len(g)):
            x = g[j].genotype[0]
            y = g[j].genotype[1]
            z = fnc.call(*g[j].genotype)

            if not isinstance(x, float):
                x = x[0]
            if not isinstance(y, float):
                y = y[0]
            if not isinstance(z, float):
                z = z[0]


            X.append(x)
            Y.append(y)
            Z.append(z)

        data.append((X,Y,Z))


    return data

def test_ea(fnc, pop_size, iter, cprob=0.1, mprob=0.9):
    intervals = fnc.get_dimension_intervals()

    ea = EvolutionAlgorithm(0,pop_size, intervals[0], intervals[1], fnc, cprob,mprob)
    (max, i,generations) = ea.run_ea(iter)
    data = prepare_data(generations, fnc)
    print("Stopped in generation " + str(i+1))
    print("Max value: " + str(max))
    
    visualize_3D(data, fnc, len(generations), save=True)

# Uncomment what you want to run
if __name__ == "__main__":

    rosenbrock_fnc = get_rosenbrock()
    rastrigin_fnc = get_rastrigin()


    test_ea(rastrigin_fnc, 10, 100)



