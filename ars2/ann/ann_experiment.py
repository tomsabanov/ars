from ann import Neural_Network



class Training():
    def __init__(self, population_size, iterations):
        self.population_size = population_size
        self.iterations = iterations



    #def generate_agents(self):
    #    for i in range(self.population_size):
    #





if __name__ == '__main__':
    NN = Neural_Network()

    # Create a network with 12 input nodes for the sensors and 2 outputs nodes for the motors
    network = NN.initialize_random_network(12, 2)