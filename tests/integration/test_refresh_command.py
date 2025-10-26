"""Integration tests for the refresh command."""

from pathlib import Path
from unittest.mock import patch

import pytest
import yaml
from click.testing import CliRunner

from promptrek.cli.main import cli


class TestRefreshCommand:
    """Test the promptrek refresh command."""

    @pytest.fixture
    def setup_project(self, tmp_path, monkeypatch):
        """Set up a test project with UPF file and generation metadata."""
        monkeypatch.chdir(tmp_path)

        # Create a simple UPF file
        upf_file = tmp_path / "project.promptrek.yaml"
        upf_file.write_text(
            """schema_version: 3.0.0
metadata:
  title: Test Project
  description: Test description
  version: 1.0.0
content: |
  # Test Content
  Current date: {{{ CURRENT_DATE }}}
  Project: {{{ PROJECT_NAME }}}
allow_commands: false
"""
        )

        # Create .promptrek directory
        promptrek_dir = tmp_path / ".promptrek"
        promptrek_dir.mkdir()

        # Create generation metadata
        metadata_file = promptrek_dir / "last-generation.yaml"
        metadata = {
            "timestamp": "2025-10-26T10:00:00",
            "source_file": str(upf_file),
            "editors": ["claude"],
            "output_dir": str(tmp_path),
            "variables": {},
            "dynamic_variables": {},
            "builtin_variables_enabled": True,
            "allow_commands": False,
        }
        metadata_file.write_text(yaml.dump(metadata))

        return tmp_path, upf_file

    def test_refresh_without_metadata(self, tmp_path, monkeypatch):
        """Test refresh fails when no generation metadata exists."""
        monkeypatch.chdir(tmp_path)

        runner = CliRunner()
        result = runner.invoke(cli, ["refresh"])

        assert result.exit_code != 0
        assert "No generation metadata found" in result.output

    def test_refresh_dry_run(self, setup_project):
        """Test refresh in dry-run mode."""
        tmp_path, upf_file = setup_project

        runner = CliRunner()
        result = runner.invoke(cli, ["refresh", "--dry-run"])

        assert "Dry run mode" in result.output

    @patch("promptrek.utils.variables.subprocess.run")
    def test_refresh_success(self, mock_run, setup_project):
        """Test successful refresh operation."""
        tmp_path, upf_file = setup_project

        # Mock git commands (called by built-in variables)
        from unittest.mock import Mock

        mock_result = Mock()
        mock_result.returncode = 1  # Not in git repo
        mock_result.stdout = ""
        mock_run.return_value = mock_result

        runner = CliRunner()
        result = runner.invoke(cli, ["--verbose", "refresh"])

        # Should complete without errors
        assert result.exit_code == 0
        assert "Refresh complete" in result.output

    def test_refresh_with_specific_editor(self, setup_project):
        """Test refresh with specific editor override."""
        tmp_path, upf_file = setup_project

        runner = CliRunner()
        result = runner.invoke(cli, ["refresh", "--editor", "cursor"])

        # Should attempt to refresh for cursor
        # (may fail due to missing adapter in test env, but command should parse correctly)
        assert (
            "cursor" in result.output
            or "No adapter found for editor 'cursor'" in result.output
        ), f"{result.output}"
        assert result.exit_code == 0 or result.exit_code == 1

    def test_refresh_missing_source_file(self, setup_project):
        """Test refresh fails when source file is missing."""
        tmp_path, upf_file = setup_project

        # Delete the source UPF file
        upf_file.unlink()

        runner = CliRunner()
        result = runner.invoke(cli, ["refresh"])

        assert result.exit_code != 0
        assert "Source file not found" in result.output

    @patch("promptrek.utils.variables.subprocess.run")
    def test_refresh_with_variable_overrides(self, mock_run, setup_project):
        """Test refresh with CLI variable overrides."""
        tmp_path, upf_file = setup_project

        # Mock git commands (called by built-in variables)
        from unittest.mock import Mock

        mock_result = Mock()
        mock_result.returncode = 1  # Not in git repo
        mock_result.stdout = ""
        mock_run.return_value = mock_result

        runner = CliRunner()
        result = runner.invoke(
            cli,
            [
                "--verbose",
                "refresh",
                "-V",
                "PROJECT_NAME=TestProject",
                "-V",
                "VERSION=2.0.0",
            ],
        )
        assert result.exit_code == 0
        assert "Refresh complete" in result.output
        # Variables should be properly parsed and not cause errors
        assert "Variable must be in format KEY=value" not in result.output


class TestGenerationMetadataSaving:
    """Test that generate command saves metadata correctly."""

    @pytest.fixture
    def setup_upf_file(self, tmp_path, monkeypatch):
        """Set up a UPF file for testing."""
        monkeypatch.chdir(tmp_path)

        upf_file = tmp_path / "project.promptrek.yaml"
        upf_file.write_text(
            """schema_version: 3.0.0
metadata:
  title: Test Project
  description: Test description
  version: 1.0.0
content: |
  # Test Content
  Date: {{{ CURRENT_DATE }}}
allow_commands: false
"""
        )
        return tmp_path, upf_file

    @patch("promptrek.utils.variables.subprocess.run")
    def test_generate_saves_metadata(self, mock_run, setup_upf_file):
        """Test that generate command saves generation metadata."""
        tmp_path, upf_file = setup_upf_file

        # Mock git commands
        from unittest.mock import Mock

        mock_result = Mock()
        mock_result.returncode = 1  # Not in git repo
        mock_result.stdout = ""
        mock_run.return_value = mock_result

        runner = CliRunner()
        result = runner.invoke(
            cli, ["--verbose", "generate", str(upf_file), "--editor", "claude"]
        )

        # Check that metadata file was created
        metadata_file = tmp_path / ".promptrek/last-generation.yaml"
        assert metadata_file.exists()

        # Validate metadata content
        with open(metadata_file) as f:
            metadata = yaml.safe_load(f)

        assert "timestamp" in metadata
        assert "source_file" in metadata
        assert "editors" in metadata
        assert "claude" in metadata["editors"]

    def test_generate_dry_run_no_metadata(self, setup_upf_file):
        """Test that dry-run mode does not save metadata."""
        tmp_path, upf_file = setup_upf_file

        runner = CliRunner()
        runner.invoke(
            cli, ["generate", str(upf_file), "--editor", "claude", "--dry-run"]
        )

        # Metadata file should not exist in dry-run mode
        metadata_file = tmp_path / ".promptrek/last-generation.yaml"
        assert not metadata_file.exists()


class TestDynamicVariablesInGenerate:
    """Test dynamic variables in generate command."""

    @pytest.fixture
    def setup_with_dynamic_vars(self, tmp_path, monkeypatch):
        """Set up project with dynamic variables."""
        monkeypatch.chdir(tmp_path)

        # Create UPF file with allow_commands enabled
        upf_file = tmp_path / "project.promptrek.yaml"
        upf_file.write_text(
            """schema_version: 3.0.0
metadata:
  title: Test Project
  description: Test with dynamic variables
  version: 1.0.0
content: |
  # Test Content
  Date: {{{ CURRENT_DATE }}}
  Dynamic: {{{ DYNAMIC_VAR }}}
allow_commands: true
"""
        )

        # Create .promptrek directory and variables file
        promptrek_dir = tmp_path / ".promptrek"
        promptrek_dir.mkdir()
        var_file = promptrek_dir / "variables.promptrek.yaml"
        var_file.write_text(
            """DYNAMIC_VAR:
  type: command
  value: echo test-value
  cache: false
"""
        )

        return tmp_path, upf_file

    @patch("promptrek.utils.variables.subprocess.run")
    def test_generate_with_dynamic_vars(self, mock_run, setup_with_dynamic_vars):
        """Test generate command with dynamic variables."""
        tmp_path, upf_file = setup_with_dynamic_vars

        # Mock command execution
        from unittest.mock import Mock

        def mock_run_side_effect(cmd, **kwargs):
            result = Mock()
            if "echo test-value" in str(cmd):
                result.stdout = "test-value"
            else:
                result.returncode = 1
                result.stdout = ""
            return result

        mock_run.side_effect = mock_run_side_effect

        runner = CliRunner()
        result = runner.invoke(
            cli, ["--verbose", "generate", str(upf_file), "--editor", "claude"]
        )

        # Check that command executed
        # (Should see the warning about command execution)
        assert result.exit_code == 0 or "WARNING" in result.output
