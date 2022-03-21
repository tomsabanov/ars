import sys
import pygame
import time
import argparse
import math
import json


from pygame.locals import (
    K_ESCAPE,
    KEYDOWN,
    QUIT,
)

from utils.agent import Agent
from utils.map import read_map
from ann import Dense, Network, get_network

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
                        time_step = 100,
                        weights = None,
                        max_vision=100,
                        max_speed=2.0,
                        speed_increment=1.0,
                        radius=50,
                        localization = False,
                        time_tick = 100,
                        time_s = 0.1,
                        sensors = True,
                        ):
        self.map = map
        self.sett = Settings()

        self.time_tick = time_tick


        self.time = time # simulation runtime
        self.render = render # should an UI be rendered?
        self.time_step = time_step # time step for the agent update
        self.counter = 0
        self.time_s = time_s

        self.sensors = sensors

        # Vision/Speed/Radius properties of an agent
        self.max_vision = max_vision
        self.max_speed = max_speed
        self.speed_increment = speed_increment
        self.radius = radius

        # For simulating an agent with an ANN
        self.weights = weights

        # For enabling/disabling localization
        self.localization = localization


        self.agent = agent
        self.simulation = True # Used for knowing whether or not to let ANN take control or keyboard
        if(self.agent == None):
            self.simulation=False
            self.setup_agent()


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


    def setup_agent(self):
        # Setup the agent and his canvas objects
        self.agent = Agent(
                        map = self.map,
                        radius = self.radius, 
                        start_pos_index = 0,
                        max_vision=self.max_vision,
                        max_speed =self.max_speed,
                        localization = self.localization,
                        time_step = self.time_step,
                        speed_increment=self.speed_increment,
                        time_s = self.time_s
                    )

    def simulate(self):
        if self.time == None:
            while 1:
                self.loop()
        else:
            t_end = time.time() + self.time
            while time.time() < t_end:
                self.loop()

        return self.agent

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


    def draw_localization(self):
        # Draw the localization of the agent

        # Draw the features on the map
        for f in self.map["features"]:
            p = (f.X, f.Y)
            pygame.draw.circle(self.screen, [0,0,255], p, 10)
        

        # Draw visible features lines
        vis_feat = self.agent.localization.get_visible_features()
        pos = self.agent.get_circle_coordinates()
        c = (pos.X, pos.Y)
        for g in vis_feat:
            (f,d) = g
            p = (f.X, f.Y)
            pygame.draw.line(self.screen, [0, 0, 255], p, c)

        # Draw predicted poses
        (pred_poses, pred_sigmas) = self.agent.localization.get_predicted()
        for p in pred_poses:
            p = p.tolist()
            p = (p[0][0], p[0][1])
            pygame.draw.circle(self.screen, [0,255,0], p, 3)
        
        # Draw corrected poses
        (pred_poses, pred_sigmas) = self.agent.localization.get_corrected()
        for p in pred_poses:
            p = p.tolist()
            p = (p[0][0], p[0][1])
            pygame.draw.circle(self.screen, [255,0,0], p, 3)
        

            


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

        if(self.sensors):
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


        if self.localization:
            self.draw_localization()
        

def main():

    parser = argparse.ArgumentParser(description='Simulate an agent.')
    parser.add_argument('--map', action='store', default='./train_maps/map_1', 
                        help='Path to the map you want to simulate.')
    parser.add_argument('--render', action=argparse.BooleanOptionalAction, default=True,
                        help='If you want to render or not the simulation.')
    parser.add_argument('--time', action='store', default=math.inf, type=float,
                        help='Amount of time the simulation runs. Default is inf.')
    parser.add_argument('--time_step', action='store', default=10, type=int,
                        help='Time step for agent update. Default is 100ms')
    parser.add_argument('--time_tick', action='store', default=100, type=int,
                        help='Number of times the agent refreshes each second. Default is 100.')
    parser.add_argument('--weights', action='store', 
                        help='Path to weights folder to simulate the agent.')
    parser.add_argument('--max_vision', action='store', default=100, type=int,
                        help='Max vision of the agent sensors.'),
    parser.add_argument('--radius', action='store', default=50, type=int,
                        help='Radius of the agent'),
    parser.add_argument('--max_speed', action='store', default=2.0, type=float,
                        help='Max speed of the agent.'),
    parser.add_argument('--speed_increment', action='store', default=0.2, type=float,
                        help='Speed increment of the agent.'),
    parser.add_argument('--localization', action=argparse.BooleanOptionalAction, 
                        default=False,
                        help='Enable/Disable localization'),
    parser.add_argument('--sensors', action=argparse.BooleanOptionalAction, 
                        default=True,
                        help='Enable/Disable sensors'),                           
    args = parser.parse_args()


    map = read_map(args.map,0)
    agent = None

    perc = args.time_step/1000
    time_step = int(perc * args.time_tick)
    if(args.weights is not None):
        ann = get_network(args.weights)
        agent = Agent(
                    map = map,
                    start_pos_index = 0,
                    max_vision = args.max_vision,
                    max_speed = args.max_speed,
                    radius = args.radius,
                    ann = ann,
                    localization = args.localization,
                    time_step = time_step,
                    time_s = perc,
                    speed_increment=args.speed_increment,
                    sensors = args.sensors
        )


    ui = Simulation(map=map, 
                    agent=agent, 
                    render=args.render,
                    max_vision=args.max_vision,
                    max_speed = args.max_speed,
                    radius = args.radius,
                    localization = args.localization,
                    time_tick = args.time_tick,
                    time_step= time_step,
                    time = args.time,
                    time_s = perc,
                    speed_increment = args.speed_increment,
                    sensors = args.sensors
                    )
    ui.simulate()


if __name__ == '__main__':
    main()
