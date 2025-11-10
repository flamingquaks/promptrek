"""
Interactive CLI wizard for PrompTrek.

Provides an interactive menu-driven interface for common PrompTrek workflows.
"""

import sys
from pathlib import Path
from typing import Dict, Optional

import click
import questionary
from questionary import Choice

from .. import __version__
from ..core.exceptions import PrompTrekError
from .commands.config_ignores import config_ignores_command
from .commands.generate import generate_command
from .commands.hooks import install_hooks_command
from .commands.init import init_command
from .commands.preview import preview_command
from .commands.refresh import refresh_command
from .commands.specs import list_specs_command, spec_export_command

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


def wait_for_return() -> None:
    """Wait for user to press a key to return to menu."""
    click.echo()
    click.echo(click.style("Press Enter to return to menu...", fg="cyan", dim=True))
    input()


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
        init_command(
            ctx,
            template=None,
            output="project.promptrek.yaml",
            setup_hooks=setup_hooks,
            schema_version=schema_version,
            config_gitignore=config_gitignore,
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
        questionary.Choice(name.capitalize(), value=name)
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

    if use_variables is None:
        click.echo("Cancelled.")
        return

    variables_dict: Dict[str, str] = {}
    if use_variables:
        click.echo("\nEnter variable overrides (KEY=VALUE). Leave blank to finish:")
        while True:
            var_input = questionary.text("Variable (or press Enter to finish):").ask()
            if var_input is None:
                click.echo("Cancelled.")
                return
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

    if headless is None:
        click.echo("Cancelled.")
        return

    # Preview mode
    dry_run = questionary.confirm(
        "Preview mode (show what will be generated)?",
        default=False,
    ).ask()

    if dry_run is None:
        click.echo("Cancelled.")
        return

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
            output_file=Path(output_path) if output_path else None,
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
            questionary.Choice(name.capitalize(), value=name)
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
    output_path = questionary.text(
        "Output PrompTrek file:",
        default="project.promptrek.yaml",
    ).ask()

    if not output_path:
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
            output_file=Path(output_path) if output_path else None,
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
                    Choice(name.capitalize(), value=name)
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
            generate_plugins_command(
                ctx,
                prompt_file=existing_config,
                editor=editor,
                output_dir=None,
                dry_run=dry_run,
                force_system_wide=False,
                auto_confirm=False,
            )

            click.echo()
            click.echo(click.style("✅ Plugin generation completed", fg="green"))

        except PrompTrekError as e:
            click.echo(click.style(f"\n❌ Error: {e}", fg="red"), err=True)
        except Exception as e:
            if ctx.obj.get("verbose"):
                raise
            click.echo(click.style(f"\n❌ Unexpected error: {e}", fg="red"), err=True)


def workflow_list_specs(ctx: click.Context) -> None:
    """Interactive workflow for listing spec documents."""
    click.echo(click.style("\n📋 List Spec Documents", fg="cyan", bold=True))
    click.echo()

    try:
        list_specs_command(ctx)
        wait_for_return()
    except PrompTrekError as e:
        click.echo(click.style(f"\n❌ Error: {e}", fg="red"), err=True)
        wait_for_return()
    except Exception as e:
        if ctx.obj.get("verbose"):
            raise
        click.echo(click.style(f"\n❌ Unexpected error: {e}", fg="red"), err=True)
        wait_for_return()


def workflow_spec_export(ctx: click.Context) -> None:
    """Interactive workflow for exporting a spec document."""
    from ..core.models import SpecMetadata
    from ..utils.spec_manager import SpecManager

    click.echo(click.style("\n📤 Export Spec Document", fg="cyan", bold=True))
    click.echo()

    try:
        # First, list available specs
        spec_manager = SpecManager(Path.cwd())
        specs = spec_manager.list_specs()

        if not specs:
            click.echo(click.style("⚠️  No specs found.", fg="yellow"))
            click.echo(
                "\nUse /promptrek.spec.specify in your editor to create a new spec."
            )
            return

        click.echo(f"Found {len(specs)} spec(s):\n")
        for spec in specs:
            click.echo(f"  [{spec.id}] {spec.title}")

        click.echo()

        # Prompt for spec ID
        spec_id = questionary.text(
            "Enter spec ID to export:",
        ).ask()

        if not spec_id:
            click.echo("Cancelled.")
            return

        # Get spec to build default filename
        selected_spec: Optional[SpecMetadata] = spec_manager.get_spec_by_id(spec_id)
        if not selected_spec:
            click.echo(click.style(f"❌ Spec with ID '{spec_id}' not found", fg="red"))
            return

        # At this point, selected_spec is guaranteed to be non-None
        # Prompt for output path
        default_output = selected_spec.path.replace(".md", "-export.md")
        output_path = questionary.text(
            "Output file path:",
            default=default_output,
        ).ask()

        if not output_path:
            click.echo("Cancelled.")
            return

        # Prompt for clean mode
        clean = questionary.confirm(
            "Remove metadata header from export?",
            default=True,
        ).ask()

        if clean is None:
            click.echo("Cancelled.")
            return

        click.echo()

        # Export the spec
        spec_export_command(ctx, spec_id, Path(output_path), clean)

        click.echo()
        click.echo(click.style("✅ Spec exported successfully", fg="green"))

    except PrompTrekError as e:
        click.echo(click.style(f"\n❌ Error: {e}", fg="red"), err=True)
    except Exception as e:
        if ctx.obj.get("verbose"):
            raise
        click.echo(click.style(f"\n❌ Unexpected error: {e}", fg="red"), err=True)


def workflow_list_editors(ctx: click.Context) -> None:
    """Interactive workflow for listing supported editors."""
    from ..adapters.registry import AdapterCapability
    from .commands.generate import registry

    click.echo(click.style("\n📚 Supported Editors", fg="cyan", bold=True))
    click.echo()

    # Get editors by capability
    project_file_adapters = registry.get_project_file_adapters()
    global_config_adapters = registry.get_global_config_adapters()
    ide_plugin_adapters = registry.get_adapters_by_capability(
        AdapterCapability.IDE_PLUGIN_ONLY
    )

    if project_file_adapters:
        click.echo(click.style("✅ Project Configuration File Support:", fg="green"))
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
                click.echo(f"   • {adapter_name:12} - {description}")
                click.echo(f"     → {files_str}")
            except Exception:
                click.echo(f"   • {adapter_name:12} - Available")
        click.echo()

    if global_config_adapters:
        click.echo(click.style("ℹ️  Global Configuration Only:", fg="blue"))
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
        click.echo(click.style("🔧 IDE Configuration Only:", fg="yellow"))
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

    click.echo(click.style("Usage Examples:", fg="cyan"))
    if project_file_adapters:
        example_editor = sorted(project_file_adapters)[0]
        click.echo(
            f"  Generate for specific editor:  "
            f"promptrek generate config.yaml --editor {example_editor}"
        )
        click.echo(
            "  Generate for all supported:    " "promptrek generate config.yaml --all"
        )

    wait_for_return()


def workflow_preview(ctx: click.Context) -> None:
    """Interactive workflow for previewing generated output."""
    click.echo(click.style("\n👁️  Preview Generated Output", fg="cyan", bold=True))
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

    project_file_adapters = registry.get_project_file_adapters()

    # Select editor
    editor = questionary.select(
        "Select editor to preview:",
        choices=[
            questionary.Choice(name.capitalize(), value=name)
            for name in sorted(project_file_adapters)
        ],
    ).ask()

    if not editor:
        click.echo("Cancelled.")
        return

    # Ask for variable overrides
    use_variables = questionary.confirm(
        "Do you want to override any variables?",
        default=False,
    ).ask()

    if use_variables is None:
        click.echo("Cancelled.")
        return

    variables_dict: Dict[str, str] = {}
    if use_variables:
        click.echo("\nEnter variable overrides (KEY=VALUE). Leave blank to finish:")
        while True:
            var_input = questionary.text("Variable (or press Enter to finish):").ask()
            if var_input is None:
                click.echo("Cancelled.")
                return
            if not var_input:
                break
            if "=" not in var_input:
                click.echo(click.style("Invalid format. Use KEY=VALUE", fg="yellow"))
                continue
            key, value = var_input.split("=", 1)
            variables_dict[key.strip()] = value.strip()

    click.echo()

    try:
        preview_command(ctx, existing_config, editor, variables_dict or None)

        click.echo()
        click.echo(click.style("✅ Preview completed", fg="green"))

    except PrompTrekError as e:
        click.echo(click.style(f"\n❌ Error: {e}", fg="red"), err=True)
    except Exception as e:
        if ctx.obj.get("verbose"):
            raise
        click.echo(click.style(f"\n❌ Unexpected error: {e}", fg="red"), err=True)


def workflow_refresh(ctx: click.Context) -> None:
    """Interactive workflow for refreshing generated files."""
    click.echo(click.style("\n🔄 Refresh Generated Files", fg="cyan", bold=True))
    click.echo()

    # Get available editors from registry
    from ..adapters import registry

    project_file_adapters = registry.get_project_file_adapters()

    # Editor selection
    editor_choice = questionary.select(
        "Select editor to refresh:",
        choices=[
            Choice("Use last generation settings", value=None),
            *[
                questionary.Choice(name.capitalize(), value=name)
                for name in sorted(project_file_adapters)
            ],
        ],
    ).ask()

    if editor_choice is False:
        click.echo("Cancelled.")
        return

    # All editors option
    all_editors = False
    if editor_choice is not None:
        all_editors = questionary.confirm(
            "Refresh all editors?",
            default=False,
        ).ask()

        if all_editors is None:
            click.echo("Cancelled.")
            return

    # Clear cache option
    clear_cache = questionary.confirm(
        "Clear cached dynamic variables?",
        default=False,
    ).ask()

    if clear_cache is None:
        click.echo("Cancelled.")
        return

    # Ask for variable overrides
    use_variables = questionary.confirm(
        "Do you want to override any variables?",
        default=False,
    ).ask()

    if use_variables is None:
        click.echo("Cancelled.")
        return

    variables_dict: Dict[str, str] = {}
    if use_variables:
        click.echo("\nEnter variable overrides (KEY=VALUE). Leave blank to finish:")
        while True:
            var_input = questionary.text("Variable (or press Enter to finish):").ask()
            if var_input is None:
                click.echo("Cancelled.")
                return
            if not var_input:
                break
            if "=" not in var_input:
                click.echo(click.style("Invalid format. Use KEY=VALUE", fg="yellow"))
                continue
            key, value = var_input.split("=", 1)
            variables_dict[key.strip()] = value.strip()

    # Dry run option
    dry_run = questionary.confirm(
        "Preview mode (show what will be refreshed)?",
        default=False,
    ).ask()

    if dry_run is None:
        click.echo("Cancelled.")
        return

    click.echo()

    try:
        refresh_command(
            ctx,
            editor=editor_choice,
            all_editors=all_editors,
            dry_run=dry_run,
            clear_cache=clear_cache,
            variables=variables_dict or None,
        )

        click.echo()
        click.echo(click.style("✅ Refresh completed successfully", fg="green"))

    except PrompTrekError as e:
        click.echo(click.style(f"\n❌ Error: {e}", fg="red"), err=True)
    except Exception as e:
        if ctx.obj.get("verbose"):
            raise
        click.echo(click.style(f"\n❌ Unexpected error: {e}", fg="red"), err=True)


def workflow_config_ignores(ctx: click.Context) -> None:
    """Interactive workflow for configuring .gitignore."""
    click.echo(click.style("\n🚫 Configure .gitignore", fg="cyan", bold=True))
    click.echo()

    # Check for existing config
    existing_config = check_existing_config()
    if existing_config:
        click.echo(click.style(f"✓ Found configuration: {existing_config}", fg="green"))
    else:
        click.echo(
            click.style(
                "⚠️  No project.promptrek.yaml found. Continuing anyway...",
                fg="yellow",
            )
        )

    click.echo()

    # Remove cached option
    remove_cached = questionary.confirm(
        "Run 'git rm --cached' on existing committed files?",
        default=False,
    ).ask()

    if remove_cached is None:
        click.echo("Cancelled.")
        return

    # Dry run option
    dry_run = questionary.confirm(
        "Preview mode (show what will be done)?",
        default=True,
    ).ask()

    if dry_run is None:
        click.echo("Cancelled.")
        return

    click.echo()

    try:
        config_ignores_command(ctx, existing_config, remove_cached, dry_run)

        click.echo()
        click.echo(click.style("✅ .gitignore configuration completed", fg="green"))

    except PrompTrekError as e:
        click.echo(click.style(f"\n❌ Error: {e}", fg="red"), err=True)
    except Exception as e:
        if ctx.obj.get("verbose"):
            raise
        click.echo(click.style(f"\n❌ Unexpected error: {e}", fg="red"), err=True)


def workflow_install_hooks(ctx: click.Context) -> None:
    """Interactive workflow for installing pre-commit hooks."""
    click.echo(click.style("\n🪝 Install Pre-commit Hooks", fg="cyan", bold=True))
    click.echo()

    # Config path
    config_path = questionary.text(
        "Path to .pre-commit-config.yaml:",
        default=".pre-commit-config.yaml",
    ).ask()

    if not config_path:
        click.echo("Cancelled.")
        return

    # Force option
    force = questionary.confirm(
        "Overwrite existing hooks without confirmation?",
        default=False,
    ).ask()

    if force is None:
        click.echo("Cancelled.")
        return

    # Activate option
    activate = questionary.confirm(
        "Automatically run 'pre-commit install' to activate hooks?",
        default=True,
    ).ask()

    if activate is None:
        click.echo("Cancelled.")
        return

    click.echo()

    try:
        install_hooks_command(ctx, Path(config_path), force, activate)

        click.echo()
        click.echo(
            click.style("✅ Pre-commit hooks installed successfully", fg="green")
        )

    except PrompTrekError as e:
        click.echo(click.style(f"\n❌ Error: {e}", fg="red"), err=True)
    except Exception as e:
        if ctx.obj.get("verbose"):
            raise
        click.echo(click.style(f"\n❌ Unexpected error: {e}", fg="red"), err=True)


def workflow_plugins_validate(ctx: click.Context) -> None:
    """Interactive workflow for validating plugin configurations."""
    from .commands.plugins import validate_plugins_command

    click.echo(click.style("\n✅ Validate Plugin Configurations", fg="cyan", bold=True))
    click.echo()

    # Check for existing config
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

    try:
        validate_plugins_command(ctx, existing_config)

        click.echo()
        click.echo(
            click.style("✅ Plugin validation completed successfully", fg="green")
        )

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

    wait_for_return()


def run_interactive_mode(ctx: click.Context) -> None:
    """Run the interactive CLI wizard."""
    # Check if we're in a terminal
    if not (sys.stdin and sys.stdin.isatty()) or not (
        sys.stdout and sys.stdout.isatty()
    ):
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
                Choice("🔄 Refresh with fresh variables", value="refresh"),
                Choice("👁️  Preview without creating files", value="preview"),
                Choice("📤 Sync from editor files", value="sync"),
                Choice("🔄 Migrate schema version", value="migrate"),
                Choice("🔍 Validate configuration", value="validate"),
                Choice("🔌 Configure plugins", value="plugins"),
                Choice("✅ Validate plugin configurations", value="plugins_validate"),
                Choice("📋 List spec documents", value="list_specs"),
                Choice("📤 Export spec to markdown", value="spec_export"),
                Choice("📚 List supported editors", value="list_editors"),
                Choice("🚫 Configure .gitignore", value="config_ignores"),
                Choice("🪝 Install pre-commit hooks", value="install_hooks"),
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
        elif choice == "refresh":
            workflow_refresh(ctx)
        elif choice == "preview":
            workflow_preview(ctx)
        elif choice == "sync":
            workflow_sync(ctx)
        elif choice == "plugins":
            workflow_plugins(ctx)
        elif choice == "plugins_validate":
            workflow_plugins_validate(ctx)
        elif choice == "list_specs":
            workflow_list_specs(ctx)
        elif choice == "spec_export":
            workflow_spec_export(ctx)
        elif choice == "list_editors":
            workflow_list_editors(ctx)
        elif choice == "config_ignores":
            workflow_config_ignores(ctx)
        elif choice == "install_hooks":
            workflow_install_hooks(ctx)
        elif choice == "migrate":
            workflow_migrate(ctx)
        elif choice == "validate":
            workflow_validate(ctx)
        elif choice == "help":
            show_help()
