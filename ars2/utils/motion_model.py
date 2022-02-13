import math
import numpy as np

from utils.vector import Point

class MotionModel():
    def __init__(self, l):
        # Left and right motor speeds
        self.vl = 0
        self.vr = 0

        self.l = l # distance between the wheels of the robot (we can use 2*radius)

        self.R = 0
        self.omega = 0

    def update_speed(self, vl, vr):
        self.vl = self.vl + vl
        self.vr = self.vr + vr

        if self.vl == self.vr:
            self.R = 0
            self.omega = 0
        else:
            self.R = (self.l/2)*( (self.vr + self.vl)/(self.vr - self.vl) )
            self.omega = ((self.vr-self.vl)/self.l)
    
    def reset_speed(self):
        self.vl = 0
        self.vr = 0

        self.R = 0
        self.omega = 0

    def update_position(self, position, theta):
        if self.vr == self.vl:
            # We have forward linear motion, theta stays the same, 
            # we only update the position
            new_position = Point(position.X + self.vr * math.cos(theta),
                                     position.Y + self.vr * math.sin(theta))
            return (new_position, theta)

        # We have a rotation

        ICCx = position.X - self.R * math.sin(theta)
        ICCy = position.Y + self.R * math.cos(theta)

        # Now let's calculate the new position of the agent
        A1 = np.array([[math.cos(self.omega), -math.sin(self.omega), 0],
                      [math.sin(self.omega), math.cos(self.omega), 0],
                      [0,0,1]])
        A2 = np.array([position.X - ICCx, 
                        position.Y - ICCy,
                        theta])
        A3 = np.array([ICCx, ICCy, self.omega])

        P = A1.dot(A2) + A3

        new_position = Point(P[0],P[1])
        new_theta = P[2]
        
        # We return the updated position and the theta angle
        return (new_position, new_theta)