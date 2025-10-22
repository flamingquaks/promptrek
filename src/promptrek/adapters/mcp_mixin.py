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

    def compare_mcp_servers(
        self, server1: Dict[str, Any], server2: Dict[str, Any]
    ) -> bool:
        """
        Compare two MCP server configurations to see if they're different.

        Args:
            server1: First server config
            server2: Second server config

        Returns:
            True if configurations are different, False if identical
        """
        # Compare all relevant fields
        fields_to_compare = ["command", "args", "env", "description"]

        for field in fields_to_compare:
            val1 = server1.get(field)
            val2 = server2.get(field)

            # Handle None vs missing key
            if val1 != val2:
                return True

        return False

    def detect_conflicting_servers(
        self,
        new_servers: Dict[str, Any],
        existing_config: Dict[str, Any],
    ) -> List[str]:
        """
        Detect MCP servers that exist with same name but different configuration.

        Args:
            new_servers: New MCP servers dict (name -> config)
            existing_config: Existing full config with mcpServers

        Returns:
            List of server names that have conflicts
        """
        conflicts = []
        existing_servers = existing_config.get("mcpServers", {})

        for server_name, new_config in new_servers.items():
            if server_name in existing_servers:
                existing_server_config = existing_servers[server_name]
                if self.compare_mcp_servers(new_config, existing_server_config):
                    conflicts.append(server_name)

        return conflicts

    def prompt_mcp_server_overwrite(
        self,
        server_name: str,
        existing_config: Dict[str, Any],
        new_config: Dict[str, Any],
        dry_run: bool = False,
    ) -> bool:
        """
        Ask user to confirm overwriting an existing MCP server with different config.

        Args:
            server_name: Name of the MCP server
            existing_config: Existing server configuration
            new_config: New server configuration
            dry_run: If True, don't actually prompt (just show message)

        Returns:
            True if user confirms overwrite (or dry_run), False otherwise
        """
        if dry_run:
            click.echo(
                f"\n⚠️  Would overwrite existing MCP server '{server_name}' with different configuration"
            )
            return True

        click.echo("\n⚠️  Conflicting MCP Server Configuration Detected")
        click.echo(f"   Server name: {server_name}")
        click.echo("")
        click.echo("   Existing configuration:")
        click.echo(f"   {json.dumps(existing_config, indent=2)}")
        click.echo("")
        click.echo("   New configuration:")
        click.echo(f"   {json.dumps(new_config, indent=2)}")
        click.echo("")

        return click.confirm(
            f"Overwrite existing '{server_name}' MCP server?", default=False
        )

    def warn_user_level_operations(
        self,
        editor_name: str,
        config_path: Path,
        server_count: int,
        dry_run: bool = False,
    ) -> bool:
        """
        Warn user about user-level MCP configuration operations.

        Args:
            editor_name: Name of the editor
            config_path: Path to user-level config file
            server_count: Number of MCP servers to add/update
            dry_run: If True, don't actually prompt (just show message)

        Returns:
            True if user confirms to proceed (or dry_run), False otherwise
        """
        if dry_run:
            click.echo(f"\n⚠️  Would update user-level {editor_name} MCP configuration")
            click.echo(f"   Location: {config_path}")
            click.echo(f"   Servers to add/update: {server_count}")
            return True

        click.echo(f"\n⚠️  {editor_name} User-Level MCP Configuration Warning")
        click.echo(
            f"   {editor_name} does not support project-level MCP server configuration"
        )
        click.echo("   This will update your user-level configuration at:")
        click.echo(f"   {config_path}")
        click.echo("")
        click.echo(f"   MCP servers to add/update: {server_count}")
        click.echo(
            "   Note: Existing MCP servers will NOT be removed, only added/updated"
        )
        click.echo("")

        return click.confirm(
            f"Proceed with user-level {editor_name} MCP configuration?", default=False
        )
