"""
Plugin management commands for PrompTrek.

Provides commands for listing, generating, validating, and syncing plugin configurations.
"""

from pathlib import Path
from typing import Any, Dict, Optional, cast

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
    force_system_wide: bool = False,
    auto_confirm: bool = False,
) -> None:
    """
    Generate plugin files for specified editor(s).

    Args:
        ctx: Click context
        prompt_file: Path to the universal prompt file
        editor: Editor to generate for (or 'all')
        output_dir: Output directory for generated files
        dry_run: Whether to show what would be generated without creating files
        force_system_wide: Force system-wide config (skip project-level)
        auto_confirm: Auto-confirm all prompts (for system-wide changes)
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
    all_plugin_editors = [
        "claude",
        "cursor",
        "continue",
        "windsurf",
        "cline",
        "amazon-q",
        "kiro",
    ]

    if editor and editor.lower() == "all":
        editors = all_plugin_editors
    elif editor:
        editors = [editor.lower()]
    else:
        # Default to editors with full plugin support (Claude, Cursor)
        editors = ["claude", "cursor"]

    # Display MCP configuration strategy if verbose
    display_mcp_strategy_summary(editors, verbose)

    # Generate for each editor
    click.echo(f"\n🔌 Generating plugin files for {', '.join(editors)}...\n")

    for editor_name in editors:
        try:
            adapter = registry.get(editor_name)

            # Store config flags in context for adapters to access
            ctx.obj["force_system_wide"] = force_system_wide
            ctx.obj["auto_confirm"] = auto_confirm

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


# Helper functions for MCP configuration strategy


def get_mcp_config_strategy(adapter_name: str) -> Dict[str, Any]:
    """
    Get MCP configuration strategy for an adapter.

    Args:
        adapter_name: Name of the adapter (e.g., 'claude', 'cursor')

    Returns:
        Dictionary containing:
            - supports_project: bool - Whether project-level config is supported
            - project_path: str or None - Relative path for project config
            - system_path: str or None - System-wide config path
            - requires_confirmation: bool - Whether system-wide needs confirmation
    """
    strategies = {
        "claude": {
            "supports_project": True,
            "project_path": ".claude/mcp.json",
            "system_path": "~/Library/Application Support/Claude/claude_desktop_config.json",
            "requires_confirmation": False,  # Project preferred
        },
        "cursor": {
            "supports_project": True,
            "project_path": ".cursor/mcp-servers.json",
            "system_path": None,
            "requires_confirmation": False,
        },
        "continue": {
            "supports_project": True,
            "project_path": ".continue/config.json",
            "system_path": "~/.continue/config.json",
            "requires_confirmation": False,
        },
        "windsurf": {
            "supports_project": False,
            "project_path": None,
            "system_path": "~/.codeium/windsurf/mcp_config.json",
            "requires_confirmation": True,  # Always confirm system-wide
        },
        "cline": {
            "supports_project": True,
            "project_path": ".vscode/settings.json",
            "system_path": None,
            "requires_confirmation": False,
        },
        "amazon-q": {
            "supports_project": True,
            "project_path": ".amazonq/mcp.json",
            "system_path": "~/.aws/amazonq/mcp.json",
            "requires_confirmation": False,
        },
        "kiro": {
            "supports_project": True,
            "project_path": ".kiro/settings/mcp.json",
            "system_path": None,
            "requires_confirmation": False,
        },
    }
    return cast(Dict[str, Any], strategies.get(adapter_name, {}))


def display_mcp_strategy_summary(editors: list, verbose: bool = False) -> None:
    """
    Display MCP configuration strategy summary for editors.

    Args:
        editors: List of editor names
        verbose: Whether to show verbose output
    """
    if not verbose:
        return

    click.echo("\n📋 MCP Configuration Strategy:")
    for editor_name in editors:
        strategy = get_mcp_config_strategy(editor_name)
        if strategy.get("supports_project"):
            click.echo(
                f"  ✅ {editor_name}: Project-level ({strategy['project_path']})"
            )
        elif strategy.get("system_path"):
            click.echo(
                f"  ⚠️  {editor_name}: System-wide only ({strategy['system_path']})"
            )
        else:
            click.echo(f"  ℹ️  {editor_name}: No MCP support configured")
    click.echo("")
