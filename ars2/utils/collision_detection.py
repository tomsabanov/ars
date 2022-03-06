import math
from utils.vector import Vector, Point

from shapely.geometry import LineString

class CollisionDetection():
    def __init__(self, radius):
        self.radius = radius

    # Returns the distance between the agent and the wall
    def get_distance(self, wall):
        #point_1 = wall.get_bounds()[0].P1
        #point_2 = wall.get_bounds()[0].P2

        c_coords = wall.get_ui_coordinates()
        point_1 = c_coords.P1
        point_2 = c_coords.P2

        # Triangle formed by the line and the center of the circle
        # wall=distance(P1, P2), side_1=distance(circle.center, Line.P1), side_2=distance(circle.center, Line.P2)
        side_wall = point_1.euclidean_distance(point_2)
        side_1 = self.position.euclidean_distance(point_1)
        side_2 = self.position.euclidean_distance(point_2)

        print(side_1)
        print(side_2)

        # Law of Cosines to find the cos of on of the angles opposite to the projection
        # Can either take angle between the sides: side_wall & side_1, or side_wall & side_2
        # If choose alpha = angle formed by side_wall & side_1
        cos_alpha = (side_1 ** 2 + side_wall ** 2 - side_2 ** 2) / (2 * side_1 * side_wall)

        # From the projection of the center of the circle, we have a right triangle where the projection is
        # the distance between the center of the circle and the line
        # Can use the SOH - sin = opp/hyp
        # sin(alpha) = projection/side_1 <=> projection = sin(alpha)*side_1
        # Which can be replaced by sqrt(1-cos(alpha)^2) from the Pythagorean theorem
        sin_alpha = math.sqrt(1 - cos_alpha ** 2)
        distance_center_wall = sin_alpha * side_1
        return distance_center_wall - self.radius

    def update(self, new_position, map, v, theta):
        self.position = new_position

        colls = []

        for i in range(len(map)):
            c = self.is_collision(map[i])
            if c == None:                    
                continue
            colls.append((c[0], c[1] ,map[i]))



        ''' Glitch checking - out of bounds
        if len(colls) == 0:
            # check if we glitched through it
            d = self.check_glitch(new_position, map, v, theta)
            if d[0] == None:
                return colls
            colls.append(d)        
        '''

        return colls

    def get_point_of_contact(self, wall):
        point_1 = wall.get_bounds()[0].P1
        point_2 = wall.get_bounds()[0].P2
        side_wall = point_1.euclidean_distance(point_2)
        side_1 = self.position.euclidean_distance(point_1)
        side_2 = self.position.euclidean_distance(point_2)

        cos_alpha = (side_1 ** 2 + side_wall ** 2 - side_2 ** 2) / (2 * side_1 * side_wall)

        # Find point on the line of the wall where the circle intersects with the wall
        # Can find this information from the cos of the angle alpha found previously
        # cos(alpha) = adjacent/hypotenuse = len(opposite side to the center of the circle)/side_1
        # <=> len(opposite side to the center of the circle) = cos(alpha)*side_1
        w_1 = cos_alpha * side_1

        # Find the coordinates of the second point of this new line = point of intersection
        # https: // math.stackexchange.com / a / 1630886
        ratio_distances = w_1 / side_wall
        point_of_contact = Point((1 - ratio_distances) * point_1.X + ratio_distances * point_2.X,
                                 (1 - ratio_distances) * point_1.Y + ratio_distances * point_2.Y)
        return point_of_contact


    def distance_between_points(self,p1,p2):
        dist = math.sqrt((p2.X - p1.X)**2 + (p2.Y - p1.Y)**2)
        return dist

    def check_glitch(self, p, map, v, theta):
        box_l = map[0]
        box_r = map[3]
        box_t = map[1]
        box_b = map[2]

        c = None
        w = None
        dist = 1000000

        '''
        if (p.X < 100 or p.X > 600 or p.Y > 600 or p.Y < 100):
            # we need to find the point on the wall
            # we must calculate the line of the agent moving
            # and then find the intersections with the map
            # and choose the closest one
            # there we will move the agent

            new_position = Point(p.X + v * math.cos(theta),
                            p.Y + v * math.sin(theta))

          
            intersections = []
            for m in map:
                g = m.get_ui_coordinates()

                (x,y) =  self.intersect(p,new_position, g.P1, g.P2)
                p2 = Point(x,y)
                d = self.distance_between_points(p, p2)
                if d < dist:
                    dist = d
                    c = Point(x, y)
                    w = m
                
                # check distance between (x,y) and agent
        '''



        if c is not None:
            return (c, dist, w)
        return (None, None, None)


    def intersect(self,a,b,c,d):
        # stuff for line 1
        a1 = b.Y-a.Y
        b1 = a.X-b.X
        c1 = a1*a.X + b1*a.Y

        # stuff for line 2
        a2 = d.Y-c.Y
        b2 = c.X-d.X
        c2 = a2*c.X + b2*c.Y

        determinant = a1*b2 - a2*b1

        if (determinant == 0):
            # Return (infinity, infinity) if they never intersect
            # By "never intersect", I mean that the lines are parallel to each other
            return (math.inf, math.inf)
        else:
            x = (b2*c1 - b1*c2)/determinant
            y = (a1*c2 - a2*c1)/determinant
            return (x,y)



    def is_collision(self, wall):
        distance = self.get_distance(wall)
        if distance <= 0:
            point_of_contact = self.get_point_of_contact(wall)
            #print("Collision at point=[", point_of_contact.X, ", ", point_of_contact.Y, "]")
            return (point_of_contact,distance)
        else:
            print("Distance from object=", distance)
            return None

    # https://stackoverflow.com/a/20677983
    def glitch_through_wall(self, wall, v, theta):
        new_position = Point(self.position.X + math.cos(theta),
                             self.position.Y + math.sin(theta))
        line_1 = (wall.get_bounds()[0].P1, wall.get_bounds()[0].P2)
        line_2 = (self.position, new_position)
        x_diff = (line_1[0].X - line_1[1].X, line_2[0].X - line_2[1].X)
        y_diff = (line_1[0].Y - line_1[1].Y, line_2[0].Y - line_2[1].Y)

        div = self.det(x_diff, y_diff)
        if div == 0:
            return True
        else:
            return False

    # Check if the wall is between the current position and the possible next position
    def det(self, a, b):
        return a[0] * b[1] - a[1] * b[0]