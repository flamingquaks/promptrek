"""
MCP (Model Context Protocol) generation mixin for editor adapters.

Provides shared functionality for generating MCP server configurations
with a project-first strategy and system-wide fallback with user confirmation.
"""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

import click

from ..core.models import MCPServer


class MCPGenerationMixin:
    """Mixin class for MCP server configuration generation."""

    def get_mcp_config_strategy(self) -> Dict[str, Any]:
        """
        Get MCP configuration strategy for this adapter.

        Returns:
            Dictionary containing:
                - supports_project: bool - Whether project-level config is supported
                - project_path: str or None - Relative path for project config
                - system_path: str or None - Absolute path for system config
                - requires_confirmation: bool - Whether system-wide needs confirmation
                - config_format: str - Format: 'json', 'yaml', etc.
        """
        # Default strategy (override in subclasses)
        return {
            "supports_project": False,
            "project_path": None,
            "system_path": None,
            "requires_confirmation": True,
            "config_format": "json",
        }

    def confirm_system_wide_mcp_update(
        self, editor_name: str, system_path: Path, dry_run: bool = False
    ) -> bool:
        """
        Ask user to confirm system-wide MCP configuration update.

        Args:
            editor_name: Name of the editor (e.g., "Windsurf")
            system_path: Path to system-wide config file
            dry_run: If True, don't actually confirm (just show message)

        Returns:
            True if user confirms (or dry_run), False otherwise
        """
        if dry_run:
            click.echo(f"\n⚠️  Would update system-wide {editor_name} MCP configuration")
            click.echo(f"   Location: {system_path}")
            return True

        click.echo(f"\n⚠️  {editor_name} MCP Configuration Warning")
        click.echo(
            f"   {editor_name} does not support project-level MCP server configuration"
        )
        click.echo("   This will update your system-wide configuration at:")
        click.echo(f"   {system_path}")
        click.echo("")

        return click.confirm(
            f"Update system-wide {editor_name} MCP configuration?", default=False
        )

    def build_mcp_servers_config(
        self,
        mcp_servers: List[MCPServer],
        variables: Optional[Dict[str, Any]] = None,
        format_style: str = "standard",
    ) -> Dict[str, Any]:
        """
        Build MCP servers configuration dictionary.

        Args:
            mcp_servers: List of MCP server configurations
            variables: Variables for substitution
            format_style: Config format style:
                - 'standard': Standard MCP format {"mcpServers": {...}}
                  (also accepts 'anthropic' and 'continue' for backward compatibility)

        Returns:
            Dictionary ready to be written as JSON/YAML
        """
        servers_dict = {}

        for server in mcp_servers:
            server_config: Dict[str, Any] = {"command": server.command}

            if server.args:
                server_config["args"] = server.args

            if server.env:
                # Apply variable substitution to env vars
                env_vars = {}
                for key, value in server.env.items():
                    substituted_value = value
                    if variables:
                        for var_name, var_value in variables.items():
                            placeholder = "{{{ " + var_name + " }}}"
                            substituted_value = substituted_value.replace(
                                placeholder, var_value
                            )
                    env_vars[key] = substituted_value
                server_config["env"] = env_vars

            if server.description:
                server_config["description"] = server.description

            servers_dict[server.name] = server_config

        # Format based on style
        # All formats use the standard MCP format
        if format_style in ["standard", "anthropic", "continue"]:
            return {"mcpServers": servers_dict}
        else:
            # Default to standard format
            return {"mcpServers": servers_dict}

    def merge_mcp_config(
        self,
        existing_config: Dict[str, Any],
        new_mcp_config: Dict[str, Any],
        format_style: str = "standard",
    ) -> Dict[str, Any]:
        """
        Merge new MCP servers with existing configuration.

        Args:
            existing_config: Existing config dictionary
            new_mcp_config: New MCP config to merge
            format_style: Config format style (standard/anthropic/continue)

        Returns:
            Merged configuration dictionary
        """
        merged = existing_config.copy()

        # All formats use standard MCP format with mcpServers object
        if "mcpServers" not in merged:
            merged["mcpServers"] = {}
        merged["mcpServers"].update(new_mcp_config.get("mcpServers", {}))

        return merged

    def write_mcp_config_file(
        self,
        config: Dict[str, Any],
        output_file: Path,
        dry_run: bool = False,
        verbose: bool = False,
    ) -> bool:
        """
        Write MCP configuration to file.

        Args:
            config: Configuration dictionary
            output_file: Path to output file
            dry_run: If True, don't actually write
            verbose: Enable verbose output

        Returns:
            True if successful (or dry_run), False otherwise
        """
        if dry_run:
            click.echo(f"  📁 Would create: {output_file}")
            if verbose:
                preview = json.dumps(config, indent=2)[:300]
                click.echo(f"    {preview}...")
            return True

        try:
            output_file.parent.mkdir(parents=True, exist_ok=True)
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(config, f, indent=2)
            click.echo(f"✅ Generated: {output_file}")
            return True
        except Exception as e:
            click.echo(f"❌ Error writing {output_file}: {e}", err=True)
            return False

    def read_existing_mcp_config(self, config_file: Path) -> Optional[Dict[str, Any]]:
        """
        Read existing MCP configuration file.

        Args:
            config_file: Path to config file

        Returns:
            Configuration dictionary or None if file doesn't exist/can't be read
        """
        if not config_file.exists():
            return None

        try:
            with open(config_file, "r", encoding="utf-8") as f:
                result: Dict[str, Any] = json.load(f)
                return result
        except Exception as e:
            click.echo(f"⚠️  Warning: Could not read {config_file}: {e}", err=True)
            return None

    def prompt_merge_strategy(self, config_file: Path, editor_name: str) -> str:
        """
        Prompt user for merge strategy when config exists.

        Args:
            config_file: Path to existing config
            editor_name: Name of the editor

        Returns:
            Strategy choice: 'merge', 'replace', 'skip', or 'system'
        """
        click.echo(f"\nℹ️  Existing {editor_name} config found at {config_file}")
        click.echo("\nChoose action:")
        click.echo("  1. Merge MCP servers with existing config (recommended)")
        click.echo("  2. Replace entire config (⚠️  will overwrite existing)")
        click.echo(f"  3. Skip {editor_name} MCP generation")
        click.echo("  4. Use system-wide config instead")

        choice = click.prompt("Choice", type=int, default=1)

        strategy_map = {1: "merge", 2: "replace", 3: "skip", 4: "system"}
        return strategy_map.get(choice, "merge")
