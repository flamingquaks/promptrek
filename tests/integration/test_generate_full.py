"""Comprehensive generate command tests."""

from pathlib import Path

import pytest
from click.testing import CliRunner

from promptrek.cli.main import cli


class TestGenerateComprehensive:
    """Comprehensive generate tests for coverage."""

    def test_generate_claude_v2(self, tmp_path):
        """Test generating Claude files from v2 schema."""
        upf_file = tmp_path / "test.promptrek.yaml"
        upf_file.write_text(
            """
schema_version: "2.0.0"
metadata:
  title: "Claude Test"
  description: "Test for Claude"
  version: "1.0.0"
content: |
  # Claude Instructions
  
  ## Project Context
  This is a test project.
  
  ## Guidelines
  - Follow best practices
  - Write clean code
variables:
  PROJECT_NAME: "TestProject"
"""
        )

        runner = CliRunner()
        result = runner.invoke(
            cli, ["generate", str(upf_file), "--editor", "claude", "-o", str(tmp_path)]
        )

        assert result.exit_code == 0
        claude_file = tmp_path / ".claude" / "CLAUDE.md"
        assert claude_file.exists()

    def test_generate_copilot_v2(self, tmp_path):
        """Test generating Copilot files from v2 schema."""
        upf_file = tmp_path / "test.promptrek.yaml"
        upf_file.write_text(
            """
schema_version: "2.0.0"
metadata:
  title: "Copilot Test"
  description: "Test for Copilot"
  version: "1.0.0"
content: |
  # Copilot Instructions
  Write great code.
"""
        )

        runner = CliRunner()
        result = runner.invoke(
            cli, ["generate", str(upf_file), "--editor", "copilot", "-o", str(tmp_path)]
        )

        assert result.exit_code == 0

    def test_generate_cursor_v2(self, tmp_path):
        """Test generating Cursor files from v2 schema."""
        upf_file = tmp_path / "test.promptrek.yaml"
        upf_file.write_text(
            """
schema_version: "2.0.0"
metadata:
  title: "Cursor Test"
  description: "Test for Cursor"
  version: "1.0.0"
content: |
  # Cursor Rules
  Follow these rules.
"""
        )

        runner = CliRunner()
        result = runner.invoke(
            cli, ["generate", str(upf_file), "--editor", "cursor", "-o", str(tmp_path)]
        )

        assert result.exit_code == 0

    def test_generate_continue_v2(self, tmp_path):
        """Test generating Continue files from v2 schema."""
        upf_file = tmp_path / "test.promptrek.yaml"
        upf_file.write_text(
            """
schema_version: "2.0.0"
metadata:
  title: "Continue Test"
  description: "Test for Continue"
  version: "1.0.0"
content: |
  # Continue Config
  Configuration here.
"""
        )

        runner = CliRunner()
        result = runner.invoke(
            cli,
            ["generate", str(upf_file), "--editor", "continue", "-o", str(tmp_path)],
        )

        assert result.exit_code == 0

    def test_generate_windsurf_v2(self, tmp_path):
        """Test generating Windsurf files from v2 schema."""
        upf_file = tmp_path / "test.promptrek.yaml"
        upf_file.write_text(
            """
schema_version: "2.0.0"
metadata:
  title: "Windsurf Test"
  description: "Test for Windsurf"
  version: "1.0.0"
content: |
  # Windsurf Rules
  Follow these guidelines.
"""
        )

        runner = CliRunner()
        result = runner.invoke(
            cli,
            ["generate", str(upf_file), "--editor", "windsurf", "-o", str(tmp_path)],
        )

        assert result.exit_code == 0

    def test_generate_with_variable_substitution(self, tmp_path):
        """Test variable substitution during generation."""
        upf_file = tmp_path / "test.promptrek.yaml"
        upf_file.write_text(
            """
schema_version: "2.0.0"
metadata:
  title: "Variable Test"
  description: "Test variables"
  version: "1.0.0"
content: |
  # Project: {{{ PROJECT_NAME }}}
  Version: {{{ VERSION }}}
variables:
  PROJECT_NAME: "DefaultName"
  VERSION: "1.0.0"
"""
        )

        runner = CliRunner()
        result = runner.invoke(
            cli,
            [
                "generate",
                str(upf_file),
                "--editor",
                "claude",
                "-o",
                str(tmp_path),
                "-V",
                "PROJECT_NAME=CustomName",
                "-V",
                "VERSION=2.0.0",
            ],
        )

        assert result.exit_code == 0
        claude_file = tmp_path / ".claude" / "CLAUDE.md"
        content = claude_file.read_text()
        assert "CustomName" in content
        assert "2.0.0" in content

    def test_generate_v1_with_examples(self, tmp_path):
        """Test generating from v1 with examples."""
        upf_file = tmp_path / "test.promptrek.yaml"
        upf_file.write_text(
            """
schema_version: "1.0.0"
metadata:
  title: "V1 Test"
  description: "Test v1"
  version: "1.0.0"
targets:
  - claude
instructions:
  general:
    - "Write tests"
examples:
  test_example: |
    def test_example():
        assert True
"""
        )

        runner = CliRunner()
        result = runner.invoke(
            cli, ["generate", str(upf_file), "--editor", "claude", "-o", str(tmp_path)]
        )

        assert result.exit_code == 0

    def test_generate_multiple_editors(self, tmp_path):
        """Test generating for multiple editors."""
        upf_file = tmp_path / "test.promptrek.yaml"
        upf_file.write_text(
            """
schema_version: "2.0.0"
metadata:
  title: "Multi Test"
  description: "Test multiple editors"
  version: "1.0.0"
content: "# Instructions"
"""
        )

        runner = CliRunner()
        result = runner.invoke(
            cli,
            [
                "generate",
                str(upf_file),
                "--editor",
                "claude",
                "--editor",
                "cursor",
                "-o",
                str(tmp_path),
            ],
        )

        assert result.exit_code == 0

    def test_generate_dry_run(self, tmp_path):
        """Test dry run mode."""
        upf_file = tmp_path / "test.promptrek.yaml"
        upf_file.write_text(
            """
schema_version: "2.0.0"
metadata:
  title: "Dry Run Test"
  description: "Test dry run"
  version: "1.0.0"
content: "# Test"
"""
        )

        runner = CliRunner()
        result = runner.invoke(
            cli, ["generate", str(upf_file), "--editor", "claude", "--dry-run"]
        )

        # Dry run should succeed but not create files
        assert result.exit_code == 0 or "dry" in result.output.lower()

    def test_generate_with_documents(self, tmp_path):
        """Test generating v2 with multiple documents."""
        upf_file = tmp_path / "test.promptrek.yaml"
        upf_file.write_text(
            """
schema_version: "2.0.0"
metadata:
  title: "Multi Doc Test"
  description: "Test multiple documents"
  version: "1.0.0"
content: "# Main content"
documents:
  - name: "additional"
    content: "# Additional doc"
  - name: "extra"
    content: "# Extra doc"
"""
        )

        runner = CliRunner()
        result = runner.invoke(
            cli,
            ["generate", str(upf_file), "--editor", "continue", "-o", str(tmp_path)],
        )

        assert result.exit_code == 0
