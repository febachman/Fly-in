
"""Module responsible for representing the zone network"""

from typing import Any
from collections import deque
from dataclasses import dataclass


@dataclass
class Hub:
    """Represent a hub in the map"""

    name: str
    x: int
    y: int
    zone: str
    color: str
    max_drones: int | None


@dataclass
class Connection:
    """Represent a connection between two hubs"""

    from_hub: str
    to: str
    max_link_capacity: int


class Graph:
    """Store and organize the hubs and connections of the map"""

    MOVEMENT_COSTS: dict[str, int] = {
        "normal": 1,
        "priority": 1,
        "restricted": 2,
    }

    def __init__(self, config: dict[str, Any]) -> None:
        self.hubs: dict[str, Hub] = {}
        self.connections: list[Connection] = []
        self.adjacency: dict[str, list[str]] = {}

        self.start_hub_name: str = config["start_hub"]["name"]
        self.end_hub_name: str = config["end_hub"]["name"]

        self._add_hub(config["start_hub"])

        for hub_data in config["hubs"]:
            self._add_hub(hub_data)

        self._add_hub(config["end_hub"])

        for connection_data in config["connections"]:
            self._add_connection(connection_data)

        self.validate_connectivity()

    def _add_hub(self, hub_data: dict[str, Any]) -> None:
        """Create and store a hub."""

        hub = Hub(
            name=hub_data["name"],
            x=hub_data["x"],
            y=hub_data["y"],
            zone=hub_data["zone"],
            color=hub_data["color"],
            max_drones=hub_data["max_drones"],
        )

        if hub.name in self.hubs:
            raise ValueError(f"Hub '{hub.name}' already exists")

        self.hubs[hub.name] = hub
        self.adjacency[hub.name] = []

    def _add_connection(self, connection_data: dict[str, Any]) -> None:
        """Create and store a bidirectional connection"""

        connection = Connection(
            from_hub=connection_data["from_hub"],
            to=connection_data["to"],
            max_link_capacity=connection_data["max_link_capacity"],
        )

        if connection.from_hub not in self.hubs:
            raise ValueError(
                f"Hub '{connection.from_hub}' does not exist"
            )

        if connection.to not in self.hubs:
            raise ValueError(
                f"Hub '{connection.to}' does not exist"
            )

        if connection.to in self.adjacency[connection.from_hub]:
            raise ValueError("Connection already exists")

        self.connections.append(connection)

        self.adjacency[connection.from_hub].append(connection.to)
        self.adjacency[connection.to].append(connection.from_hub)

    def get_neighbors(self, hub_name: str) -> list[Hub]:
        """Return all hubs directly connected to the given hub"""

        if hub_name not in self.hubs:
            raise ValueError(f"Hub '{hub_name}' does not exist")

        return [
            self.hubs[neighbor]
            for neighbor in self.adjacency[hub_name]
        ]

    def get_connection(
        self,
        hub1: str,
        hub2: str,
    ) -> Connection | None:
        """Return the connection between two hubs, if it exists"""

        if hub1 not in self.hubs:
            raise ValueError(f"Hub '{hub1}' does not exist")

        if hub2 not in self.hubs:
            raise ValueError(f"Hub '{hub2}' does not exist")

        for connection in self.connections:
            if (
                connection.from_hub == hub1
                and connection.to == hub2
            ) or (
                connection.from_hub == hub2
                and connection.to == hub1
            ):
                return connection

        return None

    def is_accessible(self, hub_name: str) -> bool:
        """Check whether a hub can be entered"""

        if hub_name not in self.hubs:
            raise ValueError(f"Hub '{hub_name}' does not exist")

        return self.hubs[hub_name].zone != "blocked"

    def get_movement_cost(self, hub_name: str) -> int | None:
        """Return the movement cost for entering a hub"""

        if hub_name not in self.hubs:
            raise ValueError(f"Hub '{hub_name}' does not exist")

        zone_type = self.hubs[hub_name].zone

        return self.MOVEMENT_COSTS.get(zone_type)

    def is_priority(self, hub_name: str) -> bool:
        """Check whether a hub belongs to a priority zone"""

        if hub_name not in self.hubs:
            raise ValueError(f"Hub '{hub_name}' does not exist")

        return self.hubs[hub_name].zone == "priority"

    def validate_connectivity(self) -> None:
        """Check whether a valid path connects the start and end hubs"""

        if not self.is_accessible(self.start_hub_name):
            raise ValueError("The start hub is inaccessible")

        if not self.is_accessible(self.end_hub_name):
            raise ValueError("The end hub is inaccessible")

        visited = {self.start_hub_name}
        queue = deque([self.start_hub_name])

        while queue:
            current_hub = queue.popleft()

            if current_hub == self.end_hub_name:
                return

            for neighbor in self.adjacency[current_hub]:
                if neighbor in visited:
                    continue

                if not self.is_accessible(neighbor):
                    continue

                visited.add(neighbor)
                queue.append(neighbor)

        raise ValueError("No valid path connects the start hub to the end hub")
