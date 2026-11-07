
"""Module responsible for representing individual drones"""

from dataclasses import dataclass


@dataclass
class Drone:
    """Represent a drone and track its current state"""

    drone_id: int
    current_hub: str | None
    is_delivered: bool = False
    transit_connection: str | None = None
    transit_destination: str | None = None

    def __post_init__(self) -> None:
        """Validate the initial drone information"""

        if self.drone_id <= 0:
            raise ValueError("Drone ID must be a positive integer")

        if not self.current_hub:
            raise ValueError("Drone must start at a valid hub")

    @property
    def is_in_transit(self) -> bool:
        """Check whether the drone is currently crossing a connection"""

        return self.transit_connection is not None

    def move_to(self, destination: str) -> None:
        """Move the drone directly to an adjacent hub"""

        if self.is_delivered:
            raise ValueError("Delivered drones cannot move")

        if self.is_in_transit:
            raise ValueError("Drone must finish its transit first")

        if not destination:
            raise ValueError("Destination hub cannot be empty")

        self.current_hub = destination

    def start_transit(
        self,
        connection_name: str,
        destination: str,
    ) -> None:
        """Start a two-turn movement through a restricted connection"""

        if self.is_delivered:
            raise ValueError("Delivered drones cannot move")

        if self.is_in_transit:
            raise ValueError("Drone is already in transit")

        if not connection_name or not destination:
            raise ValueError("Connection and destination are required")

        self.current_hub = None
        self.transit_connection = connection_name
        self.transit_destination = destination

    def complete_transit(self) -> None:
        """Finish the transit and place the drone at its destination"""

        if not self.is_in_transit or self.transit_destination is None:
            raise ValueError("Drone is not in transit")

        self.current_hub = self.transit_destination
        self.transit_connection = None
        self.transit_destination = None

    def mark_delivered(self) -> None:
        """Mark the drone as delivered at its current hub"""

        if self.is_delivered:
            raise ValueError("Drone is already delivered")

        if self.is_in_transit or self.current_hub is None:
            raise ValueError("Drone must arrive at a hub before delivery")

        self.is_delivered = True
