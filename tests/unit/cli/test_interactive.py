"""
Tests for interactive CLI wizard.
"""

import sys
from pathlib import Path
from unittest.mock import MagicMock, Mock, call, patch

import click
import pytest
from click.testing import CliRunner

from promptrek.cli.interactive import (
    BANNER,
    check_existing_config,
    print_banner,
    run_interactive_mode,
    show_help,
    workflow_generate_config,
    workflow_init_project,
    workflow_migrate,
    workflow_plugins,
    workflow_sync,
    workflow_validate,
)
from promptrek.cli.main import cli
from promptrek.core.exceptions import PrompTrekError


class TestInteractiveBanner:
    """Tests for banner functionality."""

    def test_banner_constant_exists(self) -> None:
        """Test that BANNER constant is defined."""
        assert BANNER is not None
        # Banner is ASCII art, so just check it's not empty
        assert len(BANNER) > 10

    def test_print_banner(self) -> None:
        """Test that print_banner outputs content."""
        # This will print to stdout, just verify it doesn't raise
        print_banner()


class TestCheckExistingConfig:
    """Tests for checking existing configuration."""

    def test_check_existing_config_not_found(self, tmp_path: Path) -> None:
        """Test when no config file exists."""
        import os

        original_dir = Path.cwd()
        try:
            os.chdir(tmp_path)
            result = check_existing_config()
            assert result is None
        finally:
            os.chdir(original_dir)

    def test_check_existing_config_found_project_yaml(self, tmp_path: Path) -> None:
        """Test when project.promptrek.yaml exists."""
        import os

        original_dir = Path.cwd()
        try:
            os.chdir(tmp_path)
            config_file = tmp_path / "project.promptrek.yaml"
            config_file.touch()
            result = check_existing_config()
            assert result is not None
            assert result.name == "project.promptrek.yaml"
        finally:
            os.chdir(original_dir)

    def test_check_existing_config_found_project_yml(self, tmp_path: Path) -> None:
        """Test when project.promptrek.yml exists."""
        import os

        original_dir = Path.cwd()
        try:
            os.chdir(tmp_path)
            config_file = tmp_path / "project.promptrek.yml"
            config_file.touch()
            result = check_existing_config()
            assert result is not None
            assert result.name == "project.promptrek.yml"
        finally:
            os.chdir(original_dir)

    def test_check_existing_config_found_dotfile(self, tmp_path: Path) -> None:
        """Test when .promptrek.yaml exists."""
        import os

        original_dir = Path.cwd()
        try:
            os.chdir(tmp_path)
            config_file = tmp_path / ".promptrek.yaml"
            config_file.touch()
            result = check_existing_config()
            assert result is not None
            assert result.name == ".promptrek.yaml"
        finally:
            os.chdir(original_dir)


class TestInteractiveMode:
    """Tests for interactive mode entry point."""

    def test_run_interactive_mode_non_tty(self, tmp_path: Path) -> None:
        """Test interactive mode in non-TTY environment (should show help)."""
        runner = CliRunner()
        result = runner.invoke(cli, [])

        # In non-TTY environment, should show help
        assert result.exit_code == 0

    def test_cli_with_interactive_flag(self) -> None:
        """Test that --interactive flag is recognized."""
        runner = CliRunner()
        # This will fail because we're not in a TTY, but it should parse the flag
        result = runner.invoke(cli, ["--interactive"])
        assert result.exit_code == 0

    def test_cli_help_mentions_interactive(self) -> None:
        """Test that help text mentions interactive mode."""
        runner = CliRunner()
        result = runner.invoke(cli, ["--help"])
        assert result.exit_code == 0
        assert "interactive" in result.output.lower()

    def test_interactive_mode_calls_function(self) -> None:
        """Test that interactive mode function is called when no subcommand."""
        # This is tested indirectly by verifying that the CLI doesn't error
        # when invoked without a subcommand
        runner = CliRunner()
        result = runner.invoke(cli, [])

        # Should show help in non-TTY environment
        assert result.exit_code == 0


class TestWorkflowHelpers:
    """Tests for workflow helper functions."""

    def test_workflows_importable(self) -> None:
        """Test that workflow functions can be imported."""
        from promptrek.cli.interactive import (
            workflow_generate_config,
            workflow_init_project,
            workflow_migrate,
            workflow_plugins,
            workflow_sync,
            workflow_validate,
        )

        # Just verify they're callable
        assert callable(workflow_init_project)
        assert callable(workflow_generate_config)
        assert callable(workflow_migrate)
        assert callable(workflow_validate)
        assert callable(workflow_sync)
        assert callable(workflow_plugins)

    @patch("promptrek.cli.interactive.questionary")
    @patch("promptrek.cli.interactive.check_existing_config")
    @patch("promptrek.cli.interactive.init_command")
    def test_workflow_init_project_success(
        self, mock_init_cmd, mock_check_config, mock_questionary
    ) -> None:
        """Test successful project initialization workflow."""
        # Setup mocks
        mock_check_config.return_value = None
        mock_questionary.select.return_value.ask.return_value = "v3"
        mock_questionary.confirm.return_value.ask.side_effect = [True, True, False]

        ctx = click.Context(click.Command("test"))
        ctx.obj = {"verbose": False}

        workflow_init_project(ctx)

        # Verify init_command was called
        mock_init_cmd.assert_called_once()
        assert mock_init_cmd.call_args[1]["output"] == "project.promptrek.yaml"

    @patch("promptrek.cli.interactive.questionary")
    @patch("promptrek.cli.interactive.check_existing_config")
    def test_workflow_init_project_existing_config_cancelled(
        self, mock_check_config, mock_questionary
    ) -> None:
        """Test init workflow when existing config is not overwritten."""
        mock_check_config.return_value = Path("project.promptrek.yaml")
        mock_questionary.confirm.return_value.ask.return_value = False

        ctx = click.Context(click.Command("test"))
        ctx.obj = {"verbose": False}

        workflow_init_project(ctx)

        # Should cancel without calling init
        mock_questionary.select.assert_not_called()

    @patch("promptrek.cli.interactive.questionary")
    @patch("promptrek.cli.interactive.check_existing_config")
    def test_workflow_init_project_cancelled_at_schema(
        self, mock_check_config, mock_questionary
    ) -> None:
        """Test init workflow cancelled at schema selection."""
        mock_check_config.return_value = None
        mock_questionary.select.return_value.ask.return_value = None

        ctx = click.Context(click.Command("test"))
        ctx.obj = {"verbose": False}

        workflow_init_project(ctx)

        # Should not proceed further
        mock_questionary.confirm.assert_not_called()

    @patch("promptrek.cli.interactive.questionary")
    @patch("promptrek.cli.interactive.check_existing_config")
    @patch("promptrek.cli.interactive.init_command")
    @patch("promptrek.cli.interactive.workflow_generate_config")
    def test_workflow_init_project_with_generate(
        self, mock_gen_workflow, mock_init_cmd, mock_check_config, mock_questionary
    ) -> None:
        """Test init workflow that proceeds to generate configs."""
        mock_check_config.return_value = None
        mock_questionary.select.return_value.ask.return_value = "v3"
        mock_questionary.confirm.return_value.ask.side_effect = [True, True, True]

        ctx = click.Context(click.Command("test"))
        ctx.obj = {"verbose": False}

        workflow_init_project(ctx)

        # Verify both init and generate were called
        mock_init_cmd.assert_called_once()
        mock_gen_workflow.assert_called_once_with(ctx)

    @patch("promptrek.cli.interactive.questionary")
    @patch("promptrek.cli.interactive.check_existing_config")
    @patch("promptrek.cli.interactive.init_command")
    def test_workflow_init_project_v1_schema(
        self, mock_init_cmd, mock_check_config, mock_questionary
    ) -> None:
        """Test init workflow with v1 schema selection."""
        mock_check_config.return_value = None
        mock_questionary.select.return_value.ask.return_value = "v1"
        mock_questionary.confirm.return_value.ask.side_effect = [True, True, False]

        ctx = click.Context(click.Command("test"))
        ctx.obj = {"verbose": False}

        workflow_init_project(ctx)

        # Verify init_command was called with use_v2=False for v1
        mock_init_cmd.assert_called_once()
        assert mock_init_cmd.call_args[1]["use_v2"] is False

    @patch("promptrek.cli.interactive.questionary")
    @patch("promptrek.cli.interactive.check_existing_config")
    @patch("promptrek.cli.interactive.init_command")
    def test_workflow_init_project_cancelled_at_hooks(
        self, mock_init_cmd, mock_check_config, mock_questionary
    ) -> None:
        """Test init workflow cancelled at hooks prompt."""
        mock_check_config.return_value = None
        mock_questionary.select.return_value.ask.return_value = "v3"
        mock_questionary.confirm.return_value.ask.return_value = None

        ctx = click.Context(click.Command("test"))
        ctx.obj = {"verbose": False}

        workflow_init_project(ctx)

        # Should not call init_command
        mock_init_cmd.assert_not_called()

    @patch("promptrek.cli.interactive.questionary")
    @patch("promptrek.cli.interactive.check_existing_config")
    @patch("promptrek.cli.interactive.init_command")
    def test_workflow_init_project_cancelled_at_gitignore(
        self, mock_init_cmd, mock_check_config, mock_questionary
    ) -> None:
        """Test init workflow cancelled at gitignore prompt."""
        mock_check_config.return_value = None
        mock_questionary.select.return_value.ask.return_value = "v3"
        mock_questionary.confirm.return_value.ask.side_effect = [True, None]

        ctx = click.Context(click.Command("test"))
        ctx.obj = {"verbose": False}

        workflow_init_project(ctx)

        # Should not call init_command
        mock_init_cmd.assert_not_called()

    @patch("promptrek.cli.interactive.questionary")
    @patch("promptrek.cli.interactive.check_existing_config")
    @patch("promptrek.cli.interactive.init_command")
    def test_workflow_init_project_unexpected_error(
        self, mock_init_cmd, mock_check_config, mock_questionary
    ) -> None:
        """Test init workflow with unexpected error."""
        mock_check_config.return_value = None
        mock_questionary.select.return_value.ask.return_value = "v3"
        mock_questionary.confirm.return_value.ask.side_effect = [True, True]
        mock_init_cmd.side_effect = Exception("Unexpected error")

        ctx = click.Context(click.Command("test"))
        ctx.obj = {"verbose": False}

        workflow_init_project(ctx)

        # Should handle error gracefully
        mock_init_cmd.assert_called_once()

    @patch("promptrek.cli.interactive.questionary")
    @patch("promptrek.cli.interactive.check_existing_config")
    @patch("promptrek.cli.interactive.generate_command")
    @patch("promptrek.adapters.registry")
    def test_workflow_generate_config_success(
        self, mock_registry, mock_gen_cmd, mock_check_config, mock_questionary
    ) -> None:
        """Test successful config generation workflow."""
        mock_check_config.return_value = Path("project.promptrek.yaml")
        mock_registry.get_project_file_adapters.return_value = {
            "cursor": Mock(),
            "claude": Mock(),
        }
        mock_questionary.checkbox.return_value.ask.return_value = ["cursor"]
        mock_questionary.confirm.return_value.ask.side_effect = [False, False, False]

        ctx = click.Context(click.Command("test"))
        ctx.obj = {"verbose": False}

        workflow_generate_config(ctx)

        # Verify generate_command was called
        mock_gen_cmd.assert_called_once()
        assert mock_gen_cmd.call_args[1]["editor"] == "cursor"

    @patch("promptrek.cli.interactive.check_existing_config")
    def test_workflow_generate_config_no_config(self, mock_check_config) -> None:
        """Test generate workflow when no config exists."""
        mock_check_config.return_value = None

        ctx = click.Context(click.Command("test"))
        ctx.obj = {"verbose": False}

        workflow_generate_config(ctx)

        # Should return early

    @patch("promptrek.cli.interactive.questionary")
    @patch("promptrek.cli.interactive.check_existing_config")
    @patch("promptrek.adapters.registry")
    def test_workflow_generate_config_no_editors_selected(
        self, mock_registry, mock_check_config, mock_questionary
    ) -> None:
        """Test generate workflow when no editors are selected."""
        mock_check_config.return_value = Path("project.promptrek.yaml")
        mock_registry.get_project_file_adapters.return_value = {"cursor": Mock()}
        mock_questionary.checkbox.return_value.ask.return_value = []

        ctx = click.Context(click.Command("test"))
        ctx.obj = {"verbose": False}

        workflow_generate_config(ctx)

        # Should cancel without generating

    @patch("promptrek.cli.interactive.questionary")
    @patch("promptrek.cli.interactive.check_existing_config")
    @patch("promptrek.cli.interactive.generate_command")
    @patch("promptrek.adapters.registry")
    def test_workflow_generate_config_with_variables(
        self, mock_registry, mock_gen_cmd, mock_check_config, mock_questionary
    ) -> None:
        """Test config generation with variable overrides."""
        mock_check_config.return_value = Path("project.promptrek.yaml")
        mock_registry.get_project_file_adapters.return_value = {"cursor": Mock()}
        mock_questionary.checkbox.return_value.ask.return_value = ["cursor"]
        mock_questionary.confirm.return_value.ask.side_effect = [True, False, False]
        mock_questionary.text.return_value.ask.side_effect = ["VAR=value", ""]

        ctx = click.Context(click.Command("test"))
        ctx.obj = {"verbose": False}

        workflow_generate_config(ctx)

        # Verify variables were passed
        mock_gen_cmd.assert_called_once()
        assert mock_gen_cmd.call_args[1]["variables"] == {"VAR": "value"}

    @patch("promptrek.cli.interactive.questionary")
    @patch("promptrek.cli.interactive.check_existing_config")
    @patch("promptrek.cli.interactive.generate_command")
    @patch("promptrek.adapters.registry")
    def test_workflow_generate_config_with_invalid_variable(
        self, mock_registry, mock_gen_cmd, mock_check_config, mock_questionary
    ) -> None:
        """Test config generation with invalid variable format."""
        mock_check_config.return_value = Path("project.promptrek.yaml")
        mock_registry.get_project_file_adapters.return_value = {"cursor": Mock()}
        mock_questionary.checkbox.return_value.ask.return_value = ["cursor"]
        mock_questionary.confirm.return_value.ask.side_effect = [True, False, False]
        mock_questionary.text.return_value.ask.side_effect = ["INVALID", ""]

        ctx = click.Context(click.Command("test"))
        ctx.obj = {"verbose": False}

        workflow_generate_config(ctx)

        # Should skip invalid variable and continue
        mock_gen_cmd.assert_called_once()
        assert mock_gen_cmd.call_args[1]["variables"] == {}

    @patch("promptrek.cli.interactive.questionary")
    @patch("promptrek.cli.interactive.check_existing_config")
    @patch("promptrek.cli.interactive.generate_command")
    @patch("promptrek.adapters.registry")
    def test_workflow_generate_config_with_error(
        self, mock_registry, mock_gen_cmd, mock_check_config, mock_questionary
    ) -> None:
        """Test config generation with PrompTrekError."""
        mock_check_config.return_value = Path("project.promptrek.yaml")
        mock_registry.get_project_file_adapters.return_value = {"cursor": Mock()}
        mock_questionary.checkbox.return_value.ask.return_value = ["cursor"]
        mock_questionary.confirm.return_value.ask.side_effect = [False, False, False]
        mock_gen_cmd.side_effect = PrompTrekError("Test error")

        ctx = click.Context(click.Command("test"))
        ctx.obj = {"verbose": False}

        workflow_generate_config(ctx)

        # Should handle error gracefully
        mock_gen_cmd.assert_called_once()

    @patch("promptrek.cli.interactive.questionary")
    @patch("promptrek.cli.interactive.check_existing_config")
    @patch("promptrek.cli.interactive.generate_command")
    @patch("promptrek.adapters.registry")
    def test_workflow_generate_config_unexpected_error(
        self, mock_registry, mock_gen_cmd, mock_check_config, mock_questionary
    ) -> None:
        """Test config generation with unexpected error."""
        mock_check_config.return_value = Path("project.promptrek.yaml")
        mock_registry.get_project_file_adapters.return_value = {"cursor": Mock()}
        mock_questionary.checkbox.return_value.ask.return_value = ["cursor"]
        mock_questionary.confirm.return_value.ask.side_effect = [False, False, False]
        mock_gen_cmd.side_effect = Exception("Unexpected error")

        ctx = click.Context(click.Command("test"))
        ctx.obj = {"verbose": False}

        workflow_generate_config(ctx)

        # Should handle error gracefully
        mock_gen_cmd.assert_called_once()

    @patch("promptrek.cli.interactive.questionary")
    @patch("promptrek.cli.interactive.check_existing_config")
    @patch("promptrek.cli.commands.migrate.migrate_command")
    @patch("shutil.copy2")
    def test_workflow_migrate_with_backup(
        self, mock_copy, mock_migrate_cmd, mock_check_config, mock_questionary
    ) -> None:
        """Test migration workflow with backup."""
        mock_check_config.return_value = Path("project.promptrek.yaml")
        mock_questionary.confirm.return_value.ask.side_effect = [True, True]
        mock_questionary.text.return_value.ask.return_value = "project.v2.yaml"

        ctx = click.Context(click.Command("test"))
        ctx.obj = {"verbose": False}

        workflow_migrate(ctx)

        # Should create backup
        mock_copy.assert_called_once()

    @patch("promptrek.cli.interactive.questionary")
    @patch("promptrek.cli.interactive.check_existing_config")
    @patch("promptrek.cli.commands.migrate.migrate_command")
    def test_workflow_migrate_with_error(
        self, mock_migrate_cmd, mock_check_config, mock_questionary
    ) -> None:
        """Test migration with PrompTrekError."""
        mock_check_config.return_value = Path("project.promptrek.yaml")
        mock_questionary.confirm.return_value.ask.side_effect = [True, True]
        mock_questionary.text.return_value.ask.return_value = "project.v2.yaml"
        mock_migrate_cmd.side_effect = PrompTrekError("Test error")

        ctx = click.Context(click.Command("test"))
        ctx.obj = {"verbose": False}

        workflow_migrate(ctx)

        # Should handle error gracefully
        mock_migrate_cmd.assert_called_once()

    @patch("promptrek.cli.interactive.questionary")
    @patch("promptrek.cli.interactive.check_existing_config")
    @patch("promptrek.cli.commands.migrate.migrate_command")
    def test_workflow_migrate_unexpected_error(
        self, mock_migrate_cmd, mock_check_config, mock_questionary
    ) -> None:
        """Test migration with unexpected error."""
        mock_check_config.return_value = Path("project.promptrek.yaml")
        mock_questionary.confirm.return_value.ask.side_effect = [True, True]
        mock_questionary.text.return_value.ask.return_value = "project.v2.yaml"
        mock_migrate_cmd.side_effect = Exception("Unexpected error")

        ctx = click.Context(click.Command("test"))
        ctx.obj = {"verbose": False}

        workflow_migrate(ctx)

        # Should handle error gracefully
        mock_migrate_cmd.assert_called_once()

    @patch("promptrek.cli.interactive.questionary")
    @patch("promptrek.cli.interactive.check_existing_config")
    def test_workflow_migrate_cancelled_at_backup(
        self, mock_check_config, mock_questionary
    ) -> None:
        """Test migration cancelled at backup prompt."""
        mock_check_config.return_value = Path("project.promptrek.yaml")
        mock_questionary.confirm.return_value.ask.side_effect = [True, None]

        ctx = click.Context(click.Command("test"))
        ctx.obj = {"verbose": False}

        workflow_migrate(ctx)

        # Should cancel

    @patch("promptrek.cli.interactive.questionary")
    @patch("promptrek.cli.interactive.check_existing_config")
    def test_workflow_migrate_cancelled_at_output(
        self, mock_check_config, mock_questionary
    ) -> None:
        """Test migration cancelled at output path prompt."""
        mock_check_config.return_value = Path("project.promptrek.yaml")
        mock_questionary.confirm.return_value.ask.side_effect = [True, True]
        mock_questionary.text.return_value.ask.return_value = ""

        ctx = click.Context(click.Command("test"))
        ctx.obj = {"verbose": False}

        workflow_migrate(ctx)

        # Should cancel

    @patch("promptrek.cli.interactive.check_existing_config")
    def test_workflow_migrate_no_config(self, mock_check_config) -> None:
        """Test migrate workflow when no config exists."""
        mock_check_config.return_value = None

        ctx = click.Context(click.Command("test"))
        ctx.obj = {"verbose": False}

        workflow_migrate(ctx)

        # Should return early

    @patch("promptrek.cli.interactive.questionary")
    @patch("promptrek.cli.interactive.check_existing_config")
    def test_workflow_migrate_cancelled(
        self, mock_check_config, mock_questionary
    ) -> None:
        """Test migrate workflow when user cancels."""
        mock_check_config.return_value = Path("project.promptrek.yaml")
        mock_questionary.confirm.return_value.ask.return_value = False

        ctx = click.Context(click.Command("test"))
        ctx.obj = {"verbose": False}

        workflow_migrate(ctx)

        # Should cancel

    @patch("promptrek.cli.interactive.questionary")
    @patch("promptrek.cli.interactive.check_existing_config")
    @patch("promptrek.cli.commands.validate.validate_command")
    def test_workflow_validate_success(
        self, mock_validate_cmd, mock_check_config, mock_questionary
    ) -> None:
        """Test successful validation workflow."""
        mock_check_config.return_value = Path("project.promptrek.yaml")
        mock_questionary.confirm.return_value.ask.return_value = False

        ctx = click.Context(click.Command("test"))
        ctx.obj = {"verbose": False}

        workflow_validate(ctx)

        # Verify validate_command was called
        mock_validate_cmd.assert_called_once()
        assert mock_validate_cmd.call_args[0][2] is False  # strict=False

    @patch("promptrek.cli.interactive.check_existing_config")
    def test_workflow_validate_no_config(self, mock_check_config) -> None:
        """Test validate workflow when no config exists."""
        mock_check_config.return_value = None

        ctx = click.Context(click.Command("test"))
        ctx.obj = {"verbose": False}

        workflow_validate(ctx)

        # Should return early

    @patch("promptrek.cli.interactive.questionary")
    @patch("promptrek.cli.interactive.check_existing_config")
    @patch("promptrek.cli.commands.validate.validate_command")
    def test_workflow_validate_strict_mode(
        self, mock_validate_cmd, mock_check_config, mock_questionary
    ) -> None:
        """Test validation with strict mode enabled."""
        mock_check_config.return_value = Path("project.promptrek.yaml")
        mock_questionary.confirm.return_value.ask.return_value = True

        ctx = click.Context(click.Command("test"))
        ctx.obj = {"verbose": False}

        workflow_validate(ctx)

        # Verify strict mode was enabled
        assert mock_validate_cmd.call_args[0][2] is True

    @patch("promptrek.cli.interactive.questionary")
    @patch("promptrek.cli.commands.sync.sync_command")
    @patch("promptrek.adapters.registry")
    def test_workflow_sync_success(
        self, mock_registry, mock_sync_cmd, mock_questionary
    ) -> None:
        """Test successful sync workflow."""
        mock_registry.get_project_file_adapters.return_value = {"cursor": Mock()}
        mock_questionary.select.return_value.ask.return_value = "cursor"
        mock_questionary.text.return_value.ask.side_effect = [
            ".",
            "project.promptrek.yaml",
        ]
        mock_questionary.confirm.return_value.ask.return_value = True

        ctx = click.Context(click.Command("test"))
        ctx.obj = {"verbose": False}

        workflow_sync(ctx)

        # Verify sync_command was called
        mock_sync_cmd.assert_called_once()
        assert mock_sync_cmd.call_args[1]["editor"] == "cursor"

    @patch("promptrek.cli.interactive.questionary")
    @patch("promptrek.adapters.registry")
    def test_workflow_sync_cancelled(self, mock_registry, mock_questionary) -> None:
        """Test sync workflow when user cancels."""
        mock_registry.get_project_file_adapters.return_value = {"cursor": Mock()}
        mock_questionary.select.return_value.ask.return_value = None

        ctx = click.Context(click.Command("test"))
        ctx.obj = {"verbose": False}

        workflow_sync(ctx)

        # Should cancel

    @patch("promptrek.cli.interactive.questionary")
    @patch("promptrek.cli.commands.plugins.list_plugins_command")
    def test_workflow_plugins_list(self, mock_list_cmd, mock_questionary) -> None:
        """Test plugins workflow with list action."""
        mock_questionary.select.return_value.ask.return_value = "list"

        ctx = click.Context(click.Command("test"))
        ctx.obj = {"verbose": False}

        workflow_plugins(ctx)

        # Verify list command was called
        mock_list_cmd.assert_called_once()

    @patch("promptrek.cli.interactive.questionary")
    def test_workflow_plugins_back(self, mock_questionary) -> None:
        """Test plugins workflow with back action."""
        mock_questionary.select.return_value.ask.return_value = "back"

        ctx = click.Context(click.Command("test"))
        ctx.obj = {"verbose": False}

        workflow_plugins(ctx)

        # Should return without doing anything

    @patch("promptrek.cli.interactive.questionary")
    @patch("promptrek.cli.interactive.check_existing_config")
    @patch("promptrek.cli.commands.plugins.generate_plugins_command")
    @patch("promptrek.adapters.registry")
    def test_workflow_plugins_generate(
        self, mock_registry, mock_gen_plugins_cmd, mock_check_config, mock_questionary
    ) -> None:
        """Test plugins workflow with generate action."""
        mock_questionary.select.return_value.ask.side_effect = ["generate", "cursor"]
        mock_check_config.return_value = Path("project.promptrek.yaml")
        mock_registry.get_project_file_adapters.return_value = {"cursor": Mock()}
        mock_questionary.confirm.return_value.ask.return_value = False

        ctx = click.Context(click.Command("test"))
        ctx.obj = {"verbose": False}

        workflow_plugins(ctx)

        # Verify generate_plugins_command was called
        mock_gen_plugins_cmd.assert_called_once()

    @patch("promptrek.cli.interactive.questionary")
    @patch("promptrek.cli.interactive.check_existing_config")
    def test_workflow_plugins_generate_no_config(
        self, mock_check_config, mock_questionary
    ) -> None:
        """Test plugins generate when no config exists."""
        mock_questionary.select.return_value.ask.return_value = "generate"
        mock_check_config.return_value = None

        ctx = click.Context(click.Command("test"))
        ctx.obj = {"verbose": False}

        workflow_plugins(ctx)

        # Should return early


class TestShowHelp:
    """Tests for show_help function."""

    def test_show_help(self) -> None:
        """Test that show_help displays help information."""
        show_help()
        # Just verify it doesn't raise an exception


class TestRunInteractiveMode:
    """Tests for run_interactive_mode function."""

    @patch("promptrek.cli.interactive.sys")
    def test_run_interactive_mode_non_tty(self, mock_sys) -> None:
        """Test interactive mode in non-TTY environment."""
        mock_sys.stdin.isatty.return_value = False
        mock_sys.stdout.isatty.return_value = True

        ctx = click.Context(click.Command("test"))
        ctx.obj = {"verbose": False}

        run_interactive_mode(ctx)

        # Should return early and show help

    @patch("promptrek.cli.interactive.sys")
    @patch("promptrek.cli.interactive.print_banner")
    @patch("promptrek.cli.interactive.questionary")
    def test_run_interactive_mode_exit(
        self, mock_questionary, mock_print_banner, mock_sys
    ) -> None:
        """Test interactive mode with exit choice."""
        mock_sys.stdin.isatty.return_value = True
        mock_sys.stdout.isatty.return_value = True
        mock_questionary.select.return_value.ask.return_value = "exit"

        ctx = click.Context(click.Command("test"))
        ctx.obj = {"verbose": False}

        run_interactive_mode(ctx)

        # Should print banner and exit gracefully
        mock_print_banner.assert_called_once()

    @patch("promptrek.cli.interactive.sys")
    @patch("promptrek.cli.interactive.print_banner")
    @patch("promptrek.cli.interactive.questionary")
    @patch("promptrek.cli.interactive.workflow_init_project")
    def test_run_interactive_mode_init(
        self, mock_workflow, mock_questionary, mock_print_banner, mock_sys
    ) -> None:
        """Test interactive mode with init choice."""
        mock_sys.stdin.isatty.return_value = True
        mock_sys.stdout.isatty.return_value = True
        mock_questionary.select.return_value.ask.side_effect = ["init", "exit"]

        ctx = click.Context(click.Command("test"))
        ctx.obj = {"verbose": False}

        run_interactive_mode(ctx)

        # Should call init workflow
        mock_workflow.assert_called_once_with(ctx)

    @patch("promptrek.cli.interactive.sys")
    @patch("promptrek.cli.interactive.print_banner")
    @patch("promptrek.cli.interactive.questionary")
    @patch("promptrek.cli.interactive.workflow_generate_config")
    def test_run_interactive_mode_generate(
        self, mock_workflow, mock_questionary, mock_print_banner, mock_sys
    ) -> None:
        """Test interactive mode with generate choice."""
        mock_sys.stdin.isatty.return_value = True
        mock_sys.stdout.isatty.return_value = True
        mock_questionary.select.return_value.ask.side_effect = ["generate", "exit"]

        ctx = click.Context(click.Command("test"))
        ctx.obj = {"verbose": False}

        run_interactive_mode(ctx)

        # Should call generate workflow
        mock_workflow.assert_called_once_with(ctx)

    @patch("promptrek.cli.interactive.sys")
    @patch("promptrek.cli.interactive.print_banner")
    @patch("promptrek.cli.interactive.questionary")
    @patch("promptrek.cli.interactive.show_help")
    def test_run_interactive_mode_help(
        self, mock_show_help, mock_questionary, mock_print_banner, mock_sys
    ) -> None:
        """Test interactive mode with help choice."""
        mock_sys.stdin.isatty.return_value = True
        mock_sys.stdout.isatty.return_value = True
        mock_questionary.select.return_value.ask.side_effect = ["help", "exit"]

        ctx = click.Context(click.Command("test"))
        ctx.obj = {"verbose": False}

        run_interactive_mode(ctx)

        # Should call show_help
        mock_show_help.assert_called_once()

    @patch("promptrek.cli.interactive.sys")
    @patch("promptrek.cli.interactive.print_banner")
    @patch("promptrek.cli.interactive.questionary")
    @patch("promptrek.cli.interactive.workflow_migrate")
    def test_run_interactive_mode_migrate(
        self, mock_workflow, mock_questionary, mock_print_banner, mock_sys
    ) -> None:
        """Test interactive mode with migrate choice."""
        mock_sys.stdin.isatty.return_value = True
        mock_sys.stdout.isatty.return_value = True
        mock_questionary.select.return_value.ask.side_effect = ["migrate", "exit"]

        ctx = click.Context(click.Command("test"))
        ctx.obj = {"verbose": False}

        run_interactive_mode(ctx)

        # Should call migrate workflow
        mock_workflow.assert_called_once_with(ctx)

    @patch("promptrek.cli.interactive.sys")
    @patch("promptrek.cli.interactive.print_banner")
    @patch("promptrek.cli.interactive.questionary")
    @patch("promptrek.cli.interactive.workflow_validate")
    def test_run_interactive_mode_validate(
        self, mock_workflow, mock_questionary, mock_print_banner, mock_sys
    ) -> None:
        """Test interactive mode with validate choice."""
        mock_sys.stdin.isatty.return_value = True
        mock_sys.stdout.isatty.return_value = True
        mock_questionary.select.return_value.ask.side_effect = ["validate", "exit"]

        ctx = click.Context(click.Command("test"))
        ctx.obj = {"verbose": False}

        run_interactive_mode(ctx)

        # Should call validate workflow
        mock_workflow.assert_called_once_with(ctx)

    @patch("promptrek.cli.interactive.sys")
    @patch("promptrek.cli.interactive.print_banner")
    @patch("promptrek.cli.interactive.questionary")
    @patch("promptrek.cli.interactive.workflow_sync")
    def test_run_interactive_mode_sync(
        self, mock_workflow, mock_questionary, mock_print_banner, mock_sys
    ) -> None:
        """Test interactive mode with sync choice."""
        mock_sys.stdin.isatty.return_value = True
        mock_sys.stdout.isatty.return_value = True
        mock_questionary.select.return_value.ask.side_effect = ["sync", "exit"]

        ctx = click.Context(click.Command("test"))
        ctx.obj = {"verbose": False}

        run_interactive_mode(ctx)

        # Should call sync workflow
        mock_workflow.assert_called_once_with(ctx)

    @patch("promptrek.cli.interactive.sys")
    @patch("promptrek.cli.interactive.print_banner")
    @patch("promptrek.cli.interactive.questionary")
    @patch("promptrek.cli.interactive.workflow_plugins")
    def test_run_interactive_mode_plugins(
        self, mock_workflow, mock_questionary, mock_print_banner, mock_sys
    ) -> None:
        """Test interactive mode with plugins choice."""
        mock_sys.stdin.isatty.return_value = True
        mock_sys.stdout.isatty.return_value = True
        mock_questionary.select.return_value.ask.side_effect = ["plugins", "exit"]

        ctx = click.Context(click.Command("test"))
        ctx.obj = {"verbose": False}

        run_interactive_mode(ctx)

        # Should call plugins workflow
        mock_workflow.assert_called_once_with(ctx)

    @patch("promptrek.cli.interactive.sys")
    @patch("promptrek.cli.interactive.print_banner")
    @patch("promptrek.cli.interactive.questionary")
    def test_run_interactive_mode_cancelled(
        self, mock_questionary, mock_print_banner, mock_sys
    ) -> None:
        """Test interactive mode when user presses Ctrl+C."""
        mock_sys.stdin.isatty.return_value = True
        mock_sys.stdout.isatty.return_value = True
        mock_questionary.select.return_value.ask.return_value = None

        ctx = click.Context(click.Command("test"))
        ctx.obj = {"verbose": False}

        run_interactive_mode(ctx)

        # Should exit gracefully
        mock_print_banner.assert_called_once()


class TestCLIBackwardCompatibility:
    """Tests for backward compatibility with existing CLI commands."""

    def test_init_command_still_works(self) -> None:
        """Test that 'promptrek init' still works as before."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            result = runner.invoke(cli, ["init", "--help"])
            assert result.exit_code == 0
            assert "Initialize" in result.output

    def test_generate_command_still_works(self) -> None:
        """Test that 'promptrek generate' still works as before."""
        runner = CliRunner()
        result = runner.invoke(cli, ["generate", "--help"])
        assert result.exit_code == 0
        assert "Generate" in result.output

    def test_validate_command_still_works(self) -> None:
        """Test that 'promptrek validate' still works as before."""
        runner = CliRunner()
        result = runner.invoke(cli, ["validate", "--help"])
        assert result.exit_code == 0
        assert "Validate" in result.output

    def test_all_commands_available(self) -> None:
        """Test that all original commands are still available."""
        runner = CliRunner()
        result = runner.invoke(cli, ["--help"])
        assert result.exit_code == 0

        # Check that key commands are present
        expected_commands = [
            "init",
            "generate",
            "validate",
            "migrate",
            "sync",
            "preview",
            "plugins",
            "install-hooks",
            "list-editors",
        ]

        for command in expected_commands:
            assert command in result.output
