
"""Module responsible for displaying the simulation in the terminal"""

from src.graph import Graph


class Visualizer:
    """Display drone movements, hub occupancy and connection usage"""

    COLORS = {
        "black": "\033[30m",
        "red": "\033[31m",
        "green": "\033[32m",
        "yellow": "\033[33m",
        "blue": "\033[34m",
        "magenta": "\033[35m",
        "cyan": "\033[36m",
        "white": "\033[37m",
        "normal": "\033[37m",
        "priority": "\033[33m",
        "restricted": "\033[35m",
        "blocked": "\033[90m",
    }
    RESET = "\033[0m"

    def __init__(self, graph: Graph, nb_drones: int) -> None:
        """Initialize the visualizer."""
        self.graph = graph
        self.nb_drones = nb_drones
        self.positions: dict[int, str | None] = {
            drone_id: graph.start_hub_name
            for drone_id in range(1, nb_drones + 1)
        }
        self.transit: dict[int, str] = {}

    def _get_connection_key(self, hub_a: str, hub_b: str) -> str:
        """Return a consistent name for an undirected connection"""
        return "-".join(sorted((hub_a, hub_b)))

    def _get_color(self, hub_name: str) -> str:
        """Get the display color for a hub."""
        hub = self.graph.hubs[hub_name]
        color = hub.color or hub.zone
        return self.COLORS.get(color.lower(), "")

    def _update_positions(
        self,
        movements: str,
        connection_usage: dict[str, int],
    ) -> None:
        """Update drone positions and count connection usage"""
        for movement in movements.split():
            drone_label, destination = movement.split("-", 1)
            drone_id = int(drone_label[1:])

            if destination in self.graph.hubs:
                origin = self.positions[drone_id]

                if origin is not None:
                    key = self._get_connection_key(
                        origin,
                        destination,
                    )
                    connection_usage[key] = (
                        connection_usage.get(key, 0) + 1
                    )

                self.positions[drone_id] = destination
                self.transit.pop(drone_id, None)

            else:
                connection_usage[destination] = (
                    connection_usage.get(destination, 0) + 1
                )
                self.positions[drone_id] = None
                self.transit[drone_id] = destination

    def _display_hubs(self) -> None:
        """Display hub positions and current occupancy"""
        print("\nHUB OCCUPANCY")

        for name, hub in self.graph.hubs.items():
            color = self._get_color(name)

            drones = [
                f"D{drone_id}"
                for drone_id, position in self.positions.items()
                if position == name
            ]

            if name in (
                self.graph.start_hub_name,
                self.graph.end_hub_name,
            ):
                capacity = "unlimited"
            else:
                capacity = str(hub.max_drones)

            drone_list = ", ".join(drones) if drones else "-"

            print(
                f"{color}{name}{self.RESET} "
                f"({hub.x}, {hub.y}) "
                f"[{hub.zone}] "
                f"{len(drones)}/{capacity} "
                f"| Drones: {drone_list}"
            )

    def _display_connections(
        self,
        connection_usage: dict[str, int],
    ) -> None:
        """Display connection usage during the current turn"""
        print("\nCONNECTION USAGE")

        if not connection_usage:
            print("No connections used.")
            return

        for key, used in connection_usage.items():
            hub_a, hub_b = key.split("-", 1)
            connection = self.graph.get_connection(hub_a, hub_b)

            if connection is not None:
                capacity = connection.max_link_capacity
                print(f"{key}: {used}/{capacity}")

    def display(self, history: list[str]) -> None:
        """Display the complete simulation turn by turn."""
        print("\n========== DRONE SIMULATION ==========")

        for turn, movements in enumerate(history, start=1):
            connection_usage: dict[str, int] = {}

            self._update_positions(movements, connection_usage)

            print(f"\n========== TURN {turn} ==========")
            print(f"Movements: {movements}")

            self._display_hubs()
            self._display_connections(connection_usage)

            if self.transit:
                print("\nDRONES IN TRANSIT")
                for drone_id, connection in self.transit.items():
                    print(f"D{drone_id}: {connection}")

        print("\n========== SIMULATION COMPLETE ==========")
