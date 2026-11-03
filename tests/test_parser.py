
from src.parser import ConfigParser
from pathlib import Path
import pytest


def _write_config(tmp_path: Path, content: str) -> Path:
    config = tmp_path / "config.txt"
    config.write_text(content, encoding="utf-8")
    return config


def test_valid_config(tmp_path: Path) -> None:
    config = _write_config(
        tmp_path,
        "nb_drones: 3\n"
        "start_hub: A 0 0\n"
        "hub: B 1 1\n"
        "end_hub: C 2 2\n"
        "connection: A-B\n"
        "connection: B-C\n"
    )

    parser = ConfigParser()
    result = parser.parse_file(config)

    assert result["nb_drones"] == 3
    assert result["start_hub"]["name"] == "A"
    assert result["end_hub"]["name"] == "C"
    assert len(result["hubs"]) == 1
    assert len(result["connections"]) == 2


def test_zero_drones_is_rejected(tmp_path: Path) -> None:
    config = _write_config(
        tmp_path,
        "nb_drones: 0\n"
        "start_hub: A 0 0\n"
        "end_hub: B 1 1\n"
    )

    parser = ConfigParser()

    with pytest.raises(ValueError):
        parser.parse_file(config)


def test_missing_start_hub_is_rejected(tmp_path: Path) -> None:
    config = _write_config(
        tmp_path,
        "nb_drones: 3\n"
        "hub: A 0 0\n"
        "end_hub: B 1 1\n"
    )

    parser = ConfigParser()

    with pytest.raises(ValueError):
        parser.parse_file(config)


def test_missing_end_hub_is_rejected(tmp_path: Path) -> None:
    config = _write_config(
        tmp_path,
        "nb_drones: 3\n"
        "start_hub: A 0 0\n"
        "hub: B 1 1\n"
    )

    parser = ConfigParser()

    with pytest.raises(ValueError):
        parser.parse_file(config)


def test_duplicate_hub_name_is_rejected(tmp_path: Path) -> None:
    config = _write_config(
        tmp_path,
        "nb_drones: 3\n"
        "start_hub: A 0 0\n"
        "hub: B 1 1\n"
        "hub: B 2 2\n"
        "end_hub: C 3 3\n"
    )

    parser = ConfigParser()

    with pytest.raises(ValueError):
        parser.parse_file(config)


def test_invalid_coordinates_are_rejected(tmp_path: Path) -> None:
    config = _write_config(
        tmp_path,
        "nb_drones: 3\n"
        "start_hub: A 0 0\n"
        "hub: B x 1\n"
        "end_hub: C 2 2\n"
    )

    parser = ConfigParser()

    with pytest.raises(ValueError):
        parser.parse_file(config)


def test_connection_to_undefined_hub_is_rejected(
    tmp_path: Path,
) -> None:
    config = _write_config(
        tmp_path,
        "nb_drones: 3\n"
        "start_hub: A 0 0\n"
        "hub: B 1 1\n"
        "end_hub: C 2 2\n"
        "connection: A-D\n"
    )

    parser = ConfigParser()

    with pytest.raises(ValueError):
        parser.parse_file(config)


def test_duplicate_connection_is_rejected(tmp_path: Path) -> None:
    config = _write_config(
        tmp_path,
        "nb_drones: 3\n"
        "start_hub: A 0 0\n"
        "hub: B 1 1\n"
        "end_hub: C 2 2\n"
        "connection: A-B\n"
        "connection: B-A\n"
    )

    parser = ConfigParser()

    with pytest.raises(ValueError):
        parser.parse_file(config)


def test_zero_capacity_is_rejected(tmp_path: Path) -> None:
    config = _write_config(
        tmp_path,
        "nb_drones: 3\n"
        "start_hub: A 0 0\n"
        "hub: B 1 1 [max_drones=0]\n"
        "end_hub: C 2 2\n"
    )

    parser = ConfigParser()

    with pytest.raises(ValueError):
        parser.parse_file(config)


def test_blocked_zone_is_recognized(tmp_path: Path) -> None:
    config = _write_config(
        tmp_path,
        "nb_drones: 3\n"
        "start_hub: A 0 0\n"
        "hub: B 1 1 [zone=blocked]\n"
        "end_hub: C 2 2\n"
    )

    parser = ConfigParser()
    result = parser.parse_file(config)

    assert result["hubs"][0]["zone"] == "blocked"
