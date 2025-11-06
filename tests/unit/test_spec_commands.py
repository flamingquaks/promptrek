"""Tests for spec command generation and injection."""

from pathlib import Path

import pytest

from promptrek.cli.commands.generate import _inject_spec_commands
from promptrek.commands.spec_commands import get_spec_commands
from promptrek.core.models import (
    Command,
    Instructions,
    PluginConfig,
    PromptMetadata,
    UniversalPrompt,
    UniversalPromptV2,
    UniversalPromptV3,
)


class TestGetSpecCommands:
    """Tests for get_spec_commands function."""

    def test_get_spec_commands_returns_list(self):
        """Test that get_spec_commands returns a list."""
        commands = get_spec_commands()

        assert isinstance(commands, list)
        assert len(commands) > 0

    def test_get_spec_commands_all_command_objects(self):
        """Test that all returned items are Command objects."""
        commands = get_spec_commands()

        for cmd in commands:
            assert isinstance(cmd, Command)

    def test_spec_command_names(self):
        """Test expected spec command names."""
        commands = get_spec_commands()
        command_names = {cmd.name for cmd in commands}

        expected_names = {
            "promptrek.spec.create",
            "promptrek.spec.plan",
            "promptrek.spec.tasks",
            "promptrek.spec.implement",
            "promptrek.spec.analyze",
        }

        assert command_names == expected_names

    def test_spec_command_structure(self):
        """Test structure of spec commands."""
        commands = get_spec_commands()

        for cmd in commands:
            # All commands should have required fields
            assert cmd.name
            assert cmd.description
            assert cmd.prompt
            assert cmd.name.startswith("promptrek.spec.")

            # Check output format
            assert hasattr(cmd, "output_format")
            assert cmd.output_format in ["markdown", "code"]

            # Check requires_approval
            assert hasattr(cmd, "requires_approval")
            assert isinstance(cmd.requires_approval, bool)

    def test_spec_create_command(self):
        """Test promptrek.spec.create command details."""
        commands = get_spec_commands()
        create_cmd = next(
            cmd for cmd in commands if cmd.name == "promptrek.spec.create"
        )

        assert create_cmd.description == "Create a new spec-driven project document"
        assert create_cmd.output_format == "markdown"
        assert create_cmd.requires_approval is False
        assert ".promptrek/specs/" in create_cmd.prompt
        assert "AI-driven naming" in create_cmd.prompt

    def test_spec_plan_command(self):
        """Test promptrek.spec.plan command details."""
        commands = get_spec_commands()
        plan_cmd = next(cmd for cmd in commands if cmd.name == "promptrek.spec.plan")

        assert "implementation plan" in plan_cmd.description.lower()
        assert plan_cmd.output_format == "markdown"
        assert "Architecture overview" in plan_cmd.prompt

    def test_spec_tasks_command(self):
        """Test promptrek.spec.tasks command details."""
        commands = get_spec_commands()
        tasks_cmd = next(cmd for cmd in commands if cmd.name == "promptrek.spec.tasks")

        assert "tasks" in tasks_cmd.description.lower()
        assert "actionable" in tasks_cmd.prompt.lower()
        assert "Task Breakdown" in tasks_cmd.prompt

    def test_spec_implement_command(self):
        """Test promptrek.spec.implement command details."""
        commands = get_spec_commands()
        impl_cmd = next(
            cmd for cmd in commands if cmd.name == "promptrek.spec.implement"
        )

        assert "implement" in impl_cmd.description.lower()
        assert impl_cmd.output_format == "code"
        assert "production-quality" in impl_cmd.prompt

    def test_spec_analyze_command(self):
        """Test promptrek.spec.analyze command details."""
        commands = get_spec_commands()
        analyze_cmd = next(
            cmd for cmd in commands if cmd.name == "promptrek.spec.analyze"
        )

        assert "analyze" in analyze_cmd.description.lower()
        assert "consistency" in analyze_cmd.prompt.lower()
        assert "completeness" in analyze_cmd.prompt.lower()


class TestInjectSpecCommandsV1:
    """Tests for injecting spec commands into V1 prompts."""

    def test_inject_v1_returns_unchanged(self, tmp_path):
        """Test that V1 prompts are not modified."""
        prompt = UniversalPrompt(
            schema_version="1.0.0",
            metadata=PromptMetadata(
                title="Test",
                description="Test",
            ),
            instructions=Instructions(),
        )

        result = _inject_spec_commands(prompt, tmp_path)

        # Should return the same prompt unchanged
        assert result is prompt
        assert result.schema_version == "1.0.0"


class TestInjectSpecCommandsV2:
    """Tests for injecting spec commands into V2 prompts."""

    def test_inject_v2_creates_plugin_config(self, tmp_path):
        """Test injecting into V2 prompt without plugins."""
        from promptrek.core.models import PromptMetadata

        prompt = UniversalPromptV2(
            schema_version="2.0.0",
            metadata=PromptMetadata(
                title="Test",
                description="Test",
            ),
            content="Test content",
        )

        result = _inject_spec_commands(prompt, tmp_path)

        assert isinstance(result, UniversalPromptV2)
        assert result.plugins is not None
        assert isinstance(result.plugins, PluginConfig)
        assert result.plugins.commands is not None
        assert len(result.plugins.commands) == 5

    def test_inject_v2_adds_to_existing_plugins(self, tmp_path):
        """Test injecting into V2 prompt with existing plugins."""
        from promptrek.core.models import PromptMetadata

        existing_cmd = Command(
            name="existing.command",
            description="Existing",
            prompt="Existing prompt",
        )

        prompt = UniversalPromptV2(
            schema_version="2.1.0",
            metadata=PromptMetadata(
                title="Test",
                description="Test",
            ),
            content="Test content",
            plugins=PluginConfig(commands=[existing_cmd]),
        )

        result = _inject_spec_commands(prompt, tmp_path)

        assert len(result.plugins.commands) == 6  # 1 existing + 5 spec commands

        # Check existing command is preserved
        names = {cmd.name for cmd in result.plugins.commands}
        assert "existing.command" in names
        assert "promptrek.spec.create" in names

    def test_inject_v2_no_duplicates(self, tmp_path):
        """Test that duplicate commands are not added."""
        from promptrek.core.models import PromptMetadata

        spec_commands = get_spec_commands()

        prompt = UniversalPromptV2(
            schema_version="2.0.0",
            metadata=PromptMetadata(
                title="Test",
                description="Test",
            ),
            content="Test content",
            plugins=PluginConfig(commands=spec_commands),
        )

        result = _inject_spec_commands(prompt, tmp_path)

        # Should still have 5 commands (no duplicates)
        assert len(result.plugins.commands) == 5

    def test_inject_v2_partial_overlap(self, tmp_path):
        """Test injecting with partial overlap of commands."""
        from promptrek.core.models import PromptMetadata

        existing_create = Command(
            name="promptrek.spec.create",
            description="Custom create",
            prompt="Custom prompt",
        )

        prompt = UniversalPromptV2(
            schema_version="2.0.0",
            metadata=PromptMetadata(
                title="Test",
                description="Test",
            ),
            content="Test content",
            plugins=PluginConfig(commands=[existing_create]),
        )

        result = _inject_spec_commands(prompt, tmp_path)

        # Should add 4 new commands (create already exists)
        assert len(result.plugins.commands) == 5

        # Existing create command should be preserved (not replaced)
        create_cmd = next(
            cmd
            for cmd in result.plugins.commands
            if cmd.name == "promptrek.spec.create"
        )
        assert create_cmd.description == "Custom create"


class TestInjectSpecCommandsV3:
    """Tests for injecting spec commands into V3 prompts."""

    def test_inject_v3_creates_commands_list(self, tmp_path):
        """Test injecting into V3 prompt without commands."""
        from promptrek.core.models import PromptMetadata

        prompt = UniversalPromptV3(
            schema_version="3.0.0",
            metadata=PromptMetadata(
                title="Test",
                description="Test",
            ),
            content="Test content",
        )

        result = _inject_spec_commands(prompt, tmp_path)

        assert isinstance(result, UniversalPromptV3)
        assert result.commands is not None
        assert len(result.commands) == 5

        # Check all spec commands are present
        names = {cmd.name for cmd in result.commands}
        assert "promptrek.spec.create" in names
        assert "promptrek.spec.plan" in names
        assert "promptrek.spec.tasks" in names
        assert "promptrek.spec.implement" in names
        assert "promptrek.spec.analyze" in names

    def test_inject_v3_adds_to_existing_commands(self, tmp_path):
        """Test injecting into V3 prompt with existing commands."""
        from promptrek.core.models import PromptMetadata

        existing_cmd = Command(
            name="existing.command",
            description="Existing",
            prompt="Existing prompt",
        )

        prompt = UniversalPromptV3(
            schema_version="3.0.0",
            metadata=PromptMetadata(
                title="Test",
                description="Test",
            ),
            content="Test content",
            commands=[existing_cmd],
        )

        result = _inject_spec_commands(prompt, tmp_path)

        assert len(result.commands) == 6  # 1 existing + 5 spec commands

        names = {cmd.name for cmd in result.commands}
        assert "existing.command" in names
        assert "promptrek.spec.create" in names

    def test_inject_v3_no_duplicates(self, tmp_path):
        """Test that duplicate commands are not added in V3."""
        from promptrek.core.models import PromptMetadata

        spec_commands = get_spec_commands()

        prompt = UniversalPromptV3(
            schema_version="3.0.0",
            metadata=PromptMetadata(
                title="Test",
                description="Test",
            ),
            content="Test content",
            commands=spec_commands,
        )

        result = _inject_spec_commands(prompt, tmp_path)

        # Should still have 5 commands (no duplicates)
        assert len(result.commands) == 5

    def test_inject_v3_partial_overlap(self, tmp_path):
        """Test injecting with partial overlap in V3."""
        from promptrek.core.models import PromptMetadata

        existing_plan = Command(
            name="promptrek.spec.plan",
            description="Custom plan",
            prompt="Custom prompt",
        )

        prompt = UniversalPromptV3(
            schema_version="3.0.0",
            metadata=PromptMetadata(
                title="Test",
                description="Test",
            ),
            content="Test content",
            commands=[existing_plan],
        )

        result = _inject_spec_commands(prompt, tmp_path)

        # Should add 4 new commands (plan already exists)
        assert len(result.commands) == 5

        # Existing plan command should be preserved
        plan_cmd = next(
            cmd for cmd in result.commands if cmd.name == "promptrek.spec.plan"
        )
        assert plan_cmd.description == "Custom plan"


class TestInjectSpecCommandsDirectory:
    """Tests for spec directory creation during injection."""

    def test_inject_creates_specs_directory(self, tmp_path):
        """Test that injection creates .promptrek/specs/ directory."""
        from promptrek.core.models import PromptMetadata

        prompt = UniversalPromptV3(
            schema_version="3.0.0",
            metadata=PromptMetadata(
                title="Test",
                description="Test",
            ),
            content="Test content",
        )

        specs_dir = tmp_path / ".promptrek" / "specs"
        assert not specs_dir.exists()

        _inject_spec_commands(prompt, tmp_path)

        assert specs_dir.exists()
        assert specs_dir.is_dir()

    def test_inject_directory_idempotent(self, tmp_path):
        """Test that directory creation is idempotent."""
        from promptrek.core.models import PromptMetadata

        prompt = UniversalPromptV3(
            schema_version="3.0.0",
            metadata=PromptMetadata(
                title="Test",
                description="Test",
            ),
            content="Test content",
        )

        # Inject twice
        _inject_spec_commands(prompt, tmp_path)
        _inject_spec_commands(prompt, tmp_path)

        specs_dir = tmp_path / ".promptrek" / "specs"
        assert specs_dir.exists()
