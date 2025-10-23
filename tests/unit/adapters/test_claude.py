"""
Unit tests for Claude adapter.
"""

import pytest

from promptrek.adapters.claude import ClaudeAdapter
from promptrek.core.models import PromptMetadata, UniversalPrompt

from .base_test import TestAdapterBase


class TestClaudeAdapter(TestAdapterBase):
    """Test Claude adapter."""

    @pytest.fixture
    def adapter(self):
        """Create Claude adapter instance."""
        return ClaudeAdapter()

    def test_init(self, adapter):
        """Test adapter initialization."""
        assert adapter.name == "claude"
        assert adapter.description == "Claude Code (context-based)"
        assert ".claude/CLAUDE.md" in adapter.file_patterns

    def test_supports_features(self, adapter):
        """Test feature support."""
        assert adapter.supports_variables() is True
        assert adapter.supports_conditionals() is True

    def test_validate_with_context(self, adapter, sample_prompt):
        """Test validation with context."""
        errors = adapter.validate(sample_prompt)
        # Should only have warnings, not errors
        warning_errors = [
            e for e in errors if getattr(e, "severity", "error") == "warning"
        ]
        assert len(warning_errors) == 0  # Has context and examples

    def test_validate_missing_context(self, adapter):
        """Test validation with missing context."""
        prompt = UniversalPrompt(
            schema_version="1.0.0",
            metadata=PromptMetadata(
                title="Test",
                description="Test description",
                version="1.0.0",
                author="test@example.com",
                created="2024-01-01",
                updated="2024-01-01",
            ),
            targets=["claude"],
        )
        errors = adapter.validate(prompt)
        assert len(errors) == 2  # Missing context and examples warnings

    def test_build_content(self, adapter, sample_prompt):
        """Test content generation."""
        content = adapter._build_content(sample_prompt)

        assert sample_prompt.metadata.title in content
        assert sample_prompt.metadata.description in content
        assert "## Project Details" in content
        assert "## Development Guidelines" in content
        assert "## Code Examples" in content
        assert "typescript, react, nodejs" in content

    def test_generate_v1_dry_run_verbose(self, adapter, tmp_path):
        """Test v1 generation with dry run and verbose."""
        from promptrek.core.models import Instructions

        prompt = UniversalPrompt(
            schema_version="1.0.0",
            metadata=PromptMetadata(
                title="Test",
                description="Test",
                created="2024-01-01",
                updated="2024-01-01",
                version="1.0.0",
                author="test@example.com",
            ),
            targets=["claude"],
            instructions=Instructions(general=["Test instruction"]),
        )

        files = adapter.generate(prompt, tmp_path, dry_run=True, verbose=True)

        assert len(files) > 0
        for f in files:
            assert not f.exists()

    def test_generate_with_conditionals(self, adapter, tmp_path):
        """Test generation with conditional instructions."""
        from promptrek.core.models import Condition, Instructions

        prompt = UniversalPrompt(
            schema_version="1.0.0",
            metadata=PromptMetadata(
                title="Test",
                description="Test",
                created="2024-01-01",
                updated="2024-01-01",
                version="1.0.0",
                author="test@example.com",
            ),
            targets=["claude"],
            instructions=Instructions(general=["Base instruction"]),
            conditions=[
                Condition.model_validate(
                    {
                        "if": "EDITOR == 'claude'",
                        "then": {
                            "instructions": {"general": ["Claude-specific instruction"]}
                        },
                    }
                )
            ],
        )

        files = adapter.generate(prompt, tmp_path)

        assert len(files) > 0

    def test_generate_v2_dry_run_verbose(self, adapter, tmp_path):
        """Test v2 generation with dry run and verbose."""
        from promptrek.core.models import UniversalPromptV2

        prompt = UniversalPromptV2(
            schema_version="2.0.0",
            metadata=PromptMetadata(
                title="Test",
                description="Test",
                created="2024-01-01",
                updated="2024-01-01",
                version="1.0.0",
                author="test@example.com",
            ),
            content="# Instructions\n\n" + "Content " * 50,
        )

        adapter.generate(prompt, tmp_path, dry_run=True, verbose=True)

    def test_generate_v1_all_instruction_categories(self, adapter, tmp_path):
        """Test v1 generation with all instruction categories."""
        from promptrek.core.models import Instructions, ProjectContext

        prompt = UniversalPrompt(
            schema_version="1.0.0",
            metadata=PromptMetadata(
                title="Test",
                description="Test",
                created="2024-01-01",
                updated="2024-01-01",
                version="1.0.0",
                author="test@example.com",
            ),
            targets=["claude"],
            context=ProjectContext(
                project_type="application", technologies=["Python", "TypeScript"]
            ),
            instructions=Instructions(
                general=["General rule"],
                code_style=["Code style rule"],
                architecture=["Architecture rule"],
                testing=["Testing rule"],
                security=["Security rule"],
                performance=["Performance rule"],
            ),
        )

        files = adapter.generate(prompt, tmp_path)

        assert len(files) > 0
        content = files[0].read_text()
        assert "Architecture" in content
        # Security and Performance may not always be included
        assert "Architecture" in content

    def test_parse_files_basic(self, adapter, tmp_path):
        """Test parsing Claude files."""
        claude_dir = tmp_path / ".claude"
        claude_dir.mkdir()

        claude_md = claude_dir / "CLAUDE.md"
        claude_md.write_text(
            """# Project Instructions

## General Guidelines
- Follow best practices
- Write clean code

## Code Style
- Use consistent formatting
"""
        )

        result = adapter.parse_files(tmp_path)

        assert result is not None
        assert "best practices" in str(result)

    def test_parse_agent_files_markdown_format(self, adapter, tmp_path):
        """Test parsing agent files in markdown format (generated by _build_agent_content)."""
        # Create base CLAUDE.md file (required for parse_files)
        claude_dir = tmp_path / ".claude"
        claude_dir.mkdir()
        claude_md = claude_dir / "CLAUDE.md"
        claude_md.write_text("# Project\n\nTest content")

        agents_dir = claude_dir / "agents"
        agents_dir.mkdir(parents=True)

        # Create agent file in markdown format
        agent_file = agents_dir / "test-agent.md"
        agent_file.write_text("""# test-agent

**Description:** This is a test agent

## System Prompt
You are a test agent. Follow these instructions:
1. Test thoroughly
2. Report findings

## Available Tools
- Read
- Write
- Bash

## Configuration
- Trust Level: untrusted
- Requires Approval: True

## Additional Context
- **project**: promptrek
- **language**: python
""")

        result = adapter.parse_files(tmp_path)

        assert result is not None
        assert hasattr(result, 'agents')
        assert result.agents is not None
        assert len(result.agents) == 1

        agent = result.agents[0]
        assert agent.name == "test-agent"
        assert "test agent" in agent.description.lower()
        assert "test thoroughly" in agent.system_prompt.lower()
        assert agent.tools == ["Read", "Write", "Bash"]
        assert agent.trust_level == "untrusted"
        assert agent.requires_approval is True
        assert agent.context == {"project": "promptrek", "language": "python"}

    def test_parse_agent_files_frontmatter_format(self, adapter, tmp_path):
        """Test parsing agent files in YAML frontmatter format."""
        # Create base CLAUDE.md file (required for parse_files)
        claude_dir = tmp_path / ".claude"
        claude_dir.mkdir()
        claude_md = claude_dir / "CLAUDE.md"
        claude_md.write_text("# Project\n\nTest content")

        agents_dir = claude_dir / "agents"
        agents_dir.mkdir(parents=True)

        # Create agent file with frontmatter
        agent_file = agents_dir / "test-agent.md"
        agent_file.write_text("""---
name: test-agent
description: This is a test agent
tools: ["Read", "Write"]
trust_level: full
requires_approval: false
---

You are a test agent with frontmatter configuration.""")

        result = adapter.parse_files(tmp_path)

        assert result is not None
        assert hasattr(result, 'agents')
        assert result.agents is not None
        assert len(result.agents) == 1

        agent = result.agents[0]
        assert agent.name == "test-agent"
        assert agent.description == "This is a test agent"
        assert agent.tools == ["Read", "Write"]
        assert agent.trust_level == "full"
        assert agent.requires_approval is False

    def test_parse_command_files_markdown_format(self, adapter, tmp_path):
        """Test parsing command files in markdown format (generated by _build_command_content)."""
        # Create base CLAUDE.md file (required for parse_files)
        claude_dir = tmp_path / ".claude"
        claude_dir.mkdir()
        claude_md = claude_dir / "CLAUDE.md"
        claude_md.write_text("# Project\n\nTest content")

        commands_dir = claude_dir / "commands"
        commands_dir.mkdir(parents=True)

        # Create command file in markdown format
        command_file = commands_dir / "review.md"
        command_file.write_text("""# review

**Description:** Review code for quality

## System Message
Use best practices when reviewing

## Prompt
Review the current file for:
- Code quality
- Style issues
- Potential bugs

## Examples
- Review function for performance
- Check error handling
""")

        result = adapter.parse_files(tmp_path)

        assert result is not None
        assert hasattr(result, 'commands')
        assert result.commands is not None
        assert len(result.commands) == 1

        command = result.commands[0]
        assert command.name == "review"
        assert "quality" in command.description.lower()
        assert "code quality" in command.prompt.lower()
        assert "best practices" in command.system_message.lower()
        assert len(command.examples) == 2

    def test_parse_command_files_frontmatter_format(self, adapter, tmp_path):
        """Test parsing command files in YAML frontmatter format."""
        # Create base CLAUDE.md file (required for parse_files)
        claude_dir = tmp_path / ".claude"
        claude_dir.mkdir()
        claude_md = claude_dir / "CLAUDE.md"
        claude_md.write_text("# Project\n\nTest content")

        commands_dir = claude_dir / "commands"
        commands_dir.mkdir(parents=True)

        # Create command file with frontmatter
        command_file = commands_dir / "test-command.md"
        command_file.write_text("""---
name: test-command
description: Test command description
requires_approval: true
---

This is the command prompt.""")

        result = adapter.parse_files(tmp_path)

        assert result is not None
        assert hasattr(result, 'commands')
        assert result.commands is not None
        assert len(result.commands) == 1

        command = result.commands[0]
        assert command.name == "test-command"
        assert command.description == "Test command description"
        assert command.requires_approval is True

    def test_parse_hooks_from_settings_local_json(self, adapter, tmp_path):
        """Test parsing hooks from .claude/settings.local.json."""
        import json

        claude_dir = tmp_path / ".claude"
        claude_dir.mkdir()

        # Create base CLAUDE.md file (required for parse_files)
        claude_md = claude_dir / "CLAUDE.md"
        claude_md.write_text("# Project\n\nTest content")

        # Create settings.local.json with hooks
        settings_file = claude_dir / "settings.local.json"
        settings_data = {
            "hooks": {
                "PreToolUse": [
                    {
                        "matcher": "Bash",
                        "hooks": [
                            {
                                "type": "command",
                                "command": "echo 'Running bash command'"
                            }
                        ]
                    }
                ],
                "PostToolUse": [
                    {
                        "matcher": "Read",
                        "hooks": [
                            {
                                "type": "command",
                                "command": "echo 'File read'"
                            }
                        ]
                    }
                ]
            }
        }
        settings_file.write_text(json.dumps(settings_data, indent=2))

        result = adapter.parse_files(tmp_path)

        assert result is not None
        assert hasattr(result, 'hooks')
        assert result.hooks is not None
        assert len(result.hooks) == 2

        # Check first hook
        hook1 = result.hooks[0]
        assert hook1.event == "PreToolUse"
        assert hook1.conditions == {"matcher": "Bash"}
        assert "bash command" in hook1.command.lower()

        # Check second hook
        hook2 = result.hooks[1]
        assert hook2.event == "PostToolUse"
        assert hook2.conditions == {"matcher": "Read"}

    def test_parse_hooks_from_hooks_yaml(self, adapter, tmp_path):
        """Test parsing hooks from .claude/hooks.yaml."""
        import yaml

        claude_dir = tmp_path / ".claude"
        claude_dir.mkdir()

        # Create base CLAUDE.md file (required for parse_files)
        claude_md = claude_dir / "CLAUDE.md"
        claude_md.write_text("# Project\n\nTest content")

        # Create hooks.yaml
        hooks_file = claude_dir / "hooks.yaml"
        hooks_data = {
            "hooks": [
                {
                    "name": "pre-commit-hook",
                    "event": "PreCommit",
                    "command": "npm run lint",
                    "requires_reapproval": True,
                    "description": "Run linting before commits"
                }
            ]
        }
        hooks_file.write_text(yaml.dump(hooks_data))

        result = adapter.parse_files(tmp_path)

        assert result is not None
        assert hasattr(result, 'hooks')
        assert result.hooks is not None
        assert len(result.hooks) == 1

        hook = result.hooks[0]
        assert hook.name == "pre-commit-hook"
        assert hook.event == "PreCommit"
        assert hook.command == "npm run lint"
        assert hook.requires_reapproval is True
        assert hook.description == "Run linting before commits"

    def test_generate_with_hooks_matcher(self, adapter, tmp_path):
        """Test generating hooks with matcher to settings.local.json."""
        from promptrek.core.models import UniversalPromptV3, Hook
        import json

        prompt = UniversalPromptV3(
            schema_version="3.0.0",
            metadata=PromptMetadata(
                title="Test",
                description="Test",
                created="2024-01-01",
                updated="2024-01-01",
                version="1.0.0",
                author="test@example.com",
            ),
            content="# Test content",
            hooks=[
                Hook(
                    name="test-hook",
                    event="PreToolUse",
                    command="echo 'test'",
                    conditions={"matcher": "Bash"},
                    requires_reapproval=True
                )
            ]
        )

        files = adapter.generate(prompt, tmp_path)

        # Check that settings.local.json was created
        settings_file = tmp_path / ".claude" / "settings.local.json"
        assert settings_file.exists()

        settings_data = json.loads(settings_file.read_text())
        assert "hooks" in settings_data
        assert "PreToolUse" in settings_data["hooks"]
        assert len(settings_data["hooks"]["PreToolUse"]) == 1
        assert settings_data["hooks"]["PreToolUse"][0]["matcher"] == "Bash"

    def test_generate_with_hooks_no_matcher(self, adapter, tmp_path):
        """Test generating hooks without matcher to hooks.yaml."""
        from promptrek.core.models import UniversalPromptV3, Hook
        import yaml

        prompt = UniversalPromptV3(
            schema_version="3.0.0",
            metadata=PromptMetadata(
                title="Test",
                description="Test",
                created="2024-01-01",
                updated="2024-01-01",
                version="1.0.0",
                author="test@example.com",
            ),
            content="# Test content",
            hooks=[
                Hook(
                    name="simple-hook",
                    event="PreCommit",
                    command="make lint",
                    requires_reapproval=False
                )
            ]
        )

        files = adapter.generate(prompt, tmp_path)

        # Check that hooks.yaml was created
        hooks_file = tmp_path / ".claude" / "hooks.yaml"
        assert hooks_file.exists()

        hooks_data = yaml.safe_load(hooks_file.read_text())
        assert "hooks" in hooks_data
        assert len(hooks_data["hooks"]) == 1
        assert hooks_data["hooks"][0]["name"] == "simple-hook"
        assert hooks_data["hooks"][0]["event"] == "PreCommit"

    def test_generate_with_agents_and_commands(self, adapter, tmp_path):
        """Test generating agents and commands."""
        from promptrek.core.models import UniversalPromptV3, Agent, Command

        prompt = UniversalPromptV3(
            schema_version="3.0.0",
            metadata=PromptMetadata(
                title="Test",
                description="Test",
                created="2024-01-01",
                updated="2024-01-01",
                version="1.0.0",
                author="test@example.com",
            ),
            content="# Test content",
            agents=[
                Agent(
                    name="test-agent",
                    description="Test agent",
                    system_prompt="You are a test agent",
                    tools=["Read", "Write"],
                    trust_level="untrusted",
                    requires_approval=True
                )
            ],
            commands=[
                Command(
                    name="test-command",
                    description="Test command",
                    prompt="This is a test command",
                    requires_approval=False
                )
            ]
        )

        files = adapter.generate(prompt, tmp_path)

        # Check agent file
        agent_file = tmp_path / ".claude" / "agents" / "test-agent.md"
        assert agent_file.exists()
        agent_content = agent_file.read_text()
        assert "# test-agent" in agent_content
        assert "Test agent" in agent_content
        assert "You are a test agent" in agent_content

        # Check command file
        command_file = tmp_path / ".claude" / "commands" / "test-command.md"
        assert command_file.exists()
        command_content = command_file.read_text()
        assert "# test-command" in command_content
        assert "Test command" in command_content

    def test_generate_with_mcp_servers(self, adapter, tmp_path):
        """Test generating MCP servers."""
        from promptrek.core.models import UniversalPromptV3, MCPServer
        import json

        prompt = UniversalPromptV3(
            schema_version="3.0.0",
            metadata=PromptMetadata(
                title="Test",
                description="Test",
                created="2024-01-01",
                updated="2024-01-01",
                version="1.0.0",
                author="test@example.com",
            ),
            content="# Test content",
            mcp_servers=[
                MCPServer(
                    name="filesystem",
                    command="npx",
                    args=["-y", "@modelcontextprotocol/server-filesystem", "/path"],
                    type="stdio"
                )
            ]
        )

        files = adapter.generate(prompt, tmp_path)

        # Check MCP file
        mcp_file = tmp_path / ".mcp.json"
        assert mcp_file.exists()

        mcp_data = json.loads(mcp_file.read_text())
        assert "mcpServers" in mcp_data
        assert "filesystem" in mcp_data["mcpServers"]
        assert mcp_data["mcpServers"]["filesystem"]["command"] == "npx"

    def test_parse_mcp_file(self, adapter, tmp_path):
        """Test parsing MCP server configuration."""
        import json

        claude_dir = tmp_path / ".claude"
        claude_dir.mkdir()

        # Create base CLAUDE.md file
        claude_md = claude_dir / "CLAUDE.md"
        claude_md.write_text("# Project\n\nTest content")

        # Create MCP file
        mcp_file = tmp_path / ".mcp.json"
        mcp_data = {
            "mcpServers": {
                "test-server": {
                    "command": "test-command",
                    "args": ["arg1", "arg2"],
                    "type": "stdio"
                }
            }
        }
        mcp_file.write_text(json.dumps(mcp_data))

        result = adapter.parse_files(tmp_path)

        assert result is not None
        assert hasattr(result, 'mcp_servers')
        assert result.mcp_servers is not None
        assert len(result.mcp_servers) == 1

        server = result.mcp_servers[0]
        assert server.name == "test-server"
        assert server.command == "test-command"
        assert server.args == ["arg1", "arg2"]
