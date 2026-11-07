
from src.graph import Graph
from typing import Any
import pytest


def _make_config() -> dict[str, Any]:
    """Create a simple configuration for graph tests."""

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


def test_graph_creation() -> None:
    """Check that the graph is created with all hubs."""

    graph = Graph(_make_config())

    assert len(graph.hubs) == 3
    assert "A" in graph.hubs
    assert "B" in graph.hubs
    assert "C" in graph.hubs

    assert graph.start_hub_name == "A"
    assert graph.end_hub_name == "C"


def test_hub_attributes() -> None:
    """Check that hub information is preserved."""

    graph = Graph(_make_config())

    hub = graph.hubs["B"]

    assert hub.name == "B"
    assert hub.x == 1
    assert hub.y == 1
    assert hub.zone == "normal"
    assert hub.color == "none"
    assert hub.max_drones == 1


def test_connections_creation() -> None:
    """Check that all connections are stored."""

    graph = Graph(_make_config())

    assert len(graph.connections) == 2

    assert graph.connections[0].from_hub == "A"
    assert graph.connections[0].to == "B"

    assert graph.connections[1].from_hub == "B"
    assert graph.connections[1].to == "C"


def test_adjacency_is_bidirectional() -> None:
    """Check that connections work in both directions."""

    graph = Graph(_make_config())

    assert "B" in graph.adjacency["A"]
    assert "A" in graph.adjacency["B"]

    assert "C" in graph.adjacency["B"]
    assert "B" in graph.adjacency["C"]


def test_connection_with_unknown_source() -> None:
    """Check that connections cannot start from unknown hubs."""

    config = _make_config()
    config["connections"][0]["from_hub"] = "X"

    with pytest.raises(ValueError):
        Graph(config)


def test_connection_with_unknown_destination() -> None:
    """Check that connections cannot end at unknown hubs."""

    config = _make_config()
    config["connections"][0]["to"] = "X"

    with pytest.raises(ValueError):
        Graph(config)


def test_duplicate_connection() -> None:
    """Check that duplicate connections are rejected."""

    config = _make_config()

    config["connections"].append({
        "from_hub": "B",
        "to": "A",
        "max_link_capacity": 1,
    })

    with pytest.raises(ValueError):
        Graph(config)
