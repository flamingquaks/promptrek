"""Integration tests for CLI functionality."""

from pathlib import Path

from click.testing import CliRunner

from apm.cli.main import cli


class TestCLIIntegration:
    """Test CLI command integration."""

    def test_cli_help(self):
        """Test CLI help command."""
        runner = CliRunner()
        result = runner.invoke(cli, ["--help"])

        assert result.exit_code == 0
        assert "Agent Prompt Mapper" in result.output
        assert "init" in result.output
        assert "validate" in result.output
        assert "generate" in result.output

    def test_init_command(self, tmp_path):
        """Test init command creates file."""
        runner = CliRunner()
        output_file = tmp_path / "test.apm.yaml"

        result = runner.invoke(cli, ["init", "--output", str(output_file)])

        assert result.exit_code == 0
        assert output_file.exists()
        assert "Initialized universal prompt file" in result.output

    def test_init_command_with_template(self, tmp_path):
        """Test init command with template."""
        runner = CliRunner()
        output_file = tmp_path / "react.apm.yaml"

        result = runner.invoke(
            cli, ["init", "--template", "react", "--output", str(output_file)]
        )

        assert result.exit_code == 0
        assert output_file.exists()

        # Check content has React-specific elements
        content = output_file.read_text()
        assert "React TypeScript Project Assistant" in content
        assert "typescript" in content

    def test_validate_command_valid_file(self, sample_upf_file):
        """Test validate command with valid file."""
        runner = CliRunner()
        result = runner.invoke(cli, ["validate", str(sample_upf_file)])

        assert result.exit_code == 0
        assert "Validation passed" in result.output

    def test_validate_command_invalid_file(self, tmp_path):
        """Test validate command with invalid file."""
        invalid_file = tmp_path / "invalid.apm.yaml"
        invalid_file.write_text(
            """
schema_version: "1.0.0"
metadata:
  title: ""
  description: "Test"
  version: "1.0.0"
  author: "Test"
  created: "2024-01-01"
  updated: "2024-01-01"
targets: []
"""
        )

        runner = CliRunner()
        result = runner.invoke(cli, ["validate", str(invalid_file)])

        assert result.exit_code == 1
        assert (
            "failed" in result.output
        )  # Either "Parsing failed" or "Validation failed"

    def test_generate_command_copilot(self, sample_upf_file, tmp_path):
        """Test generate command for Copilot."""
        runner = CliRunner()

        # Change to tmp directory for output
        with runner.isolated_filesystem(temp_dir=tmp_path):
            result = runner.invoke(
                cli, ["generate", str(sample_upf_file), "--editor", "copilot"]
            )

            assert result.exit_code == 0
            assert "Generated:" in result.output

            # Check if file was created
            output_file = Path(".github/copilot-instructions.md")
            assert output_file.exists()

            # Check content
            content = output_file.read_text()
            assert "Test Project Assistant" in content
            assert "General Instructions" in content

    def test_generate_command_dry_run(self, sample_upf_file):
        """Test generate command in dry-run mode."""
        runner = CliRunner()
        result = runner.invoke(
            cli, ["generate", str(sample_upf_file), "--editor", "copilot", "--dry-run"]
        )

        assert result.exit_code == 0
        assert "Dry run mode" in result.output
        assert "Would create:" in result.output

    def test_generate_command_all_editors(self, sample_upf_file, tmp_path):
        """Test generate command for all editors."""
        runner = CliRunner()

        with runner.isolated_filesystem(temp_dir=tmp_path):
            result = runner.invoke(cli, ["generate", str(sample_upf_file), "--all"])

            assert result.exit_code == 0

            # Should generate for both copilot and cursor (from sample data)
            assert Path(".github/copilot-instructions.md").exists()
            assert Path(".cursorrules").exists()

    def test_list_editors_command(self):
        """Test list-editors command."""
        runner = CliRunner()
        result = runner.invoke(cli, ["list-editors"])

        assert result.exit_code == 0
        assert "Supported editors:" in result.output
        assert "copilot" in result.output
        assert "cursor" in result.output
        assert "✅" in result.output  # Implemented editors
        assert "⏳" in result.output  # Planned editors

    def test_generate_command_missing_editor_and_all(self, sample_upf_file):
        """Test generate command fails when neither editor nor all is specified."""
        runner = CliRunner()
        result = runner.invoke(cli, ["generate", str(sample_upf_file)])

        assert result.exit_code == 1
        assert "Must specify either --editor or --all" in result.output

    def test_generate_command_invalid_editor(self, sample_upf_file):
        """Test generate command fails with invalid editor."""
        runner = CliRunner()
        result = runner.invoke(
            cli, ["generate", str(sample_upf_file), "--editor", "nonexistent"]
        )

        assert result.exit_code == 1

    def test_generate_command_with_variable_overrides(self, tmp_path):
        """Test generate command with variable overrides."""
        # Create a UPF file with variables
        upf_file = tmp_path / "test_vars.apm.yaml"
        upf_file.write_text(
            """
schema_version: "1.0.0"
metadata:
  title: "Test {{{ PROJECT_NAME }}}"
  description: "Testing variables for {{{ PROJECT_NAME }}}"
  version: "1.0.0"
  author: "default@example.com"
  created: "2024-01-01"
  updated: "2024-01-01"
targets:
  - copilot
context:
  project_type: "{{{ PROJECT_TYPE }}}"
  description: "Project using {{{ TECH_STACK }}}"
instructions:
  general:
    - "Use {{{ TECH_STACK }}} best practices"
    - "Contact {{{ SUPPORT_EMAIL }}} for help"
variables:
  PROJECT_NAME: "Default App"
  PROJECT_TYPE: "default_project"
  TECH_STACK: "Python"
  SUPPORT_EMAIL: "support@example.com"
"""
        )

        runner = CliRunner()
        with runner.isolated_filesystem(temp_dir=tmp_path):
            result = runner.invoke(
                cli,
                [
                    "generate",
                    str(upf_file),
                    "--editor",
                    "copilot",
                    "-V",
                    "PROJECT_NAME=Overridden App",
                    "-V",
                    "TECH_STACK=Go",
                    "-V",
                    "PROJECT_TYPE=go_project",
                ],
            )

            assert result.exit_code == 0
            assert "Generated:" in result.output

            # Check if file was created
            output_file = Path(".github/copilot-instructions.md")
            assert output_file.exists()

            # Check that variables were overridden
            content = output_file.read_text()
            assert "Test Overridden App" in content
            assert "Testing variables for Overridden App" in content
            assert "Type: go_project" in content
            assert "Project using Go" in content
            assert "Use Go best practices" in content
            # SUPPORT_EMAIL should remain default since not overridden
            assert "Contact support@example.com for help" in content
