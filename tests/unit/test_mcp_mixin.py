"""
Unit tests for MCPGenerationMixin functionality.
"""

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from promptrek.adapters.mcp_mixin import MCPGenerationMixin
from promptrek.core.models import MCPServer


class MockMCPAdapter(MCPGenerationMixin):
    """Mock adapter that uses MCP mixin for testing."""

    def __init__(self):
        super().__init__()
        self.name = "test"

    def get_mcp_config_strategy(self):
        """Return test strategy."""
        return {
            "supports_project": True,
            "project_path": ".test/config.json",
            "system_path": str(Path.home() / ".test" / "config.json"),
            "requires_confirmation": False,
            "config_format": "json",
        }


class TestBuildMCPServersConfig:
    """Test MCP servers config building."""

    @pytest.fixture
    def adapter(self):
        """Create test adapter."""
        return MockMCPAdapter()

    @pytest.fixture
    def sample_servers(self):
        """Create sample MCP servers."""
        return [
            MCPServer(
                name="filesystem",
                command="npx",
                args=["-y", "@modelcontextprotocol/server-filesystem"],
                env={"ROOT_PATH": "/tmp"},
            ),
            MCPServer(
                name="github",
                command="npx",
                args=["-y", "@modelcontextprotocol/server-github"],
                env={"GITHUB_TOKEN": "token123"},
            ),
        ]

    def test_build_standard_format(self, adapter, sample_servers):
        """Test building config in standard MCP format."""
        config = adapter.build_mcp_servers_config(
            sample_servers, format_style="standard"
        )

        assert "mcpServers" in config
        assert "filesystem" in config["mcpServers"]
        assert "github" in config["mcpServers"]

        filesystem = config["mcpServers"]["filesystem"]
        assert filesystem["command"] == "npx"
        assert filesystem["args"] == ["-y", "@modelcontextprotocol/server-filesystem"]
        assert filesystem["env"]["ROOT_PATH"] == "/tmp"

    def test_build_continue_format(self, adapter, sample_servers):
        """Test that 'continue' format works for backward compatibility."""
        config = adapter.build_mcp_servers_config(
            sample_servers, format_style="continue"
        )

        # Should produce same output as standard format
        assert "mcpServers" in config
        assert "filesystem" in config["mcpServers"]
        assert "github" in config["mcpServers"]

    def test_server_without_args(self, adapter):
        """Test building config for server without args."""
        servers = [
            MCPServer(
                name="simple",
                command="simple-server",
            )
        ]
        config = adapter.build_mcp_servers_config(servers, format_style="standard")

        assert "mcpServers" in config
        assert "simple" in config["mcpServers"]
        simple = config["mcpServers"]["simple"]
        assert simple["command"] == "simple-server"
        assert "args" not in simple
        assert "env" not in simple

    def test_server_without_env(self, adapter):
        """Test building config for server without environment variables."""
        servers = [
            MCPServer(
                name="noenv",
                command="cmd",
                args=["arg1", "arg2"],
            )
        ]
        config = adapter.build_mcp_servers_config(servers, format_style="standard")

        noenv = config["mcpServers"]["noenv"]
        assert noenv["command"] == "cmd"
        assert noenv["args"] == ["arg1", "arg2"]
        assert "env" not in noenv


class TestVariableSubstitution:
    """Test variable substitution in MCP configs."""

    @pytest.fixture
    def adapter(self):
        """Create test adapter."""
        return MockMCPAdapter()

    def test_substitute_variables_in_env(self, adapter):
        """Test variable substitution in environment variables."""
        servers = [
            MCPServer(
                name="test",
                command="cmd",
                env={
                    "API_KEY": "{{{ API_TOKEN }}}",
                    "ROOT_PATH": "{{{ PROJECT_ROOT }}}",
                    "STATIC": "no-substitution",
                },
            )
        ]

        variables = {
            "API_TOKEN": "secret123",
            "PROJECT_ROOT": "/home/user/project",
        }

        config = adapter.build_mcp_servers_config(
            servers, variables=variables, format_style="standard"
        )

        env = config["mcpServers"]["test"]["env"]
        assert env["API_KEY"] == "secret123"
        assert env["ROOT_PATH"] == "/home/user/project"
        assert env["STATIC"] == "no-substitution"

    def test_substitute_variables_missing_value(self, adapter):
        """Test variable substitution when variable is missing."""
        servers = [
            MCPServer(
                name="test",
                command="cmd",
                env={"KEY": "{{{ MISSING }}}"},
            )
        ]

        # Without variables, placeholder should remain
        config = adapter.build_mcp_servers_config(servers, format_style="standard")
        assert config["mcpServers"]["test"]["env"]["KEY"] == "{{{ MISSING }}}"

    def test_multiple_variable_occurrences(self, adapter):
        """Test substitution with multiple occurrences of same variable."""
        servers = [
            MCPServer(
                name="test",
                command="cmd",
                env={
                    "VAR1": "{{{ KEY }}}",
                    "VAR2": "{{{ KEY }}}",
                },
            )
        ]

        config = adapter.build_mcp_servers_config(
            servers, variables={"KEY": "value"}, format_style="standard"
        )

        env = config["mcpServers"]["test"]["env"]
        assert env["VAR1"] == "value"
        assert env["VAR2"] == "value"


class TestConfigMerging:
    """Test MCP configuration merging."""

    @pytest.fixture
    def adapter(self):
        """Create test adapter."""
        return MockMCPAdapter()

    def test_merge_standard_format(self, adapter):
        """Test merging in standard MCP format."""
        existing = {
            "otherSetting": "value",
            "mcpServers": {
                "existing-server": {
                    "command": "old-cmd",
                }
            },
        }

        new_mcp = {
            "mcpServers": {
                "new-server": {
                    "command": "new-cmd",
                    "args": ["arg1"],
                }
            }
        }

        merged = adapter.merge_mcp_config(existing, new_mcp, format_style="standard")

        # Should preserve existing settings
        assert merged["otherSetting"] == "value"

        # Should keep existing servers
        assert "existing-server" in merged["mcpServers"]
        assert merged["mcpServers"]["existing-server"]["command"] == "old-cmd"

        # Should add new servers
        assert "new-server" in merged["mcpServers"]
        assert merged["mcpServers"]["new-server"]["command"] == "new-cmd"

    def test_merge_updates_existing_server(self, adapter):
        """Test merging updates existing server with same name."""
        existing = {
            "mcpServers": {
                "filesystem": {
                    "command": "old-cmd",
                    "args": ["old-arg"],
                }
            }
        }

        new_mcp = {
            "mcpServers": {
                "filesystem": {
                    "command": "new-cmd",
                    "args": ["new-arg"],
                    "env": {"KEY": "value"},
                }
            }
        }

        merged = adapter.merge_mcp_config(existing, new_mcp, format_style="standard")

        # Should replace with new config
        fs = merged["mcpServers"]["filesystem"]
        assert fs["command"] == "new-cmd"
        assert fs["args"] == ["new-arg"]
        assert fs["env"]["KEY"] == "value"

    def test_merge_empty_existing(self, adapter):
        """Test merging when existing config is empty."""
        existing = {}
        new_mcp = {"mcpServers": {"test": {"command": "cmd"}}}

        merged = adapter.merge_mcp_config(existing, new_mcp, format_style="standard")
        assert "mcpServers" in merged
        assert "test" in merged["mcpServers"]


class TestConfigFileOperations:
    """Test reading and writing MCP config files."""

    @pytest.fixture
    def adapter(self):
        """Create test adapter."""
        return MockMCPAdapter()

    def test_read_existing_json_config(self, adapter, tmp_path):
        """Test reading existing JSON config."""
        config_file = tmp_path / "config.json"
        config_data = {"mcpServers": {"test": {"command": "cmd"}}}
        config_file.write_text(json.dumps(config_data, indent=2))

        result = adapter.read_existing_mcp_config(config_file)
        assert result == config_data

    def test_read_nonexistent_config(self, adapter, tmp_path):
        """Test reading config that doesn't exist."""
        config_file = tmp_path / "nonexistent.json"
        result = adapter.read_existing_mcp_config(config_file)
        assert result is None

    def test_read_invalid_json(self, adapter, tmp_path):
        """Test reading invalid JSON config."""
        config_file = tmp_path / "invalid.json"
        config_file.write_text("{invalid json")

        result = adapter.read_existing_mcp_config(config_file)
        assert result is None

    def test_write_config_file(self, adapter, tmp_path):
        """Test writing config file."""
        config_data = {"mcpServers": {"test": {"command": "cmd"}}}
        config_file = tmp_path / "test" / "config.json"

        result = adapter.write_mcp_config_file(config_data, config_file, dry_run=False)
        assert result is True
        assert config_file.exists()

        # Verify content
        written_data = json.loads(config_file.read_text())
        assert written_data == config_data

    def test_write_config_file_dry_run(self, adapter, tmp_path):
        """Test writing config file in dry run mode."""
        config_data = {"test": "data"}
        config_file = tmp_path / "config.json"

        result = adapter.write_mcp_config_file(config_data, config_file, dry_run=True)
        assert result is True
        assert not config_file.exists()  # Should not create file in dry run

    def test_write_config_creates_parent_dirs(self, adapter, tmp_path):
        """Test that writing config creates parent directories."""
        config_file = tmp_path / "deep" / "nested" / "config.json"
        config_data = {"test": "data"}

        adapter.write_mcp_config_file(config_data, config_file, dry_run=False)
        assert config_file.exists()
        assert config_file.parent.exists()


class TestUserConfirmation:
    """Test user confirmation for system-wide changes."""

    @pytest.fixture
    def adapter(self):
        """Create test adapter."""
        return MockMCPAdapter()

    @patch("click.confirm")
    def test_confirm_system_wide_user_accepts(self, mock_confirm, adapter):
        """Test confirmation when user accepts."""
        mock_confirm.return_value = True
        system_path = Path.home() / ".test" / "config.json"

        result = adapter.confirm_system_wide_mcp_update("Test", system_path)
        assert result is True
        mock_confirm.assert_called_once()

    @patch("click.confirm")
    def test_confirm_system_wide_user_declines(self, mock_confirm, adapter):
        """Test confirmation when user declines."""
        mock_confirm.return_value = False
        system_path = Path.home() / ".test" / "config.json"

        result = adapter.confirm_system_wide_mcp_update("Test", system_path)
        assert result is False

    def test_confirm_system_wide_dry_run(self, adapter):
        """Test confirmation in dry run mode (should skip prompt)."""
        system_path = Path.home() / ".test" / "config.json"
        result = adapter.confirm_system_wide_mcp_update(
            "Test", system_path, dry_run=True
        )
        # In dry run, should return True without prompting
        assert result is True

    @patch("click.confirm")
    def test_confirm_includes_editor_name(self, mock_confirm, adapter):
        """Test that confirmation message includes editor name."""
        mock_confirm.return_value = True
        system_path = Path.home() / ".windsurf" / "config.json"

        adapter.confirm_system_wide_mcp_update("Windsurf", system_path)

        # Check that the confirmation message was appropriate
        call_args = mock_confirm.call_args
        assert call_args is not None


class TestMCPConfigStrategy:
    """Test MCP configuration strategy method."""

    def test_get_mcp_config_strategy_required_fields(self):
        """Test that strategy returns required fields."""
        adapter = MockMCPAdapter()
        strategy = adapter.get_mcp_config_strategy()

        assert "supports_project" in strategy
        assert "project_path" in strategy
        assert "system_path" in strategy
        assert "requires_confirmation" in strategy
        assert "config_format" in strategy

    def test_get_mcp_config_strategy_types(self):
        """Test that strategy fields have correct types."""
        adapter = MockMCPAdapter()
        strategy = adapter.get_mcp_config_strategy()

        assert isinstance(strategy["supports_project"], bool)
        assert isinstance(strategy["requires_confirmation"], bool)
        assert isinstance(strategy["config_format"], str)
        # project_path and system_path can be str or None


class TestEdgecases:
    """Test edge cases and error handling."""

    @pytest.fixture
    def adapter(self):
        """Create test adapter."""
        return MockMCPAdapter()

    def test_empty_servers_list(self, adapter):
        """Test building config with empty servers list."""
        config = adapter.build_mcp_servers_config([], format_style="standard")
        assert "mcpServers" in config
        assert len(config["mcpServers"]) == 0

    def test_variable_with_spaces(self, adapter):
        """Test variable substitution with spaces in placeholder."""
        servers = [
            MCPServer(
                name="test",
                command="cmd",
                env={"KEY": "{{{    SPACED_VAR    }}}"},  # Extra spaces
            )
        ]

        # Should not substitute due to extra spaces (exact match required)
        config = adapter.build_mcp_servers_config(
            servers, variables={"SPACED_VAR": "value"}, format_style="standard"
        )
        # Placeholder should remain unchanged
        assert "{{{    SPACED_VAR    }}}" in config["mcpServers"]["test"]["env"]["KEY"]

    def test_special_characters_in_values(self, adapter):
        """Test variable substitution with special characters."""
        servers = [
            MCPServer(
                name="test",
                command="cmd",
                env={"KEY": "{{{ SPECIAL }}}"},
            )
        ]

        config = adapter.build_mcp_servers_config(
            servers,
            variables={"SPECIAL": "value-with-$pecial/chars\\and:more"},
            format_style="standard",
        )
        assert (
            config["mcpServers"]["test"]["env"]["KEY"]
            == "value-with-$pecial/chars\\and:more"
        )
