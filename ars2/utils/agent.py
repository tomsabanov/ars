import math
import numpy as np

from utils.object import Object
from utils.vector import Vector, Point


class MotionModel():
    def __init__(self, position, l):
        
        self.position = position # center point of the robot

        # Left and right motor speeds
        self.vl = 0
        self.vr = 0

        self.l = l # distance between the wheels of the robot (we can use 2*radius)

        self.theta = 0 # angle
        self.R = 0
        self.omega = 0
    
    def update_speed(self, vl, vr):
        self.vl = self.vl + vl
        self.vr = self.vr + vr
    
    def reset_speed(self):
        self.vl = 0
        self.vr = 0

    def update_position(self):
        print("Speed ")
        print(self.vl)
        print(self.vr)
        # Calculate R, omega, ICC and new position
        if self.vr == self.vl:
            # We have forward linear motion, theta stays the same, 
            # we only update the position
            self.R = 0
            self.omega = 0

            new_position = Point(self.position.X + self.vr * math.cos(self.theta),
                                     self.position.Y + self.vr * math.sin(self.theta))
            
            self.position = new_position

            return (self.position, self.theta)

        # We have a rotation
        
        self.R = (self.l/2)*( (self.vr + self.vl)/(self.vr - self.vl) )
        self.omega = (self.vr-self.vl)/self.l

        self.ICCx = self.position.X - self.R * math.sin(self.theta)
        self.ICCy = self.position.Y + self.R * math.cos(self.theta)

        # Now let's calculate the new position of the agent
        A1 = np.array([[math.cos(self.omega), -math.sin(self.omega), 0],
                      [math.sin(self.omega), math.cos(self.omega), 0],
                      [0,0,1]])
        A2 = np.array([self.position.X - self.ICCx, 
                        self.position.Y - self.ICCy,
                        self.theta])
        A3 = np.array([self.ICCx, self.ICCy, self.omega])

        P = A1.dot(A2) + A3

        new_position = Point(P[0],P[1])

        self.position = new_position
        self.theta = P[2]
        
        # We return the updated position and the theta angle
        return (self.position, self.theta)


class Agent():
    def __init__(self, center, radius):
        self.position = center
        self.radius = radius
        self.theta = 0

        self.speed_increment = 1

        self.motion_model = MotionModel(self.position,self.radius*2)

        # Radius Bound is a horizontal vector
        self.circleObject = Object(self.position, [Vector(Point(0,0), Point(self.radius, 0))], type="circle")

        # Create object line that will serve as vision. By default we put the cast to be twice the agent's radius
        self.lineObject = Object(self.position, [Vector(Point(0,0), Point(self.radius*2, 0))], type="line")

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



    def update(self):
        # update the agent motion and update its coordinates
        (new_position, new_theta) = self.motion_model.update_position()
        self.position = new_position

        self.circleObject.update_coordinates(self.position)

        #if new_theta != self.theta:
        # Update the line




        self.theta = new_theta



    def on_key_press(self, key):
        # React to the key press
        try:
            action, args = self.agent_actions[key]
            action(*args)
        except Exception:
            # ignore it
            pass

