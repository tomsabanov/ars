import sys
import os
import json


from utils.object import Object
from utils.vector import Vector, Point
from utils.agent import Agent
from Simulation import Simulation


class ER:

    def __init__(self, maps):
        self.maps = maps

        a = self.create_agent()
        s = self.create_simulation(a)

        s.simulate()

    def create_agent(self):
        map = self.maps[0]
        agent = Agent(
                        map = map,
                        radius = 100, 
                        start_pos_index = 0
                    )
        return agent
    
    def create_simulation(self, agent):
        sim = Simulation(
            agent=agent, 
            render=True,
            simulation=True,
            time=5, # how many seconds the simulation will run,
            time_step=500 # on how many ms should agent reevaluate motor speed
        )
        return sim



def read_map(map_path):
    # Read the map from map_path
    f = open(map_path, "r")
    map = f.read()
    map = map.split("\n")
    map.pop()
    length_poly = len(map)-1

    # Map[0] should contain the exterior box of the map
    j = json.loads(map[0])

    MAP = {
        "map":[],
        "start_points":[]
    }
    for i in range(length_poly):
        poly = json.loads(map[i])
        poly_len = len(poly) - 1
        for i in range(poly_len):
            c1 = poly[i]
            c2 = poly[i+1]
            MAP["map"].append(
                Object(Point(c1[0], c1[1]), [
                    Vector(Point(0,0), Point(c2[0]-c1[0], c2[1] - c1[1]))
                ], type="line")
            )

        c1 = poly[0]
        c2 = poly[len(poly)-1]
        MAP["map"].append(
            Object(Point(c1[0], c1[1]), [
                Vector(Point(0,0), Point(c2[0]-c1[0], c2[1] - c1[1]))
            ], type="line")
        )
    
    sp = json.loads(map[len(map) - 1])
    for p in sp:
        MAP["start_points"].append(
            Point(p[0],p[1])
        )

    return MAP

def get_maps(path):
    print("Available maps:")
    maps = list()
    for map_path in os.listdir(path):
        p = os.path.abspath(os.path.join(path, map_path))
        print(p)
        maps.append(read_map(p))
    
    return maps


def main():
    if len(sys.argv)<2:
        print("Provide path to maps!")
        sys.exit()

    map_dir = sys.argv[1]
    maps = get_maps(map_dir)


    er = ER(
        maps = maps
        )

if __name__ == '__main__':
    main()