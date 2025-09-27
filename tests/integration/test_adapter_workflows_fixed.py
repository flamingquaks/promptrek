"""Fixed integration tests for adapter workflows through CLI commands."""

import json
import tempfile
from pathlib import Path

import pytest
import yaml
from click.testing import CliRunner

from promptrek.cli.main import cli


class TestAdapterWorkflowsFixed:
    """Test adapter integration through CLI workflows with correct options."""

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
    def claude_upf_file(self, temp_dir):
        """Create UPF file configured for Claude adapter (file generation supported)."""
        upf_content = {
            "schema_version": "1.0.0",
            "metadata": {
                "title": "Claude Test Project",
                "description": "Claude integration test project",
                "version": "1.0.0",
                "author": "test@example.com",
                "tags": ["test", "claude"],
            },
            "targets": ["claude"],
            "context": {
                "project_type": "web_application",
                "technologies": ["python", "django"],
                "description": "A Django web application for testing Claude",
                "codebase_overview": "Standard Django project structure with models, views, and templates",
            },
            "instructions": {
                "general": [
                    "Write clean, maintainable Python code",
                    "Follow Django best practices and conventions",
                    "Use proper error handling and logging",
                ],
                "code_style": [
                    "Use PEP 8 style guidelines",
                    "Write docstrings for all functions and classes",
                    "Use type hints where appropriate",
                ],
                "testing": [
                    "Write unit tests for all business logic",
                    "Use Django's test framework",
                    "Mock external dependencies",
                ],
            },
            "examples": {
                "model": "class Product(models.Model):\\n    name = models.CharField(max_length=100)\\n    price = models.DecimalField(max_digits=10, decimal_places=2)",
                "view": "def product_list(request):\\n    products = Product.objects.all()\\n    return render(request, 'products/list.html', {'products': products})",
            },
            "variables": {
                "PROJECT_NAME": "ClaudeTestProject",
                "APP_NAME": "testapp",
                "AUTHOR_NAME": "Test Author",
                "DATABASE_ENGINE": "django.db.backends.postgresql",
            },
        }
        upf_file = temp_dir / "claude_test.promptrek.yaml"
        with open(upf_file, "w") as f:
            yaml.dump(upf_content, f, default_flow_style=False)
        return upf_file

    @pytest.fixture
    def copilot_upf_file(self, temp_dir):
        """Create UPF file configured for Copilot adapter (file generation supported)."""
        upf_content = {
            "schema_version": "1.0.0",
            "metadata": {
                "title": "Copilot Test Project",
                "description": "Copilot integration test project",
                "version": "1.0.0",
                "author": "test@example.com",
                "tags": ["test", "copilot"],
            },
            "targets": ["copilot"],
            "context": {
                "project_type": "javascript_application",
                "technologies": ["javascript", "react", "node"],
                "description": "A React application for testing Copilot",
            },
            "instructions": {
                "general": [
                    "Write modern JavaScript code",
                    "Follow React best practices",
                    "Use ES6+ features",
                ],
                "react": [
                    "Use functional components with hooks",
                    "Implement proper prop validation",
                    "Use meaningful component names",
                ],
            },
            "variables": {
                "PROJECT_NAME": "CopilotTestProject",
                "FRAMEWORK": "React",
                "VERSION": "18.0.0",
            },
        }
        upf_file = temp_dir / "copilot_test.promptrek.yaml"
        with open(upf_file, "w") as f:
            yaml.dump(upf_content, f, default_flow_style=False)
        return upf_file

    @pytest.fixture
    def cursor_upf_file(self, temp_dir):
        """Create UPF file configured for Cursor adapter (file generation supported)."""
        upf_content = {
            "schema_version": "1.0.0",
            "metadata": {
                "title": "Cursor Test Project",
                "description": "Cursor integration test project",
                "version": "1.0.0",
                "author": "test@example.com",
                "tags": ["test", "cursor"],
            },
            "targets": ["cursor"],
            "context": {
                "project_type": "python_application",
                "technologies": ["python", "fastapi"],
                "description": "A FastAPI application for testing Cursor",
            },
            "instructions": {
                "general": [
                    "Use FastAPI best practices",
                    "Implement async/await patterns",
                    "Use Pydantic for data validation",
                ],
                "api_design": [
                    "Follow RESTful conventions",
                    "Include proper error responses",
                    "Use dependency injection",
                ],
            },
            "variables": {
                "SERVICE_NAME": "cursor-api",
                "API_VERSION": "v1",
                "FRAMEWORK": "FastAPI",
            },
        }
        upf_file = temp_dir / "cursor_test.promptrek.yaml"
        with open(upf_file, "w") as f:
            yaml.dump(upf_content, f, default_flow_style=False)
        return upf_file

    @pytest.fixture
    def continue_upf_file(self, temp_dir):
        """Create UPF file configured for Continue adapter (file generation supported)."""
        upf_content = {
            "schema_version": "1.0.0",
            "metadata": {
                "title": "Continue Test Project",
                "description": "Continue integration test project",
                "version": "1.0.0",
                "author": "test@example.com",
                "tags": ["test", "continue"],
            },
            "targets": ["continue"],
            "context": {
                "project_type": "machine_learning",
                "technologies": ["python", "pytorch", "numpy"],
                "description": "A ML project for testing Continue",
            },
            "instructions": {
                "general": [
                    "Use PyTorch best practices",
                    "Implement proper model training patterns",
                    "Use proper data handling",
                ],
                "ml_specific": [
                    "Use proper data loaders",
                    "Implement model checkpointing",
                    "Use tensorboard for logging",
                ],
            },
            "variables": {
                "MODEL_NAME": "transformer",
                "BATCH_SIZE": "32",
                "LEARNING_RATE": "0.001",
            },
        }
        upf_file = temp_dir / "continue_test.promptrek.yaml"
        with open(upf_file, "w") as f:
            yaml.dump(upf_content, f, default_flow_style=False)
        return upf_file

    @pytest.fixture
    def cline_upf_file(self, temp_dir):
        """Create UPF file configured for Cline adapter (file generation supported)."""
        upf_content = {
            "schema_version": "1.0.0",
            "metadata": {
                "title": "Cline Test Project",
                "description": "Cline integration test project",
                "version": "1.0.0",
                "author": "test@example.com",
                "tags": ["test", "cline"],
            },
            "targets": ["cline"],
            "context": {
                "project_type": "cli_application",
                "technologies": ["python", "click", "rich"],
                "description": "A command-line application with rich formatting",
            },
            "instructions": {
                "general": [
                    "Build intuitive command-line interfaces",
                    "Use rich formatting for better UX",
                    "Implement proper argument validation",
                ],
                "cli_design": [
                    "Use click for command structure",
                    "Provide helpful error messages",
                    "Include progress bars for long operations",
                ],
            },
            "variables": {
                "CLI_NAME": "testcli",
                "VERSION": "1.0.0",
                "FRAMEWORK": "Click",
            },
        }
        upf_file = temp_dir / "cline_test.promptrek.yaml"
        with open(upf_file, "w") as f:
            yaml.dump(upf_content, f, default_flow_style=False)
        return upf_file

    @pytest.fixture
    def kiro_upf_file(self, temp_dir):
        """Create UPF file configured for Kiro adapter (file generation supported)."""
        upf_content = {
            "schema_version": "1.0.0",
            "metadata": {
                "title": "Kiro Test Project",
                "description": "Kiro integration test project",
                "version": "1.0.0",
                "author": "test@example.com",
                "tags": ["test", "kiro"],
            },
            "targets": ["kiro"],
            "context": {
                "project_type": "data_science",
                "technologies": ["python", "pandas", "scikit-learn"],
                "description": "A data science project for testing Kiro",
            },
            "instructions": {
                "general": [
                    "Use data science best practices",
                    "Implement proper data analysis patterns",
                    "Use appropriate visualization techniques",
                ],
                "data_analysis": [
                    "Use pandas for data manipulation",
                    "Implement proper data validation",
                    "Use matplotlib/seaborn for visualization",
                ],
            },
            "variables": {
                "PROJECT_NAME": "KiroDataProject",
                "DATA_SOURCE": "csv",
                "ANALYSIS_TYPE": "classification",
            },
        }
        upf_file = temp_dir / "kiro_test.promptrek.yaml"
        with open(upf_file, "w") as f:
            yaml.dump(upf_content, f, default_flow_style=False)
        return upf_file

    @pytest.fixture
    def multi_target_upf_file(self, temp_dir):
        """Create UPF file with multiple supported adapter targets."""
        upf_content = {
            "schema_version": "1.0.0",
            "metadata": {
                "title": "Multi-Target Project",
                "description": "Project supporting multiple adapters",
                "version": "1.0.0",
                "author": "test@example.com",
            },
            "targets": ["claude", "copilot", "cursor", "continue", "cline", "kiro"],
            "context": {
                "project_type": "full_stack_application",
                "technologies": ["python", "javascript", "react", "django"],
            },
            "instructions": {
                "general": ["Write clean, maintainable code"],
                "frontend": ["Use React best practices"],
                "backend": ["Follow Django conventions"],
            },
            "variables": {
                "PROJECT_NAME": "MultiTargetApp",
                "FRAMEWORK": "Django+React",
            },
        }
        upf_file = temp_dir / "multi_target.promptrek.yaml"
        with open(upf_file, "w") as f:
            yaml.dump(upf_content, f, default_flow_style=False)
        return upf_file

    # Test file generation adapters (claude, copilot, cursor, continue, cline, kiro)
    def test_claude_basic_generation(self, runner, claude_upf_file, temp_dir):
        """Test Claude adapter basic generation workflow."""
        with runner.isolated_filesystem(temp_dir=temp_dir):
            result = runner.invoke(
                cli, ["generate", str(claude_upf_file), "--editor", "claude"]
            )

            assert result.exit_code == 0
            assert "Generated:" in result.output

            # Check Claude specific output files
            context_files = [Path(".claude/CLAUDE.md"), Path(".claude-context.md")]
            # At least one of these should exist
            assert any(f.exists() for f in context_files)

    def test_claude_with_variables(self, runner, claude_upf_file, temp_dir):
        """Test Claude adapter with variable substitution using correct -V option."""
        with runner.isolated_filesystem(temp_dir=temp_dir):
            result = runner.invoke(
                cli,
                [
                    "generate",
                    str(claude_upf_file),
                    "--editor",
                    "claude",
                    "-V",
                    "PROJECT_NAME=CustomClaudeProject",
                    "-V",
                    "APP_NAME=customapp",
                ],
            )

            assert result.exit_code == 0
            assert "Generated:" in result.output

    def test_claude_dry_run_verbose(self, runner, claude_upf_file):
        """Test Claude adapter dry-run with verbose output."""
        result = runner.invoke(
            cli,
            [
                "--verbose",
                "generate",
                str(claude_upf_file),
                "--editor",
                "claude",
                "--dry-run",
            ],
        )

        assert result.exit_code == 0
        assert "Dry run mode" in result.output or "Would create:" in result.output

    def test_copilot_basic_generation(self, runner, copilot_upf_file, temp_dir):
        """Test Copilot adapter basic generation workflow."""
        with runner.isolated_filesystem(temp_dir=temp_dir):
            result = runner.invoke(
                cli, ["generate", str(copilot_upf_file), "--editor", "copilot"]
            )

            assert result.exit_code == 0
            assert "Generated:" in result.output

            # Check Copilot specific output files
            copilot_file = Path(".github/copilot-instructions.md")
            if copilot_file.exists():
                content = copilot_file.read_text()
                assert "Copilot Test Project" in content

    def test_copilot_with_variables(self, runner, copilot_upf_file, temp_dir):
        """Test Copilot adapter with variable substitution."""
        with runner.isolated_filesystem(temp_dir=temp_dir):
            result = runner.invoke(
                cli,
                [
                    "generate",
                    str(copilot_upf_file),
                    "--editor",
                    "copilot",
                    "-V",
                    "PROJECT_NAME=CustomCopilotProject",
                    "-V",
                    "FRAMEWORK=Vue",
                ],
            )

            assert result.exit_code == 0
            assert "Generated:" in result.output

    def test_cursor_basic_generation(self, runner, cursor_upf_file, temp_dir):
        """Test Cursor adapter basic generation workflow."""
        with runner.isolated_filesystem(temp_dir=temp_dir):
            result = runner.invoke(
                cli, ["generate", str(cursor_upf_file), "--editor", "cursor"]
            )

            assert result.exit_code == 0
            assert "Generated:" in result.output

    def test_cursor_with_variables(self, runner, cursor_upf_file, temp_dir):
        """Test Cursor adapter with variable substitution."""
        with runner.isolated_filesystem(temp_dir=temp_dir):
            result = runner.invoke(
                cli,
                [
                    "generate",
                    str(cursor_upf_file),
                    "--editor",
                    "cursor",
                    "-V",
                    "SERVICE_NAME=custom-service",
                    "-V",
                    "API_VERSION=v2",
                ],
            )

            assert result.exit_code == 0
            assert "Generated:" in result.output

    def test_continue_basic_generation(self, runner, continue_upf_file, temp_dir):
        """Test Continue adapter basic generation workflow."""
        with runner.isolated_filesystem(temp_dir=temp_dir):
            result = runner.invoke(
                cli, ["generate", str(continue_upf_file), "--editor", "continue"]
            )

            assert result.exit_code == 0
            assert "Generated:" in result.output

    def test_continue_with_variables(self, runner, continue_upf_file, temp_dir):
        """Test Continue adapter with variable substitution."""
        with runner.isolated_filesystem(temp_dir=temp_dir):
            result = runner.invoke(
                cli,
                [
                    "generate",
                    str(continue_upf_file),
                    "--editor",
                    "continue",
                    "-V",
                    "MODEL_NAME=bert",
                    "-V",
                    "BATCH_SIZE=64",
                ],
            )

            assert result.exit_code == 0
            assert "Generated:" in result.output

    def test_cline_basic_generation(self, runner, cline_upf_file, temp_dir):
        """Test Cline adapter basic generation workflow."""
        with runner.isolated_filesystem(temp_dir=temp_dir):
            result = runner.invoke(
                cli, ["generate", str(cline_upf_file), "--editor", "cline"]
            )

            assert result.exit_code == 0
            assert "Generated:" in result.output

    def test_cline_with_variables(self, runner, cline_upf_file, temp_dir):
        """Test Cline adapter with variable substitution."""
        with runner.isolated_filesystem(temp_dir=temp_dir):
            result = runner.invoke(
                cli,
                [
                    "generate",
                    str(cline_upf_file),
                    "--editor",
                    "cline",
                    "-V",
                    "CLI_NAME=mycustomcli",
                    "-V",
                    "VERSION=2.0.0",
                ],
            )

            assert result.exit_code == 0
            assert "Generated:" in result.output

    def test_kiro_basic_generation(self, runner, kiro_upf_file, temp_dir):
        """Test Kiro adapter basic generation workflow."""
        with runner.isolated_filesystem(temp_dir=temp_dir):
            result = runner.invoke(
                cli, ["generate", str(kiro_upf_file), "--editor", "kiro"]
            )

            assert result.exit_code == 0
            assert "Generated:" in result.output

    def test_kiro_with_variables(self, runner, kiro_upf_file, temp_dir):
        """Test Kiro adapter with variable substitution."""
        with runner.isolated_filesystem(temp_dir=temp_dir):
            result = runner.invoke(
                cli,
                [
                    "generate",
                    str(kiro_upf_file),
                    "--editor",
                    "kiro",
                    "-V",
                    "PROJECT_NAME=CustomKiroProject",
                    "-V",
                    "DATA_SOURCE=database",
                    "-V",
                    "ANALYSIS_TYPE=regression",
                ],
            )

            assert result.exit_code == 0
            assert "Generated:" in result.output

    def test_multi_adapter_generation_sequential(
        self, runner, multi_target_upf_file, temp_dir
    ):
        """Test generating for multiple adapters sequentially."""
        adapters = ["claude", "copilot", "cursor", "continue", "cline", "kiro"]

        with runner.isolated_filesystem(temp_dir=temp_dir):
            for adapter in adapters:
                result = runner.invoke(
                    cli, ["generate", str(multi_target_upf_file), "--editor", adapter]
                )
                assert result.exit_code == 0, f"Failed for adapter: {adapter}"
                assert "Generated:" in result.output

    def test_multi_adapter_generation_all(
        self, runner, multi_target_upf_file, temp_dir
    ):
        """Test generating for all adapters at once."""
        with runner.isolated_filesystem(temp_dir=temp_dir):
            result = runner.invoke(
                cli, ["generate", str(multi_target_upf_file), "--all"]
            )

            assert result.exit_code == 0
            assert "Generated:" in result.output

    def test_adapter_with_conditionals(self, runner, temp_dir):
        """Test adapters with conditional instructions."""
        upf_content = {
            "schema_version": "1.0.0",
            "metadata": {
                "title": "Conditional Test",
                "description": "Test conditional processing",
                "version": "1.0.0",
                "author": "test@example.com",
            },
            "targets": ["claude", "copilot"],
            "context": {
                "project_type": "{{ PROJECT_TYPE }}",
                "environment": "{{ ENVIRONMENT }}",
            },
            "instructions": {
                "general": [
                    "{% if PROJECT_TYPE == 'web' %}Use web-specific patterns{% endif %}",
                    "{% if ENVIRONMENT == 'prod' %}Enable production optimizations{% endif %}",
                ]
            },
            "variables": {"PROJECT_TYPE": "web", "ENVIRONMENT": "dev"},
        }
        upf_file = temp_dir / "conditional_test.promptrek.yaml"
        with open(upf_file, "w") as f:
            yaml.dump(upf_content, f)

        with runner.isolated_filesystem(temp_dir=temp_dir):
            result = runner.invoke(
                cli,
                [
                    "generate",
                    str(upf_file),
                    "--editor",
                    "claude",
                    "-V",
                    "ENVIRONMENT=prod",
                ],
            )

            assert result.exit_code == 0
            assert "Generated:" in result.output

    def test_adapter_validation_integration(self, runner, claude_upf_file):
        """Test adapter integration with validation workflow."""
        # First validate the file
        result = runner.invoke(cli, ["validate", str(claude_upf_file)])
        assert result.exit_code == 0
        assert "valid" in result.output.lower()

        # Then generate from validated file
        with runner.isolated_filesystem():
            result = runner.invoke(
                cli, ["generate", str(claude_upf_file), "--editor", "claude"]
            )
            assert result.exit_code == 0

    def test_error_handling_invalid_editor(self, runner, claude_upf_file):
        """Test error handling with invalid editor."""
        result = runner.invoke(
            cli, ["generate", str(claude_upf_file), "--editor", "nonexistent"]
        )

        assert result.exit_code != 0
        assert "Error:" in result.output or "not supported" in result.output.lower()

    def test_error_handling_nonexistent_file(self, runner):
        """Test error handling with nonexistent file."""
        result = runner.invoke(
            cli, ["generate", "/nonexistent/file.yaml", "--editor", "claude"]
        )

        assert result.exit_code != 0

    def test_dry_run_comprehensive(self, runner, multi_target_upf_file):
        """Test dry-run mode comprehensively."""
        result = runner.invoke(
            cli, ["generate", str(multi_target_upf_file), "--all", "--dry-run"]
        )

        assert result.exit_code == 0
        assert "Dry run mode" in result.output or "Would create:" in result.output

    def test_verbose_output(self, runner, claude_upf_file):
        """Test verbose output mode."""
        result = runner.invoke(
            cli,
            [
                "--verbose",
                "generate",
                str(claude_upf_file),
                "--editor",
                "claude",
                "--dry-run",
            ],
        )

        assert result.exit_code == 0
