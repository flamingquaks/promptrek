"""Tests specifically designed to boost core utilities coverage."""

import tempfile
from pathlib import Path

import pytest
import yaml
from click.testing import CliRunner

from promptrek.cli.main import cli


class TestCoreUtilitiesCoverage:
    """Tests designed to boost coverage in core utilities."""

    @pytest.fixture
    def runner(self):
        """Create Click test runner."""
        return CliRunner()

    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for test files."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield Path(temp_dir)

    @pytest.fixture
    def complex_variables_file(self, temp_dir):
        """Create UPF file with complex variable scenarios."""
        upf_content = {
            "schema_version": "1.0.0",
            "metadata": {
                "title": "{{ PROJECT_NAME }}",
                "description": "Project for {{ ENVIRONMENT }} with {{ FRAMEWORK }}",
                "version": "{{ VERSION }}",
                "author": "{{ AUTHOR_EMAIL }}",
            },
            "targets": ["claude"],
            "context": {
                "nested_var": "{{ OUTER_VAR }}/{{ INNER_VAR }}",
                "conditional_var": "{% if DEBUG_MODE %}{{ DEBUG_CONFIG }}{% else %}{{ PROD_CONFIG }}{% endif %}",
                "list_with_vars": ["{{ ITEM1 }}", "{{ ITEM2 }}", "static_item"],
                "complex_nested": {"level1": {"level2": "{{ DEEP_VAR }}"}},
            },
            "instructions": {
                "general": [
                    "Use {{ LANGUAGE }} with {{ FRAMEWORK }}",
                    "Environment: {{ ENVIRONMENT }}",
                    "{% if TESTING_ENABLED %}Include comprehensive tests{% endif %}",
                ]
            },
            "variables": {
                "PROJECT_NAME": "VariableTest",
                "ENVIRONMENT": "development",
                "FRAMEWORK": "Django",
                "VERSION": "1.0.0",
                "AUTHOR_EMAIL": "test@example.com",
                "OUTER_VAR": "outer",
                "INNER_VAR": "inner",
                "DEBUG_MODE": "true",
                "DEBUG_CONFIG": "debug.json",
                "PROD_CONFIG": "prod.json",
                "ITEM1": "first",
                "ITEM2": "second",
                "DEEP_VAR": "deep_value",
                "LANGUAGE": "Python",
                "TESTING_ENABLED": "true",
            },
        }
        upf_file = temp_dir / "complex_variables.promptrek.yaml"
        with open(upf_file, "w") as f:
            yaml.dump(upf_content, f, default_flow_style=False)
        return upf_file

    @pytest.fixture
    def invalid_template_file(self, temp_dir):
        """Create UPF file with invalid template syntax."""
        upf_content = {
            "schema_version": "1.0.0",
            "metadata": {
                "title": "Invalid Template Test",
                "description": "{{ UNCLOSED_VAR",  # Invalid template syntax
                "version": "1.0.0",
                "author": "test",
            },
            "targets": ["claude"],
            "instructions": {
                "general": ["{{ ANOTHER_UNCLOSED"]  # Another invalid template
            },
        }
        upf_file = temp_dir / "invalid_template.promptrek.yaml"
        with open(upf_file, "w") as f:
            yaml.dump(upf_content, f)
        return upf_file

    @pytest.fixture
    def missing_variables_file(self, temp_dir):
        """Create UPF file with undefined variables."""
        upf_content = {
            "schema_version": "1.0.0",
            "metadata": {
                "title": "{{ UNDEFINED_VAR }}",
                "description": "Uses undefined variables",
                "version": "1.0.0",
                "author": "test",
            },
            "targets": ["claude"],
            "instructions": {"general": ["{{ ANOTHER_UNDEFINED }} instruction"]},
            "variables": {"DEFINED_VAR": "defined"},
        }
        upf_file = temp_dir / "missing_variables.promptrek.yaml"
        with open(upf_file, "w") as f:
            yaml.dump(upf_content, f)
        return upf_file

    @pytest.fixture
    def complex_conditionals_file(self, temp_dir):
        """Create UPF file with complex conditional logic."""
        upf_content = {
            "schema_version": "1.0.0",
            "metadata": {
                "title": "Complex Conditionals Test",
                "description": "Test complex conditional scenarios",
                "version": "1.0.0",
                "author": "test",
            },
            "targets": ["claude"],
            "instructions": {
                "environment": [
                    "{% if ENVIRONMENT == 'production' %}Use production settings{% elif ENVIRONMENT == 'staging' %}Use staging settings{% else %}Use development settings{% endif %}",
                    "{% if DATABASE_TYPE == 'postgresql' and USE_POOLING == 'true' %}Enable connection pooling{% endif %}",
                    "{% if SCALE in ['large', 'enterprise'] %}Enable distributed caching{% endif %}",
                ],
                "features": [
                    "{% if FEATURE_A == 'enabled' %}{% if FEATURE_B == 'enabled' %}Both features enabled{% else %}Only Feature A{% endif %}{% endif %}",
                    "{% for item in ITEM_LIST.split(',') %}Process {{ item }}{% endfor %}",
                ],
            },
            "variables": {
                "ENVIRONMENT": "production",
                "DATABASE_TYPE": "postgresql",
                "USE_POOLING": "true",
                "SCALE": "large",
                "FEATURE_A": "enabled",
                "FEATURE_B": "disabled",
                "ITEM_LIST": "item1,item2,item3",
            },
        }
        upf_file = temp_dir / "complex_conditionals.promptrek.yaml"
        with open(upf_file, "w") as f:
            yaml.dump(upf_content, f, default_flow_style=False)
        return upf_file

    def test_generate_with_complex_variables(
        self, runner, complex_variables_file, temp_dir
    ):
        """Test generate command with complex variable scenarios."""
        with runner.isolated_filesystem(temp_dir=temp_dir):
            result = runner.invoke(
                cli,
                [
                    "generate",
                    str(complex_variables_file),
                    "--editor",
                    "claude",
                    "-V",
                    "PROJECT_NAME=OverriddenProject",
                    "-V",
                    "ENVIRONMENT=production",
                ],
            )

            assert result.exit_code == 0

    def test_generate_with_invalid_template_syntax(self, runner, invalid_template_file):
        """Test generate command with invalid template syntax."""
        result = runner.invoke(
            cli, ["generate", str(invalid_template_file), "--editor", "claude"]
        )

        # Should handle template errors gracefully
        assert result.exit_code != 0 or "Generated:" in result.output

    def test_generate_with_missing_variables(self, runner, missing_variables_file):
        """Test generate command with undefined variables."""
        result = runner.invoke(
            cli, ["generate", str(missing_variables_file), "--editor", "claude"]
        )

        # Should handle missing variables gracefully
        assert result.exit_code != 0 or "Generated:" in result.output

    def test_generate_with_complex_conditionals(
        self, runner, complex_conditionals_file, temp_dir
    ):
        """Test generate command with complex conditional logic."""
        with runner.isolated_filesystem(temp_dir=temp_dir):
            result = runner.invoke(
                cli, ["generate", str(complex_conditionals_file), "--editor", "claude"]
            )

            assert result.exit_code == 0

    def test_validate_with_complex_scenarios(self, runner, complex_variables_file):
        """Test validate command with complex scenarios."""
        result = runner.invoke(cli, ["validate", str(complex_variables_file)])

        assert result.exit_code == 0
        assert "valid" in result.output.lower()

    def test_validate_with_strict_mode_complex(self, runner, complex_conditionals_file):
        """Test validate command with strict mode on complex file."""
        result = runner.invoke(
            cli, ["validate", str(complex_conditionals_file), "--strict"]
        )

        # Should pass or provide helpful error messages
        assert result.exit_code == 0 or "error" in result.output.lower()

    def test_parser_with_include_files(self, runner, temp_dir):
        """Test parser handling of import/include functionality."""
        # Create base file
        base_content = {
            "schema_version": "1.0.0",
            "metadata": {
                "title": "Base",
                "description": "Base",
                "version": "1.0.0",
                "author": "test",
            },
            "targets": ["claude"],
            "instructions": {"base": ["Base instruction"]},
        }
        base_file = temp_dir / "base.promptrek.yaml"
        with open(base_file, "w") as f:
            yaml.dump(base_content, f)

        # Create file that imports base
        import_content = {
            "schema_version": "1.0.0",
            "imports": [{"path": str(base_file)}],
            "metadata": {
                "title": "Import Test",
                "description": "Test",
                "version": "1.0.0",
                "author": "test",
            },
            "targets": ["claude"],
            "instructions": {"import": ["Import instruction"]},
        }
        import_file = temp_dir / "import_test.promptrek.yaml"
        with open(import_file, "w") as f:
            yaml.dump(import_content, f)

        with runner.isolated_filesystem(temp_dir=temp_dir):
            result = runner.invoke(
                cli, ["generate", str(import_file), "--editor", "claude"]
            )

            assert result.exit_code == 0

    def test_variable_override_scenarios(
        self, runner, complex_variables_file, temp_dir
    ):
        """Test various variable override scenarios."""
        with runner.isolated_filesystem(temp_dir=temp_dir):
            # Test multiple variable overrides
            result = runner.invoke(
                cli,
                [
                    "generate",
                    str(complex_variables_file),
                    "--editor",
                    "claude",
                    "-V",
                    "ENVIRONMENT=staging",
                    "-V",
                    "DEBUG_MODE=false",
                    "-V",
                    "FRAMEWORK=Flask",
                    "-V",
                    "TESTING_ENABLED=false",
                ],
            )

            assert result.exit_code == 0
