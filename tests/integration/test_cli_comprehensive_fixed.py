"""Fixed comprehensive CLI integration tests for enhanced coverage."""

import tempfile
from pathlib import Path

import pytest
import yaml
from click.testing import CliRunner

from promptrek.cli.main import cli


class TestCLIComprehensiveFixed:
    """Fixed comprehensive CLI integration tests."""

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
    def comprehensive_upf_file(self, temp_dir):
        """Create comprehensive UPF file for testing."""
        upf_content = {
            "schema_version": "1.0.0",
            "metadata": {
                "title": "Comprehensive Test Project",
                "description": "Full-featured test project for CLI testing",
                "version": "2.1.0",
                "author": "comprehensive@test.com",
                "created": "2024-01-01",
                "updated": "2024-12-01",
                "tags": ["comprehensive", "cli", "test", "integration"],
            },
            "targets": ["claude", "copilot", "cursor", "continue", "cline", "kiro"],
            "context": {
                "project_type": "full_stack_application",
                "technologies": [
                    "python",
                    "javascript",
                    "typescript",
                    "react",
                    "django",
                ],
                "description": "A comprehensive full-stack application with multiple technologies",
                "architecture": "Microservices with API gateway",
                "database": "PostgreSQL with Redis cache",
                "deployment": "Docker containers on Kubernetes",
                "monitoring": "Prometheus and Grafana",
                "ci_cd": "GitHub Actions",
            },
            "instructions": {
                "general": [
                    "Write clean, maintainable, and well-documented code",
                    "Follow industry best practices and design patterns",
                    "Implement comprehensive error handling",
                    "Use proper logging and monitoring",
                ],
                "backend": [
                    "Use Django REST framework for APIs",
                    "Implement proper authentication and authorization",
                    "Use database migrations for schema changes",
                    "Write comprehensive unit and integration tests",
                ],
                "frontend": [
                    "Use React with TypeScript for type safety",
                    "Implement responsive design principles",
                    "Use modern CSS frameworks and patterns",
                    "Optimize for performance and accessibility",
                ],
                "testing": [
                    "Maintain 90%+ test coverage",
                    "Use TDD/BDD methodologies",
                    "Implement E2E testing with Cypress",
                    "Use property-based testing where appropriate",
                ],
                "deployment": [
                    "Use Infrastructure as Code (IaC)",
                    "Implement blue-green deployment strategies",
                    "Use configuration management",
                    "Monitor application metrics and logs",
                ],
            },
            "variables": {
                "PROJECT_NAME": "ComprehensiveApp",
                "API_VERSION": "v2",
                "DATABASE_URL": "postgresql://localhost:5432/comprehensiveapp",
                "REDIS_URL": "redis://localhost:6379/0",
                "SECRET_KEY": "your-secret-key-here",
                "DEBUG": "False",
                "ALLOWED_HOSTS": "localhost,127.0.0.1",
                "FRONTEND_PORT": "3000",
                "BACKEND_PORT": "8000",
                "DOCKER_REGISTRY": "registry.example.com",
                "ENVIRONMENT": "production",
            },
        }
        upf_file = temp_dir / "comprehensive_test.promptrek.yaml"
        with open(upf_file, "w") as f:
            yaml.dump(upf_content, f, default_flow_style=False)
        return upf_file

    @pytest.fixture
    def directory_with_upf_files(self, temp_dir):
        """Create directory structure with multiple UPF files."""
        base_dir = temp_dir / "project_directory"
        base_dir.mkdir()

        # Create multiple UPF files
        files_data = [
            (
                "project1.promptrek.yaml",
                {
                    "schema_version": "1.0.0",
                    "metadata": {
                        "title": "Project 1",
                        "description": "First project",
                        "version": "1.0.0",
                        "author": "test",
                    },
                    "targets": ["claude", "copilot"],
                    "instructions": {"general": ["Project 1 instructions"]},
                },
            ),
            (
                "project2.promptrek.yaml",
                {
                    "schema_version": "1.0.0",
                    "metadata": {
                        "title": "Project 2",
                        "description": "Second project",
                        "version": "1.0.0",
                        "author": "test",
                    },
                    "targets": ["cursor", "continue"],
                    "instructions": {"general": ["Project 2 instructions"]},
                },
            ),
            (
                "subdir/project3.promptrek.yaml",
                {
                    "schema_version": "1.0.0",
                    "metadata": {
                        "title": "Project 3",
                        "description": "Third project",
                        "version": "1.0.0",
                        "author": "test",
                    },
                    "targets": ["cline"],
                    "instructions": {"general": ["Project 3 instructions"]},
                },
            ),
        ]

        for file_path, content in files_data:
            full_path = base_dir / file_path
            full_path.parent.mkdir(parents=True, exist_ok=True)
            with open(full_path, "w") as f:
                yaml.dump(content, f)

        return base_dir

    def test_generate_command_edge_cases(
        self, runner, comprehensive_upf_file, temp_dir
    ):
        """Test generate command edge cases."""
        with runner.isolated_filesystem(temp_dir=temp_dir):
            # Test with multiple variable overrides using correct -V option
            result = runner.invoke(
                cli,
                [
                    "generate",
                    str(comprehensive_upf_file),
                    "--editor",
                    "claude",
                    "-V",
                    "PROJECT_NAME=EdgeCaseApp",
                    "-V",
                    "API_VERSION=v3",
                    "-V",
                    "ENVIRONMENT=testing",
                    "-V",
                    "DEBUG=True",
                ],
            )

            assert result.exit_code == 0
            assert "Generated:" in result.output

    def test_generate_command_all_editors_comprehensive(
        self, runner, comprehensive_upf_file, temp_dir
    ):
        """Test generate command with all editors using comprehensive file."""
        with runner.isolated_filesystem(temp_dir=temp_dir):
            result = runner.invoke(
                cli, ["generate", str(comprehensive_upf_file), "--all"]
            )

            assert result.exit_code == 0
            assert "Generated:" in result.output

    def test_generate_command_with_directory_processing(
        self, runner, directory_with_upf_files, temp_dir
    ):
        """Test generate command with directory processing."""
        with runner.isolated_filesystem(temp_dir=temp_dir):
            result = runner.invoke(
                cli,
                [
                    "generate",
                    "--editor",
                    "claude",
                    "--directory",
                    str(directory_with_upf_files),
                ],
            )

            assert result.exit_code == 0

    def test_generate_command_recursive_directory_processing(
        self, runner, directory_with_upf_files, temp_dir
    ):
        """Test generate command with recursive directory processing."""
        with runner.isolated_filesystem(temp_dir=temp_dir):
            result = runner.invoke(
                cli,
                [
                    "generate",
                    "--editor",
                    "claude",
                    "--directory",
                    str(directory_with_upf_files),
                    "--recursive",
                ],
            )

            assert result.exit_code == 0

    def test_generate_command_dry_run_comprehensive(
        self, runner, comprehensive_upf_file
    ):
        """Test generate command dry-run mode."""
        result = runner.invoke(
            cli,
            [
                "generate",
                str(comprehensive_upf_file),
                "--editor",
                "claude",
                "--dry-run",
            ],
        )

        assert result.exit_code == 0
        assert "Dry run mode" in result.output or "Would create:" in result.output

    def test_generate_command_with_output_directory(
        self, runner, comprehensive_upf_file, temp_dir
    ):
        """Test generate command with custom output directory."""
        output_dir = temp_dir / "custom_output"
        output_dir.mkdir()

        result = runner.invoke(
            cli,
            [
                "generate",
                str(comprehensive_upf_file),
                "--editor",
                "claude",
                "--output",
                str(output_dir),
            ],
        )

        assert result.exit_code == 0

    def test_main_cli_help_comprehensive(self, runner):
        """Test main CLI help with comprehensive output."""
        result = runner.invoke(cli, ["--help"])

        assert result.exit_code == 0
        assert "PrompTrek" in result.output
        assert "init" in result.output
        assert "validate" in result.output
        assert "generate" in result.output

    def test_main_cli_verbose_flag_propagation(self, runner, comprehensive_upf_file):
        """Test verbose flag propagation through subcommands."""
        result = runner.invoke(
            cli, ["--verbose", "validate", str(comprehensive_upf_file)]
        )

        assert result.exit_code == 0

    def test_main_cli_global_options(self, runner, comprehensive_upf_file):
        """Test global CLI options behavior."""
        # Test verbose with generate
        result = runner.invoke(
            cli,
            [
                "--verbose",
                "generate",
                str(comprehensive_upf_file),
                "--editor",
                "claude",
                "--dry-run",
            ],
        )

        assert result.exit_code == 0
        assert "Dry run" in result.output or "Would create:" in result.output

    def test_main_cli_error_handling(self, runner):
        """Test main CLI error handling."""
        # Test invalid command
        result = runner.invoke(cli, ["invalid-command"])

        assert result.exit_code != 0
        assert "Usage:" in result.output or "No such command" in result.output

    def test_main_cli_context_settings(self, runner):
        """Test CLI context settings and configuration."""
        # Test help formatting for generate command
        result = runner.invoke(cli, ["generate", "--help"])

        assert result.exit_code == 0
        assert "Usage:" in result.output
        assert "--editor" in result.output
        assert "--all" in result.output

    def test_init_command_comprehensive(self, runner, temp_dir):
        """Test init command with comprehensive options."""
        output_file = temp_dir / "comprehensive_init.promptrek.yaml"

        result = runner.invoke(cli, ["init", "--output", str(output_file)])

        assert result.exit_code == 0
        assert output_file.exists()

        # Validate the created file
        with open(output_file) as f:
            content = yaml.safe_load(f)
            assert content["schema_version"] == "1.0.0"
            assert "metadata" in content
            assert "targets" in content

    def test_validate_command_comprehensive(self, runner, comprehensive_upf_file):
        """Test validate command with comprehensive file."""
        result = runner.invoke(cli, ["validate", str(comprehensive_upf_file)])

        assert result.exit_code == 0
        assert "valid" in result.output.lower()

    def test_validate_command_verbose(self, runner, comprehensive_upf_file):
        """Test validate command with verbose output."""
        result = runner.invoke(
            cli, ["--verbose", "validate", str(comprehensive_upf_file)]
        )

        assert result.exit_code == 0

    def test_list_editors_command_comprehensive(self, runner):
        """Test list-editors command functionality."""
        result = runner.invoke(cli, ["list-editors"])

        assert result.exit_code == 0
        # Should list available editors
        expected_editors = ["claude", "copilot", "cursor", "continue", "cline", "kiro"]
        found_editors = 0
        for editor in expected_editors:
            if editor in result.output.lower():
                found_editors += 1

        # At least some editors should be listed
        assert found_editors > 0

    def test_cli_integration_workflow(self, runner, temp_dir):
        """Test complete CLI integration workflow."""
        # 1. Initialize a new project
        init_file = temp_dir / "workflow_test.promptrek.yaml"
        result1 = runner.invoke(cli, ["init", "--output", str(init_file)])
        assert result1.exit_code == 0

        # 2. Validate the initialized file
        result2 = runner.invoke(cli, ["validate", str(init_file)])
        assert result2.exit_code == 0

        # 3. Generate outputs using a target that's in the default init file (copilot)
        result3 = runner.invoke(
            cli, ["generate", str(init_file), "--editor", "copilot", "--dry-run"]
        )
        assert result3.exit_code == 0

        # 4. List available editors
        result4 = runner.invoke(cli, ["list-editors"])
        assert result4.exit_code == 0

    def test_error_recovery_scenarios(self, runner, temp_dir):
        """Test CLI error recovery scenarios."""
        # Create invalid YAML file
        invalid_file = temp_dir / "invalid.promptrek.yaml"
        invalid_file.write_text("invalid: yaml: content: [")

        # Test validate with invalid file
        result1 = runner.invoke(cli, ["validate", str(invalid_file)])
        assert result1.exit_code != 0

        # Test generate with invalid file
        result2 = runner.invoke(
            cli, ["generate", str(invalid_file), "--editor", "claude"]
        )
        assert result2.exit_code != 0

    def test_generate_command_invalid_combinations(
        self, runner, comprehensive_upf_file
    ):
        """Test generate command with invalid parameter combinations."""
        # Test with no editor specified and no --all flag
        result = runner.invoke(cli, ["generate", str(comprehensive_upf_file)])

        # Should fail because either --editor or --all is required
        assert result.exit_code != 0

    def test_generate_command_invalid_editor(self, runner, comprehensive_upf_file):
        """Test generate command with invalid editor."""
        result = runner.invoke(
            cli, ["generate", str(comprehensive_upf_file), "--editor", "nonexistent"]
        )

        assert result.exit_code != 0
        assert "Error:" in result.output or "not supported" in result.output.lower()

    def test_multiple_variable_overrides(
        self, runner, comprehensive_upf_file, temp_dir
    ):
        """Test multiple variable overrides with complex scenarios."""
        with runner.isolated_filesystem(temp_dir=temp_dir):
            result = runner.invoke(
                cli,
                [
                    "generate",
                    str(comprehensive_upf_file),
                    "--editor",
                    "claude",
                    "-V",
                    "PROJECT_NAME=MultiVarTest",
                    "-V",
                    "ENVIRONMENT=staging",
                    "-V",
                    "DEBUG=True",
                    "-V",
                    "API_VERSION=v3",
                    "-V",
                    "DATABASE_URL=postgresql://test:test@localhost/test",
                ],
            )

            assert result.exit_code == 0
            assert "Generated:" in result.output

    def test_directory_scanning_patterns(
        self, runner, directory_with_upf_files, temp_dir
    ):
        """Test various directory scanning patterns."""
        with runner.isolated_filesystem(temp_dir=temp_dir):
            # Test non-recursive scanning
            result1 = runner.invoke(
                cli,
                [
                    "generate",
                    "--editor",
                    "claude",
                    "--directory",
                    str(directory_with_upf_files),
                ],
            )
            assert result1.exit_code == 0

            # Test recursive scanning
            result2 = runner.invoke(
                cli,
                [
                    "generate",
                    "--editor",
                    "claude",
                    "--directory",
                    str(directory_with_upf_files),
                    "--recursive",
                ],
            )
            assert result2.exit_code == 0

    def test_output_formatting_and_verbosity(self, runner, comprehensive_upf_file):
        """Test different output formatting and verbosity levels."""
        # Test normal output
        result1 = runner.invoke(
            cli,
            [
                "generate",
                str(comprehensive_upf_file),
                "--editor",
                "claude",
                "--dry-run",
            ],
        )
        assert result1.exit_code == 0

        # Test verbose output
        result2 = runner.invoke(
            cli,
            [
                "--verbose",
                "generate",
                str(comprehensive_upf_file),
                "--editor",
                "claude",
                "--dry-run",
            ],
        )
        assert result2.exit_code == 0

    def test_file_and_directory_combinations(
        self, runner, comprehensive_upf_file, directory_with_upf_files, temp_dir
    ):
        """Test combinations of file and directory processing."""
        with runner.isolated_filesystem(temp_dir=temp_dir):
            # Test single file processing
            result1 = runner.invoke(
                cli,
                [
                    "generate",
                    str(comprehensive_upf_file),
                    "--editor",
                    "claude",
                    "--dry-run",
                ],
            )
            assert result1.exit_code == 0

            # Test directory processing
            result2 = runner.invoke(
                cli,
                [
                    "generate",
                    "--editor",
                    "claude",
                    "--directory",
                    str(directory_with_upf_files),
                    "--dry-run",
                ],
            )
            assert result2.exit_code == 0
