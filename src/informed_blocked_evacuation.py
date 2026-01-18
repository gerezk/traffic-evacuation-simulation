import traci
import xml.etree.ElementTree as ET

import generate_cars as gc
from utils import a, get_sumo_cmd
import generate_TAZs as gTAZ


args = [
    "-n", a("../data/neulengbach_sumo-webtools-osm.net.xml.gz"),
    "-a", a("../tmp/TAZ.taz.xml"),
]

SUMO_CMD = get_sumo_cmd(args, gui=True)

traci.start(SUMO_CMD)

# Load the TAZ file
taz_file = a("../tmp/TAZ.taz.xml")
tree = ET.parse(taz_file)
root = tree.getroot()

privateVehicleRoads = gc.getEdgesForVehicleType("private")
dangerRoads = gc.getEdgesFromTaz(root, "Danger_Zone_0")
safeRoads = gc.getEdgesFromTaz(root, "Safe_Zone")

safeTypedRoads = list(set(privateVehicleRoads) & set(safeRoads)) # both conditions
dangerTypedRoads = list(set(privateVehicleRoads) & set(dangerRoads)) # both conditions

dangerEdge = gc.getRandomEdge(dangerTypedRoads)
print("Random edge in Danger_Zone_0:", dangerEdge)

safeEdge = gc.getRandomEdge(safeTypedRoads)
print("Random edge in Safe_Zone:", safeEdge)
gTAZ.block_roads(dangerTypedRoads,10)

type_name = "car"
veh_type_name = "private"

traci.route.add(routeID="dynamicRoute", edges=[dangerEdge, safeEdge]) #these edges are from the rout.xml file, we will try to find a better way of handlimg

# gc.generate_vehicle_type(type_name, 2.6, 4.5, (0, 0, 255), 5, 70, veh_type_name)
# gc.generate_car(0, veh_type_name, "dynamicRoute", 0)

gc.generate_vehicle_type(veh_type_name, 2.6, 4.5, (0, 0, 255), 5, 70, veh_type_name)

dangerEdge = gc.getRandomEdge(dangerTypedRoads)
print("Random edge in Danger_Zone_0:", dangerEdge)

safeEdge = gc.getRandomEdge(safeTypedRoads)
print("Random edge in Safe_Zone:", safeEdge)

# if not gc.isRoutePossible(dangerEdge, safeEdge, veh_type_name):
#     continue  # pick new edges

route_id = "dynamicRoute" + str(0)
traci.route.add(routeID=route_id, edges=[dangerEdge, safeEdge]) #these edges are from the rout.xml file, we will try to find a better way of handlimg

gc.generate_car(0, veh_type_name, route_id, 0)
        
        # temporary obstructions: https://sumo.dlr.de/docs/Simulation/Routing.html#handling_of_temporary_obstructions
        # will reroute only when at the blocked road
        # traci.vehicle.setRoutingMode(carID, constants.ROUTING_MODE_IGNORE_TRANSIENT_PERMISSIONS)

        # blockEdge(safeEdge)



# temporary obstructions: https://sumo.dlr.de/docs/Simulation/Routing.html#handling_of_temporary_obstructions
# will reroute only when at the blocked road
# traci.vehicle.setRoutingMode(carID, constants.ROUTING_MODE_IGNORE_TRANSIENT_PERMISSIONS)

# blockEdge(safeEdge)

step = 0
while traci.simulation.getMinExpectedNumber() > 0:
    traci.simulationStep()
    vehicle_ids = traci.vehicle.getIDList()  # vehicles currently on network
    print(vehicle_ids)
    print("Count:" + str(traci.vehicle.getIDCount()))
    step += 1

traci.close()