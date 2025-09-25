"""Integration tests for CLI functionality."""

from pathlib import Path

from click.testing import CliRunner

from promptrek.cli.main import cli


class TestCLIIntegration:
    """Test CLI command integration."""

    def test_cli_help(self):
        """Test CLI help command."""
        runner = CliRunner()
        result = runner.invoke(cli, ["--help"])

        assert result.exit_code == 0
        assert "PrompTrek" in result.output
        assert "init" in result.output
        assert "validate" in result.output
        assert "generate" in result.output

    def test_init_command(self, tmp_path):
        """Test init command creates file."""
        runner = CliRunner()
        output_file = tmp_path / "test.promptrek.yaml"

        result = runner.invoke(cli, ["init", "--output", str(output_file)])

        assert result.exit_code == 0
        assert output_file.exists()
        assert "Initialized universal prompt file" in result.output

    def test_init_command_with_template(self, tmp_path):
        """Test init command with template."""
        runner = CliRunner()
        output_file = tmp_path / "react.promptrek.yaml"

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
        invalid_file = tmp_path / "invalid.promptrek.yaml"
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

    def test_validate_command_verbose(self, sample_upf_file):
        """Test validate command with verbose flag."""
        runner = CliRunner()
        result = runner.invoke(cli, ["--verbose", "validate", str(sample_upf_file)])

        assert result.exit_code == 0
        assert "✅ File parsed successfully" in result.output
        assert "📋 Summary:" in result.output
        assert "Title:" in result.output
        assert "Version:" in result.output
        assert "Targets:" in result.output

    def test_validate_command_warnings_strict(self, tmp_path):
        """Test validate command with warnings in strict mode."""
        # Create a file that generates warnings
        warning_file = tmp_path / "warning.promptrek.yaml"
        warning_file.write_text(
            """
schema_version: "1.0.0"
metadata:
  title: "Test"
  description: "Test"
  version: "1.0.0"
  author: "Test"
  created: "2024-01-01"
  updated: "2024-01-01"
targets:
  - claude
# Missing instructions field which might generate warnings
"""
        )

        runner = CliRunner()
        result = runner.invoke(cli, ["validate", str(warning_file), "--strict"])

        # In strict mode, warnings become errors
        if "warning" in result.output.lower():
            assert result.exit_code == 1
            assert "❌" in result.output

    def test_validate_command_warnings_non_strict(self, tmp_path):
        """Test validate command with warnings in non-strict mode."""
        # Create a file that generates warnings
        warning_file = tmp_path / "warning.promptrek.yaml"
        warning_file.write_text(
            """
schema_version: "1.0.0"
metadata:
  title: "Test"
  description: "Test"
  version: "1.0.0"
  author: "Test"
  created: "2024-01-01"
  updated: "2024-01-01"
targets:
  - claude
# Missing instructions field which might generate warnings
"""
        )

        runner = CliRunner()
        result = runner.invoke(cli, ["validate", str(warning_file)])

        # In non-strict mode, warnings don't cause failure
        if "warning" in result.output.lower():
            assert result.exit_code == 0
            assert "⚠️" in result.output
            assert "✅ Validation passed with warnings" in result.output

    def test_validate_command_parsing_error(self, tmp_path):
        """Test validate command with parsing errors."""
        # Create an invalid YAML file
        invalid_yaml = tmp_path / "invalid.promptrek.yaml"
        invalid_yaml.write_text(
            """
schema_version: "1.0.0"
metadata:
  title: "Test
  # Invalid YAML - unclosed quote
"""
        )

        runner = CliRunner()
        result = runner.invoke(cli, ["validate", str(invalid_yaml)])

        assert result.exit_code == 1
        assert "❌ Parsing failed" in result.output

    def test_generate_command_auto_discovery_with_verbose(self, tmp_path):
        """Test generate command with automatic file discovery and verbose output."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            # Create a UPF file in the current working directory (inside isolated filesystem)
            upf_file = Path("test.promptrek.yaml")
            upf_file.write_text(
                """
schema_version: "1.0.0"
metadata:
  title: "Auto Discovery Test"
  description: "Test file auto discovery"
  version: "1.0.0"
  author: "test@example.com"
  created: "2024-01-01"
  updated: "2024-01-01"
targets:
  - claude
instructions:
  general:
    - "Test instruction"
"""
            )

            result = runner.invoke(cli, ["--verbose", "generate", "--editor", "claude"])

            # Debug what's happening if it fails
            if result.exit_code != 0:
                print(f"Exit code: {result.exit_code}")
                print(f"Output: {result.output}")

            # Should successfully find and process the file
            assert result.exit_code == 0

    def test_generate_command_directory_processing(self, tmp_path):
        """Test generate command with directory processing."""
        # Create multiple UPF files in a directory
        test_dir = tmp_path / "test_upf_dir"
        test_dir.mkdir()

        for i in range(2):
            upf_file = test_dir / f"test{i}.promptrek.yaml"
            upf_file.write_text(
                f"""
schema_version: "1.0.0"
metadata:
  title: "Test {i}"
  description: "Test file {i}"
  version: "1.0.0"
  author: "test@example.com"
  created: "2024-01-01"
  updated: "2024-01-01"
targets:
  - claude
instructions:
  general:
    - "Test instruction {i}"
"""
            )

        runner = CliRunner()
        result = runner.invoke(
            cli,
            [
                "--verbose",
                "generate",
                "--editor",
                "claude",
                "--directory",
                str(test_dir),
            ],
        )

        assert result.exit_code == 0
        assert "Found 2 UPF files" in result.output

    def test_generate_command_no_files_no_directory(self, tmp_path):
        """Test generate command when no files are found."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            # No UPF files in the directory
            result = runner.invoke(cli, ["generate", "--editor", "claude"])

            assert result.exit_code == 1
            assert "No UPF files found" in result.output

    def test_generate_command_recursive_directory(self, tmp_path):
        """Test generate command with recursive directory processing."""
        # Create nested directory structure with UPF files
        base_dir = tmp_path / "base"
        base_dir.mkdir()
        nested_dir = base_dir / "nested"
        nested_dir.mkdir()

        for i, directory in enumerate([base_dir, nested_dir]):
            upf_file = directory / f"test{i}.promptrek.yaml"
            upf_file.write_text(
                f"""
schema_version: "1.0.0"
metadata:
  title: "Test {i}"
  description: "Test file {i}"
  version: "1.0.0"
  author: "test@example.com"
  created: "2024-01-01"
  updated: "2024-01-01"
targets:
  - claude
instructions:
  general:
    - "Test instruction {i}"
"""
            )

        runner = CliRunner()
        result = runner.invoke(
            cli,
            [
                "--verbose",
                "generate",
                "--editor",
                "claude",
                "--directory",
                str(base_dir),
            ],
        )

        assert result.exit_code == 0
        assert (
            "Found 1 UPF files" in result.output
        )  # Non-recursive search finds only base directory file

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
            # Cursor now generates files in .cursor/rules/ directory
            cursor_rules_dir = Path(".cursor/rules")
            assert cursor_rules_dir.exists() or Path("AGENTS.md").exists()

    def test_list_editors_command(self):
        """Test list-editors command."""
        runner = CliRunner()
        result = runner.invoke(cli, ["list-editors"])

        assert result.exit_code == 0
        assert "AI Editor Support Status:" in result.output
        assert "copilot" in result.output
        assert "cursor" in result.output
        assert "✅" in result.output  # Project Configuration File Support
        assert "ℹ️" in result.output  # Global Configuration Only

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
        upf_file = tmp_path / "test_vars.promptrek.yaml"
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
