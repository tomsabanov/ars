
import sys
from tkinter import *


from utils.object import Object
from utils.vector import Vector, Point
from utils.agent import Agent

class Settings:
    def __init__(self, w=600, h=600, delay=10, margin=10):
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
            Object(Point(0,0), [Vector(Point(0,0),Point(600,0))], type="line"),
            Object(Point(600,0), [Vector(Point(0, 0), Point(0, 600))], type="line"),
            Object(Point(0, 600), [Vector(Point(0, 0), Point(600, 0))], type="line"),
            Object(Point(0, 0), [Vector(Point(0, 0), Point(0, 600))], type="line"),
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
                            radius=50 
                    )
    
        c_coords = self.agent.get_circle_coordinates()
        self.agent_circle = self.create_oval(c_coords.P1.X, c_coords.P1.Y, c_coords.P2.X, c_coords.P2.Y, fill="red")

        l_coords = self.agent.get_line_coordinates()
        self.agent_line = self.create_line(l_coords.P1.X, l_coords.P1.Y, l_coords.P2.X, l_coords.P2.Y, width=5)



    def delete_agent_ui(self):
        self.delete(self.agent_circle)
        self.delete(self.agent_line)

    def update_agent_ui(self):
        self.delete_agent_ui()

        c_coords = self.agent.get_circle_coordinates()
        self.agent_circle = self.create_oval(c_coords.P1.X, c_coords.P1.Y, c_coords.P2.X, c_coords.P2.Y, fill="red")

        l_coords = self.agent.get_line_coordinates()
        self.agent_line = self.create_line(l_coords.P1.X, l_coords.P1.Y, l_coords.P2.X, l_coords.P2.Y, width=5)


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