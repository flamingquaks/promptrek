"""Tests for the agents CLI command."""

from pathlib import Path
from unittest.mock import Mock

import pytest

from promptrek.cli.commands.agents import _build_agents_content, agents_command
from promptrek.core.exceptions import CLIError
from promptrek.core.models import (
    Instructions,
    ProjectContext,
    PromptMetadata,
    UniversalPrompt,
)


class TestAgentsCommand:
    """Test suite for agents command."""

    def test_agents_command_with_explicit_file(self, tmp_path):
        """Test agents command with explicitly specified prompt file."""
        # Create a sample prompt file
        prompt_file = tmp_path / "test.promptrek.yaml"
        prompt_file.write_text(
            """
schema_version: "1.0.0"
metadata:
  title: "Test Project"
  description: "A test project"
  version: "1.0.0"
  author: "test@example.com"
  created: "2024-01-01"
  updated: "2024-01-01"
targets: ["copilot"]
"""
        )

        # Mock context
        ctx = Mock()
        ctx.obj = {"verbose": False}

        # Run command
        agents_command(ctx, prompt_file, tmp_path, dry_run=False, force=False)

        # Check that files were created
        assert (tmp_path / "AGENTS.md").exists()
        assert (tmp_path / ".github" / "copilot-instructions.md").exists()
        assert (tmp_path / ".claude" / "context.md").exists()

    def test_agents_command_auto_discovery(self, tmp_path):
        """Test agents command with auto-discovery of prompt file."""
        # Create a .promptrek.yaml file in the temp directory
        prompt_file = tmp_path / "project.promptrek.yaml"
        prompt_file.write_text(
            """
schema_version: "1.0.0"
metadata:
  title: "Auto Project"
  description: "Auto-discovered project"
  version: "1.0.0"
  author: "test@example.com"
  created: "2024-01-01"
  updated: "2024-01-01"
targets: ["copilot"]
"""
        )

        # Mock context and change to tmp_path
        ctx = Mock()
        ctx.obj = {"verbose": False}

        import os

        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)
            agents_command(ctx, None, tmp_path, dry_run=False, force=False)
        finally:
            os.chdir(original_cwd)

        # Check that files were created
        assert (tmp_path / "AGENTS.md").exists()

    def test_agents_command_no_prompt_file_error(self, tmp_path):
        """Test agents command raises error when no prompt file found."""
        ctx = Mock()
        ctx.obj = {"verbose": False}

        import os

        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)
            with pytest.raises(CLIError, match="No prompt file specified"):
                agents_command(ctx, None, tmp_path, dry_run=False, force=False)
        finally:
            os.chdir(original_cwd)

    def test_agents_command_dry_run(self, tmp_path):
        """Test agents command in dry run mode."""
        # Create a sample prompt file
        prompt_file = tmp_path / "test.promptrek.yaml"
        prompt_file.write_text(
            """
schema_version: "1.0.0"
metadata:
  title: "Test Project"
  description: "A test project"
  version: "1.0.0"
  author: "test@example.com"
  created: "2024-01-01"
  updated: "2024-01-01"
targets: ["copilot"]
"""
        )

        # Mock context
        ctx = Mock()
        ctx.obj = {"verbose": False}

        # Run command in dry run mode
        agents_command(ctx, prompt_file, tmp_path, dry_run=True, force=False)

        # Check that no files were actually created
        assert not (tmp_path / "AGENTS.md").exists()
        assert not (tmp_path / ".github" / "copilot-instructions.md").exists()
        assert not (tmp_path / ".claude" / "context.md").exists()

    def test_agents_command_force_overwrite(self, tmp_path):
        """Test agents command with force flag overwrites existing files."""
        # Create a sample prompt file
        prompt_file = tmp_path / "test.promptrek.yaml"
        prompt_file.write_text(
            """
schema_version: "1.0.0"
metadata:
  title: "Test Project"
  description: "A test project"
  version: "1.0.0"
  author: "test@example.com"
  created: "2024-01-01"
  updated: "2024-01-01"
targets: ["copilot"]
"""
        )

        # Create existing file
        agents_file = tmp_path / "AGENTS.md"
        agents_file.write_text("Old content")

        # Mock context
        ctx = Mock()
        ctx.obj = {"verbose": False}

        # Run command with force
        agents_command(ctx, prompt_file, tmp_path, dry_run=False, force=True)

        # Check that file was overwritten
        assert agents_file.exists()
        content = agents_file.read_text()
        assert "Old content" not in content
        assert "Test Project - Agent Instructions" in content


class TestBuildAgentsContent:
    """Test suite for _build_agents_content function."""

    def test_build_agents_content_basic(self):
        """Test building basic agents content."""
        prompt = UniversalPrompt(
            schema_version="1.0.0",
            metadata=PromptMetadata(
                title="Test Project",
                description="A test project for agents",
                version="1.0.0",
                author="test@example.com",
                created="2024-01-01",
                updated="2024-01-01",
            ),
            targets=["copilot"],
        )

        content = _build_agents_content(prompt)

        assert "Test Project - Agent Instructions" in content
        assert "A test project for agents" in content
        assert "PrompTrek" in content
        assert "promptrek generate --all" in content

    def test_build_agents_content_with_context(self):
        """Test building agents content with project context."""
        prompt = UniversalPrompt(
            schema_version="1.0.0",
            metadata=PromptMetadata(
                title="Test Project",
                description="A test project",
                version="1.0.0",
                author="test@example.com",
                created="2024-01-01",
                updated="2024-01-01",
            ),
            targets=["copilot"],
            context=ProjectContext(
                project_type="web_application",
                technologies=["python", "flask"],
                description="A Flask web application",
            ),
        )

        content = _build_agents_content(prompt)

        assert "Project Type:** web_application" in content
        assert "Technologies:** python, flask" in content
        assert "A Flask web application" in content

    def test_build_agents_content_with_instructions(self):
        """Test building agents content with instructions."""
        prompt = UniversalPrompt(
            schema_version="1.0.0",
            metadata=PromptMetadata(
                title="Test Project",
                description="A test project",
                version="1.0.0",
                author="test@example.com",
                created="2024-01-01",
                updated="2024-01-01",
            ),
            targets=["copilot"],
            instructions=Instructions(
                general=[
                    "Follow PEP 8",
                    "Use type hints",
                    "Write tests",
                    "Document functions",
                    "Use descriptive names",
                    "Handle errors gracefully",
                ]
            ),
        )

        content = _build_agents_content(prompt)

        assert "General Instructions" in content
        assert "Follow PEP 8" in content
        assert "Use type hints" in content
        # Should limit to first 5 and show count
        assert "1 more (see generated files)" in content

    def test_build_agents_content_few_instructions(self):
        """Test building agents content with few instructions (no truncation)."""
        prompt = UniversalPrompt(
            schema_version="1.0.0",
            metadata=PromptMetadata(
                title="Test Project",
                description="A test project",
                version="1.0.0",
                author="test@example.com",
                created="2024-01-01",
                updated="2024-01-01",
            ),
            targets=["copilot"],
            instructions=Instructions(general=["Follow PEP 8", "Use type hints"]),
        )

        content = _build_agents_content(prompt)

        assert "General Instructions" in content
        assert "Follow PEP 8" in content
        assert "Use type hints" in content
        # Should not show truncation message
        assert "more (see generated files)" not in content
