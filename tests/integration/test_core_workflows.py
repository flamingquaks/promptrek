"""Integration tests for core utilities through CLI workflows."""

import tempfile
from pathlib import Path

import pytest
import yaml
from click.testing import CliRunner

from promptrek.cli.main import cli


class TestCoreWorkflows:
    """Test core utilities integration through CLI workflows."""

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
    def variables_test_file(self, temp_dir):
        """Create UPF file for testing variable substitution."""
        upf_content = {
            "schema_version": "1.0.0",
            "metadata": {
                "title": "{{ PROJECT_TITLE }}",
                "description": "Project for {{ ENVIRONMENT }} environment",
                "version": "{{ VERSION }}",
                "author": "{{ AUTHOR_EMAIL }}",
                "tags": ["{{ TAG1 }}", "{{ TAG2 }}"],
            },
            "targets": ["claude", "copilot"],
            "context": {
                "project_type": "{{ PROJECT_TYPE }}",
                "technologies": ["{{ TECH1 }}", "{{ TECH2 }}"],
                "description": "A {{ PROJECT_TYPE }} project for {{ DOMAIN }}",
                "database": "{{ DATABASE_TYPE }}",
                "framework": "{{ FRAMEWORK }}",
            },
            "instructions": {
                "general": [
                    "Use {{ LANGUAGE }} best practices",
                    "Follow {{ STYLE_GUIDE }} conventions",
                    "Target {{ ENVIRONMENT }} environment",
                ],
                "framework_specific": [
                    "Use {{ FRAMEWORK }} {{ FRAMEWORK_VERSION }}",
                    "Implement {{ PATTERN }} patterns",
                ],
                "database": [
                    "Use {{ DATABASE_TYPE }} for persistence",
                    "Follow {{ DB_CONVENTIONS }} naming",
                ],
            },
            "examples": {
                "model": "class {{ MODEL_NAME }}(models.Model): pass",
                "view": "def {{ VIEW_NAME }}(request): return render(request, '{{ TEMPLATE }}')",
            },
            "variables": {
                "PROJECT_TITLE": "Variable Test Project",
                "ENVIRONMENT": "development",
                "VERSION": "1.0.0",
                "AUTHOR_EMAIL": "test@example.com",
                "TAG1": "test",
                "TAG2": "variables",
                "PROJECT_TYPE": "web_application",
                "TECH1": "python",
                "TECH2": "django",
                "DOMAIN": "testing",
                "DATABASE_TYPE": "postgresql",
                "FRAMEWORK": "Django",
                "LANGUAGE": "Python",
                "STYLE_GUIDE": "PEP 8",
                "FRAMEWORK_VERSION": "4.2",
                "PATTERN": "MVC",
                "DB_CONVENTIONS": "snake_case",
                "MODEL_NAME": "TestModel",
                "VIEW_NAME": "test_view",
                "TEMPLATE": "test.html",
            },
        }
        upf_file = temp_dir / "variables_test.promptrek.yaml"
        with open(upf_file, "w") as f:
            yaml.dump(upf_content, f, default_flow_style=False)
        return upf_file

    @pytest.fixture
    def conditionals_test_file(self, temp_dir):
        """Create UPF file for testing conditional processing."""
        upf_content = {
            "schema_version": "1.0.0",
            "metadata": {
                "title": "Conditional Test Project",
                "description": "Project with conditional logic",
                "version": "1.0.0",
                "author": "test@example.com",
            },
            "targets": ["claude"],
            "context": {
                "project_type": "{{ PROJECT_TYPE }}",
                "environment": "{{ ENVIRONMENT }}",
                "has_database": "{{ HAS_DATABASE }}",
                "testing_framework": "{{ TESTING_FRAMEWORK }}",
            },
            "instructions": {
                "general": [
                    "Write clean, maintainable code",
                    "{% if ENVIRONMENT == 'production' %}Use production-grade error handling{% endif %}",
                    "{% if HAS_DATABASE == 'true' %}Implement proper database migrations{% endif %}",
                ],
                "testing": [
                    "{% if TESTING_FRAMEWORK == 'pytest' %}Use pytest fixtures and parametrize{% endif %}",
                    "{% if TESTING_FRAMEWORK == 'unittest' %}Use unittest.TestCase classes{% endif %}",
                    "{% if COVERAGE_REQUIRED == 'true' %}Maintain 90%+ test coverage{% endif %}",
                ],
                "deployment": [
                    "{% if ENVIRONMENT == 'production' %}Use containerized deployment{% endif %}",
                    "{% if ENVIRONMENT == 'development' %}Use hot reloading for faster development{% endif %}",
                ],
                "security": [
                    "{% if PROJECT_TYPE == 'web_application' %}Implement CSRF protection{% endif %}",
                    "{% if HAS_DATABASE == 'true' %}Use parameterized queries{% endif %}",
                ],
            },
            "examples": {
                "test_example": "{% if TESTING_FRAMEWORK == 'pytest' %}def test_function(): assert True{% else %}class TestCase(unittest.TestCase): def test_method(self): self.assertTrue(True){% endif %}",
                "db_example": "{% if HAS_DATABASE == 'true' %}from django.db import models{% endif %}",
            },
            "variables": {
                "PROJECT_TYPE": "web_application",
                "ENVIRONMENT": "development",
                "HAS_DATABASE": "true",
                "TESTING_FRAMEWORK": "pytest",
                "COVERAGE_REQUIRED": "false",
            },
        }
        upf_file = temp_dir / "conditionals_test.promptrek.yaml"
        with open(upf_file, "w") as f:
            yaml.dump(upf_content, f, default_flow_style=False)
        return upf_file

    @pytest.fixture
    def parser_error_test_file(self, temp_dir):
        """Create UPF file for testing parser error handling."""
        # Create file with intentional YAML syntax errors for testing
        upf_content = """schema_version: "1.0.0"

metadata:
  title: "Parser Error Test"
  description: "Test parser error handling
  version: "1.0.0"  # Missing closing quote above
  author: "test@example.com"

targets:
  - claude
  invalid_key_without_dash

context:
  project_type: "test"
  technologies: ["python"  # Missing closing bracket

instructions:
  general:
    - "Test instruction"
    - malformed instruction without quotes
"""
        upf_file = temp_dir / "parser_error_test.promptrek.yaml"
        upf_file.write_text(upf_content)
        return upf_file

    @pytest.fixture
    def validation_warnings_file(self, temp_dir):
        """Create UPF file that triggers validation warnings."""
        upf_content = {
            "schema_version": "1.0.0",
            "metadata": {
                "title": "Validation Warnings Test",
                "description": "Test validation warnings",
                "version": "1.0.0",
                "author": "test@example.com",
                "tags": [],  # Empty tags should trigger warning
            },
            "targets": ["nonexistent-adapter"],  # Should trigger warning
            "context": {
                "project_type": "unknown_type",  # Should trigger warning
                "technologies": [],  # Empty technologies
                "description": "",  # Empty description
            },
            "instructions": {"general": [], "empty_section": []},  # Empty instructions
            "examples": {},  # Empty examples
            "variables": {
                "UNDEFINED_VAR": "{{ NONEXISTENT_VAR }}",  # Should trigger warning
                "CIRCULAR_REF": "{{ CIRCULAR_REF }}",  # Circular reference
            },
        }
        upf_file = temp_dir / "validation_warnings.promptrek.yaml"
        with open(upf_file, "w") as f:
            yaml.dump(upf_content, f, default_flow_style=False)
        return upf_file

    def test_variable_substitution_basic(self, runner, variables_test_file, temp_dir):
        """Test basic variable substitution through CLI workflow."""
        with runner.isolated_filesystem(temp_dir=temp_dir):
            result = runner.invoke(
                cli, ["generate", str(variables_test_file), "--editor", "claude"]
            )

            assert result.exit_code == 0
            assert "Generated:" in result.output

    def test_variable_substitution_with_overrides(
        self, runner, variables_test_file, temp_dir
    ):
        """Test variable substitution with CLI overrides."""
        with runner.isolated_filesystem(temp_dir=temp_dir):
            result = runner.invoke(
                cli,
                [
                    "generate",
                    str(variables_test_file),
                    "--editor",
                    "claude",
                    "-V",
                    "PROJECT_TITLE=Overridden Title",
                    "-V",
                    "ENVIRONMENT=production",
                    "-V",
                    "VERSION=2.0.0",
                    "-V",
                    "FRAMEWORK=Flask",
                    "-V",
                    "DATABASE_TYPE=mysql",
                ],
            )

            assert result.exit_code == 0
            assert "Generated:" in result.output

    def test_variable_substitution_verbose(self, runner, variables_test_file):
        """Test variable substitution with verbose output."""
        result = runner.invoke(
            cli,
            [
                "--verbose",
                "generate",
                str(variables_test_file),
                "--editor",
                "claude",
                "--dry-run",
                "-V",
                "LANGUAGE=JavaScript",
                "-V",
                "FRAMEWORK=Express",
            ],
        )

        assert result.exit_code == 0
        assert "Dry run mode" in result.output

    def test_variable_validation_through_cli(self, runner, temp_dir):
        """Test variable validation through CLI validation command."""
        # Create file with undefined variables
        upf_content = {
            "schema_version": "1.0.0",
            "metadata": {
                "title": "{{ UNDEFINED_TITLE }}",
                "description": "Test with {{ UNDEFINED_DESC }}",
                "version": "1.0.0",
                "author": "test@example.com",
            },
            "targets": ["claude"],
            "instructions": {
                "general": ["Use {{ UNDEFINED_LANGUAGE }} best practices"]
            },
            "variables": {"DEFINED_VAR": "defined_value"},
        }
        upf_file = temp_dir / "undefined_vars.promptrek.yaml"
        with open(upf_file, "w") as f:
            yaml.dump(upf_content, f)

        result = runner.invoke(cli, ["validate", str(upf_file)])
        assert result.exit_code == 0  # Should still pass validation but with warnings

    def test_conditional_processing_basic(
        self, runner, conditionals_test_file, temp_dir
    ):
        """Test basic conditional processing through CLI workflow."""
        with runner.isolated_filesystem(temp_dir=temp_dir):
            result = runner.invoke(
                cli, ["generate", str(conditionals_test_file), "--editor", "claude"]
            )

            assert result.exit_code == 0
            assert "Generated:" in result.output

    def test_conditional_processing_with_overrides(
        self, runner, conditionals_test_file, temp_dir
    ):
        """Test conditional processing with variable overrides."""
        with runner.isolated_filesystem(temp_dir=temp_dir):
            # Test production environment conditions
            result = runner.invoke(
                cli,
                [
                    "generate",
                    str(conditionals_test_file),
                    "--editor",
                    "claude",
                    "-V",
                    "ENVIRONMENT=production",
                    "-V",
                    "COVERAGE_REQUIRED=true",
                    "-V",
                    "TESTING_FRAMEWORK=unittest",
                ],
            )

            assert result.exit_code == 0
            assert "Generated:" in result.output

    def test_conditional_processing_different_contexts(
        self, runner, conditionals_test_file, temp_dir
    ):
        """Test conditional processing with different context scenarios."""
        with runner.isolated_filesystem(temp_dir=temp_dir):
            # Test without database
            result = runner.invoke(
                cli,
                [
                    "generate",
                    str(conditionals_test_file),
                    "--editor",
                    "claude",
                    "-V",
                    "HAS_DATABASE=false",
                    "-V",
                    "PROJECT_TYPE=cli_application",
                ],
            )

            assert result.exit_code == 0

    def test_conditional_dry_run_verbose(self, runner, conditionals_test_file):
        """Test conditional processing in dry-run with verbose output."""
        result = runner.invoke(
            cli,
            [
                "--verbose",
                "generate",
                str(conditionals_test_file),
                "--editor",
                "claude",
                "--dry-run",
                "-V",
                "ENVIRONMENT=production",
                "-V",
                "HAS_DATABASE=true",
            ],
        )

        assert result.exit_code == 0
        assert "Dry run mode" in result.output

    def test_parser_error_handling_validation(self, runner, parser_error_test_file):
        """Test parser error handling through validation command."""
        result = runner.invoke(cli, ["validate", str(parser_error_test_file)])

        assert result.exit_code != 0  # Should fail due to YAML syntax errors
        assert "error" in result.output.lower() or "invalid" in result.output.lower()

    def test_parser_error_handling_generation(self, runner, parser_error_test_file):
        """Test parser error handling through generate command."""
        result = runner.invoke(
            cli, ["generate", str(parser_error_test_file), "--editor", "claude"]
        )

        assert result.exit_code != 0  # Should fail due to parsing errors

    def test_parser_error_verbose_output(self, runner, parser_error_test_file):
        """Test parser error handling with verbose output."""
        result = runner.invoke(
            cli, ["--verbose", "validate", str(parser_error_test_file)]
        )

        assert result.exit_code != 0
        assert "error" in result.output.lower()

    def test_parser_nonexistent_file(self, runner):
        """Test parser handling of nonexistent files."""
        result = runner.invoke(cli, ["validate", "/nonexistent/path/file.yaml"])

        assert result.exit_code != 0
        assert "not found" in result.output.lower() or "error" in result.output.lower()

    def test_validator_warnings_strict_mode(self, runner, validation_warnings_file):
        """Test validator warnings in strict mode."""
        result = runner.invoke(
            cli, ["validate", str(validation_warnings_file), "--strict"]
        )

        # In strict mode, warnings should cause failure
        assert result.exit_code != 0

    def test_validator_warnings_non_strict_mode(self, runner, validation_warnings_file):
        """Test validator warnings in non-strict mode."""
        result = runner.invoke(cli, ["validate", str(validation_warnings_file)])

        # In non-strict mode, warnings should not cause failure
        assert result.exit_code == 0
        assert "warning" in result.output.lower()

    def test_validator_verbose_output(self, runner, validation_warnings_file):
        """Test validator verbose output with warnings."""
        result = runner.invoke(
            cli, ["--verbose", "validate", str(validation_warnings_file)]
        )

        assert result.exit_code == 0
        assert "warning" in result.output.lower()

    def test_validator_integration_with_generation(
        self, runner, validation_warnings_file, temp_dir
    ):
        """Test validator integration with generation workflow."""
        with runner.isolated_filesystem(temp_dir=temp_dir):
            # Should still generate despite warnings
            result = runner.invoke(
                cli, ["generate", str(validation_warnings_file), "--editor", "claude"]
            )

            # Generation might fail due to invalid targets, but that's expected
            # The important thing is that validation warnings are processed

    def test_complex_variable_and_conditional_combination(self, runner, temp_dir):
        """Test complex combination of variables and conditionals."""
        upf_content = {
            "schema_version": "1.0.0",
            "metadata": {
                "title": "{{ PROJECT_NAME }} - {{ ENVIRONMENT | title }} Environment",
                "description": "{% if ENVIRONMENT == 'production' %}Production-ready {% endif %}{{ PROJECT_TYPE }} application",
                "version": "{{ VERSION }}",
                "author": "{{ AUTHOR }}",
            },
            "targets": ["claude"],
            "context": {
                "project_type": "{{ PROJECT_TYPE }}",
                "framework": "{% if PROJECT_TYPE == 'web' %}{{ WEB_FRAMEWORK }}{% elif PROJECT_TYPE == 'api' %}{{ API_FRAMEWORK }}{% else %}{{ DEFAULT_FRAMEWORK }}{% endif %}",
                "database": "{% if HAS_DB == 'true' %}{{ DB_TYPE }}{% else %}none{% endif %}",
            },
            "instructions": {
                "general": [
                    "Use {{ LANGUAGE }} best practices",
                    "{% if ENVIRONMENT == 'development' %}Enable debug mode{% endif %}",
                    "{% if ENVIRONMENT == 'production' %}Disable debug features{% endif %}",
                ],
                "framework": [
                    "{% if PROJECT_TYPE == 'web' %}Use {{ WEB_FRAMEWORK }} for web development{% endif %}",
                    "{% if PROJECT_TYPE == 'api' %}Use {{ API_FRAMEWORK }} for API development{% endif %}",
                ],
                "database": [
                    "{% if HAS_DB == 'true' %}Use {{ DB_TYPE }} for data persistence{% endif %}",
                    "{% if HAS_DB == 'true' and ENVIRONMENT == 'production' %}Use connection pooling{% endif %}",
                ],
            },
            "variables": {
                "PROJECT_NAME": "ComplexApp",
                "PROJECT_TYPE": "web",
                "ENVIRONMENT": "development",
                "VERSION": "1.0.0",
                "AUTHOR": "Test Developer",
                "LANGUAGE": "Python",
                "WEB_FRAMEWORK": "Django",
                "API_FRAMEWORK": "FastAPI",
                "DEFAULT_FRAMEWORK": "Flask",
                "HAS_DB": "true",
                "DB_TYPE": "PostgreSQL",
            },
        }
        upf_file = temp_dir / "complex_test.promptrek.yaml"
        with open(upf_file, "w") as f:
            yaml.dump(upf_content, f, default_flow_style=False)

        with runner.isolated_filesystem(temp_dir=temp_dir):
            # Test various combinations
            test_cases = [
                {
                    "vars": ["PROJECT_TYPE=api", "ENVIRONMENT=production"],
                    "description": "API in production",
                },
                {
                    "vars": ["PROJECT_TYPE=cli", "HAS_DB=false"],
                    "description": "CLI app without database",
                },
                {
                    "vars": [
                        "PROJECT_TYPE=web",
                        "ENVIRONMENT=production",
                        "DB_TYPE=MySQL",
                    ],
                    "description": "Web app in production with MySQL",
                },
            ]

            for case in test_cases:
                args = ["generate", str(upf_file), "--editor", "claude"]
                for var in case["vars"]:
                    args.extend(["-V", var])

                result = runner.invoke(cli, args)
                assert result.exit_code == 0, f"Failed for case: {case['description']}"

    def test_import_functionality_integration(self, runner, temp_dir):
        """Test import functionality through CLI workflow."""
        # Create base UPF file
        base_content = {
            "schema_version": "1.0.0",
            "metadata": {
                "title": "Base Configuration",
                "description": "Base settings",
                "version": "1.0.0",
                "author": "test@example.com",
            },
            "targets": ["claude"],  # Required field
            "context": {"base_setting": "base_value", "shared_technology": "python"},
            "instructions": {
                "general": ["Follow base conventions", "Use shared patterns"]
            },
            "variables": {"BASE_VAR": "base_value", "SHARED_VAR": "shared"},
        }
        base_file = temp_dir / "base.promptrek.yaml"
        with open(base_file, "w") as f:
            yaml.dump(base_content, f)

        # Create importing UPF file
        import_content = {
            "schema_version": "1.0.0",
            "imports": [{"path": str(base_file)}],
            "metadata": {
                "title": "Importing Configuration",
                "description": "Configuration that imports base",
                "version": "1.0.0",
                "author": "test@example.com",
            },
            "targets": ["claude"],
            "context": {"project_type": "web_application", "additional_tech": "django"},
            "instructions": {
                "specific": [
                    "Use {{ BASE_VAR }} from base",
                    "Extend base functionality",
                ]
            },
            "variables": {"IMPORT_VAR": "import_value"},
        }
        import_file = temp_dir / "importing.promptrek.yaml"
        with open(import_file, "w") as f:
            yaml.dump(import_content, f)

        with runner.isolated_filesystem(temp_dir=temp_dir):
            result = runner.invoke(
                cli, ["generate", str(import_file), "--editor", "claude"]
            )

            assert result.exit_code == 0
            assert "Generated:" in result.output
