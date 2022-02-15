import math
from utils.vector import Vector, Point


class CollisionDetection():
    def __init__(self, radius):
        self.radius = radius

    # Returns the distance between the agent and the wall
    def get_distance(self, wall):
        point_1 = wall.get_bounds()[0].P1
        point_2 = wall.get_bounds()[0].P2

        # Triangle formed by the line and the center of the circle
        # wall=distance(P1, P2), side_1=distance(circle.center, Line.P1), side_2=distance(circle.center, Line.P2)
        side_wall = point_1.euclidean_distance(point_2)
        side_1 = self.position.euclidean_distance(point_1)
        side_2 = self.position.euclidean_distance(point_2)

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

    def update(self, new_position, map):
        self.position = new_position

        colls = []

        for i in range(len(map)):
            c = self.is_collision(map[i])
            if c == None:
                continue
            colls.append((c,map[i]))
            #print('Collision with wall ', i, ': ')

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

    def is_collision(self, wall):
        distance = self.get_distance(wall)
        if distance <= 0:
            point_of_contact = self.get_point_of_contact(wall)
            #print("Collision at point=[", point_of_contact.X, ", ", point_of_contact.Y, "]")
            return point_of_contact
        else:
            #print("Distance from object=", distance)
            return None

    # https://stackoverflow.com/a/20677983
    def glitch_through_wall(self, wall, v, theta):
        new_position = Point(self.position.X + v * math.cos(theta),
                             self.position.Y + v * math.sin(theta))
        line_1 = (wall.get_bounds()[0].P1, wall.get_bounds()[0].P2)
        line_2 = (self.position, new_position)
        x_diff = (line_1[0].X - line_1[1].X, line_2[0].X - line_2[1].X)
        y_diff = (line_1[0].Y - line_1[1].Y, line_2[0].Y - line_2[1].Y)

        div = self.det(x_diff, y_diff)
        if div == 0:
            return False
        else:
            return True

    # Check if the wall is between the current position and the possible next position
    def det(self, a, b):
        return a[0] * b[1] - a[1] * b[0]