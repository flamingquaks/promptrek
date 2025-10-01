"""
Tests for MCP generator functionality.
"""

import json
from pathlib import Path

import pytest
import yaml

from promptrek.core.mcp_generator import MCPGenerator
from promptrek.core.models import (
    MCPConfig,
    MCPConfiguration,
    MCPMetadata,
    MCPServerConfig,
)


class TestMCPGenerator:
    """Test suite for MCPGenerator."""

    @pytest.fixture
    def generator(self):
        """Create generator instance."""
        return MCPGenerator()

    @pytest.fixture
    def sample_config(self):
        """Create sample MCP configuration."""
        return MCPConfiguration(
            schema_version="1.0.0",
            metadata=MCPMetadata(
                title="Test Config", description="Test MCP configuration"
            ),
            config=MCPConfig(allow_custom_servers=True, require_all_servers=False),
            mcpServers={
                "filesystem": MCPServerConfig(
                    command="npx",
                    args=["-y", "@modelcontextprotocol/server-filesystem", "."],
                    description="Filesystem access",
                    required=True,
                ),
                "git": MCPServerConfig(
                    command="npx",
                    args=["-y", "@modelcontextprotocol/server-git"],
                    description="Git operations",
                    required=False,
                ),
            },
        )

    def test_generate_cursor_mcp(self, generator, sample_config, tmp_path):
        """Test generating Cursor MCP configuration."""
        result = generator.generate_cursor_mcp(
            sample_config, tmp_path, dry_run=False, verbose=False
        )

        assert result == tmp_path / ".cursor" / "mcp.json"
        assert result.exists()

        with open(result) as f:
            data = json.load(f)

        assert "mcpServers" in data
        assert "filesystem" in data["mcpServers"]
        assert "git" in data["mcpServers"]

    def test_generate_cursor_mcp_dry_run(self, generator, sample_config, tmp_path):
        """Test Cursor MCP generation in dry-run mode."""
        result = generator.generate_cursor_mcp(
            sample_config, tmp_path, dry_run=True, verbose=False
        )

        assert result == tmp_path / ".cursor" / "mcp.json"
        assert not result.exists()  # Should not create file in dry-run

    def test_generate_cursor_mcp_with_selection(
        self, generator, sample_config, tmp_path
    ):
        """Test Cursor MCP generation with server selection."""
        result = generator.generate_cursor_mcp(
            sample_config,
            tmp_path,
            selected_servers=["filesystem"],
            dry_run=False,
            verbose=False,
        )

        with open(result) as f:
            data = json.load(f)

        assert "filesystem" in data["mcpServers"]
        assert "git" not in data["mcpServers"]

    def test_generate_cursor_mcp_merge_existing(
        self, generator, sample_config, tmp_path
    ):
        """Test merging with existing Cursor MCP configuration."""
        # Create existing config with custom server
        cursor_dir = tmp_path / ".cursor"
        cursor_dir.mkdir()
        existing_file = cursor_dir / "mcp.json"

        existing_data = {
            "mcpServers": {"custom-server": {"command": "node", "args": ["custom.js"]}}
        }

        with open(existing_file, "w") as f:
            json.dump(existing_data, f)

        # Generate with merge enabled
        result = generator.generate_cursor_mcp(
            sample_config, tmp_path, dry_run=False, verbose=False
        )

        with open(result) as f:
            data = json.load(f)

        # Should have both custom and new servers
        assert "custom-server" in data["mcpServers"]
        assert "filesystem" in data["mcpServers"]
        assert "git" in data["mcpServers"]

    def test_generate_cursor_mcp_no_merge(self, generator, sample_config, tmp_path):
        """Test replacing existing Cursor MCP configuration."""
        # Update config to disable merging
        sample_config.config.allow_custom_servers = False

        # Create existing config with custom server
        cursor_dir = tmp_path / ".cursor"
        cursor_dir.mkdir()
        existing_file = cursor_dir / "mcp.json"

        existing_data = {
            "mcpServers": {"custom-server": {"command": "node", "args": ["custom.js"]}}
        }

        with open(existing_file, "w") as f:
            json.dump(existing_data, f)

        # Generate with merge disabled
        result = generator.generate_cursor_mcp(
            sample_config, tmp_path, dry_run=False, verbose=False
        )

        with open(result) as f:
            data = json.load(f)

        # Should only have new servers
        assert "custom-server" not in data["mcpServers"]
        assert "filesystem" in data["mcpServers"]
        assert "git" in data["mcpServers"]

    def test_generate_continue_mcp(self, generator, sample_config, tmp_path):
        """Test generating Continue MCP configuration."""
        result = generator.generate_continue_mcp(
            sample_config, tmp_path, dry_run=False, verbose=False
        )

        assert result == tmp_path / "config.yaml"
        assert result.exists()

        with open(result) as f:
            data = yaml.safe_load(f)

        assert "mcpServers" in data
        assert len(data["mcpServers"]) == 2
        assert data["mcpServers"][0]["name"] in ["filesystem", "git"]

    def test_generate_continue_mcp_format(self, generator, sample_config, tmp_path):
        """Test Continue MCP configuration format."""
        result = generator.generate_continue_mcp(
            sample_config, tmp_path, dry_run=False, verbose=False
        )

        with open(result) as f:
            data = yaml.safe_load(f)

        # Check format of server entries
        for server in data["mcpServers"]:
            assert "name" in server
            assert "command" in server
            # args and env are optional

    def test_validate_selection_required_missing(self, generator, sample_config):
        """Test validation detects missing required servers."""
        warnings = generator.validate_selection(sample_config, ["git"])

        assert len(warnings) > 0
        assert any("filesystem" in w.lower() for w in warnings)

    def test_validate_selection_require_all(self, generator, sample_config):
        """Test validation with require_all_servers setting."""
        sample_config.config.require_all_servers = True

        warnings = generator.validate_selection(sample_config, ["filesystem"])

        assert len(warnings) > 0
        assert any("require" in w.lower() for w in warnings)

    def test_validate_selection_all_ok(self, generator, sample_config):
        """Test validation passes with all servers selected."""
        warnings = generator.validate_selection(sample_config, ["filesystem", "git"])

        assert len(warnings) == 0

    def test_filter_servers(self, generator, sample_config):
        """Test server filtering."""
        filtered = generator._filter_servers(sample_config.mcpServers, ["filesystem"])

        assert "filesystem" in filtered
        assert "git" not in filtered

    def test_filter_servers_none_selection(self, generator, sample_config):
        """Test server filtering with None selection returns all."""
        filtered = generator._filter_servers(sample_config.mcpServers, None)

        assert "filesystem" in filtered
        assert "git" in filtered

    def test_servers_to_dict(self, generator, sample_config):
        """Test converting servers to dictionary."""
        result = generator._servers_to_dict(sample_config.mcpServers)

        assert "filesystem" in result
        assert result["filesystem"]["command"] == "npx"
        assert isinstance(result["filesystem"]["args"], list)
