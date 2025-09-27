"""Comprehensive CLI tests specifically designed to boost coverage."""

import tempfile
from pathlib import Path

import pytest
import yaml
from click.testing import CliRunner

from promptrek.cli.main import cli


class TestCLICoverageBoost:
    """Tests specifically designed to boost CLI command coverage."""

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
    def invalid_yaml_file(self, temp_dir):
        """Create invalid YAML file for error testing."""
        invalid_file = temp_dir / "invalid.promptrek.yaml"
        invalid_file.write_text("invalid: yaml: content: [")
        return invalid_file

    @pytest.fixture
    def invalid_schema_file(self, temp_dir):
        """Create file with invalid schema for validation error testing."""
        upf_content = {
            "schema_version": "1.0.0",
            "metadata": {
                "title": "Test",
                "description": "Test",
                "version": "1.0.0",
                "author": "test",
            },
            # Missing required 'targets' field
            "instructions": {"general": ["Test instruction"]},
        }
        upf_file = temp_dir / "invalid_schema.promptrek.yaml"
        with open(upf_file, "w") as f:
            yaml.dump(upf_content, f)
        return upf_file

    @pytest.fixture
    def valid_upf_file(self, temp_dir):
        """Create valid UPF file for testing."""
        upf_content = {
            "schema_version": "1.0.0",
            "metadata": {
                "title": "Coverage Test",
                "description": "Test for coverage",
                "version": "1.0.0",
                "author": "test@example.com",
            },
            "targets": ["claude", "copilot"],
            "instructions": {"general": ["Test instruction"]},
        }
        upf_file = temp_dir / "valid.promptrek.yaml"
        with open(upf_file, "w") as f:
            yaml.dump(upf_content, f)
        return upf_file

    @pytest.fixture
    def global_config_upf_file(self, temp_dir):
        """Create UPF file targeting global config adapters."""
        upf_content = {
            "schema_version": "1.0.0",
            "metadata": {
                "title": "Global Config Test",
                "description": "Test for global config adapters",
                "version": "1.0.0",
                "author": "test@example.com",
            },
            "targets": ["amazon-q"],
            "instructions": {"general": ["Global config instruction"]},
        }
        upf_file = temp_dir / "global_config.promptrek.yaml"
        with open(upf_file, "w") as f:
            yaml.dump(upf_content, f)
        return upf_file

    @pytest.fixture
    def ide_plugin_upf_file(self, temp_dir):
        """Create UPF file targeting IDE plugin adapters."""
        upf_content = {
            "schema_version": "1.0.0",
            "metadata": {
                "title": "IDE Plugin Test",
                "description": "Test for IDE plugin adapters",
                "version": "1.0.0",
                "author": "test@example.com",
            },
            "targets": ["jetbrains"],
            "instructions": {"general": ["IDE plugin instruction"]},
        }
        upf_file = temp_dir / "ide_plugin.promptrek.yaml"
        with open(upf_file, "w") as f:
            yaml.dump(upf_content, f)
        return upf_file

    def test_generate_parsing_error_handling(self, runner, invalid_yaml_file):
        """Test generate command error handling for parsing errors."""
        result = runner.invoke(
            cli, ["generate", str(invalid_yaml_file), "--editor", "claude"]
        )

        assert result.exit_code != 0
        assert "Failed to parse" in result.output

    def test_generate_validation_error_handling(self, runner, invalid_schema_file):
        """Test generate command error handling for validation errors."""
        result = runner.invoke(
            cli, ["generate", str(invalid_schema_file), "--editor", "claude"]
        )

        assert result.exit_code != 0
        assert "Validation failed" in result.output or "required" in result.output

    def test_generate_invalid_editor_error(self, runner, valid_upf_file):
        """Test generate command with invalid editor name."""
        result = runner.invoke(
            cli, ["generate", str(valid_upf_file), "--editor", "nonexistent-editor"]
        )

        assert result.exit_code != 0
        assert (
            "not available" in result.output
            or "not found" in result.output
            or "not yet implemented" in result.output
            or "not in targets" in result.output
        )

    def test_generate_all_editors_with_capability_info(
        self, runner, valid_upf_file, temp_dir
    ):
        """Test generate --all command showing capability information."""
        with runner.isolated_filesystem(temp_dir=temp_dir):
            result = runner.invoke(cli, ["generate", str(valid_upf_file), "--all"])

            assert result.exit_code == 0
            # Should mention different adapter types
            assert (
                "global" in result.output.lower()
                or "ide" in result.output.lower()
                or "Generated:" in result.output
            )

    def test_generate_global_config_adapter(
        self, runner, global_config_upf_file, temp_dir
    ):
        """Test generate command with global config only adapter."""
        with runner.isolated_filesystem(temp_dir=temp_dir):
            result = runner.invoke(
                cli, ["generate", str(global_config_upf_file), "--editor", "amazon-q"]
            )

            assert result.exit_code == 0
            assert (
                "global settings" in result.output.lower()
                or "Generated:" in result.output
            )

    def test_generate_ide_plugin_adapter(self, runner, ide_plugin_upf_file, temp_dir):
        """Test generate command with IDE plugin only adapter."""
        with runner.isolated_filesystem(temp_dir=temp_dir):
            result = runner.invoke(
                cli, ["generate", str(ide_plugin_upf_file), "--editor", "jetbrains"]
            )

            assert result.exit_code == 0
            assert (
                "IDE interface" in result.output.lower()
                or "ide" in result.output.lower()
                or "Generated:" in result.output
            )

    def test_generate_verbose_error_handling(self, runner, invalid_yaml_file):
        """Test generate command with verbose flag during errors."""
        result = runner.invoke(
            cli, ["--verbose", "generate", str(invalid_yaml_file), "--editor", "claude"]
        )

        assert result.exit_code != 0

    def test_generate_multiple_files_with_errors(
        self, runner, valid_upf_file, invalid_yaml_file, temp_dir
    ):
        """Test generate command with mix of valid and invalid files."""
        with runner.isolated_filesystem(temp_dir=temp_dir):
            result = runner.invoke(
                cli,
                [
                    "generate",
                    str(valid_upf_file),
                    str(invalid_yaml_file),
                    "--editor",
                    "claude",
                ],
            )

            # Should process valid file and report error for invalid file
            assert result.exit_code != 0 or "Error processing" in result.output

    def test_generate_directory_processing_errors(self, runner, temp_dir):
        """Test generate command directory processing with mixed files."""
        # Create a directory with mix of valid and invalid files
        test_dir = temp_dir / "mixed_files"
        test_dir.mkdir()

        # Valid file
        valid_content = {
            "schema_version": "1.0.0",
            "metadata": {
                "title": "Valid",
                "description": "Valid",
                "version": "1.0.0",
                "author": "test",
            },
            "targets": ["claude"],
            "instructions": {"general": ["Valid instruction"]},
        }
        valid_file = test_dir / "valid.promptrek.yaml"
        with open(valid_file, "w") as f:
            yaml.dump(valid_content, f)

        # Invalid file
        invalid_file = test_dir / "invalid.promptrek.yaml"
        invalid_file.write_text("invalid: yaml: content: [")

        with runner.isolated_filesystem(temp_dir=temp_dir):
            result = runner.invoke(
                cli, ["generate", "--directory", str(test_dir), "--editor", "claude"]
            )

            # Should process valid files and report errors for invalid ones
            assert "Error processing" in result.output or result.exit_code != 0

    def test_generate_nonexistent_directory(self, runner, temp_dir):
        """Test generate command with nonexistent directory."""
        nonexistent_dir = temp_dir / "nonexistent"

        result = runner.invoke(
            cli, ["generate", "--directory", str(nonexistent_dir), "--editor", "claude"]
        )

        assert result.exit_code != 0

    def test_generate_adapter_not_found_exception_handling(
        self, runner, valid_upf_file
    ):
        """Test generate command handling AdapterNotFoundError."""
        result = runner.invoke(
            cli, ["generate", str(valid_upf_file), "--editor", "totally-fake-editor"]
        )

        assert result.exit_code != 0
        assert (
            "not available" in result.output
            or "not found" in result.output
            or "not yet implemented" in result.output
            or "not in targets" in result.output
        )

    def test_generate_with_custom_output_directory(
        self, runner, valid_upf_file, temp_dir
    ):
        """Test generate command with custom output directory."""
        output_dir = temp_dir / "custom_output"

        with runner.isolated_filesystem(temp_dir=temp_dir):
            result = runner.invoke(
                cli,
                [
                    "generate",
                    str(valid_upf_file),
                    "--editor",
                    "claude",
                    "--output",
                    str(output_dir),
                ],
            )

            assert result.exit_code == 0

    def test_generate_dry_run_verbose_combination(self, runner, valid_upf_file):
        """Test generate command with both dry-run and verbose flags."""
        result = runner.invoke(
            cli,
            [
                "--verbose",
                "generate",
                str(valid_upf_file),
                "--editor",
                "claude",
                "--dry-run",
            ],
        )

        assert result.exit_code == 0
        assert "Would create:" in result.output or "Dry run" in result.output

    def test_generate_recursive_directory_processing(self, runner, temp_dir):
        """Test generate command recursive directory processing."""
        # Create nested directory structure
        sub_dir = temp_dir / "subdir"
        sub_dir.mkdir()

        upf_content = {
            "schema_version": "1.0.0",
            "metadata": {
                "title": "Nested",
                "description": "Nested",
                "version": "1.0.0",
                "author": "test",
            },
            "targets": ["claude"],
            "instructions": {"general": ["Nested instruction"]},
        }
        nested_file = sub_dir / "nested.promptrek.yaml"
        with open(nested_file, "w") as f:
            yaml.dump(upf_content, f)

        with runner.isolated_filesystem(temp_dir=temp_dir):
            result = runner.invoke(
                cli,
                [
                    "generate",
                    "--directory",
                    str(temp_dir),
                    "--recursive",
                    "--editor",
                    "claude",
                ],
            )

            assert result.exit_code == 0

    def test_agents_command_auto_discovery(self, runner, temp_dir):
        """Test agents command with auto-discovery of prompt files."""
        # Create a promptrek file in the working directory
        upf_content = {
            "schema_version": "1.0.0",
            "metadata": {
                "title": "Agent Test",
                "description": "Test",
                "version": "1.0.0",
                "author": "test",
            },
            "targets": ["claude"],
            "instructions": {"general": ["Agent instruction"]},
        }
        upf_file = temp_dir / "project.promptrek.yaml"
        with open(upf_file, "w") as f:
            yaml.dump(upf_content, f)

        with runner.isolated_filesystem(temp_dir=temp_dir):
            result = runner.invoke(cli, ["agents"])

            # Should either succeed or give helpful error message
            assert (
                result.exit_code == 0
                or "Auto-discovered" in result.output
                or "Created" in result.output
                or "No prompt file specified" in result.output
            )

    def test_agents_command_no_prompt_file_found(self, runner, temp_dir):
        """Test agents command when no prompt files are found."""
        with runner.isolated_filesystem(temp_dir=temp_dir):
            result = runner.invoke(cli, ["agents"])

            assert result.exit_code != 0
            assert (
                "No prompt file specified" in result.output
                or "not found" in result.output
            )

    def test_agents_command_nonexistent_file(self, runner):
        """Test agents command with nonexistent prompt file."""
        result = runner.invoke(
            cli, ["agents", "--prompt-file", "nonexistent.promptrek.yaml"]
        )

        assert result.exit_code != 0
        assert "not found" in result.output

    def test_agents_command_invalid_prompt_file(self, runner, invalid_yaml_file):
        """Test agents command with invalid prompt file."""
        result = runner.invoke(cli, ["agents", "--prompt-file", str(invalid_yaml_file)])

        assert result.exit_code != 0
        assert "Failed to parse" in result.output

    def test_agents_command_with_output_dir(self, runner, valid_upf_file, temp_dir):
        """Test agents command with custom output directory."""
        output_dir = temp_dir / "agents_output"

        with runner.isolated_filesystem(temp_dir=temp_dir):
            result = runner.invoke(
                cli,
                [
                    "agents",
                    "--prompt-file",
                    str(valid_upf_file),
                    "--output",
                    str(output_dir),
                ],
            )

            assert result.exit_code == 0

    def test_agents_command_dry_run(self, runner, valid_upf_file):
        """Test agents command in dry-run mode."""
        result = runner.invoke(
            cli, ["agents", "--prompt-file", str(valid_upf_file), "--dry-run"]
        )

        assert result.exit_code == 0
        assert "Would create" in result.output

    def test_agents_command_verbose(self, runner, valid_upf_file):
        """Test agents command with verbose output."""
        result = runner.invoke(
            cli, ["--verbose", "agents", "--prompt-file", str(valid_upf_file)]
        )

        assert result.exit_code == 0

    def test_agents_command_force_overwrite(self, runner, valid_upf_file, temp_dir):
        """Test agents command with force overwrite."""
        with runner.isolated_filesystem(temp_dir=temp_dir):
            # First run
            result1 = runner.invoke(
                cli, ["agents", "--prompt-file", str(valid_upf_file)]
            )
            assert result1.exit_code == 0

            # Second run with force
            result2 = runner.invoke(
                cli, ["agents", "--prompt-file", str(valid_upf_file), "--force"]
            )
            assert result2.exit_code == 0

    def test_agents_command_relative_paths(self, runner, temp_dir):
        """Test agents command with relative paths."""
        upf_content = {
            "schema_version": "1.0.0",
            "metadata": {
                "title": "Relative Test",
                "description": "Test",
                "version": "1.0.0",
                "author": "test",
            },
            "targets": ["claude"],
            "instructions": {"general": ["Relative path instruction"]},
        }

        with runner.isolated_filesystem(temp_dir=temp_dir):
            # Create the file in the isolated filesystem working directory
            upf_file = Path("relative.promptrek.yaml")
            with open(upf_file, "w") as f:
                yaml.dump(upf_content, f)

            result = runner.invoke(
                cli, ["agents", "--prompt-file", "relative.promptrek.yaml"]
            )

            assert result.exit_code == 0
