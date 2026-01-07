# based on gridDistricts.py in tools

import sumolib  
import traci
import math
from sumolib.miscutils import Colorgen 


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
        if edge not in danger_edges:
            generated_TAZ.edges.append(edge.getID())
    return generated_TAZ
    
def create_TAZ_file(outf_name, TAZ_list):
    with open(outf_name, 'w') as outf:
        sumolib.writeXMLHeader(outf, "$Id$", "additional")
        for taz in TAZ_list:
            taz.write(outf)
        outf.write("</additional>\n")

if __name__ == "__main__":
    SUMO_BINARY = "sumo-gui"
    network_file = "./data/neulengbach_sumo-webtools-osm.net.xml.gz"
    danger_TAZ = generateCircularDangerTAZ(network_file, 0, 1500, 1500, 1000)
    safeTAZ = generate_safeTAZ(network_file,danger_TAZ.edges)

    zones = [danger_TAZ, safeTAZ]
    TAZfileName = "DangerTAZ.taz.xml"
    create_TAZ_file(TAZfileName, zones)

    traci.start([SUMO_BINARY, "-n", network_file, "-r", TAZfileName])

    # Add polygon showing danger taz
    traci.polygon.add(
        polygonID="dangerZonePoly",
        shape=danger_TAZ.shape,
        color=danger_TAZ.color,  # RGBA
        fill=True,
        layer=0 # lowest so that everz other thing shows
    )
