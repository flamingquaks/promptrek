"""
MCP configuration parser.

Handles parsing and validation of mcp.promptrek.json files.
"""

import json
import os
import re
from pathlib import Path
from typing import Dict, Optional

from .exceptions import MCPParsingError
from .models import MCPConfiguration


class MCPParser:
    """Parser for MCP configuration files."""

    def __init__(self):
        """Initialize MCP parser."""
        self.variable_pattern = re.compile(r"\$\{([A-Z_][A-Z0-9_]*)\}")

    def parse_file(self, file_path: Path) -> MCPConfiguration:
        """
        Parse an MCP configuration file.

        Args:
            file_path: Path to mcp.promptrek.json file

        Returns:
            MCPConfiguration object

        Raises:
            MCPParsingError: If file cannot be parsed
        """
        if not file_path.exists():
            raise MCPParsingError(f"MCP configuration file not found: {file_path}")

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            raise MCPParsingError(f"Invalid JSON in {file_path}: {e}")
        except Exception as e:
            raise MCPParsingError(f"Error reading {file_path}: {e}")

        try:
            config = MCPConfiguration(**data)
            return config
        except Exception as e:
            raise MCPParsingError(f"Invalid MCP configuration in {file_path}: {e}")

    def substitute_variables(
        self,
        config: MCPConfiguration,
        variables: Optional[Dict[str, str]] = None,
        use_env: bool = True,
    ) -> MCPConfiguration:
        """
        Substitute variables in MCP server configurations.

        Supports ${VAR_NAME} syntax in environment variables.

        Args:
            config: MCP configuration to process
            variables: Dictionary of variable values to use
            use_env: Whether to use environment variables

        Returns:
            MCPConfiguration with variables substituted
        """
        variables = variables or {}

        # Process each server's environment variables
        for server_name, server_config in config.mcpServers.items():
            if server_config.env:
                new_env = {}
                for key, value in server_config.env.items():
                    new_env[key] = self._substitute_value(value, variables, use_env)
                server_config.env = new_env

        return config

    def _substitute_value(
        self, value: str, variables: Dict[str, str], use_env: bool
    ) -> str:
        """
        Substitute variables in a single value.

        Args:
            value: Value to process
            variables: Variable dictionary
            use_env: Whether to use environment variables

        Returns:
            Value with variables substituted
        """

        def replace_var(match):
            var_name = match.group(1)
            # Check provided variables first
            if var_name in variables:
                return variables[var_name]
            # Then check environment
            if use_env and var_name in os.environ:
                return os.environ[var_name]
            # Leave unresolved variables as-is
            return match.group(0)

        return self.variable_pattern.sub(replace_var, value)

    def find_mcp_file(self, directory: Path) -> Optional[Path]:
        """
        Find mcp.promptrek.json file in directory.

        Args:
            directory: Directory to search

        Returns:
            Path to MCP file or None if not found
        """
        mcp_file = directory / "mcp.promptrek.json"
        return mcp_file if mcp_file.exists() else None

    def extract_variables(self, config: MCPConfiguration) -> set[str]:
        """
        Extract all variable names used in configuration.

        Args:
            config: MCP configuration

        Returns:
            Set of variable names
        """
        variables = set()

        for server_config in config.mcpServers.values():
            if server_config.env:
                for value in server_config.env.values():
                    matches = self.variable_pattern.findall(value)
                    variables.update(matches)

        return variables

    def validate_variables(
        self, config: MCPConfiguration, provided_vars: Optional[Dict[str, str]] = None
    ) -> list[str]:
        """
        Validate that all required variables are available.

        Args:
            config: MCP configuration
            provided_vars: Provided variable values

        Returns:
            List of missing variable names
        """
        provided_vars = provided_vars or {}
        required_vars = self.extract_variables(config)
        missing = []

        for var_name in required_vars:
            if var_name not in provided_vars and var_name not in os.environ:
                missing.append(var_name)

        return missing
