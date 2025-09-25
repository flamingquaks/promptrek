"""
Generate command implementation.

Handles generation of editor-specific prompts from universal prompt files.
"""

from pathlib import Path
from typing import Optional

import click

from ...adapters import registry
from ...adapters.registry import AdapterCapability
from ...core.exceptions import AdapterNotFoundError, CLIError, UPFParsingError
from ...core.parser import UPFParser
from ...core.validator import UPFValidator


def generate_command(
    ctx: click.Context,
    file: Path,
    editor: Optional[str],
    output: Optional[Path],
    dry_run: bool,
    all_editors: bool,
    variables: Optional[dict] = None,
) -> None:
    """
    Generate editor-specific prompts from universal prompt file.

    Args:
        ctx: Click context
        file: Path to the UPF file
        editor: Target editor name
        output: Output directory path
        dry_run: Whether to show what would be generated without creating files
        all_editors: Whether to generate for all target editors
    """
    verbose = ctx.obj.get("verbose", False)

    # Parse the file
    parser = UPFParser()
    try:
        prompt = parser.parse_file(file)
        if verbose:
            click.echo(f"✅ Parsed {file}")
    except UPFParsingError as e:
        raise CLIError(f"Failed to parse {file}: {e}")

    # Validate first
    validator = UPFValidator()
    result = validator.validate(prompt)
    if result.errors:
        raise CLIError(f"Validation failed: {'; '.join(result.errors)}")

    # Determine target editors
    if all_editors:
        # Get all adapters but separate by capability
        project_file_adapters = registry.get_project_file_adapters()
        global_config_adapters = registry.get_global_config_adapters()
        ide_plugin_adapters = registry.get_adapters_by_capability(
            AdapterCapability.IDE_PLUGIN_ONLY
        )

        target_editors = project_file_adapters

        # Show information about non-project-file tools
        if global_config_adapters or ide_plugin_adapters:
            click.echo("ℹ️  Note: Some tools use global configuration only:")
            for adapter_name in global_config_adapters:
                click.echo(f"  - {adapter_name}: Configure through global settings")
            for adapter_name in ide_plugin_adapters:
                click.echo(f"  - {adapter_name}: Configure through IDE interface")
            click.echo()
    elif editor:
        # Check if the adapter exists and what capabilities it has
        available_adapters = registry.list_adapters()
        if editor not in available_adapters:
            raise CLIError(
                f"Editor '{editor}' not available. Available editors: {', '.join(available_adapters)}"
            )

        # Check if this adapter supports project files
        if not registry.has_capability(
            editor, AdapterCapability.GENERATES_PROJECT_FILES
        ):
            # Provide helpful information instead of generating files
            adapter_info = registry.get_adapter_info(editor)
            capabilities = adapter_info.get("capabilities", [])

            if AdapterCapability.GLOBAL_CONFIG_ONLY.value in capabilities:
                click.echo(f"ℹ️  {editor} uses global configuration only.")
                click.echo(
                    f"   Configure {editor} through its global settings or admin panel."
                )
            elif AdapterCapability.IDE_PLUGIN_ONLY.value in capabilities:
                click.echo(f"ℹ️  {editor} is configured through IDE interface only.")
                click.echo(
                    f"   Configure {editor} through your IDE's settings or preferences."
                )
            else:
                click.echo(
                    f"ℹ️  {editor} does not support project-level configuration files."
                )

            return  # Exit early without generating files

        target_editors = [editor]
    else:
        raise CLIError("Must specify either --editor or --all")

    # Set default output directory
    if not output:
        output = Path.cwd()

    # Ensure output directory exists
    output.mkdir(parents=True, exist_ok=True)

    if dry_run:
        click.echo("🔍 Dry run mode - showing what would be generated:")

    if target_editors:
        click.echo("Generating project configuration files for:")

    # Generate for each target editor that supports project files
    for target_editor in target_editors:
        try:
            _generate_for_editor(
                prompt, target_editor, output, dry_run, verbose, variables
            )
        except AdapterNotFoundError:
            click.echo(f"⚠️ Editor '{target_editor}' not yet implemented - skipping")
        except Exception as e:
            if verbose:
                raise
            raise CLIError(f"Failed to generate for {target_editor}: {e}")


def _generate_for_editor(
    prompt,
    editor: str,
    output_dir: Path,
    dry_run: bool,
    verbose: bool,
    variables: Optional[dict] = None,
) -> None:
    """Generate prompts for a specific editor using the adapter system."""

    try:
        adapter = registry.get(editor)
        adapter.generate(prompt, output_dir, dry_run, verbose, variables)
    except AdapterNotFoundError:
        raise AdapterNotFoundError(f"Editor '{editor}' adapter not implemented yet")
