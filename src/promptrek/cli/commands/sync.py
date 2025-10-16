"""
Sync command implementation.

Handles reading editor-specific markdown files and updating/creating
PrompTrek configuration from them.
"""

from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union

import click

from ...adapters import registry
from ...core.exceptions import PrompTrekError, UPFParsingError
from ...core.models import (
    Instructions,
    ProjectContext,
    PromptMetadata,
    UniversalPrompt,
    UniversalPromptV2,
)
from ...core.parser import UPFParser
from ...utils.gitignore import configure_gitignore
from ..yaml_writer import write_promptrek_yaml


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
    if not adapter.supports_bidirectional_sync():
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

        # Check and apply ignore_editor_files configuration
        _apply_gitignore_config(merged_prompt, output_file.parent)


def _merge_metadata(existing_data: dict, parsed: UniversalPrompt) -> dict:
    """
    Merge metadata intelligently, preserving user-defined data.

    Args:
        existing_data: Existing configuration data
        parsed: Newly parsed data from editor files

    Returns:
        Updated metadata dictionary
    """
    if not parsed.metadata:
        return existing_data

    metadata = existing_data.get("metadata", {})

    # Prefer existing user-defined metadata over auto-generated
    # Only update if existing is empty or if parsed is from a real source
    if (
        parsed.metadata.title
        and not metadata.get("title")
        and parsed.metadata.author != "PrompTrek Sync"
    ):
        metadata["title"] = parsed.metadata.title

    if (
        parsed.metadata.description
        and not metadata.get("description")
        and parsed.metadata.author != "PrompTrek Sync"
    ):
        metadata["description"] = parsed.metadata.description

    # Update timestamp from parsed data or current time
    if parsed.metadata.updated:
        metadata["updated"] = parsed.metadata.updated
    else:
        metadata["updated"] = datetime.now().isoformat()[:10]  # YYYY-MM-DD

    existing_data["metadata"] = metadata
    return existing_data


def _merge_instructions(existing_data: dict, parsed: UniversalPrompt) -> dict:
    """
    Merge instructions intelligently, avoiding duplicates.

    Args:
        existing_data: Existing configuration data
        parsed: Newly parsed data from editor files

    Returns:
        Updated configuration with merged instructions
    """
    if not parsed.instructions:
        return existing_data

    if "instructions" not in existing_data:
        existing_data["instructions"] = {}

    parsed_instructions = parsed.instructions.model_dump(exclude_none=True)
    existing_instructions = existing_data.get("instructions", {})

    for category, new_instructions in parsed_instructions.items():
        if not new_instructions:
            continue

        if category not in existing_instructions:
            # New category - add all instructions
            existing_instructions[category] = list(new_instructions)
        else:
            # Merge with existing, preserving order and avoiding duplicates
            existing_list = existing_instructions[category] or []
            existing_set = set(existing_list)

            # Add new instructions that don't exist
            for instruction in new_instructions:
                if instruction not in existing_set:
                    existing_list.append(instruction)
                    existing_set.add(instruction)

            existing_instructions[category] = existing_list

    existing_data["instructions"] = existing_instructions
    return existing_data


def _merge_context(existing_data: dict, parsed: UniversalPrompt) -> dict:
    """
    Merge context information intelligently.

    Args:
        existing_data: Existing configuration data
        parsed: Newly parsed data from editor files

    Returns:
        Updated configuration with merged context
    """
    if not parsed.context:
        return existing_data

    existing_context = existing_data.get("context", {})
    parsed_context = parsed.context.model_dump(exclude_none=True)

    # Merge technologies additively
    if "technologies" in parsed_context:
        existing_techs = set(existing_context.get("technologies", []))
        new_techs = set(parsed_context["technologies"])
        existing_context["technologies"] = sorted(existing_techs | new_techs)

    # Update project type if not set or if parsed is more specific
    if parsed_context.get("project_type") and (
        not existing_context.get("project_type")
        or existing_context.get("project_type") == "application"
    ):
        existing_context["project_type"] = parsed_context["project_type"]

    # Update description if parsed has better info
    if parsed_context.get("description") and not existing_context.get("description"):
        existing_context["description"] = parsed_context["description"]

    existing_data["context"] = existing_context
    return existing_data


def _merge_prompts(
    existing: Union[UniversalPrompt, UniversalPromptV2],
    parsed: Union[UniversalPrompt, UniversalPromptV2],
    editor: str,
) -> Union[UniversalPrompt, UniversalPromptV2]:
    """
    Merge parsed prompt data with existing PrompTrek configuration.

    V1 and V2 are separate schemas - no cross-schema merging.
    - V2 + V2 = V2 (update content and documents)
    - V1 + V1 = V1 (merge instructions and context)
    - V2 + V1 = Replace with V2 (warn user)
    - V1 + V2 = Replace with V1 (warn user)

    Args:
        existing: Existing PrompTrek configuration
        parsed: Newly parsed data from editor files
        editor: Editor name being synced

    Returns:
        Merged UniversalPrompt or UniversalPromptV2
    """
    # V2 schema handling
    if isinstance(parsed, UniversalPromptV2):
        if isinstance(existing, UniversalPromptV2):
            # V2 + V2: Merge within V2 schema
            merged_data = existing.model_dump(exclude_none=True)
            merged_data["content"] = parsed.content

            # Update metadata timestamp
            metadata = merged_data.get("metadata", {})
            if parsed.metadata.updated:
                metadata["updated"] = parsed.metadata.updated
            else:
                metadata["updated"] = datetime.now().isoformat()[:10]
            merged_data["metadata"] = metadata

            # Update documents if present
            if parsed.documents:
                merged_data["documents"] = [
                    doc.model_dump(exclude_none=True) for doc in parsed.documents
                ]

            return UniversalPromptV2.model_validate(merged_data)
        else:
            # V1 exists, V2 parsed: Replace with V2 (no cross-schema merge)
            click.echo(
                "⚠️  Existing file is V1 schema, parsed files are V2. Replacing with V2 schema."
            )
            # Preserve metadata title/description from V1 if V2 has defaults
            if (
                parsed.metadata.title == "Continue AI Assistant"
                and existing.metadata.title
            ):
                parsed.metadata.title = existing.metadata.title
            if existing.metadata.description and not parsed.metadata.description:
                parsed.metadata.description = existing.metadata.description
            return parsed

    # V1 schema handling
    if isinstance(parsed, UniversalPrompt):
        if isinstance(existing, UniversalPrompt):
            # V1 + V1: Merge within V1 schema
            merged_data = existing.model_dump(exclude_none=True)

            # Use helper functions to merge each section
            merged_data = _merge_metadata(merged_data, parsed)
            merged_data = _merge_instructions(merged_data, parsed)
            merged_data = _merge_context(merged_data, parsed)

            # Ensure the target editor is included in targets
            targets = merged_data.get("targets", [])
            if not targets:
                targets = [editor]
            elif editor not in targets:
                targets.append(editor)
            merged_data["targets"] = targets

            return UniversalPrompt.model_validate(merged_data)
        else:
            # V2 exists, V1 parsed: Replace with V1 (no cross-schema merge)
            click.echo(
                "⚠️  Existing file is V2 schema, parsed files are V1. Replacing with V1 schema."
            )
            return parsed

    # All cases handled above - this line should never be reached
    raise PrompTrekError(
        f"Unexpected schema combination in merge: {type(existing)} + {type(parsed)}"
    )


def _preview_prompt(prompt: Union[UniversalPrompt, UniversalPromptV2]) -> None:
    """Preview the prompt that would be written."""
    click.echo("📄 Preview of configuration that would be written:")
    click.echo(f"  Title: {prompt.metadata.title}")
    click.echo(f"  Description: {prompt.metadata.description}")

    # V2 schema - show content length
    if isinstance(prompt, UniversalPromptV2):
        click.echo(f"  Content length: {len(prompt.content)} characters")
        if prompt.documents:
            click.echo(f"  Documents: {len(prompt.documents)} files")
    # V1 schema - show instructions
    elif prompt.instructions:
        instructions_data = prompt.instructions.model_dump(exclude_none=True)
        for category, instructions in instructions_data.items():
            if instructions:
                click.echo(f"  {category.title()}: {len(instructions)} instructions")


def _write_prompt_file(
    prompt: Union[UniversalPrompt, UniversalPromptV2], output_file: Path
) -> None:
    """Write prompt to YAML file with proper multi-line formatting."""
    prompt_data = prompt.model_dump(exclude_none=True, by_alias=True)
    write_promptrek_yaml(prompt_data, output_file)


def _apply_gitignore_config(
    prompt: Union[UniversalPrompt, UniversalPromptV2], project_dir: Path
) -> None:
    """
    Apply .gitignore configuration based on prompt settings.

    Args:
        prompt: The prompt configuration
        project_dir: Project directory
    """
    # Check if ignore_editor_files is set (default to True if not specified)
    ignore_editor_files = getattr(prompt, "ignore_editor_files", None)

    # Default to True if not specified
    if ignore_editor_files is None:
        ignore_editor_files = True

    if ignore_editor_files:
        configure_gitignore(project_dir, add_editor_files=True, remove_cached=False)
