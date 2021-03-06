import sys
import os
import json
import random
import numpy as np
import multiprocessing as mp
import time
import matplotlib.pyplot as plt
import copy


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
        self.map_index = -1

results = []

class ER:
    def __init__(self, 
                maps = None,
                population_size = 10,
                cross_over_prob = 0.9,
                mutation_prob = 0.1,
                number_of_generations = 10,
                ann = None, # ANN that contains the structure of the NN
                max_abs_speed = 2, # if max speed is 2, that means the robot is moving 200px/s
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

        self.avg_fitness = []

        self.avg_by_map = []


    def initialize_population(self):
        structure = self.ann.get_structure()
        population = list()

        for i in range(self.population_size):
            weights = list()
            for j in range(len(structure)):
                s = structure[j]
                w = np.random.rand(s[0], s[1])

                # go over each element in w and set it to some small number instead
                for iw in range(len(w)):
                    for jw in range(len(w[iw])):
                        w[iw][jw] = random.uniform(-0.1,0.1)

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
        max_x = max(x)
        min_x = min(x)
        y = agent.y_coord 
        max_y = max(y)
        min_y = min(y)

        diff_x = max_x - min_x
        diff_y = max_y - min_y
        diff = diff_x + diff_y
        areax = np.trapz(y=y, x=x)
        areay = np.trapz(y=x, x=y)
        A = (areax+areay)

        # Punishment collisions
        col = agent.num_of_collisions
        upd = agent.num_agent_updates      
        P = col/upd
        if col>0:
            P = 0.95

        # Penalty for colliding into a corner
        corner_penalty = 1.0
        if(agent.num_of_corner_collisions > 0):
            corner_penalty = 0.00001

        if agent.counted_sensors == 0:
            agent.counted_sensors = 1

        # Reward for large  min_distance
        min_penalty = (agent.min_distance/agent.max_vision)

        # Punishment for amount of time being too close to the walls
        close_penalty = (agent.close_to_wall/agent.counted_sensors)**2

        # Reward for amount of time being a good distance from the walls
        far_reward = (agent.far_from_wall/agent.counted_sensors)**2

        # A medium-high sensor distance average is good, low is bad
        if(agent.num_agent_updates == 0):
            agent.num_agent_updates = 1
        avg_sensor_dist = (agent.avg_sensor_distance/agent.num_agent_updates)

        F = 0.0001*A*(1-P)*corner_penalty*avg_sensor_dist*1000*far_reward*500*(1-close_penalty)*min_penalty
        return F


    def find_best(self):
        for g in self.current_generation:
            if self.avg_by_map[g.map_index] == 0 or self.avg_by_map[g.map_index] == None:
                self.avg_by_map[g.map_index] = 1
            g.fitness = g.fitness/self.avg_by_map[g.map_index]
        
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
            "best_fitness":best.fitness,
            "avg_fitness":self.avg_fitness,
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


    def roullete_wheel_selection(self):
        max  = sum([c.fitness for c in self.current_generation])
        pick = random.uniform(0, max)
        current = 0
        for g in self.current_generation:
            current += g.fitness
            if current > pick:
                return g

    def tournament_selection(self):
        # First random selection
        k = 7
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
        if random.uniform(0,1) <= self.cross_over_prob:
            # Select randomly a layer, select a cross-over point and cross-over the weights
            num_layers = len(w1)
            i = random.randint(0,num_layers-1)

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
                rand_num = np.random.randint(0,len(wl)-1, random.randint(1,len(wl)))
               
                # Mutate random amount of values
                # Requires a bit of expirementation...
                for j in range(len(rand_num)):
                    r = random.uniform(0, 1)
                    c = random.randint(0,1)
                    tmp = wl[rand_num[j]]
                    if c == 0:
                        tmp = tmp + tmp*r
                    else:
                        tmp = tmp - tmp*r

                    wl[rand_num[j]] = tmp
                
                layer[mutation_index] = wl

        individual.weights = w
        return individual


    def reproduction(self):
        # Perform selection
        parents = [self.roullete_wheel_selection() for i in range(self.population_size)]

        new_gen = list()
        for i in range(0, self.population_size, 2):
            p1 = copy.deepcopy(parents[i])
            p2 = copy.deepcopy(parents[i + 1])
            
            #print("Generation p1,p2 " + str(p1.generation) + "," + str(p2.generation))
            # Perform crossover and then mutation
            for child in self.cross_over(p1, p2):
                new_c = self.mutation(child)
                new_c.generation = child.generation + 1
                new_gen.append(new_c)        

        self.current_generation = new_gen




    def run_er(self):

        best_fitness = []
        for i in range(self.number_of_generations):

            # Evaluate fitness of current generation
            self.evaluate_fitness()

            # Find best individual in the current generation 
            # and save its weights to disk

            self.avg_by_map = []

            i = 0
            for m in self.maps:
                avg = 0
                count = 0
                for g in self.current_generation:
                    if g.agent.map["index"] == i:
                        avg = avg + g.fitness
                        count = count + 1
                avg = avg/count
                if count == 0:
                    avg = 1
                self.avg_by_map.append(avg)

                i = i+1

            self.avg_fitness.append(avg)


            best = self.find_best()
            best_fitness.append(best.fitness)

            print("Best fitness: " + str(best.fitness))
            print("Average fitness: " + str(avg))


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
    individual.map_index = agent.map["index"]

    return individual

def create_agent(maps,ann, max_speed):
    # Random map from the pool
    map_index = random.randint(0, len(maps)-1)
    map = maps[map_index]

    # Random starting position on the map
    pos_index = random.randint(0, len(map["start_points"])-1)

    # Random radius in range [30,70]
    radius_min = 20
    radius_max = 50
    rnd_radius = random.uniform(radius_min, radius_max)

    # Random vision distance
    vision_min = 50
    vision_max = 500
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
        number_of_generations = 100,
        time=10, # in s (this is the runtime of a single simulation of the agent)
        time_step=10, #in ms
        weights_dir = weights_dir,
        cross_over_prob = 0.9,
        mutation_prob = 0.05,
        max_abs_speed= 2.5
        )
    er.run_er()


if __name__ == '__main__':
    main()