import sys
import pygame
import time
import json
import numpy as np

from pygame.locals import (
    K_UP,
    K_DOWN,
    K_LEFT,
    K_RIGHT,
    K_ESCAPE,
    KEYDOWN,
    QUIT,
)

from utils.agent import Agent
from utils.map import read_map
from ann import Dense, Network

class Settings:
    def __init__(self, w=1024, h=1024, margin=0):
        self.BOARD_WIDTH = w
        self.BOARD_HEIGHT = h
        self.MARGIN = margin

class Simulation():

    def __init__(self,  map = None,
                        agent = None, 
                        time = None, 
                        render = True,
                        simulation=False,
                        time_step = 100,
                        weights = None
                        ):
        self.map = map
        self.sett = Settings()

        self.agent = agent
        self.time = time # simulation runtime
        self.render = render
        self.simulation = simulation
        self.time_step = time_step
        self.counter = 0

        self.weights = weights

        self.clock = pygame.time.Clock()

        pygame.init()

        if self.render:

            pygame.font.init()
            self.font = pygame.font.SysFont('Comic Sans MS', 30)
            self.textsurface = self.font.render('Some Text', False, (0, 0, 0))

            self.screen = pygame.display.set_mode((self.sett.BOARD_WIDTH,
                                                self.sett.BOARD_HEIGHT))
            pygame.display.set_caption("Agent")
            self.screen.fill((255, 255, 255))


        self.setup()


    def simulate(self):
        if self.time == None:
            while 1:
                self.loop()
        else:
            t_end = time.time() + self.time
            while time.time() < t_end:
                self.loop()

        return self.agent

    def setup(self):
        # Setup the UI/agent

        if self.agent == None:
            self.setup_agent()
        else:
            self.map = self.agent.get_map()


    def setup_agent(self):
        # Setup the agent and his canvas objects
        self.agent = Agent(
                        map = self.map,
                        radius = 50, 
                        start_pos_index = 0
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
        self.ttime = self.clock.tick(100)


    def simulationEventLoop(self):
        # Update motor values from ANN
        # This has to be done every time step
        if self.counter == self.time_step:
            print("Updating controller!")
            self.agent.ann_controller_run()
            self.counter = 0

        self.agent.update()

    def loop(self):            
        if self.simulation == False:
            self.eventLoop()
        else:
            self.simulationEventLoop()

        self.tick()
        if self.render:
            self.draw()
            pygame.display.update()

        self.counter = self.counter + 10

    def draw(self):
        self.screen.fill((255,255,255))

        # Draw the map
        for l in self.map["map"]:
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


def main():
    map_path = "./train_maps/map_3"
    map = read_map(map_path)

    simulation = False
    time_step = 100
    agent = None
    render = True
    if len(sys.argv)>1:
        weigth_file = sys.argv[1]
        f = open(weigth_file, 'r')
        js = json.load(f)

        # Create the agent with the specified ann
        net_struct = js['nn_structure']
        weights = json.loads(js['weights'])

        layers = []
        W = []
        for i in range(len(net_struct)):
            s = net_struct[i]
            layers.append(
                Dense(s[1], s[0])
            )
            w = np.array(weights[i])
            W.append(w)
        # Create the network with the specified layers
        ann = Network(layers)
        ann.set_weights(W)

        agent = Agent(
                    map = map,
                    start_pos_index = 0,
                    max_vision = 500,
                    ann = ann,
                    max_speed = 3.0
                )
        simulation = True

    ui = Simulation(map=map, 
                    agent=agent, 
                    simulation=simulation, 
                    time_step=time_step,
                    render=render
                    )
    ui.simulate()

if __name__ == '__main__':
    main()
