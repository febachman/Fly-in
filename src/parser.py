
"""Module responsible for reading and parsing the configuration."""

from pathlib import Path
from typing import Any, Dict, Set


class ConfigParser:
    """Read, parse and validate the simulation configuration."""

    VALID_ZONES = ("normal", "blocked", "restricted", "priority")

    def parse_file(self, filepath: str | Path) -> Dict[str, Any]:
        """Read a configuration file and return its structured data."""

        path = Path(filepath)

        if not path.exists():
            raise FileNotFoundError(f"File not found: {path}")
        if not path.is_file():
            raise ValueError(f"Not a valid file: {path}")

        result: Dict[str, Any] = {
            "nb_drones": 0,
            "start_hub": None,
            "end_hub": None,
            "hubs": [],
            "connections": []
        }

        hub_names: Set[str] = set()
        connections: Set[frozenset[str]] = set()
        first_line = True

        with path.open("r", encoding="utf-8") as file:
            for line_num, line in enumerate(file, 1):
                line = line.strip()

                if not line or line.startswith("#"):
                    continue

                metadata, clean_line = self._extract_metadata(
                    line, line_num
                )

                if ":" not in clean_line:
                    raise ValueError(f"Invalid format at line {line_num}")

                prefix, content = clean_line.split(":", 1)
                prefix = prefix.strip()
                content = content.strip()

                if first_line:
                    if prefix != "nb_drones":
                        raise ValueError(
                            f"First instruction must be nb_drones "
                            f"(line {line_num})"
                        )
                    first_line = False
                elif prefix == "nb_drones":
                    raise ValueError(
                        f"Duplicate nb_drones at line {line_num}"
                    )

                if prefix == "nb_drones":
                    if metadata or not content.isdigit():
                        raise ValueError(
                            f"Invalid nb_drones at line {line_num}"
                        )

                    result["nb_drones"] = int(content)

                    if result["nb_drones"] <= 0:
                        raise ValueError(
                            f"Invalid nb_drones at line {line_num}"
                        )

                elif prefix in ("start_hub", "end_hub", "hub"):
                    hub = self._parse_hub(
                        content, metadata, prefix, line_num
                    )
                    name = hub["name"]

                    if name in hub_names:
                        raise ValueError(
                            f"Duplicate hub '{name}' at line {line_num}"
                        )

                    if prefix == "start_hub":
                        if result["start_hub"] is not None:
                            raise ValueError(
                                f"Duplicate start_hub at line {line_num}"
                            )
                        result["start_hub"] = hub

                    elif prefix == "end_hub":
                        if result["end_hub"] is not None:
                            raise ValueError(
                                f"Duplicate end_hub at line {line_num}"
                            )
                        result["end_hub"] = hub

                    else:
                        result["hubs"].append(hub)

                    hub_names.add(name)

                elif prefix == "connection":
                    connection = self._parse_connection(
                        content, metadata, line_num
                    )

                    hub1 = connection["from_hub"]
                    hub2 = connection["to"]

                    if hub1 not in hub_names or hub2 not in hub_names:
                        raise ValueError(
                            f"Undefined hub in connection at line "
                            f"{line_num}"
                        )

                    pair = frozenset((hub1, hub2))

                    if pair in connections:
                        raise ValueError(
                            f"Duplicate connection at line {line_num}"
                        )

                    connections.add(pair)
                    result["connections"].append(connection)

                else:
                    raise ValueError(
                        f"Unknown instruction '{prefix}' "
                        f"at line {line_num}"
                    )

        start = result["start_hub"]
        end = result["end_hub"]

        if start is None:
            raise ValueError("Missing start_hub.")
        if end is None:
            raise ValueError("Missing end_hub.")
        if start["name"] == end["name"]:
            raise ValueError("Start and end hubs must be different.")

        return result

    def _extract_metadata(
        self, line: str, line_num: int
    ) -> tuple[dict[str, str | int], str]:
        """Extract metadata enclosed in brackets."""

        if "[" not in line and "]" not in line:
            return {}, line

        if "[" not in line or "]" not in line:
            raise ValueError(f"Invalid metadata at line {line_num}")

        before, _, after = line.partition("[")
        metadata_text, closing, remaining = after.partition("]")

        if not closing or remaining.strip() or "[" in metadata_text:
            raise ValueError(f"Invalid metadata at line {line_num}")

        return self._parse_metadata(metadata_text, line_num), before.strip()

    def _parse_metadata(
        self, metadata_text: str, line_num: int
    ) -> dict[str, str | int]:
        """Parse metadata key-value pairs."""

        metadata: dict[str, str | int] = {}

        for item in metadata_text.split():
            if "=" not in item:
                raise ValueError(
                    f"Invalid metadata '{item}' at line {line_num}"
                )

            key, value = item.split("=", 1)

            if not key or not value or key in metadata:
                raise ValueError(
                    f"Invalid metadata '{item}' at line {line_num}"
                )

            metadata[key] = int(value) if value.isdigit() else value

        if not metadata:
            raise ValueError(f"Empty metadata at line {line_num}")

        return metadata

    def _parse_hub(
        self,
        content: str,
        metadata: dict[str, str | int],
        prefix: str,
        line_num: int
    ) -> Dict[str, Any]:
        """Parse and validate a hub definition."""

        parts = content.split()

        if len(parts) != 3:
            raise ValueError(f"Invalid hub format at line {line_num}")

        name = parts[0]

        if "-" in name:
            raise ValueError(
                f"Hub name cannot contain '-' at line {line_num}"
            )

        try:
            x, y = int(parts[1]), int(parts[2])
        except ValueError:
            raise ValueError(
                f"Invalid coordinates at line {line_num}"
            ) from None

        if set(metadata) - {"zone", "color", "max_drones"}:
            raise ValueError(f"Unknown hub metadata at line {line_num}")

        zone = metadata.get("zone", "normal")
        color = metadata.get("color", "none")

        if not isinstance(zone, str) or zone not in self.VALID_ZONES:
            raise ValueError(f"Invalid zone at line {line_num}")

        if not isinstance(color, str) or not color:
            raise ValueError(f"Invalid color at line {line_num}")

        max_drones = None

        if prefix == "hub":
            max_drones = metadata.get("max_drones", 1)

            if not isinstance(max_drones, int) or max_drones <= 0:
                raise ValueError(
                    f"Invalid max_drones at line {line_num}"
                )

        return {
            "name": name,
            "x": x,
            "y": y,
            "zone": zone,
            "color": color,
            "max_drones": max_drones
        }

    def _parse_connection(
        self,
        content: str,
        metadata: dict[str, str | int],
        line_num: int
    ) -> Dict[str, Any]:
        """Parse and validate a connection definition."""

        if set(metadata) - {"max_link_capacity"}:
            raise ValueError(
                f"Unknown connection metadata at line {line_num}"
            )

        if content.count("-") != 1:
            raise ValueError(f"Invalid connection at line {line_num}")

        hub1, hub2 = (hub.strip() for hub in content.split("-", 1))

        if not hub1 or not hub2 or hub1 == hub2:
            raise ValueError(f"Invalid connection at line {line_num}")

        capacity = metadata.get("max_link_capacity", 1)

        if not isinstance(capacity, int) or capacity <= 0:
            raise ValueError(
                f"Invalid max_link_capacity at line {line_num}"
            )

        return {
            "from_hub": hub1,
            "to": hub2,
            "max_link_capacity": capacity
        }
