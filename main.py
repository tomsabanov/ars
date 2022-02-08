# /usr/bin/python3

'''
Assignment 1:
--------------------------------
• Evaluate properties of PSO and compare
PSO against gradient descent

• Use simulations to convince a 
customer/project leader/colleague of the
pros and cons of PSO

• Find out if it makes sense to combine PSO 
and gradient descent



Steps to complete this assignment:
----------------------------------
1. Create a 3D plot of benchmark functions (rosenbrock + rastrigin)  ---> DONE
2. Implement PSO
3. Implement animations on benchmark functions
4. Evaluate PSO on benchmark functions

---------------------- Not necessary (only if there is too much time)
5. Implement gradient descent 
6. Evaluate gradient descent on benchmark functions
7. Try to combine gradient descent and PSO

'''

import numpy as np
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.colors import LogNorm
from matplotlib import cm
import matplotlib.pyplot as plt
import math
import random as rnd
import numpy as np
#import matplotlib.animation as animation
from pyglet.resource import animation
from matplotlib.animation import FuncAnimation



def rosenbrock(*X):
    a = 0
    b = 150

    x = X[0]
    y = X[1]
    return (a - x) ** 2 + b * ((y - x ** 2) ** 2)


def rastrigin(*X):
    A = 10
    result = A * len(X) + sum([(x ** 2 - A * np.cos(2 * math.pi * x)) for x in X])
    #print(len(result))
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

    def plot_contour(self, show=True):
        self.fig = plt.figure()
        self.ax = self.fig.add_subplot(111)

        plt.contour(self.X[0], self.X[1], self.value, 300)

        if show:
            plt.show()


class PSO:
    def __init__(self,
                 fnc: Function,
                 num_of_agents=20,
                 max_iter=1000,
                 a=0.9,
                 b=0,
                 c=0
                 ):
        self.fnc = fnc
        self.num_of_agents = num_of_agents
        self.max_iter = max_iter

        self.a = a
        self.b = b
        self.c = c

        # Set initial particle velocities in each dimension to 1.0 (maybe random would perform better?)
        self.velocities = self.generate_initial_velocities()

        # Generate random positions based on function specification
        # (generate values between the specified intervals....)
        self.positions = self.generate_initial_positions()

        # Set best individual positions to initial positions
        self.best_positions = self.positions

        # Remember global best position with an index
        self.best_global_position = -1

        # Evaluations of positions
        self.evaluations = np.zeros(num_of_agents)

        # Evaluations of best positions
        self.best_evaluations = np.zeros(num_of_agents)

        # Save all of the positions in a history (list of lists, where each list
        # has all of the positions of a single particle)
        self.hist = list()
        self.prepare_history()

    def prepare_history(self):
        for i in range(self.num_of_agents):
            self.hist.append(list())

    def generate_initial_velocities(self):
        velocities = np.zeros((self.num_of_agents, self.fnc.dim))
        for i in range(len(velocities)):
            velocities[i] = (rnd.uniform(-1, 1), rnd.uniform(-1, 1))
        return velocities

    def generate_initial_positions(self):
        # Set initial positions to 0
        positions = np.zeros((self.num_of_agents, self.fnc.dim))

        # Get intervals on which the function is specified
        intervals = self.fnc.get_dimension_intervals()

        # Iterate over each position and each interval and generate a random val in that interval and update the value in positions
        for i in range(len(positions)):
            for j in range(len(intervals)):
                rand_val = rnd.uniform(intervals[j][0], intervals[j][1])
                positions[i][j] = rand_val

        return positions

    def evaluate_particles(self):
        for i in range(self.num_of_agents):
            pos = self.positions[i]
            eval = self.fnc.call(*pos)

            # Add to history
            self.hist[i].append((pos[0], pos[1], eval))

            pos_best = self.best_positions[i]
            best_eval = self.fnc.call(*pos_best)

            # Update best position
            if eval < best_eval:
                self.best_positions[i] = pos
                self.best_evaluations[i] = eval

            # check if particle best position is best globally and update index
            if best_eval < self.fnc.call(*self.best_positions[self.best_global_position]):
                self.best_global_position = i

            self.evaluations[i] = eval

    def update_velocities(self):
        for i in range(self.num_of_agents):
            vel = self.velocities[i]

            pos_best = self.best_positions[i]
            pos = self.positions[i]

            pos_global_best = self.best_positions[self.best_global_position]

            new_vel = self.a * vel + self.b * rnd.random() * (pos_best - pos)
            new_vel = new_vel + self.c * rnd.random() * (pos_global_best - pos)

            self.velocities[i] = new_vel

    def update_positions(self):
        # Get intervals on which the function is specified
        intervals = self.fnc.get_dimension_intervals()

        for i in range(self.num_of_agents):
            pos = self.positions[i]
            new_pos = pos + self.velocities[i]
            self.positions[i] = new_pos

            # Check if position is out of defined bounds
            for j in range(len(intervals)):
                if self.positions[i][j] < intervals[j][0]:
                    self.positions[i][j] = intervals[j][0]

                if self.positions[i][j] > intervals[j][1]:
                    self.positions[i][j] = intervals[j][1]
        # print(self.positions[0][0])

    def run_simulation(self, a):

        for i in range(self.max_iter):

            # 1. Evaluate particle positions
            self.evaluate_particles()

            # 2. Update particle velocities
            self.update_velocities()

            # 3. Update new particle positions
            self.update_positions()

            if a == "progressive":  # If we want to decrease a from 0.9 to 0.4 over 1000 iterations
                if i <= 1000:
                    self.a = 0.9 - 0.5 * (i / 1000)
                else:
                    self.a = 0.4
            else:                   # If we want to manually set a
                self.a = a

            if i > 800 and a == "progressive":
                self.b = 2
                self.c = 2

            # print(self.a)

        #for pos in self.positions:
            # print(len(pos))
            #print(str(round(pos[0], 2)) + "," + str(round(pos[1], 2)))

    # Return error
    def get_error(self):
        #error = math.sqrt(math.pow(self.best_global_position,2) + math.pow(self.best_global_position,2))
        error = math.sqrt(math.pow(self.positions.tolist()[self.best_global_position][0],2) + math.pow(self.positions.tolist()[self.best_global_position][1],2))
        return error

    def return_position(self):
        return self.positions

    def animation_function(self, num, datasets, dots, graph):
        for i in range(self.num_of_agents):
            # lines[i].set_data(datasets[i][0:2, :num])
            # lines[i].set_3d_properties(datasets[i][2, :num])

            dots[i].set_data(datasets[i][0:2, :num])
            # dots[i].set_3d_properties(datasets[i][2, :num])

    def animate(self):
        # We have the figure in the fnc object
        self.fnc.plot_contour(False)

        # List of lists of x/y/z coordinates where each list holds x/y/z values for a single particle over the entire simulation
        X = list()
        Y = list()
        Z = list()
        for i in range(self.num_of_agents):
            X.append(list())
            Y.append(list())
            Z.append(list())

        for i in range(self.num_of_agents):
            for j in range(self.max_iter):
                pos = self.hist[i][j]
                X[i].append(pos[0])
                Y[i].append(pos[1])
                Z[i].append(pos[2])

        # Create datasets of [x,y,z] for each particle
        datasets = list()
        for i in range(self.num_of_agents):
            datasets.append([X[i], Y[i], Z[i]])
        for i in range(self.num_of_agents):
            # This has to be done because of some error in animation_function later on
            # when animating
            datasets[i] = np.array(datasets[i])

        # Create dots plots and line plots for each dataset
        dots = list()
        for i in range(self.num_of_agents):
            d = \
            plt.plot(datasets[i][0], datasets[i][1], markersize=10, markeredgecolor="black", markerfacecolor="purple",
                     marker="o", alpha=1.0)[0]
            dots.append(d)

        anim = FuncAnimation(self.fnc.fig, self.animation_function, frames=self.max_iter,
                                       fargs=(datasets, dots), interval=1000, blit=False)
        #anim.save('pso.mp4', writer='ffmpeg', fps=30)
        plt.show()

# Will find a configuration resulting in the solution (0,0)
def rastrigin_experiment_find_optimal():
    # Example rastrigin
    x = np.linspace(-4, 4, 50)
    y = np.linspace(-4, 4, 50)
    X, Y = np.meshgrid(x, y)
    rastrigin_fnc = Function(rastrigin, X, Y)

    # Loop until we find the global optimal solution
    flag = True
    while flag:
        pso = PSO(rastrigin_fnc, 20, 1000)
        pso.run_simulation("progressive")
        results = pso.return_position()
        for r in results:
           if -0.01 < r[0] and r[0] < 0.01 and -0.01 < r[1] and r[1] < 0.01:
               flag = False
               break

    pso.animate()

def rastrigin_experiment_a_constant():
    # Example rastrigin
    x = np.linspace(-4, 4, 50)
    y = np.linspace(-4, 4, 50)
    X, Y = np.meshgrid(x, y)
    rastrigin_fnc = Function(rastrigin, X, Y)

    # Loop until we find the global optimal solution
    flag = True
    experiment_results = []
    for i in np.arange(0,2,0.1):
        immediate_results = []
        for j in range(10):
            pso = PSO(rastrigin_fnc, 20, 1000)
            pso.run_simulation(i)
            immediate_results.append(pso.get_error())

        experiment_results.append(sum(immediate_results) / len(immediate_results))

    pso.animate()
    print(experiment_results)

    f = open("a_constant_results.txt", "w")
    f.write(str(experiment_results))

def rosenbrock_experiment_population_comparison():
    # Example rastrigin
    x = np.linspace(-4, 4, 50)
    y = np.linspace(-4, 4, 50)
    X, Y = np.meshgrid(x, y)
    rosenbrock_fnc = Function(rosenbrock, X, Y)

    # Loop until we find the global optimal solution
    #flag = True
    #experiment_results_constant = []
    #for i in np.arange(1,50,1):
    #    immediate_results = []
    #    print(str(i) + " - constant")
    #    for j in range(10):
    #        pso = PSO(rosenbrock_fnc, i, 1000) # Varying the amount of iterations
    #        pso.run_simulation(0.4) # Constant
    #        immediate_results.append(pso.get_error())
    #    print(immediate_results)

        #experiment_results_constant.append(sum(immediate_results) / len(immediate_results))
    #    experiment_results_constant.append(sum(abs(number) for number in immediate_results) / 10)
    #print(experiment_results_constant)
    #f = open("a_constant_results_varying_population_rosenbrock.txt", "w")
    #f.write(str(experiment_results_constant))

    experiment_results_linear = []
    for i in np.arange(1, 50, 1):
        immediate_results = []
        print(str(i) + " - linear")
        for j in range(10):
            pso = PSO(rosenbrock_fnc, i, 1000)
            pso.run_simulation("progressive")  # Varying the amount of iterations
            immediate_results.append(pso.get_error())

        experiment_results_linear.append(sum(abs(number) for number in immediate_results) / 10)

    print(experiment_results_linear)
    f = open("a_linear_results_varying_population_rosenbrock.txt", "w")
    f.write(str(experiment_results_linear))

    pso.animate()

def rastrigin_experiment_population_comparison():
    # Example rastrigin
    x = np.linspace(-4, 4, 50)
    y = np.linspace(-4, 4, 50)
    X, Y = np.meshgrid(x, y)
    rosenbrock_fnc = Function(rosenbrock, X, Y)

    # Loop until we find the global optimal solution
   # flag = True
   # experiment_results_constant = []
   # for i in np.arange(1,50,1):
   #     immediate_results = []
   #     print(str(i) + " - constant")
   #     for j in range(10):
   #         pso = PSO(rosenbrock_fnc, i, 1000) # Varying the amount of iterations
   #         pso.run_simulation(0.4) # Constant
   #         immediate_results.append(pso.get_error())
   #     print(immediate_results)#

   #     #experiment_results_constant.append(sum(immediate_results) / len(immediate_results))
   #     experiment_results_constant.append(sum(abs(number) for number in immediate_results) / 10)
   # print(experiment_results_constant)
   # f = open("a_constant_results_varying_population_rastrigin.txt", "x")
   # f.write(str(experiment_results_constant))

    experiment_results_linear = []
    for i in np.arange(1, 50, 1):
        immediate_results = []
        print(str(i) + " - linear")
        for j in range(7):
            pso = PSO(rosenbrock_fnc, i, 1000)
            pso.run_simulation("progressive")  # Varying the amount of iterations
            immediate_results.append(pso.get_error())
        print(immediate_results)
        experiment_results_linear.append(sum(abs(number) for number in immediate_results) / 7)

    print(experiment_results_linear)
    f = open("a_linear_results_varying_population_rastrigin.txt", "x")
    f.write(str(experiment_results_linear))

    pso.animate()



def rosenbrock_experiment_iteration_comparison():
    # Example rastrigin
    x = np.linspace(-4, 4, 50)
    y = np.linspace(-4, 4, 50)
    X, Y = np.meshgrid(x, y)
    rosenbrock_fnc = Function(rosenbrock, X, Y)

    # Loop until we find the global optimal solution
    flag = True
    experiment_results_constant = []
    for i in np.arange(100,2100,100):
        immediate_results = []
        print(str(i) + " - constant")
        for j in range(10):
            pso = PSO(rosenbrock_fnc, 30, i) # Varying the amount of iterations
            pso.run_simulation(0.4) # Constant
            immediate_results.append(pso.get_error())

        experiment_results_constant.append(sum(immediate_results) / 10)
    print(experiment_results_constant)
    f = open("a_constant_results_varying_iterations_rosenbrock.txt", "w")
    f.write(str(experiment_results_constant))

    experiment_results_linear = []
    for i in np.arange(100, 2100, 100):
        immediate_results = []
        print(str(i) + " - linear")
        for j in range(10):
            pso = PSO(rosenbrock_fnc, 30, i)
            pso.run_simulation("progressive")  # Varying the amount of iterations
            immediate_results.append(pso.get_error())

        experiment_results_linear.append(sum(immediate_results) / 10)

    print(experiment_results_linear)
    f = open("a_linear_results_varying_iterations_rosenbrock.txt", "w")
    f.write(str(experiment_results_linear))

    pso.animate()


def rastrigin_experiment_iteration_comparison():
    # Example rastrigin
    x = np.linspace(-4, 4, 50)
    y = np.linspace(-4, 4, 50)
    X, Y = np.meshgrid(x, y)
    rastrigin_fnc = Function(rastrigin, X, Y)

    # Loop until we find the global optimal solution
    flag = True
    experiment_results_constant = []
    for i in np.arange(100,2100,100):
        immediate_results = []
        print(str(i) + " - constant")
        for j in range(10):
            pso = PSO(rastrigin_fnc, 30, i) # Varying the amount of iterations
            pso.run_simulation(0.4) # Constant
            immediate_results.append(pso.get_error())

        experiment_results_constant.append(sum(immediate_results) / 10)
    p#rint(experiment_results_constant)
    #f = open("a_constant_results_varying_iterations.txt", "w")
    #f.write(str(experiment_results_constant))

    experiment_results_linear = []
    for i in np.arange(100, 2100, 100):
        immediate_results = []
        print(str(i) + " - linear")
        for j in range(10):
            pso = PSO(rastrigin_fnc, 30, i)
            pso.run_simulation("progressive")  # Varying the amount of iterations
            immediate_results.append(pso.get_error())

        experiment_results_linear.append(sum(immediate_results) / 10)

    print(experiment_results_linear)
    f = open("a_linear_results_varying_iterations.txt", "w")
    f.write(str(experiment_results_linear))

    pso.animate()




def plot_experiment():
    f = open("a_constant_results.txt").readline().replace("[", "").replace("]", "").replace(" ", "").split(",")
    r = [float(e) for e in f]
    print(r)
    plt.plot(r)
    plt.xlabel("Constant value for 'a'")
    plt.ylabel("Avg Error")
    plt.show()

def plot_experiment_training_size1():
    f = open("a_constant_results_varying_iterations.txt").readline().replace("[", "").replace("]", "").replace(" ", "").split(",")
    r_constant = [float(e) for e in f]
    print(r_constant)

    f = open("a_linear_results_varying_iterations.txt").readline().replace("[", "").replace("]", "").replace(" ","").split(",")
    r_linear = [float(e) for e in f]

    plt.plot(np.arange(100, 2100, 100), r_constant, label="Constant 'a'=0.4, b and c = 2")
    plt.plot( np.arange(100, 2100, 100), r_linear, label="Linear Decreasing 'a', b and c = 2")
    plt.xlabel("Iterations")
    plt.ylabel("Avg Error")
    plt.legend()
    plt.title("Error Comparison of Linear Decreasing 'a' vs Constant 'a' Over Varying Iterations with a Population Size of 20 Particles over Rastrigin.")
    plt.show()

def plot_experiment_training_size1_rosenbrock():
    f = open("a_constant_results_varying_iterations_rosenbrock.txt").readline().replace("[", "").replace("]", "").replace(" ", "").split(",")
    r_constant = [float(e) for e in f]
    print(r_constant)

    f = open("a_linear_results_varying_iterations_rosenbrock.txt").readline().replace("[", "").replace("]", "").replace(" ","").split(",")
    r_linear = [float(e) for e in f]

    plt.plot(np.arange(100, 2100, 100), r_constant, label="Constant 'a'=0.4, b and c = 2")
    plt.plot( np.arange(100, 2100, 100), r_linear, label="Linear Decreasing 'a', b and c = 2")
    plt.xlabel("Iterations")
    plt.ylabel("Avg Error")
    plt.legend()
    plt.title("Error Comparison of Linear Decreasing 'a' vs Constant 'a' Over Varying Iterations with a Population Size of 20 Particles over Rosenbrock.")
    plt.show()


def plot_experiment_population_size_rosenbrock():
    f = open("a_constant_results_varying_population_rosenbrock.txt").readline().replace("[", "").replace("]", "").replace(" ", "").split(",")
    r_constant = [float(e) for e in f]
    print(r_constant)

    f = open("a_linear_results_varying_population_rosenbrock.txt").readline().replace("[", "").replace("]", "").replace(" ","").split(",")
    r_linear = [float(e) for e in f]

    plt.plot(np.arange(1, 50, 1), r_constant, label="Constant 'a'=0.4, b and c = 2")
    plt.plot( np.arange(1, 50, 1), r_linear, label="Linear Decreasing 'a'")
    plt.xlabel("Population")
    plt.ylabel("Avg Error")
    plt.legend()
    plt.title("Error Comparison of Linear Decreasing 'a' vs Constant 'a' Over Varying Population with a Training Size of 1000 Iterations over Rosenbrock.")
    plt.show()

def plot_experiment_population_size_rastrigin():
    f = open("a_constant_results_varying_population_rastrigin.txt").readline().replace("[", "").replace("]", "").replace(" ", "").split(",")
    r_constant = [float(e) for e in f]
    print(r_constant)

    f = open("a_linear_results_varying_population_rastrigin.txt").readline().replace("[", "").replace("]", "").replace(" ","").split(",")
    r_linear = [float(e) for e in f]

    plt.plot(np.arange(1, 50, 1), r_constant, label="Constant 'a'=0.4, b and c = 2")
    plt.plot( np.arange(1, 50, 1), r_linear, label="Linear Decreasing 'a'")
    plt.xlabel("Population")
    plt.ylabel("Avg Error")
    plt.legend()
    plt.title("Error Comparison of Linear Decreasing 'a' vs Constant 'a' Over Varying Population with a Training Size of 1000 Iterations over Rastrigin.")
    plt.show()


# Uncomment what you want to run
if __name__ == "__main__":
    # Example rosenbrock
    x = np.arange(-1.5, 2.0, 0.05)
    y = np.arange(-0.5, 3.0, 0.05)
    X, Y = np.meshgrid(x, y)

    rosenbrock_fnc = Function(rosenbrock, X, Y)

    #pso = PSO(rosenbrock_fnc, 20, 1000)
    #pso.run_simulation()
    #pso.animate()

    #rastrigin_experiment_find_optimal()
    #rastrigin_experiment_a_constant()
    #rastrigin_experiment_iteration_comparison()
    #rosenbrock_experiment_iteration_comparison()
    #rosenbrock_experiment_population_comparison()
    #rastrigin_experiment_population_comparison()


    #plot_experiment()
    #plot_experiment_training_size1() #rastrigin
    #plot_experiment_training_size1_rosenbrock()
    #plot_experiment_population_size_rosenbrock()
    plot_experiment_population_size_rastrigin()
