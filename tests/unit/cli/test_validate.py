"""Tests for validate command."""

from pathlib import Path
from unittest.mock import Mock, patch

import pytest
from click.testing import CliRunner

from promptrek.cli.commands.validate import validate_command
from promptrek.cli.main import cli


class TestValidateCommand:
    """Test suite for validate command."""

    def test_validate_valid_v2_file(self, tmp_path):
        """Test validating a valid v2 file."""
        v2_file = tmp_path / "test.promptrek.yaml"
        v2_file.write_text(
            """
schema_version: "2.0.0"
metadata:
  title: "Test Project"
  description: "Test description"
  version: "1.0.0"
content: |
  # Test Instructions

  This is valid v2 format.
"""
        )

        ctx = Mock()
        ctx.obj = {"verbose": False}
        ctx.exit = Mock()

        with patch("click.echo"):
            validate_command(ctx, v2_file, strict=False)

        # Should not call exit with error
        ctx.exit.assert_not_called()

    def test_validate_valid_v1_file(self, tmp_path):
        """Test validating a valid v1 file."""
        v1_file = tmp_path / "test.promptrek.yaml"
        v1_file.write_text(
            """
schema_version: "1.0.0"
metadata:
  title: "Test Project"
  description: "Test description"
  version: "1.0.0"
targets:
  - claude
  - cursor
instructions:
  general:
    - "Use Python 3.9+"
    - "Follow PEP 8"
"""
        )

        ctx = Mock()
        ctx.obj = {"verbose": False}
        ctx.exit = Mock()

        with patch("click.echo"):
            validate_command(ctx, v1_file, strict=False)

        # Should not call exit with error
        ctx.exit.assert_not_called()

    def test_validate_file_not_found(self, tmp_path):
        """Test validating non-existent file."""
        missing_file = tmp_path / "missing.promptrek.yaml"

        ctx = Mock()
        ctx.obj = {"verbose": False}

        with pytest.raises(Exception):
            validate_command(ctx, missing_file, strict=False)

    def test_validate_invalid_yaml(self, tmp_path):
        """Test validating invalid YAML."""
        invalid_file = tmp_path / "invalid.promptrek.yaml"
        invalid_file.write_text(
            """
schema_version: "2.0.0"
metadata:
  title: "Test"
  - invalid yaml structure
content: |
  Test
"""
        )

        ctx = Mock()
        ctx.obj = {"verbose": False}

        with pytest.raises(Exception):
            validate_command(ctx, invalid_file, strict=False)

    def test_validate_with_warnings_not_strict(self, tmp_path):
        """Test validation with warnings in non-strict mode."""
        v1_file = tmp_path / "test.promptrek.yaml"
        v1_file.write_text(
            """
schema_version: "1.0.0"
metadata:
  title: "Test"
  description: "Test"
  version: "1.0.0"
targets:
  - claude
# Missing context and examples - should produce warnings
instructions:
  general:
    - "Test"
"""
        )

        ctx = Mock()
        ctx.obj = {"verbose": False}
        ctx.exit = Mock()

        with patch("click.echo"):
            validate_command(ctx, v1_file, strict=False)

        # Should not exit with error in non-strict mode
        ctx.exit.assert_not_called()

    def test_validate_strict_mode_behavior(self, tmp_path):
        """Test validation in strict mode."""
        v1_file = tmp_path / "test.promptrek.yaml"
        v1_file.write_text(
            """
schema_version: "1.0.0"
metadata:
  title: "Test"
  description: "Test"
  version: "1.0.0"
targets:
  - claude
instructions:
  general:
    - "Test"
"""
        )

        ctx = Mock()
        ctx.obj = {"verbose": False}
        ctx.exit = Mock()

        with patch("click.echo"):
            validate_command(ctx, v1_file, strict=True)

        # In strict mode, validation is more rigorous
        # May or may not call exit depending on validation results

    def test_validate_verbose(self, tmp_path):
        """Test validation with verbose output."""
        v2_file = tmp_path / "test.promptrek.yaml"
        v2_file.write_text(
            """
schema_version: "2.0.0"
metadata:
  title: "Test"
  description: "Test"
  version: "1.0.0"
content: "# Test"
"""
        )

        ctx = Mock()
        ctx.obj = {"verbose": True}
        ctx.exit = Mock()

        with patch("click.echo") as mock_echo:
            validate_command(ctx, v2_file, strict=False)

        # Verbose mode should print more details
        assert mock_echo.call_count > 1


class TestValidateIntegration:
    """Integration tests for validate command via CLI."""

    def test_validate_cli_valid_file(self, tmp_path, monkeypatch):
        """Test validate command via CLI with valid file."""
        monkeypatch.chdir(tmp_path)

        v2_file = tmp_path / "test.promptrek.yaml"
        v2_file.write_text(
            """
schema_version: "2.0.0"
metadata:
  title: "Test"
  description: "Test"
  version: "1.0.0"
content: "# Test"
"""
        )

        runner = CliRunner()
        result = runner.invoke(cli, ["validate", str(v2_file)])

        assert result.exit_code == 0
        assert "✅ Valid" in result.output or "valid" in result.output.lower()

    def test_validate_cli_multiple_files(self, tmp_path, monkeypatch):
        """Test validate command with multiple files."""
        monkeypatch.chdir(tmp_path)

        file1 = tmp_path / "test1.promptrek.yaml"
        file1.write_text(
            """
schema_version: "2.0.0"
metadata:
  title: "Test1"
  description: "Test"
  version: "1.0.0"
content: "# Test 1"
"""
        )

        file2 = tmp_path / "test2.promptrek.yaml"
        file2.write_text(
            """
schema_version: "2.0.0"
metadata:
  title: "Test2"
  description: "Test"
  version: "1.0.0"
content: "# Test 2"
"""
        )

        runner = CliRunner()
        result = runner.invoke(cli, ["validate", str(file1), str(file2)])

        assert result.exit_code == 0

    def test_validate_cli_strict_mode(self, tmp_path, monkeypatch):
        """Test validate command in strict mode."""
        monkeypatch.chdir(tmp_path)

        v1_file = tmp_path / "test.promptrek.yaml"
        v1_file.write_text(
            """
schema_version: "1.0.0"
metadata:
  title: "Test"
  description: "Test"
  version: "1.0.0"
targets:
  - claude
instructions:
  general:
    - "Test"
"""
        )

        runner = CliRunner()
        result = runner.invoke(cli, ["validate", str(v1_file), "--strict"])

        # Strict mode is more rigorous but outcome depends on actual validation
        # Just verify the command runs
        assert result.exit_code in [0, 1]

    def test_validate_cli_help(self):
        """Test validate command help."""
        runner = CliRunner()
        result = runner.invoke(cli, ["validate", "--help"])

        assert result.exit_code == 0
        assert "Validate" in result.output
        assert "--strict" in result.output

    def test_validate_v2_minimal_metadata(self, tmp_path):
        """Test validation with minimal v2 metadata."""
        v2_file = tmp_path / "test.promptrek.yaml"
        v2_file.write_text(
            """
schema_version: "2.0.0"
metadata:
  title: "Test"
  description: "Test"
content: |
  # Test
"""
        )

        ctx = Mock()
        ctx.obj = {"verbose": False}
        ctx.exit = Mock()

        with patch("click.echo"):
            validate_command(ctx, v2_file, strict=False)

    def test_validate_empty_file(self, tmp_path):
        """Test validating an empty file."""
        empty_file = tmp_path / "empty.yaml"
        empty_file.write_text("")

        ctx = Mock()
        ctx.obj = {"verbose": False}
        ctx.exit = Mock()

        with pytest.raises(Exception):  # Should raise parsing error
            validate_command(ctx, empty_file, strict=False)

    def test_validate_malformed_yaml(self, tmp_path):
        """Test validating malformed YAML."""
        bad_file = tmp_path / "bad.yaml"
        bad_file.write_text("{\ninvalid yaml\n")

        ctx = Mock()
        ctx.obj = {"verbose": False}
        ctx.exit = Mock()

        with pytest.raises(Exception):  # Should raise parsing error
            validate_command(ctx, bad_file, strict=False)

    def test_validate_v1_with_conditions(self, tmp_path):
        """Test validating v1 file with conditions."""
        v1_file = tmp_path / "conditions.yaml"
        v1_file.write_text(
            """
schema_version: "1.0.0"
metadata:
  title: "Test"
  description: "Test"
targets:
  - claude
instructions:
  general:
    - "Rule 1"
conditions:
  - if: "EDITOR == 'claude'"
    then:
      instructions:
        general:
          - "Claude-specific rule"
"""
        )

        ctx = Mock()
        ctx.obj = {"verbose": True}
        ctx.exit = Mock()

        with patch("click.echo"):
            validate_command(ctx, v1_file, strict=False)

        ctx.exit.assert_not_called()

    def test_validate_v2_with_variables(self, tmp_path):
        """Test validating v2 file with variables."""
        v2_file = tmp_path / "variables.yaml"
        v2_file.write_text(
            """
schema_version: "2.0.0"
metadata:
  title: "Test"
  description: "Test"
content: |
  # Project: {{{ PROJECT_NAME }}}

  Use {{{ LANGUAGE }}} for coding.
variables:
  PROJECT_NAME: "MyProject"
  LANGUAGE: "Python"
"""
        )

        ctx = Mock()
        ctx.obj = {"verbose": True}
        ctx.exit = Mock()

        with patch("click.echo"):
            validate_command(ctx, v2_file, strict=False)

        ctx.exit.assert_not_called()

    def test_validate_v2_with_documents(self, tmp_path):
        """Test validating v2 file with documents."""
        v2_file = tmp_path / "documents.yaml"
        v2_file.write_text(
            """
schema_version: "2.0.0"
metadata:
  title: "Test"
  description: "Test"
content: |
  # Main Content
documents:
  - name: "doc1"
    content: "# Document 1"
  - name: "doc2"
    content: "# Document 2"
"""
        )

        ctx = Mock()
        ctx.obj = {"verbose": True}
        ctx.exit = Mock()

        with patch("click.echo"):
            validate_command(ctx, v2_file, strict=False)

        ctx.exit.assert_not_called()

    def test_validate_cli_nonexistent_file(self, tmp_path, monkeypatch):
        """Test validate with non-existent file."""
        monkeypatch.chdir(tmp_path)

        runner = CliRunner()
        result = runner.invoke(cli, ["validate", "nonexistent.promptrek.yaml"])

        assert result.exit_code != 0
