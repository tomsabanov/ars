import sys
import os
import json
import random
import numpy as np
import multiprocessing as mp
import time
import matplotlib.pyplot as plt
import threading

from utils.agent import Agent
from Simulation import Simulation
from ann import Dense, Network
from utils.map import read_map, get_maps



class Individual:
    def __init__(self, generation, weights):
        self.fitness = 0
        self.weights = weights
        self.generation = generation
        self.agent = None # Agent has the ann

results = []

class ER:
    def __init__(self, 
                maps = None,
                population_size = 10,
                cross_over_prob = 0.9,
                mutation_prob = 0.05,
                number_of_generations = 10,
                ann = None, # ANN that contains the structure of the NN
                max_abs_speed = 3, # if max speed is 3, that means the robot is moving 300px/s
                time_step = 100, # in ms
                time = 10, # in seconds
                weights_dir="./weights"
                ):
        self.maps = maps

        self.population_size = population_size
        self.cross_over_prob = cross_over_prob
        self.mutation_prob = mutation_prob
        self.number_of_generations = number_of_generations

        self.ann = ann
        self.max_abs_speed = max_abs_speed
        self.time_step = time_step
        self.time = time

        self.generation_index = 0
        self.current_generation = self.initialize_population()
        self.best_in_generation= list() # best in each generation
        self.weights_dir = weights_dir


    def initialize_population(self):
        structure = self.ann.get_structure()
        population = list()

        for i in range(self.population_size):
            weights = list()
            for j in range(len(structure)):
                s = structure[j]
                w = np.random.rand(s[0], s[1])
                weights.append(w)
            i = Individual(self.generation_index, weights)
            population.append(i)

        return population



    def evaluate_fitness(self):
        # We evaluate the fitness by simulating the agent and 
        # then calculate the fitness by the properties of the agent
        print("Generation: " + str(self.generation_index))

        # We parallelize the process so we can quickly evaluate the entire generation
        print("Number of CPU cores: " + str(mp.cpu_count()))

        t = time.time()

        pool = mp.Pool(mp.cpu_count())
        # Step 3: Use loop to parallelize
        for i, individual in enumerate(self.current_generation):
            pool.apply_async(simulate, args=(
                i, 
                individual, 
                self.maps, 
                self.ann,
                self.time,
                self.time_step,
                self.max_abs_speed
                ), callback=collect_result)

        pool.close()
        pool.join()

        el = "Elapsed time: " + str(time.time() - t)
        print(el)

        # Now we loop over the individual agents in results and calculate their fittness
        global results
        self.current_generation = list()

        num_individ = len(results)
        for i in range(num_individ):
            ind = results[i]
            ind.fitness = self.calculate_fitness(ind.agent)
            self.current_generation.append(ind)

        results = []


    def calculate_fitness(self, agent):
        # Fitness function based on the data the agent has collected

        # Area
        x = agent.x_coord
        y = agent.y_coord 
        areax = np.trapz(y=y, x=x)
        areay = np.trapz(y=x, x=y)
        A = ((areax+areay)/agent.radius)/1000

        # Punishment collisions
        col = agent.num_of_collisions
        upd = agent.num_agent_updates      
        P = col/upd

        F = A*(1-P)
        return F


    def find_best(self):
        self.current_generation.sort(key=lambda x: x.fitness, reverse=True)

        best = self.current_generation[0]
        self.best_in_generation.append(best)

        # Write the weights to the disk 
        gen = "generation_"+str(best.generation)+"_weights.json"
        file = os.path.join(self.weights_dir,gen)
        
        serialized_weights = list()
        for w in best.weights:
            serialized_weights.append(
                w.tolist()
            )
        serialized_weights = json.dumps(serialized_weights)

        data = {
            "cross_over_prob":self.cross_over_prob,
            "mutation_prob":self.mutation_prob,
            "population_size":self.population_size,
            "time_step":self.time_step,
            "run_time":self.time,
            "weights":serialized_weights,
            "nn_structure":self.ann.get_structure()
        }
        with open(file, 'w') as outfile:
            json.dump(data, outfile, indent=4)
        
        return best


    def tournament_selection(self):
        # First random selection
        k = 3
        selected = np.random.randint(len(self.current_generation))
        for i in np.random.randint(0, len(self.current_generation), k-1):
            if self.current_generation[i].fitness > self.current_generation[selected].fitness:
                selected = i
        return self.current_generation[selected]


    # ind_1 = Individual(weights1)
    # ind_2 = Individual(weights2)
    def cross_over(self, individual_1, individual_2):
        child_1 = individual_1
        child_2 = individual_2

        w1 = child_1.weights
        w2 = child_2.weights
        if random.uniform(0,1) < self.cross_over_prob:
            # Go through each layer, select a cross-over point and cross-over the weights
            num_layers = len(w1)
            for i in range(num_layers):
                l1 = w1[i]
                l2 = w2[i]
                point = random.randint(1,len(l1)-1)

                # l1 gets left/right of point of l2
                coin = random.randint(0,1)
                if coin == 0:
                    tmp = l1[:point].copy()
                    l1[:point] = l2[:point]
                    l2[:point] = tmp
                else:
                    tmp = l1[point:].copy()
                    l1[point:] = l2[point:]
                    l2[point:] = tmp
                
                w1[i] = l1
                w2[i] = l2

        child_1.weights = w1
        child_2.weights = w2

        return child_1, child_2


    def mutation(self, individual):
        w = individual.weights
        if random.uniform(0,1) < self.mutation_prob:
            # Go through each layer of weights, randomly select one list
            # and mutate every value
            for i in range(len(w)):
                layer = w[i]
                mutation_index = random.randint(0, len(layer)-1)

                wl = layer[mutation_index]
                # Mutate all values or just a single one????????????????????
                # Requires a bit of expirementation
                for j in range(len(wl)):
                    r = random.uniform(0, 1)
                    wl[j] = r
                layer[mutation_index] = wl

        individual.weights = w
        return individual


    def reproduction(self):
        # Perform selection
        parents = [self.tournament_selection() for i in range(self.population_size)]

        new_gen = list()
        for i in range(0, self.population_size, 2):
            p1 = parents[i]
            p2 = parents[i + 1]
            # Perform crossover and then mutation
            for child in self.cross_over(p1, p2):
                new_c = self.mutation(child)
                new_gen.append(new_c)        

        self.current_generation = new_gen




    def run_er(self):

        best_fitness = []
        for i in range(self.number_of_generations):
            # Evaluate fitness of current generation
            self.evaluate_fitness()

            # Find best individual in the current generation 
            # and save its weights to disk
            best = self.find_best()
            best_fitness.append(best.fitness)

            print("Best fitness: " + str(best.fitness))


            # Reproduction includes selection + mutation
            self.reproduction()
            self.generation_index = self.generation_index + 1


            print("----------------")





def collect_result(result):
    global results
    results.append(result)

def simulate(i, individual, maps, ann, time, time_step, max_speed):
    # Create new ann with same layers as before, but we will set new weights
    net = Network(ann.get_layers())
    net.set_weights(individual.weights)
    
    # We create an agent with the ann
    agent = create_agent(maps, net, max_speed)
    
    # We run the simulation and receive back the updated agent
    agent = create_simulation(agent, time, time_step)

    individual.agent = agent

    return individual

def create_agent(maps,ann, max_speed):
    # Random map from the pool
    map_index = random.randint(0, len(maps)-1)
    map = maps[map_index]

    # Random starting position on the map
    pos_index = random.randint(0, len(map["start_points"])-1)

    # Random radius in range [30,70]
    radius_min = 30
    radius_max = 70
    rnd_radius = random.uniform(radius_min, radius_max)

    # Random vision distance
    vision_min = 50
    vision_max = 300
    rnd_vision = random.uniform(vision_min, vision_max) 

    agent = Agent(
                    map = map,
                    radius = rnd_radius,
                    start_pos_index = pos_index,
                    max_vision = rnd_vision,
                    ann = ann,
                    max_speed = max_speed
                )
    return agent

def create_simulation(agent, time, time_step):
    sim = Simulation(
        agent=agent, 
        render=False,
        simulation=True,
        time=time, # how many seconds the simulation will run,
        time_step=time_step # on how many ms should agent reevaluate motor speed
    )
    # simulate returns the agent object
    return sim.simulate()



def main():
    if len(sys.argv)<3:
        print("Provide path to maps and weights!")
        sys.exit()

    map_dir = sys.argv[1]
    maps = get_maps(map_dir)

    weights_dir = os.path.abspath(sys.argv[2])


    layers = [
        Dense(16,4),
        Dense(4,2)
    ]
    network = Network(layers)

    er = ER(
        maps = maps,
        ann = network,
        population_size = 40,
        number_of_generations = 10,
        time=20, # in s (this is the runtime of a single simulation of the agent)
        time_step=30, #in ms
        weights_dir = weights_dir
        )
    er.run_er()


if __name__ == '__main__':
    main()