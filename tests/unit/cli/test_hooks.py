"""Tests for hooks commands."""

from pathlib import Path
from unittest.mock import Mock, mock_open, patch

import pytest
import yaml
from click.testing import CliRunner

from promptrek.cli.commands.hooks import check_generated_command, install_hooks_command
from promptrek.cli.main import cli
from promptrek.core.exceptions import PrompTrekError


class TestCheckGeneratedCommand:
    """Test check_generated_command function."""

    def test_check_no_generated_files(self):
        """Test with no generated files."""
        ctx = Mock()
        ctx.obj = {"verbose": False}
        ctx.exit = Mock()

        files = ["src/main.py", "README.md", "project.promptrek.yaml"]

        # Should not exit
        check_generated_command(ctx, files)
        ctx.exit.assert_not_called()

    def test_check_with_generated_files(self):
        """Test with generated files detected."""
        ctx = Mock()
        ctx.obj = {"verbose": False}
        ctx.exit = Mock()

        files = [
            ".github/copilot-instructions.md",
            ".cursor/rules/index.mdc",
            "src/main.py",
        ]

        with patch("click.echo") as mock_echo:
            check_generated_command(ctx, files)

            # Should call exit with error code
            ctx.exit.assert_called_once_with(1)

            # Should echo error messages
            assert mock_echo.called
            # Check that error message was displayed
            calls = [str(call) for call in mock_echo.call_args_list]
            assert any("ERROR" in str(call) for call in calls)

    def test_check_cursor_files(self):
        """Test detection of Cursor generated files."""
        ctx = Mock()
        ctx.obj = {"verbose": False}
        ctx.exit = Mock()

        files = [".cursor/rules/typescript.mdc", ".cursorignore", "AGENTS.md"]

        with patch("click.echo"):
            check_generated_command(ctx, files)
            ctx.exit.assert_called_once_with(1)

    def test_check_continue_files(self):
        """Test detection of Continue generated files."""
        ctx = Mock()
        ctx.obj = {"verbose": False}
        ctx.exit = Mock()

        files = ["config.yaml", ".continue/rules/python.md"]

        with patch("click.echo"):
            check_generated_command(ctx, files)
            ctx.exit.assert_called_once_with(1)

    def test_check_claude_files(self):
        """Test detection of Claude generated files."""
        ctx = Mock()
        ctx.obj = {"verbose": False}
        ctx.exit = Mock()

        files = [".claude/context.md", "CLAUDE.md"]

        with patch("click.echo"):
            check_generated_command(ctx, files)
            ctx.exit.assert_called_once_with(1)

    def test_check_pattern_matching(self):
        """Test wildcard pattern matching."""
        ctx = Mock()
        ctx.obj = {"verbose": False}
        ctx.exit = Mock()

        files = [
            ".github/instructions/backend.instructions.md",
            ".github/prompts/feature.prompt.md",
        ]

        with patch("click.echo"):
            check_generated_command(ctx, files)
            ctx.exit.assert_called_once_with(1)

    def test_check_windows_paths(self):
        """Test Windows-style backslash paths are handled correctly."""
        ctx = Mock()
        ctx.obj = {"verbose": False}
        ctx.exit = Mock()

        # Windows paths with backslashes
        files = [
            ".github\\copilot-instructions.md",
            ".cursor\\rules\\index.mdc",
        ]

        with patch("click.echo"):
            check_generated_command(ctx, files)
            ctx.exit.assert_called_once_with(1)


class TestInstallHooksCommand:
    """Test install_hooks_command function."""

    def test_install_new_config(self, tmp_path):
        """Test installing hooks in new config file."""
        config_file = tmp_path / ".pre-commit-config.yaml"

        ctx = Mock()
        ctx.obj = {"verbose": False}

        with patch("click.echo") as mock_echo:
            install_hooks_command(ctx, config_file, force=False, activate=False)

            # Config file should be created
            assert config_file.exists()

            # Load and verify content
            with open(config_file) as f:
                config = yaml.safe_load(f)

            assert "repos" in config
            assert len(config["repos"]) == 1
            assert config["repos"][0]["repo"] == "local"
            assert len(config["repos"][0]["hooks"]) == 3

            # Verify hook IDs
            hook_ids = [h["id"] for h in config["repos"][0]["hooks"]]
            assert "promptrek-validate" in hook_ids
            assert "promptrek-prevent-generated" in hook_ids
            assert "promptrek-check-local-vars" in hook_ids

            # Should echo success
            assert mock_echo.called

    def test_install_existing_config_no_promptrek(self, tmp_path):
        """Test installing hooks in existing config without PrompTrek."""
        config_file = tmp_path / ".pre-commit-config.yaml"

        # Create existing config
        existing_config = {
            "repos": [
                {
                    "repo": "https://github.com/pre-commit/pre-commit-hooks",
                    "rev": "v4.0.0",
                    "hooks": [{"id": "trailing-whitespace"}],
                }
            ]
        }

        with open(config_file, "w") as f:
            yaml.dump(existing_config, f)

        ctx = Mock()
        ctx.obj = {"verbose": False}

        with patch("click.echo"):
            install_hooks_command(ctx, config_file, force=False, activate=False)

            # Load and verify content
            with open(config_file) as f:
                config = yaml.safe_load(f)

            assert len(config["repos"]) == 2
            # Original hook should be preserved
            assert config["repos"][0]["repo"] == existing_config["repos"][0]["repo"]
            # PrompTrek hooks should be added
            assert config["repos"][1]["repo"] == "local"

    def test_install_existing_config_with_promptrek(self, tmp_path):
        """Test updating existing PrompTrek hooks."""
        config_file = tmp_path / ".pre-commit-config.yaml"

        # Create config with existing PrompTrek hooks
        existing_config = {
            "repos": [
                {
                    "repo": "local",
                    "hooks": [{"id": "promptrek-validate", "entry": "old entry"}],
                }
            ]
        }

        with open(config_file, "w") as f:
            yaml.dump(existing_config, f)

        ctx = Mock()
        ctx.obj = {"verbose": False}

        # Should prompt for confirmation
        with patch("click.echo"), patch("click.confirm", return_value=True):
            install_hooks_command(ctx, config_file, force=False, activate=False)

            # Load and verify content
            with open(config_file) as f:
                config = yaml.safe_load(f)

            assert len(config["repos"]) == 1
            # Hooks should be updated
            hook_ids = [h["id"] for h in config["repos"][0]["hooks"]]
            assert "promptrek-validate" in hook_ids
            assert "promptrek-prevent-generated" in hook_ids
            assert "promptrek-check-local-vars" in hook_ids
            # Entry should be updated
            validate_hook = next(
                h
                for h in config["repos"][0]["hooks"]
                if h["id"] == "promptrek-validate"
            )
            assert validate_hook["entry"] == "promptrek validate"

    def test_install_with_force(self, tmp_path):
        """Test installing hooks with force flag."""
        config_file = tmp_path / ".pre-commit-config.yaml"

        # Create config with existing PrompTrek hooks
        existing_config = {
            "repos": [
                {
                    "repo": "local",
                    "hooks": [{"id": "promptrek-validate", "entry": "old entry"}],
                }
            ]
        }

        with open(config_file, "w") as f:
            yaml.dump(existing_config, f)

        ctx = Mock()
        ctx.obj = {"verbose": False}

        # Should not prompt with force=True
        with patch("click.echo"), patch("click.confirm") as mock_confirm:
            install_hooks_command(ctx, config_file, force=True, activate=False)

            # Should not ask for confirmation
            mock_confirm.assert_not_called()

            # Hooks should be updated
            with open(config_file) as f:
                config = yaml.safe_load(f)

            hook_ids = [h["id"] for h in config["repos"][0]["hooks"]]
            assert "promptrek-validate" in hook_ids
            assert "promptrek-prevent-generated" in hook_ids
            assert "promptrek-check-local-vars" in hook_ids

    def test_install_decline_update(self, tmp_path):
        """Test declining to update existing hooks."""
        config_file = tmp_path / ".pre-commit-config.yaml"

        # Create config with existing PrompTrek hooks
        existing_config = {
            "repos": [
                {
                    "repo": "local",
                    "hooks": [{"id": "promptrek-validate", "entry": "old entry"}],
                }
            ]
        }

        with open(config_file, "w") as f:
            yaml.dump(existing_config, f)

        ctx = Mock()
        ctx.obj = {"verbose": False}

        # Decline update
        with patch("click.echo"), patch("click.confirm", return_value=False):
            install_hooks_command(ctx, config_file, force=False, activate=False)

            # Hooks should NOT be updated
            with open(config_file) as f:
                config = yaml.safe_load(f)

            # Should still have old entry
            validate_hook = config["repos"][0]["hooks"][0]
            assert validate_hook["id"] == "promptrek-validate"
            assert validate_hook["entry"] == "old entry"

            # Should not have the second hook added
            assert len(config["repos"][0]["hooks"]) == 1

    def test_install_invalid_yaml(self, tmp_path):
        """Test error handling for invalid YAML."""
        config_file = tmp_path / ".pre-commit-config.yaml"
        config_file.write_text("invalid: yaml: content:")

        ctx = Mock()
        ctx.obj = {"verbose": False}

        with pytest.raises(PrompTrekError, match="Failed to read"):
            install_hooks_command(ctx, config_file, force=False, activate=False)

    def test_install_default_config_path(self, tmp_path, monkeypatch):
        """Test using default config path."""
        # Change to tmp directory
        monkeypatch.chdir(tmp_path)

        ctx = Mock()
        ctx.obj = {"verbose": False}

        with patch("click.echo"):
            install_hooks_command(ctx, None, force=False, activate=False)

            # Should create .pre-commit-config.yaml in current directory
            default_config = Path(".pre-commit-config.yaml")
            assert default_config.exists()

    def test_install_with_activate_success(self, tmp_path):
        """Test installing hooks with activation."""
        config_file = tmp_path / ".pre-commit-config.yaml"

        ctx = Mock()
        ctx.obj = {"verbose": False}

        # Mock successful pre-commit install
        mock_run = Mock()
        mock_run.return_value = Mock(stdout="", stderr="", returncode=0)

        with (
            patch("click.echo"),
            patch("shutil.which", return_value="/usr/bin/pre-commit"),
            patch("subprocess.run", mock_run),
        ):
            install_hooks_command(ctx, config_file, force=False, activate=True)

            # Should have called pre-commit install
            mock_run.assert_called_once()
            args = mock_run.call_args[0][0]
            assert args == ["pre-commit", "install"]

    def test_install_with_activate_pre_commit_not_found(self, tmp_path):
        """Test activation fails when pre-commit not installed."""
        config_file = tmp_path / ".pre-commit-config.yaml"

        ctx = Mock()
        ctx.obj = {"verbose": False}

        # Mock pre-commit not found
        with patch("click.echo") as mock_echo, patch("shutil.which", return_value=None):
            install_hooks_command(ctx, config_file, force=False, activate=True)

            # Should call ctx.exit(1)
            ctx.exit.assert_called_once_with(1)

            # Should show error message
            error_calls = [
                call for call in mock_echo.call_args_list if call[1].get("err")
            ]
            assert len(error_calls) > 0

    def test_install_with_activate_pre_commit_fails(self, tmp_path):
        """Test handling of pre-commit install failure."""
        config_file = tmp_path / ".pre-commit-config.yaml"

        ctx = Mock()
        ctx.obj = {"verbose": False}

        # Mock pre-commit install failing
        import subprocess

        mock_run = Mock()
        mock_run.side_effect = subprocess.CalledProcessError(
            1, ["pre-commit", "install"], stderr="Error"
        )

        with (
            patch("click.echo"),
            patch("shutil.which", return_value="/usr/bin/pre-commit"),
            patch("subprocess.run", mock_run),
        ):
            # Should not raise, just show warning
            install_hooks_command(ctx, config_file, force=False, activate=True)

            # Config should still be created
            assert config_file.exists()


class TestHooksIntegration:
    """Integration tests for hooks commands via CLI."""

    def test_install_hooks_cli(self, tmp_path, monkeypatch):
        """Test install-hooks command via CLI."""
        monkeypatch.chdir(tmp_path)

        runner = CliRunner()
        result = runner.invoke(cli, ["install-hooks"])

        assert result.exit_code == 0
        assert Path(".pre-commit-config.yaml").exists()

    def test_install_hooks_cli_with_config(self, tmp_path):
        """Test install-hooks command with custom config path."""
        config_file = tmp_path / "custom-config.yaml"

        runner = CliRunner()
        result = runner.invoke(cli, ["install-hooks", "--config", str(config_file)])

        assert result.exit_code == 0
        assert config_file.exists()

    def test_check_generated_cli_clean(self):
        """Test check-generated command with clean files."""
        runner = CliRunner()
        result = runner.invoke(
            cli, ["check-generated", "src/main.py", "project.promptrek.yaml"]
        )

        assert result.exit_code == 0

    def test_check_generated_cli_with_generated(self):
        """Test check-generated command with generated files."""
        runner = CliRunner()
        result = runner.invoke(
            cli, ["check-generated", ".github/copilot-instructions.md"]
        )

        assert result.exit_code == 1
        assert "ERROR" in result.output

    def test_check_generated_cli_no_files(self):
        """Test check-generated command with no files."""
        runner = CliRunner()
        result = runner.invoke(cli, ["check-generated"])

        # Should fail because files argument is required
        assert result.exit_code != 0

    def test_install_hooks_cli_with_activate(self, tmp_path, monkeypatch):
        """Test install-hooks command with --activate flag."""
        monkeypatch.chdir(tmp_path)

        runner = CliRunner()

        # Mock successful pre-commit install
        with (
            patch("shutil.which", return_value="/usr/bin/pre-commit"),
            patch(
                "subprocess.run", return_value=Mock(stdout="", stderr="")
            ) as mock_run,
        ):
            result = runner.invoke(cli, ["install-hooks", "--activate"])

            assert result.exit_code == 0
            assert Path(".pre-commit-config.yaml").exists()

            # Should have called pre-commit install
            mock_run.assert_called_once()
            assert mock_run.call_args[0][0] == ["pre-commit", "install"]
