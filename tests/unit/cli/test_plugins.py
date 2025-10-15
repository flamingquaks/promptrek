"""Unit tests for plugins CLI command."""

from pathlib import Path

import pytest
from click.testing import CliRunner

from promptrek.cli.main import cli


class TestPluginsCommand:
    """Test suite for plugins command."""

    @pytest.fixture
    def v21_file(self, tmp_path):
        """Create a v2.1 file with plugins."""
        upf_file = tmp_path / "test.promptrek.yaml"
        upf_file.write_text(
            """
schema_version: "2.1.0"
metadata:
  title: "Test Project"
  description: "Test with plugins"
  version: "1.0.0"
content: |
  # Test Project
  Guidelines here.

plugins:
  mcp_servers:
    - name: test-server
      command: npx
      args: ["-y", "@test/server"]
      description: "Test MCP server"
  commands:
    - name: test-cmd
      description: "Test command"
      prompt: "Do something"
  agents:
    - name: test-agent
      description: "Test agent"
      system_prompt: "You are a test agent"
  hooks:
    - name: test-hook
      event: test-event
      command: "echo test"
"""
        )
        return upf_file

    @pytest.fixture
    def v20_file(self, tmp_path):
        """Create a v2.0 file without plugins."""
        upf_file = tmp_path / "v20.promptrek.yaml"
        upf_file.write_text(
            """
schema_version: "2.0.0"
metadata:
  title: "V2.0 Project"
  description: "No plugins"
  version: "1.0.0"
content: |
  # V2.0 Project
  No plugins here.
"""
        )
        return upf_file

    def test_plugins_list_command(self, v21_file):
        """Test plugins list command."""
        runner = CliRunner()
        result = runner.invoke(cli, ["plugins", "list", "--file", str(v21_file)])

        assert result.exit_code == 0
        assert "MCP Servers" in result.output
        assert "test-server" in result.output
        assert "Commands" in result.output
        assert "test-cmd" in result.output
        assert "Agents" in result.output
        assert "test-agent" in result.output
        assert "Hooks" in result.output
        assert "test-hook" in result.output

    def test_plugins_list_no_plugins(self, v20_file):
        """Test plugins list with file that has no plugins."""
        runner = CliRunner()
        result = runner.invoke(cli, ["plugins", "list", "--file", str(v20_file)])

        assert result.exit_code == 0
        assert "No plugins configured" in result.output

    def test_plugins_list_nonexistent_file(self, tmp_path):
        """Test plugins list with nonexistent file."""
        runner = CliRunner()
        result = runner.invoke(
            cli, ["plugins", "list", "--file", str(tmp_path / "nonexistent.yaml")]
        )

        assert result.exit_code != 0

    def test_plugins_generate_command(self, v21_file, tmp_path):
        """Test plugins generate command."""
        output_dir = tmp_path / "output"
        output_dir.mkdir(parents=True, exist_ok=True)  # Create output directory
        runner = CliRunner()
        result = runner.invoke(
            cli,
            [
                "plugins",
                "generate",
                "--file",
                str(v21_file),
                "--editor",
                "claude",
                "--output",
                str(output_dir),
            ],
        )

        # Should succeed - exit code 0 even if there are errors during generation
        assert result.exit_code == 0
        assert "Generating plugin files" in result.output

    def test_plugins_generate_no_plugins(self, v20_file, tmp_path):
        """Test plugins generate with file that has no plugins."""
        output_dir = tmp_path / "output"
        runner = CliRunner()
        result = runner.invoke(
            cli,
            [
                "plugins",
                "generate",
                "--file",
                str(v20_file),
                "--editor",
                "claude",
                "--output",
                str(output_dir),
            ],
        )

        # Should succeed but not generate plugin files
        assert result.exit_code == 0

    def test_plugins_validate_command(self, v21_file):
        """Test plugins validate command."""
        runner = CliRunner()
        result = runner.invoke(cli, ["plugins", "validate", "--file", str(v21_file)])

        assert result.exit_code == 0
        assert "No critical errors found" in result.output

    def test_plugins_validate_invalid_file(self, tmp_path):
        """Test plugins validate with invalid file."""
        invalid_file = tmp_path / "invalid.promptrek.yaml"
        invalid_file.write_text(
            """
schema_version: "2.1.0"
metadata:
  title: "Invalid"
  description: "Invalid trust level"
  version: "1.0.0"
content: |
  # Invalid
plugins:
  agents:
    - name: bad-agent
      description: "Bad agent"
      system_prompt: "Test"
      trust_level: invalid_level
"""
        )

        runner = CliRunner()
        result = runner.invoke(
            cli, ["plugins", "validate", "--file", str(invalid_file)]
        )

        assert result.exit_code != 0

    def test_plugins_list_verbose(self, v21_file):
        """Test plugins list with verbose output."""
        runner = CliRunner()
        result = runner.invoke(
            cli, ["--verbose", "plugins", "list", "--file", str(v21_file)]
        )

        assert result.exit_code == 0
        # Verbose mode should show more details
        assert "test-server" in result.output

    def test_plugins_generate_dry_run(self, v21_file, tmp_path):
        """Test plugins generate with dry-run flag."""
        output_dir = tmp_path / "output"
        output_dir.mkdir(parents=True, exist_ok=True)
        runner = CliRunner()
        result = runner.invoke(
            cli,
            [
                "plugins",
                "generate",
                "--file",
                str(v21_file),
                "--editor",
                "claude",
                "--output",
                str(output_dir),
                "--dry-run",
            ],
        )

        assert result.exit_code == 0
        assert "Generating plugin files" in result.output

    def test_plugins_generate_all_editors(self, v21_file, tmp_path):
        """Test plugins generate for all editors."""
        output_dir = tmp_path / "output"
        output_dir.mkdir(parents=True, exist_ok=True)
        runner = CliRunner()
        result = runner.invoke(
            cli,
            [
                "plugins",
                "generate",
                "--file",
                str(v21_file),
                "--editor",
                "all",
                "--output",
                str(output_dir),
            ],
        )

        assert result.exit_code == 0
        assert "Generating plugin files" in result.output

    def test_plugins_validate_v1_file(self, tmp_path):
        """Test plugins validate with v1 file (no plugin support)."""
        v1_file = tmp_path / "v1.promptrek.yaml"
        v1_file.write_text(
            """
schema_version: "1.0.0"
metadata:
  title: "V1 Project"
  description: "No plugins"
targets: ["copilot"]
context:
  project_type: "web_application"
instructions:
  general:
    - "Write clean code"
"""
        )

        runner = CliRunner()
        result = runner.invoke(cli, ["plugins", "validate", "--file", str(v1_file)])

        assert result.exit_code == 0
        assert "v1.x which doesn't support plugins" in result.output

    def test_plugins_validate_no_plugins(self, v20_file):
        """Test plugins validate with file that has no plugins."""
        runner = CliRunner()
        result = runner.invoke(cli, ["plugins", "validate", "--file", str(v20_file)])

        assert result.exit_code == 0
        assert "No plugins to validate" in result.output

    def test_plugins_list_v1_file(self, tmp_path):
        """Test plugins list with v1 file."""
        v1_file = tmp_path / "v1.promptrek.yaml"
        v1_file.write_text(
            """
schema_version: "1.0.0"
metadata:
  title: "V1 Project"
  description: "No plugins"
targets: ["copilot"]
context:
  project_type: "web_application"
instructions:
  general:
    - "Write clean code"
"""
        )

        runner = CliRunner()
        result = runner.invoke(cli, ["plugins", "list", "--file", str(v1_file)])

        assert result.exit_code == 0
        assert "v1.x which doesn't support plugins" in result.output

    def test_plugins_generate_default_editor(self, v21_file, tmp_path):
        """Test plugins generate without specifying editor (should use defaults)."""
        output_dir = tmp_path / "output"
        output_dir.mkdir(parents=True, exist_ok=True)
        runner = CliRunner()
        result = runner.invoke(
            cli,
            [
                "plugins",
                "generate",
                "--file",
                str(v21_file),
                "--output",
                str(output_dir),
            ],
        )

        assert result.exit_code == 0
        assert "Generating plugin files" in result.output
