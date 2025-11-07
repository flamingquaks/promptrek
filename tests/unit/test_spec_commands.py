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
            "promptrek.spec.constitution",
            "promptrek.spec.specify",
            "promptrek.spec.plan",
            "promptrek.spec.tasks",
            "promptrek.spec.implement",
            "promptrek.spec.analyze",
            "promptrek.spec.history",
            "promptrek.spec.feedback",
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

    def test_spec_specify_command(self):
        """Test promptrek.spec.specify command details."""
        commands = get_spec_commands()
        specify_cmd = next(
            cmd for cmd in commands if cmd.name == "promptrek.spec.specify"
        )

        assert specify_cmd.description == "Create a structured software specification"
        assert specify_cmd.output_format == "markdown"
        assert specify_cmd.requires_approval is False
        assert "{{ topic }}" in specify_cmd.prompt
        assert specify_cmd.supports_arguments is True

    def test_spec_plan_command(self):
        """Test promptrek.spec.plan command details."""
        commands = get_spec_commands()
        plan_cmd = next(cmd for cmd in commands if cmd.name == "promptrek.spec.plan")

        assert "implementation plan" in plan_cmd.description.lower()
        assert plan_cmd.output_format == "markdown"
        assert "## Approach" in plan_cmd.prompt
        assert "{{ topic }}" in plan_cmd.prompt
        assert plan_cmd.supports_arguments is True

    def test_spec_tasks_command(self):
        """Test promptrek.spec.tasks command details."""
        commands = get_spec_commands()
        tasks_cmd = next(cmd for cmd in commands if cmd.name == "promptrek.spec.tasks")

        assert "tasks" in tasks_cmd.description.lower()
        assert "checklist" in tasks_cmd.prompt.lower()
        assert "atomic task items" in tasks_cmd.prompt
        assert "{{ topic }}" in tasks_cmd.prompt
        assert tasks_cmd.supports_arguments is True

    def test_spec_implement_command(self):
        """Test promptrek.spec.implement command details."""
        commands = get_spec_commands()
        impl_cmd = next(
            cmd for cmd in commands if cmd.name == "promptrek.spec.implement"
        )

        assert "implement" in impl_cmd.description.lower()
        assert impl_cmd.output_format == "code"
        assert "production-ready" in impl_cmd.prompt
        assert "{{ topic }}" in impl_cmd.prompt
        assert impl_cmd.supports_arguments is True

    def test_spec_analyze_command(self):
        """Test promptrek.spec.analyze command details."""
        commands = get_spec_commands()
        analyze_cmd = next(
            cmd for cmd in commands if cmd.name == "promptrek.spec.analyze"
        )

        assert "analyze" in analyze_cmd.description.lower()
        assert "consistency" in analyze_cmd.prompt.lower()
        assert "inconsistencies" in analyze_cmd.prompt.lower()
        assert "{{ topic }}" in analyze_cmd.prompt
        assert analyze_cmd.supports_arguments is True

    def test_all_spec_commands_have_argument_support(self):
        """Test that all spec commands support arguments."""
        commands = get_spec_commands()

        for cmd in commands:
            assert (
                cmd.supports_arguments is True
            ), f"{cmd.name} should support arguments"
            assert (
                cmd.argument_description is not None
            ), f"{cmd.name} should have argument description"
            assert (
                len(cmd.argument_description) > 0
            ), f"{cmd.name} argument description should not be empty"

    def test_all_spec_commands_have_topic_placeholder(self):
        """Test that all spec command prompts contain {{ topic }} placeholder."""
        commands = get_spec_commands()

        for cmd in commands:
            assert (
                "{{ topic }}" in cmd.prompt
            ), f"{cmd.name} prompt should contain '{{{{ topic }}}}' placeholder"

    def test_spec_command_with_required_argument(self):
        """Test commands that require arguments (not optional)."""
        commands = get_spec_commands()

        # These commands have required {{ topic }} argument
        required_commands = [
            "promptrek.spec.specify",
            "promptrek.spec.plan",
            "promptrek.spec.tasks",
            "promptrek.spec.implement",
            "promptrek.spec.feedback",
        ]

        for cmd_name in required_commands:
            cmd = next(c for c in commands if c.name == cmd_name)
            # Should NOT say "optional" in the prompt comments
            assert (
                "(optional)" not in cmd.prompt.lower()
            ), f"{cmd_name} should not have optional argument"

    def test_spec_command_with_optional_argument(self):
        """Test commands that have optional arguments."""
        commands = get_spec_commands()

        # These commands have optional {{ topic }} argument
        optional_commands = [
            "promptrek.spec.constitution",
            "promptrek.spec.analyze",
            "promptrek.spec.history",
        ]

        for cmd_name in optional_commands:
            cmd = next(c for c in commands if c.name == cmd_name)
            # Should say "optional" in the prompt comments
            assert (
                "(optional)" in cmd.prompt.lower()
            ), f"{cmd_name} should have optional argument indication"


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
        assert len(result.plugins.commands) == 8

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

        assert len(result.plugins.commands) == 9  # 1 existing + 8 spec commands

        # Check existing command is preserved
        names = {cmd.name for cmd in result.plugins.commands}
        assert "existing.command" in names
        assert "promptrek.spec.specify" in names

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

        # Should still have 8 commands (no duplicates)
        assert len(result.plugins.commands) == 8

    def test_inject_v2_partial_overlap(self, tmp_path):
        """Test injecting with partial overlap of commands."""
        from promptrek.core.models import PromptMetadata

        existing_specify = Command(
            name="promptrek.spec.specify",
            description="Custom specify",
            prompt="Custom prompt",
        )

        prompt = UniversalPromptV2(
            schema_version="2.0.0",
            metadata=PromptMetadata(
                title="Test",
                description="Test",
            ),
            content="Test content",
            plugins=PluginConfig(commands=[existing_specify]),
        )

        result = _inject_spec_commands(prompt, tmp_path)

        # Should add 7 new commands (specify already exists)
        assert len(result.plugins.commands) == 8

        # Existing specify command should be preserved (not replaced)
        specify_cmd = next(
            cmd
            for cmd in result.plugins.commands
            if cmd.name == "promptrek.spec.specify"
        )
        assert specify_cmd.description == "Custom specify"


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
        assert len(result.commands) == 8

        # Check all spec commands are present
        names = {cmd.name for cmd in result.commands}
        assert "promptrek.spec.constitution" in names
        assert "promptrek.spec.specify" in names
        assert "promptrek.spec.plan" in names
        assert "promptrek.spec.tasks" in names
        assert "promptrek.spec.implement" in names
        assert "promptrek.spec.analyze" in names
        assert "promptrek.spec.history" in names
        assert "promptrek.spec.feedback" in names

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

        assert len(result.commands) == 9  # 1 existing + 8 spec commands

        names = {cmd.name for cmd in result.commands}
        assert "existing.command" in names
        assert "promptrek.spec.specify" in names

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

        # Should still have 8 commands (no duplicates)
        assert len(result.commands) == 8

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

        # Should add 7 new commands (plan already exists)
        assert len(result.commands) == 8

        # Existing plan command should be preserved
        plan_cmd = next(
            cmd for cmd in result.commands if cmd.name == "promptrek.spec.plan"
        )
        assert plan_cmd.description == "Custom plan"


class TestInjectSpecCommandsDirectory:
    """Tests for spec directory creation during injection."""

    def test_inject_creates_specs_directory(self, tmp_path):
        """Test that injection creates promptrek/specs/ directory."""
        from promptrek.core.models import PromptMetadata

        prompt = UniversalPromptV3(
            schema_version="3.0.0",
            metadata=PromptMetadata(
                title="Test",
                description="Test",
            ),
            content="Test content",
        )

        specs_dir = tmp_path / "promptrek" / "specs"
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

        specs_dir = tmp_path / "promptrek" / "specs"
        assert specs_dir.exists()
