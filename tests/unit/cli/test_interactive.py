"""
Tests for interactive CLI wizard.
"""

import sys
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import pytest
from click.testing import CliRunner

from promptrek.cli.interactive import (
    BANNER,
    check_existing_config,
    print_banner,
    run_interactive_mode,
)
from promptrek.cli.main import cli


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

        os.chdir(tmp_path)
        result = check_existing_config()
        assert result is None

    def test_check_existing_config_found_project_yaml(self, tmp_path: Path) -> None:
        """Test when project.promptrek.yaml exists."""
        import os

        os.chdir(tmp_path)
        config_file = tmp_path / "project.promptrek.yaml"
        config_file.touch()
        result = check_existing_config()
        assert result is not None
        assert result.name == "project.promptrek.yaml"

    def test_check_existing_config_found_project_yml(self, tmp_path: Path) -> None:
        """Test when project.promptrek.yml exists."""
        import os

        os.chdir(tmp_path)
        config_file = tmp_path / "project.promptrek.yml"
        config_file.touch()
        result = check_existing_config()
        assert result is not None
        assert result.name == "project.promptrek.yml"

    def test_check_existing_config_found_dotfile(self, tmp_path: Path) -> None:
        """Test when .promptrek.yaml exists."""
        import os

        os.chdir(tmp_path)
        config_file = tmp_path / ".promptrek.yaml"
        config_file.touch()
        result = check_existing_config()
        assert result is not None
        assert result.name == ".promptrek.yaml"


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


class TestWorkflowInitProject:
    """Tests for workflow_init_project function."""

    @patch("click.echo")
    @patch("promptrek.cli.interactive.questionary.confirm")
    @patch("promptrek.cli.interactive.questionary.select")
    @patch("promptrek.cli.interactive.init_command")
    def test_workflow_init_project_no_existing_config(
        self, mock_init, mock_select, mock_confirm, mock_echo, tmp_path: Path
    ) -> None:
        """Test init workflow when no config exists."""
        import os

        os.chdir(tmp_path)

        # Mock questionary responses
        mock_select.return_value.ask.return_value = "v3"
        # Mock confirm to return different values for hooks, gitignore, generate_now
        confirm_returns = [
            Mock(ask=Mock(return_value=True)),
            Mock(ask=Mock(return_value=True)),
            Mock(ask=Mock(return_value=False)),
        ]
        mock_confirm.side_effect = confirm_returns

        ctx = Mock()
        ctx.obj = {"verbose": False}

        from promptrek.cli.interactive import workflow_init_project

        workflow_init_project(ctx)

        # Verify init_command was called
        mock_init.assert_called_once()

    @patch("promptrek.cli.interactive.questionary.confirm")
    @patch("promptrek.cli.interactive.questionary.select")
    def test_workflow_init_project_cancel_on_overwrite(
        self, mock_select, mock_confirm, tmp_path: Path
    ) -> None:
        """Test init workflow when user cancels overwrite."""
        import os

        os.chdir(tmp_path)

        # Create existing config
        config_file = tmp_path / "project.promptrek.yaml"
        config_file.write_text("test")

        # Mock user declining to overwrite
        mock_confirm.return_value.ask.return_value = False

        ctx = Mock()
        ctx.obj = {"verbose": False}

        with patch("click.echo"):
            from promptrek.cli.interactive import workflow_init_project

            workflow_init_project(ctx)

        # Should not call select since we cancelled
        mock_select.assert_not_called()

    @patch("promptrek.cli.interactive.questionary.confirm")
    @patch("promptrek.cli.interactive.questionary.select")
    def test_workflow_init_project_cancel_on_schema(
        self, mock_select, mock_confirm, tmp_path: Path
    ) -> None:
        """Test init workflow when user cancels schema selection."""
        import os

        os.chdir(tmp_path)

        # Mock user cancelling on schema selection
        mock_select.return_value.ask.return_value = None

        ctx = Mock()
        ctx.obj = {"verbose": False}

        from promptrek.cli.interactive import workflow_init_project

        workflow_init_project(ctx)

        # Should not call confirm for hooks since we cancelled
        mock_confirm.assert_not_called()


class TestWorkflowGenerateConfig:
    """Tests for workflow_generate_config function."""

    @patch("click.echo")
    def test_workflow_generate_config_no_config(
        self, mock_echo, tmp_path: Path
    ) -> None:
        """Test generate workflow when no config exists."""
        import os

        os.chdir(tmp_path)

        ctx = Mock()
        ctx.obj = {"verbose": False}

        from promptrek.cli.interactive import workflow_generate_config

        workflow_generate_config(ctx)
        # Should return early without error

    @patch("click.echo")
    @patch("promptrek.cli.interactive.questionary.checkbox")
    def test_workflow_generate_config_no_editors_selected(
        self, mock_checkbox, mock_echo, tmp_path: Path
    ) -> None:
        """Test generate workflow when no editors selected."""
        import os

        os.chdir(tmp_path)

        # Create existing config
        config_file = tmp_path / "project.promptrek.yaml"
        config_file.write_text("schema_version: 3.0.0\ncontent: test")

        # Mock no editors selected
        mock_checkbox.return_value.ask.return_value = []

        ctx = Mock()
        ctx.obj = {"verbose": False}

        from promptrek.cli.interactive import workflow_generate_config

        workflow_generate_config(ctx)
        # Should return early


class TestWorkflowMigrate:
    """Tests for workflow_migrate function."""

    @patch("promptrek.cli.interactive.questionary.confirm")
    @patch("promptrek.cli.interactive.questionary.text")
    def test_workflow_migrate_cancel_on_proceed(
        self, mock_text, mock_confirm, tmp_path: Path
    ) -> None:
        """Test migrate workflow when user cancels."""
        import os

        os.chdir(tmp_path)

        # Create existing config
        config_file = tmp_path / "project.promptrek.yaml"
        config_file.write_text("schema_version: 1.0.0\nname: test")

        # Mock user declining to proceed
        mock_confirm.return_value.ask.return_value = False

        ctx = Mock()
        ctx.obj = {"verbose": False}

        from promptrek.cli.interactive import workflow_migrate

        workflow_migrate(ctx)

        # Should not ask for output path
        mock_text.assert_not_called()


class TestWorkflowValidate:
    """Tests for workflow_validate function."""

    @patch("click.echo")
    def test_workflow_validate_no_config(self, mock_echo, tmp_path: Path) -> None:
        """Test validate workflow when no config exists."""
        import os

        os.chdir(tmp_path)

        ctx = Mock()
        ctx.obj = {"verbose": False}

        from promptrek.cli.interactive import workflow_validate

        workflow_validate(ctx)
        # Should return early without error


class TestWorkflowSync:
    """Tests for workflow_sync function."""

    @patch("promptrek.cli.interactive.questionary.select")
    @patch("promptrek.cli.interactive.questionary.text")
    @patch("promptrek.cli.interactive.questionary.confirm")
    def test_workflow_sync_cancel_on_editor(
        self, mock_confirm, mock_text, mock_select, tmp_path: Path
    ) -> None:
        """Test sync workflow when user cancels editor selection."""
        import os

        os.chdir(tmp_path)

        # Mock user cancelling on editor selection
        mock_select.return_value.ask.return_value = None

        ctx = Mock()
        ctx.obj = {"verbose": False}

        from promptrek.cli.interactive import workflow_sync

        workflow_sync(ctx)

        # Should not ask for source directory
        mock_text.assert_not_called()


class TestWorkflowPlugins:
    """Tests for workflow_plugins function."""

    @patch("click.echo")
    @patch("promptrek.cli.interactive.questionary.select")
    def test_workflow_plugins_go_back(
        self, mock_select, mock_echo, tmp_path: Path
    ) -> None:
        """Test plugins workflow when user goes back."""
        import os

        os.chdir(tmp_path)

        # Mock user selecting 'back'
        mock_select.return_value.ask.return_value = "back"

        ctx = Mock()
        ctx.obj = {"verbose": False}

        from promptrek.cli.interactive import workflow_plugins

        workflow_plugins(ctx)
        # Should return early


class TestShowHelp:
    """Tests for show_help function."""

    @patch("click.echo")
    def test_show_help_displays_content(self, mock_echo) -> None:
        """Test that show_help displays help content."""
        from promptrek.cli.interactive import show_help

        show_help()

        # Should print multiple lines
        assert mock_echo.call_count > 0

        # Check that it mentions common commands
        output = " ".join(str(call) for call in mock_echo.call_args_list)
        assert "init" in output or "generate" in output


class TestRunInteractiveMode:
    """Tests for run_interactive_mode function."""

    @patch("click.echo")
    @patch("promptrek.cli.interactive.questionary.select")
    @patch("promptrek.cli.interactive.print_banner")
    def test_run_interactive_mode_exit_immediately(
        self, mock_banner, mock_select, mock_echo
    ) -> None:
        """Test interactive mode when user exits immediately."""
        # Mock TTY
        with (
            patch("sys.stdin.isatty", return_value=True),
            patch("sys.stdout.isatty", return_value=True),
        ):
            # Mock user selecting exit
            mock_select.return_value.ask.return_value = "exit"

            ctx = Mock()
            ctx.obj = {"verbose": False}

            run_interactive_mode(ctx)

    @patch("click.echo")
    @patch("promptrek.cli.interactive.questionary.select")
    @patch("promptrek.cli.interactive.workflow_init_project")
    @patch("promptrek.cli.interactive.print_banner")
    def test_run_interactive_mode_init_then_exit(
        self, mock_banner, mock_workflow_init, mock_select, mock_echo
    ) -> None:
        """Test interactive mode selecting init then exiting."""
        # Mock TTY
        with (
            patch("sys.stdin.isatty", return_value=True),
            patch("sys.stdout.isatty", return_value=True),
        ):
            # Mock user selecting init then exit
            mock_select.return_value.ask.side_effect = ["init", "exit"]

            ctx = Mock()
            ctx.obj = {"verbose": False}

            run_interactive_mode(ctx)

            # Verify workflow was called
            mock_workflow_init.assert_called_once()

    @patch("click.echo")
    @patch("promptrek.cli.interactive.questionary.select")
    @patch("promptrek.cli.interactive.show_help")
    @patch("promptrek.cli.interactive.print_banner")
    def test_run_interactive_mode_help_then_exit(
        self, mock_banner, mock_help, mock_select, mock_echo
    ) -> None:
        """Test interactive mode selecting help then exiting."""
        # Mock TTY
        with (
            patch("sys.stdin.isatty", return_value=True),
            patch("sys.stdout.isatty", return_value=True),
        ):
            # Mock user selecting help then exit
            mock_select.return_value.ask.side_effect = ["help", "exit"]

            ctx = Mock()
            ctx.obj = {"verbose": False}

            run_interactive_mode(ctx)

            # Verify help was called
            mock_help.assert_called_once()

    @patch("click.echo")
    @patch("promptrek.cli.interactive.questionary.select")
    @patch("promptrek.cli.interactive.print_banner")
    def test_run_interactive_mode_cancel(
        self, mock_banner, mock_select, mock_echo
    ) -> None:
        """Test interactive mode when user cancels."""
        # Mock TTY
        with (
            patch("sys.stdin.isatty", return_value=True),
            patch("sys.stdout.isatty", return_value=True),
        ):
            # Mock user cancelling (None)
            mock_select.return_value.ask.return_value = None

            ctx = Mock()
            ctx.obj = {"verbose": False}

            run_interactive_mode(ctx)
            # Should exit gracefully

    @patch("click.echo")
    @patch("promptrek.cli.interactive.questionary.select")
    @patch("promptrek.cli.interactive.workflow_generate_config")
    @patch("promptrek.cli.interactive.print_banner")
    def test_run_interactive_mode_generate(
        self, mock_banner, mock_workflow_generate, mock_select, mock_echo
    ) -> None:
        """Test interactive mode selecting generate."""
        # Mock TTY
        with (
            patch("sys.stdin.isatty", return_value=True),
            patch("sys.stdout.isatty", return_value=True),
        ):
            # Mock user selecting generate then exit
            mock_select.return_value.ask.side_effect = ["generate", "exit"]

            ctx = Mock()
            ctx.obj = {"verbose": False}

            run_interactive_mode(ctx)

            # Verify workflow was called
            mock_workflow_generate.assert_called_once()

    @patch("click.echo")
    @patch("promptrek.cli.interactive.questionary.select")
    @patch("promptrek.cli.interactive.workflow_migrate")
    @patch("promptrek.cli.interactive.print_banner")
    def test_run_interactive_mode_migrate(
        self, mock_banner, mock_workflow_migrate, mock_select, mock_echo
    ) -> None:
        """Test interactive mode selecting migrate."""
        # Mock TTY
        with (
            patch("sys.stdin.isatty", return_value=True),
            patch("sys.stdout.isatty", return_value=True),
        ):
            # Mock user selecting migrate then exit
            mock_select.return_value.ask.side_effect = ["migrate", "exit"]

            ctx = Mock()
            ctx.obj = {"verbose": False}

            run_interactive_mode(ctx)

            # Verify workflow was called
            mock_workflow_migrate.assert_called_once()

    @patch("click.echo")
    @patch("promptrek.cli.interactive.questionary.select")
    @patch("promptrek.cli.interactive.workflow_validate")
    @patch("promptrek.cli.interactive.print_banner")
    def test_run_interactive_mode_validate(
        self, mock_banner, mock_workflow_validate, mock_select, mock_echo
    ) -> None:
        """Test interactive mode selecting validate."""
        # Mock TTY
        with (
            patch("sys.stdin.isatty", return_value=True),
            patch("sys.stdout.isatty", return_value=True),
        ):
            # Mock user selecting validate then exit
            mock_select.return_value.ask.side_effect = ["validate", "exit"]

            ctx = Mock()
            ctx.obj = {"verbose": False}

            run_interactive_mode(ctx)

            # Verify workflow was called
            mock_workflow_validate.assert_called_once()

    @patch("click.echo")
    @patch("promptrek.cli.interactive.questionary.select")
    @patch("promptrek.cli.interactive.workflow_sync")
    @patch("promptrek.cli.interactive.print_banner")
    def test_run_interactive_mode_sync(
        self, mock_banner, mock_workflow_sync, mock_select, mock_echo
    ) -> None:
        """Test interactive mode selecting sync."""
        # Mock TTY
        with (
            patch("sys.stdin.isatty", return_value=True),
            patch("sys.stdout.isatty", return_value=True),
        ):
            # Mock user selecting sync then exit
            mock_select.return_value.ask.side_effect = ["sync", "exit"]

            ctx = Mock()
            ctx.obj = {"verbose": False}

            from promptrek.cli.interactive import run_interactive_mode

            run_interactive_mode(ctx)

            # Verify workflow was called
            mock_workflow_sync.assert_called_once()

    @patch("click.echo")
    @patch("promptrek.cli.interactive.questionary.select")
    @patch("promptrek.cli.interactive.workflow_plugins")
    @patch("promptrek.cli.interactive.print_banner")
    def test_run_interactive_mode_plugins(
        self, mock_banner, mock_workflow_plugins, mock_select, mock_echo
    ) -> None:
        """Test interactive mode selecting plugins."""
        # Mock TTY
        with (
            patch("sys.stdin.isatty", return_value=True),
            patch("sys.stdout.isatty", return_value=True),
        ):
            # Mock user selecting plugins then exit
            mock_select.return_value.ask.side_effect = ["plugins", "exit"]

            ctx = Mock()
            ctx.obj = {"verbose": False}

            from promptrek.cli.interactive import run_interactive_mode

            run_interactive_mode(ctx)

            # Verify workflow was called
            mock_workflow_plugins.assert_called_once()


class TestWorkflowErrorHandling:
    """Tests for error handling in workflows."""

    @patch("click.echo")
    @patch("promptrek.cli.interactive.init_command")
    def test_workflow_init_with_exception(self, mock_init, mock_echo, tmp_path):
        """Test init workflow when command raises exception."""
        import os

        os.chdir(tmp_path)

        ctx = Mock()
        ctx.obj = {"verbose": False}

        # Make init raise an exception
        from promptrek.core.exceptions import PrompTrekError

        mock_init.side_effect = PrompTrekError("Init failed")

        with patch("promptrek.cli.interactive.questionary.select") as mock_select:
            with patch("promptrek.cli.interactive.questionary.confirm") as mock_confirm:
                mock_select.return_value.ask.return_value = "v3"
                confirm_returns = [
                    Mock(ask=Mock(return_value=True)),
                    Mock(ask=Mock(return_value=True)),
                ]
                mock_confirm.side_effect = confirm_returns

                from promptrek.cli.interactive import workflow_init_project

                # Should not raise - should catch and display error
                workflow_init_project(ctx)

                # Should have printed error message
                error_calls = [
                    call for call in mock_echo.call_args_list if "Error" in str(call)
                ]
                assert len(error_calls) > 0

    @patch("click.echo")
    def test_workflow_migrate_no_config(self, mock_echo, tmp_path):
        """Test migrate workflow when no config exists."""
        import os

        os.chdir(tmp_path)

        ctx = Mock()
        ctx.obj = {"verbose": False}

        from promptrek.cli.interactive import workflow_migrate

        workflow_migrate(ctx)

        # Should display warning about missing config
        warning_calls = [
            call for call in mock_echo.call_args_list if "found" in str(call).lower()
        ]
        assert len(warning_calls) > 0

    @patch("click.echo")
    @patch("promptrek.cli.interactive.generate_command")
    def test_workflow_generate_with_exception(self, mock_generate, mock_echo, tmp_path):
        """Test generate workflow when command raises exception."""
        import os

        os.chdir(tmp_path)

        # Create existing config
        config_file = tmp_path / "project.promptrek.yaml"
        config_file.write_text("schema_version: 3.0.0\ncontent: test")

        ctx = Mock()
        ctx.obj = {"verbose": False}

        # Make generate raise an exception
        from promptrek.core.exceptions import PrompTrekError

        mock_generate.side_effect = PrompTrekError("Generate failed")

        with patch("promptrek.cli.interactive.questionary.checkbox") as mock_checkbox:
            with patch("promptrek.cli.interactive.questionary.confirm") as mock_confirm:
                mock_checkbox.return_value.ask.return_value = ["claude"]
                confirm_returns = [
                    Mock(ask=Mock(return_value=False)),
                    Mock(ask=Mock(return_value=False)),
                    Mock(ask=Mock(return_value=False)),
                ]
                mock_confirm.side_effect = confirm_returns

                from promptrek.cli.interactive import workflow_generate_config

                # Should not raise - should catch and display error
                workflow_generate_config(ctx)

                # Should have printed error message
                error_calls = [
                    call for call in mock_echo.call_args_list if "Error" in str(call)
                ]
                assert len(error_calls) > 0

    @patch("click.echo")
    def test_workflow_sync_cancel_source_dir(self, mock_echo, tmp_path):
        """Test sync workflow when user cancels source directory."""
        import os

        os.chdir(tmp_path)

        ctx = Mock()
        ctx.obj = {"verbose": False}

        with patch("promptrek.cli.interactive.questionary.select") as mock_select:
            with patch("promptrek.cli.interactive.questionary.text") as mock_text:
                mock_select.return_value.ask.return_value = "claude"
                # User cancels on source directory
                mock_text.return_value.ask.return_value = None

                from promptrek.cli.interactive import workflow_sync

                workflow_sync(ctx)

                # Should display cancelled message
                cancelled_calls = [
                    call
                    for call in mock_echo.call_args_list
                    if "Cancelled" in str(call)
                ]
                assert len(cancelled_calls) > 0

    @patch("click.echo")
    def test_workflow_plugins_cancel(self, mock_echo, tmp_path):
        """Test plugins workflow when user cancels."""
        import os

        os.chdir(tmp_path)

        ctx = Mock()
        ctx.obj = {"verbose": False}

        with patch("promptrek.cli.interactive.questionary.select") as mock_select:
            # User cancels selection
            mock_select.return_value.ask.return_value = None

            from promptrek.cli.interactive import workflow_plugins

            workflow_plugins(ctx)
            # Should return early without error

    @patch("click.echo")
    def test_workflow_validate_cancel(self, mock_echo, tmp_path):
        """Test validate workflow when user cancels."""
        import os

        os.chdir(tmp_path)

        # Create existing config
        config_file = tmp_path / "project.promptrek.yaml"
        config_file.write_text("schema_version: 3.0.0\ncontent: test")

        ctx = Mock()
        ctx.obj = {"verbose": False}

        with patch("promptrek.cli.interactive.questionary.confirm") as mock_confirm:
            # User cancels on strict mode
            mock_confirm.return_value.ask.return_value = None

            from promptrek.cli.interactive import workflow_validate

            workflow_validate(ctx)

            # Should display cancelled message
            cancelled_calls = [
                call for call in mock_echo.call_args_list if "Cancelled" in str(call)
            ]
            assert len(cancelled_calls) > 0

    @patch("click.echo")
    @patch("promptrek.cli.interactive.init_command")
    def test_workflow_init_verbose_error(self, mock_init, mock_echo, tmp_path):
        """Test init workflow in verbose mode with error (should re-raise)."""
        import os

        os.chdir(tmp_path)

        ctx = Mock()
        ctx.obj = {"verbose": True}  # Verbose mode

        # Make init raise an exception
        mock_init.side_effect = Exception("Generic error")

        with patch("promptrek.cli.interactive.questionary.select") as mock_select:
            with patch("promptrek.cli.interactive.questionary.confirm") as mock_confirm:
                mock_select.return_value.ask.return_value = "v3"
                confirm_returns = [
                    Mock(ask=Mock(return_value=True)),
                    Mock(ask=Mock(return_value=True)),
                ]
                mock_confirm.side_effect = confirm_returns

                from promptrek.cli.interactive import workflow_init_project

                # In verbose mode, should re-raise
                with pytest.raises(Exception, match="Generic error"):
                    workflow_init_project(ctx)

    @patch("click.echo")
    @patch("promptrek.cli.interactive.generate_command")
    def test_workflow_generate_verbose_error(self, mock_generate, mock_echo, tmp_path):
        """Test generate workflow in verbose mode with error (should re-raise)."""
        import os

        os.chdir(tmp_path)

        # Create existing config
        config_file = tmp_path / "project.promptrek.yaml"
        config_file.write_text("schema_version: 3.0.0\ncontent: test")

        ctx = Mock()
        ctx.obj = {"verbose": True}  # Verbose mode

        # Make generate raise an exception
        mock_generate.side_effect = Exception("Generic error")

        with patch("promptrek.cli.interactive.questionary.checkbox") as mock_checkbox:
            with patch("promptrek.cli.interactive.questionary.confirm") as mock_confirm:
                mock_checkbox.return_value.ask.return_value = ["claude"]
                confirm_returns = [
                    Mock(ask=Mock(return_value=False)),
                    Mock(ask=Mock(return_value=False)),
                    Mock(ask=Mock(return_value=False)),
                ]
                mock_confirm.side_effect = confirm_returns

                from promptrek.cli.interactive import workflow_generate_config

                # In verbose mode, should re-raise
                with pytest.raises(Exception, match="Generic error"):
                    workflow_generate_config(ctx)

    @patch("click.echo")
    @patch("promptrek.cli.commands.migrate.migrate_command")
    def test_workflow_migrate_with_exception(self, mock_migrate, mock_echo, tmp_path):
        """Test migrate workflow when command raises exception."""
        import os

        os.chdir(tmp_path)

        # Create existing config
        config_file = tmp_path / "project.promptrek.yaml"
        config_file.write_text("schema_version: 1.0.0\nname: test")

        ctx = Mock()
        ctx.obj = {"verbose": False}

        # Make migrate raise an exception
        from promptrek.core.exceptions import PrompTrekError

        mock_migrate.side_effect = PrompTrekError("Migrate failed")

        with patch("promptrek.cli.interactive.questionary.confirm") as mock_confirm:
            with patch("promptrek.cli.interactive.questionary.text") as mock_text:
                confirm_returns = [
                    Mock(ask=Mock(return_value=True)),
                    Mock(ask=Mock(return_value=True)),
                ]
                mock_confirm.side_effect = confirm_returns
                mock_text.return_value.ask.return_value = "output.yaml"

                from promptrek.cli.interactive import workflow_migrate

                # Should not raise - should catch and display error
                workflow_migrate(ctx)

                # Should have printed error message
                error_calls = [
                    call for call in mock_echo.call_args_list if "Error" in str(call)
                ]
                assert len(error_calls) > 0

    @patch("click.echo")
    @patch("promptrek.cli.commands.validate.validate_command")
    def test_workflow_validate_with_exception(self, mock_validate, mock_echo, tmp_path):
        """Test validate workflow when command raises exception."""
        import os

        os.chdir(tmp_path)

        # Create existing config
        config_file = tmp_path / "project.promptrek.yaml"
        config_file.write_text("schema_version: 3.0.0\ncontent: test")

        ctx = Mock()
        ctx.obj = {"verbose": False}

        # Make validate raise an exception
        from promptrek.core.exceptions import PrompTrekError

        mock_validate.side_effect = PrompTrekError("Validate failed")

        with patch("promptrek.cli.interactive.questionary.confirm") as mock_confirm:
            mock_confirm.return_value.ask.return_value = False

            from promptrek.cli.interactive import workflow_validate

            # Should not raise - should catch and display error
            workflow_validate(ctx)

            # Should have printed error message
            error_calls = [
                call for call in mock_echo.call_args_list if "Error" in str(call)
            ]
            assert len(error_calls) > 0

    @patch("click.echo")
    @patch("promptrek.cli.commands.sync.sync_command")
    def test_workflow_sync_with_exception(self, mock_sync, mock_echo, tmp_path):
        """Test sync workflow when command raises exception."""
        import os

        os.chdir(tmp_path)

        ctx = Mock()
        ctx.obj = {"verbose": False}

        # Make sync raise an exception
        from promptrek.core.exceptions import PrompTrekError

        mock_sync.side_effect = PrompTrekError("Sync failed")

        with patch("promptrek.cli.interactive.questionary.select") as mock_select:
            with patch("promptrek.cli.interactive.questionary.text") as mock_text:
                with patch(
                    "promptrek.cli.interactive.questionary.confirm"
                ) as mock_confirm:
                    mock_select.return_value.ask.return_value = "claude"
                    mock_text.return_value.ask.side_effect = [".", "output.yaml"]
                    mock_confirm.return_value.ask.return_value = True

                    from promptrek.cli.interactive import workflow_sync

                    # Should not raise - should catch and display error
                    workflow_sync(ctx)

                    # Should have printed error message
                    error_calls = [
                        call
                        for call in mock_echo.call_args_list
                        if "Error" in str(call)
                    ]
                    assert len(error_calls) > 0

    @patch("click.echo")
    @patch("promptrek.cli.commands.plugins.generate_plugins_command")
    def test_workflow_plugins_generate_no_config(
        self, mock_generate_plugins, mock_echo, tmp_path
    ):
        """Test plugins generate workflow when no config exists."""
        import os

        os.chdir(tmp_path)

        ctx = Mock()
        ctx.obj = {"verbose": False}

        with patch("promptrek.cli.interactive.questionary.select") as mock_select:
            # User selects generate
            mock_select.return_value.ask.return_value = "generate"

            from promptrek.cli.interactive import workflow_plugins

            workflow_plugins(ctx)

            # Should display warning about missing config
            warning_calls = [
                call
                for call in mock_echo.call_args_list
                if "found" in str(call).lower()
            ]
            assert len(warning_calls) > 0

    @patch("click.echo")
    @patch("promptrek.cli.commands.plugins.generate_plugins_command")
    def test_workflow_plugins_generate_with_exception(
        self, mock_generate_plugins, mock_echo, tmp_path
    ):
        """Test plugins generate workflow when command raises exception."""
        import os

        os.chdir(tmp_path)

        # Create existing config
        config_file = tmp_path / "project.promptrek.yaml"
        config_file.write_text("schema_version: 3.0.0\ncontent: test")

        ctx = Mock()
        ctx.obj = {"verbose": False}

        # Make generate raise an exception
        from promptrek.core.exceptions import PrompTrekError

        mock_generate_plugins.side_effect = PrompTrekError("Plugin generation failed")

        with patch("promptrek.cli.interactive.questionary.select") as mock_select:
            with patch("promptrek.cli.interactive.questionary.confirm") as mock_confirm:
                # User selects generate, then selects an editor
                mock_select.return_value.ask.side_effect = ["generate", "claude"]
                mock_confirm.return_value.ask.return_value = False

                from promptrek.cli.interactive import workflow_plugins

                # Should not raise - should catch and display error
                workflow_plugins(ctx)

                # Should have printed error message
                error_calls = [
                    call for call in mock_echo.call_args_list if "Error" in str(call)
                ]
                assert len(error_calls) > 0

    @patch("click.echo")
    @patch("promptrek.cli.interactive.init_command")
    def test_workflow_init_with_existing_and_generate(
        self, mock_init, mock_echo, tmp_path
    ):
        """Test init workflow with existing config, overwrite, and generate."""
        import os

        os.chdir(tmp_path)

        # Create existing config
        config_file = tmp_path / "project.promptrek.yaml"
        config_file.write_text("old content")

        ctx = Mock()
        ctx.obj = {"verbose": False}

        with patch("promptrek.cli.interactive.questionary.select") as mock_select:
            with patch("promptrek.cli.interactive.questionary.confirm") as mock_confirm:
                with patch(
                    "promptrek.cli.interactive.workflow_generate_config"
                ) as mock_workflow:
                    mock_select.return_value.ask.return_value = "v3"
                    confirm_returns = [
                        Mock(ask=Mock(return_value=True)),  # overwrite
                        Mock(ask=Mock(return_value=True)),  # setup_hooks
                        Mock(ask=Mock(return_value=True)),  # config_gitignore
                        Mock(ask=Mock(return_value=True)),  # generate_now
                    ]
                    mock_confirm.side_effect = confirm_returns

                    from promptrek.cli.interactive import workflow_init_project

                    workflow_init_project(ctx)

                    # Verify init was called
                    mock_init.assert_called_once()
                    # Verify generate workflow was triggered
                    mock_workflow.assert_called_once_with(ctx)

    @patch("click.echo")
    @patch("promptrek.cli.commands.sync.sync_command")
    def test_workflow_sync_with_file_selection(self, mock_sync, mock_echo, tmp_path):
        """Test sync workflow with file selection."""
        import os

        os.chdir(tmp_path)

        # Create an editor file to sync from
        claude_dir = tmp_path / ".claude"
        claude_dir.mkdir()
        (claude_dir / "CLAUDE.md").write_text("# Test content")

        ctx = Mock()
        ctx.obj = {"verbose": False}

        with patch("promptrek.cli.interactive.questionary.select") as mock_select:
            with patch("promptrek.cli.interactive.questionary.confirm") as mock_confirm:
                with patch("promptrek.cli.interactive.questionary.text") as mock_text:
                    # User selects claude editor, confirms auto-detect, enters output file
                    mock_select.return_value.ask.return_value = "claude"
                    mock_confirm.return_value.ask.return_value = True  # auto-detect
                    mock_text.return_value.ask.return_value = "project.promptrek.yaml"

                    from promptrek.cli.interactive import workflow_sync

                    workflow_sync(ctx)

                    # Verify sync was called with correct editor
                    mock_sync.assert_called_once()
                    call_args = mock_sync.call_args
                    assert call_args[1]["editor"] == "claude"

    @patch("click.echo")
    @patch("promptrek.cli.commands.sync.sync_command")
    def test_workflow_sync_success_message(self, mock_sync, mock_echo, tmp_path):
        """Test sync workflow shows success message on completion."""
        import os

        os.chdir(tmp_path)

        # Create an editor file to sync from
        claude_dir = tmp_path / ".claude"
        claude_dir.mkdir()
        (claude_dir / "CLAUDE.md").write_text("# Test content")

        ctx = Mock()
        ctx.obj = {"verbose": False}

        # Make sync_command succeed (no exception)
        mock_sync.return_value = None

        with patch("promptrek.cli.interactive.questionary.select") as mock_select:
            with patch("promptrek.cli.interactive.questionary.confirm") as mock_confirm:
                with patch("promptrek.cli.interactive.questionary.text") as mock_text:
                    mock_select.return_value.ask.return_value = "claude"
                    mock_confirm.return_value.ask.return_value = True
                    mock_text.return_value.ask.return_value = "project.promptrek.yaml"

                    from promptrek.cli.interactive import workflow_sync

                    workflow_sync(ctx)

                    # Verify success message was shown
                    success_calls = [
                        call
                        for call in mock_echo.call_args_list
                        if "completed successfully" in str(call)
                    ]
                    assert len(success_calls) > 0

    @patch("click.echo")
    @patch("promptrek.cli.commands.sync.sync_command")
    def test_workflow_sync_verbose_exception(self, mock_sync, mock_echo, tmp_path):
        """Test sync workflow with exception in verbose mode (should re-raise)."""
        import os

        os.chdir(tmp_path)

        # Create an editor file to sync from
        claude_dir = tmp_path / ".claude"
        claude_dir.mkdir()
        (claude_dir / "CLAUDE.md").write_text("# Test content")

        ctx = Mock()
        ctx.obj = {"verbose": True}  # Verbose mode

        # Make sync raise a generic exception
        mock_sync.side_effect = Exception("Sync failed")

        with patch("promptrek.cli.interactive.questionary.select") as mock_select:
            with patch("promptrek.cli.interactive.questionary.confirm") as mock_confirm:
                with patch("promptrek.cli.interactive.questionary.text") as mock_text:
                    mock_select.return_value.ask.return_value = "claude"
                    mock_confirm.return_value.ask.return_value = True
                    mock_text.return_value.ask.return_value = "project.promptrek.yaml"

                    from promptrek.cli.interactive import workflow_sync

                    # In verbose mode, should re-raise the exception
                    with pytest.raises(Exception, match="Sync failed"):
                        workflow_sync(ctx)

    @patch("click.echo")
    @patch("promptrek.cli.interactive.init_command")
    def test_workflow_init_cancelled_at_setup_hooks(
        self, mock_init, mock_echo, tmp_path
    ):
        """Test init workflow when user cancels at setup hooks prompt."""
        import os

        os.chdir(tmp_path)

        ctx = Mock()
        ctx.obj = {"verbose": False}

        with patch("promptrek.cli.interactive.questionary.select") as mock_select:
            with patch("promptrek.cli.interactive.questionary.confirm") as mock_confirm:
                mock_select.return_value.ask.return_value = "v3"
                # User cancels at setup_hooks prompt (returns None)
                mock_confirm.return_value.ask.return_value = None

                from promptrek.cli.interactive import workflow_init_project

                workflow_init_project(ctx)

                # Init should not have been called
                mock_init.assert_not_called()
                # Should have printed "Cancelled."
                cancelled_calls = [
                    call
                    for call in mock_echo.call_args_list
                    if "Cancelled" in str(call)
                ]
                assert len(cancelled_calls) > 0

    @patch("click.echo")
    @patch("promptrek.cli.interactive.init_command")
    def test_workflow_init_cancelled_at_gitignore(self, mock_init, mock_echo, tmp_path):
        """Test init workflow when user cancels at gitignore prompt."""
        import os

        os.chdir(tmp_path)

        ctx = Mock()
        ctx.obj = {"verbose": False}

        with patch("promptrek.cli.interactive.questionary.select") as mock_select:
            with patch("promptrek.cli.interactive.questionary.confirm") as mock_confirm:
                mock_select.return_value.ask.return_value = "v3"
                # User confirms setup_hooks, then cancels at gitignore prompt
                confirm_returns = [
                    Mock(ask=Mock(return_value=True)),  # setup_hooks
                    Mock(ask=Mock(return_value=None)),  # config_gitignore (cancelled)
                ]
                mock_confirm.side_effect = confirm_returns

                from promptrek.cli.interactive import workflow_init_project

                workflow_init_project(ctx)

                # Init should not have been called
                mock_init.assert_not_called()
                # Should have printed "Cancelled."
                cancelled_calls = [
                    call
                    for call in mock_echo.call_args_list
                    if "Cancelled" in str(call)
                ]
                assert len(cancelled_calls) > 0
