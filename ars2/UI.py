import math
import sys
from tkinter import *


from utils.object import Object
from utils.vector import Vector, Point
from utils.agent import Agent

class Settings:
    def __init__(self, w=800, h=800, delay=1, margin=0):
        self.BOARD_WIDTH = w
        self.BOARD_HEIGHT = h
        self.DELAY = delay
        self.MARGIN = margin

class UI(Canvas):

    def __init__(self, sett: Settings):
        super().__init__(width=sett.BOARD_WIDTH+sett.MARGIN*2, height=sett.BOARD_HEIGHT + sett.MARGIN*2,
            background="white", highlightthickness=0)

        self.settings = sett
        self.setup()
        self.pack()


    def setup(self):
        # Setup the UI/agent

        # TODO: Map should be a hollow polygon, it should also be read from a file
        #       and scaled appropriately to the dimensions of the UI
        self.map = [
            Object(Point(100,100), [Vector(Point(0,0),Point(500,0))], type="line"),
            Object(Point(600,100), [Vector(Point(0, 0), Point(0, 500))], type="line"),
            Object(Point(100, 600), [Vector(Point(0, 0), Point(500, 0))], type="line"),
            Object(Point(100, 100), [Vector(Point(0, 0), Point(0, 500))], type="line"),
        ]
        for l in self.map:
            c_coords = l.get_ui_coordinates()
            self.create_line(c_coords.P1.X+self.settings.MARGIN,
                            c_coords.P1.Y+self.settings.MARGIN, 
                            c_coords.P2.X+self.settings.MARGIN, 
                            c_coords.P2.Y+self.settings.MARGIN, width=5)

        self.setup_agent()


        self.bind_all("<Key>", self.onKeyPressed)
        self.after(self.settings.DELAY, self.onTimer)


    def setup_agent(self):
        # Setup the agent and his canvas objects

        self.agent = Agent(Point(
                            int(self.settings.BOARD_WIDTH/2), 
                            int(self.settings.BOARD_HEIGHT/2)
                            ),
                            50,
                            self.map
                    )
    
        c_coords = self.agent.get_circle_coordinates()
        self.agent_circle = self.create_oval(c_coords.P1.X, c_coords.P1.Y, c_coords.P2.X, c_coords.P2.Y, fill="red")

        l_coords = self.agent.get_line_coordinates()
        self.agent_line = self.create_line(l_coords.P1.X, l_coords.P1.Y, l_coords.P2.X, l_coords.P2.Y, width=4,  fill='green')

        (vision_lines, distances) = self.agent.get_vision_lines()
        self.agent_vision_lines = []
        self.agent_distances = []
        i = 0
        for l in vision_lines:
            self.agent_vision_lines.append(
                self.create_line(l.P1.X, l.P1.Y, l.P2.X, l.P2.Y, width=2)
            )
            self.agent_distances.append(
                self.create_text(l.P1.X,l.P1.Y, text=str(distances[i]), fill="black", font=('Helvetica 12'))
            )
            i = i+1


        (left_speed, right_speed) = self.agent.get_speeds()
        tl = "Left motor speed: " + str(left_speed)
        tr = "Right motor speed: " + str(right_speed)
        self.agent_speed_left = self.create_text(700,700, text=tl, fill="black", font=('Helvetica 12'))
        self.agent_speed_right = self.create_text(700,750, text=tr, fill="black", font=('Helvetica 12'))

        

    def delete_agent_ui(self):
        self.delete(self.agent_circle)
        self.delete(self.agent_line)

        for v in self.agent_vision_lines:
            self.delete(v)
        for d in self.agent_distances:
            self.delete(d)
    
    def update_agent_speed_ui(self):
        self.delete(self.agent_speed_left)
        self.delete(self.agent_speed_right)        
        (left_speed, right_speed) = self.agent.get_speeds()
        tl = "Left motor speed: " + str(left_speed)
        tr = "Right motor speed: " + str(right_speed)
        self.agent_speed_left = self.create_text(620,30, text=tl, fill="black", font=('Helvetica 12'))
        self.agent_speed_right = self.create_text(620,50, text=tr, fill="black", font=('Helvetica 12'))

    def update_agent_ui(self):
        if self.agent.is_agent_moving() == False:
            self.update_agent_speed_ui()
            return 

        self.delete_agent_ui()

        c_coords = self.agent.get_circle_coordinates()
        self.agent_circle = self.create_oval(c_coords.P1.X, c_coords.P1.Y, c_coords.P2.X, c_coords.P2.Y, fill="red")

        l_coords = self.agent.get_line_coordinates()
        self.agent_line = self.create_line(l_coords.P1.X, l_coords.P1.Y, l_coords.P2.X, l_coords.P2.Y,  width=4,  fill='green')

        (vision_lines, distances) = self.agent.get_vision_lines()
        i = 0
        for l in vision_lines:
            self.agent_vision_lines.append(
                self.create_line(l.P1.X, l.P1.Y, l.P2.X, l.P2.Y, width=2)
            )
            self.agent_distances.append(
                self.create_text(l.P1.X,l.P1.Y, text=str(distances[i]), fill="black", font=('Helvetica 12'))
            )
            i = i+1

        self.update_agent_speed_ui()

        


    def onKeyPressed(self, e):
        # Key tracking

        key = e.keysym
        if key == "Escape":
            sys.exit()
        
        # Provide the agent the key press so it can react
        self.agent.on_key_press(key)
        

    def onTimer(self):
        # We update the agent and then the agent 
        # canvas objects on each timer event and then redraw them
        self.agent.update()

        self.update_agent_ui()

        self.after(self.settings.DELAY, self.onTimer)


def main():
    root = Tk()

    settings = Settings()
    ui = UI(settings)

    root.mainloop()


if __name__ == '__main__':
    main()