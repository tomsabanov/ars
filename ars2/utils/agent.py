import math
import numpy as np

from utils.motion_model import MotionModel
from utils.object import Object
from utils.vector import Vector, Point

from shapely.geometry import LineString

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

            # Check if line is intersecting 
            # (valid, I, wall) = self.calculate_sensor_collision(l)
                
            self.sensors.append(l)
            i = i + math.radians(angle)
        

    def get_sensor_lines(self):
        coords = []
        for s in self.sensors:
            coords.append(s.get_ui_coordinates())
        return coords
    
    def distance_between_points(self,p1,p2):
        dist = math.sqrt((p2.X - p1.X)**2 + (p2.Y - p1.Y)**2)
        return dist

    def update(self, new_position, new_theta):
        self.sensors = []
        angle = 360/self.num_sensors

        #TODO: backwards motion -> theta should be negative probably -> needs experimentation
        t = new_theta

        # TODO: This could be done better - instead of creating a new line 
        # we could just update the existing ones......
        i = math.radians(0)
        while i < 360:
            # Calculate the line for every angle and append it to sensors
            P1 = Point(self.radius * math.cos(i+t), self.radius*math.sin(i+t))
            P2 = Point((self.max_vision+self.radius) * math.cos(i+t), (self.max_vision+self.radius)*math.sin(i+t))
            l = Object(new_position, [Vector(P1, P2)], type="line")

            lc = l.get_ui_coordinates()

            # Check if line is intersecting 
            (valid, I, wall) = self.calculate_sensor_collision(l)
            if valid == True:
                # we must adjust the length
                dist = self.distance_between_points(lc.P2, I)
                P2 = Point((self.max_vision+self.radius - dist) * math.cos(i+t), (self.max_vision+self.radius - dist)*math.sin(i+t))
                l = Object(new_position, [Vector(P1, P2)], type="line")

            self.sensors.append(l)
            i = i + math.radians(angle)
        
        self.position = new_position
        self.theta = new_theta
    

    def calculate_sensor_collision(self, sensor_line):
        # TODO: This algorithm is bad in terms of complexity -> O(n^2)
        # Could be done better with a Sweep Line Algorithm -> O(nlogn)

        sensor_coords = sensor_line.get_ui_coordinates()
        A = sensor_coords.P1
        B = sensor_coords.P2

        for m in self.map:
            coords = m.get_ui_coordinates()
            C = coords.P1
            D = coords.P2

            line1 = LineString([(A.X,A.Y), (B.X,B.Y)])
            line2 = LineString([(C.X,C.Y), (D.X,D.Y)])
            
            I = line1.intersection(line2)
            if not I.is_empty:
                c = I.coords[:]
                new_point = Point(c[0][0], c[0][1])
                return (True, new_point, m.get_ui_coordinates())

        return (False,None, None)





class Agent():
    def __init__(self, center, radius, map):
        self.position = center
        self.theta = 0
        self.radius = radius

        self.map = map

        self.motion_model = MotionModel(self.radius*2)
        self.sensor_model = SensorModel(self.position, self.theta, self.radius,
                                        self.map,6,100)

        # Radius Bound is a horizontal vector
        self.circleObject = Object(self.position, [Vector(Point(0,0), Point(self.radius, 0))], type="circle")

        # Create object line that will serve as vision. By default we put the cast to be twice the agent's radius
        self.lineObject = Object(self.position, [Vector(Point(0,0), Point(self.radius, 0))], type="line")



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

