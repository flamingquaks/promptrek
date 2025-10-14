"""
Plugin management commands for PrompTrek.

Provides commands for listing, generating, validating, and syncing plugin configurations.
"""

from pathlib import Path
from typing import Optional

import click

from ...adapters.registry import registry
from ...core.exceptions import CLIError, UPFParsingError
from ...core.models import UniversalPromptV2
from ...core.parser import UPFParser


def list_plugins_command(
    ctx: click.Context,
    prompt_file: Optional[Path],
) -> None:
    """
    List all configured plugins in a PrompTrek file.

    Args:
        ctx: Click context
        prompt_file: Path to the universal prompt file
    """
    verbose = ctx.obj.get("verbose", False)

    # Find prompt file if not specified
    if not prompt_file:
        potential_files = list(Path.cwd().glob("*.promptrek.yaml"))
        if not potential_files:
            raise CLIError(
                "No prompt file specified and no .promptrek.yaml files found "
                "in current directory."
            )
        prompt_file = potential_files[0]
        if verbose:
            click.echo(f"Auto-discovered prompt file: {prompt_file}")

    # Convert to absolute path and check existence
    if not prompt_file.is_absolute():
        prompt_file = Path.cwd() / prompt_file

    if not prompt_file.exists():
        raise CLIError(f"Prompt file not found: {prompt_file}")

    # Parse the prompt file
    try:
        parser = UPFParser()
        prompt = parser.parse_file(prompt_file)
        if verbose:
            click.echo(f"Parsed prompt file: {prompt_file}")
    except UPFParsingError as e:
        raise CLIError(f"Failed to parse prompt file: {e}")

    # Check if it's v2.1+ with plugins
    if not isinstance(prompt, UniversalPromptV2):
        click.echo("⚠️  This file uses schema v1.x which doesn't support plugins.")
        click.echo("   Run 'promptrek migrate' to upgrade to v2.1.0")
        return

    if not prompt.plugins:
        click.echo("No plugins configured in this file.")
        click.echo(f"Schema version: {prompt.schema_version}")
        return

    # Display plugin information
    click.echo(f"\n📦 Plugins configured in {prompt_file.name}:")
    click.echo(f"Schema version: {prompt.schema_version}\n")

    if prompt.plugins.mcp_servers:
        click.echo(f"🔌 MCP Servers ({len(prompt.plugins.mcp_servers)}):")
        for server in prompt.plugins.mcp_servers:
            click.echo(f"  • {server.name}: {server.command}")
            if server.description:
                click.echo(f"    {server.description}")

    if prompt.plugins.commands:
        click.echo(f"\n⚡ Commands ({len(prompt.plugins.commands)}):")
        for command in prompt.plugins.commands:
            click.echo(f"  • {command.name}: {command.description}")

    if prompt.plugins.agents:
        click.echo(f"\n🤖 Agents ({len(prompt.plugins.agents)}):")
        for agent in prompt.plugins.agents:
            click.echo(f"  • {agent.name}: {agent.description}")
            click.echo(f"    Trust Level: {agent.trust_level}")

    if prompt.plugins.hooks:
        click.echo(f"\n🪝 Hooks ({len(prompt.plugins.hooks)}):")
        for hook in prompt.plugins.hooks:
            click.echo(f"  • {hook.name} (on {hook.event})")


def generate_plugins_command(
    ctx: click.Context,
    prompt_file: Optional[Path],
    editor: Optional[str],
    output_dir: Optional[Path],
    dry_run: bool,
) -> None:
    """
    Generate plugin files for specified editor(s).

    Args:
        ctx: Click context
        prompt_file: Path to the universal prompt file
        editor: Editor to generate for (or 'all')
        output_dir: Output directory for generated files
        dry_run: Whether to show what would be generated without creating files
    """
    verbose = ctx.obj.get("verbose", False)

    # Find prompt file if not specified
    if not prompt_file:
        potential_files = list(Path.cwd().glob("*.promptrek.yaml"))
        if not potential_files:
            raise CLIError(
                "No prompt file specified and no .promptrek.yaml files found."
            )
        prompt_file = potential_files[0]
        if verbose:
            click.echo(f"Auto-discovered prompt file: {prompt_file}")

    # Resolve paths
    if not prompt_file.is_absolute():
        prompt_file = Path.cwd() / prompt_file

    if not prompt_file.exists():
        raise CLIError(f"Prompt file not found: {prompt_file}")

    if output_dir is None:
        output_dir = Path.cwd()
    elif not output_dir.is_absolute():
        output_dir = Path.cwd() / output_dir

    # Parse the prompt file
    try:
        parser = UPFParser()
        prompt = parser.parse_file(prompt_file)
    except UPFParsingError as e:
        raise CLIError(f"Failed to parse prompt file: {e}")

    # Check for v2.1+ with plugins
    if not isinstance(prompt, UniversalPromptV2) or not prompt.plugins:
        click.echo("⚠️  No plugins to generate (requires v2.1.0+ schema with plugins).")
        return

    # Determine which editors to generate for
    if editor and editor.lower() == "all":
        editors = ["claude", "cursor"]  # Only editors with plugin support
    elif editor:
        editors = [editor.lower()]
    else:
        editors = ["claude", "cursor"]  # Default to plugin-supporting editors

    # Generate for each editor
    click.echo(f"\n🔌 Generating plugin files for {', '.join(editors)}...\n")

    for editor_name in editors:
        try:
            adapter = registry.get(editor_name)
            files = adapter.generate(
                prompt, output_dir, dry_run=dry_run, verbose=verbose
            )

            if dry_run:
                click.echo(f"  {editor_name}: Would generate {len(files)} files")
            else:
                click.echo(f"  {editor_name}: Generated {len(files)} files")

        except Exception as e:
            click.echo(f"  ❌ {editor_name}: {e}", err=True)


def validate_plugins_command(
    ctx: click.Context,
    prompt_file: Optional[Path],
) -> None:
    """
    Validate plugin configurations in a PrompTrek file.

    Args:
        ctx: Click context
        prompt_file: Path to the universal prompt file
    """
    verbose = ctx.obj.get("verbose", False)

    # Find prompt file if not specified
    if not prompt_file:
        potential_files = list(Path.cwd().glob("*.promptrek.yaml"))
        if not potential_files:
            raise CLIError(
                "No prompt file specified and no .promptrek.yaml files found."
            )
        prompt_file = potential_files[0]

    # Resolve paths
    if not prompt_file.is_absolute():
        prompt_file = Path.cwd() / prompt_file

    if not prompt_file.exists():
        raise CLIError(f"Prompt file not found: {prompt_file}")

    # Parse the prompt file
    try:
        parser = UPFParser()
        prompt = parser.parse_file(prompt_file)
    except UPFParsingError as e:
        raise CLIError(f"Failed to parse prompt file: {e}")

    # Check schema version
    if not isinstance(prompt, UniversalPromptV2):
        click.echo("⚠️  This file uses schema v1.x which doesn't support plugins.")
        return

    if not prompt.plugins:
        click.echo("✅ No plugins to validate.")
        return

    # Validate plugin configurations
    click.echo(f"\n🔍 Validating plugin configurations in {prompt_file.name}...\n")

    errors = []
    warnings = []

    # Validate MCP servers
    if prompt.plugins.mcp_servers:
        for server in prompt.plugins.mcp_servers:
            if not server.command:
                errors.append(f"MCP server '{server.name}' missing command")
            if server.trust_metadata and not server.trust_metadata.trusted:
                warnings.append(f"MCP server '{server.name}' is not marked as trusted")

    # Validate commands
    if prompt.plugins.commands:
        for command in prompt.plugins.commands:
            if not command.prompt:
                errors.append(f"Command '{command.name}' missing prompt")
            if command.requires_approval and verbose:
                click.echo(f"  ℹ️  Command '{command.name}' requires approval")

    # Validate agents
    if prompt.plugins.agents:
        for agent in prompt.plugins.agents:
            if not agent.system_prompt:
                errors.append(f"Agent '{agent.name}' missing system_prompt")
            if agent.trust_level == "untrusted":
                warnings.append(f"Agent '{agent.name}' has untrusted access level")

    # Validate hooks
    if prompt.plugins.hooks:
        for hook in prompt.plugins.hooks:
            if not hook.command:
                errors.append(f"Hook '{hook.name}' missing command")

    # Display results
    if errors:
        click.echo("❌ Validation errors found:")
        for error in errors:
            click.echo(f"  • {error}")

    if warnings:
        click.echo("\n⚠️  Warnings:")
        for warning in warnings:
            click.echo(f"  • {warning}")

    if not errors and not warnings:
        click.echo("✅ All plugin configurations are valid!")
    elif not errors:
        click.echo("\n✅ No critical errors found.")
