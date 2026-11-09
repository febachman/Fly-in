# simulation.py — motor da simulação

# Será responsável por:
# 1. Criar e acompanhar todos os drones.
# 2. Determinar os movimentos de cada turno.
# 3. Controlar a ocupação dos hubs e das conexões.
# 4. Respeitar os tempos de deslocamento,
#    inclusive os 2 turnos das zonas restritas.
# 5. Evitar conflitos entre drones.
# 6. Repetir os turnos até todos chegarem ao destino.
# 7. Registrar os movimentos no formato exigido pelo projeto


"""Module responsible for coordinating the drone simulation."""

import heapq
from src.drone import Drone
from src.graph import Graph


class Simulation:
    """Coordinate drone movements across the map."""

    def __init__(self, graph: Graph, nb_drones: int) -> None:
        """Initialize the simulation and assign paths to drones"""

        if nb_drones <= 0:
            raise ValueError("The number of drones must be positive")

        self.graph = graph
        self.drones = self._create_drones(nb_drones)

        self.paths: dict[int, list[str]] = {}
        self.path_positions: dict[int, int] = {}
        self.path_usage: dict[str, int] = {}

        self.reserved_hubs: dict[str, int] = {}

        self.turn_count = 0
        self.history: list[str] = []

        self._assign_paths()

        if self.graph.start_hub_name == self.graph.end_hub_name:
            for drone in self.drones:
                drone.mark_delivered()

    def _create_drones(self, nb_drones: int) -> list[Drone]:
        """Create all drones at the starting hub"""

        start = self.graph.start_hub_name

        return [
            Drone(drone_id, start)
            for drone_id in range(1, nb_drones + 1)
        ]

    @staticmethod
    def _get_connection_key(hub1: str, hub2: str) -> str:
        """Return a direction-independent connection identifier"""

        return "-".join(sorted([hub1, hub2]))

    def _find_path(self, start: str) -> list[str]:
        """Find a path using movement cost, priority and route usage"""

        end = self.graph.end_hub_name

        if start == end:
            return [start]

        queue: list[tuple[int, int, int, str, list[str]]] = [
            (0, 0, 0, start, [start])
        ]

        best_scores: dict[str, tuple[int, int, int]] = {
            start: (0, 0, 0)
        }

        while queue:
            cost, priority_score, congestion, current, path = (
                heapq.heappop(queue)
            )

            current_score = (cost, priority_score, congestion)

            if best_scores.get(current) != current_score:
                continue

            if current == end:
                return path

            for neighbor in self.graph.get_neighbors(current):
                name = neighbor.name

                if not self.graph.is_accessible(name):
                    continue

                movement_cost = self.graph.get_movement_cost(name)

                if movement_cost is None:
                    continue

                edge_key = self._get_connection_key(current, name)

                next_score = (
                    cost + movement_cost,
                    priority_score - int(self.graph.is_priority(name)),
                    congestion
                    + self.path_usage.get(f"hub:{name}", 0)
                    + self.path_usage.get(f"edge:{edge_key}", 0),
                )

                if (
                    name not in best_scores
                    or next_score < best_scores[name]
                ):
                    best_scores[name] = next_score

                    heapq.heappush(
                        queue,
                        (
                            *next_score,
                            name,
                            path + [name],
                        ),
                    )

        raise ValueError("No valid path connects the start to the end")

    def _assign_paths(self) -> None:
        """Find and assign a path to every drone"""

        for drone in self.drones:
            path = self._find_path(self.graph.start_hub_name)

            self.paths[drone.drone_id] = path
            self.path_positions[drone.drone_id] = 0

            for hub in path[1:-1]:
                key = f"hub:{hub}"
                self.path_usage[key] = self.path_usage.get(key, 0) + 1

            for origin, destination in zip(path, path[1:]):
                edge_key = self._get_connection_key(
                    origin,
                    destination,
                )
                key = f"edge:{edge_key}"

                self.path_usage[key] = self.path_usage.get(key, 0) + 1

    def _get_occupancy(self) -> dict[str, int]:
        """Count the drones currently occupying each hub"""

        occupancy = {
            hub_name: 0
            for hub_name in self.graph.hubs
        }

        for drone in self.drones:
            if not drone.is_delivered and drone.current_hub is not None:
                occupancy[drone.current_hub] += 1

        return occupancy

    def _has_zone_space(
        self,
        destination: str,
        occupancy: dict[str, int],
    ) -> bool:
        """Check whether a hub has room for another drone"""

        if destination in (
            self.graph.start_hub_name,
            self.graph.end_hub_name,
        ):
            return True

        hub = self.graph.hubs[destination]

        if hub.max_drones is None:
            return True

        current = occupancy.get(destination, 0)
        reserved = self.reserved_hubs.get(destination, 0)

        return current + reserved < hub.max_drones

    def _get_remaining_cost(self, drone: Drone) -> int:
        """Calculate the remaining movement cost along a drone's path"""

        path = self.paths[drone.drone_id]
        position = self.path_positions[drone.drone_id]

        remaining = 0

        for hub_name in path[position + 1:]:
            cost = self.graph.get_movement_cost(hub_name)

            if cost is not None:
                remaining += cost

        return remaining

    def _advance_transits(
        self,
        occupancy: dict[str, int],
        movements: list[str],
    ) -> set[int]:
        """Complete restricted movements started during the previous turn"""

        completed: set[int] = set()

        for drone in self.drones:
            if not drone.is_in_transit:
                continue

            destination = drone.transit_destination

            if destination is None:
                raise RuntimeError("Drone has no transit destination")

            drone.complete_transit()
            completed.add(drone.drone_id)

            reserved = self.reserved_hubs.get(destination, 0)

            if reserved > 1:
                self.reserved_hubs[destination] = reserved - 1
            elif reserved == 1:
                del self.reserved_hubs[destination]

            if destination == self.graph.end_hub_name:
                drone.mark_delivered()
            else:
                occupancy[destination] += 1

            movements.append(f"D{drone.drone_id}-{destination}")

        return completed

    def _move_drones(
        self,
        occupancy: dict[str, int],
        movements: list[str],
        completed: set[int],
    ) -> None:
        """Move drones that are currently occupying hubs"""

        active_drones = [
            drone
            for drone in self.drones
            if (
                not drone.is_delivered
                and not drone.is_in_transit
                and drone.drone_id not in completed
            )
        ]

        active_drones.sort(
            key=lambda drone: (
                self._get_remaining_cost(drone),
                drone.drone_id,
            )
        )

        connection_usage: dict[str, int] = {}

        for drone in active_drones:
            current = drone.current_hub

            if current is None:
                continue

            path = self.paths[drone.drone_id]
            position = self.path_positions[drone.drone_id]

            if position >= len(path) - 1:
                continue

            destination = path[position + 1]

            connection = self.graph.get_connection(
                current,
                destination,
            )

            if connection is None:
                raise RuntimeError(
                    f"No connection between '{current}' and '{destination}'"
                )

            connection_key = self._get_connection_key(
                current,
                destination,
            )

            used = connection_usage.get(connection_key, 0)

            if used >= connection.max_link_capacity:
                continue

            if not self._has_zone_space(destination, occupancy):
                continue

            connection_name = (
                f"{connection.from_hub}-{connection.to}"
            )

            if self.graph.hubs[destination].zone == "restricted":
                occupancy[current] -= 1
                drone.start_transit(connection_name, destination)

                self.reserved_hubs[destination] = (
                    self.reserved_hubs.get(destination, 0) + 1
                )

                movements.append(
                    f"D{drone.drone_id}-{connection_name}"
                )

            else:
                occupancy[current] -= 1
                drone.move_to(destination)

                if destination == self.graph.end_hub_name:
                    drone.mark_delivered()
                else:
                    occupancy[destination] += 1

                movements.append(
                    f"D{drone.drone_id}-{destination}"
                )

            self.path_positions[drone.drone_id] += 1
            connection_usage[connection_key] = used + 1

    def _all_delivered(self) -> bool:
        """Check whether every drone has reached the end hub"""

        return all(drone.is_delivered for drone in self.drones)

    def run(self) -> list[str]:
        """Run the simulation until all drones are delivered"""

        while not self._all_delivered():
            self.turn_count += 1
            movements: list[str] = []

            occupancy = self._get_occupancy()

            completed = self._advance_transits(
                occupancy,
                movements,
            )

            self._move_drones(
                occupancy,
                movements,
                completed,
            )

            if not movements:
                raise RuntimeError("Simulation is stuck: no drone can move")

            self.history.append(" ".join(movements))

        return self.history
