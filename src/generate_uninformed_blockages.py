import traci
import xml.etree.ElementTree as ET
import sumolib

import generate_cars as gc
from utils import a, get_sumo_cmd


BLOCKED_ROADS_COUNT = 5
TRIGGER_STEPS = 3
OUT_FILE = "./data/rerouter.add.xml"

taz_file = "./tmp/TAZ.taz.xml"
tree = ET.parse(taz_file)
root = tree.getroot()

net = sumolib.net.readNet("./data/neulengbach_sumo-webtools-osm.net.xml.gz")
blockableRoads = gc.getEdgesFromTaz(root, "Zone_1")

def get_adjacent_edges(start_edge, steps):
    visited = set()
    frontier = {start_edge}

    for _ in range(steps):
        next_frontier = set()

        for edge in frontier:
            if edge in visited:
                continue

            visited.add(edge)

            for succ in net.getEdge(edge).getOutgoing():
                next_frontier.add(succ.getID())

            for pred in net.getEdge(edge).getIncoming():
                next_frontier.add(pred.getID())

        frontier = next_frontier

    return visited

args = [
    "-n", a("../data/neulengbach_sumo-webtools-osm.net.xml.gz"),
    "-a", a("../tmp/TAZ.taz.xml"),
]

SUMO_CMD = get_sumo_cmd(args, gui=False)
traci.start(SUMO_CMD)

blocked_edges = set()
trigger_edges = set()

for _ in range(BLOCKED_ROADS_COUNT):
    blocked = gc.getRandomEdge(blockableRoads)
    blocked_edges.add(blocked)
    print(f"added {blocked} to blocked_edges")
    neighbors = get_adjacent_edges(blocked, TRIGGER_STEPS)
    trigger_edges.update(neighbors)
    
    #Check for edge in other direction
    if blocked.startswith("-"):
        opposite = blocked[1:]
    else:
        opposite = "-" + blocked

    if net.hasEdge(opposite):
        blocked_edges.add(opposite)
        print(f"added {opposite} to blocked_edges as opposite")
        neighbors = get_adjacent_edges(blocked, TRIGGER_STEPS)
        trigger_edges.update(neighbors)


additional = ET.Element("additional")

rerouter = ET.SubElement(
    additional,
    "rerouter",
    {
        "id": "rerouter",
        "edges": " ".join(sorted(trigger_edges))
    }
)

interval = ET.SubElement(
    rerouter,
    "interval",
    {
        "begin": "0",
        "end": "1000000"
    }
)

for edge in blocked_edges:
    ET.SubElement(
        interval,
        "closingReroute",
        {"id": edge} 
    )


tree = ET.ElementTree(additional)
tree.write(OUT_FILE)

traci.close()