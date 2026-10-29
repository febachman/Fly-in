"""Module responsible for reading and parsing
    the zone network configuration for fly-in."""

import re
from pathlib import Path
from typing import Dict, Union, Any


def _parse_metadata(metadata_str: str) -> Dict[str, Union[str, int]]:
    """Extract key-value pairs from inside brackets.

    Args:
        metadata_str: The string found inside brackets.

    Returns:
        A dictionary containing parsed metadata keys and values.
    """
    meta: Dict[str, Union[str, int]] = {}
    if not metadata_str:
        return meta

    matches = re.findall(r'([a-zA-Z_][a-zA-Z0-9_]*)=([^\s\]]+)', metadata_str)
    for key, value in matches:
        if value.isdigit():
            meta[key] = int(value)
        else:
            meta[key] = value
    return meta


def parse_config(filepath: Union[str, Path]) -> Dict[str, Any]:
    """Read the simulation config file and return a structured dictionary.

    Args:
        filepath: Path to the config file.

    Returns:
        A dict containing nb_drones, start_hub, end_hub, hubs, and connections.

    Raises:
        FileNotFoundError: If the configuration file does not exist.
        ValueError: If the file format contains invalid lines or syntax.
    """

    path = Path(filepath)
    if not path.exists():
        raise FileNotFoundError(f"Configuration file not found: {path}")

    result: Dict[str, Any] = {
        "nb_drones": 0,
        "start_hub": None,
        "end_hub": None,
        "hubs": [],
        "connections": []
    }

    with open(path, "r", encoding="utf-8") as file:
        for line_num, line in enumerate(file, 1):
            line = line.strip()

            if not line or line.startswith("#"):
                continue

            meta_match = re.search(r'\[(.*?)\]', line)
            metadata_str = meta_match.group(1) if meta_match else ""
            metadata = _parse_metadata(metadata_str)

            clean_line = re.sub(r'\[.*?\]', '', line).strip()

            if ":" not in clean_line:
                raise ValueError(
                    f"Invalid format at line {line_num}: '{line}'"
                )

            prefix, content = clean_line.split(":", 1)
            prefix = prefix.strip()
            content = content.strip()

            if prefix == "nb_drones":
                result["nb_drones"] = int(content)

            elif prefix in ("start_hub", "end_hub", "hub"):
                parts = content.split()
                if len(parts) < 3:
                    raise ValueError(
                        f"Invalid hub format at line {line_num}: '{line}'"
                    )

                name = parts[0]
                x = int(parts[1])
                y = int(parts[2])

                zone_val = metadata.get("zone", "normal")
                color_val = metadata.get("color", "none")
                max_drones_val = metadata.get("max_drones", 1)

                hub_data: Dict[str, Any] = {
                    "name": name,
                    "x": x,
                    "y": y,
                    "zone": str(zone_val),
                    "color": str(color_val),
                    "max_drones": int(str(max_drones_val))
                }

                if prefix == "start_hub":
                    result["start_hub"] = hub_data
                elif prefix == "end_hub":
                    result["end_hub"] = hub_data
                else:
                    result["hubs"].append(hub_data)

            elif prefix == "connection":
                if "-" not in content:
                    raise ValueError(
                        f"Invalid connection at line {line_num}: '{line}'"
                    )

                hub1, hub2 = content.split("-", 1)
                max_link_cap = metadata.get("max_link_capacity", 1)
                conn_data: Dict[str, Any] = {
                    "from_hub": hub1.strip(),
                    "to": hub2.strip(),
                    "max_link_capacity": int(str(max_link_cap))
                }
                result["connections"].append(conn_data)

            else:
                raise ValueError(
                    f"Unknown prefix '{prefix}' at line {line_num}"
                )

    return result
