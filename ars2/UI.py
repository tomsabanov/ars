import sys
import pygame

from pygame.locals import (
    K_UP,
    K_DOWN,
    K_LEFT,
    K_RIGHT,
    K_ESCAPE,
    KEYDOWN,
    QUIT,
)

from utils.object import Object
from utils.vector import Vector, Point
from utils.agent import Agent


class Settings:
    def __init__(self, w=800, h=800, margin=0):
        self.BOARD_WIDTH = w
        self.BOARD_HEIGHT = h
        self.MARGIN = margin

class UI():

    def __init__(self, sett: Settings):
        #super().__init__(width=sett.BOARD_WIDTH+sett.MARGIN*2, height=sett.BOARD_HEIGHT + sett.MARGIN*2,
        #    background="white", highlightthickness=0)
        self.sett = sett
        self.clock = pygame.time.Clock()


        pygame.init()
        pygame.font.init()
        self.font = pygame.font.SysFont('Comic Sans MS', 30)
        self.textsurface = self.font.render('Some Text', False, (0, 0, 0))

        self.screen = pygame.display.set_mode((sett.BOARD_WIDTH,
                                            sett.BOARD_HEIGHT))
        pygame.display.set_caption("Agent")
        self.screen.fill((255, 255, 255))


        self.setup()


    def show_UI(self):
        while True:
            self.loop()

    def setup(self):
        # Setup the UI/agent
        self.setup_map()
        self.setup_agent()


    def setup_map(self):
        # TODO: Map should be a hollow polygon, it should also be read from a file
        #       and scaled appropriately to the dimensions of the UI
        self.map = [
            Object(Point(100,100), [Vector(Point(0,0),Point(500,0))], type="line"),
            Object(Point(600,100), [Vector(Point(0, 0), Point(0, 500))], type="line"),
            Object(Point(100, 600), [Vector(Point(0, 0), Point(500, 0))], type="line"),
            Object(Point(100, 100), [Vector(Point(0, 0), Point(0, 500))], type="line"),
        ]



    def setup_agent(self):
        # Setup the agent and his canvas objects
        self.agent = Agent(Point(
                            int(self.sett.BOARD_WIDTH/2), 
                            int(self.sett.BOARD_HEIGHT/2)
                            ),
                            50,
                            self.map
                    )

    def eventLoop(self):
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                self.agent.on_key_press(event.unicode)
        self.agent.update()

    def tick(self):
        self.ttime = self.clock.tick(120)

    def loop(self):            
        self.eventLoop()
        self.tick()
        self.draw()
        pygame.display.update()


    def draw(self):
        self.screen.fill((255,255,255))

        # Draw the map
        for l in self.map:
            c_coords = l.get_ui_coordinates()
            p1 = (c_coords.P1.X, c_coords.P1.Y)
            p2 = (c_coords.P2.X, c_coords.P2.Y)
            pygame.draw.line(self.screen, [0, 0, 0], p1, p2)
        

        # Draw the agent
        pos = self.agent.get_circle_coordinates()
        c = (pos.X, pos.Y)
        pygame.draw.circle(self.screen, [255,0,0], c, self.agent.radius)


        # Draw agent orientation line
        l_coords = self.agent.get_line_coordinates()
        p1 = (l_coords.P1.X, l_coords.P1.Y)
        p2 = (l_coords.P2.X, l_coords.P2.Y)
        pygame.draw.line(self.screen, [0, 0, 0], p1, p2)


        
        # Draw sensor lines
        (vision_lines, distances) = self.agent.get_vision_lines()
        self.agent_vision_lines = []
        self.agent_distances = []
        i = 0
        for l in vision_lines:
            p1 = (l.P1.X, l.P1.Y)
            p2 = (l.P2.X, l.P2.Y)
            pygame.draw.line(self.screen, [0, 0, 0], p1, p2)

            textsurface = self.font.render(str(distances[i]), False, (0, 0, 0))
            self.screen.blit(textsurface,p1)
            i = i+1

             
        (left_speed, right_speed) = self.agent.get_speeds()
        tl = "Left motor speed: " + str(left_speed)
        tr = "Right motor speed: " + str(right_speed)
        textsurface = self.font.render(tl, False, (0, 0, 0))
        self.screen.blit(textsurface,(350,30))
        textsurface = self.font.render(tr, False, (0, 0, 0))
        self.screen.blit(textsurface,(350,50))


    def self_agent_weights(self, network):
        self.agent.set_network_weights(network)


def train_agents():
    generations = 5
    population = 20
    best_fitness = -1
    result_previous_generation = []

    # Creates initial population for starting:
    for i in range(population):
        settings = Settings()
        ui = UI(settings)

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
            ui = UI(settings)

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



def main():
    settings = Settings()
    ui = UI(settings)
    ui.show_UI()

if __name__ == '__main__':
    main()
    #train_agents()