from Simulation import Simulation, Settings


def train_agents():
    generations = 5
    population = 20
    best_fitness = -1
    result_previous_generation = []
    map_path = "./map/map_3"


    # Creates initial population for starting:
    for i in range(population):
        settings = Settings()
        ui = Simulation(map_path, settings)

        ui.agent.loop_agent(1)

        # Compute fitness function here
        # To implement
        if ui.agent.fitness > best_fitness:
            # Get genome here to store in results_generation
            genome = ui.agent.network
            result_previous_generation.append(genome)
            best_fitness = ui.agent.fitness

    for i in range(generations):
        results_generation = []


        for j in range(population):
            settings = Settings()
            ui = Simulation(map_path, settings)

            # Do creation of individuals here:

            # Set previous weights:
            ui.self_agent_weights(result_previous_generation[0])

            ui.agent.ann.mutate_genes()

            ui.agent.loop_agent(20)

            # Compute fitness function here
            # To implement
            if ui.agent.fitness >= best_fitness:
                # Get genome here to store in results_generation
                genome = ui.agent.network
                results_generation.append(genome)
                best_fitness = ui.agent.fitness

        # Do selection for next iteration here:
        result_previous_generation = results_generation


    print("results:")
    for r in result_previous_generation:
        print(r)


    f = open("best_weights.txt", "w")
    f.write(str(result_previous_generation[0]))

    print("best fitness: " + str(best_fitness))

if __name__ == '__main__':
    train_agents()