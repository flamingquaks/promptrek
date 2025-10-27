"""
Tests for interactive CLI wizard.
"""

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

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
