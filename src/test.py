import traci
import sumolib

SUMO_BINARY = "sumo-gui"

vehicle_exit_times = {}
vehicle_depart_times = {}

def run_simulation():
    traci.start([SUMO_BINARY, "-n", "./data/neulengbach_sumo-webtools-osm.net.xml.gz", "-r", "./data/routes.rou.xml"])
    
    # Get all route IDs from the loaded routes file
    route_ids = traci.route.getIDList()  # returns list of route IDs
    print(route_ids)
    
    step = 0
    while traci.simulation.getMinExpectedNumber() > 0:
        traci.simulationStep()
        vehicle_ids = traci.vehicle.getIDList()  # vehicles currently on network
        print(vehicle_ids)
        step += 1

    traci.close()


if __name__ == "__main__":
    print("Running simulation")
    run_simulation()