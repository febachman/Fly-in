*This project has been created as part of the 42 curriculum by <fbachman>*

# Fly-in

## Description

**Fly-in** is a Python project that simulates multiple drones travelling through a network of connected hubs, from a starting hub to a destination hub.
The map is defined in a configuration file. Each hub has coordinates and may have specific properties, such as a zone type, a display color, or a maximum drone capacity. Connections between hubs may also have a maximum traversal capacity.
The goal is to coordinate all drones so they reach the destination while respecting movement costs, hub capacities, connection capacities, and restricted-zone rules.
The project focuses on object-oriented programming, graph representation, pathfinding, resource management, and simulation scheduling.

## Instructions

### Requirements

- Python 3.10 or later
- `make`
- Internet connection for the initial installation of development dependencies

### Installation

Clone the repository and enter the project directory:

```bash
git clone <repository-url>
cd <repository-directory>
```

Install the development dependencies and create the virtual environment:

```bash
make install
```

### Running the simulation

Run the program with the configuration file:

```bash
make run
```

The default configuration file is `config.txt`.

The simulation can also be started directly:

```bash
.venv/bin/python -m src.main config.txt
```

### Terminal visualization

To display the simulation with the graphical terminal representation:

```bash
make run ARGS=--visual
```

The visualization displays the map using hub coordinates, connection lines, zone colors, drone positions, and capacity information.

### Debugging

To run the program with Python's debugger:

```bash
make debug
```

### Code quality

Run the linter and static type checker:

```bash
make lint
```

Run the test suite:

```bash
make test
```

Remove generated caches:

```bash
make clean
```

## Configuration file

The simulation receives its map through a text configuration file.

The configuration supports:

- `nb_drones`: number of drones.
- `start_hub`: initial hub.
- `end_hub`: destination hub.
- `hub`: intermediate hub.
- `connection`: connection between two hubs.

Hubs are declared using one of the following keywords:

```text
start_hub: start 0 0 [color=green]
hub: intermediate 1 0 [zone=normal color=blue max_drones=2]
end_hub: goal 2 0 [color=red]
```

Connections are declared between two previously defined hubs:

```text
connection: start-intermediate
connection: intermediate-goal [max_link_capacity=2]
```

### Hub properties

Hubs are defined by their name and coordinates (`x`, `y`). Optional metadata can specify:

| Property | Description | Default |
|---|---|---|
| `zone` | Movement behavior of the hub: `normal`, `blocked`, `restricted`, or `priority` | `normal` |
| `color` | Display color associated with the hub | No color |
| `max_drones` | Maximum number of drones allowed in the hub at the same time | `1` |

The starting and destination hubs have unlimited capacity. The `max_drones` property does not limit them.

### Connection properties

| Property | Description | Default |
|---|---|---|
| `max_link_capacity` | Maximum number of drones that can traverse a connection during one turn | `1` |

Lines beginning with `#` are comments. Empty lines are ignored.

## Movement Rules

The simulation follows these movement rules:

- Normal zones require one turn to cross.
- Priority zones require one turn and are preferred during route selection.
- Restricted zones require two turns: one to enter transit and another to reach the destination hub.
- Blocked zones cannot be traversed.
- Hub capacity limits are respected. Start and end hubs have unlimited capacity.
- Connection capacity limits the number of drones that can traverse a connection simultaneously.
- Drones already delivered to the destination are no longer scheduled for movement.

## Algorithm and implementation
The project is organized into separate modules to keep configuration parsing, graph representation, drone behavior, simulation logic, and visualization independent.

### Object-oriented structure

The implementation is divided into modules with separate responsibilities:

| Module | Responsibility |
|---|---|
| `parser.py` | Reads and validates the configuration file |
| `graph.py` | Represents hubs and connections and validates graph connectivity |
| `drone.py` | Defines drone state and movement operations |
| `simulation.py` | Coordinates paths, occupancy, capacities, and turns |
| `visualizer.py` | Displays the simulation in the terminal. |
| `main.py` | Handles program execution and user-facing errors |
| `tests/` | Automated tests for the project modules. |

### Graph representation

The map is represented as a graph:

- Hubs are the graph's vertices.
- Connections are bidirectional edges.
- Each hub stores its name, coordinates, zone type, color, and capacity.
- Each connection stores the maximum number of drones that can use it during one turn.

The graph is built from the parsed configuration and checked for a valid route between the starting and destination hubs. Blocked zones are excluded from route validation and pathfinding.
A weighted shortest-path search is used to find routes. Movement costs account for the different zone types, while priority zones influence route selection.

### Pathfinding

The project uses a custom shortest-path search implemented with Python's `heapq`, rather than an external graph library.

The route selection considers:

- Movement cost associated with each destination hub.
- Preference for priority zones when comparing routes.
- Previously assigned route usage, to encourage distribution across available paths.

### Simulation and movement

The simulation coordinates drones turn by turn.

Each drone keeps track of its current hub, assigned route, route position, and delivery or transit status.

It considers:

- Hub occupancy.
- Connection capacity.
- Restricted-zone transit.
- Priority routes.
- Available space created by drones moving out of hubs.

During each turn, the simulation:

1. Updates drones that were already travelling through restricted zones.
2. Calculates current hub occupancy.
3. Schedules eligible drone movements.
4. Checks hub and connection capacities.
5. Records the movements made during that turn.

Normal and priority zones take one turn to enter. Restricted zones take two turns: the drone first enters transit and must arrive at the destination on the following turn. A drone cannot wait while in transit.

Blocked zones cannot be used.

The simulation stops when all drones have reached the destination or reports an error if no further movement is possible.

### Visualization and user experience

The current interface presents the simulation in the terminal, one line per turn.

Each movement is represented by the drone identifier followed by its destination:

A regular simulation prints the movements performed during each turn:

```text
D1-hub_a D2-hub_b
D1-goal D2-hub_c
D2-goal
```

Drones that do not move during a turn are omitted from that turn's output. Drones that have reached the destination are no longer included in subsequent turns.

Hub colors and coordinates are defined in the configuration file and provide the information needed for a graphical representation of the map.

The optional `--visual` mode provides a coordinate-based representation of the map directly in the terminal.

It includes:

- **Hub positions:** hubs are positioned according to their configured `x` and `y` coordinates.
- **Hub identifiers:** short numerical identifiers are used in the map to avoid overlapping long hub names.
- **Connections:** lines represent connections between hubs.
- **Zone colors:** configured hub colors are displayed when available; otherwise, zone colors are used.
- **Drone positions:** the hub legend displays the drones currently occupying each hub.
- **Hub occupancy:** current occupancy is displayed alongside the configured capacity.
- **Connection usage:** connection usage and capacity are displayed for each turn.
- **Restricted transit:** drones traveling through restricted connections are displayed separately.

### Map legend

- `[NN]`: hub identifier, with details available in the hub legend.
- `*`: connection used during the current turn.
- `-`: unused horizontal connection.
- `|`: unused vertical connection.

The visualization is updated after every simulation turn.

### Tests

The project includes tests for the main components:

- Drone creation, movement, transit, and delivery.
- Graph construction, connections, zone behavior, and connectivity.
- Configuration parsing and invalid input handling.
- Simulation movement, capacities, restricted zones, and output.
- Main program execution and error handling.

Run the complete test suite with:

```bash
make test
```

## Resources

### Documentation and references

- [Python documentation](https://docs.python.org/3/)
- [Python `heapq` documentation](https://docs.python.org/3/library/heapq.html)
- [Python `dataclasses` documentation](https://docs.python.org/3/library/dataclasses.html)
- [Python `collections` documentation](https://docs.python.org/3/library/collections.html)
- [Graph theory and shortest-path algorithms](https://www.geeksforgeeks.org/dsa/dijkstras-shortest-path-algorithm-greedy-algo-7/)
- [Graph theory and shortest-path algorithms](https://learngraphtheory.org/articles/shortest-path-algorithms.html)

### AI usage disclosure

AI tools were used as learning and development support during this project. Their assistance included explaining programming concepts, discussing algorithmic approaches, helping investigate errors, suggesting test cases, reviewing implementation decisions, and assisting with project documentation.
The project implementation was developed and reviewed as part of the learning process. AI-generated suggestions were evaluated and tested before being incorporated.






### Drone scheduling

The simulation coordinates drone movements turn by turn.

It considers:

- Hub occupancy.
- Connection capacity.
- Restricted-zone transit.
- Priority routes.
- Available space created by drones moving out of hubs.

The simulation continues until all drones reach the destination.


