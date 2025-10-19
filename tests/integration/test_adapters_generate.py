"""Test adapter generation for all editors."""

from pathlib import Path

import pytest
from click.testing import CliRunner

from promptrek.cli.main import cli


class TestAllAdaptersGenerate:
    """Test generation for all 9 adapters."""

    @pytest.fixture
    def v2_prompt_file(self, tmp_path):
        """Create a v2 prompt file for testing."""
        upf_file = tmp_path / "test.promptrek.yaml"
        upf_file.write_text(
            """
schema_version: "2.0.0"
metadata:
  title: "Test Project"
  description: "Test for all editors"
  version: "1.0.0"
  author: "Test Author"
  tags: ["test", "ai"]
content: |
  # Test Project
  
  ## Guidelines
  - Write clean code
  - Add tests
  - Follow best practices
  
  ## Examples
  ```python
  def example():
      pass
  ```
variables:
  PROJECT_NAME: "TestProject"
"""
        )
        return upf_file

    def test_generate_cline(self, v2_prompt_file, tmp_path):
        """Test Cline adapter generation."""
        runner = CliRunner()
        result = runner.invoke(
            cli,
            ["generate", str(v2_prompt_file), "--editor", "cline", "-o", str(tmp_path)],
        )

        assert result.exit_code == 0

    def test_generate_kiro(self, v2_prompt_file, tmp_path):
        """Test Kiro adapter generation."""
        runner = CliRunner()
        result = runner.invoke(
            cli,
            ["generate", str(v2_prompt_file), "--editor", "kiro", "-o", str(tmp_path)],
        )

        assert result.exit_code == 0

    def test_generate_jetbrains(self, v2_prompt_file, tmp_path):
        """Test JetBrains adapter generation."""
        runner = CliRunner()
        result = runner.invoke(
            cli,
            [
                "generate",
                str(v2_prompt_file),
                "--editor",
                "jetbrains",
                "-o",
                str(tmp_path),
            ],
        )

        assert result.exit_code == 0

    def test_generate_amazonq(self, v2_prompt_file, tmp_path):
        """Test Amazon Q adapter generation."""
        runner = CliRunner()
        result = runner.invoke(
            cli,
            [
                "generate",
                str(v2_prompt_file),
                "--editor",
                "amazonq",
                "-o",
                str(tmp_path),
            ],
        )

        assert result.exit_code == 0

    def test_generate_all_at_once(self, v2_prompt_file, tmp_path):
        """Test generating for all editors at once."""
        runner = CliRunner()
        result = runner.invoke(
            cli, ["generate", str(v2_prompt_file), "--all", "-o", str(tmp_path)]
        )

        assert result.exit_code == 0
        # Should have created files for multiple editors
        assert any(tmp_path.rglob("*"))

    def test_generate_with_all_variable_types(self, tmp_path):
        """Test generation with various variable types."""
        upf_file = tmp_path / "test.promptrek.yaml"
        upf_file.write_text(
            """
schema_version: "2.0.0"
metadata:
  title: "Variable Test"
  description: "Test all variable types"
  version: "1.0.0"
content: |
  Project: {{{ PROJECT_NAME }}}
  Version: {{{ VERSION }}}
  API Key: {{{ API_KEY }}}
  Database: {{{ DB_URL }}}
variables:
  PROJECT_NAME: "MyProject"
  VERSION: "1.0.0"
  API_KEY: "test-key"
  DB_URL: "postgresql://localhost"
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
                "API_KEY=override-key",
            ],
        )

        assert result.exit_code == 0

    def test_generate_v1_all_instruction_categories(self, tmp_path):
        """Test v1 generation with all instruction categories."""
        upf_file = tmp_path / "test.promptrek.yaml"
        upf_file.write_text(
            """
schema_version: "1.0.0"
metadata:
  title: "Full V1 Test"
  description: "Test all v1 features"
  version: "1.0.0"
targets:
  - claude
  - cursor
context:
  project_type: "web_application"
  technologies:
    - Python
    - React
instructions:
  general:
    - "General instruction 1"
    - "General instruction 2"
  code_style:
    - "Use PEP 8"
    - "Add docstrings"
  architecture:
    - "Use MVC pattern"
  testing:
    - "Write unit tests"
  security:
    - "Validate inputs"
  performance:
    - "Optimize queries"
examples:
  function: |
    def example():
        return True
variables:
  ENV: "test"
"""
        )

        runner = CliRunner()
        result = runner.invoke(
            cli, ["generate", str(upf_file), "--editor", "claude", "-o", str(tmp_path)]
        )

        assert result.exit_code == 0
