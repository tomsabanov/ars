import math
import numpy as np

from utils.motion_model import MotionModel
from utils.object import Object
from utils.vector import Vector, Point


class SensorModel():
    def __init__(self, position, theta, radius, map, num_sensors=12, max_vision=100):
        self.position  = position
        self.theta = theta
        self.radius = radius
        self.map = map

        self.num_sensors = num_sensors
        self.max_vision = max_vision

        self.sensors = []
        self.init_sensors()

    def init_sensors(self):
        angle = 360/self.num_sensors

        i = math.radians(0)
        while i < 360:
            # Calculate the line for every angle and append it to sensors
            P1 = Point(self.radius * math.cos(i), self.radius*math.sin(i))
            P2 = Point(self.max_vision * math.cos(i), self.max_vision*math.sin(i))
            l = Object(self.position, [Vector(P1, P2)], type="line")

            self.sensors.append(l)
            i = i + math.radians(angle)

    def get_sensor_lines(self):
        coords = []
        for s in self.sensors:
            coords.append(s.get_ui_coordinates())
        return coords
    

    def update(self, new_position, new_theta):
        self.sensors = []
        angle = 360/self.num_sensors

        #TODO: backwards motion -> theta should be negative
        t = new_theta

        # TODO: This could be done better - instead of creating a new line 
        # we could just update the existing ones......
        i = math.radians(0)
        while i < 360:
            # Calculate the line for every angle and append it to sensors
            P1 = Point(self.radius * math.cos(i+t), self.radius*math.sin(i+t))
            P2 = Point(self.max_vision * math.cos(i+t), self.max_vision*math.sin(i+t))
            l = Object(new_position, [Vector(P1, P2)], type="line")

            self.sensors.append(l)
            i = i + math.radians(angle)
        
        self.position = new_position
        self.theta = new_theta
        


class Agent():
    def __init__(self, center, radius, map):
        self.position = center
        self.theta = 0
        self.radius = radius

        self.map = map

        self.motion_model = MotionModel(self.radius*2)
        self.sensor_model = SensorModel(self.position, self.theta, self.radius,
                                        self.map,12,100)

        # Radius Bound is a horizontal vector
        self.circleObject = Object(self.position, [Vector(Point(0,0), Point(self.radius, 0))], type="circle")

        # Create object line that will serve as vision. By default we put the cast to be twice the agent's radius
        self.lineObject = Object(self.position, [Vector(Point(0,0), Point(self.radius*2, 0))], type="line")



        self.speed_increment = 10
        self.agent_actions = {
            "w": (self.motion_model.update_speed, [self.speed_increment, 0]),
            "s": (self.motion_model.update_speed, [-self.speed_increment, 0]),
            "o": (self.motion_model.update_speed, [0, self.speed_increment]),
            "l": (self.motion_model.update_speed, [0, -self.speed_increment]),
            "x": (self.motion_model.reset_speed, []),
            "t": (self.motion_model.update_speed, [self.speed_increment, self.speed_increment]),
            "g": (self.motion_model.update_speed, [-self.speed_increment, -self.speed_increment]),
        }


    def get_circle_coordinates(self):
        return self.circleObject.get_ui_coordinates()
    def get_line_coordinates(self):
        return self.lineObject.get_ui_coordinates()
    def get_vision_lines(self):
        return self.sensor_model.get_sensor_lines()



    def update_agent_objects(self, new_position, new_theta):
        # Update agent line
        self.lineObject.update_coordinates(new_position)
        if new_theta != self.theta:
            self.lineObject.rotate(new_theta)

        # Update agent circle 
        self.circleObject.update_coordinates(new_position)


    def update(self):
        # Update motion model
        (new_position, new_theta) = self.motion_model.update_position(self.position, self.theta)
        self.update_agent_objects(new_position, new_theta)

        # Update the sensor model
        self.sensor_model.update(new_position, new_theta)

        
        self.theta = new_theta
        self.position = new_position



    def on_key_press(self, key):
        # React to the key press
        try:
            action, args = self.agent_actions[key]
            action(*args)
        except Exception:
            # ignore it
            pass

