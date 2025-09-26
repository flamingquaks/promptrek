"""
Main CLI entry point for PrompTrek.

Provides the primary command-line interface for PrompTrek functionality.
"""

from pathlib import Path

import click

from ..core.exceptions import PrompTrekError
from .commands.generate import generate_command
from .commands.init import init_command
from .commands.sync import sync_command
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
@click.option(
    "--source-dir",
    "-s",
    type=click.Path(exists=True, file_okay=False, path_type=Path),
    default=".",
    help="Directory containing editor files to sync from",
)
@click.option(
    "--editor", "-e", 
    type=str, 
    required=True,
    help="Editor type to sync from (e.g., continue)"
)
@click.option(
    "--output", "-o", 
    type=click.Path(path_type=Path),
    help="Output PrompTrek file (defaults to project.promptrek.yaml)"
)
@click.option(
    "--dry-run",
    is_flag=True,
    help="Show what would be updated without making changes",
)
@click.option(
    "--force", "-f",
    is_flag=True,
    help="Overwrite existing files without confirmation",
)
@click.pass_context
def sync(ctx: click.Context, source_dir: Path, editor: str, output: Path, dry_run: bool, force: bool) -> None:
    """Sync editor-specific files to PrompTrek configuration."""
    try:
        sync_command(ctx, source_dir, editor, output, dry_run, force)
    except PrompTrekError as e:
        click.echo(f"Error: {e}", err=True)
        ctx.exit(1)
    except Exception as e:
        if ctx.obj.get("verbose"):
            raise
        click.echo(f"Unexpected error: {e}", err=True)
        ctx.exit(1)


@cli.command()
@click.argument("files", nargs=-1, type=click.Path(exists=True, path_type=Path))
@click.option(
    "--directory",
    "-d",
    type=click.Path(exists=True, file_okay=False, path_type=Path),
    help="Directory to search for .promptrek.yaml files",
)
@click.option(
    "--recursive", "-r", is_flag=True, help="Search recursively in directories"
)
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
    files: tuple[Path, ...],
    directory: Path,
    recursive: bool,
    editor: str,
    output: Path,
    dry_run: bool,
    all_editors: bool,
    variables: tuple,
) -> None:
    """Generate editor-specific prompts from universal prompt files."""
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

        generate_command(
            ctx,
            files,
            directory,
            recursive,
            editor,
            output,
            dry_run,
            all_editors,
            var_dict,
        )
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
    """List supported editors and their capabilities."""
    from ..adapters.registry import AdapterCapability
    from .commands.generate import registry

    # Get editors by capability
    project_file_adapters = registry.get_project_file_adapters()
    global_config_adapters = registry.get_global_config_adapters()
    ide_plugin_adapters = registry.get_adapters_by_capability(
        AdapterCapability.IDE_PLUGIN_ONLY
    )

    click.echo("AI Editor Support Status:")
    click.echo()

    if project_file_adapters:
        click.echo("✅ Project Configuration File Support:")
        click.echo(
            "   These editors support project-level configuration files that PrompTrek can generate:"
        )

        for adapter_name in sorted(project_file_adapters):
            try:
                info = registry.get_adapter_info(adapter_name)
                description = info.get("description", "No description")
                file_patterns = info.get("file_patterns", [])
                files_str = (
                    ", ".join(file_patterns) if file_patterns else "configuration files"
                )
                click.echo(f"   • {adapter_name:12} - {description} → {files_str}")
            except Exception:
                click.echo(f"   • {adapter_name:12} - Available")
        click.echo()

    if global_config_adapters:
        click.echo("ℹ️  Global Configuration Only:")
        click.echo(
            "   These tools use global settings (no project-level files generated):"
        )

        for adapter_name in sorted(global_config_adapters):
            try:
                info = registry.get_adapter_info(adapter_name)
                description = info.get("description", "No description")
                click.echo(
                    f"   • {adapter_name:12} - Configure through global settings or admin panel"
                )
            except Exception:
                click.echo(f"   • {adapter_name:12} - Global configuration only")
        click.echo()

    if ide_plugin_adapters:
        click.echo("🔧 IDE Configuration Only:")
        click.echo("   These tools are configured through IDE interface:")

        for adapter_name in sorted(ide_plugin_adapters):
            try:
                info = registry.get_adapter_info(adapter_name)
                click.echo(
                    f"   • {adapter_name:12} - Configure through IDE settings/preferences"
                )
            except Exception:
                click.echo(f"   • {adapter_name:12} - IDE configuration only")
        click.echo()

    # Usage examples
    click.echo("Usage Examples:")
    if project_file_adapters:
        example_editor = sorted(project_file_adapters)[0]
        click.echo(
            f"  Generate for specific editor:  promptrek generate config.yaml --editor {example_editor}"
        )
        click.echo(
            "  Generate for all supported:    promptrek generate config.yaml --all"
        )
    click.echo()

    click.echo(
        "Note: Only editors with 'Project Configuration File Support' will generate files."
    )
    click.echo(
        "      Other editors require manual configuration through their respective interfaces."
    )


if __name__ == "__main__":
    cli()
