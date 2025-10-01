"""
Tests for MCP parser functionality.
"""

import json
import os
from pathlib import Path

import pytest

from promptrek.core.exceptions import MCPParsingError
from promptrek.core.mcp_parser import MCPParser
from promptrek.core.models import MCPConfiguration


class TestMCPParser:
    """Test suite for MCPParser."""

    @pytest.fixture
    def parser(self):
        """Create parser instance."""
        return MCPParser()

    @pytest.fixture
    def valid_mcp_config(self, tmp_path):
        """Create valid MCP configuration file."""
        config = {
            "schema_version": "1.0.0",
            "metadata": {
                "title": "Test MCP Config",
                "description": "Test configuration",
            },
            "config": {
                "allow_custom_servers": True,
                "require_all_servers": False,
            },
            "mcpServers": {
                "test-server": {
                    "command": "npx",
                    "args": ["-y", "test-server"],
                    "description": "Test server",
                }
            },
        }

        mcp_file = tmp_path / "mcp.promptrek.json"
        with open(mcp_file, "w") as f:
            json.dump(config, f)

        return mcp_file

    def test_parse_valid_file(self, parser, valid_mcp_config):
        """Test parsing valid MCP configuration file."""
        config = parser.parse_file(valid_mcp_config)

        assert isinstance(config, MCPConfiguration)
        assert config.schema_version == "1.0.0"
        assert config.metadata.title == "Test MCP Config"
        assert "test-server" in config.mcpServers

    def test_parse_nonexistent_file(self, parser, tmp_path):
        """Test parsing nonexistent file raises error."""
        nonexistent = tmp_path / "nonexistent.json"

        with pytest.raises(MCPParsingError, match="not found"):
            parser.parse_file(nonexistent)

    def test_parse_invalid_json(self, parser, tmp_path):
        """Test parsing invalid JSON raises error."""
        invalid_file = tmp_path / "invalid.json"
        with open(invalid_file, "w") as f:
            f.write("{invalid json")

        with pytest.raises(MCPParsingError, match="Invalid JSON"):
            parser.parse_file(invalid_file)

    def test_parse_invalid_schema(self, parser, tmp_path):
        """Test parsing invalid schema raises error."""
        invalid_file = tmp_path / "invalid.json"
        config = {
            "schema_version": "invalid",  # Should be x.y.z format
            "metadata": {"title": "Test"},
        }
        with open(invalid_file, "w") as f:
            json.dump(config, f)

        with pytest.raises(MCPParsingError, match="Invalid MCP configuration"):
            parser.parse_file(invalid_file)

    def test_parse_file_read_error(self, parser, tmp_path):
        """Test parsing file with read error."""
        invalid_file = tmp_path / "unreadable.json"
        invalid_file.write_text("{}")
        # Make file unreadable by changing permissions
        invalid_file.chmod(0o000)

        try:
            with pytest.raises(MCPParsingError, match="Error reading"):
                parser.parse_file(invalid_file)
        finally:
            # Restore permissions for cleanup
            invalid_file.chmod(0o644)

    def test_substitute_variables_with_provided_vars(self, parser, valid_mcp_config):
        """Test variable substitution with provided variables."""
        config_data = {
            "schema_version": "1.0.0",
            "metadata": {"title": "Test", "description": "Test"},
            "mcpServers": {
                "server": {
                    "command": "npx",
                    "env": {"API_KEY": "${API_KEY}", "TOKEN": "${TOKEN}"},
                }
            },
        }

        config_file = valid_mcp_config.parent / "var_test.json"
        with open(config_file, "w") as f:
            json.dump(config_data, f)

        config = parser.parse_file(config_file)
        variables = {"API_KEY": "secret", "TOKEN": "token123"}

        result = parser.substitute_variables(config, variables, use_env=False)

        assert result.mcpServers["server"].env["API_KEY"] == "secret"
        assert result.mcpServers["server"].env["TOKEN"] == "token123"

    def test_substitute_variables_with_env(self, parser, valid_mcp_config, monkeypatch):
        """Test variable substitution using environment variables."""
        monkeypatch.setenv("API_KEY", "env_secret")

        config_data = {
            "schema_version": "1.0.0",
            "metadata": {"title": "Test", "description": "Test"},
            "mcpServers": {
                "server": {"command": "npx", "env": {"API_KEY": "${API_KEY}"}}
            },
        }

        config_file = valid_mcp_config.parent / "env_test.json"
        with open(config_file, "w") as f:
            json.dump(config_data, f)

        config = parser.parse_file(config_file)
        result = parser.substitute_variables(config, use_env=True)

        assert result.mcpServers["server"].env["API_KEY"] == "env_secret"

    def test_substitute_variables_unresolved(self, parser, valid_mcp_config):
        """Test that unresolved variables are left as-is."""
        config_data = {
            "schema_version": "1.0.0",
            "metadata": {"title": "Test", "description": "Test"},
            "mcpServers": {
                "server": {"command": "npx", "env": {"API_KEY": "${API_KEY}"}}
            },
        }

        config_file = valid_mcp_config.parent / "unresolved.json"
        with open(config_file, "w") as f:
            json.dump(config_data, f)

        config = parser.parse_file(config_file)
        result = parser.substitute_variables(config, use_env=False)

        assert result.mcpServers["server"].env["API_KEY"] == "${API_KEY}"

    def test_find_mcp_file(self, parser, tmp_path):
        """Test finding MCP file in directory."""
        mcp_file = tmp_path / "mcp.promptrek.json"
        mcp_file.write_text("{}")

        found = parser.find_mcp_file(tmp_path)
        assert found == mcp_file

    def test_find_mcp_file_not_found(self, parser, tmp_path):
        """Test finding MCP file returns None when not found."""
        found = parser.find_mcp_file(tmp_path)
        assert found is None

    def test_extract_variables(self, parser, valid_mcp_config):
        """Test extracting variable names from configuration."""
        config_data = {
            "schema_version": "1.0.0",
            "metadata": {"title": "Test", "description": "Test"},
            "mcpServers": {
                "server1": {
                    "command": "npx",
                    "env": {"API_KEY": "${API_KEY}", "TOKEN": "${TOKEN}"},
                },
                "server2": {"command": "npx", "env": {"SECRET": "${SECRET}"}},
            },
        }

        config_file = valid_mcp_config.parent / "extract.json"
        with open(config_file, "w") as f:
            json.dump(config_data, f)

        config = parser.parse_file(config_file)
        variables = parser.extract_variables(config)

        assert variables == {"API_KEY", "TOKEN", "SECRET"}

    def test_validate_variables_all_present(self, parser, valid_mcp_config):
        """Test validation passes when all variables are provided."""
        config_data = {
            "schema_version": "1.0.0",
            "metadata": {"title": "Test", "description": "Test"},
            "mcpServers": {
                "server": {"command": "npx", "env": {"API_KEY": "${API_KEY}"}}
            },
        }

        config_file = valid_mcp_config.parent / "validate.json"
        with open(config_file, "w") as f:
            json.dump(config_data, f)

        config = parser.parse_file(config_file)
        provided_vars = {"API_KEY": "secret"}

        missing = parser.validate_variables(config, provided_vars)
        assert missing == []

    def test_validate_variables_missing(self, parser, valid_mcp_config):
        """Test validation detects missing variables."""
        config_data = {
            "schema_version": "1.0.0",
            "metadata": {"title": "Test", "description": "Test"},
            "mcpServers": {
                "server": {
                    "command": "npx",
                    "env": {"API_KEY": "${API_KEY}", "TOKEN": "${TOKEN}"},
                }
            },
        }

        config_file = valid_mcp_config.parent / "missing.json"
        with open(config_file, "w") as f:
            json.dump(config_data, f)

        config = parser.parse_file(config_file)
        provided_vars = {"API_KEY": "secret"}  # Missing TOKEN

        missing = parser.validate_variables(config, provided_vars)
        assert "TOKEN" in missing
        assert len(missing) == 1

    def test_substitute_promptrek_style_variables(self, parser, valid_mcp_config):
        """Test substitution of PrompTrek-style {{{ VAR }}} variables."""
        config_data = {
            "schema_version": "1.0.0",
            "metadata": {"title": "Test", "description": "Test"},
            "mcpServers": {
                "server": {
                    "command": "npx",
                    "env": {
                        "API_KEY": "{{{ API_KEY }}}",
                        "TOKEN": "{{{ TOKEN }}}",
                    },
                }
            },
        }

        config_file = valid_mcp_config.parent / "pt_vars.json"
        with open(config_file, "w") as f:
            json.dump(config_data, f)

        config = parser.parse_file(config_file)
        variables = {"API_KEY": "secret-key", "TOKEN": "secret-token"}

        result = parser.substitute_variables(config, variables, use_env=False)

        assert result.mcpServers["server"].env["API_KEY"] == "secret-key"
        assert result.mcpServers["server"].env["TOKEN"] == "secret-token"

    def test_substitute_mixed_variable_styles(self, parser, valid_mcp_config):
        """Test substitution with both ${VAR} and {{{ VAR }}} styles."""
        config_data = {
            "schema_version": "1.0.0",
            "metadata": {"title": "Test", "description": "Test"},
            "mcpServers": {
                "server": {
                    "command": "npx",
                    "env": {
                        "MCP_STYLE": "${API_KEY}",
                        "PROMPTREK_STYLE": "{{{ TOKEN }}}",
                    },
                }
            },
        }

        config_file = valid_mcp_config.parent / "mixed_vars.json"
        with open(config_file, "w") as f:
            json.dump(config_data, f)

        config = parser.parse_file(config_file)
        variables = {"API_KEY": "mcp-secret", "TOKEN": "pt-token"}

        result = parser.substitute_variables(config, variables, use_env=False)

        assert result.mcpServers["server"].env["MCP_STYLE"] == "mcp-secret"
        assert result.mcpServers["server"].env["PROMPTREK_STYLE"] == "pt-token"

    def test_substitute_variables_in_args(self, parser, valid_mcp_config):
        """Test substitution of variables in args field."""
        config_data = {
            "schema_version": "1.0.0",
            "metadata": {"title": "Test", "description": "Test"},
            "mcpServers": {
                "server": {
                    "command": "npx",
                    "args": ["--path", "{{{ PROJECT_PATH }}}", "--key", "${API_KEY}"],
                }
            },
        }

        config_file = valid_mcp_config.parent / "args_vars.json"
        with open(config_file, "w") as f:
            json.dump(config_data, f)

        config = parser.parse_file(config_file)
        variables = {"PROJECT_PATH": "/home/user/project", "API_KEY": "secret"}

        result = parser.substitute_variables(config, variables, use_env=False)

        assert result.mcpServers["server"].args[0] == "--path"
        assert result.mcpServers["server"].args[1] == "/home/user/project"
        assert result.mcpServers["server"].args[2] == "--key"
        assert result.mcpServers["server"].args[3] == "secret"

    def test_extract_variables_both_styles(self, parser, valid_mcp_config):
        """Test extraction of variables from both syntax styles."""
        config_data = {
            "schema_version": "1.0.0",
            "metadata": {"title": "Test", "description": "Test"},
            "mcpServers": {
                "server1": {
                    "command": "npx",
                    "env": {"KEY1": "${VAR1}", "KEY2": "{{{ VAR2 }}}"},
                },
                "server2": {
                    "command": "npx",
                    "args": ["--path", "{{{ PROJECT_PATH }}}"],
                    "env": {"KEY3": "${VAR3}"},
                },
            },
        }

        config_file = valid_mcp_config.parent / "both_styles.json"
        with open(config_file, "w") as f:
            json.dump(config_data, f)

        config = parser.parse_file(config_file)
        variables = parser.extract_variables(config)

        assert variables == {"VAR1", "VAR2", "VAR3", "PROJECT_PATH"}

    def test_variable_precedence_local_over_env(
        self, parser, valid_mcp_config, monkeypatch
    ):
        """Test that provided variables take precedence over environment variables."""
        monkeypatch.setenv("API_KEY", "env-value")

        config_data = {
            "schema_version": "1.0.0",
            "metadata": {"title": "Test", "description": "Test"},
            "mcpServers": {
                "server": {
                    "command": "npx",
                    "env": {"API_KEY": "${API_KEY}"},
                }
            },
        }

        config_file = valid_mcp_config.parent / "precedence.json"
        with open(config_file, "w") as f:
            json.dump(config_data, f)

        config = parser.parse_file(config_file)
        variables = {"API_KEY": "local-value"}

        result = parser.substitute_variables(config, variables, use_env=True)

        # Local variable should take precedence over env
        assert result.mcpServers["server"].env["API_KEY"] == "local-value"
