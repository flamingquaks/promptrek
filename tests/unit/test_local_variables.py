"""
Test local variables file support.
"""

import sys
from pathlib import Path
from unittest.mock import patch

import pytest
import yaml

from promptrek.utils.variables import VariableSubstitution


class TestLocalVariables:
    """Test local variables file loading and precedence."""

    def test_load_local_variables_not_found(self, tmp_path):
        """Test loading when no local variables file exists."""
        vs = VariableSubstitution()
        variables = vs.load_local_variables(tmp_path)

        assert variables == {}

    def test_load_local_variables_found(self, tmp_path):
        """Test loading local variables from file (new location)."""
        # Create local variables file in new location
        promptrek_dir = tmp_path / ".promptrek"
        promptrek_dir.mkdir()
        var_file = promptrek_dir / "variables.promptrek.yaml"
        var_data = {
            "AUTHOR_NAME": "John Doe",
            "AUTHOR_EMAIL": "john@example.com",
            "API_KEY": "secret-key",
        }
        with open(var_file, "w") as f:
            yaml.dump(var_data, f)

        vs = VariableSubstitution()
        variables = vs.load_local_variables(tmp_path)

        assert variables == var_data

    def test_load_local_variables_searches_parent_directories(self, tmp_path):
        """Test that search walks up parent directories."""
        # Create local variables file in parent (new location)
        promptrek_dir = tmp_path / ".promptrek"
        promptrek_dir.mkdir()
        var_file = promptrek_dir / "variables.promptrek.yaml"
        var_data = {"PROJECT_NAME": "MyProject"}
        with open(var_file, "w") as f:
            yaml.dump(var_data, f)

        # Search from subdirectory
        subdir = tmp_path / "subdir" / "nested"
        subdir.mkdir(parents=True)

        vs = VariableSubstitution()
        variables = vs.load_local_variables(subdir)

        assert variables == var_data

    def test_load_local_variables_prefers_closer_file(self, tmp_path):
        """Test that closer file takes precedence over parent."""
        # Create parent variables file (new location)
        parent_promptrek_dir = tmp_path / ".promptrek"
        parent_promptrek_dir.mkdir()
        parent_var_file = parent_promptrek_dir / "variables.promptrek.yaml"
        parent_data = {"VAR1": "parent"}
        with open(parent_var_file, "w") as f:
            yaml.dump(parent_data, f)

        # Create child variables file (new location)
        subdir = tmp_path / "subdir"
        subdir.mkdir()
        child_promptrek_dir = subdir / ".promptrek"
        child_promptrek_dir.mkdir()
        child_var_file = child_promptrek_dir / "variables.promptrek.yaml"
        child_data = {"VAR1": "child"}
        with open(child_var_file, "w") as f:
            yaml.dump(child_data, f)

        vs = VariableSubstitution()
        variables = vs.load_local_variables(subdir)

        # Should get child data
        assert variables == child_data

    def test_load_local_variables_invalid_yaml(self, tmp_path):
        """Test handling of invalid YAML in local variables file."""
        promptrek_dir = tmp_path / ".promptrek"
        promptrek_dir.mkdir()
        var_file = promptrek_dir / "variables.promptrek.yaml"
        with open(var_file, "w") as f:
            f.write("invalid: yaml: [content")

        vs = VariableSubstitution()
        variables = vs.load_local_variables(tmp_path)

        # Should return empty dict on error
        assert variables == {}

    def test_load_local_variables_non_dict_content(self, tmp_path):
        """Test handling of non-dict content in variables file."""
        promptrek_dir = tmp_path / ".promptrek"
        promptrek_dir.mkdir()
        var_file = promptrek_dir / "variables.promptrek.yaml"
        with open(var_file, "w") as f:
            yaml.dump(["item1", "item2"], f)

        vs = VariableSubstitution()
        variables = vs.load_local_variables(tmp_path)

        # Should return empty dict for non-dict content
        assert variables == {}

    def test_load_local_variables_empty_file(self, tmp_path):
        """Test handling of empty variables file."""
        promptrek_dir = tmp_path / ".promptrek"
        promptrek_dir.mkdir()
        var_file = promptrek_dir / "variables.promptrek.yaml"
        var_file.touch()

        vs = VariableSubstitution()
        variables = vs.load_local_variables(tmp_path)

        assert variables == {}

    def test_load_local_variables_default_search_path(self, tmp_path, monkeypatch):
        """Test loading with default search path (current directory)."""
        # Change to tmp_path
        monkeypatch.chdir(tmp_path)

        # Create local variables file in current directory (new location)
        promptrek_dir = tmp_path / ".promptrek"
        promptrek_dir.mkdir()
        var_file = promptrek_dir / "variables.promptrek.yaml"
        var_data = {"TEST_VAR": "test_value"}
        with open(var_file, "w") as f:
            yaml.dump(var_data, f)

        vs = VariableSubstitution()
        variables = vs.load_local_variables()

        assert variables == var_data

    def test_variable_substitution_with_local_variables(self, tmp_path):
        """Test that variables are properly used in substitution."""
        # Create local variables file (new location)
        promptrek_dir = tmp_path / ".promptrek"
        promptrek_dir.mkdir()
        var_file = promptrek_dir / "variables.promptrek.yaml"
        var_data = {"PROJECT_NAME": "MyProject", "AUTHOR": "John Doe"}
        with open(var_file, "w") as f:
            yaml.dump(var_data, f)

        vs = VariableSubstitution()
        local_vars = vs.load_local_variables(tmp_path)

        content = "Project: {{{ PROJECT_NAME }}}, Author: {{{ AUTHOR }}}"
        result = vs.substitute(content, local_vars)

        assert result == "Project: MyProject, Author: John Doe"

    def test_variable_precedence_cli_over_local(self, tmp_path):
        """Test that CLI variables take precedence over local file variables."""
        # Create local variables file (new location)
        promptrek_dir = tmp_path / ".promptrek"
        promptrek_dir.mkdir()
        var_file = promptrek_dir / "variables.promptrek.yaml"
        var_data = {"VAR1": "local_value", "VAR2": "local_only"}
        with open(var_file, "w") as f:
            yaml.dump(var_data, f)

        vs = VariableSubstitution()
        local_vars = vs.load_local_variables(tmp_path)

        # Simulate CLI override
        cli_vars = {"VAR1": "cli_value"}
        merged = local_vars.copy()
        merged.update(cli_vars)

        content = "VAR1: {{{ VAR1 }}}, VAR2: {{{ VAR2 }}}"
        result = vs.substitute(content, merged)

        assert result == "VAR1: cli_value, VAR2: local_only"

    def test_load_local_variables_from_old_location_still_works(self, tmp_path):
        """Test that old location (deprecated) still works for backwards compatibility."""
        # Create local variables file in old location (root)
        var_file = tmp_path / "variables.promptrek.yaml"
        var_data = {"OLD_LOCATION": "still_works"}
        with open(var_file, "w") as f:
            yaml.dump(var_data, f)

        vs = VariableSubstitution()
        # Don't trigger migration in test - we need non-interactive mode

        with patch.object(sys.stdout, "isatty", return_value=False):
            variables = vs.load_local_variables(tmp_path)

        # File should be migrated to new location
        new_var_file = tmp_path / ".promptrek" / "variables.promptrek.yaml"
        assert new_var_file.exists()
        assert not var_file.exists()  # Old file should be moved
        assert variables == var_data
