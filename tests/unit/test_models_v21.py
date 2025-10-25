"""
Unit tests for v2.1.0 plugin models.

Tests for TrustMetadata, MCPServer, Command, Agent, Hook, and PluginConfig models.
"""

import pytest
from pydantic import ValidationError

from promptrek.core.models import (
    Agent,
    Command,
    Hook,
    MCPServer,
    PluginConfig,
    PromptMetadata,
    TrustMetadata,
    UniversalPromptV2,
    UniversalPromptV3,
)


class TestTrustMetadata:
    """Tests for TrustMetadata model."""

    def test_trust_metadata_defaults(self) -> None:
        """Test TrustMetadata default values."""
        trust = TrustMetadata()
        assert trust.trusted is False
        assert trust.trust_level is None
        assert trust.requires_approval is True
        assert trust.source is None
        assert trust.verified_by is None

    def test_trust_metadata_full(self) -> None:
        """Test TrustMetadata with all fields."""
        trust = TrustMetadata(
            trusted=True,
            trust_level="full",
            requires_approval=False,
            source="official",
            verified_by="PrompTrek Team",
            verified_date="2025-01-15",
        )
        assert trust.trusted is True
        assert trust.trust_level == "full"
        assert trust.requires_approval is False
        assert trust.source == "official"
        assert trust.verified_by == "PrompTrek Team"
        assert trust.verified_date == "2025-01-15"

    def test_trust_level_validation(self) -> None:
        """Test trust level validation."""
        # Valid trust levels
        for level in ["full", "partial", "untrusted"]:
            trust = TrustMetadata(trust_level=level)
            assert trust.trust_level == level

        # Invalid trust level
        with pytest.raises(ValidationError) as exc_info:
            TrustMetadata(trust_level="invalid")
        assert "Trust level must be" in str(exc_info.value)


class TestMCPServer:
    """Tests for MCPServer model."""

    def test_mcp_server_minimal(self) -> None:
        """Test MCPServer with minimal fields."""
        server = MCPServer(name="test-server", command="npx")
        assert server.name == "test-server"
        assert server.command == "npx"
        assert server.args is None
        assert server.env is None

    def test_mcp_server_with_args(self) -> None:
        """Test MCPServer with arguments."""
        server = MCPServer(
            name="filesystem",
            command="npx",
            args=["-y", "@modelcontextprotocol/server-filesystem", "/path/to/files"],
        )
        assert server.name == "filesystem"
        assert len(server.args) == 3
        assert server.args[0] == "-y"

    def test_mcp_server_with_env(self) -> None:
        """Test MCPServer with environment variables."""
        server = MCPServer(
            name="github",
            command="npx",
            env={"GITHUB_TOKEN": "secret123", "GITHUB_OWNER": "promptrek"},
        )
        assert server.env["GITHUB_TOKEN"] == "secret123"
        assert server.env["GITHUB_OWNER"] == "promptrek"

    def test_mcp_server_with_trust_metadata(self) -> None:
        """Test MCPServer with trust metadata."""
        trust = TrustMetadata(trusted=True, trust_level="full")
        server = MCPServer(name="trusted-server", command="node", trust_metadata=trust)
        assert server.trust_metadata is not None
        assert server.trust_metadata.trusted is True


class TestCommand:
    """Tests for Command model."""

    def test_command_minimal(self) -> None:
        """Test Command with minimal fields."""
        cmd = Command(
            name="test-command", description="Test command", prompt="Do something"
        )
        assert cmd.name == "test-command"
        assert cmd.description == "Test command"
        assert cmd.prompt == "Do something"
        assert cmd.requires_approval is False

    def test_command_full(self) -> None:
        """Test Command with all fields."""
        cmd = Command(
            name="review-pr",
            description="Review pull request",
            prompt="Review the PR for code quality",
            output_format="markdown",
            requires_approval=True,
            examples=["review-pr --pr=123", "review-pr --detailed"],
        )
        assert cmd.name == "review-pr"
        assert cmd.output_format == "markdown"
        assert cmd.requires_approval is True
        assert len(cmd.examples) == 2


class TestAgent:
    """Tests for Agent model."""

    def test_agent_minimal(self) -> None:
        """Test Agent with minimal fields."""
        agent = Agent(
            name="test-agent",
            description="Test agent",
            system_prompt="You are a test agent",
        )
        assert agent.name == "test-agent"
        assert agent.trust_level == "untrusted"
        assert agent.requires_approval is True

    def test_agent_with_tools(self) -> None:
        """Test Agent with tools."""
        agent = Agent(
            name="code-agent",
            description="Code assistant",
            system_prompt="You help with code",
            tools=["file_read", "file_write", "git_diff"],
            trust_level="partial",
            requires_approval=False,
        )
        assert len(agent.tools) == 3
        assert "file_read" in agent.tools
        assert agent.trust_level == "partial"

    def test_agent_trust_level_validation(self) -> None:
        """Test Agent trust level validation."""
        # Valid trust levels
        for level in ["full", "partial", "untrusted"]:
            agent = Agent(
                name="agent",
                description="test",
                system_prompt="test",
                trust_level=level,
            )
            assert agent.trust_level == level

        # Invalid trust level
        with pytest.raises(ValidationError) as exc_info:
            Agent(
                name="agent",
                description="test",
                system_prompt="test",
                trust_level="invalid",
            )
        assert "Trust level must be" in str(exc_info.value)


class TestHook:
    """Tests for Hook model."""

    def test_hook_minimal(self) -> None:
        """Test Hook with minimal fields."""
        hook = Hook(name="pre-commit", event="pre-commit", command="npm test")
        assert hook.name == "pre-commit"
        assert hook.event == "pre-commit"
        assert hook.command == "npm test"
        assert hook.requires_reapproval is True

    def test_hook_with_conditions(self) -> None:
        """Test Hook with conditions."""
        hook = Hook(
            name="post-save",
            event="post-save",
            command="promptrek generate --all",
            conditions={"file_pattern": "*.promptrek.yaml"},
            requires_reapproval=False,
        )
        assert hook.conditions is not None
        assert hook.conditions["file_pattern"] == "*.promptrek.yaml"
        assert hook.requires_reapproval is False


class TestPluginConfig:
    """Tests for PluginConfig model."""

    def test_plugin_config_empty(self) -> None:
        """Test PluginConfig with no plugins."""
        config = PluginConfig()
        assert config.mcp_servers is None
        assert config.commands is None
        assert config.agents is None
        assert config.hooks is None

    def test_plugin_config_with_mcp_servers(self) -> None:
        """Test PluginConfig with MCP servers."""
        servers = [
            MCPServer(name="server1", command="npx"),
            MCPServer(name="server2", command="node"),
        ]
        config = PluginConfig(mcp_servers=servers)
        assert len(config.mcp_servers) == 2
        assert config.mcp_servers[0].name == "server1"

    def test_plugin_config_full(self) -> None:
        """Test PluginConfig with all plugin types."""
        config = PluginConfig(
            mcp_servers=[MCPServer(name="server", command="npx")],
            commands=[Command(name="cmd", description="test", prompt="do something")],
            agents=[
                Agent(name="agent", description="test", system_prompt="test prompt")
            ],
            hooks=[Hook(name="hook", event="pre-commit", command="test")],
        )
        assert len(config.mcp_servers) == 1
        assert len(config.commands) == 1
        assert len(config.agents) == 1
        assert len(config.hooks) == 1


class TestUniversalPromptV2WithPlugins:
    """Tests for UniversalPromptV2 with v2.1.0 plugins field."""

    def test_v21_prompt_without_plugins(self) -> None:
        """Test v2.1.0 prompt without plugins (backward compatible)."""
        prompt = UniversalPromptV2(
            schema_version="2.1.0",
            metadata=PromptMetadata(title="Test", description="Test prompt"),
            content="# Test content",
        )
        assert prompt.schema_version == "2.1.0"
        assert prompt.plugins is None

    def test_v21_prompt_with_plugins(self) -> None:
        """Test v2.1.0 prompt with plugins."""
        plugins = PluginConfig(
            mcp_servers=[MCPServer(name="test", command="npx")],
            commands=[
                Command(name="test-cmd", description="test", prompt="do something")
            ],
        )
        prompt = UniversalPromptV2(
            schema_version="2.1.0",
            metadata=PromptMetadata(title="Test", description="Test"),
            content="# Test",
            plugins=plugins,
        )
        assert prompt.plugins is not None
        assert len(prompt.plugins.mcp_servers) == 1
        assert len(prompt.plugins.commands) == 1

    def test_v20_prompt_still_works(self) -> None:
        """Test that v2.0.0 prompts still work (backward compatibility)."""
        prompt = UniversalPromptV2(
            schema_version="2.0.0",
            metadata=PromptMetadata(title="Test", description="Test"),
            content="# Test",
        )
        assert prompt.schema_version == "2.0.0"
        assert prompt.plugins is None

    def test_v21_schema_validation(self) -> None:
        """Test v2.1.0 schema version validation."""
        # Valid v2.1.x versions
        for version in ["2.1.0", "2.1.1", "2.1.99"]:
            prompt = UniversalPromptV2(
                schema_version=version,
                metadata=PromptMetadata(title="Test", description="Test"),
                content="# Test",
            )
            assert prompt.schema_version == version

        # Invalid version (not 2.x.x)
        with pytest.raises(ValidationError) as exc_info:
            UniversalPromptV2(
                schema_version="3.0.0",
                metadata=PromptMetadata(title="Test", description="Test"),
                content="# Test",
            )
        assert "UniversalPromptV2 requires schema version 2.x.x" in str(exc_info.value)

    def test_v21_schema_version_format_validation(self) -> None:
        """Test schema version format validation."""
        # Invalid format (not x.y.z)
        with pytest.raises(ValidationError) as exc_info:
            UniversalPromptV2(
                schema_version="2.1",
                metadata=PromptMetadata(title="Test", description="Test"),
                content="# Test",
            )
        assert "Schema version must be in format 'x.y.z'" in str(exc_info.value)

    def test_v21_empty_content_validation(self) -> None:
        """Test empty content validation."""
        # Empty content
        with pytest.raises(ValidationError) as exc_info:
            UniversalPromptV2(
                schema_version="2.1.0",
                metadata=PromptMetadata(title="Test", description="Test"),
                content="",
            )
        assert "Content cannot be empty" in str(exc_info.value)

        # Whitespace-only content
        with pytest.raises(ValidationError) as exc_info:
            UniversalPromptV2(
                schema_version="2.1.0",
                metadata=PromptMetadata(title="Test", description="Test"),
                content="   \n  \t  ",
            )
        assert "Content cannot be empty" in str(exc_info.value)


class TestUniversalPromptV3:
    """Tests for UniversalPromptV3 with top-level plugin fields."""

    def test_v3_prompt_minimal(self) -> None:
        """Test v3.0.0 prompt with minimal fields."""
        prompt = UniversalPromptV3(
            schema_version="3.0.0",
            metadata=PromptMetadata(title="Test", description="Test prompt"),
            content="# Test content",
        )
        assert prompt.schema_version == "3.0.0"
        assert prompt.mcp_servers is None
        assert prompt.commands is None
        assert prompt.agents is None
        assert prompt.hooks is None

    def test_v3_prompt_with_top_level_plugins(self) -> None:
        """Test v3.0.0 prompt with top-level plugin fields."""
        prompt = UniversalPromptV3(
            schema_version="3.0.0",
            metadata=PromptMetadata(title="Test", description="Test"),
            content="# Test",
            mcp_servers=[MCPServer(name="test", command="npx")],
            commands=[
                Command(name="test-cmd", description="test", prompt="do something")
            ],
            agents=[
                Agent(name="agent", description="test", system_prompt="test prompt")
            ],
            hooks=[Hook(name="hook", event="pre-commit", command="test")],
        )
        assert prompt.mcp_servers is not None
        assert len(prompt.mcp_servers) == 1
        assert len(prompt.commands) == 1
        assert len(prompt.agents) == 1
        assert len(prompt.hooks) == 1

    def test_v3_schema_validation(self) -> None:
        """Test v3.0.0 schema version validation."""
        # Valid v3.x.x versions
        for version in ["3.0.0", "3.0.1", "3.1.0"]:
            prompt = UniversalPromptV3(
                schema_version=version,
                metadata=PromptMetadata(title="Test", description="Test"),
                content="# Test",
            )
            assert prompt.schema_version == version

        # Invalid version (not 3.x.x)
        with pytest.raises(ValidationError) as exc_info:
            UniversalPromptV3(
                schema_version="2.1.0",
                metadata=PromptMetadata(title="Test", description="Test"),
                content="# Test",
            )
        assert "UniversalPromptV3 requires schema version 3.x.x" in str(exc_info.value)

    def test_v3_schema_version_format_validation(self) -> None:
        """Test schema version format validation."""
        # Invalid format (not x.y.z)
        with pytest.raises(ValidationError) as exc_info:
            UniversalPromptV3(
                schema_version="3.0",
                metadata=PromptMetadata(title="Test", description="Test"),
                content="# Test",
            )
        assert "Schema version must be in format 'x.y.z'" in str(exc_info.value)

    def test_v3_empty_content_validation(self) -> None:
        """Test empty content validation."""
        # Empty content
        with pytest.raises(ValidationError) as exc_info:
            UniversalPromptV3(
                schema_version="3.0.0",
                metadata=PromptMetadata(title="Test", description="Test"),
                content="",
            )
        assert "Content cannot be empty" in str(exc_info.value)

        # Whitespace-only content
        with pytest.raises(ValidationError) as exc_info:
            UniversalPromptV3(
                schema_version="3.0.0",
                metadata=PromptMetadata(title="Test", description="Test"),
                content="   \n  \t  ",
            )
        assert "Content cannot be empty" in str(exc_info.value)
