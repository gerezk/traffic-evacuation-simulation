# Planning
Let's do some planning here. These are just suggestions, please add your opinions

- Generate cars
    - define number of cars at the beginning of the simulation
      - each car has a vehicle type, here we can also lay with the idea of informed and uninformed drivers
      - cars have routes in principle, but most probaby we cannot have their routes at the beginning we have their routes 
    - define the danger zone 
      - can we do it graphically, or do we need to enter in the 
    - define number of cars outside danger zone (?)
    - generate the cars in specified areas
- Routing
  - We can possibly make use of [traffic assignment zones](https://sumo.dlr.de/docs/Definition_of_Vehicles%2C_Vehicle_Types%2C_and_Routes.html#traffic_assignment_zones_taz)
    - this allows defining zones of certain edges
  -[Automatic Routing](https://sumo.dlr.de/docs/Demand/Automatic_Routing.html): didnt even fully read yet but name looks helpful
- Measure metrics
    - possibly save everything to a file at the end of sim
- Visulaisations
- Use scenario
    - Let's discuss how do we run the smulation, how configurable it is, config files vs. selecting things on run time graphically 

Nice description of vehicles and routes: [see](https://sumo.dlr.de/docs/Definition_of_Vehicles%2C_Vehicle_Types%2C_and_Routes.html)

# Scenarios
## Baseline
- Generate TAZs: Safe, dangerous, blockage(?)
  - determine graphically or statically
- Generate certain number of cars (with router atribute- reroute: bool)inside danger TAZ, and maybe in safe TAZ as well
- Route for cars' current locaton to safe TAZ
- Measure
## Blockage - Informed
## Blockage - Uninformed
# XML files
- Describes the maps, routes, edges etc.
- I suggest we dont push so much of these file to git. We already have one example, We can keep most of them locally

# Config files
- will allow us to keep track of all the parameters we run (including the names of xml files)