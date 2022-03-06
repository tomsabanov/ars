import sys
import pygame
import json
import time

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
    def __init__(self, w=1024, h=1024, margin=0):
        self.BOARD_WIDTH = w
        self.BOARD_HEIGHT = h
        self.MARGIN = margin

class Simulation():

    def __init__(self,  map = None, map_path = "./train_maps/map_1", 
                        agent = None, 
                        time = None, 
                        render = True,
                        simulation=False,
                        time_step = None
                        ):
        self.map_path = map_path
        self.map = map
        self.sett = Settings()

        self.agent = agent
        self.time = time # simulation runtime
        self.render = render
        self.simulation = simulation
        self.time_step = time_step
        self.counter = 0

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


    def setup(self):
        # Setup the UI/agent

        if self.agent == None:
            self.setup_map()
            self.setup_agent()
        else:
            self.map = self.agent.get_map()


    def setup_map(self):
        # Read the map from map_path
        f = open(self.map_path, "r")
        map = f.read()
        map = map.split("\n")
        map.pop()
        length_poly = len(map)-1

        # Map[0] should contain the exterior box of the map
        j = json.loads(map[0])

        # Last element in map should contain an array of possible starting points
        # for the agents

        self.map = {
            "map" : [],
            "start_points" : []
        }
        for i in range(length_poly):
            poly = json.loads(map[i])

            poly_len = len(poly) - 1
            for i in range(poly_len):
                c1 = poly[i]
                c2 = poly[i+1]
                self.map["map"].append(
                    Object(Point(c1[0], c1[1]), [
                        Vector(Point(0,0), Point(c2[0]-c1[0], c2[1] - c1[1]))
                    ], type="line")
                )

            c1 = poly[0]
            c2 = poly[len(poly)-1]
            self.map["map"].append(
                Object(Point(c1[0], c1[1]), [
                    Vector(Point(0,0), Point(c2[0]-c1[0], c2[1] - c1[1]))
                ], type="line")
            )
        
        sp = json.loads(map[len(map) - 1])
        for p in sp:
            self.map["start_points"].append(
                Point(p[0],p[1])
            )

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
    ui = Simulation(map_path = map_path)
    ui.simulate()

if __name__ == '__main__':
    main()
