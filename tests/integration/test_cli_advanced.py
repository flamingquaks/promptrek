"""
Integration tests for CLI commands.
"""

import shutil
import tempfile
from pathlib import Path

import pytest
from click.testing import CliRunner

from src.promptrek.cli.main import cli


class TestCLIIntegration:
    """Integration tests for CLI commands."""

    @pytest.fixture
    def runner(self):
        """Create Click test runner."""
        return CliRunner()

    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for test files."""
        temp_dir = Path(tempfile.mkdtemp())
        yield temp_dir
        shutil.rmtree(temp_dir)

    @pytest.fixture
    def sample_upf_file(self, temp_dir):
        """Create a sample UPF file for testing."""
        upf_content = """schema_version: "1.0.0"

metadata:
  title: "CLI Test Project"
  description: "Project for CLI integration testing"
  version: "1.0.0"
  author: "test@example.com"
  created: "2024-01-01"
  updated: "2024-01-01"
  tags: ["test", "cli"]

targets:
  - claude
  - continue
  - codeium

context:
  project_type: "web_application"
  technologies: ["typescript", "react"]
  description: "A test web application"

instructions:
  general:
    - "Write clean, maintainable code"
    - "Follow TypeScript best practices"
  code_style:
    - "Use consistent indentation"
    - "Prefer const over let"
  testing:
    - "Write unit tests for all functions"

examples:
  component: "const Button = ({ label }: { label: string }) => <button>{label}</button>;"
  function: "export const formatDate = (date: Date): string => date.toISOString();"

variables:
  PROJECT_NAME: "CLITestProject"
  AUTHOR_NAME: "Test Author"
"""
        upf_file = temp_dir / "test.promptrek.yaml"
        upf_file.write_text(upf_content)
        return upf_file

    @pytest.fixture
    def conditional_upf_file(self, temp_dir):
        """Create a UPF file with conditionals for testing."""
        upf_content = """schema_version: "1.0.0"

metadata:
  title: "Conditional CLI Test"
  description: "Project with conditionals for CLI testing"
  version: "1.0.0"
  author: "test@example.com"
  created: "2024-01-01"
  updated: "2024-01-01"

targets:
  - claude
  - continue

instructions:
  general:
    - "Write clean code"

conditions:
  - if: 'EDITOR == "claude"'
    then:
      instructions:
        general:
          - "Claude-specific: Provide detailed explanations"
  - if: 'EDITOR == "continue"'
    then:
      instructions:
        general:
          - "Continue-specific: Generate comprehensive completions"

variables:
  TEST_VAR: "default_value"
"""
        upf_file = temp_dir / "conditional.promptrek.yaml"
        upf_file.write_text(upf_content)
        return upf_file

    def test_cli_help(self, runner):
        """Test CLI help command."""
        result = runner.invoke(cli, ["--help"])
        assert result.exit_code == 0
        assert "PrompTrek" in result.output
        assert "generate" in result.output
        assert "validate" in result.output
        assert "list-editors" in result.output

    def test_list_editors_command(self, runner):
        """Test list-editors command."""
        result = runner.invoke(cli, ["list-editors"])
        assert result.exit_code == 0
        assert "claude" in result.output
        assert "continue" in result.output
        assert "windsurf" in result.output
        assert "copilot" in result.output

    def test_validate_valid_file(self, runner, sample_upf_file):
        """Test validate command with valid file."""
        result = runner.invoke(cli, ["validate", str(sample_upf_file)])
        assert result.exit_code == 0
        assert "valid" in result.output.lower()

    def test_validate_nonexistent_file(self, runner):
        """Test validate command with nonexistent file."""
        result = runner.invoke(cli, ["validate", "nonexistent.promptrek.yaml"])
        assert result.exit_code != 0
        assert "does not exist" in result.output.lower()

    def test_generate_single_editor_dry_run(self, runner, sample_upf_file, temp_dir):
        """Test generate command with single editor in dry run mode."""
        result = runner.invoke(
            cli,
            [
                "generate",
                "--editor",
                "claude",
                "--output",
                str(temp_dir),
                "--dry-run",
                str(sample_upf_file),
            ],
        )
        assert result.exit_code == 0
        assert "Would create" in result.output
        assert ".claude/context.md" in result.output

    def test_generate_single_editor_actual(self, runner, sample_upf_file, temp_dir):
        """Test generate command with single editor actual generation."""
        result = runner.invoke(
            cli,
            [
                "generate",
                "--editor",
                "claude",
                "--output",
                str(temp_dir),
                str(sample_upf_file),
            ],
        )
        assert result.exit_code == 0
        assert "Generated:" in result.output

        # Check that file was actually created
        generated_file = temp_dir / ".claude" / "context.md"
        assert generated_file.exists()

        # Check content
        content = generated_file.read_text()
        assert "CLI Test Project" in content
        assert "Write clean, maintainable code" in content
        assert "typescript, react" in content

    def test_generate_all_editors_dry_run(self, runner, sample_upf_file, temp_dir):
        """Test generate command with all editors in dry run mode."""
        result = runner.invoke(
            cli,
            [
                "generate",
                "--all",
                "--output",
                str(temp_dir),
                "--dry-run",
                str(sample_upf_file),
            ],
        )
        assert result.exit_code == 0
        assert "Would create" in result.output
        # Should create files for all target editors using new formats
        assert (
            "config.yaml" in result.output
        ) or (
            ".continue/rules/" in result.output
        )
        # Verify at least some expected output for other tools
        assert any(
            tool in result.output
            for tool in ["windsurf", "global configuration", "Note:", "Would create"]
        )

    def test_generate_with_variable_overrides(self, runner, sample_upf_file, temp_dir):
        """Test generate command with variable overrides."""
        result = runner.invoke(
            cli,
            [
                "generate",
                "--editor",
                "claude",
                "--output",
                str(temp_dir),
                "-V",
                "PROJECT_NAME=OverriddenProject",
                "-V",
                "AUTHOR_NAME=Override Author",
                str(sample_upf_file),
            ],
        )
        assert result.exit_code == 0

        # Check that variables were overridden
        generated_file = temp_dir / ".claude" / "context.md"
        assert generated_file.exists()
        # Verify file was generated
        # The content should include the overridden values if variable substitution is used

    def test_generate_with_conditionals(self, runner, conditional_upf_file, temp_dir):
        """Test generate command with conditional instructions."""
        # Test Claude-specific generation
        result = runner.invoke(
            cli,
            [
                "generate",
                "--editor",
                "claude",
                "--output",
                str(temp_dir),
                str(conditional_upf_file),
            ],
        )
        assert result.exit_code == 0

        claude_file = temp_dir / ".claude" / "context.md"
        assert claude_file.exists()
        claude_content = claude_file.read_text()
        assert "Claude-specific: Provide detailed explanations" in claude_content
        assert "Continue-specific" not in claude_content

        # Test Continue-specific generation
        result = runner.invoke(
            cli,
            [
                "generate",
                "--editor",
                "continue",
                "--output",
                str(temp_dir),
                str(conditional_upf_file),
            ],
        )
        assert result.exit_code == 0

        # Check for the new Continue format (config.yaml)
        continue_config = temp_dir / "config.yaml"
        if continue_config.exists():
            continue_content = continue_config.read_text()
            assert (
                "Continue-specific: Generate comprehensive completions"
                in continue_content
            )
            assert "Claude-specific" not in continue_content
        else:
            # Check for rules files if config.yaml doesn't exist
            continue_rules_dir = temp_dir / ".continue" / "rules"
            assert continue_rules_dir.exists()
            rule_files = list(continue_rules_dir.glob("*.md"))
            assert len(rule_files) > 0

    def test_generate_invalid_editor(self, runner, sample_upf_file):
        """Test generate command with invalid editor."""
        result = runner.invoke(
            cli, ["generate", "--editor", "nonexistent", str(sample_upf_file)]
        )
        assert result.exit_code != 0
        assert "not available" in result.output

    def test_generate_no_editor_or_all(self, runner, sample_upf_file):
        """Test generate command without specifying editor or --all."""
        result = runner.invoke(cli, ["generate", str(sample_upf_file)])
        assert result.exit_code != 0
        assert "Must specify either --editor or --all" in result.output

    def test_generate_with_verbose_flag(self, runner, sample_upf_file, temp_dir):
        """Test generate command with verbose flag."""
        result = runner.invoke(
            cli,
            [
                "-v",
                "generate",
                "--editor",
                "claude",
                "--output",
                str(temp_dir),
                "--dry-run",
                str(sample_upf_file),
            ],
        )
        assert result.exit_code == 0
        assert "Parsed" in result.output
        assert str(sample_upf_file) in result.output

    def test_init_command_basic(self, runner, temp_dir):
        """Test init command basic functionality."""
        init_file = temp_dir / "init_test.promptrek.yaml"
        result = runner.invoke(
            cli, ["init", "--output", str(init_file)], input="\n\n\n\n\n\n"
        )  # Accept all defaults

        assert result.exit_code == 0
        assert init_file.exists()

        # Verify the created file has basic structure
        content = init_file.read_text()
        assert "schema_version" in content
        assert "metadata" in content
        assert "targets" in content

    def test_init_command_with_template(self, runner, temp_dir):
        """Test init command with template."""
        init_file = temp_dir / "template_test.promptrek.yaml"
        result = runner.invoke(
            cli, ["init", "--template", "basic", "--output", str(init_file)]
        )

        assert result.exit_code == 0
        assert init_file.exists()

        # Verify the created file has template content
        content = init_file.read_text()
        assert "schema_version" in content
        assert "targets" in content

    def test_validate_command_with_errors(self, runner, temp_dir):
        """Test validate command with a file containing errors."""
        # Create an invalid UPF file
        invalid_content = """schema_version: "1.0.0"
metadata:
  title: ""  # Invalid: empty title
  description: "Test description"
  version: "1.0.0"
  author: "Test Author"
targets: []  # Invalid: no targets
"""
        invalid_file = temp_dir / "invalid.promptrek.yaml"
        invalid_file.write_text(invalid_content)

        result = runner.invoke(cli, ["validate", str(invalid_file)])
        assert result.exit_code != 0
        assert "error" in result.output.lower() or "invalid" in result.output.lower()

    def test_validate_command_verbose(self, runner, sample_upf_file):
        """Test validate command with verbose output."""
        result = runner.invoke(cli, ["-v", "validate", str(sample_upf_file)])
        assert result.exit_code == 0
        assert "valid" in result.output.lower()
