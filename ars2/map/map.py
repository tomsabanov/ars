

# The coordinates 0,0 should always be present INSIDE the map and not into some edge
class Map():
    def __init__(self, bounds):
        self.bounds = bounds





if __name__ == "__main__":
    map_boundaries = [
        [[-10,10],[10,10]],     # Top Edge
        [[-10,-10],[-10,10]],   # Left Edge
        [[10,10],[10,-10]],     # Right Edge
        [[-10,-10],[10,-10]]    # Bottom Edge
    ]

    map = Map(map_boundaries)