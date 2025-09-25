"""Integration tests for multiple file processing functionality."""

from pathlib import Path

from click.testing import CliRunner

from src.promptrek.cli.main import cli


class TestMultipleFilesIntegration:
    """Test multiple file processing integration."""

    def test_multiple_files_explicit(self, tmp_path):
        """Test generating from multiple explicitly specified files."""
        # Create multiple test files
        file1 = tmp_path / "project.promptrek.yaml"
        file2 = tmp_path / "workflow.promptrek.yaml"
        
        file1_content = """
schema_version: 1.0.0
metadata:
  title: Project Assistant
  description: Main project configuration
  version: 1.0.0
  author: Test Author
  created: '2024-01-01'
  updated: '2024-01-01'
targets:
  - copilot
instructions:
  general:
    - Write clean code
    - Follow conventions
"""
        
        file2_content = """
schema_version: 1.0.0
metadata:
  title: Workflow Assistant
  description: Development workflow configuration
  version: 1.0.0
  author: Test Author
  created: '2024-01-01'
  updated: '2024-01-01'
targets:
  - copilot
instructions:
  general:
    - Follow git workflow
    - Create feature branches
"""
        
        file1.write_text(file1_content)
        file2.write_text(file2_content)
        
        runner = CliRunner()
        with runner.isolated_filesystem():
            result = runner.invoke(
                cli,
                ["generate", "--editor", "copilot", str(file1), str(file2)],
            )
        
        assert result.exit_code == 0
        assert "Generated merged" in result.output
        assert "from 2 files" in result.output

    def test_directory_scanning(self, tmp_path):
        """Test generating from directory scanning."""
        # Create multiple test files in directory
        file1 = tmp_path / "project.promptrek.yaml"
        file2 = tmp_path / "workflow.promptrek.yaml"
        
        file1_content = """
schema_version: 1.0.0
metadata:
  title: Project Assistant
  description: Main project configuration
  version: 1.0.0
  author: Test Author
  created: '2024-01-01'
  updated: '2024-01-01'
targets:
  - copilot
instructions:
  general:
    - Write clean code
"""
        
        file2_content = """
schema_version: 1.0.0
metadata:
  title: Workflow Assistant
  description: Development workflow configuration
  version: 1.0.0
  author: Test Author
  created: '2024-01-01'
  updated: '2024-01-01'
targets:
  - copilot
instructions:
  general:
    - Follow git workflow
"""
        
        file1.write_text(file1_content)
        file2.write_text(file2_content)
        
        runner = CliRunner()
        result = runner.invoke(
            cli,
            ["--verbose", "generate", "--editor", "copilot", "--directory", str(tmp_path)],
        )
        
        assert result.exit_code == 0
        assert "Found 2 UPF files" in result.output
        assert "Generated merged" in result.output

    def test_single_file_backward_compatibility(self, tmp_path):
        """Test that single file generation still works (backward compatibility)."""
        file1 = tmp_path / "project.promptrek.yaml"
        
        file1_content = """
schema_version: 1.0.0
metadata:
  title: Project Assistant
  description: Main project configuration
  version: 1.0.0
  author: Test Author
  created: '2024-01-01'
  updated: '2024-01-01'
targets:
  - copilot
instructions:
  general:
    - Write clean code
"""
        
        file1.write_text(file1_content)
        
        runner = CliRunner()
        result = runner.invoke(
            cli,
            ["generate", "--editor", "copilot", str(file1)],
        )
        
        assert result.exit_code == 0
        assert "Generated:" in result.output
        # Should not mention merging for single file
        assert "merged" not in result.output.lower()

    def test_fallback_for_non_merging_adapters(self, tmp_path):
        """Test fallback behavior for adapters that don't support merging."""
        # Create multiple test files
        file1 = tmp_path / "project.promptrek.yaml"
        file2 = tmp_path / "workflow.promptrek.yaml"
        
        file1_content = """
schema_version: 1.0.0
metadata:
  title: Project Assistant
  description: Main project configuration
  version: 1.0.0
  author: Test Author
  created: '2024-01-01'
  updated: '2024-01-01'
targets:
  - continue
instructions:
  general:
    - Write clean code
"""
        
        file2_content = """
schema_version: 1.0.0
metadata:
  title: Workflow Assistant
  description: Development workflow configuration
  version: 1.0.0
  author: Test Author
  created: '2024-01-01'
  updated: '2024-01-01'
targets:
  - continue
instructions:
  general:
    - Follow git workflow
"""
        
        file1.write_text(file1_content)
        file2.write_text(file2_content)
        
        runner = CliRunner()
        result = runner.invoke(
            cli,
            ["generate", "--editor", "continue", str(file1), str(file2)],
        )
        
        assert result.exit_code == 0
        assert "doesn't support merging" in result.output
        assert "other files ignored" in result.output

    def test_no_files_found_error(self, tmp_path):
        """Test error when no UPF files are found."""
        # Create empty directory
        empty_dir = tmp_path / "empty"
        empty_dir.mkdir()
        
        runner = CliRunner()
        result = runner.invoke(
            cli,
            ["generate", "--editor", "copilot", "--directory", str(empty_dir)],
        )
        
        assert result.exit_code == 1
        assert "No UPF files found" in result.output

    def test_mixed_targets_filtering(self, tmp_path):
        """Test that files are properly filtered by target editor."""
        # Create files with different targets
        file1 = tmp_path / "copilot-only.promptrek.yaml"
        file2 = tmp_path / "cursor-only.promptrek.yaml"
        file3 = tmp_path / "both.promptrek.yaml"
        
        file1_content = """
schema_version: 1.0.0
metadata:
  title: Copilot Only 
  description: Copilot-specific configuration
  version: 1.0.0
  author: Test Author
  created: '2024-01-01'
  updated: '2024-01-01'
targets:
  - copilot
instructions:
  general:
    - Copilot instruction
"""
        
        file2_content = """
schema_version: 1.0.0
metadata:
  title: Cursor Only
  description: Cursor-specific configuration
  version: 1.0.0
  author: Test Author
  created: '2024-01-01'
  updated: '2024-01-01'
targets:
  - cursor
instructions:
  general:
    - Cursor instruction
"""
        
        file3_content = """
schema_version: 1.0.0
metadata:
  title: Both Editors
  description: Configuration for both editors
  version: 1.0.0
  author: Test Author
  created: '2024-01-01'
  updated: '2024-01-01'
targets:
  - copilot
  - cursor
instructions:
  general:
    - Shared instruction
"""
        
        file1.write_text(file1_content)
        file2.write_text(file2_content)
        file3.write_text(file3_content)
        
        runner = CliRunner()
        result = runner.invoke(
            cli,
            ["--verbose", "generate", "--editor", "copilot", "--directory", str(tmp_path)],
        )
        
        assert result.exit_code == 0
        # Should process file1 and file3, but skip file2 (cursor-only)
        assert "Generated merged" in result.output
        assert "from 2 files" in result.output  # file1 + file3

    def test_claude_multiple_files_separate_generation(self, tmp_path):
        """Test that Claude adapter generates separate files for multiple prompts."""
        # Create multiple test files for Claude
        file1 = tmp_path / "main.promptrek.yaml"
        file2 = tmp_path / "workflows.promptrek.yaml"
        
        file1_content = """
schema_version: 1.0.0
metadata:
  title: Main Project
  description: Main project configuration
  version: 1.0.0
  author: Test Author
  created: '2024-01-01'
  updated: '2024-01-01'
targets:
  - claude
context:
  project_type: web_application
  technologies:
    - typescript
    - react
instructions:
  general:
    - Write clean code
    - Follow conventions
examples:
  test_function: |
    ```typescript
    function test() { return true; }
    ```
"""
        
        file2_content = """
schema_version: 1.0.0
metadata:
  title: Development Workflows
  description: Team workflow guidelines
  version: 1.0.0
  author: Test Author
  created: '2024-01-01'
  updated: '2024-01-01'
targets:
  - claude
context:
  project_type: workflow
  technologies:
    - git
    - ci-cd
instructions:
  general:
    - Follow git workflow
    - Create detailed PRs
"""
        
        file1.write_text(file1_content)
        file2.write_text(file2_content)
        
        runner = CliRunner()
        with runner.isolated_filesystem():
            result = runner.invoke(
                cli,
                ["--verbose", "generate", "--editor", "claude", str(file1), str(file2)],
            )
        
        assert result.exit_code == 0
        assert "Generated separate claude files" in result.output
        # Should mention both source files
        assert "main.promptrek.yaml" in result.output
        assert "workflows.promptrek.yaml" in result.output