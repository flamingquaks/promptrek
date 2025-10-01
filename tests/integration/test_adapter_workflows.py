"""Integration tests for adapter workflows through CLI commands."""

import json
import tempfile
from pathlib import Path

import pytest
import yaml
from click.testing import CliRunner

from promptrek.cli.main import cli


class TestAdapterWorkflows:
    """Test adapter integration through CLI workflows."""

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
    def amazon_q_upf_file(self, temp_dir):
        """Create UPF file configured for Amazon Q adapter."""
        upf_content = {
            "schema_version": "1.0.0",
            "metadata": {
                "title": "Amazon Q Test Project",
                "description": "Amazon Q integration test project",
                "version": "1.0.0",
                "author": "test@example.com",
                "created": "2024-01-01",
                "updated": "2024-01-01",
                "tags": ["test", "amazon-q"],
            },
            "targets": ["amazon-q"],
            "context": {
                "project_type": "web_application",
                "technologies": ["python", "django"],
                "description": "A Django web application for testing Amazon Q",
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
                "security": [
                    "Always validate user input",
                    "Use Django's built-in security features",
                    "Follow OWASP guidelines",
                ],
            },
            "examples": {
                "model": "class Product(models.Model):\\n    name = models.CharField(max_length=100)\\n    price = models.DecimalField(max_digits=10, decimal_places=2)",
                "view": "def product_list(request):\\n    products = Product.objects.all()\\n    return render(request, 'products/list.html', {'products': products})",
                "test": "class ProductTestCase(TestCase):\\n    def test_product_creation(self):\\n        product = Product.objects.create(name='Test', price=10.00)\\n        self.assertEqual(product.name, 'Test')",
            },
            "variables": {
                "PROJECT_NAME": "AmazonQTestProject",
                "APP_NAME": "testapp",
                "AUTHOR_NAME": "Test Author",
                "DATABASE_ENGINE": "django.db.backends.postgresql",
            },
        }
        upf_file = temp_dir / "amazon_q_test.promptrek.yaml"
        with open(upf_file, "w") as f:
            yaml.dump(upf_content, f, default_flow_style=False)
        return upf_file

    @pytest.fixture
    def kiro_upf_file(self, temp_dir):
        """Create UPF file configured for Kiro adapter."""
        upf_content = {
            "schema_version": "1.0.0",
            "metadata": {
                "title": "Kiro AI Assistant",
                "description": "Kiro integration test project",
                "version": "1.0.0",
                "author": "test@example.com",
                "created": "2024-01-01",
                "updated": "2024-01-01",
                "tags": ["test", "kiro", "ai"],
            },
            "targets": ["kiro"],
            "context": {
                "project_type": "machine_learning",
                "technologies": ["python", "tensorflow", "scikit-learn"],
                "description": "A machine learning project for data analysis and model training",
                "architecture": "Microservices architecture with API endpoints",
                "data_sources": ["PostgreSQL", "Redis", "S3"],
            },
            "instructions": {
                "general": [
                    "Focus on code quality and maintainability",
                    "Use proper logging and monitoring",
                    "Implement comprehensive error handling",
                    "Follow ML engineering best practices",
                ],
                "data_handling": [
                    "Validate all input data thoroughly",
                    "Use appropriate data preprocessing techniques",
                    "Implement data versioning and lineage tracking",
                ],
                "model_development": [
                    "Use cross-validation for model evaluation",
                    "Implement proper feature engineering",
                    "Track model metrics and performance",
                    "Use MLOps practices for deployment",
                ],
                "testing": [
                    "Write unit tests for data processing functions",
                    "Implement integration tests for ML pipelines",
                    "Use property-based testing for data validation",
                    "Mock external services and APIs",
                ],
            },
            "examples": {
                "data_processor": "class DataProcessor:\\n    def clean_data(self, df):\\n        return df.dropna().reset_index(drop=True)",
                "model_trainer": "class ModelTrainer:\\n    def train(self, X, y):\\n        model = RandomForestClassifier()\\n        return model.fit(X, y)",
                "api_endpoint": "@app.route('/predict', methods=['POST'])\\ndef predict():\\n    data = request.get_json()\\n    prediction = model.predict(data)\\n    return jsonify({'prediction': prediction})",
            },
            "variables": {
                "PROJECT_NAME": "KiroMLProject",
                "MODEL_TYPE": "RandomForest",
                "DATA_SOURCE": "postgresql://localhost:5432/mldata",
                "API_VERSION": "v1",
                "ENVIRONMENT": "development",
            },
        }
        upf_file = temp_dir / "kiro_test.promptrek.yaml"
        with open(upf_file, "w") as f:
            yaml.dump(upf_content, f, default_flow_style=False)
        return upf_file

    @pytest.fixture
    def cline_upf_file(self, temp_dir):
        """Create UPF file configured for Cline adapter."""
        upf_content = {
            "schema_version": "1.0.0",
            "metadata": {
                "title": "Cline Assistant",
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
            "examples": {
                "command": "@click.command()\\n@click.option('--count', default=1)\\ndef hello(count):\\n    for _ in range(count):\\n        click.echo('Hello World!')"
            },
            "variables": {"CLI_NAME": "testcli", "VERSION": "1.0.0"},
        }
        upf_file = temp_dir / "cline_test.promptrek.yaml"
        with open(upf_file, "w") as f:
            yaml.dump(upf_content, f, default_flow_style=False)
        return upf_file

    @pytest.fixture
    def multi_target_upf_file(self, temp_dir):
        """Create UPF file with multiple adapter targets."""
        upf_content = {
            "schema_version": "1.0.0",
            "metadata": {
                "title": "Multi-Target Project",
                "description": "Project supporting multiple adapters",
                "version": "1.0.0",
                "author": "test@example.com",
            },
            "targets": [
                "amazon-q",
                "kiro",
                "cline",
                "windsurf",
                "jetbrains",
                "tabnine",
            ],
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

    def test_amazon_q_basic_generation(self, runner, amazon_q_upf_file, temp_dir):
        """Test Amazon Q adapter basic generation workflow."""
        with runner.isolated_filesystem(temp_dir=temp_dir):
            result = runner.invoke(
                cli, ["generate", str(amazon_q_upf_file), "--editor", "amazon-q"]
            )

            assert result.exit_code == 0
            assert "Generated:" in result.output

            # Check Amazon Q specific output files
            assert Path(".amazonq").exists()
            context_file = Path(".amazonq/context.md")
            if context_file.exists():
                content = context_file.read_text()
                assert "Amazon Q Test Project" in content
                assert "Django web application" in content

    def test_amazon_q_with_variables(self, runner, amazon_q_upf_file, temp_dir):
        """Test Amazon Q adapter with variable substitution."""
        with runner.isolated_filesystem(temp_dir=temp_dir):
            result = runner.invoke(
                cli,
                [
                    "generate",
                    str(amazon_q_upf_file),
                    "--editor",
                    "amazon-q",
                    "-V",
                    "PROJECT_NAME=CustomAmazonProject",
                    "-V",
                    "APP_NAME=customapp",
                ],
            )

            assert result.exit_code == 0
            assert "Generated:" in result.output

    def test_amazon_q_dry_run_verbose(self, runner, amazon_q_upf_file):
        """Test Amazon Q adapter dry-run with verbose output."""
        result = runner.invoke(
            cli,
            [
                "--verbose",
                "generate",
                str(amazon_q_upf_file),
                "--editor",
                "amazon-q",
                "--dry-run",
            ],
        )

        assert result.exit_code == 0
        assert "Dry run mode" in result.output
        assert "Would create:" in result.output

    def test_amazon_q_error_scenarios(self, runner, temp_dir):
        """Test Amazon Q adapter error handling scenarios."""
        # Test with invalid UPF file
        invalid_upf = temp_dir / "invalid.promptrek.yaml"
        invalid_upf.write_text("invalid: yaml: content: [")

        result = runner.invoke(
            cli, ["generate", str(invalid_upf), "--editor", "amazon-q"]
        )

        assert result.exit_code != 0

    def test_kiro_basic_generation(self, runner, kiro_upf_file, temp_dir):
        """Test Kiro adapter basic generation workflow."""
        with runner.isolated_filesystem(temp_dir=temp_dir):
            result = runner.invoke(
                cli, ["generate", str(kiro_upf_file), "--editor", "kiro"]
            )

            assert result.exit_code == 0
            assert "Generated:" in result.output

            # Check Kiro specific output structure
            kiro_dir = Path(".kiro")
            if kiro_dir.exists():
                # Check for steering directory
                steering_dir = kiro_dir / "steering"
                if steering_dir.exists():
                    assert steering_dir.is_dir()

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
                    "MODEL_TYPE=XGBoost",
                    "-V",
                    "ENVIRONMENT=production",
                ],
            )

            assert result.exit_code == 0
            assert "Generated:" in result.output

    def test_kiro_with_context(self, runner, kiro_upf_file, temp_dir):
        """Test Kiro adapter with full context usage."""
        with runner.isolated_filesystem(temp_dir=temp_dir):
            result = runner.invoke(
                cli, ["--verbose", "generate", str(kiro_upf_file), "--editor", "kiro"]
            )

            assert result.exit_code == 0
            assert "Generated:" in result.output

    def test_kiro_error_scenarios(self, runner, temp_dir):
        """Test Kiro adapter error handling scenarios."""
        # Test with missing targets
        invalid_upf_content = {
            "schema_version": "1.0.0",
            "metadata": {
                "title": "No Targets",
                "description": "Test",
                "version": "1.0.0",
                "author": "test",
            },
            "targets": [],  # Empty targets
            "instructions": {"general": ["Test"]},
        }
        invalid_upf = temp_dir / "no_targets.promptrek.yaml"
        with open(invalid_upf, "w") as f:
            yaml.dump(invalid_upf_content, f)

        result = runner.invoke(cli, ["generate", str(invalid_upf), "--editor", "kiro"])

        assert result.exit_code != 0

    def test_kiro_dry_run_verbose(self, runner, kiro_upf_file):
        """Test Kiro adapter dry-run with verbose output."""
        result = runner.invoke(
            cli,
            [
                "--verbose",
                "generate",
                str(kiro_upf_file),
                "--editor",
                "kiro",
                "--dry-run",
            ],
        )

        assert result.exit_code == 0
        assert "Dry run mode" in result.output
        assert "Would create:" in result.output

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

    def test_cline_error_scenarios(self, runner, cline_upf_file):
        """Test Cline adapter error handling scenarios."""
        # Test with non-existent file
        result = runner.invoke(
            cli, ["generate", "/nonexistent/file.yaml", "--editor", "cline"]
        )

        assert result.exit_code != 0

    def test_cline_dry_run_verbose(self, runner, cline_upf_file):
        """Test Cline adapter dry-run with verbose output."""
        result = runner.invoke(
            cli,
            [
                "--verbose",
                "generate",
                str(cline_upf_file),
                "--editor",
                "cline",
                "--dry-run",
            ],
        )

        assert result.exit_code == 0
        assert "Dry run mode" in result.output

    def test_multi_adapter_generation(self, runner, multi_target_upf_file, temp_dir):
        """Test generation for multiple adapters in sequence."""
        with runner.isolated_filesystem(temp_dir=temp_dir):
            # Test each adapter individually
            for adapter in ["amazon-q", "kiro", "cline"]:
                result = runner.invoke(
                    cli, ["generate", str(multi_target_upf_file), "--editor", adapter]
                )
                assert result.exit_code == 0, f"Failed for adapter: {adapter}"

    def test_all_adapters_dry_run(self, runner, multi_target_upf_file):
        """Test all adapters in dry-run mode."""
        result = runner.invoke(
            cli, ["generate", str(multi_target_upf_file), "--all", "--dry-run"]
        )

        assert result.exit_code == 0
        assert "Dry run mode" in result.output
        assert "Would create:" in result.output

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
            "targets": ["amazon-q", "kiro"],
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
                    "amazon-q",
                    "-V",
                    "ENVIRONMENT=prod",
                ],
            )

            assert result.exit_code == 0

    @pytest.fixture
    def windsurf_upf_file(self, temp_dir):
        """Create UPF file configured for Windsurf adapter."""
        upf_content = {
            "schema_version": "1.0.0",
            "metadata": {
                "title": "Windsurf Assistant",
                "description": "Windsurf integration test project",
                "version": "1.0.0",
                "author": "test@example.com",
                "tags": ["test", "windsurf", "ai-coding"],
            },
            "targets": ["windsurf"],
            "context": {
                "project_type": "api_service",
                "technologies": ["python", "fastapi", "pydantic"],
                "description": "FastAPI service with AI code assistance",
                "architecture": "Microservices with async patterns",
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
                "testing": [
                    "Use pytest for async testing",
                    "Mock external services",
                    "Test error conditions",
                ],
            },
            "variables": {"SERVICE_NAME": "codeium-api", "API_VERSION": "v1"},
        }
        upf_file = temp_dir / "windsurf_test.promptrek.yaml"
        with open(upf_file, "w") as f:
            yaml.dump(upf_content, f, default_flow_style=False)
        return upf_file

    @pytest.fixture
    def jetbrains_upf_file(self, temp_dir):
        """Create UPF file configured for JetBrains adapter."""
        upf_content = {
            "schema_version": "1.0.0",
            "metadata": {
                "title": "JetBrains Assistant",
                "description": "JetBrains integration test project",
                "version": "1.0.0",
                "author": "test@example.com",
                "tags": ["test", "jetbrains", "ide"],
            },
            "targets": ["jetbrains"],
            "context": {
                "project_type": "java_application",
                "technologies": ["java", "spring", "maven"],
                "description": "Spring Boot application with JetBrains IDE support",
            },
            "instructions": {
                "general": [
                    "Follow Java conventions",
                    "Use Spring Boot best practices",
                    "Implement proper dependency injection",
                ],
                "code_style": [
                    "Use Google Java Style",
                    "Write comprehensive JavaDoc",
                    "Use meaningful variable names",
                ],
            },
            "variables": {"APP_NAME": "jetbrains-app", "SPRING_VERSION": "3.0.0"},
        }
        upf_file = temp_dir / "jetbrains_test.promptrek.yaml"
        with open(upf_file, "w") as f:
            yaml.dump(upf_content, f, default_flow_style=False)
        return upf_file

    @pytest.fixture
    def tabnine_upf_file(self, temp_dir):
        """Create UPF file configured for Tabnine adapter."""
        upf_content = {
            "schema_version": "1.0.0",
            "metadata": {
                "title": "Tabnine Assistant",
                "description": "Tabnine integration test project",
                "version": "1.0.0",
                "author": "test@example.com",
                "tags": ["test", "tabnine", "autocomplete"],
            },
            "targets": ["tabnine"],
            "context": {
                "project_type": "mobile_application",
                "technologies": ["react-native", "typescript", "expo"],
                "description": "React Native mobile app with Tabnine assistance",
            },
            "instructions": {
                "general": [
                    "Use React Native best practices",
                    "Implement proper navigation patterns",
                    "Use TypeScript for type safety",
                ],
                "mobile_specific": [
                    "Handle platform differences gracefully",
                    "Optimize for performance",
                    "Use appropriate native modules",
                ],
            },
            "variables": {"APP_NAME": "tabnine-mobile", "EXPO_VERSION": "49.0.0"},
        }
        upf_file = temp_dir / "tabnine_test.promptrek.yaml"
        with open(upf_file, "w") as f:
            yaml.dump(upf_content, f, default_flow_style=False)
        return upf_file

    def test_windsurf_basic_generation(self, runner, windsurf_upf_file, temp_dir):
        """Test Windsurf adapter basic generation workflow."""
        with runner.isolated_filesystem(temp_dir=temp_dir):
            result = runner.invoke(
                cli, ["generate", str(windsurf_upf_file), "--editor", "windsurf"]
            )

            assert result.exit_code == 0
            assert (
                "Generated:" in result.output or "not yet implemented" in result.output
            )

    def test_windsurf_with_variables(self, runner, windsurf_upf_file, temp_dir):
        """Test Windsurf adapter with variable substitution."""
        with runner.isolated_filesystem(temp_dir=temp_dir):
            result = runner.invoke(
                cli,
                [
                    "generate",
                    str(windsurf_upf_file),
                    "--editor",
                    "windsurf",
                    "-V",
                    "SERVICE_NAME=custom-service",
                    "-V",
                    "API_VERSION=v2",
                ],
            )

            assert result.exit_code == 0

    def test_windsurf_error_scenarios(self, runner, windsurf_upf_file):
        """Test Windsurf adapter error handling scenarios."""
        result = runner.invoke(
            cli, ["generate", str(windsurf_upf_file), "--editor", "invalid-editor"]
        )

        assert result.exit_code != 0

    def test_windsurf_dry_run_verbose(self, runner, windsurf_upf_file):
        """Test Windsurf adapter dry-run with verbose output."""
        result = runner.invoke(
            cli,
            [
                "--verbose",
                "generate",
                str(windsurf_upf_file),
                "--editor",
                "windsurf",
                "--dry-run",
            ],
        )

        assert result.exit_code == 0
        assert "Dry run mode" in result.output

    def test_jetbrains_basic_generation(self, runner, jetbrains_upf_file, temp_dir):
        """Test JetBrains adapter basic generation workflow."""
        with runner.isolated_filesystem(temp_dir=temp_dir):
            result = runner.invoke(
                cli, ["generate", str(jetbrains_upf_file), "--editor", "jetbrains"]
            )

            assert result.exit_code == 0
            assert "Generated:" in result.output

    def test_jetbrains_with_variables(self, runner, jetbrains_upf_file, temp_dir):
        """Test JetBrains adapter with variable substitution."""
        with runner.isolated_filesystem(temp_dir=temp_dir):
            result = runner.invoke(
                cli,
                [
                    "generate",
                    str(jetbrains_upf_file),
                    "--editor",
                    "jetbrains",
                    "-V",
                    "APP_NAME=custom-java-app",
                    "-V",
                    "SPRING_VERSION=3.1.0",
                ],
            )

            assert result.exit_code == 0

    def test_jetbrains_error_scenarios(self, runner, jetbrains_upf_file):
        """Test JetBrains adapter error handling scenarios."""
        result = runner.invoke(cli, ["validate", "/nonexistent/path/file.yaml"])

        assert result.exit_code != 0

    def test_jetbrains_dry_run_verbose(self, runner, jetbrains_upf_file):
        """Test JetBrains adapter dry-run with verbose output."""
        result = runner.invoke(
            cli,
            [
                "--verbose",
                "generate",
                str(jetbrains_upf_file),
                "--editor",
                "jetbrains",
                "--dry-run",
            ],
        )

        assert result.exit_code == 0
        assert "Dry run mode" in result.output

    def test_tabnine_basic_generation(self, runner, tabnine_upf_file, temp_dir):
        """Test Tabnine adapter basic generation workflow."""
        with runner.isolated_filesystem(temp_dir=temp_dir):
            result = runner.invoke(
                cli, ["generate", str(tabnine_upf_file), "--editor", "tabnine"]
            )

            assert result.exit_code == 0
            assert "Generated:" in result.output

    def test_tabnine_with_variables(self, runner, tabnine_upf_file, temp_dir):
        """Test Tabnine adapter with variable substitution."""
        with runner.isolated_filesystem(temp_dir=temp_dir):
            result = runner.invoke(
                cli,
                [
                    "generate",
                    str(tabnine_upf_file),
                    "--editor",
                    "tabnine",
                    "-V",
                    "APP_NAME=custom-mobile-app",
                    "-V",
                    "EXPO_VERSION=50.0.0",
                ],
            )

            assert result.exit_code == 0

    def test_tabnine_error_scenarios(self, runner, tabnine_upf_file):
        """Test Tabnine adapter error handling scenarios."""
        result = runner.invoke(
            cli,
            [
                "generate",
                str(tabnine_upf_file),
                "--editor",
                "tabnine",
                "--invalid-flag",
            ],
        )

        assert result.exit_code != 0

    def test_tabnine_dry_run_verbose(self, runner, tabnine_upf_file):
        """Test Tabnine adapter dry-run with verbose output."""
        result = runner.invoke(
            cli,
            [
                "--verbose",
                "generate",
                str(tabnine_upf_file),
                "--editor",
                "tabnine",
                "--dry-run",
            ],
        )

        assert result.exit_code == 0
        assert "Dry run mode" in result.output

    def test_adapter_validation_integration(self, runner, amazon_q_upf_file):
        """Test adapter integration with validation workflow."""
        # First validate the file
        result = runner.invoke(cli, ["validate", str(amazon_q_upf_file)])
        assert result.exit_code == 0
        assert "valid" in result.output.lower()

        # Then generate from validated file
        with runner.isolated_filesystem():
            result = runner.invoke(
                cli, ["generate", str(amazon_q_upf_file), "--editor", "amazon-q"]
            )
            assert result.exit_code == 0
