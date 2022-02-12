# Assignment 1

## Evaluate properties of PSO and compare PSO against gradient descent

In PSO each particle represents a possible solution.
In the beginning, we initialize n number of random possible solutions.
Each particle has its own velocity and it also remembers its previous best position, called Pbest.
A group of particles (or swarm) also keeps track of the best Pbest achieved in the group, 
called Gbest.
The idea of PSO is to move each particle towards its Pbest and Gbest in each iteration 
of the algorithm. How fast the particle accelerates is determined by random weights for 
Pbest and Gbest.
The velocity of the particles is very important to achieve a good solution. 
If the velocity is too high, then the particle will keep jumping from place to place, 
possibly missing a good solution. If the velocity is too small, then the particle may
get trapped in a local minimum.

The PSO parameters play a vital role in achieving a good solution in a problem space.
How fast we converge to a solution completely depends on the chosen parameters.
Parameters a, b and c are crucial in calculating a particles new velocity, and 
the number of particles n also affects the convergence rate, since if there are more particles
trying to find a solution, then the chance of finding it is higher. But that comes at the 
computational cost, as we have to iterate over each particle and update its velocity and new position in each iteration.
To determine these parameters, we could simply run trial and error experiments.


Gradient descent:
Gradient descent is a minimization algorithm, that tries to minimize a given function.
We can think of the gradient as a vector that tells us the direction of the slope at a certain point in a function. 

b = a - gamma * derivitive f(a) 
where b is the next position, a is our current position, gamma represents the learning rate
and the gradient term represents the direction of the steepest descent.


For example, let's imagine we have a function that we want to minimize with two parameters, 
theta1 and theta2.
In gradient descent, we initialize those two parameters with random values and then we try to 
minimize the cost function J(theta1, theta2) and reach a local minimum by changing the parameters. We start at the initial point and apply the gradient descent in each iteration, 
so that we take one step in the steepest direction of the slope (downside direction), until 
we reach a point, where the cost function is smaller than our error allows.

The most important parameter of gradient descent is the learning rate. If it's too high, 
than we may never reach the local minimum as it would bounce between the convex function of
gradient descent, but if its too low, than the convergance to the minimum will be very slow.


## Use simulations to convince a customer/project leader/colleague of the pros and cons of PSO







## Find out if it makes sense to combine PSO and gradient descent

PSO searches randomly through the space while gradient descent uses the information 
about the gradient of the surface to find its next step towards the minimum.

PSO basically does global random search, so it wastes some computation power while gradient descent is a deterministic algorithm that quickly converges, but may get stuck in a local minimum of complex non-convex functions.

We can look at it from a exploration vs exploitation problem.
PSO basically explores the function, while gradient descent exploits the information about 
it.

We could combine the strenghts of both of these by applying gradient descent to each particle 
after every iteration, but that would be quite computationally expensive and it also might 
present a problem, as if the particle would be in a local minimum after moving towards
the Gbest, than the gradient descent would move it backwards.

A better solution may be to apply gradient descent only to the best particle. That would allow 
for a faster convergence to a global minimum, as the best particle wouldn't just randomly explore the space, but also use the information about the gradient.
