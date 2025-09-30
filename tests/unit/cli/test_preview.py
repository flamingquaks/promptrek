"""Tests for preview command."""

from pathlib import Path
from unittest.mock import Mock, patch

import pytest
from click.testing import CliRunner

from promptrek.cli.commands.preview import preview_command
from promptrek.cli.main import cli
from promptrek.core.exceptions import CLIError
from promptrek.core.models import Instructions, PromptMetadata, UniversalPrompt


class TestPreviewCommand:
    """Test preview_command function."""

    @patch("promptrek.cli.commands.preview.registry")
    @patch("promptrek.cli.commands.preview.UPFValidator")
    @patch("promptrek.cli.commands.preview.UPFParser")
    def test_preview_basic(
        self, mock_parser_class, mock_validator_class, mock_registry, sample_upf_file
    ):
        """Test basic preview functionality."""
        # Setup mocks
        mock_parser = Mock()
        mock_parser.parse_file.return_value = UniversalPrompt(
            schema_version="1.0.0",
            metadata=PromptMetadata(title="Test", description="Test"),
            targets=["copilot"],
            instructions=Instructions(general=["test"]),
        )
        mock_parser_class.return_value = mock_parser

        mock_validator = Mock()
        mock_result = Mock()
        mock_result.errors = []
        mock_validator.validate.return_value = mock_result
        mock_validator_class.return_value = mock_validator

        mock_adapter = Mock()
        mock_adapter.generate.return_value = [Path(".github/copilot-instructions.md")]
        mock_registry.get.return_value = mock_adapter

        ctx = Mock()
        ctx.obj = {"verbose": False}

        # Run preview
        with patch("click.echo") as mock_echo:
            preview_command(ctx, sample_upf_file, "copilot", None)

            # Should call adapter with dry_run=True
            assert mock_adapter.generate.called
            call_kwargs = mock_adapter.generate.call_args[1]
            assert call_kwargs["dry_run"] is True

            # Should echo preview output
            assert mock_echo.called

    @patch("promptrek.cli.commands.preview.UPFParser")
    def test_preview_parse_error(self, mock_parser_class, tmp_path):
        """Test preview with parse error."""
        bad_file = tmp_path / "bad.yaml"
        bad_file.write_text("invalid: yaml:")

        mock_parser = Mock()
        mock_parser.parse_file.side_effect = Exception("Parse error")
        mock_parser_class.return_value = mock_parser

        ctx = Mock()
        ctx.obj = {"verbose": False}

        with pytest.raises(CLIError, match="Failed to parse"):
            preview_command(ctx, bad_file, "copilot", None)

    @patch("promptrek.cli.commands.preview.UPFValidator")
    @patch("promptrek.cli.commands.preview.UPFParser")
    def test_preview_validation_error(
        self, mock_parser_class, mock_validator_class, sample_upf_file
    ):
        """Test preview with validation error."""
        mock_parser = Mock()
        mock_parser.parse_file.return_value = UniversalPrompt(
            schema_version="1.0.0",
            metadata=PromptMetadata(title="Test", description="Test"),
            targets=["copilot"],
            instructions=Instructions(general=["test"]),
        )
        mock_parser_class.return_value = mock_parser

        mock_validator = Mock()
        mock_result = Mock()
        mock_result.errors = ["Validation error"]
        mock_validator.validate.return_value = mock_result
        mock_validator_class.return_value = mock_validator

        ctx = Mock()
        ctx.obj = {"verbose": False}

        with pytest.raises(CLIError, match="Validation failed"):
            preview_command(ctx, sample_upf_file, "copilot", None)

    @patch("promptrek.cli.commands.preview.registry")
    @patch("promptrek.cli.commands.preview.UPFValidator")
    @patch("promptrek.cli.commands.preview.UPFParser")
    @patch("click.echo")
    def test_preview_editor_not_in_targets_warning(
        self,
        mock_echo,
        mock_parser_class,
        mock_validator_class,
        mock_registry,
        sample_upf_file,
    ):
        """Test warning when editor not in targets."""
        mock_parser = Mock()
        mock_parser.parse_file.return_value = UniversalPrompt(
            schema_version="1.0.0",
            metadata=PromptMetadata(title="Test", description="Test"),
            targets=["cursor"],  # copilot not in targets
            instructions=Instructions(general=["test"]),
        )
        mock_parser_class.return_value = mock_parser

        mock_validator = Mock()
        mock_result = Mock()
        mock_result.errors = []
        mock_validator.validate.return_value = mock_result
        mock_validator_class.return_value = mock_validator

        mock_adapter = Mock()
        mock_adapter.generate.return_value = []
        mock_registry.get.return_value = mock_adapter

        ctx = Mock()
        ctx.obj = {"verbose": False}

        preview_command(ctx, sample_upf_file, "copilot", None)

        # Should echo warning
        warning_calls = [
            call for call in mock_echo.call_args_list if "Warning" in str(call)
        ]
        assert len(warning_calls) > 0


class TestPreviewCLI:
    """Test preview CLI command."""

    def test_preview_cli_help(self):
        """Test preview command help."""
        runner = CliRunner()
        result = runner.invoke(cli, ["preview", "--help"])

        assert result.exit_code == 0
        assert "preview" in result.output.lower()
        assert "--editor" in result.output

    def test_preview_cli_missing_file(self):
        """Test error with non-existent file."""
        runner = CliRunner()
        result = runner.invoke(cli, ["preview", "nonexistent.yaml", "--editor", "copilot"])

        assert result.exit_code != 0

    def test_preview_cli_missing_editor(self, sample_upf_file):
        """Test error when editor not specified."""
        runner = CliRunner()
        result = runner.invoke(cli, ["preview", str(sample_upf_file)])

        assert result.exit_code != 0
        assert "required" in result.output.lower() or "missing" in result.output.lower()

    def test_preview_cli_with_variables(self, sample_upf_file, tmp_path):
        """Test preview with variable overrides."""
        runner = CliRunner()

        with patch("promptrek.cli.commands.preview.registry") as mock_registry:
            with patch("promptrek.cli.commands.preview.UPFParser") as mock_parser_class:
                with patch("promptrek.cli.commands.preview.UPFValidator") as mock_validator_class:
                    # Setup mocks
                    mock_parser = Mock()
                    mock_parser.parse_file.return_value = UniversalPrompt(
                        schema_version="1.0.0",
                        metadata=PromptMetadata(title="Test", description="Test"),
                        targets=["copilot"],
                        instructions=Instructions(general=["test"]),
                    )
                    mock_parser_class.return_value = mock_parser

                    mock_validator = Mock()
                    mock_result = Mock()
                    mock_result.errors = []
                    mock_validator.validate.return_value = mock_result
                    mock_validator_class.return_value = mock_validator

                    mock_adapter = Mock()
                    mock_adapter.generate.return_value = []
                    mock_registry.get.return_value = mock_adapter

                    result = runner.invoke(
                        cli,
                        [
                            "preview",
                            str(sample_upf_file),
                            "--editor",
                            "copilot",
                            "-V",
                            "PROJECT=Test",
                            "-V",
                            "AUTHOR=Me",
                        ],
                    )

                    # Should complete successfully
                    assert result.exit_code == 0
                    assert "preview" in result.output.lower()