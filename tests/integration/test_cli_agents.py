"""Integration tests for the agents CLI command."""

import pytest
from pathlib import Path
from click.testing import CliRunner

from promptrek.cli.main import cli


class TestAgentsCLIIntegration:
    """Integration tests for agents CLI command."""

    def test_agents_command_help(self):
        """Test agents command help output."""
        runner = CliRunner()
        result = runner.invoke(cli, ["agents", "--help"])

        assert result.exit_code == 0
        assert "Generate persistent agent instruction files" in result.output
        assert "--prompt-file" in result.output
        assert "--dry-run" in result.output
        assert "--force" in result.output

    def test_agents_command_with_explicit_file(self):
        """Test agents command with explicit prompt file."""
        runner = CliRunner()

        with runner.isolated_filesystem():
            # Create a test prompt file
            prompt_file = Path("test.promptrek.yaml")
            prompt_file.write_text(
                """
schema_version: "1.0.0"
metadata:
  title: "Test Project"
  description: "A test project"
  version: "1.0.0"
  author: "test@example.com"
  created: "2024-01-01"
  updated: "2024-01-01"
targets: ["copilot"]
"""
            )

            # Run the command
            result = runner.invoke(cli, ["agents", "--prompt-file", str(prompt_file)])

            assert result.exit_code == 0
            assert "Created 3 agent instruction files" in result.output

            # Check files were created
            assert Path("AGENTS.md").exists()
            assert Path(".github/copilot-instructions.md").exists()
            assert Path(".claude/context.md").exists()

    def test_agents_command_auto_discovery(self):
        """Test agents command with auto-discovery."""
        runner = CliRunner()

        with runner.isolated_filesystem():
            # Create a .promptrek.yaml file
            prompt_file = Path("project.promptrek.yaml")
            prompt_file.write_text(
                """
schema_version: "1.0.0"
metadata:
  title: "Auto Discovery Test"
  description: "Testing auto-discovery"
  version: "1.0.0"
  author: "test@example.com"
  created: "2024-01-01"
  updated: "2024-01-01"
targets: ["copilot"]
"""
            )

            # Run the command without specifying file
            result = runner.invoke(cli, ["agents"])

            assert result.exit_code == 0
            assert "Created 3 agent instruction files" in result.output

            # Check files were created
            assert Path("AGENTS.md").exists()

    def test_agents_command_dry_run(self):
        """Test agents command with dry run."""
        runner = CliRunner()

        with runner.isolated_filesystem():
            # Create a test prompt file
            prompt_file = Path("test.promptrek.yaml")
            prompt_file.write_text(
                """
schema_version: "1.0.0"
metadata:
  title: "Dry Run Test"
  description: "Testing dry run"
  version: "1.0.0"
  author: "test@example.com"
  created: "2024-01-01"
  updated: "2024-01-01"
targets: ["copilot"]
"""
            )

            # Run with dry run
            result = runner.invoke(
                cli, ["agents", "--prompt-file", str(prompt_file), "--dry-run"]
            )

            assert result.exit_code == 0
            assert "Would create 3 agent instruction files" in result.output

            # Check no files were actually created
            assert not Path("AGENTS.md").exists()
            assert not Path(".github/copilot-instructions.md").exists()
            assert not Path(".claude/context.md").exists()

    def test_agents_command_verbose(self):
        """Test agents command with verbose output."""
        runner = CliRunner()

        with runner.isolated_filesystem():
            # Create a test prompt file
            prompt_file = Path("test.promptrek.yaml")
            prompt_file.write_text(
                """
schema_version: "1.0.0"
metadata:
  title: "Verbose Test"
  description: "Testing verbose output"
  version: "1.0.0"
  author: "test@example.com"
  created: "2024-01-01"
  updated: "2024-01-01"
targets: ["copilot"]
"""
            )

            # Run with verbose flag
            result = runner.invoke(
                cli, ["-v", "agents", "--prompt-file", str(prompt_file)]
            )

            assert result.exit_code == 0
            assert (
                "Auto-discovered prompt file" in result.output
                or "Parsed prompt file" in result.output
            )
            assert "Created 3 agent instruction files" in result.output

    def test_agents_command_force_overwrite(self):
        """Test agents command with force flag."""
        runner = CliRunner()

        with runner.isolated_filesystem():
            # Create a test prompt file
            prompt_file = Path("test.promptrek.yaml")
            prompt_file.write_text(
                """
schema_version: "1.0.0"
metadata:
  title: "Force Test"
  description: "Testing force overwrite"
  version: "1.0.0"
  author: "test@example.com"
  created: "2024-01-01"
  updated: "2024-01-01"
targets: ["copilot"]
"""
            )

            # Create existing file
            Path("AGENTS.md").write_text("Old content")

            # Run with force
            result = runner.invoke(
                cli, ["agents", "--prompt-file", str(prompt_file), "--force"]
            )

            assert result.exit_code == 0
            assert "Created 3 agent instruction files" in result.output

            # Check file was overwritten
            content = Path("AGENTS.md").read_text()
            assert "Old content" not in content
            assert "Force Test - Agent Instructions" in content

    def test_agents_command_no_prompt_file_error(self):
        """Test agents command error when no prompt file found."""
        runner = CliRunner()

        with runner.isolated_filesystem():
            # Run without any prompt files
            result = runner.invoke(cli, ["agents"])

            assert result.exit_code == 1
            assert "No prompt file specified" in result.output

    def test_agents_command_nonexistent_file_error(self):
        """Test agents command error with nonexistent file."""
        runner = CliRunner()

        result = runner.invoke(cli, ["agents", "--prompt-file", "nonexistent.yaml"])

        assert result.exit_code == 1
        assert "Prompt file not found" in result.output

    def test_agents_command_invalid_yaml_error(self):
        """Test agents command error with invalid YAML."""
        runner = CliRunner()

        with runner.isolated_filesystem():
            # Create invalid YAML file
            prompt_file = Path("invalid.promptrek.yaml")
            prompt_file.write_text("invalid: yaml: content: [unclosed")

            # Run the command
            result = runner.invoke(cli, ["agents", "--prompt-file", str(prompt_file)])

            assert result.exit_code == 1
            assert "Failed to parse prompt file" in result.output

    def test_agents_command_custom_output_directory(self):
        """Test agents command with custom output directory."""
        runner = CliRunner()

        with runner.isolated_filesystem():
            # Create a test prompt file
            prompt_file = Path("test.promptrek.yaml")
            prompt_file.write_text(
                """
schema_version: "1.0.0"
metadata:
  title: "Custom Output Test"
  description: "Testing custom output directory"
  version: "1.0.0"
  author: "test@example.com"  
  created: "2024-01-01"
  updated: "2024-01-01"
targets: ["copilot"]
"""
            )

            # Create custom output directory
            output_dir = Path("custom_output")
            output_dir.mkdir()

            # Run with custom output directory
            result = runner.invoke(
                cli,
                [
                    "agents",
                    "--prompt-file",
                    str(prompt_file),
                    "--output",
                    str(output_dir),
                ],
            )

            assert result.exit_code == 0
            assert "Created 3 agent instruction files" in result.output

            # Check files were created in custom directory
            assert (output_dir / "AGENTS.md").exists()
            assert (output_dir / ".github" / "copilot-instructions.md").exists()
            assert (output_dir / ".claude" / "context.md").exists()
