"""Tests specifically designed to boost adapter coverage."""

import tempfile
from pathlib import Path

import pytest
import yaml
from click.testing import CliRunner

from promptrek.cli.main import cli


class TestAdapterCoverageBoost:
    """Tests designed to boost coverage in specific adapters."""

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
    def continue_upf_file(self, temp_dir):
        """Create UPF file for Continue adapter testing."""
        upf_content = {
            "schema_version": "1.0.0",
            "metadata": {
                "title": "Continue Test Project",
                "description": "Test project for Continue adapter coverage",
                "version": "1.0.0",
                "author": "test@example.com",
            },
            "targets": ["continue"],
            "context": {
                "project_type": "web_application",
                "technologies": ["python", "react"],
                "framework": "{{ FRAMEWORK }}",
                "database": "{{ DATABASE_TYPE }}",
            },
            "instructions": {
                "general": [
                    "Use {{ FRAMEWORK }} best practices",
                    "Follow Continue IDE conventions",
                    "{% if TESTING_ENABLED %}Include comprehensive tests{% endif %}",
                ],
                "backend": [
                    "Use {{ DATABASE_TYPE }} for data storage",
                    "Implement proper error handling",
                ],
                "frontend": [
                    "Use React with TypeScript",
                    "Implement responsive design",
                ],
            },
            "examples": {
                "api_endpoint": "def get_users(): return User.objects.all()",
                "component": "const UserList = () => { return <div>Users</div>; }",
            },
            "variables": {
                "FRAMEWORK": "Django",
                "DATABASE_TYPE": "PostgreSQL",
                "TESTING_ENABLED": "true",
                "API_VERSION": "v1",
            },
        }
        upf_file = temp_dir / "continue_test.promptrek.yaml"
        with open(upf_file, "w") as f:
            yaml.dump(upf_content, f, default_flow_style=False)
        return upf_file

    @pytest.fixture
    def cursor_upf_file(self, temp_dir):
        """Create UPF file for Cursor adapter testing."""
        upf_content = {
            "schema_version": "1.0.0",
            "metadata": {
                "title": "Cursor Test Project",
                "description": "Test project for Cursor adapter coverage",
                "version": "1.0.0",
                "author": "test@example.com",
            },
            "targets": ["cursor"],
            "context": {
                "project_type": "mobile_application",
                "technologies": ["typescript", "react-native"],
                "platform": "{{ TARGET_PLATFORM }}",
                "deployment": "{{ DEPLOYMENT_TYPE }}",
            },
            "instructions": {
                "general": [
                    "Use {{ TARGET_PLATFORM }} development practices",
                    "Follow Cursor IDE conventions",
                    "{% if OFFLINE_SUPPORT %}Implement offline capabilities{% endif %}",
                ],
                "mobile": [
                    "Use React Native best practices",
                    "Implement proper navigation",
                    "Handle platform-specific code",
                ],
                "testing": [
                    "Use Jest for unit testing",
                    "Implement E2E testing with Detox",
                ],
            },
            "examples": {
                "component": "const Screen = () => { return <View><Text>Hello</Text></View>; }",
                "navigation": "navigation.navigate('Home')",
            },
            "variables": {
                "TARGET_PLATFORM": "iOS",
                "DEPLOYMENT_TYPE": "App Store",
                "OFFLINE_SUPPORT": "true",
                "MIN_VERSION": "iOS 13",
            },
        }
        upf_file = temp_dir / "cursor_test.promptrek.yaml"
        with open(upf_file, "w") as f:
            yaml.dump(upf_content, f, default_flow_style=False)
        return upf_file

    @pytest.fixture
    def kiro_upf_file(self, temp_dir):
        """Create UPF file for Kiro adapter testing."""
        upf_content = {
            "schema_version": "1.0.0",
            "metadata": {
                "title": "Kiro Test Project",
                "description": "Test project for Kiro adapter coverage",
                "version": "1.0.0",
                "author": "test@example.com",
            },
            "targets": ["kiro"],
            "context": {
                "project_type": "data_science",
                "technologies": ["python", "jupyter"],
                "domain": "{{ DOMAIN }}",
                "data_source": "{{ DATA_SOURCE }}",
            },
            "instructions": {
                "general": [
                    "Use {{ DOMAIN }} domain expertise",
                    "Follow Kiro AI conventions",
                    "{% if VISUALIZATION_ENABLED %}Create interactive visualizations{% endif %}",
                ],
                "data_processing": [
                    "Use pandas for data manipulation",
                    "Implement proper data validation",
                    "Handle missing data appropriately",
                ],
                "machine_learning": [
                    "Use scikit-learn for modeling",
                    "Implement cross-validation",
                    "Document model performance",
                ],
            },
            "examples": {
                "data_processing": "df = pd.read_csv('data.csv')",
                "model": "model = RandomForestClassifier()",
            },
            "variables": {
                "DOMAIN": "healthcare",
                "DATA_SOURCE": "clinical_trials",
                "VISUALIZATION_ENABLED": "true",
                "MODEL_TYPE": "classification",
            },
        }
        upf_file = temp_dir / "kiro_test.promptrek.yaml"
        with open(upf_file, "w") as f:
            yaml.dump(upf_content, f, default_flow_style=False)
        return upf_file

    def test_continue_adapter_comprehensive(self, runner, continue_upf_file, temp_dir):
        """Test Continue adapter with comprehensive scenarios."""
        with runner.isolated_filesystem(temp_dir=temp_dir):
            # Basic generation
            result = runner.invoke(
                cli, ["generate", str(continue_upf_file), "--editor", "continue"]
            )
            assert result.exit_code == 0

            # With variable overrides
            result = runner.invoke(
                cli,
                [
                    "generate",
                    str(continue_upf_file),
                    "--editor",
                    "continue",
                    "-V",
                    "FRAMEWORK=FastAPI",
                    "-V",
                    "DATABASE_TYPE=MongoDB",
                ],
            )
            assert result.exit_code == 0

            # Dry run with verbose
            result = runner.invoke(
                cli,
                [
                    "--verbose",
                    "generate",
                    str(continue_upf_file),
                    "--editor",
                    "continue",
                    "--dry-run",
                ],
            )
            assert result.exit_code == 0

    def test_cursor_adapter_comprehensive(self, runner, cursor_upf_file, temp_dir):
        """Test Cursor adapter with comprehensive scenarios."""
        with runner.isolated_filesystem(temp_dir=temp_dir):
            # Basic generation
            result = runner.invoke(
                cli, ["generate", str(cursor_upf_file), "--editor", "cursor"]
            )
            assert result.exit_code == 0

            # With variable overrides
            result = runner.invoke(
                cli,
                [
                    "generate",
                    str(cursor_upf_file),
                    "--editor",
                    "cursor",
                    "-V",
                    "TARGET_PLATFORM=Android",
                    "-V",
                    "DEPLOYMENT_TYPE=Google Play",
                ],
            )
            assert result.exit_code == 0

            # Dry run with verbose
            result = runner.invoke(
                cli,
                [
                    "--verbose",
                    "generate",
                    str(cursor_upf_file),
                    "--editor",
                    "cursor",
                    "--dry-run",
                ],
            )
            assert result.exit_code == 0

    def test_kiro_adapter_comprehensive(self, runner, kiro_upf_file, temp_dir):
        """Test Kiro adapter with comprehensive scenarios."""
        with runner.isolated_filesystem(temp_dir=temp_dir):
            # Basic generation
            result = runner.invoke(
                cli, ["generate", str(kiro_upf_file), "--editor", "kiro"]
            )
            assert result.exit_code == 0

            # With variable overrides
            result = runner.invoke(
                cli,
                [
                    "generate",
                    str(kiro_upf_file),
                    "--editor",
                    "kiro",
                    "-V",
                    "DOMAIN=finance",
                    "-V",
                    "MODEL_TYPE=regression",
                ],
            )
            assert result.exit_code == 0

            # Dry run with verbose
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

    def test_adapter_validation_scenarios(
        self, runner, continue_upf_file, cursor_upf_file, kiro_upf_file
    ):
        """Test adapter validation with different file types."""
        # Test Continue file validation
        result = runner.invoke(cli, ["validate", str(continue_upf_file)])
        assert result.exit_code == 0

        # Test Cursor file validation
        result = runner.invoke(cli, ["validate", str(cursor_upf_file)])
        assert result.exit_code == 0

        # Test Kiro file validation
        result = runner.invoke(cli, ["validate", str(kiro_upf_file)])
        assert result.exit_code == 0

    def test_adapter_error_handling(self, runner, temp_dir):
        """Test adapter error handling scenarios."""
        # Create file with unsupported adapter
        upf_content = {
            "schema_version": "1.0.0",
            "metadata": {
                "title": "Test",
                "description": "Test",
                "version": "1.0.0",
                "author": "test",
            },
            "targets": ["unsupported-adapter"],
            "instructions": {"general": ["Test"]},
        }
        upf_file = temp_dir / "unsupported.promptrek.yaml"
        with open(upf_file, "w") as f:
            yaml.dump(upf_content, f)

        result = runner.invoke(
            cli, ["generate", str(upf_file), "--editor", "unsupported-adapter"]
        )
        assert result.exit_code == 0  # CLI skips unsupported adapters with warning
        assert "not yet implemented" in result.output

    def test_adapter_with_custom_output_directories(
        self, runner, continue_upf_file, cursor_upf_file, temp_dir
    ):
        """Test adapters with custom output directories."""
        with runner.isolated_filesystem(temp_dir=temp_dir):
            output_dir = temp_dir / "custom_output"

            # Test Continue with custom output
            result = runner.invoke(
                cli,
                [
                    "generate",
                    str(continue_upf_file),
                    "--editor",
                    "continue",
                    "--output",
                    str(output_dir),
                ],
            )
            assert result.exit_code == 0

            # Test Cursor with custom output
            result = runner.invoke(
                cli,
                [
                    "generate",
                    str(cursor_upf_file),
                    "--editor",
                    "cursor",
                    "--output",
                    str(output_dir),
                ],
            )
            assert result.exit_code == 0

    def test_adapter_complex_variable_scenarios(self, runner, temp_dir):
        """Test adapters with complex variable scenarios."""
        upf_content = {
            "schema_version": "1.0.0",
            "metadata": {
                "title": "Complex Variables",
                "description": "Testing complex variable substitution",
                "version": "1.0.0",
                "author": "test",
            },
            "targets": ["continue", "cursor", "kiro"],
            "context": {
                "env_specific": "{% if ENVIRONMENT == 'prod' %}production{% else %}development{% endif %}",
                "nested_vars": "{{ OUTER }}/{{ INNER }}/{{ DEEP }}",
                "conditional_list": [
                    "{% if FEATURE_A %}Feature A enabled{% endif %}",
                    "{% if FEATURE_B %}Feature B enabled{% endif %}",
                ],
            },
            "instructions": {
                "general": [
                    "Environment: {{ env_specific }}",
                    "Path: {{ nested_vars }}",
                    "{% for feature in conditional_list %}{{ feature }}{% endfor %}",
                ]
            },
            "variables": {
                "ENVIRONMENT": "prod",
                "OUTER": "src",
                "INNER": "components",
                "DEEP": "ui",
                "FEATURE_A": "enabled",
                "FEATURE_B": "disabled",
            },
        }
        upf_file = temp_dir / "complex_vars.promptrek.yaml"
        with open(upf_file, "w") as f:
            yaml.dump(upf_content, f, default_flow_style=False)

        with runner.isolated_filesystem(temp_dir=temp_dir):
            for adapter in ["continue", "cursor", "kiro"]:
                result = runner.invoke(
                    cli, ["generate", str(upf_file), "--editor", adapter]
                )
                assert result.exit_code == 0

    def test_adapter_conditional_processing(self, runner, temp_dir):
        """Test adapters with complex conditional processing."""
        upf_content = {
            "schema_version": "1.0.0",
            "metadata": {
                "title": "Conditional Processing Test",
                "description": "Testing conditional logic in adapters",
                "version": "1.0.0",
                "author": "test",
            },
            "targets": ["continue", "cursor"],
            "instructions": {
                "conditional": [
                    "{% if PLATFORM == 'web' %}Use web-specific patterns{% elif PLATFORM == 'mobile' %}Use mobile patterns{% else %}Use generic patterns{% endif %}",
                    "{% if DEBUG and TESTING %}Enable debug and test mode{% endif %}",
                    "{% if not PRODUCTION %}Add development tools{% endif %}",
                ]
            },
            "variables": {
                "PLATFORM": "web",
                "DEBUG": "true",
                "TESTING": "true",
                "PRODUCTION": "false",
            },
        }
        upf_file = temp_dir / "conditionals.promptrek.yaml"
        with open(upf_file, "w") as f:
            yaml.dump(upf_content, f, default_flow_style=False)

        with runner.isolated_filesystem(temp_dir=temp_dir):
            for adapter in ["continue", "cursor"]:
                result = runner.invoke(
                    cli, ["generate", str(upf_file), "--editor", adapter]
                )
                assert result.exit_code == 0
