"""
Unit tests for config-ignores command.
"""

from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import pytest
from click.testing import CliRunner

from promptrek.cli.commands.config_ignores import (
    _find_config_file,
    config_ignores_command,
)
from promptrek.cli.main import cli
from promptrek.core.exceptions import CLIError


class TestFindConfigFile:
    """Tests for _find_config_file helper function."""

    def test_finds_project_promptrek_yaml(self, tmp_path, monkeypatch):
        """Should find project.promptrek.yaml."""
        monkeypatch.chdir(tmp_path)
        config_file = tmp_path / "project.promptrek.yaml"
        config_file.write_text("schema_version: '2.0.0'")

        result = _find_config_file()
        assert result == config_file

    def test_finds_dot_promptrek_yaml(self, tmp_path, monkeypatch):
        """Should find .promptrek.yaml."""
        monkeypatch.chdir(tmp_path)
        config_file = tmp_path / ".promptrek.yaml"
        config_file.write_text("schema_version: '2.0.0'")

        result = _find_config_file()
        assert result == config_file

    def test_finds_any_promptrek_yaml(self, tmp_path, monkeypatch):
        """Should find any .promptrek.yaml file."""
        monkeypatch.chdir(tmp_path)
        config_file = tmp_path / "myconfig.promptrek.yaml"
        config_file.write_text("schema_version: '2.0.0'")

        result = _find_config_file()
        assert result == config_file

    def test_returns_none_when_no_config_found(self, tmp_path, monkeypatch):
        """Should return None when no config file is found."""
        monkeypatch.chdir(tmp_path)

        result = _find_config_file()
        assert result is None

    def test_prioritizes_project_promptrek_yaml(self, tmp_path, monkeypatch):
        """Should prioritize project.promptrek.yaml over other names."""
        monkeypatch.chdir(tmp_path)
        (tmp_path / "project.promptrek.yaml").write_text("schema_version: '2.0.0'")
        (tmp_path / "other.promptrek.yaml").write_text("schema_version: '2.0.0'")

        result = _find_config_file()
        assert result.name == "project.promptrek.yaml"


class TestConfigIgnoresCommand:
    """Tests for config_ignores_command function."""

    @patch("promptrek.cli.commands.config_ignores.configure_gitignore")
    @patch("promptrek.cli.commands.config_ignores.UPFParser")
    def test_raises_error_when_no_config_file_found(self, mock_parser, mock_config):
        """Should raise error when no config file is found."""
        ctx = MagicMock()

        with pytest.raises(CLIError) as exc_info:
            config_ignores_command(ctx, config_file=None, remove_cached=False, dry_run=False)

        assert "No PrompTrek config file found" in str(exc_info.value)

    @patch("promptrek.cli.commands.config_ignores.configure_gitignore")
    @patch("promptrek.cli.commands.config_ignores.UPFParser")
    def test_raises_error_when_config_file_not_exists(self, mock_parser, mock_config, tmp_path):
        """Should raise error when specified config file doesn't exist."""
        ctx = MagicMock()
        config_file = tmp_path / "nonexistent.promptrek.yaml"

        with pytest.raises(CLIError) as exc_info:
            config_ignores_command(ctx, config_file=config_file, remove_cached=False, dry_run=False)

        assert "Config file not found" in str(exc_info.value)

    @patch("promptrek.cli.commands.config_ignores.configure_gitignore")
    @patch("promptrek.cli.commands.config_ignores.UPFParser")
    def test_configures_gitignore_successfully(self, mock_parser, mock_config, tmp_path):
        """Should configure .gitignore successfully."""
        ctx = MagicMock()
        config_file = tmp_path / "project.promptrek.yaml"
        config_file.write_text("schema_version: '2.0.0'\nmetadata:\n  title: Test")

        # Mock parser to return a prompt with ignore_editor_files=True
        mock_prompt = Mock()
        mock_prompt.ignore_editor_files = True
        mock_parser_instance = Mock()
        mock_parser_instance.parse_file.return_value = mock_prompt
        mock_parser.return_value = mock_parser_instance

        # Mock configure_gitignore to return success
        mock_config.return_value = {"patterns_added": 5, "files_removed": []}

        config_ignores_command(ctx, config_file=config_file, remove_cached=False, dry_run=False)

        assert mock_config.called
        call_args = mock_config.call_args
        assert call_args[0][0] == tmp_path  # project_dir
        assert call_args[1]["add_editor_files"] is True
        assert call_args[1]["remove_cached"] is False

    @patch("promptrek.cli.commands.config_ignores.configure_gitignore")
    @patch("promptrek.cli.commands.config_ignores.UPFParser")
    @patch("click.confirm")
    def test_warns_when_ignore_editor_files_is_false(
        self, mock_confirm, mock_parser, mock_config, tmp_path
    ):
        """Should warn when ignore_editor_files is False."""
        ctx = MagicMock()
        config_file = tmp_path / "project.promptrek.yaml"
        config_file.write_text("schema_version: '2.0.0'\nmetadata:\n  title: Test")

        # Mock parser to return a prompt with ignore_editor_files=False
        mock_prompt = Mock()
        mock_prompt.ignore_editor_files = False
        mock_parser_instance = Mock()
        mock_parser_instance.parse_file.return_value = mock_prompt
        mock_parser.return_value = mock_parser_instance

        # Mock user declining to continue
        mock_confirm.return_value = False

        config_ignores_command(ctx, config_file=config_file, remove_cached=False, dry_run=False)

        assert mock_confirm.called
        # Should not call configure_gitignore if user declines
        assert not mock_config.called

    @patch("promptrek.cli.commands.config_ignores.configure_gitignore")
    @patch("promptrek.cli.commands.config_ignores.UPFParser")
    def test_removes_cached_files_when_requested(self, mock_parser, mock_config, tmp_path):
        """Should remove cached files when remove_cached is True."""
        ctx = MagicMock()
        config_file = tmp_path / "project.promptrek.yaml"
        config_file.write_text("schema_version: '2.0.0'\nmetadata:\n  title: Test")

        # Mock parser
        mock_prompt = Mock()
        mock_prompt.ignore_editor_files = True
        mock_parser_instance = Mock()
        mock_parser_instance.parse_file.return_value = mock_prompt
        mock_parser.return_value = mock_parser_instance

        # Mock configure_gitignore with files removed
        mock_config.return_value = {
            "patterns_added": 5,
            "files_removed": ["file1.md", "file2.md"],
        }

        config_ignores_command(ctx, config_file=config_file, remove_cached=True, dry_run=False)

        call_args = mock_config.call_args
        assert call_args[1]["remove_cached"] is True

    @patch("promptrek.cli.commands.config_ignores.configure_gitignore")
    @patch("promptrek.cli.commands.config_ignores.UPFParser")
    def test_dry_run_mode_does_not_make_changes(self, mock_parser, mock_config, tmp_path):
        """Should not make changes in dry-run mode."""
        ctx = MagicMock()
        config_file = tmp_path / "project.promptrek.yaml"
        config_file.write_text("schema_version: '2.0.0'\nmetadata:\n  title: Test")

        # Mock parser
        mock_prompt = Mock()
        mock_prompt.ignore_editor_files = True
        mock_parser_instance = Mock()
        mock_parser_instance.parse_file.return_value = mock_prompt
        mock_parser.return_value = mock_parser_instance

        config_ignores_command(ctx, config_file=config_file, remove_cached=True, dry_run=True)

        # Should not call configure_gitignore in dry-run mode
        assert not mock_config.called

    @patch("promptrek.cli.commands.config_ignores.configure_gitignore")
    @patch("promptrek.cli.commands.config_ignores.UPFParser")
    def test_raises_error_on_parse_failure(self, mock_parser, mock_config, tmp_path):
        """Should raise error when parsing config file fails."""
        ctx = MagicMock()
        config_file = tmp_path / "project.promptrek.yaml"
        config_file.write_text("invalid yaml content {")

        # Mock parser to raise exception
        mock_parser_instance = Mock()
        mock_parser_instance.parse_file.side_effect = Exception("Parse error")
        mock_parser.return_value = mock_parser_instance

        with pytest.raises(CLIError) as exc_info:
            config_ignores_command(ctx, config_file=config_file, remove_cached=False, dry_run=False)

        assert "Failed to parse config file" in str(exc_info.value)


class TestConfigIgnoresCLI:
    """Integration tests for config-ignores CLI command."""

    def test_cli_config_ignores_help(self):
        """Should display help for config-ignores command."""
        runner = CliRunner()
        result = runner.invoke(cli, ["config-ignores", "--help"])

        assert result.exit_code == 0
        assert "Configure .gitignore to exclude editor-specific files" in result.output

    @patch("promptrek.cli.commands.config_ignores.configure_gitignore")
    @patch("promptrek.cli.commands.config_ignores._find_config_file")
    @patch("promptrek.cli.commands.config_ignores.UPFParser")
    def test_cli_config_ignores_basic(self, mock_parser, mock_find, mock_config, tmp_path):
        """Should run config-ignores command successfully."""
        runner = CliRunner()

        # Mock finding config file
        config_file = tmp_path / "project.promptrek.yaml"
        config_file.write_text("schema_version: '2.0.0'\nmetadata:\n  title: Test")
        mock_find.return_value = config_file

        # Mock parser
        mock_prompt = Mock()
        mock_prompt.ignore_editor_files = True
        mock_parser_instance = Mock()
        mock_parser_instance.parse_file.return_value = mock_prompt
        mock_parser.return_value = mock_parser_instance

        # Mock configure_gitignore
        mock_config.return_value = {"patterns_added": 5, "files_removed": []}

        result = runner.invoke(cli, ["config-ignores"])

        assert result.exit_code == 0
        assert mock_config.called

    @patch("promptrek.cli.commands.config_ignores.configure_gitignore")
    @patch("promptrek.cli.commands.config_ignores.UPFParser")
    def test_cli_config_ignores_with_config_option(self, mock_parser, mock_config, tmp_path):
        """Should accept --config option."""
        runner = CliRunner()

        config_file = tmp_path / "custom.promptrek.yaml"
        config_file.write_text("schema_version: '2.0.0'\nmetadata:\n  title: Test")

        # Mock parser
        mock_prompt = Mock()
        mock_prompt.ignore_editor_files = True
        mock_parser_instance = Mock()
        mock_parser_instance.parse_file.return_value = mock_prompt
        mock_parser.return_value = mock_parser_instance

        # Mock configure_gitignore
        mock_config.return_value = {"patterns_added": 3, "files_removed": []}

        result = runner.invoke(cli, ["config-ignores", "--config", str(config_file)])

        assert result.exit_code == 0
        assert mock_config.called

    @patch("promptrek.cli.commands.config_ignores.configure_gitignore")
    @patch("promptrek.cli.commands.config_ignores._find_config_file")
    @patch("promptrek.cli.commands.config_ignores.UPFParser")
    def test_cli_config_ignores_dry_run(self, mock_parser, mock_find, mock_config, tmp_path):
        """Should support --dry-run option."""
        runner = CliRunner()

        config_file = tmp_path / "project.promptrek.yaml"
        config_file.write_text("schema_version: '2.0.0'\nmetadata:\n  title: Test")
        mock_find.return_value = config_file

        # Mock parser
        mock_prompt = Mock()
        mock_prompt.ignore_editor_files = True
        mock_parser_instance = Mock()
        mock_parser_instance.parse_file.return_value = mock_prompt
        mock_parser.return_value = mock_parser_instance

        result = runner.invoke(cli, ["config-ignores", "--dry-run"])

        assert result.exit_code == 0
        assert "Dry run mode" in result.output
        # Should not call configure_gitignore in dry-run
        assert not mock_config.called

    @patch("promptrek.cli.commands.config_ignores.configure_gitignore")
    @patch("promptrek.cli.commands.config_ignores._find_config_file")
    @patch("promptrek.cli.commands.config_ignores.UPFParser")
    def test_cli_config_ignores_remove_cached(self, mock_parser, mock_find, mock_config, tmp_path):
        """Should support --remove-cached option."""
        runner = CliRunner()

        config_file = tmp_path / "project.promptrek.yaml"
        config_file.write_text("schema_version: '2.0.0'\nmetadata:\n  title: Test")
        mock_find.return_value = config_file

        # Mock parser
        mock_prompt = Mock()
        mock_prompt.ignore_editor_files = True
        mock_parser_instance = Mock()
        mock_parser_instance.parse_file.return_value = mock_prompt
        mock_parser.return_value = mock_parser_instance

        # Mock configure_gitignore with files removed
        mock_config.return_value = {
            "patterns_added": 5,
            "files_removed": ["file1.md", "file2.md"],
        }

        result = runner.invoke(cli, ["config-ignores", "--remove-cached"])

        assert result.exit_code == 0
        call_args = mock_config.call_args
        assert call_args[1]["remove_cached"] is True
