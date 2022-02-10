import math

from utils.object import Object
from utils.vector import Vector, Point


# Agent implements an objects but also has an orientation and parameters for moving, sensors...
agent_radius = 50

class Agent():
    def __init__(self, coordinates, Canvas, margin):
        self.coordinates = coordinates
        self.Canvas = Canvas
                                                     # Radius Bound is a horizontal vector
        self.circleObject = Object(self.coordinates, [Vector(Point(0,0), Point(agent_radius, 0))], type="circle")
        # Create object line that will serve as vision. By default we put the cast to be twice the agent's radius
        self.lineObject = Object(self.coordinates, [Vector(Point(0,0), Point(agent_radius*2, 0))], type="line")
        self.lineObject.rotate(math.pi / 2) # Rotate it to face the direction we want

        self.margin = margin

        self.generate_circle()

    def generate_circle(self):
        c_coords = self.circleObject.get_ui_coordinates()   # Get translated object coordinates to show in the UI
        #c_coords.print()
        print("coords agent: " + str(c_coords.P1.X) + "," + str(c_coords.P1.Y) + "," + str(c_coords.P2.X) + "," + str(c_coords.P2.Y))
        self.circle = self.Canvas.create_oval(c_coords.P1.X+self.margin, c_coords.P1.Y+self.margin, c_coords.P2.X+self.margin, c_coords.P2.Y+self.margin, fill="red")
        l_coords = self.lineObject.get_ui_coordinates()
        self.vision = self.Canvas.create_line(l_coords.P1.X + self.margin, l_coords.P1.Y + self.margin, l_coords.P2.X + self.margin, l_coords.P2.Y + self.margin, width=5)


    #TODO: when moving the object by rotation, we should delete the old GUI Canvas and create a new one with update coordinates
    #TODO: This is because Tkinter only allows for moving up,down,left,right, but no rotations. So we should always delete and redo
    # Should be for each moving function below:

    # From KeyTracker, Move the agent in a certain direction
    def move_up(self):
        # Update internal representation of circleObject (being the physical robot)
        self.circleObject.translate_coordinates(Point(0,-5))
        # Update its Vision Vector
        self.lineObject.translate_coordinates(Point(0,-5))
        # Then update on the interface
        # todo: this is where we should replace the lines below by creating new GUI shapes and also our self.circle and self.vision
        self.Canvas.move(self.circle, 0, -5)
        self.Canvas.move(self.vision, 0, -5)

    def move_down(self):
        # Update internal representation of circleObject (being the physical robot)
        self.circleObject.translate_coordinates(Point(0, 5))
        # Update its Vision Vector
        self.lineObject.translate_coordinates(Point(0, 5))
        # Then update on the interface
        self.Canvas.move(self.circle, 0, 5)
        self.Canvas.move(self.vision, 0, 5)

    def move_left(self):
        # Update internal representation of circleObject (being the physical robot)
        self.circleObject.translate_coordinates(Point(-5, 0))
        # Update its Vision Vector
        self.lineObject.translate_coordinates(Point(-5, 0))
        # Then update on the interface
        self.Canvas.move(self.circle, -5, 0)
        self.Canvas.move(self.vision, -5, 0)

    def move_right(self):
        # Update internal representation of circleObject (being the physical robot)
        self.circleObject.translate_coordinates(Point(5, 0))
        # Update its Vision Vector
        self.lineObject.translate_coordinates(Point(5, 0))
        # Then update on the interface
        self.Canvas.move(self.circle, 5, 0)
        self.Canvas.move(self.vision, 5, 5)
