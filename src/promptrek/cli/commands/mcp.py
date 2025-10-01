"""
MCP command implementation.

Handles generation of editor-specific MCP server configurations.
"""

from pathlib import Path
from typing import List, Optional

import click

from ...core.exceptions import CLIError, MCPParsingError
from ...core.mcp_generator import MCPGenerator
from ...core.mcp_parser import MCPParser


def mcp_command(
    ctx: click.Context,
    mcp_file: Optional[Path],
    editor: Optional[str],
    output: Optional[Path],
    servers: Optional[List[str]],
    dry_run: bool,
    force: bool,
    variables: Optional[dict],
) -> None:
    """
    Generate editor-specific MCP server configurations.

    Args:
        ctx: Click context
        mcp_file: Path to mcp.promptrek.json file
        editor: Target editor(s), comma-separated
        output: Output directory
        servers: Selected server names
        dry_run: Dry run mode
        force: Force overwrite
        variables: Variable overrides
    """
    verbose = ctx.obj.get("verbose", False)

    # Set default output directory
    if not output:
        output = Path.cwd()

    # Find MCP file if not specified
    if not mcp_file:
        parser = MCPParser()
        mcp_file = parser.find_mcp_file(output)
        if not mcp_file:
            raise CLIError(
                "No mcp.promptrek.json file found. "
                "Create one in your project root or specify with --file"
            )

    if verbose:
        click.echo(f"Using MCP file: {mcp_file}")

    # Parse MCP configuration
    parser = MCPParser()
    try:
        config = parser.parse_file(mcp_file)
    except MCPParsingError as e:
        raise CLIError(f"Failed to parse MCP configuration: {e}")

    # Validate and substitute variables
    if variables:
        missing = parser.validate_variables(config, variables)
        if missing:
            raise CLIError(
                f"Missing required variables: {', '.join(missing)}. "
                "Provide with --var KEY=VALUE"
            )
        config = parser.substitute_variables(config, variables, use_env=True)
    else:
        # Use environment variables only
        missing = parser.validate_variables(config)
        if missing:
            raise CLIError(
                f"Missing required environment variables: {', '.join(missing)}"
            )
        config = parser.substitute_variables(config, use_env=True)

    if dry_run:
        click.echo("🔍 Dry run mode - showing what would be generated:")

    # Interactive editor selection if not specified
    if not editor:
        editor = _prompt_editor_selection()

    # Parse editor list
    editors = [e.strip() for e in editor.split(",")]

    # Interactive server selection if not specified
    selected_servers = servers
    if not selected_servers:
        selected_servers = _prompt_server_selection(config, verbose)

    # Validate selection
    generator = MCPGenerator()
    warnings = generator.validate_selection(config, selected_servers)
    if warnings:
        for warning in warnings:
            click.echo(f"⚠️  {warning}")
        if config.config.require_all_servers and not force:
            raise CLIError(
                "Configuration requires all servers. Use --force to override."
            )

    # Confirm if not dry run and would overwrite
    if not dry_run and not force and not config.config.allow_custom_servers:
        click.echo(
            "⚠️  Configuration set to overwrite custom servers"
            "(allow_custom_servers=false)"
        )
        if not click.confirm("Continue?"):
            click.echo("Aborted.")
            return

    # Generate for each editor
    for target_editor in editors:
        try:
            _generate_for_editor(
                target_editor, config, output, selected_servers, dry_run, verbose
            )
        except Exception as e:
            if verbose:
                raise
            click.echo(f"❌ Failed to generate for {target_editor}: {e}", err=True)


def _prompt_editor_selection() -> str:
    """
    Prompt user to select target editor(s).

    Returns:
        Comma-separated list of editor names
    """
    click.echo("Select target editor(s):")
    click.echo("  1. Cursor")
    click.echo("  2. Continue")
    click.echo("  3. Both")

    choice = click.prompt("Enter choice", type=int, default=3)

    if choice == 1:
        return "cursor"
    elif choice == 2:
        return "continue"
    elif choice == 3:
        return "cursor,continue"
    else:
        raise CLIError("Invalid choice")


def _prompt_server_selection(
    config,
    verbose: bool,
) -> List[str]:
    """
    Prompt user to select MCP servers.

    Args:
        config: MCP configuration
        verbose: Verbose output

    Returns:
        List of selected server names
    """
    if not config.mcpServers:
        click.echo("No MCP servers defined in configuration")
        return []

    # If require_all_servers is set, select all automatically
    if config.config.require_all_servers:
        click.echo("Configuration requires all servers - selecting all")
        return list(config.mcpServers.keys())

    click.echo("\nAvailable MCP servers:")
    for i, (name, server) in enumerate(config.mcpServers.items(), 1):
        required_marker = " [REQUIRED]" if server.required else ""
        desc = server.description or "No description"
        click.echo(f"  {i}. {name}{required_marker}")
        if verbose:
            click.echo(f"     {desc}")
            click.echo(f"     Command: {server.command} {' '.join(server.args or [])}")

    click.echo("\nSelect servers to install:")
    click.echo("  Enter numbers separated by commas (e.g., 1,2,4)")
    click.echo("  Or 'all' to select all servers")

    selection = click.prompt("Selection", default="all")

    if selection.lower() == "all":
        return list(config.mcpServers.keys())

    # Parse selection
    try:
        indices = [int(i.strip()) for i in selection.split(",")]
        server_list = list(config.mcpServers.keys())
        selected = [server_list[i - 1] for i in indices if 1 <= i <= len(server_list)]
        return selected
    except (ValueError, IndexError):
        raise CLIError("Invalid selection")


def _generate_for_editor(
    editor: str,
    config,
    output_dir: Path,
    selected_servers: List[str],
    dry_run: bool,
    verbose: bool,
) -> None:
    """
    Generate MCP configuration for a specific editor.

    Args:
        editor: Editor name
        config: MCP configuration
        output_dir: Output directory
        selected_servers: Selected server names
        dry_run: Dry run mode
        verbose: Verbose output
    """
    generator = MCPGenerator()

    if editor == "cursor":
        generator.generate_cursor_mcp(
            config, output_dir, selected_servers, dry_run, verbose
        )
    elif editor == "continue":
        generator.generate_continue_mcp(
            config, output_dir, selected_servers, dry_run, verbose
        )
    else:
        click.echo(f"⚠️  Editor '{editor}' not yet supported for MCP generation")
