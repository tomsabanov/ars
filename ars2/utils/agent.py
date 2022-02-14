import math
import numpy as np

from utils.motion_model import MotionModel
from utils.sensor_model import SensorModel

from utils.object import Object
from utils.vector import Vector, Point

class CollisionDetection():
    def __init__(self, position, radius):
        self.position = position
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

    def update(self, new_position):
        self.position = new_position

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
            print("Collision at point=[", point_of_contact.X, ", ", point_of_contact.Y, "]")
            return True
        else:
            print("Distance from object=", distance)
            return False



class Agent():
    def __init__(self, center, radius, map):
        self.position = center
        self.theta = 0
        self.radius = radius

        self.map = map

        self.motion_model = MotionModel(self.radius * 2)
        self.sensor_model = SensorModel(self.position, self.theta, self.radius,
                                        self.map,6,1000)
        self.collision_detection = CollisionDetection(self.position, self.radius)

        # Radius Bound is a horizontal vector
        self.circleObject = Object(self.position, [Vector(Point(0, 0), Point(self.radius, 0))], type="circle")

        # Create object line that will serve as vision. By default we put the cast to be twice the agent's radius
        self.lineObject = Object(self.position, [Vector(Point(0, 0), Point(self.radius, 0))], type="line")

        self.speed_increment = 5
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
        (new_position, new_theta, change) = self.motion_model.update_position(self.position, self.theta)
        
        # If there is no change in movement, then just skip the update
        if change == False:
            return
        
        self.update_agent_objects(new_position, new_theta)

        # Update the sensor model
        self.sensor_model.update(new_position, new_theta)
        self.collision_detection.update(new_position)
        # for wall in self.map:
        #     # print()
        for i in range(len(self.map)):
            print('Collision with wall ', i, ': ', self.collision_detection.is_collision(self.map[i]))

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
