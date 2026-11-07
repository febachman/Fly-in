
from src.graph import Graph
from typing import Any
import pytest


def _make_config() -> dict[str, Any]:
    """Create a simple configuration for graph tests"""

    return {
        "nb_drones": 3,
        "start_hub": {
            "name": "A",
            "x": 0,
            "y": 0,
            "zone": "normal",
            "color": "none",
            "max_drones": None,
        },
        "hubs": [
            {
                "name": "B",
                "x": 1,
                "y": 1,
                "zone": "normal",
                "color": "none",
                "max_drones": 1,
            },
        ],
        "end_hub": {
            "name": "C",
            "x": 2,
            "y": 2,
            "zone": "normal",
            "color": "none",
            "max_drones": None,
        },
        "connections": [
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
        ],
    }


def _make_alternative_config() -> dict[str, Any]:
    """Create a configuration with an alternative path"""

    config = _make_config()

    config["hubs"].append({
        "name": "D",
        "x": 1,
        "y": 2,
        "zone": "restricted",
        "color": "none",
        "max_drones": 1,
    })

    config["connections"].append({
        "from_hub": "A",
        "to": "D",
        "max_link_capacity": 1,
    })

    config["connections"].append({
        "from_hub": "D",
        "to": "C",
        "max_link_capacity": 1,
    })

    return config


def test_graph_creation() -> None:
    """Check that the graph is created with all hubs"""

    graph = Graph(_make_config())

    assert len(graph.hubs) == 3
    assert "A" in graph.hubs
    assert "B" in graph.hubs
    assert "C" in graph.hubs

    assert graph.start_hub_name == "A"
    assert graph.end_hub_name == "C"


def test_hub_attributes() -> None:
    """Check that hub information is preserved"""

    graph = Graph(_make_config())

    hub = graph.hubs["B"]

    assert hub.name == "B"
    assert hub.x == 1
    assert hub.y == 1
    assert hub.zone == "normal"
    assert hub.color == "none"
    assert hub.max_drones == 1


def test_connections_creation() -> None:
    """Check that all connections are stored"""

    graph = Graph(_make_config())

    assert len(graph.connections) == 2

    assert graph.connections[0].from_hub == "A"
    assert graph.connections[0].to == "B"

    assert graph.connections[1].from_hub == "B"
    assert graph.connections[1].to == "C"


def test_adjacency_is_bidirectional() -> None:
    """Check that connections work in both directions"""

    graph = Graph(_make_config())

    assert "B" in graph.adjacency["A"]
    assert "A" in graph.adjacency["B"]

    assert "C" in graph.adjacency["B"]
    assert "B" in graph.adjacency["C"]


def test_connection_with_unknown_source() -> None:
    """Check that connections cannot start from unknown hubs"""

    config = _make_config()
    config["connections"][0]["from_hub"] = "X"

    with pytest.raises(ValueError):
        Graph(config)


def test_connection_with_unknown_destination() -> None:
    """Check that connections cannot end at unknown hubs"""

    config = _make_config()
    config["connections"][0]["to"] = "X"

    with pytest.raises(ValueError):
        Graph(config)


def test_duplicate_connection() -> None:
    """Check that duplicate connections are rejected"""

    config = _make_config()

    config["connections"].append({
        "from_hub": "B",
        "to": "A",
        "max_link_capacity": 1,
    })

    with pytest.raises(ValueError):
        Graph(config)


def test_get_neighbors() -> None:
    """Check that neighboring hubs are returned"""

    graph = Graph(_make_config())

    neighbors = graph.get_neighbors("B")

    assert {hub.name for hub in neighbors} == {"A", "C"}


def test_get_neighbors_unknown_hub() -> None:
    """Check that unknown hubs raise an error"""

    graph = Graph(_make_config())

    with pytest.raises(ValueError):
        graph.get_neighbors("X")


def test_get_connection() -> None:
    """Check that a connection can be found in both directions"""

    graph = Graph(_make_config())

    connection = graph.get_connection("A", "B")

    assert connection is not None
    assert connection.from_hub == "A"
    assert connection.to == "B"
    assert connection.max_link_capacity == 1

    reverse_connection = graph.get_connection("B", "A")

    assert reverse_connection is connection


def test_get_connection_not_found() -> None:
    """Check that missing connections return None"""

    graph = Graph(_make_config())

    assert graph.get_connection("A", "C") is None


def test_get_connection_unknown_hub() -> None:
    """Check that unknown hubs raise an error"""

    graph = Graph(_make_config())

    with pytest.raises(ValueError):
        graph.get_connection("A", "X")


def test_is_accessible() -> None:
    """Check that accessible hubs return True"""

    graph = Graph(_make_config())

    assert graph.is_accessible("A") is True
    assert graph.is_accessible("B") is True


def test_blocked_hub_is_not_accessible() -> None:
    """Check that blocked hubs return False"""

    config = _make_alternative_config()
    config["hubs"][0]["zone"] = "blocked"

    graph = Graph(config)

    assert graph.is_accessible("B") is False
    assert graph.is_accessible("D") is True


def test_is_accessible_unknown_hub() -> None:
    """Check that unknown hubs raise an error"""

    graph = Graph(_make_config())

    with pytest.raises(ValueError):
        graph.is_accessible("X")


def test_movement_costs() -> None:
    """Check the movement cost of each accessible zone type"""

    config = _make_alternative_config()
    config["hubs"][0]["zone"] = "priority"

    graph = Graph(config)

    assert graph.get_movement_cost("A") == 1
    assert graph.get_movement_cost("B") == 1
    assert graph.get_movement_cost("D") == 2
    assert graph.get_movement_cost("C") == 1


def test_blocked_hub_has_no_movement_cost() -> None:
    """Check that blocked hubs have no movement cost"""

    config = _make_alternative_config()
    config["hubs"][0]["zone"] = "blocked"

    graph = Graph(config)

    assert graph.get_movement_cost("B") is None


def test_movement_cost_unknown_hub() -> None:
    """Check that unknown hubs raise an error"""

    graph = Graph(_make_config())

    with pytest.raises(ValueError):
        graph.get_movement_cost("X")


def test_is_priority() -> None:
    """Check whether a hub belongs to a priority zone"""

    config = _make_config()
    config["hubs"][0]["zone"] = "priority"

    graph = Graph(config)

    assert graph.is_priority("B") is True
    assert graph.is_priority("A") is False


def test_is_priority_unknown_hub() -> None:
    """Check that unknown hubs raise an error"""

    graph = Graph(_make_config())

    with pytest.raises(ValueError):
        graph.is_priority("X")


def test_disconnected_graph() -> None:
    """Check that disconnected graphs are rejected"""

    config = _make_config()
    config["connections"] = [
        {
            "from_hub": "A",
            "to": "B",
            "max_link_capacity": 1,
        },
    ]

    with pytest.raises(ValueError, match="No valid path"):
        Graph(config)


def test_blocked_path() -> None:
    """Check that a blocked hub cannot be part of the only path"""

    config = _make_config()
    config["hubs"][0]["zone"] = "blocked"

    with pytest.raises(ValueError, match="No valid path"):
        Graph(config)


def test_alternative_path_around_blocked_hub() -> None:
    """Check that an alternative path can avoid a blocked hub"""

    config = _make_alternative_config()
    config["hubs"][0]["zone"] = "blocked"

    graph = Graph(config)

    assert graph.is_accessible("D") is True
    assert graph.is_accessible("B") is False
