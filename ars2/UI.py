from tkinter import *

from utils.key_tracker import KeyTracker
from utils.object import Object
from utils.vector import Vector, Point
from utils.agent import Agent

def return_pressed(event):
    print('Return key pressed.')

def key_press(e):
   print("a")

def key_released(e):
   print("b")

class UI():
    def __init__(self, dimensions, objects):
        self.dimensions = dimensions
        self.objects = objects
        self.margin = 10



    def show(self):
        root = Tk()
        root.title("Interface")
        root.geometry(str(self.dimensions[0]) + "x" + str(self.dimensions[1]) + "+" + str(self.margin*2) + "+" + str(self.margin*2))
        # Create canvas
        c = Canvas(root, height=self.dimensions[0]+self.margin*2, width=self.dimensions[1]+self.margin*2, bg="gray")


        # Implement an example of an agent:
        agent = Agent(Point(150,150), c, self.margin)

        #agent = c.create_oval(100,100,200,200, fill="red")
        #agent_vision = c.create_line()

        # Keeps track of the commands from the UI
        keytracker = KeyTracker(agent, c)

        # Loop and display objects
        # When drawing each object we add the margin to have it visible on the frame
        for object in self.objects:
            if object.type == "line":
                c_coords = object.get_ui_coordinates()
                c.create_line(c_coords.P1.X+self.margin, c_coords.P1.Y+self.margin, c_coords.P2.X+self.margin, c_coords.P2.Y+self.margin, width=5)
            elif object.type == "circle":
                c_ui_origin = object.get_ui_coordinates()
                c.create_oval(c_ui_origin.P1.X+self.margin, c_ui_origin.P1.Y+self.margin, c_ui_origin.P2.X+self.margin, c_ui_origin.P2.Y+self.margin, fill="blue")

        # Bind the keyboard commands to specific actions in KeyTracker
        root.bind('<Up>', keytracker.key_up)
        root.bind('<Down>', keytracker.key_down)
        root.bind('<Left>', keytracker.key_left)
        root.bind('<Right>', keytracker.key_right)

        c.pack()
        root.mainloop()


if __name__ == "__main__":

    # Some objects:
    obj1 = Object(Point(400, 100), [Vector(Point(0, 0), Point(50, 50))], type="circle")
    #obj1.translate_coordinates(Point(200,200))


    objects = [
        # Map borders:
        Object(Point(0,0), [Vector(Point(0,0),Point(600,0))], type="line"),
        Object(Point(600,0), [Vector(Point(0, 0), Point(0, 600))], type="line"),
        Object(Point(0, 600), [Vector(Point(0, 0), Point(600, 0))], type="line"),
        Object(Point(0, 0), [Vector(Point(0, 0), Point(0, 600))], type="line"),

        obj1
    ]

    ui = UI([600, 600], objects)

    ui.show()
