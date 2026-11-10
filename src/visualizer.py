
"""Module responsible for displaying the simulation in the terminal"""

import shutil

from src.graph import Graph


class Visualizer:
    """Display drone movements, hub occupancy and connections"""

    COLORS = {
        "black": "\033[30m",
        "red": "\033[31m",
        "green": "\033[32m",
        "yellow": "\033[33m",
        "blue": "\033[34m",
        "magenta": "\033[35m",
        "cyan": "\033[36m",
        "white": "\033[37m",
        "normal": "\033[34m",
        "priority": "\033[33m",
        "restricted": "\033[35m",
        "blocked": "\033[90m",
    }
    RESET = "\033[0m"
    HIGHLIGHT = "\033[1;32m"

    def __init__(self, graph: Graph, nb_drones: int) -> None:
        """Initialize the visualizer."""
        self.graph = graph
        self.nb_drones = nb_drones
        self.positions: dict[int, str | None] = {
            drone_id: graph.start_hub_name
            for drone_id in range(1, nb_drones + 1)
        }
        self.transit: dict[int, str] = {}
        self.used_connections: set[str] = set()

        self.hub_ids = {
            name: f"{index:02}"
            for index, name in enumerate(graph.hubs, start=1)
        }

    def _get_connection_key(self, hub_a: str, hub_b: str) -> str:
        """Return a consistent name for an undirected connection"""
        return "-".join(sorted((hub_a, hub_b)))

    def _get_color(self, hub_name: str) -> str:
        """Get the display color for a hub."""
        hub = self.graph.hubs[hub_name]
        color = hub.color or hub.zone
        return self.COLORS.get(color.lower(), "")

    def _update_positions(self, movements: str) -> None:
        """Update drone positions and track used connections"""
        self.used_connections = set()

        for movement in movements.split():
            drone_label, destination = movement.split("-", 1)
            drone_id = int(drone_label[1:])

            if destination in self.graph.hubs:
                origin = self.positions[drone_id]

                if origin is not None:
                    self.used_connections.add(
                        self._get_connection_key(origin, destination)
                    )

                self.positions[drone_id] = destination
                self.transit.pop(drone_id, None)

            else:
                self.used_connections.add(destination)
                self.positions[drone_id] = None
                self.transit[drone_id] = destination

    def _display_map(self) -> None:
        """Display a coordinate-based map with numbered hubs"""
        terminal_width = shutil.get_terminal_size((100, 24)).columns
        cell_width = max(5, min(12, (terminal_width - 12) // max(
            1, len(self.graph.hubs)
        )))

        min_x = min(hub.x for hub in self.graph.hubs.values())
        max_x = max(hub.x for hub in self.graph.hubs.values())
        min_y = min(hub.y for hub in self.graph.hubs.values())
        max_y = max(hub.y for hub in self.graph.hubs.values())

        width = max(1, max_x - min_x + 1)
        height = max(1, max_y - min_y + 1)

        scale = min(
            4,
            max(1, (terminal_width - 8) // (width * cell_width)),
        )

        map_width = width * cell_width * scale
        map_height = height * 2

        canvas = [
            [" " for _ in range(map_width)]
            for _ in range(map_height)
        ]

        hub_positions: dict[str, tuple[int, int]] = {}

        for name, hub in self.graph.hubs.items():
            x = (hub.x - min_x) * cell_width * scale
            y = (max_y - hub.y) * 2
            hub_positions[name] = (x, y)

        for connection in self.graph.connections:
            start = connection.from_hub
            end = connection.to

            if start not in hub_positions or end not in hub_positions:
                continue

            x1, y1 = hub_positions[start]
            x2, y2 = hub_positions[end]

            key = self._get_connection_key(start, end)
            symbol = "*" if key in self.used_connections else "-"

            if y1 == y2:
                for x in range(min(x1, x2) + 3, max(x1, x2)):
                    if x < map_width:
                        canvas[y1][x] = symbol

            elif x1 == x2:
                for y in range(min(y1, y2) + 1, max(y1, y2)):
                    if y < map_height:
                        canvas[y][x1 + 1] = "|"

            else:
                for x in range(min(x1, x2) + 3, max(x1, x2)):
                    if y1 < map_height:
                        canvas[y1][x] = symbol

                step = 1 if y2 > y1 else -1
                for y in range(y1, y2, step):
                    if 0 <= y < map_height and x1 + 1 < map_width:
                        canvas[y][x1 + 1] = "|"

        for name, (x, y) in hub_positions.items():
            hub_id = self.hub_ids[name]
            label = f"[{hub_id}]"

            if x + len(label) <= map_width:
                for index, char in enumerate(label):
                    canvas[y][x + index] = char

        print("\nMAP")
        for line in canvas:
            print("".join(line).rstrip())

        print("\nHUB LEGEND")
        for name, hub in self.graph.hubs.items():
            color = self._get_color(name)
            drones = [
                f"D{drone_id}"
                for drone_id, position in self.positions.items()
                if position == name
            ]

            drone_list = ", ".join(drones) if drones else "-"
            capacity = (
                "unlimited"
                if name in (
                    self.graph.start_hub_name,
                    self.graph.end_hub_name,
                )
                else str(hub.max_drones)
            )

            print(
                f"{color}[{self.hub_ids[name]}] {name}{self.RESET} "
                f"({hub.x}, {hub.y}) [{hub.zone}] "
                f"{len(drones)}/{capacity} | {drone_list}"
            )

    def _display_connections(self) -> None:
        """Display connection usage during the current turn"""
        print("\nCONNECTION USAGE")

        for connection in self.graph.connections:
            key = self._get_connection_key(
                connection.from_hub,
                connection.to,
            )

            used = 1 if key in self.used_connections else 0
            color = self.HIGHLIGHT if used else ""

            print(
                f"{color}{key}: {used}/"
                f"{connection.max_link_capacity}{self.RESET}"
            )

    def display(self, history: list[str]) -> None:
        """Display the simulation turn by turn."""
        print("\n========== DRONE SIMULATION ==========")

        for turn, movements in enumerate(history, start=1):
            self._update_positions(movements)

            print(f"\n========== TURN {turn} ==========")
            print(f"Movements: {movements}")

            self._display_map()
            self._display_connections()

            if self.transit:
                print("\nDRONES IN TRANSIT")
                for drone_id, connection in self.transit.items():
                    print(f"D{drone_id}: {connection}")

        print("\n========== SIMULATION COMPLETE ==========")
