"""
Test variable substitution functionality.
"""

import os

import pytest

from promptrek.core.exceptions import TemplateError
from promptrek.core.models import Instructions, PromptMetadata, UniversalPrompt
from promptrek.utils.variables import VariableSubstitution


class TestVariableSubstitution:
    """Test variable substitution utilities."""

    def test_basic_variable_substitution(self):
        """Test basic variable substitution."""
        vs = VariableSubstitution()
        content = "Hello {{{ NAME }}}, welcome to {{{ PROJECT }}}!"
        variables = {"NAME": "John", "PROJECT": "PromptTrek"}

        result = vs.substitute(content, variables)
        assert result == "Hello John, welcome to PromptTrek!"

    def test_environment_variable_substitution(self):
        """Test environment variable substitution."""
        vs = VariableSubstitution()

        # Set test environment variable
        os.environ["TEST_VAR"] = "test_value"

        content = "Test: ${TEST_VAR}"
        result = vs.substitute(content, {}, env_variables=True)
        assert result == "Test: test_value"

        # Clean up
        del os.environ["TEST_VAR"]

    def test_strict_mode_error(self):
        """Test strict mode raises error for undefined variables."""
        vs = VariableSubstitution()
        content = "Hello {{{ UNDEFINED_VAR }}}!"

        with pytest.raises(TemplateError, match="Undefined variable: UNDEFINED_VAR"):
            vs.substitute(content, {}, strict=True)

    def test_non_strict_mode_leaves_undefined(self):
        """Test non-strict mode leaves undefined variables unchanged."""
        vs = VariableSubstitution()
        content = "Hello {{{ UNDEFINED_VAR }}}!"

        result = vs.substitute(content, {})
        assert result == "Hello {{{ UNDEFINED_VAR }}}!"

    def test_get_undefined_variables(self):
        """Test getting undefined variables from content."""
        vs = VariableSubstitution()
        content = "Hello {{{ NAME }}} and {{{ UNDEFINED1 }}} and {{{ UNDEFINED2 }}}!"
        variables = {"NAME": "John"}

        undefined = vs.get_undefined_variables(content, variables)
        assert set(undefined) == {"UNDEFINED1", "UNDEFINED2"}

    def test_extract_variables(self):
        """Test extracting all variables from content."""
        vs = VariableSubstitution()
        content = "Hello {{{ NAME }}}, project: {{{ PROJECT }}}, env: ${HOME}"

        variables = vs.extract_variables(content)
        assert set(variables) == {"NAME", "PROJECT", "${HOME}"}

    def test_substitute_prompt(self):
        """Test substituting variables in a full prompt."""
        vs = VariableSubstitution()

        # Create test prompt
        prompt = UniversalPrompt(
            schema_version="1.0.0",
            metadata=PromptMetadata(
                title="Test {{{ PROJECT_NAME }}}",
                description="Description for {{{ PROJECT_NAME }}}",
                version="1.0.0",
                author="{{{ AUTHOR }}}",
                created="2024-01-01",
                updated="2024-01-01",
            ),
            targets=["copilot"],
            instructions=Instructions(general=["Use {{{ PROJECT_NAME }}} conventions"]),
            variables={"PROJECT_NAME": "My App", "AUTHOR": "Developer"},
        )

        result = vs.substitute_prompt(prompt)

        assert result.metadata.title == "Test My App"
        assert result.metadata.description == "Description for My App"
        assert result.metadata.author == "Developer"
        assert result.instructions.general[0] == "Use My App conventions"

    def test_substitute_prompt_with_additional_variables(self):
        """Test substituting prompt with additional variables."""
        vs = VariableSubstitution()

        prompt = UniversalPrompt(
            schema_version="1.0.0",
            metadata=PromptMetadata(
                title="Test {{{ PROJECT_NAME }}}",
                description="Version {{{ VERSION }}}",
                version="1.0.0",
                author="Developer",
                created="2024-01-01",
                updated="2024-01-01",
            ),
            targets=["copilot"],
            variables={"PROJECT_NAME": "My App"},
        )

        additional_vars = {"VERSION": "2.0.0"}
        result = vs.substitute_prompt(prompt, additional_vars)

        assert result.metadata.title == "Test My App"
        assert result.metadata.description == "Version 2.0.0"

    def test_nested_data_substitution(self):
        """Test substitution in nested data structures."""
        vs = VariableSubstitution()

        data = {
            "title": "Project {{{ NAME }}}",
            "config": {
                "author": "{{{ AUTHOR }}}",
                "settings": ["option1", "option2 for {{{ NAME }}}"],
            },
        }

        variables = {"NAME": "TestApp", "AUTHOR": "Developer"}
        result = vs._substitute_dict_recursive(data, variables, False, False)

        assert result["title"] == "Project TestApp"
        assert result["config"]["author"] == "Developer"
        assert result["config"]["settings"][1] == "option2 for TestApp"

    def test_substitute_dict_recursive_with_non_string_values(self):
        """Test substitution with non-string values."""
        vs = VariableSubstitution()

        data = {
            "number": 42,
            "boolean": True,
            "none_value": None,
            "string": "Value {{{ VAR }}}",
        }

        variables = {"VAR": "test"}
        result = vs._substitute_dict_recursive(data, variables, False, False)

        assert result["number"] == 42
        assert result["boolean"] is True
        assert result["none_value"] is None
        assert result["string"] == "Value test"

    def test_extract_variables_complex(self):
        """Test extracting variables from complex content."""
        vs = VariableSubstitution()
        text = """
        Use {{{ PROJECT_NAME }}} with {{{ LANGUAGE }}}.
        Version: {{{ VERSION }}}
        Repeat {{{ PROJECT_NAME }}} again.
        """

        variables = vs.extract_variables(text)

        assert "PROJECT_NAME" in variables
        assert "LANGUAGE" in variables
        assert "VERSION" in variables
        # Should not have duplicates
        assert variables.count("PROJECT_NAME") == 1

    def test_substitute_nested_dicts(self):
        """Test substituting variables in nested dictionaries."""
        vs = VariableSubstitution()

        data = {"outer": {"inner": {"value": "Project {{{ NAME }}}"}}}

        variables = {"NAME": "PromptTrek"}
        result = vs._substitute_dict_recursive(data, variables, False, False)

        assert result["outer"]["inner"]["value"] == "Project PromptTrek"

    def test_get_undefined_variables_nested(self):
        """Test getting undefined variables from nested content."""
        vs = VariableSubstitution()

        text = "{{{ VAR1 }}} {{{ VAR2 }}} {{{ VAR3 }}}"
        undefined = vs.get_undefined_variables(text, {"VAR1": "val1"})

        assert "VAR2" in undefined
        assert "VAR3" in undefined
        assert "VAR1" not in undefined

    def test_environment_variable_strict_mode_error(self):
        """Test strict mode raises error for undefined environment variables."""
        vs = VariableSubstitution()
        content = "Path: ${UNDEFINED_ENV_VAR}"

        # Make sure the env var doesn't exist
        if "UNDEFINED_ENV_VAR" in os.environ:
            del os.environ["UNDEFINED_ENV_VAR"]

        with pytest.raises(
            TemplateError, match="Undefined environment variable: UNDEFINED_ENV_VAR"
        ):
            vs.substitute(content, {}, env_variables=True, strict=True)

    def test_environment_variable_non_strict_mode(self):
        """Test non-strict mode leaves undefined env variables unchanged."""
        vs = VariableSubstitution()
        content = "Path: ${UNDEFINED_ENV_VAR}"

        # Make sure the env var doesn't exist
        if "UNDEFINED_ENV_VAR" in os.environ:
            del os.environ["UNDEFINED_ENV_VAR"]

        result = vs.substitute(content, {}, env_variables=True, strict=False)
        assert result == "Path: ${UNDEFINED_ENV_VAR}"

    def test_restore_variables_basic(self, tmp_path):
        """Test basic variable restoration in content."""
        vs = VariableSubstitution()

        # Create a variables file
        var_file = tmp_path / ".promptrek" / "variables.promptrek.yaml"
        var_file.parent.mkdir(parents=True, exist_ok=True)
        var_file.write_text("PROJECT_NAME: My Project\nAUTHOR: Developer")

        # Original content with variables
        original = "Welcome to {{{ PROJECT_NAME }}} by {{{ AUTHOR }}}"

        # Parsed content with values (simulating what sync would get)
        parsed = "Welcome to My Project by Developer"

        # Restore variables
        result = vs.restore_variables_in_content(
            original_content=original,
            parsed_content=parsed,
            source_dir=tmp_path,
            verbose=False,
        )

        # Should restore the variable placeholders
        assert result == "Welcome to {{{ PROJECT_NAME }}} by {{{ AUTHOR }}}"

    def test_restore_variables_partial_match(self, tmp_path):
        """Test variable restoration when only some values were substituted."""
        vs = VariableSubstitution()

        # Create a variables file
        var_file = tmp_path / ".promptrek" / "variables.promptrek.yaml"
        var_file.parent.mkdir(parents=True, exist_ok=True)
        var_file.write_text("PROJECT_NAME: My Project")

        # Original has variable, but also mentions "My Project" naturally
        original = "{{{ PROJECT_NAME }}} is about My Project"

        # After substitution, both become "My Project"
        parsed = "My Project is about My Project"

        # Restore - should restore the variable
        result = vs.restore_variables_in_content(
            original_content=original,
            parsed_content=parsed,
            source_dir=tmp_path,
            verbose=False,
        )

        # Should restore the variable placeholder
        assert result == "{{{ PROJECT_NAME }}} is about {{{ PROJECT_NAME }}}"

    def test_restore_variables_no_change_if_no_variables(self, tmp_path):
        """Test that content without variables is unchanged."""
        vs = VariableSubstitution()

        original = "This is plain text"
        parsed = "This is plain text with edits"

        result = vs.restore_variables_in_content(
            original_content=original,
            parsed_content=parsed,
            source_dir=tmp_path,
            verbose=False,
        )

        # Should keep the edited content since no variables
        assert result == "This is plain text with edits"

    def test_restore_variables_with_overlapping_values(self, tmp_path):
        """Test variable restoration with overlapping values."""
        vs = VariableSubstitution()

        # Create a variables file with overlapping values
        var_file = tmp_path / ".promptrek" / "variables.promptrek.yaml"
        var_file.parent.mkdir(parents=True, exist_ok=True)
        var_file.write_text("SHORT: My\nLONG: My Project")

        # Original content
        original = "{{{ LONG }}} and {{{ SHORT }}}"

        # Parsed (after substitution)
        parsed = "My Project and My"

        # Restore variables
        result = vs.restore_variables_in_content(
            original_content=original,
            parsed_content=parsed,
            source_dir=tmp_path,
            verbose=False,
        )

        # Should restore both variables (longest first prevents substring issues)
        assert result == "{{{ LONG }}} and {{{ SHORT }}}"

    def test_restore_variables_with_env_vars(self, tmp_path):
        """Test variable restoration with environment variables."""
        vs = VariableSubstitution()

        # Set env variable
        os.environ["TEST_VAR"] = "test_value"

        try:
            # Original content with env variable
            original = "Value: ${TEST_VAR}"

            # Parsed (after substitution)
            parsed = "Value: test_value"

            # Restore
            result = vs.restore_variables_in_content(
                original_content=original,
                parsed_content=parsed,
                source_dir=tmp_path,
                verbose=False,
            )

            # Should restore the env variable placeholder
            assert result == "Value: ${TEST_VAR}"
        finally:
            # Clean up
            del os.environ["TEST_VAR"]

    def test_restore_variables_no_restoration_if_value_in_original(self, tmp_path):
        """Test that values appearing naturally in content aren't replaced."""
        vs = VariableSubstitution()

        # Create a variables file
        var_file = tmp_path / ".promptrek" / "variables.promptrek.yaml"
        var_file.parent.mkdir(parents=True, exist_ok=True)
        var_file.write_text("PROJECT_NAME: My Project")

        # Original already contains "My Project" without the variable
        original = "My Project is the name"

        # Parsed is the same
        parsed = "My Project is the name"

        # Restore
        result = vs.restore_variables_in_content(
            original_content=original,
            parsed_content=parsed,
            source_dir=tmp_path,
            verbose=False,
        )

        # Should NOT restore since "My Project" appears naturally
        # Wait - my implementation checks if placeholder is in original
        # If placeholder is not in original, it won't restore
        # This is the correct behavior!
        assert result == "My Project is the name"

    def test_restore_variables_empty_content(self, tmp_path):
        """Test variable restoration with empty content."""
        vs = VariableSubstitution()

        # Test empty original
        result = vs.restore_variables_in_content(
            original_content="",
            parsed_content="Some content",
            source_dir=tmp_path,
            verbose=False,
        )
        assert result == "Some content"

        # Test empty parsed
        result = vs.restore_variables_in_content(
            original_content="Some {{{ VAR }}}",
            parsed_content="",
            source_dir=tmp_path,
            verbose=False,
        )
        assert result == ""

    def test_restore_variables_multiple_occurrences(self, tmp_path):
        """Test variable restoration with multiple occurrences."""
        vs = VariableSubstitution()

        # Create a variables file
        var_file = tmp_path / ".promptrek" / "variables.promptrek.yaml"
        var_file.parent.mkdir(parents=True, exist_ok=True)
        var_file.write_text("NAME: John")

        # Original with multiple variable occurrences
        original = "Hi {{{ NAME }}}, welcome {{{ NAME }}}! Mr. {{{ NAME }}}"

        # Parsed (after substitution)
        parsed = "Hi John, welcome John! Mr. John"

        # Restore
        result = vs.restore_variables_in_content(
            original_content=original,
            parsed_content=parsed,
            source_dir=tmp_path,
            verbose=False,
        )

        # Should restore all occurrences
        assert result == "Hi {{{ NAME }}}, welcome {{{ NAME }}}! Mr. {{{ NAME }}}"
