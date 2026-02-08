from pathlib import Path
import shutil
import traci
import random
import xml.etree.ElementTree as ET


def a(path):
    """
    Return absolute path given a relative path
    Ensures compatability across platforms
    """
    return str((Path(__file__).parent / path).resolve())

# --------------------------------
# Sumo related functions below
# --------------------------------

# ----- Functions related to pathing and running sumo -----

def get_sumo_cmd(base_args, gui=True):
    """
    Needed to support use of the flatpack version of sumo
    base_args: list of SUMO arguments, e.g.
      ["-n", "net.xml", "-r", "routes.rou.xml", "--step-length", "0.1"]
    """
    binary = "sumo-gui" if gui else "sumo"

    if shutil.which(binary):
        return [binary] + base_args

    flatpak_id = "org.eclipse.sumo"

    return ["flatpak", "run", flatpak_id] + base_args

def get_root_TAZ(rel_path: str):
    abs_path = a(rel_path)
    tree = ET.parse(abs_path)
    root = tree.getroot()

    return root

def run_sim(danger_polygon) -> dict:
    """
    Run simulation and collect results.
    :return:
    """
    # structures to keep track of individual vehicles
    evacuation_time = {}  # vehID -> time
    was_inside = {}  # vehID -> bool

    while traci.simulation.getMinExpectedNumber() > 0:
        traci.simulationStep()
        t = traci.simulation.getTime()

        # get set of vehicles that have not yet evacuated
        vehicles_still_inside = set(traci.vehicle.getIDList()) # all vehicles in the sim at current time step
        vehicles_still_inside = vehicles_still_inside.difference(set(evacuation_time.keys()))

        # terminate sim if all cars evacuated, even if there are cars left still driving to their destinations
        if len(vehicles_still_inside) == 0:
            break

        # iterate over all vehicles still inside and check if they crossed into the safe zone
        for veh_id in vehicles_still_inside:
            x, y = traci.vehicle.getPosition(veh_id)
            inside = point_in_polygon(x, y, danger_polygon)

            if veh_id not in was_inside:
                was_inside[veh_id] = inside
                continue

            # mark vehicle's first exit from the danger zone
            if was_inside[veh_id] and not inside:
                evacuation_time[veh_id] = t
                # print(f"Vehicle {veh_id} evacuated at {t:.1f}s")

            was_inside[veh_id] = inside

    traci.close()

    return evacuation_time

# ----- Functions used to setup scenarios -----

def generate_car(veh_id, vehicle_type, route_id, depart_time=0 ):
    """
    Add car into simulation
    """
    traci.vehicle.add(vehID=veh_id, typeID=vehicle_type, depart=depart_time, routeID=route_id)

def initialize_cars(seed, n_cars, safe_roads, danger_roads, veh_type):
    """
    Initialize n_cars in simulation according to the seed and other arguments.
    Note tight coupling to other functions in utils.py
    :param seed: based on config file
    :param n_cars: from config file
    :param safe_roads: created using filter_edges_by_veh_type()
    :param danger_roads: created using filter_edges_by_veh_type()
    :param veh_type: str - should be "private"
    :return: None
    """
    random.seed(seed) # ensure reproducibility in using getRandomEdge
    
    for i in range(n_cars):
        dangerEdge = getRandomEdge(danger_roads, zone="Zone_0") #
        # print("Random edge in Zone_0:", dangerEdge)

        safeEdge = getRandomEdge(safe_roads, zone="Safe_Zone")
        # print("Random edge in Safe_Zone:", safeEdge)

        if not isRoutePossible(dangerEdge, safeEdge, veh_type):
            continue  # pick new edges

        route_id = "dynamicRoute" + str(i)
        traci.route.add(routeID=route_id, edges=[dangerEdge, safeEdge])

        generate_car(i, veh_type, route_id, 0)

        # temporary obstructions: https://sumo.dlr.de/docs/Simulation/Routing.html#handling_of_temporary_obstructions
        # will reroute only when at the blocked road

        # utils.blockEdge(safeEdge)

def generate_vehicle_type(type_name, accel, decel, color, length, max_speed, veh_class):
    traci.vehicletype.copy("DEFAULT_VEHTYPE", type_name)
    traci.vehicletype.setAccel(type_name, accel)
    traci.vehicletype.setDecel(type_name, decel)
    traci.vehicletype.setMaxSpeed(type_name, max_speed)
    traci.vehicletype.setLength(type_name, length)
    traci.vehicletype.setColor(type_name, color)
    traci.vehicletype.setVehicleClass(type_name, veh_class)

def getEdgesFromTaz(xmlRoot, zone):
    # Find the Zone_0 TAZ (Danger)
    danger_taz = xmlRoot.find(".//taz[@id='" + zone + "']")
    if danger_taz is None:
        raise ValueError("TAZ Danger_Zone_0 not found")

    # Get all edges
    edges = danger_taz.attrib.get("edges", "").split()

    return edges

def getPolygonFromTaz(xmlRoot, zone):
    # Find the Zone_0 TAZ (Danger)
    danger_taz = xmlRoot.find(".//taz[@id='" + zone + "']")
    if danger_taz is None:
        raise ValueError("TAZ Danger_Zone_0 not found")

    shape_str = danger_taz.attrib["shape"]
    polygon = [
        tuple(map(float, p.split(",")))
        for p in shape_str.split()
    ]
    return polygon

def point_in_polygon(x, y, polygon):
    inside = False
    n = len(polygon)
    px, py = polygon[0]

    for i in range(1, n + 1):
        nx, ny = polygon[i % n]
        if ((py > y) != (ny > y)) and \
           (x < (nx - px) * (y - py) / (ny - py + 1e-12) + px):
            inside = not inside
        px, py = nx, ny

    return inside

def filter_edges_by_veh_type(root, veh_type, safe_zone, danger_zone):
    """Note tight coupling to other functions in utils.py"""
    privateVehicleRoads = getEdgesForVehicleType(veh_type)
    safeRoads = getEdgesFromTaz(root, safe_zone)
    dangerRoads = getEdgesFromTaz(root, danger_zone)

    # Sort lists after to ensure order consistent across runs (reproducibility)
    safeTypedRoads = sorted(list(set(privateVehicleRoads) & set(safeRoads)))  # both conditions
    dangerTypedRoads = sorted(list(set(privateVehicleRoads) & set(dangerRoads)))  # both conditions

    return safeTypedRoads, dangerTypedRoads

def getRandomEdge(edges, zone):
    if not edges:
        raise ValueError(f"No edges defined in {zone}")

    # Pick a random edge
    random_edge = random.choice(edges)

    return random_edge

def getEdgesForVehicleType(vehicle_type: str):
    """
    Seems like the default type for car is called "private"
    """
    allowed_lanes = []

    # Get all lane IDs in the network
    all_lanes = traci.lane.getIDList()  # returns list of lane IDs

    for lane_id in all_lanes:
        allowed = traci.lane.getAllowed(lane_id)  # list of allowed vehicle types
        disallowed = traci.lane.getDisallowed(lane_id)  # list of allowed vehicle types
        if ((vehicle_type in allowed) or (not allowed)) and (
                vehicle_type not in disallowed):  # empty means all types allowed
            allowed_lanes.append(lane_id)

    allowed_edges = list({traci.lane.getEdgeID(lane_id) for lane_id in allowed_lanes})

    return allowed_edges

def blockEdge(edgeID, vehicleType):
    """
    Used for scenario 2 & 3
    The config file sets the edgeID
    """
    traci.edge.setDisallowed(edgeID, vehicleType)

def get_zone_names():
    """Hard-coded from TAZ file for now"""
    return "Safe_Zone", "Zone_0"

def isRoutePossible(from_edge, to_edge, vtype="car"):
    try:
        route = traci.simulation.findRoute(from_edge, to_edge, vType=vtype)
        return len(route.edges) > 0
    except traci.exceptions.TraCIException:
        return False

def get_reachable_danger_edges(safe_edges, danger_edges, vtype="private"):
    reachable_danger_edges = []
    for edge in danger_edges:
        if any(
                traci.simulation.findRoute(edge, safe, vType=vtype).edges
                for safe in safe_edges
        ):
            reachable_danger_edges.append(edge)
    return reachable_danger_edges