"""Comprehensive tests for generate command."""

import inspect
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import pytest
from click.testing import CliRunner

from promptrek.adapters.registry import AdapterCapability
from promptrek.cli.commands.generate import (
    _adapter_supports_headless,
    _generate_for_editor,
    _generate_for_editor_multiple,
    _parse_and_validate_file,
    generate_command,
)
from promptrek.cli.main import cli
from promptrek.core.exceptions import AdapterNotFoundError, CLIError, UPFParsingError
from promptrek.core.models import Instructions, PromptMetadata, UniversalPrompt


class TestAdapterSupportsHeadless:
    """Test _adapter_supports_headless helper function."""

    def test_supports_headless_with_parameter(self):
        """Test adapter with headless parameter."""

        class MockAdapter:
            def generate(
                self, prompt, output_dir, dry_run, verbose, variables, headless=False
            ):
                pass

        adapter = MockAdapter()
        assert _adapter_supports_headless(adapter, "generate") is True

    def test_supports_headless_without_parameter(self):
        """Test adapter without headless parameter."""

        class MockAdapter:
            def generate(self, prompt, output_dir, dry_run, verbose, variables):
                pass

        adapter = MockAdapter()
        assert _adapter_supports_headless(adapter, "generate") is False

    def test_supports_headless_no_method(self):
        """Test adapter without the method."""

        class MockAdapter:
            pass

        adapter = MockAdapter()
        assert _adapter_supports_headless(adapter, "generate") is False

    def test_supports_headless_signature_error(self):
        """Test handling of signature inspection errors."""

        class MockAdapter:
            @property
            def generate(self):
                return None

        adapter = MockAdapter()
        # Should return False when signature inspection fails
        result = _adapter_supports_headless(adapter, "generate")
        assert result is False


class TestParseAndValidateFile:
    """Test _parse_and_validate_file function."""

    def test_parse_valid_file(self, sample_upf_file):
        """Test parsing valid file."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            ctx = Mock()
            ctx.obj = {"verbose": False}

            result = _parse_and_validate_file(ctx, sample_upf_file)

            assert isinstance(result, UniversalPrompt)
            assert result.metadata.title is not None

    def test_parse_with_verbose(self, sample_upf_file):
        """Test parsing with verbose output."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            ctx = Mock()
            ctx.obj = {"verbose": True}

            with patch("click.echo") as mock_echo:
                result = _parse_and_validate_file(ctx, sample_upf_file)

                assert isinstance(result, UniversalPrompt)
                # Should echo parsed message
                mock_echo.assert_called()

    def test_parse_invalid_file(self, tmp_path):
        """Test parsing invalid YAML file."""
        invalid_file = tmp_path / "invalid.yaml"
        invalid_file.write_text("invalid: yaml: content: [")

        ctx = Mock()
        ctx.obj = {"verbose": False}

        with pytest.raises(CLIError, match="Failed to parse"):
            _parse_and_validate_file(ctx, invalid_file)

    def test_parse_validation_errors(self, tmp_path):
        """Test file with validation errors."""
        invalid_file = tmp_path / "invalid.promptrek.yaml"
        # Missing required metadata.description field
        invalid_file.write_text(
            """
schema_version: "1.0.0"
metadata:
  title: "Test"
targets: []
"""
        )

        ctx = Mock()
        ctx.obj = {"verbose": False}

        with pytest.raises(CLIError, match="Validation failed|Failed to parse"):
            _parse_and_validate_file(ctx, invalid_file)


class TestGenerateForEditor:
    """Test _generate_for_editor function."""

    @patch("promptrek.cli.commands.generate.registry")
    def test_generate_basic(self, mock_registry, sample_prompt):
        """Test basic generation."""
        mock_adapter = Mock()
        mock_adapter.generate = Mock()
        mock_registry.get.return_value = mock_adapter

        output_dir = Path("/tmp/output")
        _generate_for_editor(
            sample_prompt, "copilot", output_dir, False, False, None, None, False
        )

        mock_adapter.generate.assert_called_once()

    @patch("promptrek.cli.commands.generate.registry")
    def test_generate_with_headless_support(self, mock_registry, sample_prompt):
        """Test generation with headless mode support."""

        class MockAdapter:
            def generate(
                self, prompt, output_dir, dry_run, verbose, variables, headless=False
            ):
                return []

        mock_adapter = MockAdapter()
        mock_adapter.generate = Mock(return_value=[])
        mock_registry.get.return_value = mock_adapter

        output_dir = Path("/tmp/output")
        _generate_for_editor(
            sample_prompt, "copilot", output_dir, False, False, None, None, True
        )

        # Should call with headless=True
        assert mock_adapter.generate.called
        # Check either positional or keyword arguments
        call_args, call_kwargs = mock_adapter.generate.call_args
        # headless is typically the 6th positional or a keyword arg
        if "headless" in call_kwargs:
            assert call_kwargs["headless"] is True
        elif len(call_args) > 5:
            assert call_args[5] is True  # headless is 6th param (0-indexed)

    @patch("promptrek.cli.commands.generate.registry")
    @patch("click.echo")
    def test_generate_headless_without_support(
        self, mock_echo, mock_registry, sample_prompt
    ):
        """Test generation with headless mode when adapter doesn't support it."""

        class MockAdapter:
            def generate(self, prompt, output_dir, dry_run, verbose, variables):
                pass

        mock_adapter = MockAdapter()
        mock_adapter.generate = Mock()
        mock_registry.get.return_value = mock_adapter

        output_dir = Path("/tmp/output")
        _generate_for_editor(
            sample_prompt, "copilot", output_dir, False, False, None, None, True
        )

        # Should warn about unsupported headless mode
        mock_echo.assert_called()
        warning_calls = [
            call for call in mock_echo.call_args_list if "Warning" in str(call)
        ]
        assert len(warning_calls) > 0

    @patch("promptrek.cli.commands.generate.registry")
    def test_generate_adapter_not_found(self, mock_registry, sample_prompt):
        """Test generation with non-existent adapter."""
        mock_registry.get.side_effect = AdapterNotFoundError("Not found")

        with pytest.raises(AdapterNotFoundError):
            _generate_for_editor(
                sample_prompt, "unknown", Path("/tmp"), False, False, None, None, False
            )


class TestGenerateForEditorMultiple:
    """Test _generate_for_editor_multiple function."""

    @patch("promptrek.cli.commands.generate.registry")
    def test_generate_single_file(self, mock_registry, sample_prompt):
        """Test generation with single file."""
        mock_adapter = Mock()
        mock_adapter.generate = Mock()
        mock_registry.get.return_value = mock_adapter

        prompt_files = [(sample_prompt, Path("test.yaml"))]
        _generate_for_editor_multiple(
            prompt_files, "copilot", Path("/tmp"), False, False, None, False
        )

        mock_adapter.generate.assert_called_once()

    @patch("promptrek.cli.commands.generate.registry")
    def test_generate_multiple_with_merge_support(self, mock_registry, sample_prompt):
        """Test generation with multiple files and merge support."""
        mock_adapter = Mock()
        mock_adapter.generate_merged = Mock(return_value=[])
        mock_adapter.generate_multiple = None  # Not present
        mock_registry.get.return_value = mock_adapter
        mock_registry.has_capability.return_value = False  # No multiple file capability

        prompt_files = [
            (sample_prompt, Path("test1.yaml")),
            (sample_prompt, Path("test2.yaml")),
        ]
        _generate_for_editor_multiple(
            prompt_files, "copilot", Path("/tmp"), False, False, None, False
        )

        mock_adapter.generate_merged.assert_called_once()

    @patch("promptrek.cli.commands.generate.registry")
    def test_generate_multiple_with_capability(self, mock_registry, sample_prompt):
        """Test generation with multiple files and multiple file capability."""
        mock_adapter = Mock()
        mock_adapter.generate_multiple = Mock()
        mock_registry.get.return_value = mock_adapter
        mock_registry.has_capability.return_value = True

        prompt_files = [
            (sample_prompt, Path("test1.yaml")),
            (sample_prompt, Path("test2.yaml")),
        ]
        _generate_for_editor_multiple(
            prompt_files, "copilot", Path("/tmp"), False, False, None, False
        )

        mock_adapter.generate_multiple.assert_called_once()

    @patch("promptrek.cli.commands.generate.registry")
    @patch("click.echo")
    def test_generate_multiple_fallback(self, mock_echo, mock_registry, sample_prompt):
        """Test generation fallback when merge not supported."""
        mock_adapter = Mock()
        mock_adapter.generate = Mock()
        mock_adapter.generate_merged = Mock(side_effect=NotImplementedError)
        mock_registry.get.return_value = mock_adapter
        mock_registry.has_capability.return_value = False

        prompt_files = [
            (sample_prompt, Path("test1.yaml")),
            (sample_prompt, Path("test2.yaml")),
        ]
        _generate_for_editor_multiple(
            prompt_files, "copilot", Path("/tmp"), False, False, None, False
        )

        # Should fall back to generate
        mock_adapter.generate.assert_called_once()
        # Should warn about fallback
        warning_calls = [
            call
            for call in mock_echo.call_args_list
            if "doesn't support merging" in str(call)
        ]
        assert len(warning_calls) > 0


class TestGenerateCommand:
    """Test generate_command function."""

    @patch("promptrek.cli.commands.generate.UPFParser")
    def test_generate_no_files_error(self, mock_parser_class, tmp_path):
        """Test error when no files found."""
        # Mock parser to return no files
        mock_parser = Mock()
        mock_parser.find_upf_files.return_value = []
        mock_parser_class.return_value = mock_parser

        ctx = Mock()
        ctx.obj = {"verbose": False}

        with pytest.raises(CLIError, match="No UPF files found"):
            generate_command(
                ctx,
                tuple(),
                None,
                False,
                "copilot",
                tmp_path,
                False,
                False,
                None,
                False,
            )

    def test_generate_missing_editor_flag(self, sample_upf_file):
        """Test error when neither --editor nor --all specified."""
        ctx = Mock()
        ctx.obj = {"verbose": False}

        with pytest.raises(CLIError, match="Must specify either --editor or --all"):
            generate_command(
                ctx,
                (sample_upf_file,),
                None,
                False,
                None,  # No editor
                Path("/tmp"),
                False,
                False,  # Not --all
                None,
                False,
            )

    @patch("promptrek.cli.commands.generate._generate_for_editor_multiple")
    @patch("promptrek.cli.commands.generate.UPFParser")
    def test_generate_with_directory(
        self, mock_parser_class, mock_generate, tmp_path, sample_upf_file
    ):
        """Test generation with --directory option."""
        # Setup mock parser
        mock_parser = Mock()
        mock_parser.find_upf_files.return_value = [sample_upf_file]
        mock_parser.parse_file.return_value = UniversalPrompt(
            schema_version="1.0.0",
            metadata=PromptMetadata(title="Test", description="Test"),
            targets=["copilot"],
            instructions=Instructions(general=["test"]),
        )
        mock_parser_class.return_value = mock_parser

        ctx = Mock()
        ctx.obj = {"verbose": False}

        generate_command(
            ctx,
            tuple(),
            tmp_path,  # directory
            False,
            "copilot",
            tmp_path,
            False,
            False,
            None,
            False,
        )

        # Should find files in directory
        mock_parser.find_upf_files.assert_called()
        mock_generate.assert_called_once()

    @patch("promptrek.cli.commands.generate._generate_for_editor_multiple")
    @patch("promptrek.cli.commands.generate.UPFParser")
    def test_generate_recursive(
        self, mock_parser_class, mock_generate, tmp_path, sample_upf_file
    ):
        """Test generation with recursive directory search."""
        mock_parser = Mock()
        mock_parser.find_upf_files.return_value = [sample_upf_file]
        mock_parser.parse_file.return_value = UniversalPrompt(
            schema_version="1.0.0",
            metadata=PromptMetadata(title="Test", description="Test"),
            targets=["copilot"],
            instructions=Instructions(general=["test"]),
        )
        mock_parser_class.return_value = mock_parser

        ctx = Mock()
        ctx.obj = {"verbose": False}

        generate_command(
            ctx,
            tuple(),
            tmp_path,
            True,  # recursive
            "copilot",
            tmp_path,
            False,
            False,
            None,
            False,
        )

        # Should call find_upf_files with recursive=True
        call_args = mock_parser.find_upf_files.call_args
        assert call_args[0][1] is True  # recursive argument

    @patch("promptrek.cli.commands.generate._generate_for_editor_multiple")
    @patch("promptrek.cli.commands.generate.UPFParser")
    def test_generate_dry_run(
        self, mock_parser_class, mock_generate, tmp_path, sample_upf_file
    ):
        """Test dry-run mode."""
        mock_parser = Mock()
        mock_parser.find_upf_files.return_value = []
        mock_parser.parse_file.return_value = UniversalPrompt(
            schema_version="1.0.0",
            metadata=PromptMetadata(title="Test", description="Test"),
            targets=["copilot"],
            instructions=Instructions(general=["test"]),
        )
        mock_parser_class.return_value = mock_parser

        ctx = Mock()
        ctx.obj = {"verbose": False}

        with patch("click.echo") as mock_echo:
            generate_command(
                ctx,
                (sample_upf_file,),
                None,
                False,
                "copilot",
                tmp_path,
                True,  # dry_run
                False,
                None,
                False,
            )

            # Should echo dry run message
            dry_run_calls = [
                call for call in mock_echo.call_args_list if "Dry run" in str(call)
            ]
            assert len(dry_run_calls) > 0

    @patch("promptrek.cli.commands.generate._generate_for_editor_multiple")
    @patch("promptrek.cli.commands.generate.UPFValidator")
    @patch("promptrek.cli.commands.generate.UPFParser")
    def test_generate_with_variables(
        self,
        mock_parser_class,
        mock_validator_class,
        mock_generate,
        tmp_path,
        sample_upf_file,
    ):
        """Test generation with variable overrides."""
        mock_parser = Mock()
        mock_parser.find_upf_files.return_value = []
        mock_parser.parse_file.return_value = UniversalPrompt(
            schema_version="1.0.0",
            metadata=PromptMetadata(title="Test", description="Test"),
            targets=["copilot"],
            instructions=Instructions(general=["test"]),
        )
        mock_parser_class.return_value = mock_parser

        # Mock validator
        mock_validator = Mock()
        mock_result = Mock()
        mock_result.errors = []
        mock_validator.validate.return_value = mock_result
        mock_validator_class.return_value = mock_validator

        ctx = Mock()
        ctx.obj = {"verbose": False}

        variables = {"PROJECT_NAME": "MyProject", "AUTHOR": "Test"}
        generate_command(
            ctx,
            (sample_upf_file,),
            None,
            False,
            "copilot",
            tmp_path,
            False,
            False,
            variables,
            False,
        )

        # Should pass variables to generate function as cli_overrides
        # _generate_for_editor_multiple is called with keyword args
        assert mock_generate.called
        call_args = mock_generate.call_args
        # Check that cli_overrides contains the variables we passed
        assert call_args[1].get("cli_overrides") == variables
        # Check that base_variables contains built-in variables
        assert "CURRENT_DATE" in call_args[1].get("base_variables", {})

    @patch("promptrek.cli.commands.generate._generate_for_editor_multiple")
    @patch("promptrek.cli.commands.generate.UPFParser")
    def test_generate_duplicate_files(
        self, mock_parser_class, mock_generate, tmp_path, sample_upf_file
    ):
        """Test that duplicate files are removed."""
        mock_parser = Mock()
        mock_parser.find_upf_files.return_value = [sample_upf_file, sample_upf_file]
        mock_parser.parse_file.return_value = UniversalPrompt(
            schema_version="1.0.0",
            metadata=PromptMetadata(title="Test", description="Test"),
            targets=["copilot"],
            instructions=Instructions(general=["test"]),
        )
        mock_parser_class.return_value = mock_parser

        ctx = Mock()
        ctx.obj = {"verbose": False}

        generate_command(
            ctx,
            (sample_upf_file, sample_upf_file),  # Duplicate
            None,
            False,
            "copilot",
            tmp_path,
            False,
            False,
            None,
            False,
        )

        # File is parsed twice: once to check allow_commands, once to generate
        # But duplicates are still removed (only unique file in the list)
        assert (
            mock_parser.parse_file.call_count == 2
        )  # parse for allow_commands + parse for generation
        assert mock_generate.call_count == 1  # but generate is only called once

    @patch("promptrek.cli.commands.generate._generate_for_editor_multiple")
    @patch("promptrek.cli.commands.generate.UPFParser")
    @patch("click.echo")
    def test_generate_editor_not_in_targets_warning(
        self, mock_echo, mock_parser_class, mock_generate, tmp_path, sample_upf_file
    ):
        """Test warning when editor not in file targets (multiple files)."""
        mock_parser = Mock()
        file1 = tmp_path / "file1.yaml"
        file2 = tmp_path / "file2.yaml"
        file1.touch()
        file2.touch()

        # First file has copilot target, second doesn't
        def parse_side_effect(path):
            if "file1" in str(path):
                return UniversalPrompt(
                    schema_version="1.0.0",
                    metadata=PromptMetadata(title="Test1", description="Test"),
                    targets=["copilot"],
                    instructions=Instructions(general=["test"]),
                )
            else:
                return UniversalPrompt(
                    schema_version="1.0.0",
                    metadata=PromptMetadata(title="Test2", description="Test"),
                    targets=["cursor"],  # Different target
                    instructions=Instructions(general=["test"]),
                )

        mock_parser.parse_file.side_effect = parse_side_effect
        mock_parser.find_upf_files.return_value = []
        mock_parser_class.return_value = mock_parser

        ctx = Mock()
        ctx.obj = {"verbose": True}

        generate_command(
            ctx,
            (file1, file2),
            None,
            False,
            "copilot",
            tmp_path,
            False,
            False,
            None,
            False,
        )

        # Should warn about skipping file2
        warning_calls = [
            call for call in mock_echo.call_args_list if "skipping" in str(call)
        ]
        assert len(warning_calls) > 0

    @patch("promptrek.cli.commands.generate.UPFParser")
    def test_generate_parsing_error(self, mock_parser_class, tmp_path):
        """Test handling of parsing errors."""
        mock_parser = Mock()
        mock_parser.find_upf_files.return_value = []
        mock_parser.parse_file.side_effect = UPFParsingError("Parse error")
        mock_parser_class.return_value = mock_parser

        bad_file = tmp_path / "bad.yaml"
        bad_file.write_text("invalid")

        ctx = Mock()
        ctx.obj = {"verbose": False}

        with pytest.raises(CLIError, match="Failed to parse"):
            generate_command(
                ctx,
                (bad_file,),
                None,
                False,
                "copilot",
                tmp_path,
                False,
                False,
                None,
                False,
            )

    @patch("promptrek.cli.commands.generate._generate_for_editor_multiple")
    @patch("promptrek.cli.commands.generate.UPFParser")
    @patch("click.echo")
    def test_generate_adapter_not_found_warning(
        self, mock_echo, mock_parser_class, mock_generate, tmp_path, sample_upf_file
    ):
        """Test warning when adapter not found."""
        mock_parser = Mock()
        mock_parser.find_upf_files.return_value = []
        mock_parser.parse_file.return_value = UniversalPrompt(
            schema_version="1.0.0",
            metadata=PromptMetadata(title="Test", description="Test"),
            targets=["unknown_editor"],
            instructions=Instructions(general=["test"]),
        )
        mock_parser_class.return_value = mock_parser
        mock_generate.side_effect = AdapterNotFoundError("Not found")

        ctx = Mock()
        ctx.obj = {"verbose": False}

        generate_command(
            ctx,
            (sample_upf_file,),
            None,
            False,
            "unknown_editor",
            tmp_path,
            False,
            False,
            None,
            False,
        )

        # Should echo warning about not implemented
        warning_calls = [
            call
            for call in mock_echo.call_args_list
            if "not yet implemented" in str(call)
        ]
        assert len(warning_calls) > 0


class TestProcessSingleFile:
    """Test _process_single_file function."""

    @patch("promptrek.cli.commands.generate._generate_for_editor")
    @patch("promptrek.cli.commands.generate.UPFValidator")
    @patch("promptrek.cli.commands.generate.UPFParser")
    def test_process_single_file_all_editors(
        self,
        mock_parser_class,
        mock_validator_class,
        mock_generate,
        sample_upf_file,
        tmp_path,
    ):
        """Test processing single file with --all flag."""
        from promptrek.cli.commands.generate import _process_single_file

        mock_parser = Mock()
        mock_parser.parse_file.return_value = UniversalPrompt(
            schema_version="1.0.0",
            metadata=PromptMetadata(title="Test", description="Test"),
            targets=["copilot", "cursor"],
            instructions=Instructions(general=["test"]),
        )
        mock_parser_class.return_value = mock_parser

        mock_validator = Mock()
        mock_result = Mock()
        mock_result.errors = []
        mock_validator.validate.return_value = mock_result
        mock_validator_class.return_value = mock_validator

        with patch("promptrek.cli.commands.generate.registry") as mock_registry:
            mock_registry.get_project_file_adapters.return_value = ["copilot", "cursor"]
            mock_registry.get_global_config_adapters.return_value = []
            mock_registry.get_adapters_by_capability.return_value = []

            ctx = Mock()
            ctx.obj = {"verbose": False}

            _process_single_file(
                ctx, sample_upf_file, None, tmp_path, False, True, None, False
            )

            # Should call generate for both editors
            assert mock_generate.call_count == 2

    @patch("promptrek.cli.commands.generate.UPFValidator")
    @patch("promptrek.cli.commands.generate.UPFParser")
    @patch("click.echo")
    def test_process_single_file_global_config_only(
        self,
        mock_echo,
        mock_parser_class,
        mock_validator_class,
        sample_upf_file,
        tmp_path,
    ):
        """Test processing file with global config only adapter."""
        from promptrek.cli.commands.generate import _process_single_file

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

        with patch("promptrek.cli.commands.generate.registry") as mock_registry:
            mock_registry.list_adapters.return_value = ["copilot"]
            mock_registry.has_capability.return_value = False  # No project files
            mock_registry.get_adapter_info.return_value = {
                "capabilities": [AdapterCapability.GLOBAL_CONFIG_ONLY.value]
            }

            ctx = Mock()
            ctx.obj = {"verbose": False}

            _process_single_file(
                ctx, sample_upf_file, "copilot", tmp_path, False, False, None, False
            )

            # Should echo info about global config
            info_calls = [
                call
                for call in mock_echo.call_args_list
                if "global" in str(call).lower()
            ]
            assert len(info_calls) > 0

    @patch("promptrek.cli.commands.generate.UPFValidator")
    @patch("promptrek.cli.commands.generate.UPFParser")
    @patch("click.echo")
    def test_process_single_file_ide_plugin_only(
        self,
        mock_echo,
        mock_parser_class,
        mock_validator_class,
        sample_upf_file,
        tmp_path,
    ):
        """Test processing file with IDE plugin only adapter."""
        from promptrek.cli.commands.generate import _process_single_file

        mock_parser = Mock()
        mock_parser.parse_file.return_value = UniversalPrompt(
            schema_version="1.0.0",
            metadata=PromptMetadata(title="Test", description="Test"),
            targets=["windsurf"],
            instructions=Instructions(general=["test"]),
        )
        mock_parser_class.return_value = mock_parser

        mock_validator = Mock()
        mock_result = Mock()
        mock_result.errors = []
        mock_validator.validate.return_value = mock_result
        mock_validator_class.return_value = mock_validator

        with patch("promptrek.cli.commands.generate.registry") as mock_registry:
            mock_registry.list_adapters.return_value = ["windsurf"]
            mock_registry.has_capability.return_value = False
            mock_registry.get_adapter_info.return_value = {
                "capabilities": [AdapterCapability.IDE_PLUGIN_ONLY.value]
            }

            ctx = Mock()
            ctx.obj = {"verbose": False}

            _process_single_file(
                ctx, sample_upf_file, "windsurf", tmp_path, False, False, None, False
            )

            # Should echo info about IDE configuration
            info_calls = [
                call for call in mock_echo.call_args_list if "IDE" in str(call)
            ]
            assert len(info_calls) > 0

    @patch("promptrek.cli.commands.generate.UPFValidator")
    @patch("promptrek.cli.commands.generate.UPFParser")
    def test_process_single_file_invalid_editor(
        self, mock_parser_class, mock_validator_class, sample_upf_file, tmp_path
    ):
        """Test processing file with invalid editor."""
        from promptrek.cli.commands.generate import _process_single_file

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

        with patch("promptrek.cli.commands.generate.registry") as mock_registry:
            mock_registry.list_adapters.return_value = ["copilot"]

            ctx = Mock()
            ctx.obj = {"verbose": False}

            with pytest.raises(CLIError, match="not available"):
                _process_single_file(
                    ctx,
                    sample_upf_file,
                    "unknown_editor",
                    tmp_path,
                    False,
                    False,
                    None,
                    False,
                )

    @patch("promptrek.cli.commands.generate._generate_for_editor")
    @patch("promptrek.cli.commands.generate.UPFValidator")
    @patch("promptrek.cli.commands.generate.UPFParser")
    @patch("click.echo")
    def test_process_single_file_with_verbose_errors(
        self,
        mock_echo,
        mock_parser_class,
        mock_validator_class,
        mock_generate,
        sample_upf_file,
        tmp_path,
    ):
        """Test processing file with generation errors in verbose mode."""
        from promptrek.cli.commands.generate import _process_single_file

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

        mock_generate.side_effect = Exception("Test error")

        with patch("promptrek.cli.commands.generate.registry") as mock_registry:
            mock_registry.list_adapters.return_value = ["copilot"]
            mock_registry.has_capability.return_value = True

            ctx = Mock()
            ctx.obj = {"verbose": True}

            with pytest.raises(Exception, match="Test error"):
                _process_single_file(
                    ctx, sample_upf_file, "copilot", tmp_path, False, False, None, False
                )


class TestGenerateCLIIntegration:
    """Integration tests for generate CLI command."""

    def test_generate_cli_help(self):
        """Test generate command help."""
        runner = CliRunner()
        result = runner.invoke(cli, ["generate", "--help"])

        assert result.exit_code == 0
        assert "generate" in result.output.lower()
        assert "--editor" in result.output
        assert "--all" in result.output
        assert "--dry-run" in result.output

    def test_generate_cli_missing_file(self):
        """Test error with non-existent file."""
        runner = CliRunner()
        result = runner.invoke(
            cli, ["generate", "nonexistent.yaml", "--editor", "copilot"]
        )

        assert result.exit_code != 0

    def test_generate_cli_dry_run_output(self, sample_upf_file, tmp_path):
        """Test dry-run shows expected output."""
        runner = CliRunner()
        result = runner.invoke(
            cli,
            [
                "generate",
                str(sample_upf_file),
                "--editor",
                "copilot",
                "--output",
                str(tmp_path),
                "--dry-run",
            ],
        )

        assert "Dry run" in result.output
        # Files shouldn't actually be created
        assert not (tmp_path / ".github" / "copilot-instructions.md").exists()

    def test_generate_cli_verbose(self, sample_upf_file, tmp_path):
        """Test verbose output."""
        runner = CliRunner()
        result = runner.invoke(
            cli,
            [
                "--verbose",
                "generate",
                str(sample_upf_file),
                "--editor",
                "copilot",
                "--output",
                str(tmp_path),
            ],
        )

        assert "Processing" in result.output or "Generated" in result.output

    def test_generate_cli_variable_override(self, sample_upf_file, tmp_path):
        """Test variable override via CLI."""
        runner = CliRunner()
        result = runner.invoke(
            cli,
            [
                "generate",
                str(sample_upf_file),
                "--editor",
                "copilot",
                "--output",
                str(tmp_path),
                "-V",
                "PROJECT_NAME=TestProject",
                "-V",
                "AUTHOR=TestAuthor",
            ],
        )

        # Should complete without error
        assert result.exit_code == 0
