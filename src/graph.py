
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

    def _add_hub(self, hub_data: dict[str, Any]) -> None:
        """Create and store a hub"""

        hub = Hub(
            name=hub_data["name"],
            x=hub_data["x"],
            y=hub_data["y"],
            zone=hub_data["zone"],
            color=hub_data["color"],
            max_drones=hub_data["max_drones"]
        )

        if hub.name in self.hubs:
            raise ValueError(f"Hub '{hub.name}' already exists")

        self.hubs[hub.name] = hub
        self.adjacency[hub.name] = []

    def _add_connection(
        self,
        connection_data: dict[str, Any]
    ) -> None:
        """Create and store a bidirectional connection"""

        connection = Connection(
            from_hub=connection_data["from_hub"],
            to=connection_data["to"],
            max_link_capacity=connection_data["max_link_capacity"]
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
