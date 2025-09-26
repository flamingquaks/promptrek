"""
Sync command implementation.

Handles reading editor-specific markdown files and updating/creating
PrompTrek configuration from them.
"""

from pathlib import Path
from typing import Dict, List, Optional, Tuple

import click
import yaml

from ...adapters import registry
from ...core.exceptions import PrompTrekError, UPFParsingError
from ...core.models import UniversalPrompt, Instructions, PromptMetadata, ProjectContext
from ...core.parser import UPFParser


def sync_command(
    ctx: click.Context,
    source_dir: Path,
    editor: str,
    output_file: Optional[Path],
    dry_run: bool,
    force: bool,
) -> None:
    """
    Sync editor-specific files to PrompTrek configuration.

    Args:
        ctx: Click context
        source_dir: Directory containing editor files to read
        editor: Editor type to sync from
        output_file: Output PrompTrek file (defaults to project.promptrek.yaml)
        dry_run: Show what would be done without making changes
        force: Overwrite existing files without confirmation
    """
    if output_file is None:
        output_file = Path("project.promptrek.yaml")

    # Get the adapter for the specified editor
    try:
        adapter = registry.get(editor)
    except Exception:
        raise PrompTrekError(f"Unsupported editor: {editor}")

    # Check if adapter supports reverse parsing
    if not hasattr(adapter, "parse_files"):
        raise PrompTrekError(f"Editor '{editor}' does not support syncing from files")

    # Parse files from the source directory
    try:
        parsed_prompt = adapter.parse_files(source_dir)
    except Exception as e:
        raise PrompTrekError(f"Failed to parse {editor} files: {e}")

    # Handle existing PrompTrek file
    existing_prompt = None
    if output_file.exists():
        if not force and not dry_run:
            if not click.confirm(f"File {output_file} exists. Update it?"):
                click.echo("Sync cancelled.")
                return

        try:
            parser = UPFParser()
            existing_prompt = parser.parse_file(output_file)
        except Exception as e:
            click.echo(f"Warning: Could not parse existing file {output_file}: {e}")

    # Merge with existing configuration if present
    if existing_prompt:
        merged_prompt = _merge_prompts(existing_prompt, parsed_prompt, editor)
    else:
        merged_prompt = parsed_prompt

    # Write the result
    if dry_run:
        click.echo(f"🔍 Dry run mode - would write to: {output_file}")
        _preview_prompt(merged_prompt)
    else:
        _write_prompt_file(merged_prompt, output_file)
        click.echo(f"✅ Synced {editor} configuration to: {output_file}")


def _merge_prompts(
    existing: UniversalPrompt, parsed: UniversalPrompt, editor: str
) -> UniversalPrompt:
    """
    Merge parsed prompt data with existing PrompTrek configuration.

    Args:
        existing: Existing PrompTrek configuration
        parsed: Newly parsed data from editor files
        editor: Editor name being synced

    Returns:
        Merged UniversalPrompt
    """
    # Start with existing configuration
    merged_data = existing.model_dump()

    # Update instructions with parsed data
    if parsed.instructions:
        if "instructions" not in merged_data:
            merged_data["instructions"] = {}

        parsed_instructions = parsed.instructions.model_dump(exclude_none=True)
        for category, instructions in parsed_instructions.items():
            if instructions:  # Only merge non-empty instruction lists
                if category not in merged_data["instructions"]:
                    merged_data["instructions"][category] = []

                # Merge instructions, avoiding duplicates
                existing_list = merged_data["instructions"][category]
                if existing_list is None:
                    existing_list = []
                    merged_data["instructions"][category] = existing_list

                existing_set = set(existing_list)
                for instruction in instructions:
                    if instruction not in existing_set:
                        merged_data["instructions"][category].append(instruction)

    # Update metadata updated timestamp
    merged_data["metadata"]["updated"] = parsed.metadata.updated

    # Ensure the target editor is included
    if "targets" not in merged_data:
        merged_data["targets"] = []
    if editor not in merged_data["targets"]:
        merged_data["targets"].append(editor)

    return UniversalPrompt.model_validate(merged_data)


def _preview_prompt(prompt: UniversalPrompt) -> None:
    """Preview the prompt that would be written."""
    click.echo("📄 Preview of configuration that would be written:")
    click.echo(f"  Title: {prompt.metadata.title}")
    click.echo(f"  Description: {prompt.metadata.description}")

    if prompt.instructions:
        instructions_data = prompt.instructions.model_dump(exclude_none=True)
        for category, instructions in instructions_data.items():
            if instructions:
                click.echo(f"  {category.title()}: {len(instructions)} instructions")


def _write_prompt_file(prompt: UniversalPrompt, output_file: Path) -> None:
    """Write prompt to YAML file."""
    prompt_data = prompt.model_dump(exclude_none=True, by_alias=True)

    with open(output_file, "w", encoding="utf-8") as f:
        yaml.dump(prompt_data, f, default_flow_style=False, sort_keys=False)
