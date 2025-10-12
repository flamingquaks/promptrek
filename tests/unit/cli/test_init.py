"""Tests for init command."""

from pathlib import Path
from unittest.mock import Mock, patch

import pytest
import yaml
from click.testing import CliRunner

from promptrek.cli.commands.init import init_command
from promptrek.cli.main import cli
from promptrek.core.exceptions import CLIError


class TestInitCommand:
    """Test init_command function."""

    def test_init_basic(self, tmp_path):
        """Test basic initialization."""
        output_file = tmp_path / "test.promptrek.yaml"

        ctx = Mock()
        ctx.obj = {"verbose": False}

        with patch("click.echo"):
            init_command(ctx, template=None, output=str(output_file), setup_hooks=False)

        # File should be created
        assert output_file.exists()

        # Check content (V2 schema)
        with open(output_file) as f:
            data = yaml.safe_load(f)

        assert data["schema_version"] == "2.0.0"  # V2 schema
        assert "metadata" in data
        assert "content" in data  # V2 uses content instead of instructions

    def test_init_with_template(self, tmp_path):
        """Test initialization with template."""
        output_file = tmp_path / "test.promptrek.yaml"

        ctx = Mock()
        ctx.obj = {"verbose": False}

        with patch("click.echo"):
            init_command(
                ctx, template="react", output=str(output_file), setup_hooks=False
            )

        # File should be created
        assert output_file.exists()

        # Check React-specific content (V2 schema uses content field)
        with open(output_file) as f:
            data = yaml.safe_load(f)

        assert data["schema_version"] == "2.0.0"
        assert "content" in data
        # V2 schema includes technology info in the content string
        assert (
            "typescript" in data["content"].lower()
            or "react" in data["content"].lower()
        )

    def test_init_with_setup_hooks_success(self, tmp_path, monkeypatch):
        """Test initialization with hooks setup."""
        monkeypatch.chdir(tmp_path)
        output_file = tmp_path / "test.promptrek.yaml"

        ctx = Mock()
        ctx.obj = {"verbose": False}

        # Mock successful hook installation
        mock_install = Mock()

        with (
            patch("click.echo"),
            patch.dict(
                "sys.modules",
                {
                    "promptrek.cli.commands.hooks": Mock(
                        install_hooks_command=mock_install
                    )
                },
            ),
        ):
            init_command(ctx, template=None, output=str(output_file), setup_hooks=True)

            # Should have called install_hooks_command
            mock_install.assert_called_once()
            call_args = mock_install.call_args
            assert call_args[1]["activate"] is True
            assert call_args[1]["force"] is False

        # File should be created
        assert output_file.exists()

    def test_init_with_setup_hooks_failure(self, tmp_path, monkeypatch):
        """Test initialization handles hook setup failure gracefully."""
        monkeypatch.chdir(tmp_path)
        output_file = tmp_path / "test.promptrek.yaml"

        ctx = Mock()
        ctx.obj = {"verbose": False}

        # Mock hook installation failure
        mock_install = Mock(side_effect=Exception("Hook setup failed"))

        with (
            patch("click.echo"),
            patch.dict(
                "sys.modules",
                {
                    "promptrek.cli.commands.hooks": Mock(
                        install_hooks_command=mock_install
                    )
                },
            ),
        ):
            # Should not raise, just show warning
            init_command(ctx, template=None, output=str(output_file), setup_hooks=True)

        # File should still be created
        assert output_file.exists()

    def test_init_file_exists_confirm_no(self, tmp_path):
        """Test initialization with existing file, user declines."""
        output_file = tmp_path / "test.promptrek.yaml"
        output_file.write_text("existing content")

        ctx = Mock()
        ctx.obj = {"verbose": False}

        with patch("click.confirm", return_value=False):
            with pytest.raises(CLIError, match="cancelled"):
                init_command(
                    ctx, template=None, output=str(output_file), setup_hooks=False
                )

        # File should not be modified
        assert output_file.read_text() == "existing content"

    def test_init_file_exists_confirm_yes(self, tmp_path):
        """Test initialization with existing file, user confirms."""
        output_file = tmp_path / "test.promptrek.yaml"
        output_file.write_text("existing content")

        ctx = Mock()
        ctx.obj = {"verbose": False}

        with patch("click.echo"), patch("click.confirm", return_value=True):
            init_command(ctx, template=None, output=str(output_file), setup_hooks=False)

        # File should be overwritten (V2 schema)
        with open(output_file) as f:
            data = yaml.safe_load(f)
        assert data["schema_version"] == "2.0.0"  # V2 schema

    def test_init_invalid_template(self, tmp_path):
        """Test initialization with invalid template."""
        output_file = tmp_path / "test.promptrek.yaml"

        ctx = Mock()
        ctx.obj = {"verbose": False}

        with pytest.raises(CLIError, match="Unknown template"):
            init_command(
                ctx, template="invalid", output=str(output_file), setup_hooks=False
            )

    def test_init_creates_parent_directory(self, tmp_path):
        """Test initialization creates parent directories."""
        output_file = tmp_path / "subdir" / "nested" / "test.promptrek.yaml"

        ctx = Mock()
        ctx.obj = {"verbose": False}

        with patch("click.echo"):
            init_command(ctx, template=None, output=str(output_file), setup_hooks=False)

        # File and parent directories should be created
        assert output_file.exists()
        assert output_file.parent.exists()

    def test_init_v1_basic(self, tmp_path):
        """Test v1 initialization."""
        output_file = tmp_path / "test.promptrek.yaml"

        ctx = Mock()
        ctx.obj = {"verbose": False}

        with patch("click.echo"):
            init_command(ctx, template=None, output=str(output_file), setup_hooks=False, use_v2=False)

        # File should be created
        assert output_file.exists()

        # Check content (V1 schema)
        with open(output_file) as f:
            data = yaml.safe_load(f)

        assert data["schema_version"] == "1.0.0"
        assert "targets" in data
        assert "instructions" in data

    def test_init_api_template(self, tmp_path):
        """Test API template initialization."""
        output_file = tmp_path / "test.promptrek.yaml"

        ctx = Mock()
        ctx.obj = {"verbose": False}

        with patch("click.echo"):
            init_command(ctx, template="api", output=str(output_file), setup_hooks=False)

        assert output_file.exists()

        with open(output_file) as f:
            data = yaml.safe_load(f)

        assert "fastapi" in data["content"].lower() or "api" in data["content"].lower()

    def test_init_react_template_v1(self, tmp_path):
        """Test React template v1 initialization."""
        output_file = tmp_path / "test.promptrek.yaml"

        ctx = Mock()
        ctx.obj = {"verbose": False}

        with patch("click.echo"):
            init_command(ctx, template="react", output=str(output_file), setup_hooks=False, use_v2=False)

        assert output_file.exists()

        with open(output_file) as f:
            data = yaml.safe_load(f)

        assert data["schema_version"] == "1.0.0"
        assert "typescript" in str(data).lower()

    def test_init_api_template_v1(self, tmp_path):
        """Test API template v1 initialization."""
        output_file = tmp_path / "test.promptrek.yaml"

        ctx = Mock()
        ctx.obj = {"verbose": False}

        with patch("click.echo"):
            init_command(ctx, template="api", output=str(output_file), setup_hooks=False, use_v2=False)

        assert output_file.exists()

        with open(output_file) as f:
            data = yaml.safe_load(f)

        assert data["schema_version"] == "1.0.0"
        assert "fastapi" in str(data).lower()

    def test_init_adds_to_existing_gitignore(self, tmp_path):
        """Test initialization adds to existing gitignore."""
        output_file = tmp_path / "test.promptrek.yaml"

        # Create existing gitignore
        gitignore = tmp_path / ".gitignore"
        gitignore.write_text("*.pyc\n__pycache__/\n")

        ctx = Mock()
        ctx.obj = {"verbose": False}

        with patch("click.echo"):
            init_command(ctx, template=None, output=str(output_file), setup_hooks=False)

        assert output_file.exists()
        assert gitignore.exists()

        content = gitignore.read_text()
        assert "variables.promptrek.yaml" in content
        assert "*.pyc" in content  # Original content preserved

    def test_init_creates_new_gitignore(self, tmp_path):
        """Test initialization creates new gitignore."""
        output_file = tmp_path / "test.promptrek.yaml"

        ctx = Mock()
        ctx.obj = {"verbose": False}

        with patch("click.echo"):
            init_command(ctx, template=None, output=str(output_file), setup_hooks=False)

        assert output_file.exists()

        gitignore = tmp_path / ".gitignore"
        assert gitignore.exists()

        content = gitignore.read_text()
        assert "variables.promptrek.yaml" in content


class TestInitIntegration:
    """Integration tests for init command via CLI."""

    def test_init_cli_basic(self, tmp_path, monkeypatch):
        """Test init command via CLI."""
        monkeypatch.chdir(tmp_path)

        runner = CliRunner()
        result = runner.invoke(cli, ["init", "--output", "test.promptrek.yaml"])

        assert result.exit_code == 0
        assert Path("test.promptrek.yaml").exists()

    def test_init_cli_with_template(self, tmp_path, monkeypatch):
        """Test init command with template via CLI."""
        monkeypatch.chdir(tmp_path)

        runner = CliRunner()
        result = runner.invoke(
            cli, ["init", "--template", "api", "--output", "api.promptrek.yaml"]
        )

        assert result.exit_code == 0
        assert Path("api.promptrek.yaml").exists()

    def test_init_cli_with_setup_hooks(self, tmp_path, monkeypatch):
        """Test init command with --setup-hooks flag."""
        monkeypatch.chdir(tmp_path)

        # Initialize git repo (required for pre-commit)
        import subprocess

        subprocess.run(["git", "init"], capture_output=True, check=True)

        runner = CliRunner()

        # Mock successful pre-commit install
        with (
            patch("shutil.which", return_value="/usr/bin/pre-commit"),
            patch("subprocess.run", return_value=Mock(stdout="", stderr="")),
        ):
            result = runner.invoke(
                cli, ["init", "--output", "test.promptrek.yaml", "--setup-hooks"]
            )

        assert result.exit_code == 0
        assert Path("test.promptrek.yaml").exists()
        assert Path(".pre-commit-config.yaml").exists()
        assert "Setting up pre-commit hooks" in result.output

    def test_init_cli_setup_hooks_no_git(self, tmp_path, monkeypatch):
        """Test init with --setup-hooks in non-git directory."""
        monkeypatch.chdir(tmp_path)

        runner = CliRunner()

        # Without git init, pre-commit install will fail
        # But init should still create the .promptrek.yaml file
        result = runner.invoke(
            cli, ["init", "--output", "test.promptrek.yaml", "--setup-hooks"]
        )

        # Should succeed in creating the file
        assert Path("test.promptrek.yaml").exists()
        # Hooks config should be created
        assert Path(".pre-commit-config.yaml").exists()

    def test_init_cli_default_output(self, tmp_path, monkeypatch):
        """Test init with default output filename."""
        monkeypatch.chdir(tmp_path)

        runner = CliRunner()
        result = runner.invoke(cli, ["init"])

        assert result.exit_code == 0
        assert Path("project.promptrek.yaml").exists()

    def test_init_cli_help(self):
        """Test init command help."""
        runner = CliRunner()
        result = runner.invoke(cli, ["init", "--help"])

        assert result.exit_code == 0
        assert "Initialize a new universal prompt file" in result.output
        assert "--setup-hooks" in result.output
