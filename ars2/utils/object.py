#from vector import Vector, Point


# Object sees its own bound coordinates from its referential point of view
# Use trigonometry for angles

# Object class
# An object is defined by a center point and a set of vectors defining its bounds.
# For some objects having a round shape, the bounds will be different.
# But for now we create a template class.
# We assume that all objects are convex
# The bounds of the object must always be in reference to the point (0,0) which represents its internal representation.
# It must not be mistaken with the self.coordinates which is the referential location of the object in the environment.
import math

# Todo: create objects according to their types and throw error if wrong
# Coordinates: the referential point for that object. It should usually be the center but is specified below
# Bounds: a set of vector(s) implying the bounds of the objects. This changes whether it is a circle, rectangle etc...
# The coordinates will serve as a referential point between the bound objects, such as translating the vectors through the space

# TYPE = circle, should have only one bound that is a vector defining the radius between its center and outer edge.
#       Length of bounds for circle must always be 1
#       Referential coordinates must be center of the circle
# TYPE = line, should have only one bound that is a vector defining the line of the object from its center point to end of line
#       Length of bounds for line must always be 1
#       Referential coordinates must be the one end point of the line
# TYPE = rectangle, should have two bounds where one is the length and the other the height of the rectangle
#       Length of bounds for rectangle must always be 2
#       Referential coordinates must be the center of the rectangle
# TYPE = polygon, should have at least 3 bounds where the order of those must complete a full polygon. The last bound should
#       close the first one. The polygon must be CONVEX, the coordinate center can be any point in that case.
#       Length of bounds must be at least 3
#       Referential coordinates can be anything

from utils.vector import Point
from utils.vector import Vector


class Object():
    def __init__(self, coordinates, bounds, type):
        self.coordinates = coordinates  # Point
        self.bounds = bounds            # List[Vector]
        self.type = type                # String type

    # Get object's coordinates origin in a 2D space
    def get_coordinates(self):
        return self.coordinates

    # Update the center of the object coordinate
    # POV FP
    def translate_coordinates(self, point):
        self.coordinates = Point(self.coordinates.X + point.X, self.coordinates.Y + point.Y)

    # Function to rotate an object by an angle, having its center as pivot
    # POV FP
    def rotate(self, angle):
        new_bounds = []
        for bounds in self.bounds:
            if self.type == "circle" or self.type == "line" or self.type == "rectangle":
                x1 = bounds.P1.X * math.cos(angle) - bounds.P1.Y * math.sin(angle)
                y1 = bounds.P1.X * math.sin(angle) + bounds.P1.X * math.cos(angle)
                x2 = bounds.P2.X * math.cos(angle) - bounds.P2.Y * math.sin(angle)
                y2 = bounds.P2.X * math.sin(angle) + bounds.P2.Y * math.cos(angle)
                new_bounds.append(Vector(Point(x1,y1), Point(x2,y2)))
        self.bounds = new_bounds

    # Return the translated bounds in the environment's referential
    # POV ENV
    def get_bounds(self):
        translated_bounds = []
        for bound in self.bounds:
            #bound.print()
            if self.type == "line" or self.type == "circle" or self.type == "rectangle":
                x1 = bound.P1.X + self.coordinates.X
                y1 = bound.P1.Y + self.coordinates.Y
                x2 = bound.P2.X + self.coordinates.X
                y2 = bound.P2.Y + self.coordinates.Y
                translated_bounds.append(Vector(Point(x1,y1), Point(x2,y2)))
                #break # Only one vector that define the radius from the relative POV of the object

        return translated_bounds

    # For the UI, we need to return proper coordinates to have them handled
    def get_ui_coordinates(self):

        # For circle type we need to get the upper left corner of the box surrounding the circle
        if self.type == "circle":
            origin_start = Point(self.coordinates.X - self.bounds[0].P2.X, self.coordinates.Y - self.bounds[0].P2.Y)
            origin_end = Point(self.coordinates.X + self.bounds[0].P2.X, self.coordinates.Y + self.bounds[0].P2.Y)
            return Vector(origin_start, origin_end)
        elif self.type == "line":
            origin_start = Point(self.coordinates.X + self.bounds[0].P1.X, self.coordinates.Y + self.bounds[0].P1.Y)
            origin_end = Point(self.coordinates.X + self.bounds[0].P2.X, self.coordinates.Y + self.bounds[0].P2.Y)
            return Vector(origin_start, origin_end)




def test_rotation():
    bounds = [Vector(Point(0,0), Point(1,0))]
    test_obj = Object(Point(0,0), bounds, "line")
    for b in bounds:
        b.print()
    test_obj.rotate(math.pi / 4)
    rotated_bounds = test_obj.get_bounds()
    for r in rotated_bounds:
        r.print()

# Translate referential point, and then return the translated bounds
def test_translate():
    bounds = [Vector(Point(0,0), Point(1,0))]
    test_obj = Object(Point(0,0), bounds, "line")
    print("Test for single line: ")
    test_obj.get_coordinates().print()          # See initial referential point
    initial_bounds = test_obj.get_bounds()                      # See initial bounds coordinates
    for i in initial_bounds:
        i.print()
    test_obj.translate_coordinates(Point(2.0,2.0))   # Translate referential coordinate points
    test_obj.get_coordinates().print()          # See internal change coordinates
    translated_bounds = test_obj.get_bounds()   # Return the bounds in the referential environment
    for t in translated_bounds:
        t.print() # Built-in print function for vectors

def test_circle():
    print("Test for circle: ")
    bounds = [Vector(Point(0,0), Point(1,0))]

    test_circle = Object(Point(0,0), bounds, "circle")
    test_circle.translate_coordinates(Point(-3.0,3.0))
    test_circle.get_coordinates().print()  # See internal change coordinates
    c_bounds = test_circle.get_bounds()  # Return the bounds in the referential environment
    for c in c_bounds:
        c.print()

def test_rectangle():
    print("Test for rectangle: ")
    bounds = [Vector(Point(0,0),Point(2,0)), Vector(Point(0,0),Point(0,1))]
    test_rectangle = Object(Point(1,0), bounds, "rectangle")
    #test_rectangle.translate_coordinates(Point(1,1))
    #test_rectangle.get_coordinates().print()  # See internal change coordinates
    #r_bounds = test_rectangle.get_bounds()  # Return the bounds in the referential environment
    #for r in r_bounds:
    #    r.print()

    #test_rectangle.translate_coordinates(Point(-1,-1))
    #test_rectangle.get_coordinates().print()  # See internal change coordinates
    r_bounds = test_rectangle.get_bounds()  # Return the bounds in the referential environment
    for r in r_bounds:
        r.print()
    test_rectangle.rotate(math.pi)
    r_bounds = test_rectangle.get_bounds()  # Return the bounds in the referential environment
    for r in r_bounds:
        r.print()

# Test function
if __name__ == "__main__":

    #test_rotation()
    #test_translate()
    #test_circle()
    test_rectangle()