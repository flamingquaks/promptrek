"""
Unit tests for gitignore utility functions.
"""

import subprocess
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import pytest

from promptrek.utils.gitignore import (
    add_patterns_to_gitignore,
    configure_gitignore,
    get_editor_file_patterns,
    read_gitignore,
    remove_cached_files,
)


class TestGetEditorFilePatterns:
    """Tests for get_editor_file_patterns function."""

    def test_returns_list_of_patterns(self):
        """Should return a list of file patterns."""
        patterns = get_editor_file_patterns()
        assert isinstance(patterns, list)
        assert len(patterns) > 0

    def test_includes_common_editor_patterns(self):
        """Should include patterns for common editors."""
        patterns = get_editor_file_patterns()

        # Check for key patterns
        assert ".github/copilot-instructions.md" in patterns
        assert ".cursor/rules/*.mdc" in patterns
        assert ".continue/rules/*.md" in patterns
        assert ".windsurf/rules/*.md" in patterns
        assert ".clinerules" in patterns


class TestReadGitignore:
    """Tests for read_gitignore function."""

    def test_returns_empty_set_for_nonexistent_file(self, tmp_path):
        """Should return empty set if .gitignore doesn't exist."""
        gitignore_path = tmp_path / ".gitignore"
        patterns = read_gitignore(gitignore_path)
        assert patterns == set()

    def test_reads_patterns_from_file(self, tmp_path):
        """Should read patterns from .gitignore file."""
        gitignore_path = tmp_path / ".gitignore"
        gitignore_path.write_text("*.pyc\n__pycache__\n.env\n")

        patterns = read_gitignore(gitignore_path)
        assert patterns == {"*.pyc", "__pycache__", ".env"}

    def test_ignores_comments_and_empty_lines(self, tmp_path):
        """Should ignore comments and empty lines."""
        gitignore_path = tmp_path / ".gitignore"
        gitignore_path.write_text("# Comment\n*.pyc\n\n__pycache__\n# Another comment\n")

        patterns = read_gitignore(gitignore_path)
        assert patterns == {"*.pyc", "__pycache__"}

    def test_handles_whitespace(self, tmp_path):
        """Should handle whitespace correctly."""
        gitignore_path = tmp_path / ".gitignore"
        gitignore_path.write_text("  *.pyc  \n__pycache__\n")

        patterns = read_gitignore(gitignore_path)
        assert patterns == {"*.pyc", "__pycache__"}


class TestAddPatternsToGitignore:
    """Tests for add_patterns_to_gitignore function."""

    def test_creates_new_gitignore_file(self, tmp_path):
        """Should create new .gitignore file if it doesn't exist."""
        gitignore_path = tmp_path / ".gitignore"
        patterns = ["*.pyc", "__pycache__"]

        count = add_patterns_to_gitignore(gitignore_path, patterns)

        assert count == 2
        assert gitignore_path.exists()
        content = gitignore_path.read_text()
        assert "*.pyc" in content
        assert "__pycache__" in content

    def test_adds_patterns_to_existing_file(self, tmp_path):
        """Should append patterns to existing .gitignore file."""
        gitignore_path = tmp_path / ".gitignore"
        gitignore_path.write_text("*.pyc\n")

        patterns = ["__pycache__", ".env"]
        count = add_patterns_to_gitignore(gitignore_path, patterns)

        assert count == 2
        content = gitignore_path.read_text()
        assert "*.pyc" in content
        assert "__pycache__" in content
        assert ".env" in content

    def test_skips_existing_patterns(self, tmp_path):
        """Should not add patterns that already exist."""
        gitignore_path = tmp_path / ".gitignore"
        gitignore_path.write_text("*.pyc\n__pycache__\n")

        patterns = ["*.pyc", ".env"]
        count = add_patterns_to_gitignore(gitignore_path, patterns)

        assert count == 1  # Only .env should be added
        content = gitignore_path.read_text()
        assert content.count("*.pyc") == 1  # Should not duplicate

    def test_adds_comment_when_provided(self, tmp_path):
        """Should add comment before patterns."""
        gitignore_path = tmp_path / ".gitignore"
        patterns = ["*.pyc"]
        comment = "Python cache files"

        count = add_patterns_to_gitignore(gitignore_path, patterns, comment)

        assert count == 1
        content = gitignore_path.read_text()
        assert f"# {comment}" in content

    def test_ensures_newline_before_appending(self, tmp_path):
        """Should ensure existing file ends with newline before appending."""
        gitignore_path = tmp_path / ".gitignore"
        gitignore_path.write_text("*.pyc")  # No trailing newline

        patterns = [".env"]
        count = add_patterns_to_gitignore(gitignore_path, patterns)

        assert count == 1
        content = gitignore_path.read_text()
        # Should have added newline before .env
        assert "*.pyc\n" in content or "*.pyc\n\n" in content

    def test_returns_zero_when_no_patterns_to_add(self, tmp_path):
        """Should return 0 when all patterns already exist."""
        gitignore_path = tmp_path / ".gitignore"
        gitignore_path.write_text("*.pyc\n.env\n")

        patterns = ["*.pyc", ".env"]
        count = add_patterns_to_gitignore(gitignore_path, patterns)

        assert count == 0


class TestRemoveCachedFiles:
    """Tests for remove_cached_files function."""

    def test_returns_empty_list_when_not_git_repo(self, tmp_path):
        """Should return empty list if not in a git repository."""
        patterns = ["*.md"]
        removed = remove_cached_files(patterns, tmp_path)

        assert removed == []

    @patch("subprocess.run")
    def test_removes_tracked_files_from_cache(self, mock_run, tmp_path):
        """Should remove tracked files matching patterns from git cache."""
        # Setup git directory
        (tmp_path / ".git").mkdir()

        # Track which pattern we're processing
        call_count = [0]

        # Configure mock to return different results based on pattern
        def run_side_effect(*args, **kwargs):
            command = args[0]
            if "ls-files" in command:
                # First pattern returns one file, second returns another
                if call_count[0] == 0:
                    result = Mock()
                    result.returncode = 0
                    result.stdout = ".github/copilot-instructions.md\n"
                    call_count[0] += 1
                    return result
                else:
                    result = Mock()
                    result.returncode = 0
                    result.stdout = ".cursor/rules/index.mdc\n"
                    return result
            elif "rm" in command:
                result = Mock()
                result.returncode = 0
                return result
            return Mock(returncode=1)

        mock_run.side_effect = run_side_effect

        patterns = [".github/copilot-instructions.md", ".cursor/rules/*.mdc"]
        removed = remove_cached_files(patterns, tmp_path)

        assert len(removed) == 2
        assert ".github/copilot-instructions.md" in removed
        assert ".cursor/rules/index.mdc" in removed

    @patch("subprocess.run")
    def test_handles_git_command_failures_gracefully(self, mock_run, tmp_path):
        """Should handle git command failures gracefully."""
        (tmp_path / ".git").mkdir()

        # Mock git ls-files to fail
        ls_files_result = Mock()
        ls_files_result.returncode = 1
        ls_files_result.stdout = ""

        mock_run.return_value = ls_files_result

        patterns = ["*.md"]
        removed = remove_cached_files(patterns, tmp_path)

        assert removed == []

    @patch("subprocess.run")
    def test_skips_patterns_with_no_matches(self, mock_run, tmp_path):
        """Should skip patterns that don't match any files."""
        (tmp_path / ".git").mkdir()

        # Mock git ls-files to return empty
        ls_files_result = Mock()
        ls_files_result.returncode = 0
        ls_files_result.stdout = ""

        mock_run.return_value = ls_files_result

        patterns = ["nonexistent/*.md"]
        removed = remove_cached_files(patterns, tmp_path)

        assert removed == []


class TestConfigureGitignore:
    """Tests for configure_gitignore function."""

    @patch("promptrek.utils.gitignore.add_patterns_to_gitignore")
    @patch("promptrek.utils.gitignore.remove_cached_files")
    def test_adds_editor_patterns_when_requested(
        self, mock_remove, mock_add, tmp_path
    ):
        """Should add editor file patterns when add_editor_files is True."""
        mock_add.return_value = 5
        mock_remove.return_value = []

        result = configure_gitignore(tmp_path, add_editor_files=True)

        assert result["patterns_added"] == 5
        assert mock_add.called

    @patch("promptrek.utils.gitignore.add_patterns_to_gitignore")
    @patch("promptrek.utils.gitignore.remove_cached_files")
    def test_removes_cached_files_when_requested(
        self, mock_remove, mock_add, tmp_path
    ):
        """Should remove cached files when remove_cached is True."""
        mock_add.return_value = 5
        mock_remove.return_value = ["file1.md", "file2.md"]

        result = configure_gitignore(
            tmp_path, add_editor_files=True, remove_cached=True
        )

        assert result["files_removed"] == ["file1.md", "file2.md"]
        assert mock_remove.called

    @patch("promptrek.utils.gitignore.add_patterns_to_gitignore")
    def test_adds_custom_patterns(self, mock_add, tmp_path):
        """Should add custom patterns when provided."""
        mock_add.return_value = 2
        custom_patterns = ["custom1.txt", "custom2.txt"]

        result = configure_gitignore(
            tmp_path, add_editor_files=False, custom_patterns=custom_patterns
        )

        assert mock_add.called
        call_args = mock_add.call_args
        patterns = call_args[0][1]
        assert "custom1.txt" in patterns
        assert "custom2.txt" in patterns

    @patch("promptrek.utils.gitignore.add_patterns_to_gitignore")
    @patch("promptrek.utils.gitignore.remove_cached_files")
    def test_combines_editor_and_custom_patterns(
        self, mock_remove, mock_add, tmp_path
    ):
        """Should combine editor and custom patterns when both requested."""
        mock_add.return_value = 10
        mock_remove.return_value = []
        custom_patterns = ["custom.txt"]

        result = configure_gitignore(
            tmp_path, add_editor_files=True, custom_patterns=custom_patterns
        )

        assert mock_add.called
        call_args = mock_add.call_args
        patterns = call_args[0][1]
        # Should include both editor patterns and custom patterns
        assert len(patterns) > 1
        assert "custom.txt" in patterns

    @patch("promptrek.utils.gitignore.add_patterns_to_gitignore")
    def test_returns_correct_result_structure(self, mock_add, tmp_path):
        """Should return result dict with correct structure."""
        mock_add.return_value = 3

        result = configure_gitignore(tmp_path, add_editor_files=True)

        assert "patterns_added" in result
        assert "files_removed" in result
        assert isinstance(result["patterns_added"], int)
        assert isinstance(result["files_removed"], list)
