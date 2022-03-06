import sys
import pygame
import json
from shapely.geometry import Polygon

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
    def __init__(self, w=1024, h=1024, margin=0, render=True):
        self.BOARD_WIDTH = w
        self.BOARD_HEIGHT = h
        self.MARGIN = margin
        self.render = render

class Simulation():

    def __init__(self, map_path, sett: Settings):
        self.sett = sett
        self.map_path = map_path

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


    def simulate(self):
        while 1:
            self.loop()

    def setup(self):
        # Setup the UI/agent
        self.setup_map()
        self.setup_agent()


    def setup_map(self):
        # Read the map from map_path
        f = open(self.map_path, "r")
        map = f.read()
        map = map.split("\n")
        length_poly = len(map)-1

        # Map[0] should contain the exterior box of the map
        j = json.loads(map[0])



        self.map = []
        for i in range(length_poly):
            poly = json.loads(map[i])
            print(poly)

            poly_len = len(poly) - 1
            for i in range(poly_len):
                c1 = poly[i]
                c2 = poly[i+1]
                self.map.append(
                    Object(Point(c1[0], c1[1]), [
                        Vector(Point(0,0), Point(c2[0]-c1[0], c2[1] - c1[1]))
                    ], type="line")
                )

            c1 = poly[0]
            c2 = poly[len(poly)-1]
            self.map.append(
                Object(Point(c1[0], c1[1]), [
                    Vector(Point(0,0), Point(c2[0]-c1[0], c2[1] - c1[1]))
                ], type="line")
            )


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



def main():
    settings = Settings()

    map_path = "./map/map_2"
    ui = Simulation(map_path,settings)
    ui.simulate()

if __name__ == '__main__':
    main()
