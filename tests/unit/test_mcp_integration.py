"""
Integration tests for MCP with local variables.
"""

import json
from pathlib import Path
from typing import Any, Dict

import pytest
import yaml

from promptrek.core.mcp_parser import MCPParser
from promptrek.utils.variables import VariableSubstitution


class TestMCPLocalVariablesIntegration:
    """Test MCP integration with local variables file."""

    @pytest.fixture
    def project_dir(self, tmp_path: Path) -> Path:
        """Create a project directory with MCP config and local variables."""
        # Create MCP config with variables
        mcp_config: Dict[str, Any] = {
            "schema_version": "1.0.0",
            "metadata": {
                "title": "Test Project",
                "description": "Test configuration",
            },
            "config": {
                "allow_custom_servers": True,
                "require_all_servers": False,
            },
            "mcpServers": {
                "github": {
                    "command": "npx",
                    "args": ["-y", "@modelcontextprotocol/server-github"],
                    "env": {
                        "GITHUB_PERSONAL_ACCESS_TOKEN": "${GITHUB_TOKEN}",
                    },
                    "description": "GitHub API access",
                },
                "filesystem": {
                    "command": "npx",
                    "args": [
                        "-y",
                        "@modelcontextprotocol/server-filesystem",
                        "{{{ PROJECT_PATH }}}",
                    ],
                    "description": "Filesystem access",
                },
                "database": {
                    "command": "npx",
                    "args": [
                        "-y",
                        "@modelcontextprotocol/server-postgres",
                        "{{{ DATABASE_URL }}}",
                    ],
                    "env": {
                        "PGPASSWORD": "{{{ DATABASE_PASSWORD }}}",
                    },
                },
            },
        }

        mcp_file = tmp_path / "mcp.promptrek.json"
        with open(mcp_file, "w", encoding="utf-8") as f:
            json.dump(mcp_config, f)

        # Create local variables file
        local_vars: Dict[str, str] = {
            "GITHUB_TOKEN": "ghp_test_token_12345",
            "PROJECT_PATH": "/home/user/projects/test",
            "DATABASE_URL": "postgresql://localhost:5432/testdb",
            "DATABASE_PASSWORD": "test_password",
        }

        var_file = tmp_path / "variables.promptrek.yaml"
        with open(var_file, "w", encoding="utf-8") as f:
            yaml.dump(local_vars, f)

        return tmp_path

    def test_load_and_substitute_local_variables(self, project_dir: Path) -> None:
        """Test loading local variables and substituting in MCP config."""
        # Load local variables
        var_sub = VariableSubstitution()
        local_vars = var_sub.load_local_variables(project_dir)

        assert len(local_vars) == 4
        assert local_vars["GITHUB_TOKEN"] == "ghp_test_token_12345"
        assert local_vars["PROJECT_PATH"] == "/home/user/projects/test"

        # Parse MCP config
        parser = MCPParser()
        mcp_file = project_dir / "mcp.promptrek.json"
        config = parser.parse_file(mcp_file)

        # Substitute variables
        result = parser.substitute_variables(config, local_vars, use_env=False)

        # Verify substitution
        github_env = result.mcpServers["github"].env
        assert github_env is not None
        assert github_env["GITHUB_PERSONAL_ACCESS_TOKEN"] == "ghp_test_token_12345"

        filesystem_args = result.mcpServers["filesystem"].args
        assert filesystem_args is not None
        assert filesystem_args[2] == "/home/user/projects/test"

        database_args = result.mcpServers["database"].args
        assert database_args is not None
        assert database_args[2] == "postgresql://localhost:5432/testdb"

        database_env = result.mcpServers["database"].env
        assert database_env is not None
        assert database_env["PGPASSWORD"] == "test_password"

    def test_cli_variables_override_local_variables(self, project_dir: Path) -> None:
        """Test that CLI variables override local variables."""
        # Load local variables
        var_sub = VariableSubstitution()
        local_vars = var_sub.load_local_variables(project_dir)

        # CLI override
        cli_vars: Dict[str, str] = {"GITHUB_TOKEN": "ghp_cli_override_token"}

        # Merge: local < CLI
        merged_vars = local_vars.copy()
        merged_vars.update(cli_vars)

        # Parse and substitute
        parser = MCPParser()
        mcp_file = project_dir / "mcp.promptrek.json"
        config = parser.parse_file(mcp_file)
        result = parser.substitute_variables(config, merged_vars, use_env=False)

        # CLI value should win
        github_env = result.mcpServers["github"].env
        assert github_env is not None
        assert github_env["GITHUB_PERSONAL_ACCESS_TOKEN"] == "ghp_cli_override_token"

        # Other local values should remain
        filesystem_args = result.mcpServers["filesystem"].args
        assert filesystem_args is not None
        assert filesystem_args[2] == "/home/user/projects/test"

    def test_mixed_variable_syntax_in_same_config(self, project_dir: Path) -> None:
        """Test that both ${VAR} and {{{ VAR }}} work in same config."""
        # Load local variables
        var_sub = VariableSubstitution()
        local_vars = var_sub.load_local_variables(project_dir)

        # Parse and substitute
        parser = MCPParser()
        mcp_file = project_dir / "mcp.promptrek.json"
        config = parser.parse_file(mcp_file)
        result = parser.substitute_variables(config, local_vars, use_env=False)

        # Both syntax styles should work
        # ${GITHUB_TOKEN} in github server
        github_env = result.mcpServers["github"].env
        assert github_env is not None
        assert github_env["GITHUB_PERSONAL_ACCESS_TOKEN"] == "ghp_test_token_12345"

        # {{{ PROJECT_PATH }}} in filesystem server
        filesystem_args = result.mcpServers["filesystem"].args
        assert filesystem_args is not None
        assert filesystem_args[2] == "/home/user/projects/test"

        # {{{ DATABASE_URL }}} in database server
        database_args = result.mcpServers["database"].args
        assert database_args is not None
        assert database_args[2] == "postgresql://localhost:5432/testdb"

    def test_missing_variables_detected(self, project_dir: Path) -> None:
        """Test that missing variables are properly detected."""
        # Parse config
        parser = MCPParser()
        mcp_file = project_dir / "mcp.promptrek.json"
        config = parser.parse_file(mcp_file)

        # Only provide partial variables
        partial_vars: Dict[str, str] = {"GITHUB_TOKEN": "token"}

        # Validate should detect missing variables
        missing = parser.validate_variables(config, partial_vars)

        assert len(missing) == 3
        assert "PROJECT_PATH" in missing
        assert "DATABASE_URL" in missing
        assert "DATABASE_PASSWORD" in missing

    def test_local_variables_not_required_with_env(
        self, project_dir: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test that environment variables work when local file doesn't exist."""
        # Set environment variables
        monkeypatch.setenv("GITHUB_TOKEN", "ghp_env_token")
        monkeypatch.setenv("PROJECT_PATH", "/env/path")
        monkeypatch.setenv("DATABASE_URL", "postgresql://env/db")
        monkeypatch.setenv("DATABASE_PASSWORD", "env_password")

        # Remove local variables file
        var_file = project_dir / "variables.promptrek.yaml"
        var_file.unlink()

        # Parse and substitute using env
        parser = MCPParser()
        mcp_file = project_dir / "mcp.promptrek.json"
        config = parser.parse_file(mcp_file)

        # Substitute with empty dict but use_env=True
        result = parser.substitute_variables(config, {}, use_env=True)

        # Should use environment variables
        github_env = result.mcpServers["github"].env
        assert github_env is not None
        assert github_env["GITHUB_PERSONAL_ACCESS_TOKEN"] == "ghp_env_token"

        filesystem_args = result.mcpServers["filesystem"].args
        assert filesystem_args is not None
        assert filesystem_args[2] == "/env/path"

        database_args = result.mcpServers["database"].args
        assert database_args is not None
        assert database_args[2] == "postgresql://env/db"

        database_env = result.mcpServers["database"].env
        assert database_env is not None
        assert database_env["PGPASSWORD"] == "env_password"

    def test_extract_all_variables_both_syntaxes(self, project_dir: Path) -> None:
        """Test extracting all variables from config with mixed syntax."""
        parser = MCPParser()
        mcp_file = project_dir / "mcp.promptrek.json"
        config = parser.parse_file(mcp_file)

        variables = parser.extract_variables(config)

        # Should find all 4 variables regardless of syntax
        assert len(variables) == 4
        assert "GITHUB_TOKEN" in variables
        assert "PROJECT_PATH" in variables
        assert "DATABASE_URL" in variables
        assert "DATABASE_PASSWORD" in variables
