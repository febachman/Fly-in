"""Tests for the drone simulation"""

from typing import Any
from src.graph import Graph
from src.simulation import Simulation
import pytest


def make_config(
    hubs: list[dict[str, Any]] | None = None,
    connections: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Create a basic map configuration for testing"""
    if hubs is None:
        hubs = [
            {
                "name": "B",
                "x": 1,
                "y": 0,
                "zone": "normal",
                "color": "none",
                "max_drones": 1,
            }
        ]

    if connections is None:
        connections = [
            {
                "from_hub": "A",
                "to": "B",
                "max_link_capacity": 1,
            },
            {
                "from_hub": "B",
                "to": "C",
                "max_link_capacity": 1,
            },
        ]

    return {
        "nb_drones": 1,
        "start_hub": {
            "name": "A",
            "x": 0,
            "y": 0,
            "zone": "normal",
            "color": "none",
            "max_drones": None,
        },
        "end_hub": {
            "name": "C",
            "x": 2,
            "y": 0,
            "zone": "normal",
            "color": "none",
            "max_drones": None,
        },
        "hubs": hubs,
        "connections": connections,
    }


def test_simulation_initialization() -> None:
    """Test that the simulation creates the correct number of drones"""
    graph = Graph(make_config())
    simulation = Simulation(graph, 3)

    assert len(simulation.drones) == 3
    assert all(drone.current_hub == "A" for drone in simulation.drones)
    assert len(simulation.paths) == 3


def test_simulation_rejects_zero_drones() -> None:
    """Test that the simulation rejects a non-positive drone count"""
    graph = Graph(make_config())

    with pytest.raises(ValueError):
        Simulation(graph, 0)


def test_find_path() -> None:
    """Test that the simulation finds a path to the end hub"""
    graph = Graph(make_config())
    simulation = Simulation(graph, 1)

    path = simulation._find_path("A")

    assert path == ["A", "B", "C"]


def test_priority_hub_is_preferred() -> None:
    """Test that a priority hub is preferred between equal-cost paths"""
    hubs = [
        {
            "name": "B",
            "x": 1,
            "y": 0,
            "zone": "normal",
            "color": "none",
            "max_drones": 1,
        },
        {
            "name": "D",
            "x": 1,
            "y": 1,
            "zone": "priority",
            "color": "none",
            "max_drones": 1,
        },
    ]
    connections = [
        {"from_hub": "A", "to": "B", "max_link_capacity": 1},
        {"from_hub": "B", "to": "C", "max_link_capacity": 1},
        {"from_hub": "A", "to": "D", "max_link_capacity": 1},
        {"from_hub": "D", "to": "C", "max_link_capacity": 1},
    ]
    graph = Graph(make_config(hubs, connections))
    simulation = Simulation(graph, 1)

    path = simulation._find_path("A")

    assert path == ["A", "D", "C"]


def test_run_with_one_drone() -> None:
    """Test that one drone reaches the end hub"""
    graph = Graph(make_config())
    simulation = Simulation(graph, 1)

    history = simulation.run()

    assert history == ["D1-B", "D1-C"]
    assert simulation.drones[0].is_delivered


def test_run_with_multiple_drones() -> None:
    """Test that multiple drones reach the end hub"""
    graph = Graph(make_config())
    simulation = Simulation(graph, 2)

    history = simulation.run()

    assert history == [
        "D1-B",
        "D1-C D2-B",
        "D2-C",
    ]
    assert all(drone.is_delivered for drone in simulation.drones)


def test_hub_capacity_is_respected() -> None:
    """Test that only one drone occupies a limited-capacity hub"""
    graph = Graph(make_config())
    simulation = Simulation(graph, 2)

    history = simulation.run()

    assert history[0] == "D1-B"
    assert history[1] == "D1-C D2-B"


def test_connection_capacity_is_respected() -> None:
    """Test that only one drone uses a limited-capacity connection per turn"""
    graph = Graph(make_config())
    simulation = Simulation(graph, 2)

    history = simulation.run()

    first_turn_movements = history[0].split()

    assert len(first_turn_movements) == 1
    assert first_turn_movements[0] == "D1-B"


def test_restricted_hub_requires_two_turns() -> None:
    """Test that entering a restricted hub takes two turns"""
    hubs = [
        {
            "name": "R",
            "x": 1,
            "y": 0,
            "zone": "restricted",
            "color": "none",
            "max_drones": 1,
        }
    ]
    connections = [
        {"from_hub": "A", "to": "R", "max_link_capacity": 1},
        {"from_hub": "R", "to": "C", "max_link_capacity": 1},
    ]
    graph = Graph(make_config(hubs, connections))
    simulation = Simulation(graph, 1)

    history = simulation.run()

    assert history == [
        "D1-A-R",
        "D1-R",
        "D1-C",
    ]
    assert simulation.drones[0].is_delivered
