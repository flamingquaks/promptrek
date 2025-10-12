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
