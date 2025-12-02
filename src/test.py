import traci
import sumolib
import os

# Define the path to the SUMO executable
# Assuming SUMO_HOME is set and contains the path to the main directory
if 'SUMO_HOME' in os.environ:
    # Use sumo if you want to run without the graphical interface
    # SUMO_BINARY = os.path.join(os.environ['SUMO_HOME'], 'bin', 'sumo')
    # If you want to see the simulation, use:
    SUMO_BINARY = os.path.join(os.environ['SUMO_HOME'], 'bin', 'sumo-gui')
else:
    # hardcode path if env var not set
    SUMO_BINARY = "sumo"

vehicle_exit_times = {}
vehicle_depart_times = {}

def run_simulation():
    traci.start([SUMO_BINARY, "-n", "./data/neulengbach_sumo-webtools-osm.net.xml", "-r", "./data/routes.rou.xml"])
    
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