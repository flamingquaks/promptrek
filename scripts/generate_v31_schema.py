#!/usr/bin/env python3
"""Generate JSON Schema for Universal Prompt Format v3.1 with workflow support."""

import json
from pathlib import Path

from promptrek.core.models import UniversalPromptV3


def main():
    """Generate v3.1 schema files."""
    # Get the repository root
    repo_root = Path(__file__).parent.parent
    schema_dir = repo_root / "gh-pages" / "schema"

    # Generate v3.1 schema from current UniversalPromptV3 model (includes workflow fields)
    schema = UniversalPromptV3.model_json_schema()

    # Add title and description
    schema["title"] = "Universal Prompt Format v3.1"
    schema["description"] = (
        "JSON Schema for Universal Prompt Format version 3.1 - "
        "Adds multi-step workflow support (multi_step, tool_calls, steps fields in commands)"
    )

    # Add $schema reference
    schema["$schema"] = "http://json-schema.org/draft-07/schema#"

    # Write v3.1.json
    v31_file = schema_dir / "v3.1.json"
    with open(v31_file, "w") as f:
        json.dump(schema, f, indent=2)
    print(f"Generated schema: {v31_file}")

    # Write v3.1.0.json (copy)
    v310_file = schema_dir / "v3.1.0.json"
    with open(v310_file, "w") as f:
        json.dump(schema, f, indent=2)
    print(f"Generated schema: {v310_file}")

    print("\nv3.1 schemas generated successfully!")
    print(
        "Note: v2.x and v3.0 schemas are NOT regenerated to maintain backward compatibility."
    )


if __name__ == "__main__":
    main()
