"""
YAML writing utilities for PrompTrek CLI commands.

Provides consistent YAML formatting across all commands that write .promptrek.yaml files.
"""

from pathlib import Path
from typing import Any, Dict

import yaml


class LiteralString(str):
    """String subclass to force literal block scalar style in YAML."""

    pass


class LiteralBlockScalarDumper(yaml.SafeDumper):
    """Custom YAML dumper that uses literal block scalar (|-) for multi-line strings."""

    def write_line_break(self, data=None):
        super().write_line_break(data)

    def choose_scalar_style(self):
        # Override to prefer literal style for multi-line strings
        if (
            isinstance(self.event, yaml.events.ScalarEvent)
            and self.event.value
            and "\n" in self.event.value
        ):
            return "|"
        return super().choose_scalar_style()


def _literal_str_representer(dumper: yaml.SafeDumper, data: str) -> yaml.ScalarNode:
    """Representer for LiteralString that forces literal block scalar style."""
    # Use '|' which produces a literal block scalar with final newline preserved
    # Force literal style even for strings with special characters
    if isinstance(data, str):
        return dumper.represent_scalar("tag:yaml.org,2002:str", data, style="|")
    return dumper.represent_scalar("tag:yaml.org,2002:str", data, style="|")


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
        # Convert to LiteralString to force literal block scalar (|-) style
        return _literal_str_representer(dumper, data)
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
LiteralBlockScalarDumper.add_representer(LiteralString, _literal_str_representer)
LiteralBlockScalarDumper.add_representer(str, _str_representer)
LiteralBlockScalarDumper.add_representer(list, _list_representer)


def _convert_multiline_strings(obj: Any) -> Any:
    """
    Recursively convert multi-line strings to LiteralString for proper YAML formatting.

    Args:
        obj: Object to process (dict, list, str, or other)

    Returns:
        Processed object with multi-line strings converted to LiteralString
    """
    if isinstance(obj, dict):
        return {key: _convert_multiline_strings(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [_convert_multiline_strings(item) for item in obj]
    elif isinstance(obj, str) and "\n" in obj:
        return LiteralString(obj)
    else:
        return obj


def write_promptrek_yaml(data: Dict[str, Any], output_path: Path) -> None:
    """
    Write PrompTrek YAML file with proper formatting.

    Uses literal block scalar (|-) for multi-line strings like content fields,
    making the YAML more readable and maintainable.

    Args:
        data: Dictionary to write as YAML
        output_path: Path to write the YAML file
    """
    # Convert multi-line strings to LiteralString for proper formatting
    processed_data = _convert_multiline_strings(data)

    # Determine schema version and URL
    schema_version = data.get("schema_version", "3.0.0")
    # Parse version for more precise comparison
    version_parts = schema_version.split(".")
    major = (
        int(version_parts[0])
        if len(version_parts) > 0 and version_parts[0].isdigit()
        else 0
    )
    minor = (
        int(version_parts[1])
        if len(version_parts) > 1 and version_parts[1].isdigit()
        else 0
    )

    if major == 3 and minor >= 1:
        schema_url = "https://promptrek.ai/schema/v3.1.0.json"
    elif major == 3:
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
            processed_data,
            f,
            Dumper=LiteralBlockScalarDumper,
            default_flow_style=False,
            sort_keys=False,
            allow_unicode=True,
        )
