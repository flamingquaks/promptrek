"""
Main CLI entry point for PrompTrek.

Provides the primary command-line interface for PrompTrek functionality.
"""

from pathlib import Path

import click

from ..core.exceptions import PrompTrekError
from .commands.generate import generate_command
from .commands.init import init_command
from .commands.validate import validate_command


@click.group()
@click.version_option(version="0.1.0")
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose output")
@click.pass_context
def cli(ctx: click.Context, verbose: bool) -> None:
    """
    PrompTrek - Universal AI editor prompt management.

    PrompTrek allows you to create prompts in a universal format and generate
    editor-specific prompts for GitHub Copilot, Cursor, Continue, and more.
    """
    ctx.ensure_object(dict)
    ctx.obj["verbose"] = verbose


@cli.command()
@click.option("--template", "-t", type=str, help="Template to use for initialization")
@click.option(
    "--output",
    "-o",
    type=click.Path(),
    default="project.promptrek.yaml",
    help="Output file path",
)
@click.pass_context
def init(ctx: click.Context, template: str, output: str) -> None:
    """Initialize a new universal prompt file."""
    try:
        init_command(ctx, template, output)
    except PrompTrekError as e:
        click.echo(f"Error: {e}", err=True)
        ctx.exit(1)
    except Exception as e:
        if ctx.obj.get("verbose"):
            raise
        click.echo(f"Unexpected error: {e}", err=True)
        ctx.exit(1)


@cli.command()
@click.argument("file", type=click.Path(exists=True, path_type=Path))
@click.option("--strict", is_flag=True, help="Treat warnings as errors")
@click.pass_context
def validate(ctx: click.Context, file: Path, strict: bool) -> None:
    """Validate a universal prompt file."""
    try:
        validate_command(ctx, file, strict)
    except PrompTrekError as e:
        click.echo(f"Error: {e}", err=True)
        ctx.exit(1)
    except Exception as e:
        if ctx.obj.get("verbose"):
            raise
        click.echo(f"Unexpected error: {e}", err=True)
        ctx.exit(1)


@cli.command()
@click.argument("file", type=click.Path(exists=True, path_type=Path))
@click.option(
    "--editor", "-e", type=str, help="Target editor (copilot, cursor, continue)"
)
@click.option(
    "--output", "-o", type=click.Path(path_type=Path), help="Output directory"
)
@click.option(
    "--dry-run",
    is_flag=True,
    help="Show what would be generated without creating files",
)
@click.option(
    "--all", "all_editors", is_flag=True, help="Generate for all target editors"
)
@click.option(
    "--var",
    "-V",
    "variables",
    multiple=True,
    help="Override variables (e.g., -V KEY=value)",
)
@click.pass_context
def generate(
    ctx: click.Context,
    file: Path,
    editor: str,
    output: Path,
    dry_run: bool,
    all_editors: bool,
    variables: tuple,
) -> None:
    """Generate editor-specific prompts from universal prompt file."""
    try:
        # Parse variable overrides
        var_dict = {}
        for var in variables:
            if "=" not in var:
                raise click.BadParameter(
                    f"Variable must be in format KEY=value, got: {var}"
                )
            key, value = var.split("=", 1)
            var_dict[key.strip()] = value.strip()

        generate_command(ctx, file, editor, output, dry_run, all_editors, var_dict)
    except PrompTrekError as e:
        click.echo(f"Error: {e}", err=True)
        ctx.exit(1)
    except Exception as e:
        if ctx.obj.get("verbose"):
            raise
        click.echo(f"Unexpected error: {e}", err=True)
        ctx.exit(1)


@cli.command()
def list_editors() -> None:
    """List supported editors."""
    from .commands.generate import registry

    # Get implemented editors from registry
    implemented_editors = set(registry.list_adapters())

    # All editors we plan to support
    all_editors = [
        ("copilot", "GitHub Copilot (.github/copilot-instructions.md)"),
        ("cursor", "Cursor (.cursorrules)"),
        ("continue", "Continue (.continue/config.json)"),
        ("claude", "Claude Code (context-based)"),
        ("cline", "Cline (terminal-based)"),
        ("codeium", "Codeium (context-based)"),
        ("kiro", "Kiro (AI-powered assistance)"),
        ("tabnine", "Tabnine (team configurations)"),
        ("amazon-q", "Amazon Q (comment-based)"),
        ("jetbrains", "JetBrains AI (IDE-integrated)"),
    ]

    click.echo("Supported editors:")
    for name, description in all_editors:
        status = "✅" if name in implemented_editors else "⏳"
        click.echo(f"  {status} {name:12} - {description}")

    click.echo("\nLegend:")
    click.echo("  ✅ Implemented")
    click.echo("  ⏳ Planned")


if __name__ == "__main__":
    cli()
