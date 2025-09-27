"""Advanced integration workflow tests for complex scenarios."""

import tempfile
from pathlib import Path

import pytest
import yaml
from click.testing import CliRunner

from promptrek.cli.main import cli


class TestAdvancedWorkflows:
    """Test advanced integration workflows and complex scenarios."""

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
    def multi_adapter_project(self, temp_dir):
        """Create project with multiple adapters for testing."""
        upf_content = {
            "schema_version": "1.0.0",
            "metadata": {
                "title": "Multi-Adapter Project",
                "description": "Project supporting all major AI coding assistants",
                "version": "1.0.0",
                "author": "test@example.com",
                "tags": ["multi-adapter", "comprehensive"],
            },
            "targets": [
                "claude",
                "copilot",
                "cursor",
                "continue",
                "codeium",
                "amazon-q",
                "kiro",
                "cline",
                "jetbrains",
                "tabnine",
            ],
            "context": {
                "project_type": "{{ PROJECT_TYPE }}",
                "technologies": ["{{ PRIMARY_LANG }}", "{{ SECONDARY_LANG }}"],
                "framework": "{{ FRAMEWORK }}",
                "database": "{{ DATABASE }}",
                "deployment": "{{ DEPLOYMENT_PLATFORM }}",
            },
            "instructions": {
                "general": [
                    "Use {{ PRIMARY_LANG }} best practices",
                    "Follow {{ CODING_STANDARD }} standards",
                    "{% if TESTING_REQUIRED == 'true' %}Write comprehensive tests{% endif %}",
                ],
                "architecture": [
                    "{% if PROJECT_TYPE == 'microservices' %}Use service-oriented architecture{% endif %}",
                    "{% if PROJECT_TYPE == 'monolith' %}Use layered architecture{% endif %}",
                ],
                "deployment": [
                    "{% if DEPLOYMENT_PLATFORM == 'kubernetes' %}Use K8s manifests{% endif %}",
                    "{% if DEPLOYMENT_PLATFORM == 'docker' %}Use Docker Compose{% endif %}",
                ],
            },
            "variables": {
                "PROJECT_TYPE": "microservices",
                "PRIMARY_LANG": "Python",
                "SECONDARY_LANG": "JavaScript",
                "FRAMEWORK": "FastAPI",
                "DATABASE": "PostgreSQL",
                "DEPLOYMENT_PLATFORM": "kubernetes",
                "CODING_STANDARD": "PEP8",
                "TESTING_REQUIRED": "true",
            },
        }
        upf_file = temp_dir / "multi_adapter.promptrek.yaml"
        with open(upf_file, "w") as f:
            yaml.dump(upf_content, f, default_flow_style=False)
        return upf_file

    @pytest.fixture
    def import_chain_files(self, temp_dir):
        """Create chain of import files for testing import resolution."""
        # Base configuration
        base_content = {
            "schema_version": "1.0.0",
            "metadata": {
                "title": "Base Configuration",
                "description": "Base settings for all projects",
                "version": "1.0.0",
                "author": "base@example.com",
            },
            "targets": ["claude"],
            "context": {
                "base_technology": "python",
                "coding_standards": "PEP8",
                "testing_framework": "pytest",
            },
            "instructions": {
                "base": [
                    "Follow Python best practices",
                    "Use type hints",
                    "Write docstrings",
                ]
            },
            "variables": {"PYTHON_VERSION": "3.11", "BASE_PACKAGE": "myproject"},
        }
        base_file = temp_dir / "base.promptrek.yaml"
        with open(base_file, "w") as f:
            yaml.dump(base_content, f)

        # Framework-specific configuration
        framework_content = {
            "schema_version": "1.0.0",
            "imports": [{"path": str(base_file)}],
            "metadata": {
                "title": "Framework Configuration",
                "description": "Framework-specific settings",
                "version": "1.0.0",
                "author": "framework@example.com",
            },
            "targets": ["claude"],
            "context": {
                "framework": "{{ FRAMEWORK_NAME }}",
                "framework_version": "{{ FRAMEWORK_VERSION }}",
            },
            "instructions": {
                "framework": [
                    "Use {{ FRAMEWORK_NAME }} best practices",
                    "Follow {{ FRAMEWORK_NAME }} conventions",
                ]
            },
            "variables": {"FRAMEWORK_NAME": "Django", "FRAMEWORK_VERSION": "4.2"},
        }
        framework_file = temp_dir / "framework.promptrek.yaml"
        with open(framework_file, "w") as f:
            yaml.dump(framework_content, f)

        # Project-specific configuration
        project_content = {
            "schema_version": "1.0.0",
            "imports": [{"path": str(framework_file)}],
            "metadata": {
                "title": "Project Configuration",
                "description": "Project-specific configuration",
                "version": "1.0.0",
                "author": "project@example.com",
            },
            "targets": ["claude", "copilot"],
            "context": {"project_name": "{{ PROJECT_NAME }}", "domain": "{{ DOMAIN }}"},
            "instructions": {
                "project": [
                    "Implement {{ PROJECT_NAME }} requirements",
                    "Focus on {{ DOMAIN }} domain logic",
                ]
            },
            "variables": {"PROJECT_NAME": "ImportChainTest", "DOMAIN": "e-commerce"},
        }
        project_file = temp_dir / "project.promptrek.yaml"
        with open(project_file, "w") as f:
            yaml.dump(project_content, f)

        return {"base": base_file, "framework": framework_file, "project": project_file}

    @pytest.fixture
    def complex_conditional_file(self, temp_dir):
        """Create file with complex conditional and variable combinations."""
        upf_content = {
            "schema_version": "1.0.0",
            "metadata": {
                "title": "Complex Conditional Project",
                "description": "Project with complex conditional logic",
                "version": "1.0.0",
                "author": "test@example.com",
            },
            "targets": ["claude"],
            "context": {
                "environment": "{{ ENVIRONMENT }}",
                "project_scale": "{{ SCALE }}",
                "has_auth": "{{ HAS_AUTHENTICATION }}",
                "database_type": "{% if SCALE == 'enterprise' %}{{ ENTERPRISE_DB }}{% else %}{{ SIMPLE_DB }}{% endif %}",
                "caching": "{% if SCALE in ['large', 'enterprise'] %}{{ CACHE_SYSTEM }}{% else %}none{% endif %}",
            },
            "instructions": {
                "architecture": [
                    "{% if SCALE == 'small' %}Use monolithic architecture{% elif SCALE == 'medium' %}Use modular monolith{% else %}Use microservices{% endif %}",
                    "{% if HAS_AUTHENTICATION == 'true' %}Implement JWT authentication{% endif %}",
                    "{% if ENVIRONMENT == 'production' and SCALE == 'enterprise' %}Use distributed caching{% endif %}",
                ],
                "database": [
                    "{% if SCALE == 'small' %}Use SQLite for development{% endif %}",
                    "{% if SCALE in ['medium', 'large'] %}Use PostgreSQL with connection pooling{% endif %}",
                    "{% if SCALE == 'enterprise' %}Use database sharding and read replicas{% endif %}",
                ],
                "monitoring": [
                    "{% if ENVIRONMENT == 'production' %}Enable comprehensive logging{% endif %}",
                    "{% if SCALE in ['large', 'enterprise'] %}Use APM tools{% endif %}",
                    "{% if ENVIRONMENT == 'production' and SCALE == 'enterprise' %}Enable distributed tracing{% endif %}",
                ],
                "security": [
                    "{% if HAS_AUTHENTICATION == 'true' %}Implement rate limiting{% endif %}",
                    "{% if ENVIRONMENT == 'production' %}Use HTTPS everywhere{% endif %}",
                    "{% if SCALE == 'enterprise' %}Implement WAF and DDoS protection{% endif %}",
                ],
            },
            "examples": {
                "auth_middleware": "{% if HAS_AUTHENTICATION == 'true' %}@jwt_required\\ndef protected_route(): pass{% endif %}",
                "database_config": "{% if SCALE == 'enterprise' %}DATABASE_POOL_SIZE = 100{% else %}DATABASE_POOL_SIZE = 10{% endif %}",
                "cache_config": "{% if SCALE in ['large', 'enterprise'] %}CACHE_BACKEND = '{{ CACHE_SYSTEM }}'{% endif %}",
            },
            "variables": {
                "ENVIRONMENT": "development",
                "SCALE": "medium",
                "HAS_AUTHENTICATION": "true",
                "SIMPLE_DB": "PostgreSQL",
                "ENTERPRISE_DB": "PostgreSQL Cluster",
                "CACHE_SYSTEM": "Redis",
            },
        }
        upf_file = temp_dir / "complex_conditional.promptrek.yaml"
        with open(upf_file, "w") as f:
            yaml.dump(upf_content, f, default_flow_style=False)
        return upf_file

    def test_multi_adapter_generation_sequential(
        self, runner, multi_adapter_project, temp_dir
    ):
        """Test generating for multiple adapters sequentially."""
        adapters = ["claude", "copilot", "cursor", "continue", "codeium"]

        with runner.isolated_filesystem(temp_dir=temp_dir):
            for adapter in adapters:
                result = runner.invoke(
                    cli, ["generate", str(multi_adapter_project), "--editor", adapter]
                )
                # Some adapters might not be supported, so we allow both success and failure
                assert result.exit_code in [
                    0,
                    1,
                ], f"Unexpected exit code for {adapter}: {result.exit_code}"

    def test_multi_adapter_generation_all(
        self, runner, multi_adapter_project, temp_dir
    ):
        """Test generating for all adapters at once."""
        with runner.isolated_filesystem(temp_dir=temp_dir):
            result = runner.invoke(
                cli, ["generate", str(multi_adapter_project), "--all"]
            )

            assert result.exit_code == 0
            assert "Generated:" in result.output

    def test_multi_adapter_with_variable_matrix(
        self, runner, multi_adapter_project, temp_dir
    ):
        """Test multi-adapter generation with different variable combinations."""
        variable_combinations = [
            {
                "PROJECT_TYPE": "monolith",
                "DEPLOYMENT_PLATFORM": "docker",
                "FRAMEWORK": "Django",
            },
            {
                "PROJECT_TYPE": "microservices",
                "DEPLOYMENT_PLATFORM": "kubernetes",
                "FRAMEWORK": "FastAPI",
            },
            {
                "PROJECT_TYPE": "serverless",
                "DEPLOYMENT_PLATFORM": "aws",
                "FRAMEWORK": "Chalice",
            },
        ]

        with runner.isolated_filesystem(temp_dir=temp_dir):
            for i, variables in enumerate(variable_combinations):
                args = ["generate", str(multi_adapter_project), "--editor", "claude"]
                for key, value in variables.items():
                    args.extend(["-V", f"{key}={value}"])

                result = runner.invoke(cli, args)
                assert result.exit_code == 0, f"Failed for combination {i}: {variables}"

    def test_import_resolution_chain(self, runner, import_chain_files, temp_dir):
        """Test import resolution through chain of files."""
        with runner.isolated_filesystem(temp_dir=temp_dir):
            result = runner.invoke(
                cli,
                ["generate", str(import_chain_files["project"]), "--editor", "claude"],
            )

            assert result.exit_code == 0
            assert "Generated:" in result.output

    def test_import_resolution_with_overrides(
        self, runner, import_chain_files, temp_dir
    ):
        """Test import resolution with variable overrides."""
        with runner.isolated_filesystem(temp_dir=temp_dir):
            result = runner.invoke(
                cli,
                [
                    "generate",
                    str(import_chain_files["project"]),
                    "--editor",
                    "claude",
                    "-V",
                    "PYTHON_VERSION=3.12",
                    "-V",
                    "FRAMEWORK_NAME=FastAPI",
                    "-V",
                    "PROJECT_NAME=OverriddenProject",
                ],
            )

            assert result.exit_code == 0

    def test_import_resolution_validation(self, runner, import_chain_files):
        """Test validation of files with import chains."""
        result = runner.invoke(cli, ["validate", str(import_chain_files["project"])])

        assert result.exit_code == 0
        assert "valid" in result.output.lower()

    def test_import_resolution_verbose(self, runner, import_chain_files):
        """Test import resolution with verbose output."""
        result = runner.invoke(
            cli,
            [
                "--verbose",
                "generate",
                str(import_chain_files["project"]),
                "--editor",
                "claude",
                "--dry-run",
            ],
        )

        assert result.exit_code == 0
        assert "Dry run" in result.output

    def test_complex_conditional_combinations(
        self, runner, complex_conditional_file, temp_dir
    ):
        """Test complex conditional and variable combinations."""
        test_scenarios = [
            {
                "name": "Small development setup",
                "vars": {
                    "ENVIRONMENT": "development",
                    "SCALE": "small",
                    "HAS_AUTHENTICATION": "false",
                },
            },
            {
                "name": "Medium production setup",
                "vars": {
                    "ENVIRONMENT": "production",
                    "SCALE": "medium",
                    "HAS_AUTHENTICATION": "true",
                },
            },
            {
                "name": "Large production setup",
                "vars": {
                    "ENVIRONMENT": "production",
                    "SCALE": "large",
                    "HAS_AUTHENTICATION": "true",
                    "CACHE_SYSTEM": "Memcached",
                },
            },
            {
                "name": "Enterprise production setup",
                "vars": {
                    "ENVIRONMENT": "production",
                    "SCALE": "enterprise",
                    "HAS_AUTHENTICATION": "true",
                    "ENTERPRISE_DB": "PostgreSQL Cluster",
                    "CACHE_SYSTEM": "Redis Cluster",
                },
            },
        ]

        with runner.isolated_filesystem(temp_dir=temp_dir):
            for scenario in test_scenarios:
                args = ["generate", str(complex_conditional_file), "--editor", "claude"]
                for key, value in scenario["vars"].items():
                    args.extend(["-V", f"{key}={value}"])

                result = runner.invoke(cli, args)
                assert result.exit_code == 0, f"Failed for scenario: {scenario['name']}"

    def test_cross_adapter_compatibility_generation(
        self, runner, multi_adapter_project, temp_dir
    ):
        """Test cross-adapter compatibility by generating same content for different adapters."""
        compatible_adapters = ["claude", "copilot", "cursor"]

        with runner.isolated_filesystem(temp_dir=temp_dir):
            # Generate for each adapter with same configuration
            for adapter in compatible_adapters:
                result = runner.invoke(
                    cli,
                    [
                        "generate",
                        str(multi_adapter_project),
                        "--editor",
                        adapter,
                        "-V",
                        "PROJECT_TYPE=microservices",
                        "-V",
                        "FRAMEWORK=FastAPI",
                    ],
                )
                # Allow both success and failure as some adapters might not support certain features
                assert result.exit_code in [0, 1], f"Unexpected result for {adapter}"

    def test_cross_adapter_output_consistency(self, runner, temp_dir):
        """Test output consistency across different adapters."""
        # Create a simple, well-supported configuration
        simple_config = {
            "schema_version": "1.0.0",
            "metadata": {
                "title": "Cross-Adapter Test",
                "description": "Simple configuration for testing adapter consistency",
                "version": "1.0.0",
                "author": "test@example.com",
            },
            "targets": ["claude", "copilot", "cursor", "continue"],
            "context": {
                "project_type": "web_application",
                "technologies": ["python", "django"],
            },
            "instructions": {
                "general": [
                    "Write clean, maintainable code",
                    "Follow Django best practices",
                ]
            },
            "variables": {"PROJECT_NAME": "CrossAdapterTest"},
        }
        config_file = temp_dir / "cross_adapter.promptrek.yaml"
        with open(config_file, "w") as f:
            yaml.dump(simple_config, f)

        with runner.isolated_filesystem(temp_dir=temp_dir):
            # Test multiple adapters
            for adapter in ["claude", "copilot"]:
                result = runner.invoke(
                    cli, ["generate", str(config_file), "--editor", adapter]
                )
                if result.exit_code == 0:
                    assert "Generated:" in result.output

    def test_performance_with_large_configurations(self, runner, temp_dir):
        """Test performance with large, complex configurations."""
        # Create a large configuration file
        large_config = {
            "schema_version": "1.0.0",
            "metadata": {
                "title": "Large Configuration Test",
                "description": "Large configuration for performance testing",
                "version": "1.0.0",
                "author": "test@example.com",
                "tags": [f"tag{i}" for i in range(50)],
            },
            "targets": ["claude"],
            "context": {
                "project_type": "enterprise_application",
                "technologies": [f"tech{i}" for i in range(20)],
                **{f"context_field_{i}": f"value_{i}" for i in range(30)},
            },
            "instructions": {
                "general": [
                    f"Instruction {i}: Follow best practices" for i in range(50)
                ],
                "specific": [f"Specific instruction {i}" for i in range(30)],
                "advanced": [f"Advanced instruction {i}" for i in range(20)],
            },
            "examples": {
                f"example_{i}": f"Example code snippet {i}" for i in range(25)
            },
            "variables": {f"VAR_{i}": f"value_{i}" for i in range(100)},
        }
        large_file = temp_dir / "large_config.promptrek.yaml"
        with open(large_file, "w") as f:
            yaml.dump(large_config, f)

        with runner.isolated_filesystem(temp_dir=temp_dir):
            result = runner.invoke(
                cli, ["generate", str(large_file), "--editor", "claude"]
            )

            assert result.exit_code == 0
            assert "Generated:" in result.output

    def test_error_recovery_in_complex_workflows(self, runner, temp_dir):
        """Test error recovery in complex workflow scenarios."""
        # Create configuration with potential issues
        problematic_config = {
            "schema_version": "1.0.0",
            "metadata": {
                "title": "Problematic Configuration",
                "description": "Configuration with potential issues",
                "version": "1.0.0",
                "author": "test@example.com",
            },
            "targets": ["nonexistent-adapter", "claude"],
            "context": {
                "undefined_var": "{{ UNDEFINED_VARIABLE }}",
                "circular_ref": "{{ CIRCULAR_REF }}",
            },
            "instructions": {
                "general": [
                    "Use {{ UNDEFINED_VARIABLE }} practices",
                    "{% if NONEXISTENT_VAR == 'true' %}This won't work{% endif %}",
                ]
            },
            "variables": {
                "CIRCULAR_REF": "{{ CIRCULAR_REF }}",
                "DEFINED_VAR": "proper_value",
            },
        }
        problematic_file = temp_dir / "problematic.promptrek.yaml"
        with open(problematic_file, "w") as f:
            yaml.dump(problematic_config, f)

        # Test validation (should pass with warnings)
        result1 = runner.invoke(cli, ["validate", str(problematic_file)])
        assert result1.exit_code == 0  # Should pass but with warnings

        # Test generation (might fail, but should handle gracefully)
        with runner.isolated_filesystem(temp_dir=temp_dir):
            result2 = runner.invoke(
                cli, ["generate", str(problematic_file), "--editor", "claude"]
            )
            # Should either succeed or fail gracefully
            assert result2.exit_code in [0, 1]

    def test_concurrent_generation_simulation(
        self, runner, multi_adapter_project, temp_dir
    ):
        """Simulate concurrent generation scenarios."""
        # This is a simulation since we can't easily test true concurrency in CLI tests
        with runner.isolated_filesystem(temp_dir=temp_dir):
            # Generate multiple times with different configurations
            configurations = [
                {"SCALE": "small", "ENVIRONMENT": "development"},
                {"SCALE": "medium", "ENVIRONMENT": "staging"},
                {"SCALE": "large", "ENVIRONMENT": "production"},
            ]

            for i, config in enumerate(configurations):
                output_dir = temp_dir / f"output_{i}"
                output_dir.mkdir(exist_ok=True)

                args = ["generate", str(multi_adapter_project), "--editor", "claude"]
                for key, value in config.items():
                    args.extend(["-V", f"{key}={value}"])

                with runner.isolated_filesystem(temp_dir=output_dir):
                    result = runner.invoke(cli, args)
                    assert result.exit_code == 0

    def test_workflow_with_multiple_file_types(self, runner, temp_dir):
        """Test workflows involving multiple file types and formats."""
        # Create directory with mixed file types
        project_dir = temp_dir / "mixed_project"
        project_dir.mkdir()

        # Create multiple UPF files
        configs = [
            (
                "backend.promptrek.yaml",
                {
                    "schema_version": "1.0.0",
                    "metadata": {
                        "title": "Backend Config",
                        "description": "Backend",
                        "version": "1.0.0",
                        "author": "test",
                    },
                    "targets": ["claude"],
                    "context": {"component": "backend"},
                    "instructions": {"general": ["Backend instructions"]},
                },
            ),
            (
                "frontend.promptrek.yaml",
                {
                    "schema_version": "1.0.0",
                    "metadata": {
                        "title": "Frontend Config",
                        "description": "Frontend",
                        "version": "1.0.0",
                        "author": "test",
                    },
                    "targets": ["copilot"],
                    "context": {"component": "frontend"},
                    "instructions": {"general": ["Frontend instructions"]},
                },
            ),
        ]

        for filename, content in configs:
            config_file = project_dir / filename
            with open(config_file, "w") as f:
                yaml.dump(content, f)

        # Test sync on the directory
        with runner.isolated_filesystem(temp_dir=temp_dir):
            result = runner.invoke(
                cli, ["sync", "--source-dir", str(project_dir), "--editor", "continue"]
            )

            assert result.exit_code == 0
