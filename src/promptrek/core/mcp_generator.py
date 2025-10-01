"""
MCP configuration generator.

Handles generation of editor-specific MCP configuration files.
"""

import json
from pathlib import Path
from typing import Dict, List, Optional

import click
import yaml

from .models import MCPConfiguration, MCPServerConfig


class MCPGenerator:
    """Generator for editor-specific MCP configuration files."""

    def __init__(self):
        """Initialize MCP generator."""
        pass

    def generate_cursor_mcp(
        self,
        config: MCPConfiguration,
        output_dir: Path,
        selected_servers: Optional[List[str]] = None,
        dry_run: bool = False,
        verbose: bool = False,
    ) -> Path:
        """
        Generate Cursor MCP configuration (.cursor/mcp.json).

        Args:
            config: MCP configuration
            output_dir: Output directory
            selected_servers: List of server names to include (None = all)
            dry_run: Whether to perform dry run
            verbose: Verbose output

        Returns:
            Path to generated file
        """
        cursor_dir = output_dir / ".cursor"
        mcp_file = cursor_dir / "mcp.json"

        # Filter servers if selection provided
        servers = self._filter_servers(config.mcpServers, selected_servers)

        # Check for existing configuration
        existing_servers = {}
        if mcp_file.exists():
            try:
                with open(mcp_file, "r", encoding="utf-8") as f:
                    existing_data = json.load(f)
                    existing_servers = existing_data.get("mcpServers", {})
            except Exception:
                pass

        # Merge or replace based on configuration
        if config.config.allow_custom_servers and existing_servers:
            merged_servers = self._merge_servers(existing_servers, servers, verbose)
        else:
            if existing_servers and not dry_run:
                removed = set(existing_servers.keys()) - set(servers.keys())
                if removed:
                    click.echo(f"⚠️  Removing custom servers: {', '.join(removed)}")
            merged_servers = servers

        # Build output
        output = {"mcpServers": self._servers_to_dict(merged_servers)}

        if dry_run:
            click.echo(f"📁 Would create/update: {mcp_file}")
            if verbose:
                click.echo("Content:")
                click.echo(json.dumps(output, indent=2))
        else:
            cursor_dir.mkdir(parents=True, exist_ok=True)
            with open(mcp_file, "w", encoding="utf-8") as f:
                json.dump(output, f, indent=2)
            click.echo(f"✅ Generated: {mcp_file}")

        return mcp_file

    def generate_continue_mcp(
        self,
        config: MCPConfiguration,
        output_dir: Path,
        selected_servers: Optional[List[str]] = None,
        dry_run: bool = False,
        verbose: bool = False,
    ) -> Path:
        """
        Generate Continue MCP configuration in config.yaml.

        Args:
            config: MCP configuration
            output_dir: Output directory
            selected_servers: List of server names to include (None = all)
            dry_run: Whether to perform dry run
            verbose: Verbose output

        Returns:
            Path to generated/updated file
        """
        config_file = output_dir / "config.yaml"

        # Filter servers
        servers = self._filter_servers(config.mcpServers, selected_servers)

        # Convert to Continue format (list of server configs)
        continue_servers = []
        for name, server in servers.items():
            server_config = {
                "name": name,
                "command": server.command,
            }
            if server.args:
                server_config["args"] = server.args
            if server.env:
                server_config["env"] = server.env
            continue_servers.append(server_config)

        # Check for existing config
        existing_config = {}
        if config_file.exists():
            try:
                with open(config_file, "r", encoding="utf-8") as f:
                    existing_config = yaml.safe_load(f) or {}
            except Exception:
                pass

        # Merge MCP servers section
        if config.config.allow_custom_servers and "mcpServers" in existing_config:
            existing_names = {s["name"] for s in existing_config.get("mcpServers", [])}
            new_names = {s["name"] for s in continue_servers}

            # Keep existing servers not in new config
            merged = [
                s for s in existing_config["mcpServers"] if s["name"] not in new_names
            ]
            # Add new/updated servers
            merged.extend(continue_servers)

            if verbose:
                added = new_names - existing_names
                updated = new_names & existing_names
                if added:
                    click.echo(f"  Adding servers: {', '.join(added)}")
                if updated:
                    click.echo(f"  Updating servers: {', '.join(updated)}")

            existing_config["mcpServers"] = merged
        else:
            if (
                "mcpServers" in existing_config
                and not config.config.allow_custom_servers
            ):
                removed = {s["name"] for s in existing_config["mcpServers"]} - {
                    s["name"] for s in continue_servers
                }
                if removed:
                    click.echo(f"⚠️  Removing custom servers: {', '.join(removed)}")
            existing_config["mcpServers"] = continue_servers

        if dry_run:
            click.echo(f"📁 Would create/update: {config_file}")
            if verbose:
                click.echo("MCP Servers section:")
                click.echo(yaml.dump({"mcpServers": existing_config["mcpServers"]}))
        else:
            with open(config_file, "w", encoding="utf-8") as f:
                yaml.dump(existing_config, f, default_flow_style=False, sort_keys=False)
            click.echo(f"✅ Generated/Updated: {config_file}")

        return config_file

    def _filter_servers(
        self,
        servers: Dict[str, MCPServerConfig],
        selected: Optional[List[str]],
    ) -> Dict[str, MCPServerConfig]:
        """
        Filter servers based on selection.

        Args:
            servers: All servers
            selected: Selected server names (None = all)

        Returns:
            Filtered server dict
        """
        if selected is None:
            return servers

        return {name: config for name, config in servers.items() if name in selected}

    def _merge_servers(
        self,
        existing: Dict[str, dict],
        new_servers: Dict[str, MCPServerConfig],
        verbose: bool,
    ) -> Dict[str, MCPServerConfig]:
        """
        Merge existing servers with new configuration.

        Args:
            existing: Existing server configurations (raw dict)
            new_servers: New server configurations
            verbose: Verbose output

        Returns:
            Merged server dict
        """
        merged = {}

        # Convert existing to MCPServerConfig
        for name, config in existing.items():
            if name not in new_servers:
                # Keep custom servers
                try:
                    merged[name] = MCPServerConfig(**config)
                    if verbose:
                        click.echo(f"  Keeping custom server: {name}")
                except Exception:
                    if verbose:
                        click.echo(f"  Skipping invalid server: {name}")

        # Add/update new servers
        added = []
        updated = []
        for name, config in new_servers.items():
            if name in existing:
                updated.append(name)
            else:
                added.append(name)
            merged[name] = config

        if verbose and added:
            click.echo(f"  Adding servers: {', '.join(added)}")
        if verbose and updated:
            click.echo(f"  Updating servers: {', '.join(updated)}")

        return merged

    def _servers_to_dict(self, servers: Dict[str, MCPServerConfig]) -> Dict[str, dict]:
        """
        Convert MCPServerConfig dict to plain dict for JSON serialization.

        Args:
            servers: Server configurations

        Returns:
            Plain dict
        """
        result = {}
        for name, config in servers.items():
            server_dict = {"command": config.command}
            if config.args:
                server_dict["args"] = config.args
            if config.env:
                server_dict["env"] = config.env
            result[name] = server_dict
        return result

    def validate_selection(
        self, config: MCPConfiguration, selected: List[str]
    ) -> List[str]:
        """
        Validate server selection against requirements.

        Args:
            config: MCP configuration
            selected: Selected server names

        Returns:
            List of validation warnings
        """
        warnings = []

        # Check if all required servers are selected
        required = [
            name
            for name, server in config.mcpServers.items()
            if server.required and name not in selected
        ]
        if required:
            warnings.append(f"Required servers not selected: {', '.join(required)}")

        # Check require_all_servers setting
        if config.config.require_all_servers:
            all_servers = set(config.mcpServers.keys())
            selected_set = set(selected)
            missing = all_servers - selected_set
            if missing:
                warnings.append(
                    f"Configuration requires all servers, but missing:"
                    f" {', '.join(missing)}"
                )

        return warnings
