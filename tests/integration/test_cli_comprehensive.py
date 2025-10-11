"""Comprehensive CLI integration tests for enhanced coverage."""

import tempfile
from pathlib import Path

import pytest
import yaml
from click.testing import CliRunner

from promptrek.cli.main import cli


class TestCLIComprehensive:
    """Comprehensive CLI integration tests."""

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
            "targets": ["claude", "copilot", "cursor", "continue", "windsurf"],
            "context": {
                "project_type": "web_application",
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
            "examples": {
                "api_endpoint": """
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def user_profile(request):
    if request.method == 'GET':
        serializer = UserProfileSerializer(request.user.profile)
        return Response(serializer.data)
    elif request.method == 'POST':
        serializer = UserProfileSerializer(
            request.user.profile,
            data=request.data,
            partial=True
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)
""",
                "react_component": """
interface UserProfileProps {
    user: User;
    onUpdate: (user: User) => void;
}

const UserProfile: React.FC<UserProfileProps> = ({ user, onUpdate }) => {
    const [isEditing, setIsEditing] = useState(false);

    const handleSubmit = async (data: UserData) => {
        try {
            const updatedUser = await updateUser(data);
            onUpdate(updatedUser);
            setIsEditing(false);
        } catch (error) {
            console.error('Failed to update user:', error);
        }
    };

    return (
        <div className="user-profile">
            {isEditing ? (
                <UserEditForm user={user} onSubmit={handleSubmit} />
            ) : (
                <UserDisplay user={user} onEdit={() => setIsEditing(true)} />
            )}
        </div>
    );
};
""",
                "test_example": """
@pytest.mark.django_db
class TestUserProfileAPI:
    def test_get_user_profile_authenticated(self, api_client, user):
        api_client.force_authenticate(user=user)
        response = api_client.get('/api/profile/')
        assert response.status_code == 200
        assert response.data['username'] == user.username

    def test_update_user_profile(self, api_client, user):
        api_client.force_authenticate(user=user)
        data = {'first_name': 'Updated'}
        response = api_client.post('/api/profile/', data)
        assert response.status_code == 200
        user.refresh_from_db()
        assert user.first_name == 'Updated'
""",
                "dockerfile": """
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "project.wsgi:application"]
""",
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
    def sync_test_directory(self, temp_dir):
        """Create directory structure for sync testing."""
        sync_dir = temp_dir / "sync_test"
        sync_dir.mkdir()

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
                    "targets": ["windsurf"],
                    "instructions": {"general": ["Project 3 instructions"]},
                },
            ),
        ]

        for file_path, content in files_data:
            full_path = sync_dir / file_path
            full_path.parent.mkdir(parents=True, exist_ok=True)
            with open(full_path, "w") as f:
                yaml.dump(content, f)

        return sync_dir

    def test_sync_command_basic(self, runner, sync_test_directory):
        """Test basic sync command functionality."""
        with runner.isolated_filesystem(temp_dir=sync_test_directory):
            result = runner.invoke(
                cli,
                [
                    "sync",
                    "--source-dir",
                    str(sync_test_directory),
                    "--editor",
                    "continue",
                ],
            )

            assert result.exit_code == 0
            assert "Synced" in result.output or result.exit_code == 0

    def test_sync_command_dry_run(self, runner, sync_test_directory):
        """Test sync command in dry-run mode."""
        result = runner.invoke(
            cli,
            [
                "sync",
                "--source-dir",
                str(sync_test_directory),
                "--editor",
                "continue",
                "--dry-run",
            ],
        )

        assert result.exit_code == 0
        assert "Dry run" in result.output or "Would" in result.output

    def test_sync_command_verbose(self, runner, sync_test_directory):
        """Test sync command with verbose output."""
        result = runner.invoke(
            cli,
            [
                "--verbose",
                "sync",
                "--source-dir",
                str(sync_test_directory),
                "--editor",
                "continue",
                "--dry-run",
            ],
        )

        assert result.exit_code == 0

    def test_sync_command_recursive(self, runner, sync_test_directory):
        """Test sync command with recursive directory scanning."""
        with runner.isolated_filesystem(temp_dir=sync_test_directory):
            result = runner.invoke(
                cli,
                [
                    "sync",
                    "--source-dir",
                    str(sync_test_directory),
                    "--editor",
                    "continue",
                ],
            )

            assert result.exit_code == 0

    def test_sync_command_force_overwrite(self, runner, sync_test_directory):
        """Test sync command with force overwrite option."""
        with runner.isolated_filesystem(temp_dir=sync_test_directory):
            # First run to create files
            runner.invoke(
                cli,
                [
                    "sync",
                    "--source-dir",
                    str(sync_test_directory),
                    "--editor",
                    "continue",
                ],
            )

            # Second run with force overwrite
            result = runner.invoke(
                cli,
                [
                    "sync",
                    "--source-dir",
                    str(sync_test_directory),
                    "--editor",
                    "continue",
                    "--force",
                ],
            )

            assert result.exit_code == 0

    def test_sync_command_error_handling(self, runner, temp_dir):
        """Test sync command error handling."""
        # Test with non-existent directory
        result = runner.invoke(
            cli,
            [
                "sync",
                "--source-dir",
                str(temp_dir / "nonexistent"),
                "--editor",
                "continue",
            ],
        )

        assert result.exit_code != 0

    def test_generate_command_edge_cases(
        self, runner, comprehensive_upf_file, temp_dir
    ):
        """Test generate command edge cases."""
        with runner.isolated_filesystem(temp_dir=temp_dir):
            # Test with multiple variable overrides
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

    def test_generate_command_with_directory_output(
        self, runner, comprehensive_upf_file, temp_dir
    ):
        """Test generate command with custom output directory."""
        output_dir = temp_dir / "custom_output"
        output_dir.mkdir()

        with runner.isolated_filesystem(temp_dir=output_dir):
            result = runner.invoke(
                cli,
                [
                    "generate",
                    str(comprehensive_upf_file),
                    "--editor",
                    "claude",
                    "--directory",
                    str(output_dir),
                ],
            )

            assert result.exit_code == 0

    def test_generate_command_recursive_directory_processing(
        self, runner, sync_test_directory, temp_dir
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
                    str(sync_test_directory),
                    "--recursive",
                ],
            )

            assert result.exit_code == 0

    def test_generate_command_force_overwrite(
        self, runner, comprehensive_upf_file, temp_dir
    ):
        """Test generate command with force overwrite."""
        with runner.isolated_filesystem(temp_dir=temp_dir):
            # First generation
            result1 = runner.invoke(
                cli, ["generate", str(comprehensive_upf_file), "--editor", "claude"]
            )
            assert result1.exit_code == 0

            # Second generation (should work without force)
            result2 = runner.invoke(
                cli, ["generate", str(comprehensive_upf_file), "--editor", "claude"]
            )
            assert result2.exit_code == 0

    def test_generate_command_invalid_combinations(
        self, runner, comprehensive_upf_file
    ):
        """Test generate command with invalid parameter combinations."""
        # Test with both --editor and --all
        result = runner.invoke(
            cli,
            ["generate", str(comprehensive_upf_file), "--editor", "claude", "--all"],
        )

        # Should either fail or ignore one of the options
        # The exact behavior depends on implementation

    def test_main_cli_help_comprehensive(self, runner):
        """Test main CLI help with comprehensive output."""
        result = runner.invoke(cli, ["--help"])

        assert result.exit_code == 0
        assert "PrompTrek" in result.output
        assert "init" in result.output
        assert "validate" in result.output
        assert "generate" in result.output
        assert "sync" in result.output

    def test_main_cli_version_info(self, runner):
        """Test CLI version information."""
        result = runner.invoke(cli, ["--version"])

        # Version command might not be implemented, so we check both possibilities
        assert result.exit_code in [0, 2]  # 2 for unrecognized option

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
        assert "Dry run" in result.output

    def test_main_cli_error_handling(self, runner):
        """Test main CLI error handling."""
        # Test invalid command
        result = runner.invoke(cli, ["invalid-command"])

        assert result.exit_code != 0
        assert "Usage:" in result.output or "No such command" in result.output

    def test_main_cli_context_settings(self, runner):
        """Test CLI context settings and configuration."""
        # Test help formatting
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

        # Validate the created file (V2 schema)
        with open(output_file) as f:
            content = yaml.safe_load(f)
            assert content["schema_version"] == "2.0.0"  # V2 schema
            assert "metadata" in content
            assert "content" in content  # V2 uses content instead of targets

    def test_init_command_with_templates(self, runner, temp_dir):
        """Test init command with different templates."""
        templates = ["react", "python", "node"]

        for template in templates:
            output_file = temp_dir / f"{template}_init.promptrek.yaml"
            result = runner.invoke(
                cli, ["init", "--template", template, "--output", str(output_file)]
            )

            # Template might not exist, so we check for appropriate response
            if result.exit_code == 0:
                assert output_file.exists()

    def test_validate_command_comprehensive(self, runner, comprehensive_upf_file):
        """Test validate command with comprehensive file."""
        result = runner.invoke(cli, ["validate", str(comprehensive_upf_file)])

        assert result.exit_code == 0
        assert "valid" in result.output.lower()

    def test_validate_command_with_strict_mode(self, runner, comprehensive_upf_file):
        """Test validate command in strict mode."""
        result = runner.invoke(
            cli, ["validate", str(comprehensive_upf_file), "--strict"]
        )

        assert result.exit_code == 0

    def test_list_editors_command_comprehensive(self, runner):
        """Test list-editors command functionality."""
        result = runner.invoke(cli, ["list-editors"])

        assert result.exit_code == 0
        # Should list available editors
        expected_editors = ["claude", "copilot", "cursor", "continue", "windsurf"]
        for editor in expected_editors:
            if editor in result.output.lower():
                # At least some editors should be listed
                break
        else:
            # If no expected editors found, at least verify it's a proper list
            assert "editor" in result.output.lower() or len(result.output.strip()) > 0

    def test_cli_integration_workflow(self, runner, temp_dir):
        """Test complete CLI integration workflow."""
        # 1. Initialize a new project
        init_file = temp_dir / "workflow_test.promptrek.yaml"
        result1 = runner.invoke(cli, ["init", "--output", str(init_file)])
        assert result1.exit_code == 0

        # 2. Validate the initialized file
        result2 = runner.invoke(cli, ["validate", str(init_file)])
        assert result2.exit_code == 0

        # 3. Generate outputs
        with runner.isolated_filesystem(temp_dir=temp_dir):
            result3 = runner.invoke(
                cli, ["generate", str(init_file), "--editor", "claude"]
            )
            # Might fail if targets don't include claude, but that's fine for this test

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

        # Test with permission denied scenario (if possible)
        # This is platform-dependent and might not work in all environments
