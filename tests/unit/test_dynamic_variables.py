"""Tests for dynamic variables functionality."""

import subprocess
from datetime import datetime
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import pytest

from promptrek.core.exceptions import TemplateError
from promptrek.utils.variables import (
    BuiltInVariables,
    CommandExecutor,
    DynamicVariable,
    VariableSubstitution,
)


class TestCommandExecutor:
    """Test CommandExecutor class."""

    def test_init_default_values(self):
        """Test executor initialization with default values."""
        executor = CommandExecutor()
        assert executor.allow_commands is False
        assert executor.timeout == 5
        assert executor.verbose is False

    def test_init_custom_values(self):
        """Test executor initialization with custom values."""
        executor = CommandExecutor(allow_commands=True, timeout=10, verbose=True)
        assert executor.allow_commands is True
        assert executor.timeout == 10
        assert executor.verbose is True

    def test_execute_raises_when_disabled(self):
        """Test that execute raises error when commands are disabled."""
        executor = CommandExecutor(allow_commands=False)
        with pytest.raises(TemplateError, match="Command execution is disabled"):
            executor.execute("echo test")

    @patch("promptrek.utils.variables.subprocess.run")
    def test_execute_success(self, mock_run):
        """Test successful command execution."""
        mock_result = Mock()
        mock_result.stdout = "test output\n"
        mock_run.return_value = mock_result

        executor = CommandExecutor(allow_commands=True)
        result = executor.execute("echo test")

        assert result == "test output"
        mock_run.assert_called_once()

    @patch("promptrek.utils.variables.subprocess.run")
    def test_execute_timeout(self, mock_run):
        """Test command execution timeout."""
        mock_run.side_effect = subprocess.TimeoutExpired("cmd", 5)

        executor = CommandExecutor(allow_commands=True, timeout=5)
        with pytest.raises(TemplateError, match="Command timed out"):
            executor.execute("sleep 10")

    @patch("promptrek.utils.variables.subprocess.run")
    def test_execute_failure(self, mock_run):
        """Test command execution failure."""
        mock_error = subprocess.CalledProcessError(1, "cmd", stderr="error message")
        mock_run.side_effect = mock_error

        executor = CommandExecutor(allow_commands=True)
        with pytest.raises(TemplateError, match="Command failed"):
            executor.execute("false")


class TestDynamicVariable:
    """Test DynamicVariable class."""

    def test_init(self):
        """Test dynamic variable initialization."""
        var = DynamicVariable(name="TEST", command="echo test", cache=True)
        assert var.name == "TEST"
        assert var.command == "echo test"
        assert var.cache is True
        assert var._cached_value is None

    @patch("promptrek.utils.variables.subprocess.run")
    def test_evaluate_no_cache(self, mock_run):
        """Test evaluating a non-cached variable."""
        mock_result = Mock()
        mock_result.stdout = "test value"
        mock_run.return_value = mock_result

        executor = CommandExecutor(allow_commands=True)
        var = DynamicVariable(name="TEST", command="echo test", cache=False)

        result1 = var.evaluate(executor)
        result2 = var.evaluate(executor)

        assert result1 == "test value"
        assert result2 == "test value"
        assert mock_run.call_count == 2  # Called twice (not cached)

    @patch("promptrek.utils.variables.subprocess.run")
    def test_evaluate_with_cache(self, mock_run):
        """Test evaluating a cached variable."""
        mock_result = Mock()
        mock_result.stdout = "cached value"
        mock_run.return_value = mock_result

        executor = CommandExecutor(allow_commands=True)
        var = DynamicVariable(name="TEST", command="echo test", cache=True)

        result1 = var.evaluate(executor)
        result2 = var.evaluate(executor)

        assert result1 == "cached value"
        assert result2 == "cached value"
        assert mock_run.call_count == 1  # Called once (cached)

    def test_clear_cache(self):
        """Test clearing cached value."""
        var = DynamicVariable(name="TEST", command="echo test", cache=True)
        var._cached_value = "old value"

        var.clear_cache()

        assert var._cached_value is None


class TestBuiltInVariables:
    """Test BuiltInVariables class."""

    def test_get_all_returns_dict(self):
        """Test that get_all returns a dictionary."""
        vars_dict = BuiltInVariables.get_all()
        assert isinstance(vars_dict, dict)

    def test_get_all_includes_date_variables(self):
        """Test that date/time variables are included."""
        vars_dict = BuiltInVariables.get_all()

        assert "CURRENT_DATE" in vars_dict
        assert "CURRENT_TIME" in vars_dict
        assert "CURRENT_DATETIME" in vars_dict
        assert "CURRENT_YEAR" in vars_dict
        assert "CURRENT_MONTH" in vars_dict
        assert "CURRENT_DAY" in vars_dict

    def test_get_all_includes_project_variables(self):
        """Test that project context variables are included."""
        vars_dict = BuiltInVariables.get_all()

        assert "PROJECT_NAME" in vars_dict
        assert "PROJECT_ROOT" in vars_dict

    def test_date_format(self):
        """Test that date variables have correct format."""
        now = datetime.now()
        vars_dict = BuiltInVariables.get_all()

        # Check CURRENT_DATE format (YYYY-MM-DD)
        assert vars_dict["CURRENT_DATE"] == now.strftime("%Y-%m-%d")

        # Check CURRENT_YEAR format
        assert vars_dict["CURRENT_YEAR"] == now.strftime("%Y")

    @patch("promptrek.utils.variables.subprocess.run")
    def test_project_name_from_git_repo(self, mock_run):
        """Test that PROJECT_NAME is derived from git repository name."""
        # Mock successful git commands returning repository URL
        mock_run.side_effect = [
            Mock(returncode=0, stdout="", stderr=""),  # is-inside-work-tree
            Mock(
                returncode=0, stdout="https://github.com/user/my-repo.git\n", stderr=""
            ),  # remote get-url
        ]

        project_name = BuiltInVariables._get_project_name()
        assert project_name == "my-repo"

    @patch("promptrek.utils.variables.subprocess.run")
    def test_project_name_from_ssh_git_url(self, mock_run):
        """Test that PROJECT_NAME is derived from SSH git URL format."""
        # Mock successful git commands returning SSH repository URL
        mock_run.side_effect = [
            Mock(returncode=0, stdout="", stderr=""),  # is-inside-work-tree
            Mock(
                returncode=0, stdout="git@github.com:user/my-repo.git\n", stderr=""
            ),  # remote get-url
        ]

        project_name = BuiltInVariables._get_project_name()
        assert project_name == "my-repo"

    @patch("promptrek.utils.variables.subprocess.run")
    def test_project_name_from_https_url_no_git_suffix(self, mock_run):
        """Test that PROJECT_NAME is derived from HTTPS URL without .git suffix."""
        # Mock successful git commands returning repository URL without .git
        mock_run.side_effect = [
            Mock(returncode=0, stdout="", stderr=""),  # is-inside-work-tree
            Mock(
                returncode=0, stdout="https://github.com/user/my-repo\n", stderr=""
            ),  # remote get-url
        ]

        project_name = BuiltInVariables._get_project_name()
        assert project_name == "my-repo"

    @patch("promptrek.utils.variables.subprocess.run")
    def test_project_name_fallback_to_directory(self, mock_run):
        """Test that PROJECT_NAME falls back to directory name when not in git repo."""
        # Mock git command failing (not in repo)
        mock_run.return_value = Mock(returncode=1, stdout="", stderr="")

        project_name = BuiltInVariables._get_project_name()
        expected_name = Path.cwd().name
        assert project_name == expected_name

    @patch("promptrek.utils.variables.subprocess.run")
    def test_project_name_when_git_not_installed(self, mock_run):
        """Test that PROJECT_NAME falls back to directory name when git is not installed."""
        # Mock FileNotFoundError (git command not found)
        mock_run.side_effect = FileNotFoundError("git not found")

        project_name = BuiltInVariables._get_project_name()
        expected_name = Path.cwd().name
        assert project_name == expected_name

    @patch("promptrek.utils.variables.subprocess.run")
    def test_project_name_when_git_times_out(self, mock_run):
        """Test that PROJECT_NAME falls back to directory name when git command times out."""
        # Mock timeout
        mock_run.side_effect = subprocess.TimeoutExpired("git", 2)

        project_name = BuiltInVariables._get_project_name()
        expected_name = Path.cwd().name
        assert project_name == expected_name
        # Ensure subprocess.run was called and the exception was handled
        assert mock_run.call_count > 0

    @patch("promptrek.utils.variables.subprocess.run")
    def test_get_git_variables_when_in_repo(self, mock_run):
        """Test git variables when in a git repository."""
        # Mock successful git commands
        mock_results = [
            Mock(returncode=0, stdout="", stderr=""),  # is-inside-work-tree
            Mock(stdout="main\n", stderr=""),  # branch name
            Mock(stdout="abc1234\n", stderr=""),  # short commit hash
        ]
        mock_run.side_effect = mock_results

        vars_dict = BuiltInVariables._get_git_variables()

        assert "GIT_BRANCH" in vars_dict
        assert "GIT_COMMIT_SHORT" in vars_dict
        assert vars_dict["GIT_BRANCH"] == "main"
        assert vars_dict["GIT_COMMIT_SHORT"] == "abc1234"

    @patch("promptrek.utils.variables.subprocess.run")
    def test_get_git_variables_when_not_in_repo(self, mock_run):
        """Test git variables when not in a git repository."""
        # Mock failed git command
        mock_run.return_value = Mock(returncode=1, stdout="", stderr="")

        vars_dict = BuiltInVariables._get_git_variables()

    @patch("promptrek.utils.variables.subprocess.run")
    def test_get_git_variables_when_git_times_out(self, mock_run):
        """Test that git variables fallback gracefully when git command times out."""
        mock_run.side_effect = subprocess.TimeoutExpired("git", 2)

        vars_dict = BuiltInVariables._get_git_variables()
        assert vars_dict == {}
        assert mock_run.called  # Ensure the timeout logic was exercised
        vars_dict = BuiltInVariables._get_git_variables()
        assert vars_dict == {}


class TestVariableSubstitutionWithDynamicVars:
    """Test VariableSubstitution with dynamic variables."""

    @patch("promptrek.utils.variables.subprocess.run")
    def test_load_and_evaluate_variables_with_builtins(
        self, mock_run, tmp_path, monkeypatch
    ):
        """Test loading variables with built-ins enabled."""
        monkeypatch.chdir(tmp_path)

        var_sub = VariableSubstitution()
        vars_dict = var_sub.load_and_evaluate_variables(
            allow_commands=False, include_builtins=True
        )

        assert "CURRENT_DATE" in vars_dict
        assert "PROJECT_NAME" in vars_dict

    @patch("promptrek.utils.variables.subprocess.run")
    def test_load_and_evaluate_without_builtins(self, mock_run, tmp_path, monkeypatch):
        """Test loading variables without built-ins."""
        monkeypatch.chdir(tmp_path)

        var_sub = VariableSubstitution()
        vars_dict = var_sub.load_and_evaluate_variables(
            allow_commands=False, include_builtins=False
        )

        assert "CURRENT_DATE" not in vars_dict
        assert "PROJECT_NAME" not in vars_dict

    @patch("promptrek.utils.variables.subprocess.run")
    def test_load_and_evaluate_with_dynamic_vars(self, mock_run, tmp_path, monkeypatch):
        """Test loading and evaluating dynamic variables."""
        monkeypatch.chdir(tmp_path)

        # Create .promptrek directory and variables file
        promptrek_dir = tmp_path / ".promptrek"
        promptrek_dir.mkdir()
        var_file = promptrek_dir / "variables.promptrek.yaml"

        var_file.write_text(
            """
STATIC_VAR: static value
DYNAMIC_VAR:
  type: command
  value: echo dynamic
  cache: false
"""
        )

        # Mock command execution
        mock_result = Mock()
        mock_result.stdout = "dynamic output"
        mock_run.return_value = mock_result

        var_sub = VariableSubstitution()
        vars_dict = var_sub.load_and_evaluate_variables(
            allow_commands=True, include_builtins=False
        )

        assert vars_dict["STATIC_VAR"] == "static value"
        assert vars_dict["DYNAMIC_VAR"] == "dynamic output"

    def test_load_and_evaluate_without_allow_commands(self, tmp_path, monkeypatch):
        """Test that dynamic variables fail without allow_commands."""
        monkeypatch.chdir(tmp_path)

        # Create .promptrek directory and variables file with dynamic var
        promptrek_dir = tmp_path / ".promptrek"
        promptrek_dir.mkdir()
        var_file = promptrek_dir / "variables.promptrek.yaml"

        var_file.write_text(
            """
DYNAMIC_VAR:
  type: command
  value: echo test
"""
        )

        var_sub = VariableSubstitution()
        vars_dict = var_sub.load_and_evaluate_variables(
            allow_commands=False,  # Commands disabled
            include_builtins=False,
            verbose=False,
        )

        # Dynamic variable should not be in the result (failed to evaluate)
        assert "DYNAMIC_VAR" not in vars_dict


class TestVariablePriority:
    """Test variable priority chain: CLI > File > Inline > Built-in."""

    def test_builtin_variable_baseline(self, tmp_path):
        """Test that built-in variables are available."""
        var_sub = VariableSubstitution()

        # Change to temp directory to isolate from real git repo
        import os

        original_cwd = Path.cwd()
        try:
            os.chdir(tmp_path)

            # Load with built-ins enabled
            vars_dict = var_sub.load_and_evaluate_variables(
                search_dir=tmp_path,
                include_builtins=True,
                allow_commands=False,
            )

            # Built-in variables should be present
            assert "CURRENT_DATE" in vars_dict
            assert "PROJECT_NAME" in vars_dict
            assert vars_dict["PROJECT_NAME"] == tmp_path.name
        finally:
            os.chdir(original_cwd)

    def test_file_overrides_builtin(self, tmp_path):
        """Test that file-based variables override built-in variables."""
        var_sub = VariableSubstitution()

        # Create variable file with override
        var_file = tmp_path / ".promptrek" / "variables.promptrek.yaml"
        var_file.parent.mkdir(parents=True, exist_ok=True)
        var_file.write_text(
            """
PROJECT_NAME: my-custom-project
CURRENT_DATE: 2025-01-01
"""
        )

        # Change to temp directory
        import os

        original_cwd = Path.cwd()
        try:
            os.chdir(tmp_path)

            vars_dict = var_sub.load_and_evaluate_variables(
                search_dir=tmp_path,
                include_builtins=True,
                allow_commands=False,
            )

            # File variables should override built-ins
            assert vars_dict["PROJECT_NAME"] == "my-custom-project"
            assert vars_dict["CURRENT_DATE"] == "2025-01-01"
        finally:
            os.chdir(original_cwd)

    @patch("promptrek.utils.variables.subprocess.run")
    def test_complete_priority_chain(self, mock_run, tmp_path):
        """Test complete variable priority: CLI > File > Built-in."""
        var_sub = VariableSubstitution()

        # Mock git to return consistent PROJECT_NAME
        # get_all() calls: _get_project_name() (2 calls) + _get_git_variables() (3 calls) = 5 total
        mock_run.side_effect = [
            Mock(
                returncode=0, stdout="", stderr=""
            ),  # PROJECT_NAME: is-inside-work-tree
            Mock(
                returncode=0, stdout="https://github.com/user/git-repo.git\n", stderr=""
            ),  # PROJECT_NAME: remote URL
            Mock(returncode=0, stdout="", stderr=""),  # GIT vars: is-inside-work-tree
            Mock(stdout="main\n", stderr=""),  # GIT vars: branch name
            Mock(stdout="abc1234\n", stderr=""),  # GIT vars: commit hash
        ]

        # Create variable file
        var_file = tmp_path / ".promptrek" / "variables.promptrek.yaml"
        var_file.parent.mkdir(parents=True, exist_ok=True)
        var_file.write_text(
            """
PROJECT_NAME: file-override
CUSTOM_VAR: from-file
"""
        )

        # Change to temp directory
        import os

        original_cwd = Path.cwd()
        try:
            os.chdir(tmp_path)

            # Load variables (Built-in)
            vars_dict = var_sub.load_and_evaluate_variables(
                search_dir=tmp_path,
                include_builtins=True,
                allow_commands=False,
            )

            # At this point: File overrides Built-in
            assert vars_dict["PROJECT_NAME"] == "file-override"
            assert vars_dict["CUSTOM_VAR"] == "from-file"

            # Now simulate CLI override (highest priority)
            cli_vars = {"PROJECT_NAME": "cli-override", "CLI_VAR": "from-cli"}
            vars_dict.update(cli_vars)

            # CLI should override everything
            assert vars_dict["PROJECT_NAME"] == "cli-override"
            assert vars_dict["CUSTOM_VAR"] == "from-file"  # Not overridden by CLI
            assert vars_dict["CLI_VAR"] == "from-cli"
            assert "CURRENT_DATE" in vars_dict  # Built-in still present
        finally:
            os.chdir(original_cwd)

    def test_inline_variable_in_upf(self, tmp_path):
        """Test that inline variables in UPF are used (lowest priority before built-in)."""
        from promptrek.core.models import PromptMetadata, UniversalPromptV3

        # Create UPF with inline variables
        upf = UniversalPromptV3(
            schema_version="3.0.0",
            metadata=PromptMetadata(
                title="Test Prompt", description="Test description", version="1.0.0"
            ),
            content="Test content with {{{ INLINE_VAR }}}",
            variables={"INLINE_VAR": "inline-value", "PROJECT_NAME": "inline-project"},
        )

        var_sub = VariableSubstitution()

        # Inline variables from UPF
        inline_vars = upf.variables or {}

        # Load file and built-in variables
        import os

        original_cwd = Path.cwd()
        try:
            os.chdir(tmp_path)

            loaded_vars = var_sub.load_and_evaluate_variables(
                search_dir=tmp_path,
                include_builtins=True,
                allow_commands=False,
            )

            # Priority: File/Built-in > Inline
            # Start with inline (lowest)
            final_vars = inline_vars.copy()
            # Overlay with file/built-in (higher priority)
            final_vars.update(loaded_vars)

            # Built-in should override inline
            assert final_vars["PROJECT_NAME"] == tmp_path.name  # Built-in wins
            assert final_vars["INLINE_VAR"] == "inline-value"  # Inline only
            assert "CURRENT_DATE" in final_vars  # Built-in present
        finally:
            os.chdir(original_cwd)
