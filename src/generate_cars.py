import traci
from launcher import get_sumo_cmd
import xml.etree.ElementTree as ET
import random

def generate_vehicle_type(type_name, accel, decel, color, length, max_speed):
    traci.vehicletype.copy("DEFAULT_VEHTYPE", type_name)
    traci.vehicletype.setAccel(type_name, accel)
    traci.vehicletype.setDecel(type_name, decel)
    traci.vehicletype.setMaxSpeed(type_name, max_speed)
    traci.vehicletype.setLength(type_name, length)
    traci.vehicletype.setColor(type_name, color)

def generate_car(vehicle_type, position_x, position_y, depart_time=0 ): #didnt decide on how to initialize position yet
    veh_id = traci.vehicle.getIDCount() # no of currently running vehicles, since we start from 0 this gives the new id
    traci.vehicle.add(vehID=veh_id, typeID=vehicle_type, depart=depart_time, routeID="dynamicRoute") # add to simulation
    return veh_id

def getRandomEdge(xmlRoot, zone):
    # Find the Danger_Zone_0 TAZ
    danger_taz = root.find(".//taz[@id='" + zone + "']")
    if danger_taz is None:
        raise ValueError("TAZ Danger_Zone_0 not found")

    # Get all edges
    edges = danger_taz.attrib.get("edges", "").split()
    if not edges:
        raise ValueError("No edges defined in Danger_Zone_0")

    # Pick a random edge
    random_edge = random.choice(edges)

    return random_edge

if __name__ == "__main__":
    args = [
        "-n", "./data/neulengbach_sumo-webtools-osm.net.xml.gz",
        "-a", "./tmp/DangerTAZ.taz.xml",
    ]

    SUMO_CMD = get_sumo_cmd(args, gui=True)

    # Load the TAZ file
    taz_file = "./tmp/DangerTAZ.taz.xml"
    tree = ET.parse(taz_file)
    root = tree.getroot()

    dangerEdge = getRandomEdge(root, "Danger_Zone_0")
    print("Random edge in Danger_Zone_0:", dangerEdge)

    safeEdge = getRandomEdge(root, "Safe_Zone")
    print("Random edge in Safe_Zone:", safeEdge)

    traci.start(SUMO_CMD)
    print(traci.vehicle.getIDCount())

    type_name = "car"
    traci.route.add(routeID="dynamicRoute", edges=[dangerEdge, safeEdge]) #these edges are from the rout.xml file, we will try to find a better way of handlimg
    generate_vehicle_type(type_name, 2.6, 4.5, (0,0,1), 5, 70)
    generate_car(type_name,0,0,0)
    for _ in range(100): # car gets created at departer time (aftter in simulation step)
        traci.simulationStep()
    print(traci.vehicle.getIDCount())

    traci.close()
