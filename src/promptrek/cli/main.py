"""
Main CLI entry point for PrompTrek.

Provides the primary command-line interface for PrompTrek functionality.
"""

from pathlib import Path
from typing import Optional

import click

from .. import __version__
from ..core.exceptions import PrompTrekError
from .commands.agents import agents_command
from .commands.config_ignores import config_ignores_command
from .commands.generate import generate_command
from .commands.hooks import check_generated_command, install_hooks_command
from .commands.init import init_command
from .commands.migrate import migrate_command
from .commands.plugins import (
    generate_plugins_command,
    list_plugins_command,
    validate_plugins_command,
)
from .commands.preview import preview_command
from .commands.sync import sync_command
from .commands.validate import validate_command


@click.group()
@click.version_option(version=__version__)
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
@click.option(
    "--setup-hooks",
    is_flag=True,
    help="Automatically set up and activate pre-commit hooks",
)
@click.option(
    "--v1",
    is_flag=True,
    help="Use v1 schema format (default is v2)",
)
@click.pass_context
def init(
    ctx: click.Context, template: str, output: str, setup_hooks: bool, v1: bool
) -> None:
    """Initialize a new universal prompt file.

    Creates a v2 format file by default (markdown-first approach).
    Use --v1 for legacy v1 format with structured fields.

    Use --setup-hooks to automatically configure pre-commit hooks after
    creating the file, making your project ready for development.
    """
    try:
        init_command(ctx, template, output, setup_hooks, use_v2=not v1)
    except PrompTrekError as e:
        click.echo(f"Error: {e}", err=True)
        ctx.exit(1)
    except Exception as e:
        if ctx.obj.get("verbose"):
            raise
        click.echo(f"Unexpected error: {e}", err=True)
        ctx.exit(1)


@cli.command()
@click.argument(
    "files", nargs=-1, type=click.Path(exists=True, path_type=Path), required=True
)
@click.option("--strict", is_flag=True, help="Treat warnings as errors")
@click.pass_context
def validate(ctx: click.Context, files: tuple[Path, ...], strict: bool) -> None:
    """Validate one or more universal prompt files."""
    has_error = False
    for file in files:
        try:
            validate_command(ctx, file, strict)
        except PrompTrekError as e:
            click.echo(f"Error: {e}", err=True)
            has_error = True
        except Exception as e:
            if ctx.obj.get("verbose"):
                raise
            click.echo(f"Unexpected error: {e}", err=True)
            has_error = True

    if has_error:
        ctx.exit(1)


@cli.command()
@click.argument("input-file", type=click.Path(exists=True, path_type=Path))
@click.option(
    "--output",
    "-o",
    type=click.Path(path_type=Path),
    help="Output file path (default: <input>.v2.promptrek.yaml)",
)
@click.option(
    "--force",
    "-f",
    is_flag=True,
    help="Overwrite output file if it exists",
)
@click.pass_context
def migrate(
    ctx: click.Context,
    input_file: Path,
    output: Optional[Path],
    force: bool,
) -> None:
    """Migrate a v1 .promptrek.yaml file to v2 format.

    The v2 format uses pure markdown content instead of structured fields,
    making it simpler and aligned with how AI editors actually work.

    By default, creates a new file with .v2.promptrek.yaml suffix.
    """
    try:
        migrate_command(ctx, input_file, output, force)
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
    "--editor",
    "-e",
    type=str,
    required=True,
    help="Target editor for preview",
)
@click.option(
    "--var",
    "-V",
    "variables",
    multiple=True,
    help="Variable override in KEY=VALUE format",
)
@click.pass_context
def preview(
    ctx: click.Context,
    file: Path,
    editor: str,
    variables: tuple,
) -> None:
    """Preview generated output without creating files."""
    try:
        # Parse variables
        var_dict = {}
        for var in variables:
            if "=" not in var:
                click.echo(f"Invalid variable format: {var}. Use KEY=VALUE", err=True)
                ctx.exit(1)
            key, value = var.split("=", 1)
            var_dict[key] = value

        preview_command(ctx, file, editor, var_dict if var_dict else None)
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
    "--editor",
    "-e",
    type=str,
    required=True,
    help="Editor type to sync from (e.g., continue)",
)
@click.option(
    "--output",
    "-o",
    type=click.Path(path_type=Path),
    help="Output PrompTrek file (defaults to project.promptrek.yaml)",
)
@click.option(
    "--dry-run",
    is_flag=True,
    help="Show what would be updated without making changes",
)
@click.option(
    "--force",
    "-f",
    is_flag=True,
    help="Overwrite existing files without confirmation",
)
@click.pass_context
def sync(
    ctx: click.Context,
    source_dir: Path,
    editor: str,
    output: Path,
    dry_run: bool,
    force: bool,
) -> None:
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
@click.option(
    "--headless",
    is_flag=True,
    help="Generate with headless agent instructions for autonomous operation",
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
    headless: bool,
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
            headless,
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
@click.option(
    "--prompt-file",
    "-f",
    type=click.Path(path_type=Path),
    help="Universal prompt file to use (auto-detects if not specified)",
)
@click.option(
    "--output",
    "-o",
    type=click.Path(path_type=Path),
    help="Output directory for agent files (default: current directory)",
)
@click.option(
    "--dry-run",
    is_flag=True,
    help="Show what would be generated without creating files",
)
@click.option(
    "--force",
    is_flag=True,
    help="Overwrite existing agent files",
)
@click.pass_context
def agents(
    ctx: click.Context,
    prompt_file: Path,
    output: Path,
    dry_run: bool,
    force: bool,
) -> None:
    """Generate persistent agent instruction files.

    Creates agent instruction files (AGENTS.md, .github/copilot-instructions.md, etc.)
    that tell autonomous agents to use PrompTrek and follow the generated instructions.
    These files persist in your repository and help autonomous agents understand
    your project configuration.
    """
    try:
        agents_command(ctx, prompt_file, output, dry_run, force)
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
            "   These editors support project-level configuration files "
            "that PrompTrek can generate:"
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
            "   These tools use global settings " "(no project-level files generated):"
        )

        for adapter_name in sorted(global_config_adapters):
            try:
                info = registry.get_adapter_info(adapter_name)
                description = info.get("description", "No description")
                click.echo(
                    f"   • {adapter_name:12} - Configure through global "
                    "settings or admin panel"
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
                    f"   • {adapter_name:12} - Configure through IDE "
                    "settings/preferences"
                )
            except Exception:
                click.echo(f"   • {adapter_name:12} - IDE configuration only")
        click.echo()

    # Usage examples
    click.echo("Usage Examples:")
    if project_file_adapters:
        example_editor = sorted(project_file_adapters)[0]
        click.echo(
            f"  Generate for specific editor:  "
            f"promptrek generate config.yaml --editor {example_editor}"
        )
        click.echo(
            "  Generate for all supported:    " "promptrek generate config.yaml --all"
        )
    click.echo()

    click.echo(
        "Note: Only editors with 'Project Configuration File Support' "
        "will generate files."
    )
    click.echo(
        "      Other editors require manual configuration through their "
        "respective interfaces."
    )


@cli.command()
@click.option(
    "--config",
    "-c",
    type=click.Path(path_type=Path),
    help="Path to .pre-commit-config.yaml (defaults to .pre-commit-config.yaml)",
)
@click.option(
    "--force",
    "-f",
    is_flag=True,
    help="Overwrite existing hooks without confirmation",
)
@click.option(
    "--activate",
    "-a",
    is_flag=True,
    help="Automatically run 'pre-commit install' to activate hooks in git",
)
@click.pass_context
def install_hooks(
    ctx: click.Context,
    config: Optional[Path],
    force: bool,
    activate: bool,
) -> None:
    """Install PrompTrek pre-commit hooks.

    This command safely adds or updates PrompTrek hooks in your .pre-commit-config.yaml
    file. It will not affect any existing hooks you have configured.

    If .pre-commit-config.yaml doesn't exist, it will be created with PrompTrek hooks.
    If it exists, PrompTrek hooks will be added or updated while preserving other hooks.

    Use --activate to automatically run 'pre-commit install' after configuration,
    which activates the hooks in your git repository.
    """
    try:
        install_hooks_command(ctx, config, force, activate)
    except PrompTrekError as e:
        click.echo(f"Error: {e}", err=True)
        ctx.exit(1)
    except Exception as e:
        if ctx.obj.get("verbose"):
            raise
        click.echo(f"Unexpected error: {e}", err=True)
        ctx.exit(1)


@cli.command()
@click.argument("files", nargs=-1, required=True)
@click.pass_context
def check_generated(ctx: click.Context, files: tuple[str, ...]) -> None:
    """Check if files are generated by promptrek (used by pre-commit hook).

    This command is primarily used by pre-commit hooks to prevent committing
    generated AI editor configuration files.
    """
    try:
        check_generated_command(ctx, list(files))
    except PrompTrekError as e:
        click.echo(f"Error: {e}", err=True)
        ctx.exit(1)
    except Exception as e:
        if ctx.obj.get("verbose"):
            raise
        click.echo(f"Unexpected error: {e}", err=True)
        ctx.exit(1)


@cli.group()
@click.pass_context
def plugins(ctx: click.Context) -> None:
    """Manage plugin configurations (v2.1.0+).

    Plugin commands allow you to work with MCP servers, slash commands,
    agents, and hooks defined in your PrompTrek v2.1+ configuration.
    """
    pass


@plugins.command("list")
@click.option(
    "--file",
    "-f",
    "prompt_file",
    type=click.Path(path_type=Path),
    help="PrompTrek file to list plugins from (auto-detects if not specified)",
)
@click.pass_context
def plugins_list(ctx: click.Context, prompt_file: Optional[Path]) -> None:
    """List all configured plugins."""
    try:
        list_plugins_command(ctx, prompt_file)
    except PrompTrekError as e:
        click.echo(f"Error: {e}", err=True)
        ctx.exit(1)
    except Exception as e:
        if ctx.obj.get("verbose"):
            raise
        click.echo(f"Unexpected error: {e}", err=True)
        ctx.exit(1)


@plugins.command("generate")
@click.option(
    "--file",
    "-f",
    "prompt_file",
    type=click.Path(path_type=Path),
    help="PrompTrek file to generate from (auto-detects if not specified)",
)
@click.option(
    "--editor",
    "-e",
    type=str,
    help="Editor to generate for (claude, cursor, continue, windsurf, cline, amazon-q, kiro, or 'all')",
)
@click.option(
    "--output",
    "-o",
    "output_dir",
    type=click.Path(path_type=Path),
    help="Output directory (default: current directory)",
)
@click.option(
    "--dry-run",
    is_flag=True,
    help="Show what would be generated without creating files",
)
@click.option(
    "--force-system-wide",
    "-s",
    is_flag=True,
    help="Force system-wide configuration (skip project-level)",
)
@click.option(
    "--yes",
    "-y",
    is_flag=True,
    help="Auto-confirm all prompts (use with caution for system-wide changes)",
)
@click.pass_context
def plugins_generate(
    ctx: click.Context,
    prompt_file: Optional[Path],
    editor: Optional[str],
    output_dir: Optional[Path],
    dry_run: bool,
    force_system_wide: bool,
    yes: bool,
) -> None:
    """Generate plugin files for editors.

    Supports MCP servers, custom commands, agents, and hooks for v2.1+ schemas.

    Configuration Strategy:
    - Project-level configs are preferred when available
    - System-wide configs require confirmation (use --yes to auto-confirm)
    - Use --force-system-wide to skip project-level and use system configs

    Examples:
        # Generate for Claude with project-level config
        promptrek plugins generate --editor claude

        # Generate for Windsurf (system-wide only, will prompt for confirmation)
        promptrek plugins generate --editor windsurf

        # Auto-confirm system-wide changes
        promptrek plugins generate --editor windsurf --yes

        # Generate for all editors with plugin support
        promptrek plugins generate --editor all
    """
    try:
        # Store flags in context for commands to access
        ctx.obj["force_system_wide"] = force_system_wide
        ctx.obj["auto_confirm"] = yes

        generate_plugins_command(
            ctx, prompt_file, editor, output_dir, dry_run, force_system_wide, yes
        )
    except PrompTrekError as e:
        click.echo(f"Error: {e}", err=True)
        ctx.exit(1)
    except Exception as e:
        if ctx.obj.get("verbose"):
            raise
        click.echo(f"Unexpected error: {e}", err=True)
        ctx.exit(1)


@plugins.command("validate")
@click.option(
    "--file",
    "-f",
    "prompt_file",
    type=click.Path(path_type=Path),
    help="PrompTrek file to validate (auto-detects if not specified)",
)
@click.pass_context
def plugins_validate(ctx: click.Context, prompt_file: Optional[Path]) -> None:
    """Validate plugin configurations."""
    try:
        validate_plugins_command(ctx, prompt_file)
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
    "--config",
    "-c",
    type=click.Path(path_type=Path),
    help="Path to PrompTrek config file (auto-detects if not specified)",
)
@click.option(
    "--remove-cached",
    "-r",
    is_flag=True,
    help="Run 'git rm --cached' on existing committed files",
)
@click.option(
    "--dry-run",
    is_flag=True,
    help="Show what would be done without making changes",
)
@click.pass_context
def config_ignores(
    ctx: click.Context,
    config: Optional[Path],
    remove_cached: bool,
    dry_run: bool,
) -> None:
    """Configure .gitignore to exclude editor-specific files.

    This command adds editor file patterns to .gitignore and optionally
    removes them from git cache if they were previously committed.

    The command respects the ignore_editor_files setting in your PrompTrek
    configuration file.

    Examples:
        # Add patterns to .gitignore
        promptrek config-ignores

        # Add patterns and remove cached files
        promptrek config-ignores --remove-cached

        # Show what would be done
        promptrek config-ignores --dry-run
    """
    try:
        config_ignores_command(ctx, config, remove_cached, dry_run)
    except PrompTrekError as e:
        click.echo(f"Error: {e}", err=True)
        ctx.exit(1)
    except Exception as e:
        if ctx.obj.get("verbose"):
            raise
        click.echo(f"Unexpected error: {e}", err=True)
        ctx.exit(1)


if __name__ == "__main__":
    cli()
