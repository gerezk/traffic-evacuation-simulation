# based on gridDistricts.py in tools

import sumolib  
import traci
import math
from pathlib import Path
import random
import copy

from utils import a, get_sumo_cmd


# traffic assignment zone
class TAZ:
    def __init__(self, id, shape, color):
        self.id = id
        self.shape = shape
        self.color = color
        self.edges = []

    def write(self, outf):
        outf.write('    <taz id="%s" shape="%s" edges="%s"/>\n' % (
        self.id, ' '.join(["%s,%s" % (x, y) for x, y in self.shape]),
         ' '.join(self.edges)))


def generateCircularTAZ(network, id, center_x, center_y, radius, color=(255, 0, 0, 100)):
    net = sumolib.net.readNet(network)
    xmin, ymin, xmax, ymax = net.getBoundary() # TODO: should be used for error handling
    # print(xmin, ymin, xmax, ymax)
    polygon_num = 12 # the shape of the polygon is only for representng it on the map, higher it is better it looks
    polygon_rep_circle=[]
    polygon_color = color
    for i in range(polygon_num):
        angle = math.pi*2/polygon_num*i
        polygon_rep_circle.append((center_x+radius*math.sin(angle), center_y+radius*math.cos(angle)))
    polygon_rep_circle.append(polygon_rep_circle[0]) # close the polygon

    generated_TAZ = TAZ(f"Zone_{id}",
                    polygon_rep_circle,
                    polygon_color)
    for edge in net.getEdges():
        x, y = sumolib.geomhelper.positionAtShapeOffset(edge.getShape(True), edge.getLength() / 2)
        
        distance = math.sqrt((x-center_x)**2+(y-center_y)**2)
        if (distance<radius):
            generated_TAZ.edges.append(edge.getID())
            
    return generated_TAZ

def generate_safeTAZ(network, danger_edges):
    net = sumolib.net.readNet(network)
    generated_TAZ = TAZ("Safe_Zone",
                [(0,0)],
                (0,0,0,0))
    for edge in net.getEdges():
        if edge.getID() not in danger_edges:
            generated_TAZ.edges.append(edge.getID())
    return generated_TAZ
    
def create_TAZ_file(outf_name, TAZ_list):
    with open(outf_name, 'w') as outf:
        sumolib.writeXMLHeader(outf, "$Id$", "additional")
        for taz in TAZ_list:
            taz.write(outf)
        outf.write("</additional>\n")

def main():
    network_file = a("../data/neulengbach_sumo-webtools-osm.net.xml.gz")
    danger_TAZ = generateCircularTAZ(network_file, 0, 1250, 1100, 800)
    blocked_TAZ = generateCircularTAZ(network_file, 1, 1250, 1100, 500, color=(120, 120, 0,
                                                                               100))  # used by the generation of the uninformed blockages, so the blockades are somewhere in the inner city
    safeTAZ = generate_safeTAZ(network_file, danger_TAZ.edges)

    zones = [danger_TAZ, blocked_TAZ, safeTAZ]
    out_dir = Path("../tmp")
    out_dir.mkdir(parents=True, exist_ok=True)
    dangerTAZfileName = a("../tmp/TAZ.taz.xml")

    create_TAZ_file(dangerTAZfileName, zones)

    args = [
        "-n", network_file,
        "-r", dangerTAZfileName
    ]

    SUMO_CMD = get_sumo_cmd(args, gui=False)

    traci.start(SUMO_CMD)

    # Add polygon showing danger taz
    traci.polygon.add(
        polygonID="dangerZonePoly",
        shape=danger_TAZ.shape,
        color=danger_TAZ.color,  # RGBA
        fill=True,
        layer=0  # lowest so that everz other thing shows
    )

    # Add polygon showing danger taz
    traci.polygon.add(
        polygonID="blockedZonePoly",
        shape=blocked_TAZ.shape,
        color=blocked_TAZ.color,
        fill=True,
        layer=1
    )

    traci.close()

if __name__ == "__main__":
    main()