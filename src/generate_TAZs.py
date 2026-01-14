# based on gridDistricts.py in tools

import sumolib  
import traci
import math
from sumolib.miscutils import Colorgen 
from launcher import get_sumo_cmd
from pathlib import Path

import random
import copy


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


def generateCircularDangerTAZ(network, id, center_x, center_y, radius, color=(255, 0, 0, 100)):
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

    generated_TAZ = TAZ("Danger_Zone_%s" % (id),
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

def block_roads(zone_edge_list, num_to_block):
    blocked_edges = []
    copy_edges_list= copy.deepcopy(zone_edge_list)
    vehicle_types = traci.vehicletype.getIDList()
    # todo: handle if too many edges are blocked. eg %80
    if (len(copy_edges_list)<=num_to_block):
         raise Exception('too many edges to block')
    for i in range(num_to_block):
        selected_int = random.randint(0, len(copy_edges_list))
        selected_edge_id= copy_edges_list[selected_int]
        blocked_edges.append(selected_edge_id)
        copy_edges_list.pop(selected_int)

        traci.edge.setDisallowed(selected_edge_id, "private")
        # traci.edge.setAllowed(selected_edge_id, "none")

def a(path):
    return str((Path(__file__).parent / path).resolve())
     
if __name__ == "__main__":
    network_file = a("../data/neulengbach_sumo-webtools-osm.net.xml.gz")
    danger_TAZ = generateCircularDangerTAZ(network_file, 0, 1250, 1100, 800)
    safeTAZ = generate_safeTAZ(network_file, danger_TAZ.edges)

    zones = [danger_TAZ, safeTAZ]
    out_dir = Path("../tmp")
    out_dir.mkdir(parents=True, exist_ok=True)
    TAZfileName = a("../tmp/DangerTAZ.taz.xml")

    create_TAZ_file(TAZfileName, zones)

    args = [
        "-n", network_file, 
        "-r", TAZfileName
    ]

    SUMO_CMD = get_sumo_cmd(args, gui=True)

    traci.start(SUMO_CMD)

    # Add polygon showing danger taz
    traci.polygon.add(
        polygonID="dangerZonePoly",
        shape=danger_TAZ.shape,
        color=danger_TAZ.color,  # RGBA
        fill=True,
        layer=0 # lowest so that everz other thing shows
    )
    
    traci.close()
