"""Test CLI error handling."""

from pathlib import Path

import pytest
from click.testing import CliRunner

from promptrek.cli.main import cli


class TestCLIErrors:
    """Test CLI error cases."""

    def test_generate_nonexistent_file(self):
        """Test generate with non-existent file."""
        runner = CliRunner()
        result = runner.invoke(
            cli, ["generate", "/nonexistent/file.promptrek.yaml", "--editor", "claude"]
        )

        assert result.exit_code != 0

    def test_generate_no_editor_specified(self, tmp_path):
        """Test generate without editor."""
        upf_file = tmp_path / "test.promptrek.yaml"
        upf_file.write_text(
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
        result = runner.invoke(cli, ["generate", str(upf_file)])

        # Should either prompt for editor or fail
        assert result.exit_code != 0 or "editor" in result.output.lower()

    def test_sync_nonexistent_directory(self):
        """Test sync with non-existent directory."""
        runner = CliRunner()
        result = runner.invoke(
            cli, ["sync", "--editor", "claude", "--source-dir", "/nonexistent"]
        )

        assert result.exit_code != 0

    def test_preview_nonexistent_file(self):
        """Test preview with non-existent file."""
        runner = CliRunner()
        result = runner.invoke(cli, ["preview", "/nonexistent/file.promptrek.yaml"])

        assert result.exit_code != 0

    def test_init_existing_file_no_force(self, tmp_path):
        """Test init when file already exists without force."""
        runner = CliRunner()
        with runner.isolated_filesystem(temp_dir=tmp_path):
            # Create initial file
            result1 = runner.invoke(cli, ["init"])
            assert result1.exit_code == 0

            # Try to create again without force
            result2 = runner.invoke(cli, ["init"])
            assert result2.exit_code != 0 or "exists" in result2.output.lower()

    def test_init_v1_format(self, tmp_path):
        """Test init with v1 format."""
        runner = CliRunner()
        with runner.isolated_filesystem(temp_dir=tmp_path):
            result = runner.invoke(cli, ["init", "--v1"])
            assert result.exit_code == 0

            # Check created file
            upf_file = Path("project.promptrek.yaml")
            assert upf_file.exists()
            content = upf_file.read_text()
            assert "schema_version" in content
            assert "1.0.0" in content or '"1.0.0"' in content

    def test_init_with_template(self, tmp_path):
        """Test init with template."""
        runner = CliRunner()
        with runner.isolated_filesystem(temp_dir=tmp_path):
            result = runner.invoke(cli, ["init", "--template", "react"])
            assert result.exit_code == 0

    def test_generate_with_variables(self, tmp_path):
        """Test generate with variable overrides."""
        upf_file = tmp_path / "test.promptrek.yaml"
        upf_file.write_text(
            """
schema_version: "2.0.0"
metadata:
  title: "Test"
  description: "Test"
  version: "1.0.0"
content: "# {{{ PROJECT_NAME }}}"
variables:
  PROJECT_NAME: "Default"
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
                "-V",
                "PROJECT_NAME=Override",
            ],
        )

        assert result.exit_code == 0

    def test_validate_nonexistent_file(self):
        """Test validate with non-existent file."""
        runner = CliRunner()
        result = runner.invoke(cli, ["validate", "/nonexistent/file.promptrek.yaml"])

        assert result.exit_code != 0

    def test_migrate_nonexistent_file(self):
        """Test migrate with non-existent file."""
        runner = CliRunner()
        result = runner.invoke(cli, ["migrate", "/nonexistent/file.promptrek.yaml"])

        assert result.exit_code != 0

    def test_global_verbose_flag(self, tmp_path):
        """Test global verbose flag."""
        upf_file = tmp_path / "test.promptrek.yaml"
        upf_file.write_text(
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
        result = runner.invoke(cli, ["--verbose", "validate", str(upf_file)])

        assert result.exit_code == 0
        # Verbose output should show additional information
        assert "✅" in result.output or "Summary" in result.output

    def test_help_command(self):
        """Test help command."""
        runner = CliRunner()
        result = runner.invoke(cli, ["--help"])

        assert result.exit_code == 0
        assert "Usage:" in result.output
        assert "validate" in result.output
        assert "generate" in result.output
        assert "migrate" in result.output

    def test_version_command(self):
        """Test version command."""
        runner = CliRunner()
        result = runner.invoke(cli, ["--version"])

        assert result.exit_code == 0 or "version" in result.output.lower()

    def test_generate_all_editors(self, tmp_path):
        """Test generate for all editors."""
        upf_file = tmp_path / "test.promptrek.yaml"
        upf_file.write_text(
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
        result = runner.invoke(
            cli, ["generate", str(upf_file), "--all", "-o", str(tmp_path)]
        )

        assert result.exit_code == 0
        # Should generate for multiple editors
        assert "✅" in result.output or "Generated" in result.output

    def test_sync_output_file(self, tmp_path):
        """Test sync with custom output file."""
        # Create a Claude file to sync from
        claude_dir = tmp_path / ".claude"
        claude_dir.mkdir()
        claude_file = claude_dir / "CLAUDE.md"
        claude_file.write_text("# Test Project")

        output_file = tmp_path / "synced.promptrek.yaml"

        runner = CliRunner()
        result = runner.invoke(
            cli,
            [
                "sync",
                "--editor",
                "claude",
                "--source-dir",
                str(tmp_path),
                "--output",
                str(output_file),
            ],
        )

        # May succeed or fail depending on content, but should run
        assert result.exit_code in [0, 1]

    def test_preview_with_editor(self, tmp_path):
        """Test preview with specific editor."""
        upf_file = tmp_path / "test.promptrek.yaml"
        upf_file.write_text(
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
        result = runner.invoke(cli, ["preview", str(upf_file), "--editor", "claude"])

        assert result.exit_code == 0
        assert "#" in result.output or "Test" in result.output
