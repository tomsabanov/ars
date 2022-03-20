import json
import os

from utils.object import Object
from utils.vector import Vector, Point


def read_map(map_path, index):
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
        "start_points":[],
        "index":index,
        "features":[]
    }
    for i in range(length_poly):
        poly = json.loads(map[i])
        poly_len = len(poly) - 1
        for i in range(poly_len):
            c1 = poly[i]
            c2 = poly[i+1]
            p = Point(c1[0], c1[1])

            MAP["features"].append(p)
            MAP["map"].append(
                Object(p, [
                    Vector(Point(0,0), Point(c2[0]-c1[0], c2[1] - c1[1]))
                ], type="line")
            )

        c1 = poly[0]
        c2 = poly[len(poly)-1]
        p = Point(c2[0], c2[1])
        MAP["features"].append(p)
        
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
    i = 0
    for map_path in os.listdir(path):
        p = os.path.abspath(os.path.join(path, map_path))
        print(p)
        maps.append(read_map(p, i))
        i = i+1
    
    return maps