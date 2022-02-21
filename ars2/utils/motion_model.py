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
        self.is_colliding2 = False
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
        print("Number of collisions : " + str(len(collisions)))
        if len(collisions) == 1:
            self.is_colliding2 = False
            if  self.is_colliding == False:
                # snap the agent back
                self.is_colliding = True
                self.collisions = collisions

                (col_point,distance,wall) = collisions[0]
                d = abs(distance)
            
                new_x = new_position.X - self.dir*d*math.cos(new_theta)
                new_y = new_position.Y - self.dir*d*math.sin(new_theta)
                new_position = Point(new_x, new_y)
            else:
                # calculate the new position differently
                vec = self.sliding_agains(self.collisions[0], position, theta, self.l/2)
                new_position = Point(position.X - vec[0], position.Y - vec[1])


        elif len(collisions) > 1:

            if self.is_colliding2:
                new_position = position
                new_theta = theta
            else:
                # Colliding with two walls
                self.is_colliding = True
                self.is_colliding2 = True
                self.collisions = collisions

                (col_point1,distance,wall) = collisions[0]
                (col_point2,distance2,wall2) = collisions[1]


                # Calculate intersection between two circles around d1 and d2 with 
                # the same radius as the agent

                (x3, y3, x4, y4) = self.get_intersections(
                    col_point1.X, col_point1.Y, self.l/2,
                    col_point2.X, col_point2.Y, self.l/2
                )

                a = np.array([new_position.X, new_position.Y])
                p1 = np.array([x3, y3])
                p2 = np.array([x4, y4])

                d1 = np.linalg.norm(a-p1)
                d2 = np.linalg.norm(a-p2)

                if d2 < d1:
                    p1 = p2

                new_position = Point(p1[0], p1[1])
                new_theta = theta


        else:
            self.is_colliding = False
            self.is_colliding2 = False
            self.collisions = []


        
        # We return the updated position and the theta angle
        return (new_position, new_theta, True)


    def get_intersections(self, x0, y0, r0, x1, y1, r1):
        # circle 1: (x0, y0), radius r0
        # circle 2: (x1, y1), radius r1

        d=math.sqrt((x1-x0)**2 + (y1-y0)**2)
        
        # non intersecting
        if d > r0 + r1 :
            return None
        # One circle within other
        if d < abs(r0-r1):
            return None
        # coincident circles
        if d == 0 and r0 == r1:
            return None
        else:
            a=(r0**2-r1**2+d**2)/(2*d)
            h=math.sqrt(r0**2-a**2)
            x2=x0+a*(x1-x0)/d   
            y2=y0+a*(y1-y0)/d   
            x3=x2+h*(y1-y0)/d     
            y3=y2-h*(x1-x0)/d 

            x4=x2-h*(y1-y0)/d
            y4=y2+h*(x1-x0)/d
            
            return (x3, y3, x4, y4)



    def sliding_agains(self, collision, position, theta, radius):

        point_of_contact = collision[0]
        wall = collision[2]

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