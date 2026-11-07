
"""Tests for the Drone class."""

import pytest

from src.drone import Drone


def test_drone_creation() -> None:
    drone = Drone(1, "A")

    assert drone.drone_id == 1
    assert drone.current_hub == "A"
    assert drone.is_delivered is False
    assert drone.transit_connection is None
    assert drone.transit_destination is None
    assert drone.is_in_transit is False


def test_drone_creation_with_invalid_id() -> None:
    with pytest.raises(ValueError):
        Drone(0, "A")

    with pytest.raises(ValueError):
        Drone(-1, "A")


def test_drone_creation_without_starting_hub() -> None:
    with pytest.raises(ValueError):
        Drone(1, "")

    with pytest.raises(ValueError):
        Drone(1, None)


def test_move_to_hub() -> None:
    drone = Drone(1, "A")

    drone.move_to("B")

    assert drone.current_hub == "B"
    assert drone.is_in_transit is False


def test_move_to_empty_destination() -> None:
    drone = Drone(1, "A")

    with pytest.raises(ValueError):
        drone.move_to("")


def test_cannot_move_while_in_transit() -> None:
    drone = Drone(1, "A")
    drone.start_transit("A-B", "B")

    with pytest.raises(ValueError):
        drone.move_to("C")


def test_cannot_move_after_delivery() -> None:
    drone = Drone(1, "C")
    drone.mark_delivered()

    with pytest.raises(ValueError):
        drone.move_to("D")


def test_start_transit() -> None:
    drone = Drone(1, "A")

    drone.start_transit("A-B", "B")

    assert drone.current_hub is None
    assert drone.transit_connection == "A-B"
    assert drone.transit_destination == "B"
    assert drone.is_in_transit is True


def test_start_transit_without_connection_or_destination() -> None:
    drone = Drone(1, "A")

    with pytest.raises(ValueError):
        drone.start_transit("", "B")

    with pytest.raises(ValueError):
        drone.start_transit("A-B", "")


def test_cannot_start_transit_while_already_in_transit() -> None:
    drone = Drone(1, "A")
    drone.start_transit("A-B", "B")

    with pytest.raises(ValueError):
        drone.start_transit("B-C", "C")


def test_cannot_start_transit_after_delivery() -> None:
    drone = Drone(1, "C")
    drone.mark_delivered()

    with pytest.raises(ValueError):
        drone.start_transit("C-D", "D")


def test_complete_transit() -> None:
    drone = Drone(1, "A")
    drone.start_transit("A-B", "B")

    drone.complete_transit()

    assert drone.current_hub == "B"
    assert drone.transit_connection is None
    assert drone.transit_destination is None
    assert drone.is_in_transit is False


def test_cannot_complete_transit_when_not_in_transit() -> None:
    drone = Drone(1, "A")

    with pytest.raises(ValueError):
        drone.complete_transit()


def test_mark_delivered() -> None:
    drone = Drone(1, "C")

    drone.mark_delivered()

    assert drone.is_delivered is True
    assert drone.current_hub == "C"


def test_cannot_mark_delivered_while_in_transit() -> None:
    drone = Drone(1, "A")
    drone.start_transit("A-B", "B")

    with pytest.raises(ValueError):
        drone.mark_delivered()


def test_cannot_mark_delivered_twice() -> None:
    drone = Drone(1, "C")
    drone.mark_delivered()

    with pytest.raises(ValueError):
        drone.mark_delivered()
