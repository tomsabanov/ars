

# Point class that is a 2D point with X and Y
import math
import numpy as np

class Point():
    def __init__(self, X, Y):
        self.X = X
        self.Y = Y

    # Translate a point with another one
    def translate(self, direction):
        self.X = self.X + direction.X
        self.Y = self.Y + direction.Y

    # Euclidean distance between two points
    def euclidean_distance(self, point):
        return math.sqrt((self.X-point.X)**2 + (self.Y-point.Y)**2)

    def print(self):
        print("P(" + str(self.X) + "," + str(self.Y) + ")")

# Vector class to create bounds for our objects
# We can also compute distances etc here
# Vector's direction starts from P1 and goes to P2
class Vector():
    def __init__(self, P1, P2):
        self.P1 = P1
        self.P2 = P2

    # Adding the other vector to P2
    def addition_vector(self, vector):
        self.P2.translate(vector)

    # Translate a vector's coordinates with another one
    def translate_vector(self, vector):
        self.P1.translate(vector)
        self.P2.translate(vector)

    def print(self):
        print("vec{P(" + str(self.P1.X) + "," + str(self.P1.Y) + "),P(" + str(self.P2.X) + "," + str(self.P2.Y) + ")}")

