import numpy as np
import sys
import math


class Dense:
    def __init__(self, input, output):
        self.weights = np.random.rand(output,input)
        self.bias = np.ones(output)

        self.shape = self.weights.shape

        self.output = np.zeros(output)
    
    def get_structure(self):
        return self.shape

    def forward_propagate(self,input):
        self.output = self.weights.dot(input)
        self.output = np.add(self.output, self.bias)

        # apply activation
        self.output = np.array([self.sigmoid(o) for o in self.output])

        return self.output
    
    def set_weights(self, weights):
        if self.shape != weights.shape:
            print("Error! Shape of weights is wrong!")
            sys.exit()
        self.weights = weights


    def sigmoid(self, x):
        sig = 1 / (1 + np.exp(-x))     # Define sigmoid function
        sig = np.minimum(sig, 0.9999999)  # Set upper bound
        sig = np.maximum(sig, 0.0000001)  # Set lower bound
        return sig


class Network:
    def __init__(self, layers=None):
        self.layers = layers
    
    def get_layers(self):
        return self.layers
        
    def set_weights(self, weights):
        i = 0 
        for layer in self.layers:
            layer.set_weights(weights[i])
            i = i+1

    def get_structure(self):
        structure = list()
        for layer in self.layers:
            structure.append(layer.get_structure())
        return structure
        
    def run_network(self, sensor_values):
        output = sensor_values
        for i in range(len(self.layers)):
            layer = self.layers[i]

            if i == 0:
                # Get previous output and add it to the input
                prev_out = layer.output
                output = np.concatenate((output, prev_out))

            # Forward propagate
            output = layer.forward_propagate(output)

        return output



