"""
YAML writing utilities for PrompTrek CLI commands.

Provides consistent YAML formatting across all commands that write .promptrek.yaml files.
"""

from pathlib import Path
from typing import Any, Dict

import yaml


class LiteralBlockScalarDumper(yaml.SafeDumper):
    """Custom YAML dumper that uses literal block scalar (|) for multi-line strings."""

    pass


def _str_representer(dumper: yaml.SafeDumper, data: str) -> yaml.ScalarNode:
    """
    Custom representer for strings that uses literal block scalar for multi-line content.

    Args:
        dumper: YAML dumper instance
        data: String to represent

    Returns:
        YAML scalar node with appropriate style
    """
    if "\n" in data:
        # Use literal block scalar (|-) for multi-line strings
        return dumper.represent_scalar("tag:yaml.org,2002:str", data, style="|")
    return dumper.represent_scalar("tag:yaml.org,2002:str", data)


# Register the custom representer
LiteralBlockScalarDumper.add_representer(str, _str_representer)


def write_promptrek_yaml(data: Dict[str, Any], output_path: Path) -> None:
    """
    Write PrompTrek YAML file with proper formatting.

    Uses literal block scalar (|) for multi-line strings like content fields,
    making the YAML more readable and maintainable.

    Args:
        data: Dictionary to write as YAML
        output_path: Path to write the YAML file
    """
    with open(output_path, "w", encoding="utf-8") as f:
        yaml.dump(
            data,
            f,
            Dumper=LiteralBlockScalarDumper,
            default_flow_style=False,
            sort_keys=False,
            allow_unicode=True,
        )
