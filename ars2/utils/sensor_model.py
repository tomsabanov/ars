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
        self.distances = []

        self.init_sensors()

    def init_sensors(self):
        angle = 360/self.num_sensors

        j = 0
        i = math.radians(0)
        while i < math.pi * 2:
            # Calculate the line for every angle and append it to sensors
            P1 = Point(self.radius * math.cos(i), self.radius*math.sin(i))
            P2 = Point(self.max_vision * math.cos(i), self.max_vision*math.sin(i))
            l = Object(self.position, [Vector(P1, P2)], type="line")

            # Check if line is intersecting 
            # (valid, I, wall) = self.calculate_sensor_collision(l)
            self.distances.append(-1)
                
            self.sensors.append(l)
            i = i + math.radians(angle)
            j = j + 1
        

    def get_sensor_lines(self):
        coords = []
        for s in self.sensors:
            coords.append(s.get_ui_coordinates())
        return coords

    def get_sensor_distances(self):
        return self.distances
    
    def distance_between_points(self,p1,p2):
        dist = math.sqrt((p2.X - p1.X)**2 + (p2.Y - p1.Y)**2)
        return dist


    def update(self, new_position, new_theta):
        self.sensors = []
        angle = 360/self.num_sensors

        t = new_theta

        # TODO: This could be done better - instead of creating a new line 
        # we could just update the existing ones......
        i = math.radians(0)
        j = 0
        while i < math.pi * 2:
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

                dist_to_wall = round(self.distance_between_points(lc.P1, I),1)
                self.distances[j] = dist_to_wall
            else:
                self.distances[j] = -1000


            self.sensors.append(l)
            i = i + math.radians(angle)
            j = j+1
        
        self.position = new_position
        self.theta = new_theta



    def calculate_sensor_collision(self, sensor_line):
        # TODO: This algorithm is bad in terms of complexity -> O(n^2)
        # Could be done better with a Sweep Line Algorithm -> O(nlogn)

        sensor_coords = sensor_line.get_ui_coordinates()
        A = sensor_coords.P1
        B = sensor_coords.P2
        
        dist = None
        wall = None
        point = None

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

                # Check if distance of new_point to this wall is smaller than previous one
                d = new_point.euclidean_distance(A)
                if dist == None:
                    dist = d
                    wall = m
                    point = new_point
                    continue

                if d < dist:
                    dist = d
                    wall = m
                    point = new_point
                    # The reason why we can already return here is because
                    # we only really need to check for neighbouring lines
                
        if dist is not None:
            return (True, point, wall.get_ui_coordinates())

        return (False,None, None)