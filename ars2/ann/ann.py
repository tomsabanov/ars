from random import uniform, random, randrange
import numpy as np
import copy


class Neural_Network():
    def __init__(self):

        self.network = list()
        self.bias = 0

    # Create network with two layers. Use o
    def initialize_random_network(self, inputs_l: int, output_l: int):
        # one extra input is the bias node
        layer = [{'weights': [uniform(-1, 1) for i in range(inputs_l + 1)]} for i in range(output_l)]
        self.network.append(layer)
        print('network :')
        print(layer)
        return self.network

    def initialize_network(self, network):
        self.network = network
        print("new network")
        print(network)
        return self.network

    def mutate_genes(self):
        mutation_coef = 0.025   # By amount we can increment
        mutation_rate = 0.2     # Percentage of weights updated
        network = list()
        for layer in self.network:
            layer_list = []
            for weight in layer:
                weight_list = []

                for n in weight['weights']:
                    if randrange(0,100) / 100 <= mutation_rate:
                        if randrange(0,1) == 0:
                            weight_list.append(n - mutation_coef)
                        else:
                            weight_list.append(n + mutation_coef)

                layer_list.append({'weights': weight_list})
            network.append(layer)
        self.network = network

    def sigmoid(self, activation):
        return 1.0 / (1.0 + np.exp(-activation))

    def activate(self, weights, inputs):  # Calculate neuron activation for an input,
        # Bias term is added and is assumed that it is the last entry
        if len(inputs) < len(weights):
            extended_input = copy.deepcopy(inputs)
            extended_input.append(1)
        else:
            extended_input = copy.deepcopy(inputs)

        activation = np.dot(weights, extended_input)

        # Compute sigmoid
        activation = self.sigmoid(activation)
        return activation

    # Forward propagate input to a network output
    def forward_propagation(self, inputs):

        for layer in self.network:
            activation_layer = []  # Get the input result of intermediate layer
            for neuron in layer:
                activation_value = self.activate(np.array(neuron['weights']), inputs)
                activation_layer.append(activation_value)

            inputs = activation_layer

        return inputs  # In the last iteration, becomes the output

    # Calculate the derivative of an neuron output, output is sigmoid result
    def sigmoid_derivative(self, output):
        return output * (1.0 - output)
