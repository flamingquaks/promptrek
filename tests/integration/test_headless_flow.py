"""Integration tests for headless bootstrap flow."""

from pathlib import Path

import pytest
from click.testing import CliRunner

from promptrek.cli.main import cli


class TestHeadlessBootstrapGeneration:
    """Test headless bootstrap file generation via CLI."""

    @pytest.fixture
    def v3_prompt_file(self, tmp_path):
        """Create a v3 prompt file with headless config."""
        upf_file = tmp_path / "project.promptrek.yaml"
        upf_file.write_text(
            """
schema_version: "3.0.0"
metadata:
  title: "Headless Test Project"
  description: "Test project for headless bootstrap"
  version: "1.0.0"
  author: "Test Author"
  tags: ["test", "headless"]
content: |
  # Headless Test Project

  ## Guidelines
  - Write clean code
  - Test everything
  - Follow conventions

headless:
  enabled: true
  custom_message: "Run npm test after generation to verify everything works"
  auto_execute: true
variables:
  PROJECT_NAME: "HeadlessTest"
"""
        )
        return upf_file

    @pytest.fixture
    def v3_prompt_no_headless(self, tmp_path):
        """Create a v3 prompt file without headless config."""
        upf_file = tmp_path / "project.promptrek.yaml"
        upf_file.write_text(
            """
schema_version: "3.0.0"
metadata:
  title: "Regular Test Project"
  description: "Test project without headless"
  version: "1.0.0"
  author: "Test Author"
content: |
  # Regular Project

  Write good code.
"""
        )
        return upf_file

    def test_generate_with_headless_flag_claude(self, v3_prompt_no_headless, tmp_path):
        """Test generating Claude with --headless flag."""
        runner = CliRunner()
        result = runner.invoke(
            cli,
            [
                "generate",
                str(v3_prompt_no_headless),
                "--editor",
                "claude",
                "--headless",
                "-o",
                str(tmp_path),
            ],
        )

        assert result.exit_code == 0

        # Check bootstrap file was created
        bootstrap_file = tmp_path / ".claude" / "_bootstrap.md"
        assert bootstrap_file.exists()

        # Verify bootstrap content
        content = bootstrap_file.read_text()
        assert "PrompTrek" in content
        assert "Claude Code" in content
        assert "promptrek generate" in content

    def test_generate_with_headless_schema_claude(self, v3_prompt_file, tmp_path):
        """Test generating Claude with headless in schema."""
        runner = CliRunner()
        result = runner.invoke(
            cli,
            [
                "generate",
                str(v3_prompt_file),
                "--editor",
                "claude",
                "-o",
                str(tmp_path),
            ],
        )

        assert result.exit_code == 0

        # Check bootstrap file was created (due to schema config)
        bootstrap_file = tmp_path / ".claude" / "_bootstrap.md"
        assert bootstrap_file.exists()

        # Verify custom message is included
        content = bootstrap_file.read_text()
        assert "npm test" in content

    def test_generate_without_headless_no_bootstrap(
        self, v3_prompt_no_headless, tmp_path
    ):
        """Test generating without headless does not create bootstrap."""
        runner = CliRunner()
        result = runner.invoke(
            cli,
            [
                "generate",
                str(v3_prompt_no_headless),
                "--editor",
                "claude",
                "-o",
                str(tmp_path),
            ],
        )

        assert result.exit_code == 0

        # Check bootstrap file was NOT created
        bootstrap_file = tmp_path / ".claude" / "_bootstrap.md"
        assert not bootstrap_file.exists()

    def test_headless_with_all_editors(self, v3_prompt_file, tmp_path):
        """Test headless generation for all editors."""
        editors_and_paths = [
            ("claude", ".claude/_bootstrap.md"),
            ("copilot", ".github/_bootstrap.md"),
            ("cursor", ".cursor/rules/_bootstrap.md"),
            ("continue", ".continue/rules/_bootstrap.md"),
            ("windsurf", ".windsurf/rules/_bootstrap.md"),
            ("kiro", ".kiro/steering/_bootstrap.md"),
            ("cline", ".clinerules/_bootstrap.md"),
            ("amazon-q", ".amazonq/rules/_bootstrap.md"),
            ("jetbrains", ".assistant/rules/_bootstrap.md"),
        ]

        runner = CliRunner()

        for editor, bootstrap_path in editors_and_paths:
            result = runner.invoke(
                cli,
                [
                    "generate",
                    str(v3_prompt_file),
                    "--editor",
                    editor,
                    "-o",
                    str(tmp_path),
                ],
            )

            assert result.exit_code == 0, f"Failed for {editor}"

            # Check bootstrap file exists
            bootstrap_file = tmp_path / bootstrap_path
            assert bootstrap_file.exists(), f"Bootstrap missing for {editor}"


class TestHeadlessBootstrapContent:
    """Test bootstrap file content and formatting."""

    @pytest.fixture
    def v3_prompt_with_custom(self, tmp_path):
        """Create prompt with custom bootstrap message."""
        upf_file = tmp_path / "project.promptrek.yaml"
        upf_file.write_text(
            """
schema_version: "3.0.0"
metadata:
  title: "Custom Bootstrap Test"
  description: "Test custom message"
  version: "1.0.0"
content: "# Test\\n\\nWrite code."
headless:
  enabled: true
  custom_message: "Important: Set ENV_VAR before starting!"
  auto_execute: true
"""
        )
        return upf_file

    def test_bootstrap_contains_yaml_frontmatter(self, v3_prompt_with_custom, tmp_path):
        """Test bootstrap file has valid YAML frontmatter."""
        runner = CliRunner()
        runner.invoke(
            cli,
            [
                "generate",
                str(v3_prompt_with_custom),
                "--editor",
                "claude",
                "-o",
                str(tmp_path),
            ],
        )

        bootstrap_file = tmp_path / ".claude" / "_bootstrap.md"
        content = bootstrap_file.read_text()

        # Check YAML frontmatter structure
        assert content.startswith("---")
        # Check for closing --- (allows for longer frontmatter)
        assert content.count("---") >= 2  # Opening and closing

    def test_bootstrap_includes_custom_message(self, v3_prompt_with_custom, tmp_path):
        """Test custom message appears in bootstrap."""
        runner = CliRunner()
        runner.invoke(
            cli,
            [
                "generate",
                str(v3_prompt_with_custom),
                "--editor",
                "claude",
                "-o",
                str(tmp_path),
            ],
        )

        bootstrap_file = tmp_path / ".claude" / "_bootstrap.md"
        content = bootstrap_file.read_text()

        assert "ENV_VAR" in content

    def test_bootstrap_dry_run(self, v3_prompt_with_custom, tmp_path):
        """Test dry run does not create bootstrap file."""
        runner = CliRunner()
        result = runner.invoke(
            cli,
            [
                "generate",
                str(v3_prompt_with_custom),
                "--editor",
                "claude",
                "--headless",
                "--dry-run",
                "-o",
                str(tmp_path),
            ],
        )

        assert result.exit_code == 0
        assert "Would create" in result.output

        # Bootstrap file should NOT be created in dry-run
        bootstrap_file = tmp_path / ".claude" / "_bootstrap.md"
        assert not bootstrap_file.exists()
