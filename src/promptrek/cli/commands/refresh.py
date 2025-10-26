"""
Refresh command implementation.

Regenerates editor files using last generation settings with updated dynamic variables.
"""

from pathlib import Path
from typing import Optional

import click
import yaml

from ...core.exceptions import CLIError
from ...core.models import GenerationMetadata
from ...core.parser import UPFParser


def refresh_command(
    ctx: click.Context,
    editor: Optional[str],
    all_editors: bool,
    dry_run: bool,
    clear_cache: bool,
) -> None:
    """
    Regenerate editor files with fresh dynamic variables.

    Uses metadata from last generation run (.promptrek/last-generation.yaml)
    to regenerate files with updated variable values.

    Args:
        ctx: Click context
        editor: Target editor to refresh (overrides last generation)
        all_editors: Refresh all editors from last generation
        dry_run: Show what would be refreshed without making changes
        clear_cache: Clear cached dynamic variables before refreshing
    """
    verbose = ctx.obj.get("verbose", False)

    # Load generation metadata
    metadata_file = Path.cwd() / ".promptrek/last-generation.yaml"

    if not metadata_file.exists():
        raise CLIError(
            "No generation metadata found. Run 'promptrek generate' first.\n"
            f"Expected metadata file: {metadata_file}"
        )

    try:
        with open(metadata_file, "r", encoding="utf-8") as f:
            metadata_dict = yaml.safe_load(f)

        # Validate metadata using Pydantic model
        metadata = GenerationMetadata.model_validate(metadata_dict)

        if verbose:
            click.echo(f"📋 Loaded generation metadata from {metadata_file}")
            click.echo(f"  Source file: {metadata.source_file}")
            click.echo(f"  Generated at: {metadata.timestamp}")
            click.echo(f"  Editors: {', '.join(metadata.editors)}")

    except Exception as e:
        raise CLIError(
            f"Failed to load generation metadata from {metadata_file}: {e}"
        ) from e

    # Determine which editors to refresh
    if editor:
        # User specified a specific editor (override)
        target_editors = [editor]
    elif all_editors:
        # Refresh all editors from last generation
        target_editors = metadata.editors
    else:
        # Default: refresh all editors from last generation
        target_editors = metadata.editors

    if verbose:
        click.echo(f"🔄 Refreshing for: {', '.join(target_editors)}")

    # Import generate_command to reuse generation logic
    from .generate import generate_command

    # Prepare arguments for generate command
    source_file = Path(metadata.source_file)

    if not source_file.exists():
        raise CLIError(
            f"Source file not found: {source_file}\n"
            "The file may have been moved or deleted since last generation."
        )

    # Build variables dict (will be overridden by CLI if user provided any)
    # The generate command will reload and re-evaluate all variables
    variables_dict = {}
    if ctx.params.get("variables"):
        # Convert CLI variables to dict
        for var in ctx.params.get("variables"):
            if "=" in var:
                key, value = var.split("=", 1)
                variables_dict[key.strip()] = value.strip()

    if dry_run:
        click.echo("🔍 Dry run mode - showing what would be refreshed:")

    # Call generate command for each target editor
    for target_editor in target_editors:
        try:
            if verbose:
                click.echo(f"\n🔄 Refreshing {target_editor}...")

            # Re-run generation with fresh variables
            generate_command(
                ctx=ctx,
                files=(source_file,),
                directory=None,
                recursive=False,
                editor=target_editor,
                output=Path(metadata.output_dir),
                dry_run=dry_run,
                all_editors=False,
                variables=variables_dict or None,
                headless=False,
            )

            if verbose and not dry_run:
                click.echo(f"✅ Refreshed {target_editor}")

        except Exception as e:
            click.echo(f"❌ Failed to refresh {target_editor}: {e}", err=True)
            if verbose:
                raise

    if not dry_run:
        click.echo(
            f"✅ Refresh complete for {len(target_editors)} editor(s)"
        )
