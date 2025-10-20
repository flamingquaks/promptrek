#!/usr/bin/env python3
"""Generate JSON Schema files for Universal Prompt Format versions."""

import json
from pathlib import Path

from promptrek.core.models import UniversalPromptV2, UniversalPromptV3


def generate_schema(model_class, output_file: Path, title: str, description: str):
    """Generate JSON Schema for a Pydantic model."""
    schema = model_class.model_json_schema()
    
    # Add title and description
    schema["title"] = title
    schema["description"] = description
    
    # Add $schema reference
    schema["$schema"] = "http://json-schema.org/draft-07/schema#"
    
    # Write to file
    output_file.parent.mkdir(parents=True, exist_ok=True)
    with open(output_file, "w") as f:
        json.dump(schema, f, indent=2)
    
    print(f"Generated schema: {output_file}")


def main():
    """Generate all schema files."""
    # Get the repository root
    repo_root = Path(__file__).parent.parent
    schema_dir = repo_root / "gh-pages" / "schema"
    
    # Generate v2.0 schema (UniversalPromptV2 without plugins field documented)
    generate_schema(
        UniversalPromptV2,
        schema_dir / "v2.0.json",
        "Universal Prompt Format v2.0",
        "JSON Schema for Universal Prompt Format version 2.0 - Simplified markdown-first approach",
    )
    
    # Generate v2.1 schema (UniversalPromptV2 with plugins support)
    generate_schema(
        UniversalPromptV2,
        schema_dir / "v2.1.json",
        "Universal Prompt Format v2.1",
        "JSON Schema for Universal Prompt Format version 2.1 - Adds plugin support (MCP servers, commands, agents, hooks)",
    )
    
    # Generate v3.0 schema (UniversalPromptV3)
    generate_schema(
        UniversalPromptV3,
        schema_dir / "v3.0.json",
        "Universal Prompt Format v3.0",
        "JSON Schema for Universal Prompt Format version 3.0 - Top-level plugin fields (mcp_servers, commands, agents, hooks)",
    )
    
    print(f"\nAll schemas generated in: {schema_dir}")


if __name__ == "__main__":
    main()
