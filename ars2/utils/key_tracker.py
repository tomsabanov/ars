
# Manages the commands received from the UI
class KeyTracker():
    def __init__(self, agent, canvas):
        self.agent = agent
        self.canvas = canvas

    # Each event will call a function in the agent to perform an action
    def key_up(self, e):
        self.agent.move_up()
        print("up")

    def key_down(self, e):
        self.agent.move_down()
        print("down")

    def key_left(self, e):
        self.agent.move_left()
        print("left")

    def key_right(self, e):
        self.agent.move_right()
        print("right")