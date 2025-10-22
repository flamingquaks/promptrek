"""Tests for migrate command."""

from pathlib import Path

import pytest
from click.testing import CliRunner

from promptrek.cli.main import cli


class TestMigrateCommand:
    """Test suite for migrate command."""

    def test_migrate_v1_to_v2_basic(self, tmp_path):
        """Test basic v1 to v2 migration."""
        # Create v1 file
        v1_file = tmp_path / "test.promptrek.yaml"
        v1_file.write_text(
            """
schema_version: "1.0.0"
metadata:
  title: "Test Project"
  description: "Test description"
  version: "1.0.0"
  author: "Test Author"
  created: "2024-01-01"
  updated: "2024-01-01"
targets:
  - claude
  - cursor
context:
  project_type: "web_application"
  technologies:
    - Python
    - React
  description: "A web application"
instructions:
  general:
    - "Use Python 3.9+"
    - "Follow PEP 8"
  code_style:
    - "Use type hints"
"""
        )

        runner = CliRunner()
        result = runner.invoke(cli, ["migrate", str(v1_file)])

        assert result.exit_code == 0
        assert "✅ Migrated" in result.output
        assert "1.0.0 → 3.0.0" in result.output

        # Check output file was created
        output_file = tmp_path / "test.promptrek.v3.yaml"
        assert output_file.exists()

        # Verify it's valid v3.0
        content = output_file.read_text()
        assert (
            "schema_version: 3.0.0" in content or 'schema_version: "3.0.0"' in content
        )
        assert "content:" in content

    def test_migrate_with_custom_output(self, tmp_path):
        """Test migration with custom output path."""
        v1_file = tmp_path / "input.promptrek.yaml"
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
    - "Test instruction"
"""
        )

        output_file = tmp_path / "custom-output.promptrek.yaml"
        runner = CliRunner()
        result = runner.invoke(cli, ["migrate", str(v1_file), "-o", str(output_file)])

        assert result.exit_code == 0
        assert output_file.exists()

    def test_migrate_v20_to_v30(self, tmp_path):
        """Test migrating v2.0.0 to v3.0.0."""
        v20_file = tmp_path / "test.promptrek.yaml"
        v20_file.write_text(
            """
schema_version: "2.0.0"
metadata:
  title: "Test"
  description: "V2.0 format"
  version: "1.0.0"
content: |
  # Test
  This is v2.0 format.
"""
        )

        runner = CliRunner()
        result = runner.invoke(cli, ["migrate", str(v20_file)])

        assert result.exit_code == 0
        assert "2.0.0 → 3.0.0" in result.output

        # Check output file
        output_file = tmp_path / "test.promptrek.v3.yaml"
        assert output_file.exists()
        content = output_file.read_text()
        assert (
            "schema_version: 3.0.0" in content or 'schema_version: "3.0.0"' in content
        )

    def test_migrate_already_v3(self, tmp_path):
        """Test migrating a file that's already v3.0."""
        v3_file = tmp_path / "test.promptrek.yaml"
        v3_file.write_text(
            """
schema_version: "3.0.0"
metadata:
  title: "Test"
  description: "Already v3.0"
  version: "1.0.0"
content: |
  # Test
  This is v3.0 format.
"""
        )

        runner = CliRunner()
        result = runner.invoke(cli, ["migrate", str(v3_file)])

        assert result.exit_code == 0
        assert "already v3.x format" in result.output

    def test_migrate_output_exists_no_force(self, tmp_path):
        """Test migration fails when output exists without --force."""
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

        # Create existing output file
        output_file = tmp_path / "test.promptrek.v3.yaml"
        output_file.write_text("existing content")

        runner = CliRunner()
        result = runner.invoke(cli, ["migrate", str(v1_file)])

        assert result.exit_code == 1
        assert "already exists" in result.output

    def test_migrate_with_all_instruction_categories(self, tmp_path):
        """Test migration with all instruction categories."""
        v1_file = tmp_path / "test.promptrek.yaml"
        v1_file.write_text(
            """
schema_version: "1.0.0"
metadata:
  title: "Full Test"
  description: "Test all categories"
  version: "1.0.0"
  author: "Test"
  created: "2024-01-01"
  updated: "2024-01-01"
targets:
  - claude
context:
  project_type: "application"
  technologies:
    - Python
instructions:
  general:
    - "General instruction"
  code_style:
    - "Code style rule"
  architecture:
    - "Architecture guideline"
  testing:
    - "Testing standard"
  security:
    - "Security requirement"
  performance:
    - "Performance guideline"
"""
        )

        runner = CliRunner()
        result = runner.invoke(cli, ["migrate", str(v1_file)])

        assert result.exit_code == 0

        # Check output file
        output_file = tmp_path / "test.promptrek.v3.yaml"
        content = output_file.read_text()

        # Verify all sections are present
        assert "Architecture Guidelines" in content
        assert "Testing Standards" in content
        assert "Security Requirements" in content
        assert "Performance Guidelines" in content

    def test_migrate_with_conditions(self, tmp_path):
        """Test migration with conditional instructions."""
        v1_file = tmp_path / "test.promptrek.yaml"
        v1_file.write_text(
            """
schema_version: "1.0.0"
metadata:
  title: "Test with Conditions"
  description: "Test"
  version: "1.0.0"
targets:
  - claude
instructions:
  general:
    - "Base instruction"
conditions:
  - if: "EDITOR == 'claude'"
    then:
      instructions:
        general:
          - "Claude-specific instruction"
"""
        )

        runner = CliRunner()
        result = runner.invoke(cli, ["migrate", str(v1_file)])

        assert result.exit_code == 0

        # Check output includes conditional note
        output_file = tmp_path / "test.promptrek.v3.yaml"
        content = output_file.read_text()
        assert "Conditional Instructions" in content

    def test_migrate_with_examples(self, tmp_path):
        """Test migration with code examples."""
        v1_file = tmp_path / "test.promptrek.yaml"
        v1_file.write_text(
            """
schema_version: "1.0.0"
metadata:
  title: "Test with Examples"
  description: "Test"
  version: "1.0.0"
targets:
  - claude
instructions:
  general:
    - "Test"
examples:
  python_example: |
    def hello():
        print("Hello")
  javascript_example: |
    function hello() {
        console.log("Hello");
    }
"""
        )

        runner = CliRunner()
        result = runner.invoke(cli, ["migrate", str(v1_file)])

        assert result.exit_code == 0

        # Check output includes examples
        output_file = tmp_path / "test.promptrek.v3.yaml"
        content = output_file.read_text()
        assert "Code Examples" in content
        assert "Python Example" in content or "python_example" in content.lower()

    def test_migrate_with_variables(self, tmp_path):
        """Test migration preserves variables."""
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
    - "Test instruction with {{{ PROJECT_NAME }}}"
variables:
  PROJECT_NAME: "MyProject"
"""
        )

        runner = CliRunner()
        result = runner.invoke(cli, ["migrate", str(v1_file)])

        assert result.exit_code == 0

        # Check variables are preserved
        output_file = tmp_path / "test.promptrek.v3.yaml"
        content = output_file.read_text()
        assert "variables:" in content
        assert "PROJECT_NAME" in content

    def test_migrate_output_exists_with_force(self, tmp_path):
        """Test migration overwrites when --force is used."""
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

        # Create existing output file
        output_file = tmp_path / "output.promptrek.yaml"
        output_file.write_text("existing content")

        runner = CliRunner()
        result = runner.invoke(
            cli,
            ["migrate", str(v1_file), "-o", str(output_file), "--force"],
        )

        assert result.exit_code == 0
        assert "✅ Migrated" in result.output

        # Verify file was overwritten
        new_content = output_file.read_text()
        assert new_content != "existing content"
        assert (
            "schema_version: 3.0.0" in new_content
            or 'schema_version: "3.0.0"' in new_content
        )

    def test_migrate_verbose(self, tmp_path):
        """Test migrate command with verbose output."""
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
        result = runner.invoke(cli, ["--verbose", "migrate", str(v1_file)])

        assert result.exit_code == 0
        assert "✅ Parsed" in result.output
        assert "Content length:" in result.output

    def test_migrate_invalid_file(self, tmp_path):
        """Test migrating an invalid file."""
        invalid_file = tmp_path / "invalid.promptrek.yaml"
        invalid_file.write_text(
            """
schema_version: "1.0.0"
metadata:
  title: "Test
  # Invalid YAML
"""
        )

        runner = CliRunner()
        result = runner.invoke(cli, ["migrate", str(invalid_file)])

        assert result.exit_code == 1
        assert "Failed to parse" in result.output or "Error" in result.output

    def test_migrate_nonexistent_file(self, tmp_path):
        """Test migrating a file that doesn't exist."""
        nonexistent = tmp_path / "nonexistent.promptrek.yaml"

        runner = CliRunner()
        result = runner.invoke(cli, ["migrate", str(nonexistent)])

        assert result.exit_code != 0
