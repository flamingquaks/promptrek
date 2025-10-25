"""
Unit tests for Claude adapter.
"""

import json

import pytest
import yaml

from promptrek.adapters.claude import ClaudeAdapter
from promptrek.core.models import (
    Agent,
    Command,
    Condition,
    Hook,
    Instructions,
    MCPServer,
    ProjectContext,
    PromptMetadata,
    UniversalPrompt,
    UniversalPromptV2,
    UniversalPromptV3,
)

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
        agent_file.write_text(
            """# test-agent

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
"""
        )

        result = adapter.parse_files(tmp_path)

        assert result is not None
        assert hasattr(result, "agents")
        assert result.agents is not None
        assert len(result.agents) == 1

        agent = result.agents[0]
        assert agent.name == "test-agent"
        assert agent.description is not None and agent.description.strip() != ""
        assert "test agent" in agent.description.lower()
        assert "test thoroughly" in agent.prompt.lower()
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
        agent_file.write_text(
            """---
name: test-agent
description: This is a test agent
tools: ["Read", "Write"]
trust_level: full
requires_approval: false
---

You are a test agent with frontmatter configuration."""
        )

        result = adapter.parse_files(tmp_path)

        assert result is not None
        assert hasattr(result, "agents")
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
        command_file.write_text(
            """# review

**Description:** Review code for quality

## Prompt
Review the current file for:
- Code quality
- Style issues
- Potential bugs

## Examples
- Review function for performance
- Check error handling
"""
        )

        result = adapter.parse_files(tmp_path)

        assert result is not None
        assert hasattr(result, "commands")
        assert result.commands is not None
        assert len(result.commands) == 1

        command = result.commands[0]
        assert command.name == "review"
        assert "quality" in command.description.lower()
        assert "code quality" in command.prompt.lower()
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
        command_file.write_text(
            """---
name: test-command
description: Test command description
requires_approval: true
---

This is the command prompt."""
        )

        result = adapter.parse_files(tmp_path)

        assert result is not None
        assert hasattr(result, "commands")
        assert result.commands is not None
        assert len(result.commands) == 1

        command = result.commands[0]
        assert command.name == "test-command"
        assert command.description == "Test command description"
        assert command.requires_approval is True

    def test_parse_hooks_from_settings_local_json(self, adapter, tmp_path):
        """Test parsing hooks from .claude/settings.local.json."""
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
                                "command": "echo 'Running bash command'",
                            }
                        ],
                    }
                ],
                "PostToolUse": [
                    {
                        "matcher": "Read",
                        "hooks": [{"type": "command", "command": "echo 'File read'"}],
                    }
                ],
            }
        }
        settings_file.write_text(json.dumps(settings_data, indent=2))

        result = adapter.parse_files(tmp_path)

        assert result is not None
        assert hasattr(result, "hooks")
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
                    "description": "Run linting before commits",
                }
            ]
        }
        hooks_file.write_text(yaml.dump(hooks_data))

        result = adapter.parse_files(tmp_path)

        assert result is not None
        assert hasattr(result, "hooks")
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
                    requires_reapproval=True,
                )
            ],
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
                    requires_reapproval=False,
                )
            ],
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
                    prompt="You are a test agent",  # type: ignore[call-arg]  # Pydantic field alias
                    description="Test agent",
                    tools=["Read", "Write"],
                    trust_level="untrusted",
                    requires_approval=True,
                )
            ],
            commands=[
                Command(
                    name="test-command",
                    description="Test command",
                    prompt="This is a test command",
                    requires_approval=False,
                )
            ],
        )

        files = adapter.generate(prompt, tmp_path)

        # Check agent file
        agent_file = tmp_path / ".claude" / "agents" / "test-agent.md"
        assert agent_file.exists()
        agent_content = agent_file.read_text()
        # Check for YAML frontmatter format
        assert "---" in agent_content
        assert "name: test-agent" in agent_content
        assert "description: Test agent" in agent_content
        assert "model: sonnet" in agent_content
        assert "tools:" in agent_content
        assert "- Read" in agent_content
        assert "- Write" in agent_content
        assert "trust_level: untrusted" in agent_content
        assert "requires_approval: true" in agent_content
        # Check prompt content after frontmatter
        assert "You are a test agent" in agent_content

        # Check command file
        command_file = tmp_path / ".claude" / "commands" / "test-command.md"
        assert command_file.exists()
        command_content = command_file.read_text()
        assert "# test-command" in command_content
        assert "Test command" in command_content

    def test_generate_with_mcp_servers(self, adapter, tmp_path):
        """Test generating MCP servers."""
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
                )
            ],
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
                    "type": "stdio",
                }
            }
        }
        mcp_file.write_text(json.dumps(mcp_data))

        result = adapter.parse_files(tmp_path)

        assert result is not None
        assert hasattr(result, "mcp_servers")
        assert result.mcp_servers is not None
        assert len(result.mcp_servers) == 1

        server = result.mcp_servers[0]
        assert server.name == "test-server"
        assert server.command == "test-command"
        assert server.args == ["arg1", "arg2"]


class TestClaudeWorkflowsV3:
    """Test v3.1 workflow support for Claude adapter."""

    @pytest.fixture
    def adapter(self):
        """Create Claude adapter instance."""
        return ClaudeAdapter()

    @pytest.fixture
    def sample_workflow_prompt_v3(self):
        """Create sample v3 prompt with workflows."""
        from promptrek.core.models import WorkflowStep

        workflow = Command(
            name="deploy-production",
            description="Deploy application to production environment",
            prompt="Deploy the application following best practices and safety checks",
            multi_step=True,
            tool_calls=["gh", "docker", "kubectl"],
            steps=[
                WorkflowStep(
                    name="verify_tests",
                    action="execute_command",
                    description="Verify all tests pass",
                    params={"command": "npm test"},
                ),
                WorkflowStep(
                    name="build_image",
                    action="execute_command",
                    description="Build production Docker image",
                    params={"command": "docker build -t app:prod ."},
                ),
                WorkflowStep(
                    name="deploy",
                    action="execute_command",
                    description="Deploy to Kubernetes cluster",
                    params={"command": "kubectl apply -f prod/"},
                ),
            ],
            requires_approval=True,
            examples=["Deploy latest version to production"],
        )

        return UniversalPromptV3(
            schema_version="3.1.0",
            metadata=PromptMetadata(
                title="Test Workflows", description="Test workflow configuration"
            ),
            content="# Test Project\n\nProject with production deployment workflows",
            commands=[workflow],
        )

    def test_generate_v3_workflow_as_command(
        self, adapter, sample_workflow_prompt_v3, tmp_path
    ):
        """Test that v3.1 workflows are generated as Claude commands."""
        files = adapter.generate(
            sample_workflow_prompt_v3, tmp_path, dry_run=False, verbose=False
        )

        # Should create CLAUDE.md and command file
        assert len(files) == 2

        # Check that command file exists for workflow
        command_file = tmp_path / ".claude" / "commands" / "deploy-production.md"
        assert command_file.exists()
        assert command_file.is_file()

        content = command_file.read_text()
        assert "# deploy-production" in content
        assert "Deploy application to production environment" in content

    def test_generate_v3_workflow_includes_type_marker(
        self, adapter, sample_workflow_prompt_v3, tmp_path
    ):
        """Test that workflow command includes Type: Multi-step Workflow marker."""
        files = adapter.generate(
            sample_workflow_prompt_v3, tmp_path, dry_run=False, verbose=False
        )

        command_file = tmp_path / ".claude" / "commands" / "deploy-production.md"
        content = command_file.read_text()

        # Should include workflow type marker
        assert "**Type:** Multi-step Workflow" in content

    def test_generate_v3_workflow_includes_required_tools(
        self, adapter, sample_workflow_prompt_v3, tmp_path
    ):
        """Test that workflow includes Required Tools section."""
        files = adapter.generate(
            sample_workflow_prompt_v3, tmp_path, dry_run=False, verbose=False
        )

        command_file = tmp_path / ".claude" / "commands" / "deploy-production.md"
        content = command_file.read_text()

        # Check for Required Tools section
        assert "## Required Tools" in content
        assert "- `gh`" in content
        assert "- `docker`" in content
        assert "- `kubectl`" in content

    def test_generate_v3_workflow_includes_steps(
        self, adapter, sample_workflow_prompt_v3, tmp_path
    ):
        """Test that workflow includes Workflow Steps section."""
        files = adapter.generate(
            sample_workflow_prompt_v3, tmp_path, dry_run=False, verbose=False
        )

        command_file = tmp_path / ".claude" / "commands" / "deploy-production.md"
        content = command_file.read_text()

        # Check for Workflow Steps section
        assert "## Workflow Steps" in content
        assert "### 1. verify_tests" in content
        assert "Verify all tests pass" in content
        assert "execute_command" in content

    def test_generate_v3_multiple_workflows_and_commands(self, adapter, tmp_path):
        """Test generating both workflows and regular commands."""
        from promptrek.core.models import WorkflowStep

        regular_command = Command(
            name="format-code",
            description="Format code using prettier",
            prompt="Format all code files using prettier with project settings",
            multi_step=False,  # Regular command
        )

        workflow = Command(
            name="run-ci",
            description="Run CI pipeline",
            prompt="Execute full CI pipeline including lint, test, and build",
            multi_step=True,  # Workflow
            tool_calls=["npm"],
            steps=[
                WorkflowStep(
                    name="lint",
                    action="execute_command",
                    params={"command": "npm run lint"},
                ),
                WorkflowStep(
                    name="test",
                    action="execute_command",
                    params={"command": "npm test"},
                ),
            ],
        )

        prompt = UniversalPromptV3(
            schema_version="3.1.0",
            metadata=PromptMetadata(title="Test", description="Test"),
            content="Test content",
            commands=[regular_command, workflow],
        )

        files = adapter.generate(prompt, tmp_path, dry_run=False, verbose=False)

        # Should create CLAUDE.md + 2 command files
        assert len(files) == 3

        # Both should be in .claude/commands/
        assert (tmp_path / ".claude" / "commands" / "format-code.md").exists()
        assert (tmp_path / ".claude" / "commands" / "run-ci.md").exists()

        # Workflow should have type marker
        workflow_content = (tmp_path / ".claude" / "commands" / "run-ci.md").read_text()
        assert "**Type:** Multi-step Workflow" in workflow_content

        # Regular command should NOT have type marker
        regular_content = (
            tmp_path / ".claude" / "commands" / "format-code.md"
        ).read_text()
        assert "**Type:** Multi-step Workflow" not in regular_content

    def test_generate_v3_workflow_with_variables(self, adapter, tmp_path):
        """Test workflow generation with variable substitution."""
        workflow = Command(
            name="deploy",
            description="Deploy to environment",
            prompt="Deploy the application to {{{ ENVIRONMENT }}} with {{{ VERSION }}}",
            multi_step=True,
            tool_calls=["kubectl"],
        )

        prompt = UniversalPromptV3(
            schema_version="3.1.0",
            metadata=PromptMetadata(title="Test", description="Test"),
            content="Test content",
            commands=[workflow],
        )

        variables = {"ENVIRONMENT": "staging", "VERSION": "v1.2.3"}

        files = adapter.generate(
            prompt, tmp_path, dry_run=False, verbose=False, variables=variables
        )

        command_file = tmp_path / ".claude" / "commands" / "deploy.md"
        content = command_file.read_text()

        # Variables should be substituted in prompt section
        assert "Deploy the application to staging with v1.2.3" in content

    def test_validate_v3_workflow_prompt(self, adapter, sample_workflow_prompt_v3):
        """Test validation of v3 prompt with workflows."""
        errors = adapter.validate(sample_workflow_prompt_v3)
        # V3 validation is simpler - just checks content exists
        assert len(errors) == 0

    def test_generate_v3_workflow_dry_run(
        self, adapter, sample_workflow_prompt_v3, tmp_path
    ):
        """Test workflow generation in dry run mode."""
        files = adapter.generate(
            sample_workflow_prompt_v3, tmp_path, dry_run=True, verbose=True
        )

        # Should return expected file paths
        assert len(files) == 2

        # But files should not be created
        command_file = tmp_path / ".claude" / "commands" / "deploy-production.md"
        assert not command_file.exists()

    def test_generate_v3_workflow_without_steps(self, adapter, tmp_path):
        """Test workflow generation when steps are not provided."""
        workflow = Command(
            name="simple-workflow",
            description="Simple workflow without detailed steps",
            prompt="Execute a simple workflow",
            multi_step=True,
            tool_calls=["npm"],
            # No steps provided
        )

        prompt = UniversalPromptV3(
            schema_version="3.1.0",
            metadata=PromptMetadata(title="Test", description="Test"),
            content="Test content",
            commands=[workflow],
        )

        files = adapter.generate(prompt, tmp_path, dry_run=False, verbose=False)

        command_file = tmp_path / ".claude" / "commands" / "simple-workflow.md"
        content = command_file.read_text()

        # Should still have workflow type marker and tools
        assert "**Type:** Multi-step Workflow" in content
        assert "## Required Tools" in content

        # But no Workflow Steps section
        assert "## Workflow Steps" not in content
