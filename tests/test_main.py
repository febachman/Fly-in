"""Tests for the main module"""

from src.main import main
from pathlib import Path
import pytest


def create_config_file(tmp_path: Path) -> Path:
    """Create a valid configuration file for testing"""
    config = """\
nb_drones: 1
start_hub: A 0 0
end_hub: C 2 0
hub: B 1 0
connection: A-B
connection: B-C
"""
    config_file = tmp_path / "config.txt"
    config_file.write_text(config, encoding="utf-8")
    return config_file


def test_main_runs_simulation(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Test that main runs the simulation and prints its output"""
    config_file = create_config_file(tmp_path)
    monkeypatch.setattr(
        "sys.argv",
        ["main.py", str(config_file)],
    )

    result = main()
    captured = capsys.readouterr()

    assert result == 0
    assert captured.out == "D1-B\nD1-C\n"
    assert captured.err == ""


def test_main_without_arguments(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Test that main reports an error when no file is provided"""
    monkeypatch.setattr("sys.argv", ["main.py"])

    result = main()
    captured = capsys.readouterr()

    assert result == 1
    assert "Usage:" in captured.err


def test_main_with_missing_file(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Test that main handles a configuration file that does not exist"""
    monkeypatch.setattr(
        "sys.argv",
        ["main.py", "missing_config.txt"],
    )

    result = main()
    captured = capsys.readouterr()

    assert result == 1
    assert "Error:" in captured.err
