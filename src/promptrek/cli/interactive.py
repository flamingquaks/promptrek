"""
Interactive CLI wizard for PrompTrek.

Provides an interactive menu-driven interface for common PrompTrek workflows.
"""

import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

import click
import questionary
from questionary import Choice

from .. import __version__
from ..core.exceptions import PrompTrekError
from .commands.generate import generate_command
from .commands.init import init_command

BANNER = r"""
 ____                       _____         _
|  _ \ _ __ ___  _ __ ___  |_   _| __ ___| | __
| |_) | '__/ _ \| '_ ` _ \   | || '__/ _ \ |/ /
|  __/| | | (_) | | | | | |  | || | |  __/   <
|_|   |_|  \___/|_| |_| |_|  |_||_|  \___|_|\_\
"""


def print_banner() -> None:
    """Print the PrompTrek ASCII banner."""
    click.echo(click.style(BANNER, fg="cyan", bold=True))
    click.echo(
        click.style(
            f"Universal AI Editor Prompt Management (v{__version__})",
            fg="bright_white",
            bold=True,
        )
    )
    click.echo()


def check_existing_config() -> Optional[Path]:
    """Check if a PrompTrek config file exists in the current directory."""
    config_files = [
        "project.promptrek.yaml",
        "project.promptrek.yml",
        ".promptrek.yaml",
        ".promptrek.yml",
    ]
    for config_file in config_files:
        path = Path(config_file)
        if path.exists():
            return path
    return None


def workflow_init_project(ctx: click.Context) -> None:
    """Interactive workflow for initializing a new project."""
    click.echo(click.style("\n🚀 Initialize New Project", fg="cyan", bold=True))
    click.echo()

    # Check for existing config
    existing_config = check_existing_config()
    if existing_config:
        click.echo(
            click.style(
                f"⚠️  Found existing configuration: {existing_config}",
                fg="yellow",
            )
        )
        overwrite = questionary.confirm(
            "Do you want to overwrite it?",
            default=False,
        ).ask()
        if not overwrite:
            click.echo("Cancelled.")
            return
    else:
        click.echo(
            click.style("✓ No existing project.promptrek.yaml found", fg="green")
        )

    click.echo()

    # Select schema version
    schema_version = questionary.select(
        "Select schema version:",
        choices=[
            Choice("v3.0 (Current - Recommended)", value="v3"),
            Choice("v2.x (Legacy)", value="v2"),
            Choice("v1.0 (Not recommended)", value="v1"),
        ],
    ).ask()

    if schema_version is None:
        click.echo("Cancelled.")
        return

    # Setup hooks
    setup_hooks = questionary.confirm(
        "Setup pre-commit hooks?",
        default=True,
    ).ask()

    if setup_hooks is None:
        click.echo("Cancelled.")
        return

    # Configure .gitignore
    config_gitignore = questionary.confirm(
        "Add editor files to .gitignore?",
        default=True,
    ).ask()

    if config_gitignore is None:
        click.echo("Cancelled.")
        return

    click.echo()

    # Execute init command
    try:
        use_v2 = schema_version != "v1"
        init_command(
            ctx,
            template=None,
            output="project.promptrek.yaml",
            setup_hooks=setup_hooks,
            use_v2=use_v2,
        )

        click.echo()
        click.echo(click.style("✅ Created project.promptrek.yaml", fg="green"))

        if config_gitignore:
            click.echo(click.style("✅ Configured .gitignore", fg="green"))

        if setup_hooks:
            click.echo(click.style("✅ Installed pre-commit hooks", fg="green"))

        click.echo()

        # Ask if user wants to generate editor configurations
        generate_now = questionary.confirm(
            "Generate editor configurations now?",
            default=True,
        ).ask()

        if generate_now:
            workflow_generate_config(ctx)

    except PrompTrekError as e:
        click.echo(click.style(f"\n❌ Error: {e}", fg="red"), err=True)
    except Exception as e:
        if ctx.obj.get("verbose"):
            raise
        click.echo(click.style(f"\n❌ Unexpected error: {e}", fg="red"), err=True)


def workflow_generate_config(ctx: click.Context) -> None:
    """Interactive workflow for generating editor configurations."""
    click.echo(click.style("\n⚙️  Generate Editor Configurations", fg="cyan", bold=True))
    click.echo()

    # Check for existing config
    existing_config = check_existing_config()
    if not existing_config:
        click.echo(
            click.style(
                "⚠️  No project.promptrek.yaml found. Please run initialization first.",
                fg="yellow",
            )
        )
        return

    click.echo(click.style(f"✓ Using configuration: {existing_config}", fg="green"))
    click.echo()

    # Get available editors from registry
    from ..adapters import registry
    from ..adapters.registry import AdapterCapability

    project_file_adapters = registry.get_project_file_adapters()

    # Create choices for editor selection
    editor_choices = [
        questionary.Choice(f"{name.capitalize()}", value=name)
        for name in sorted(project_file_adapters)
    ]

    # Select editors
    selected_editors = questionary.checkbox(
        "Select editors to generate for:",
        choices=editor_choices,
    ).ask()

    if not selected_editors:
        click.echo("No editors selected. Cancelled.")
        return

    click.echo()

    # Ask for variable overrides
    use_variables = questionary.confirm(
        "Do you want to override any variables?",
        default=False,
    ).ask()

    variables_dict: Dict[str, str] = {}
    if use_variables:
        click.echo("\nEnter variable overrides (KEY=VALUE). Leave blank to finish:")
        while True:
            var_input = questionary.text("Variable (or press Enter to finish):").ask()
            if not var_input:
                break
            if "=" not in var_input:
                click.echo(click.style("Invalid format. Use KEY=VALUE", fg="yellow"))
                continue
            key, value = var_input.split("=", 1)
            variables_dict[key.strip()] = value.strip()

    # Ask for headless mode
    headless = questionary.confirm(
        "Generate with headless agent instructions?",
        default=False,
    ).ask()

    # Preview mode
    dry_run = questionary.confirm(
        "Preview mode (show what will be generated)?",
        default=False,
    ).ask()

    click.echo()

    # Generate for each selected editor
    try:
        for editor in selected_editors:
            click.echo(
                click.style(f"Generating for {editor.capitalize()}...", fg="cyan")
            )
            generate_command(
                ctx,
                files=(existing_config,),
                directory=None,
                recursive=False,
                editor=editor,
                output=None,
                dry_run=dry_run,
                all_editors=False,
                variables=variables_dict,
                headless=headless,
            )

        click.echo()
        click.echo(
            click.style(
                "🎉 All done! Your PrompTrek project is ready.",
                fg="green",
                bold=True,
            )
        )

    except PrompTrekError as e:
        click.echo(click.style(f"\n❌ Error: {e}", fg="red"), err=True)
    except Exception as e:
        if ctx.obj.get("verbose"):
            raise
        click.echo(click.style(f"\n❌ Unexpected error: {e}", fg="red"), err=True)


def workflow_migrate(ctx: click.Context) -> None:
    """Interactive workflow for migrating schema versions."""
    from .commands.migrate import migrate_command

    click.echo(click.style("\n🔄 Migrate Schema Version", fg="cyan", bold=True))
    click.echo()

    # Find existing config
    existing_config = check_existing_config()
    if not existing_config:
        click.echo(
            click.style(
                "⚠️  No project.promptrek.yaml found.",
                fg="yellow",
            )
        )
        return

    click.echo(click.style(f"✓ Found configuration: {existing_config}", fg="green"))
    click.echo()

    # Confirm migration
    proceed = questionary.confirm(
        "Migrate to v2 format? (v2 uses pure markdown content)",
        default=True,
    ).ask()

    if not proceed:
        click.echo("Cancelled.")
        return

    # Backup option
    backup = questionary.confirm(
        "Create backup of original file?",
        default=True,
    ).ask()

    if backup is None:
        click.echo("Cancelled.")
        return

    # Output file path
    output_path = questionary.text(
        "Output file path:",
        default=f"{existing_config.stem}.v2{existing_config.suffix}",
    ).ask()

    if not output_path:
        click.echo("Cancelled.")
        return

    click.echo()

    try:
        migrate_command(
            ctx,
            input_file=existing_config,
            output=Path(output_path) if output_path else None,
            force=False,
        )

        click.echo()
        click.echo(click.style("✅ Migration completed successfully", fg="green"))

        if backup:
            import shutil

            backup_path = existing_config.with_suffix(
                existing_config.suffix + ".backup"
            )
            shutil.copy2(existing_config, backup_path)
            click.echo(click.style(f"✅ Backup saved to {backup_path}", fg="green"))

    except PrompTrekError as e:
        click.echo(click.style(f"\n❌ Error: {e}", fg="red"), err=True)
    except Exception as e:
        if ctx.obj.get("verbose"):
            raise
        click.echo(click.style(f"\n❌ Unexpected error: {e}", fg="red"), err=True)


def workflow_validate(ctx: click.Context) -> None:
    """Interactive workflow for validating configuration."""
    from .commands.validate import validate_command

    click.echo(click.style("\n🔍 Validate Configuration", fg="cyan", bold=True))
    click.echo()

    # Find existing config
    existing_config = check_existing_config()
    if not existing_config:
        click.echo(
            click.style(
                "⚠️  No project.promptrek.yaml found.",
                fg="yellow",
            )
        )
        return

    click.echo(click.style(f"✓ Validating: {existing_config}", fg="green"))
    click.echo()

    # Strict mode
    strict = questionary.confirm(
        "Use strict mode (treat warnings as errors)?",
        default=False,
    ).ask()

    if strict is None:
        click.echo("Cancelled.")
        return

    click.echo()

    try:
        validate_command(ctx, existing_config, strict)
        click.echo()
        click.echo(click.style("✅ Validation completed successfully", fg="green"))

    except PrompTrekError as e:
        click.echo(click.style(f"\n❌ Error: {e}", fg="red"), err=True)
    except Exception as e:
        if ctx.obj.get("verbose"):
            raise
        click.echo(click.style(f"\n❌ Unexpected error: {e}", fg="red"), err=True)


def workflow_sync(ctx: click.Context) -> None:
    """Interactive workflow for syncing from editor files."""
    from .commands.sync import sync_command

    click.echo(click.style("\n📤 Sync from Editor Files", fg="cyan", bold=True))
    click.echo()

    # Get available editors
    from ..adapters import registry

    project_file_adapters = registry.get_project_file_adapters()

    # Select editor
    editor = questionary.select(
        "Select editor to sync from:",
        choices=[
            questionary.Choice(f"{name.capitalize()}", value=name)
            for name in sorted(project_file_adapters)
        ],
    ).ask()

    if not editor:
        click.echo("Cancelled.")
        return

    # Source directory
    source_dir = questionary.text(
        "Source directory:",
        default=".",
    ).ask()

    if not source_dir:
        click.echo("Cancelled.")
        return

    # Output file
    output = questionary.text(
        "Output PrompTrek file:",
        default="project.promptrek.yaml",
    ).ask()

    if not output:
        click.echo("Cancelled.")
        return

    # Dry run
    dry_run = questionary.confirm(
        "Preview mode (show what will be updated)?",
        default=True,
    ).ask()

    click.echo()

    try:
        sync_command(
            ctx,
            source_dir=Path(source_dir),
            editor=editor,
            output=Path(output),
            dry_run=dry_run,
            force=False,
        )

        click.echo()
        click.echo(click.style("✅ Sync completed successfully", fg="green"))

    except PrompTrekError as e:
        click.echo(click.style(f"\n❌ Error: {e}", fg="red"), err=True)
    except Exception as e:
        if ctx.obj.get("verbose"):
            raise
        click.echo(click.style(f"\n❌ Unexpected error: {e}", fg="red"), err=True)


def workflow_plugins(ctx: click.Context) -> None:
    """Interactive workflow for configuring plugins."""
    from .commands.plugins import (
        generate_plugins_command,
        list_plugins_command,
    )

    click.echo(click.style("\n🔌 Configure Plugins", fg="cyan", bold=True))
    click.echo()

    # Plugin action
    action = questionary.select(
        "What would you like to do?",
        choices=[
            Choice("List configured plugins", value="list"),
            Choice("Generate plugin files", value="generate"),
            Choice("Go back", value="back"),
        ],
    ).ask()

    if action == "back" or action is None:
        return

    if action == "list":
        click.echo()
        try:
            list_plugins_command(ctx, prompt_file=None)
        except PrompTrekError as e:
            click.echo(click.style(f"\n❌ Error: {e}", fg="red"), err=True)
        return

    if action == "generate":
        # Find existing config
        existing_config = check_existing_config()
        if not existing_config:
            click.echo(
                click.style(
                    "⚠️  No project.promptrek.yaml found.",
                    fg="yellow",
                )
            )
            return

        click.echo()

        # Select editor
        from ..adapters import registry

        project_file_adapters = registry.get_project_file_adapters()

        editor = questionary.select(
            "Select editor for plugin generation:",
            choices=[
                Choice("All editors", value="all"),
                *[
                    Choice(f"{name.capitalize()}", value=name)
                    for name in sorted(project_file_adapters)
                ],
            ],
        ).ask()

        if not editor:
            click.echo("Cancelled.")
            return

        # Dry run
        dry_run = questionary.confirm(
            "Preview mode (show what will be generated)?",
            default=False,
        ).ask()

        click.echo()

        try:
            ctx.obj["force_system_wide"] = False
            ctx.obj["auto_confirm"] = False

            generate_plugins_command(
                ctx,
                prompt_file=existing_config,
                editor=editor,
                output_dir=None,
                dry_run=dry_run,
                force_system_wide=False,
                yes=False,
            )

            click.echo()
            click.echo(click.style("✅ Plugin generation completed", fg="green"))

        except PrompTrekError as e:
            click.echo(click.style(f"\n❌ Error: {e}", fg="red"), err=True)
        except Exception as e:
            if ctx.obj.get("verbose"):
                raise
            click.echo(click.style(f"\n❌ Unexpected error: {e}", fg="red"), err=True)


def show_help() -> None:
    """Show help and documentation."""
    click.echo(click.style("\n❓ Help & Documentation", fg="cyan", bold=True))
    click.echo()
    click.echo("For detailed documentation, visit:")
    click.echo("  https://github.com/flamingquaks/promptrek")
    click.echo()
    click.echo("Common commands:")
    click.echo("  promptrek init              - Initialize new project")
    click.echo("  promptrek generate          - Generate editor configs")
    click.echo("  promptrek validate          - Validate configuration")
    click.echo("  promptrek --help            - Show all commands")
    click.echo()


def run_interactive_mode(ctx: click.Context) -> None:
    """Run the interactive CLI wizard."""
    # Check if we're in a terminal
    if not sys.stdin.isatty() or not sys.stdout.isatty():
        # Non-interactive mode, show help
        click.echo(ctx.get_help())
        return

    print_banner()

    while True:
        click.echo()
        choice = questionary.select(
            "What would you like to do?",
            choices=[
                Choice("🚀 Initialize new project", value="init"),
                Choice("⚙️  Generate editor configurations", value="generate"),
                Choice(
                    "🔌 Configure plugins (MCP servers, commands, agents)",
                    value="plugins",
                ),
                Choice("🔄 Migrate schema version", value="migrate"),
                Choice("🔍 Validate configuration", value="validate"),
                Choice("📤 Sync from editor files", value="sync"),
                Choice("❓ Help & Documentation", value="help"),
                Choice("👋 Exit", value="exit"),
            ],
        ).ask()

        if choice is None or choice == "exit":
            click.echo()
            click.echo(click.style("👋 Goodbye!", fg="cyan"))
            break

        if choice == "init":
            workflow_init_project(ctx)
        elif choice == "generate":
            workflow_generate_config(ctx)
        elif choice == "plugins":
            workflow_plugins(ctx)
        elif choice == "migrate":
            workflow_migrate(ctx)
        elif choice == "validate":
            workflow_validate(ctx)
        elif choice == "sync":
            workflow_sync(ctx)
        elif choice == "help":
            show_help()
