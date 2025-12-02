# Group Project: City Evacuation

Simulate and analyze the evacuation of at least 1,000 vehicles from a city center using
SUMO ([https://sumo.dlr.de/docs/index.html](https://sumo.dlr.de/docs/index.html)) and OpenStreetMap (OSM) data.

## Setup:

- Map: Choose any real city. Import a region into SUMO.
- Zone: Define a danger zone (e.g., 2 km radius).
- Demand: Generate 1,000 cars starting inside the zone, heading to safe areas outside.
- Event: A major road is dynamically blocked at simulation time.

## Scenarios to Implement:

1. Baseline: No blockage. Measure total evacuation time under normal conditions.
2. Informed: Road is blocked. Cars are informed and reroute globally to avoid the edge before reaching it.
3. Uninformed: Road is blocked. Cars are not informed until they physically reach the blockage. They must perform a U-Turn and replan locally.

## Analysis & Deliverables:

- Metrics: KPIs of choice (e.g. Total evacuation time, average time loss, queue lengths)
- Visualization: Visualizations of choice (e.g. plot comparison of evacuation curves (cumulative arrivals) and heatmaps of congestion)
- Submission: Python/TraCI scripts + Presentation Slides + Report