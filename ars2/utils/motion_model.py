import math
import numpy as np

from utils.vector import Point, Vector
from utils.collision_detection import CollisionDetection

class MotionModel():
    def __init__(self, l, map):
        # Left and right motor speeds
        self.vl = 0
        self.vr = 0
        self.dir = 0

        self.l = l # distance between the wheels of the robot (we can use 2*radius)

        self.R = 0
        self.omega = 0

        self.map = map

        self.collision_detection = CollisionDetection(self.l/2)

        self.is_colliding = False
        self.collisions = []


    def get_speeds(self):
        return (self.vl, self.vr)
        
    def update_speed(self, vl, vr):
        self.vl = self.vl + vl
        self.vr = self.vr + vr

        if self.vl + self.vr > 0:
            self.dir = 1
        elif self.vl + self.vr < 0:
            self.dir = -1
        else:
            self.dir = 0

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

    def update(self, position, theta):
        if self.vr == 0 and self.vl == 0:
            return (None, None, False)
        
        if self.vr == self.vl:
            # We have forward linear motion, theta stays the same, 
            # we only update the position
            new_position = Point(position.X + self.vr * math.cos(theta),
                                     position.Y + self.vr * math.sin(theta))
            new_theta = theta

        else:
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


        collisions = self.collision_detection.update(new_position, self.map, (self.vr + self.vl)/2, new_theta)

        if len(collisions) > 0:
            if  self.is_colliding == False:
                # snap the agent back
                self.is_colliding = True
                self.collisions = collisions

                (col_point,wall) = collisions[0]
                r = self.l/2

                new_position = Point(col_point.X - self.dir* r*math.cos(new_theta), 
                                col_point.Y - self.dir* r*math.sin(new_theta))
            else:
                # calculate the new position differently
                vec = self.sliding_agains(self.collisions[0], position, theta, self.l/2)
                new_position = Point(position.X - vec[0], position.Y - vec[1])
                
                if theta == 0:
                    new_position = position
        else:
            self.is_colliding = False
            self.collisions = []


        


        
        # We return the updated position and the theta angle
        return (new_position, new_theta, True)

    def sliding_agains(self, collision, position, theta, radius):

        point_of_contact = collision[0]
        wall = collision[1]

        v = (self.vr + self.vl)/2

        # Simulate next position as if there was no wall
        new_position = Point(point_of_contact.X - self.dir*v * math.cos(theta),
                             point_of_contact.Y - self.dir*v * math.sin(theta))

        # Make the new "supposed" point, project it to the wall
        # Project the trajectory of the agent if there were no wall on the wall vector
        #to_project = np.array([[point_of_contact.X, point_of_contact.Y], 
        #                    [new_position.X, new_position.Y]])
        to_project = np.array([new_position.X - point_of_contact.X, new_position.Y - point_of_contact.Y])

        # Points of wall into vector
        wall_1 = wall.get_bounds()[0].P1
        wall_2 = wall.get_bounds()[0].P2
        #wall_vector = np.array([[wall_1.X, wall_1.Y], [wall_2.X, wall_2.Y]])
        wall_vector = np.array([wall_2.X - wall_1.X, wall_2.Y - wall_1.Y])

        # Projection formula
        v_parallel = (np.dot(to_project, wall_vector)/np.dot(wall_vector, wall_vector))*wall_vector
        return v_parallel

    def is_moving(self):
        if abs(self.vl) > 0 or abs(self.vr) > 0:
            return True
        
        return False