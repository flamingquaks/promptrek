"""
Spec management command implementations.

Handles listing and exporting spec-driven project documents.
"""

from pathlib import Path
from typing import Optional

import click

from ...core.exceptions import CLIError
from ...utils.spec_manager import SpecManager


def list_specs_command(ctx: click.Context) -> None:
    """
    List all registered spec-driven project documents.

    Args:
        ctx: Click context
    """
    verbose = ctx.obj.get("verbose", False)

    try:
        spec_manager = SpecManager(Path.cwd())
        specs = spec_manager.list_specs()

        if not specs:
            click.echo("📋 No specs registered yet.")
            click.echo(
                "\nUse /promptrek.spec.create in your editor to create a new spec."
            )
            return

        click.echo(f"📋 Found {len(specs)} spec(s):\n")

        for spec in specs:
            click.echo(f"  [{spec.id}] {spec.title}")
            click.echo(f"      Path: {spec.path}")
            click.echo(f"      Created: {spec.created}")
            if spec.updated:
                click.echo(f"      Updated: {spec.updated}")
            if spec.summary:
                click.echo(f"      Summary: {spec.summary}")
            if spec.tags:
                click.echo(f"      Tags: {', '.join(spec.tags)}")
            click.echo(f"      Source: {spec.source_command}")
            if spec.linked_specs:
                click.echo(f"      Linked: {', '.join(spec.linked_specs)}")
            click.echo()

    except Exception as e:
        if verbose:
            raise
        raise CLIError(f"Failed to list specs: {e}")


def spec_export_command(
    ctx: click.Context,
    spec_id: str,
    output: Optional[Path],
    clean: bool,
) -> None:
    """
    Export a spec to a markdown file.

    Args:
        ctx: Click context
        spec_id: ID of the spec to export
        output: Output file path
        clean: Remove metadata header from export
    """
    verbose = ctx.obj.get("verbose", False)

    try:
        spec_manager = SpecManager(Path.cwd())

        # Get spec metadata
        spec = spec_manager.get_spec_by_id(spec_id)
        if not spec:
            raise CLIError(f"Spec with ID '{spec_id}' not found")

        # Determine output path
        if output is None:
            # Generate filename from spec title
            filename = spec.path.replace(".md", "-export.md")
            output = Path.cwd() / filename

        # Export the spec
        spec_manager.export_spec(spec_id, output, clean=clean)

        click.echo(f"✅ Exported spec '{spec.title}' to: {output}")
        if clean:
            click.echo("   (Metadata header removed)")

    except CLIError:
        raise
    except Exception as e:
        if verbose:
            raise
        raise CLIError(f"Failed to export spec: {e}")
