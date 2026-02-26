# About this Repository

The repository was originally developed as a group project for the Modeling and Simulation course at the [Vienna University of Technology](https://www.tuwien.at/). My main contribution was refactoring the codebase to ensure reproducibility and enable easy setup of simulations.

Beyond the course, I did additional refactoring of the codebase.

# Setup

1. Download [SUMO](https://sumo.dlr.de/docs/Downloads.php).
2. Ensure that entering `sumo` or `sumo-gui` in the terminal activates the appropriate SUMO binaries. See this [page](https://sumo.dlr.de/docs/Basics/Basic_Computer_Skills.html#running_programs_from_the_command_line) for tips.
3. Install required packages
   ```
   pip install -r requirements.txt
   ```
   1. Python v3.12.12 was used.
4. Adjust `config.yaml` as needed and run `driver.py`.
