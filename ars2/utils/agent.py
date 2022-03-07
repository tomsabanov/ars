import math
import numpy as np

from utils.motion_model import MotionModel
from utils.sensor_model import SensorModel

from utils.object import Object
from utils.vector import Vector, Point

import sys



class Agent():
    def __init__(self, map = None, radius = 50, start_pos_index = None, max_vision=100, ann = None, max_speed = 3.0):
        if map == None or radius == None or start_pos_index == None:
            print("SPECIFY MAP, RADIUS AND START_POS_INDEX FOR AGENT!")
            sys.exit()

        self.position = map["start_points"][start_pos_index]
        self.theta = 0
        self.radius = radius
        self.max_vision = max_vision
        self.max_speed = max_speed

        self.fitness = 0


        self.map = map

        self.motion_model = MotionModel(self.radius * 2, self.map["map"])
        self.sensor_model = SensorModel(self.position, self.theta, self.radius,
                                        self.map["map"],12,self.max_vision)

        # Radius Bound is a horizontal vector
        self.circleObject = Object(self.position, [Vector(Point(0, 0), Point(self.radius, 0))], type="circle")

        # Create object line that will serve as vision. By default we put the cast to be twice the agent's radius
        self.lineObject = Object(self.position, [Vector(Point(0, 0), Point(self.radius, 0))], type="line")

        self.speed_increment = 1
        self.agent_actions = {
            "w": (self.motion_model.update_speed, [self.speed_increment, 0]),
            "s": (self.motion_model.update_speed, [-self.speed_increment, 0]),
            "o": (self.motion_model.update_speed, [0, self.speed_increment]),
            "l": (self.motion_model.update_speed, [0, -self.speed_increment]),
            "x": (self.motion_model.reset_speed, []),
            "t": (self.motion_model.update_speed, [self.speed_increment, self.speed_increment]),
            "g": (self.motion_model.update_speed, [-self.speed_increment, -self.speed_increment]),
        }

        self.ann = ann


    def get_map(self):
        return self.map


    def ann_controller_run(self):
        # Get sensor distances 
        sensor_distances = self.sensor_model.get_sensor_distances()

        # Run the ann and get the output
        (l, r) = self.ann.run_network(sensor_distances)
        
        # Above 0.5, speed is positive, under 0.5 speed is negative
        c = 0.5

        vl = (abs(l-c)/c)*self.max_speed
        vr = (abs(r-c)/c)*self.max_speed

        if l<c:
            vl = -vl
        if r<c:
            vr = -vr

        self.motion_model.set_speed(vl,vr)    

    def set_speed(self, vr, vl):
        self.motion_model.update_speed(vr, vl)

    # This loop will be the agent's own controller
    # The ANN will be controlled from here
    def loop_agent(self, timesteps):
        output = self.motion_model.get_speeds()
        for i in range(timesteps):
            print("- Iteration " + str(i))

            input_layer = []
            for d in self.sensor_model.get_sensor_distances():
                input_layer.append(d)
            input_layer.append(output[0])
            input_layer.append(output[1])

            print(input_layer)


            output = self.ann.forward_propagation(input_layer)
            left_motor = output[0]
            right_motor = output[1]
            print(output)

            # Move backward, forward, or nothing
            if left_motor < 0.5:
                self.move_agent("l")
            else:
                self.move_agent("o")

            if right_motor < 0.5:
                self.move_agent("s")
            else:
                self.move_agent("w")

            self.update()


            # Increment metrics for Fitness function here such as amount of dust sucked:
            if len(self.motion_model.get_collisions()) == 0: # and left_motor > 0 and right_motor > 0:
                print("UPDATE FITNESS")
                self.fitness = self.fitness + 1




    # Passes an action parameter to move the agent according to the output weights of the ANN
    def move_agent(self, action):
        if action == "w":
            self.motion_model.update_speed(self.speed_increment, 0)
        elif action == "s":
            self.motion_model.update_speed(-self.speed_increment, 0)
        elif action == "o":
            self.motion_model.update_speed(0, self.speed_increment)
        elif action == "l":
            self.motion_model.update_speed(0, -self.speed_increment)
        elif action == "x":
            self.motion_model.update_speed()
        elif action == "t":
            self.motion_model.update_speed(self.speed_increment, self.speed_increment)
        elif action == "g":
            self.motion_model.update_speed(-self.speed_increment, -self.speed_increment)

    def set_network_weights(self, network):
        self.network = self.ann.initialize_network(network)

    def get_circle_coordinates(self):
        return self.position

    def get_line_coordinates(self):
        return self.lineObject.get_ui_coordinates()

    def get_vision_lines(self):
        lines = self.sensor_model.get_sensor_lines()
        dist = self.sensor_model.get_sensor_distances()
        return (lines, dist)

    def is_agent_moving(self):
        return self.motion_model.is_moving()

    def get_speeds(self):
        return self.motion_model.get_speeds()

    def update_agent_objects(self, new_position, new_theta):
        # Update agent line
        self.lineObject.update_coordinates(new_position)
        if new_theta != self.theta:
            self.lineObject.rotate(new_theta)

        # Update agent circle 
        self.circleObject.update_coordinates(new_position)

    def update(self):
        # Update motion model
        (new_position, new_theta, change) = self.motion_model.update(self.position, self.theta)
        
        # If there is no change in movement, then just skip the update
        if change == False:
            return
        self.update_agent_objects(new_position, new_theta)


        # Update the sensor model
        self.sensor_model.update(new_position, new_theta)

    
        self.theta = new_theta
        self.position = new_position

        print(self.position.X)

    def on_key_press(self, key):
        # React to the key press
        try:
            action, args = self.agent_actions[key]
            action(*args)
        except Exception:
            # ignore it
            pass
