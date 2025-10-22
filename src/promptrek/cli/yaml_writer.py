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


def _list_representer(dumper: yaml.SafeDumper, data: list) -> yaml.SequenceNode:
    """
    Custom representer for lists that uses flow style for short lists.

    Args:
        dumper: YAML dumper instance
        data: List to represent

    Returns:
        YAML sequence node with appropriate style
    """
    # Use flow style (inline) for short lists without nested structures
    if len(data) <= 5 and all(
        isinstance(item, (str, int, float, bool)) or item is None for item in data
    ):
        return dumper.represent_sequence("tag:yaml.org,2002:seq", data, flow_style=True)
    # Use block style for longer or nested lists
    return dumper.represent_sequence("tag:yaml.org,2002:seq", data, flow_style=False)


# Register the custom representers
LiteralBlockScalarDumper.add_representer(str, _str_representer)
LiteralBlockScalarDumper.add_representer(list, _list_representer)


def write_promptrek_yaml(data: Dict[str, Any], output_path: Path) -> None:
    """
    Write PrompTrek YAML file with proper formatting.

    Uses literal block scalar (|) for multi-line strings like content fields,
    making the YAML more readable and maintainable.

    Args:
        data: Dictionary to write as YAML
        output_path: Path to write the YAML file
    """
    # Determine schema version and URL
    schema_version = data.get("schema_version", "3.0.0")
    if schema_version.startswith("3."):
        schema_url = "https://promptrek.ai/schema/v3.0.0.json"
    elif schema_version.startswith("2.1"):
        schema_url = "https://promptrek.ai/schema/v2.1.0.json"
    elif schema_version.startswith("2."):
        schema_url = "https://promptrek.ai/schema/v2.0.0.json"
    else:
        schema_url = None  # v1.x or unknown versions don't have schema

    with open(output_path, "w", encoding="utf-8") as f:
        # Write schema comment if applicable
        if schema_url:
            f.write(f"# yaml-language-server: $schema={schema_url}\n")

        yaml.dump(
            data,
            f,
            Dumper=LiteralBlockScalarDumper,
            default_flow_style=False,
            sort_keys=False,
            allow_unicode=True,
        )
