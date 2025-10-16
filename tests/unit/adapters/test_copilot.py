"""
Unit tests for Copilot adapter.
"""

import json
from pathlib import Path

import pytest

from promptrek.adapters.copilot import CopilotAdapter
from promptrek.core.models import PromptMetadata, UniversalPromptV2, UniversalPromptV3

from .base_test import TestAdapterBase


class TestCopilotAdapter(TestAdapterBase):
    """Test Copilot adapter."""

    @pytest.fixture
    def adapter(self):
        """Create Copilot adapter instance."""
        return CopilotAdapter()

    def test_init(self, adapter):
        """Test adapter initialization."""
        assert adapter.name == "copilot"
        assert ".github/copilot-instructions.md" in adapter.file_patterns

    def test_supports_features(self, adapter):
        """Test feature support."""
        assert adapter.supports_variables() is True
        assert adapter.supports_conditionals() is True

    def test_generate_v2_basic(self, adapter, tmp_path):
        """Test basic v2 generation."""
        prompt = UniversalPromptV2(
            schema_version="2.0.0",
            metadata=PromptMetadata(
                title="Test Project",
                description="Test description",
                version="1.0.0",
            ),
            content="# Test Project\n\nThis is test content.",
        )

        files = adapter.generate(prompt, tmp_path, dry_run=False, verbose=False)

        assert len(files) == 1
        instructions_file = tmp_path / ".github" / "copilot-instructions.md"
        assert instructions_file.exists()
        content = instructions_file.read_text()
        assert "# Test Project" in content
        assert "This is test content." in content

    def test_generate_v3_with_mcp(self, adapter, tmp_path):
        """Test v3 generation with MCP servers."""
        prompt = UniversalPromptV3(
            schema_version="3.0.0",
            metadata=PromptMetadata(
                title="Test MCP Project",
                description="Test MCP description",
                version="1.0.0",
            ),
            content="# Test MCP Project\n\nContent with MCP.",
            mcp_servers=[
                {
                    "name": "filesystem",
                    "command": "npx",
                    "args": ["-y", "@modelcontextprotocol/server-filesystem", "/tmp"],
                    "description": "Filesystem access",
                }
            ],
        )

        files = adapter.generate(prompt, tmp_path, dry_run=False, verbose=False)

        assert len(files) == 2
        instructions_file = tmp_path / ".github" / "copilot-instructions.md"
        mcp_file = tmp_path / ".vscode" / "mcp.json"

        assert instructions_file.exists()
        assert mcp_file.exists()

        # Verify MCP config
        mcp_config = json.loads(mcp_file.read_text())
        assert "mcpServers" in mcp_config
        assert "filesystem" in mcp_config["mcpServers"]
        assert mcp_config["mcpServers"]["filesystem"]["command"] == "npx"

    def test_generate_v21_with_mcp_nested(self, adapter, tmp_path):
        """Test v2.1 generation with nested MCP servers (deprecated)."""
        from promptrek.core.models import PluginConfig

        prompt = UniversalPromptV2(
            schema_version="2.1.0",
            metadata=PromptMetadata(
                title="Test V2.1",
                description="Test v2.1 with plugins",
                version="1.0.0",
            ),
            content="# Test V2.1\n\nContent.",
            plugins=PluginConfig(
                mcp_servers=[
                    {
                        "name": "test-server",
                        "command": "node",
                        "args": ["server.js"],
                    }
                ]
            ),
        )

        files = adapter.generate(prompt, tmp_path, dry_run=False, verbose=False)

        assert len(files) == 2
        mcp_file = tmp_path / ".vscode" / "mcp.json"
        assert mcp_file.exists()

        mcp_config = json.loads(mcp_file.read_text())
        assert "test-server" in mcp_config["mcpServers"]

    def test_variable_substitution_in_mcp(self, adapter, tmp_path):
        """Test variable substitution in MCP servers."""
        prompt = UniversalPromptV3(
            schema_version="3.0.0",
            metadata=PromptMetadata(
                title="Test Variables",
                description="Test",
                version="1.0.0",
            ),
            content="# Test",
            mcp_servers=[
                {
                    "name": "api-server",
                    "command": "npx",
                    "env": {
                        "API_KEY": "{{{ API_KEY }}}",
                        "API_URL": "{{{ API_URL }}}",
                    },
                }
            ],
            variables={"API_KEY": "test-key-123", "API_URL": "https://api.test.com"},
        )

        variables = {"API_KEY": "test-key-123", "API_URL": "https://api.test.com"}
        files = adapter.generate(
            prompt, tmp_path, dry_run=False, verbose=False, variables=variables
        )

        mcp_file = tmp_path / ".vscode" / "mcp.json"
        mcp_config = json.loads(mcp_file.read_text())

        env = mcp_config["mcpServers"]["api-server"]["env"]
        assert env["API_KEY"] == "test-key-123"
        assert env["API_URL"] == "https://api.test.com"

    def test_validate_v3(self, adapter):
        """Test validation for v3 prompt."""
        # Valid v3 prompt
        valid_prompt = UniversalPromptV3(
            schema_version="3.0.0",
            metadata=PromptMetadata(title="Test", description="Test", version="1.0.0"),
            content="# Test content",
        )
        errors = adapter.validate(valid_prompt)
        assert len(errors) == 0

        # Test with whitespace-only content (bypasses pydantic validator but fails adapter validator)
        invalid_prompt = UniversalPromptV3.model_construct(
            schema_version="3.0.0",
            metadata=PromptMetadata(title="Test", description="Test", version="1.0.0"),
            content="   ",  # Whitespace only
        )
        errors = adapter.validate(invalid_prompt)
        assert len(errors) == 1
        assert errors[0].field == "content"

    def test_dry_run_with_mcp(self, adapter, tmp_path):
        """Test dry run mode with MCP servers."""
        prompt = UniversalPromptV3(
            schema_version="3.0.0",
            metadata=PromptMetadata(
                title="Test Dry Run",
                description="Test",
                version="1.0.0",
            ),
            content="# Test",
            mcp_servers=[{"name": "test", "command": "node"}],
        )

        files = adapter.generate(prompt, tmp_path, dry_run=True, verbose=True)

        # Files should not be created in dry run
        instructions_file = tmp_path / ".github" / "copilot-instructions.md"
        mcp_file = tmp_path / ".vscode" / "mcp.json"

        # In dry run, files are returned but not created
        assert not instructions_file.exists()
        assert not mcp_file.exists()

    def test_get_mcp_config_strategy(self, adapter):
        """Test MCP configuration strategy."""
        strategy = adapter.get_mcp_config_strategy()

        assert strategy["supports_project"] is True
        assert strategy["project_path"] == ".vscode/mcp.json"
        assert strategy["system_path"] is None
        assert strategy["config_format"] == "json"

    def test_generate_v2_with_headless(self, adapter, tmp_path):
        """Test v2 generation with headless mode."""
        prompt = UniversalPromptV2(
            schema_version="2.0.0",
            metadata=PromptMetadata(
                title="Test Headless",
                description="Test headless",
                version="1.0.0",
            ),
            content="# Test Project\n\nContent.",
        )

        files = adapter.generate(
            prompt, tmp_path, dry_run=False, verbose=False, headless=True
        )

        assert len(files) == 1
        instructions_file = tmp_path / ".github" / "copilot-instructions.md"
        assert instructions_file.exists()
        content = instructions_file.read_text()
        assert "HEADLESS INSTRUCTIONS START" in content
        assert "promptrek generate" in content
