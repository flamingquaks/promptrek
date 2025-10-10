"""
Test cases for sync command functionality.
"""

import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import click
import pytest
import yaml

from promptrek.adapters.continue_adapter import ContinueAdapter
from promptrek.cli.commands.sync import (
    _merge_prompts,
    _preview_prompt,
    _write_prompt_file,
    sync_command,
)
from promptrek.core.exceptions import PrompTrekError
from promptrek.core.models import (
    Instructions,
    ProjectContext,
    PromptMetadata,
    UniversalPrompt,
    UniversalPromptV2,
)


class TestSyncCommand:
    """Test sync command functionality."""

    def test_continue_adapter_parse_files(self, tmp_path):
        """Test Continue adapter can parse its own generated files."""
        # Create test Continue files
        config_content = {
            "name": "Test Assistant",
            "systemMessage": "Test Assistant\n\nA test configuration",
            "rules": ["Write clean code", "Follow conventions", "Add comments"],
        }

        config_file = tmp_path / "config.yaml"
        with open(config_file, "w") as f:
            yaml.dump(config_content, f)

        # Create rules directory with markdown files
        rules_dir = tmp_path / ".continue" / "rules"
        rules_dir.mkdir(parents=True)

        general_md = rules_dir / "general.md"
        general_md.write_text(
            """# General Coding Rules

- Use descriptive variable names
- Follow project patterns
- Implement error handling

## Additional Guidelines
- Follow project-specific patterns and conventions
- Maintain consistency with existing codebase
- Consider performance and security implications
"""
        )

        code_style_md = rules_dir / "code-style.md"
        code_style_md.write_text(
            """# Code Style Rules

- Use consistent indentation
- Follow linting rules
- Prefer explicit code

## Additional Guidelines
- Follow project-specific patterns and conventions
- Maintain consistency with existing codebase
- Consider performance and security implications
"""
        )

        # Test parsing
        adapter = ContinueAdapter()
        parsed_prompt = adapter.parse_files(tmp_path)

        assert isinstance(parsed_prompt, UniversalPrompt)
        assert parsed_prompt.metadata.title == "Test Assistant"
        assert parsed_prompt.metadata.description == "A test configuration"
        assert "continue" in parsed_prompt.targets

        # Check instructions were parsed
        assert parsed_prompt.instructions is not None
        assert parsed_prompt.instructions.general is not None
        assert (
            len(parsed_prompt.instructions.general) >= 5
        )  # 3 from config + 3 from markdown (minus generic ones)
        assert "Write clean code" in parsed_prompt.instructions.general
        assert "Use descriptive variable names" in parsed_prompt.instructions.general

        assert parsed_prompt.instructions.code_style is not None
        assert "Use consistent indentation" in parsed_prompt.instructions.code_style

    def test_continue_adapter_parse_files_no_config(self, tmp_path):
        """Test parsing when only markdown files exist."""
        rules_dir = tmp_path / ".continue" / "rules"
        rules_dir.mkdir(parents=True)

        general_md = rules_dir / "general.md"
        general_md.write_text(
            """# General Rules
- Use descriptive names
- Follow patterns
"""
        )

        adapter = ContinueAdapter()
        parsed_prompt = adapter.parse_files(tmp_path)

        assert parsed_prompt.metadata.title == "Continue AI Assistant"
        assert len(parsed_prompt.instructions.general) == 2

    def test_continue_adapter_parse_files_empty_directory(self, tmp_path):
        """Test parsing from empty directory."""
        adapter = ContinueAdapter()
        parsed_prompt = adapter.parse_files(tmp_path)

        assert parsed_prompt.metadata.title == "Continue AI Assistant"
        assert (
            parsed_prompt.instructions.general is None
            or len(parsed_prompt.instructions.general) == 0
        )

    def test_merge_prompts(self):
        """Test merging of existing and parsed prompts."""
        # Create existing prompt
        existing = UniversalPrompt(
            schema_version="1.0.0",
            metadata=PromptMetadata(
                title="Existing Assistant",
                description="Original description",
                version="1.0.0",
                author="Original Author",
                created="2024-01-01",
                updated="2024-01-01",
            ),
            targets=["copilot"],
            instructions=Instructions(
                general=["Original instruction"], testing=["Original test rule"]
            ),
        )

        # Create parsed prompt
        parsed = UniversalPrompt(
            schema_version="1.0.0",
            metadata=PromptMetadata(
                title="Parsed Assistant",
                description="Parsed description",
                version="1.0.0",
                author="PrompTrek Sync",
                created="2024-01-02",
                updated="2024-01-02",
            ),
            targets=["continue"],
            instructions=Instructions(
                general=["New instruction", "Original instruction"],  # Duplicate
                code_style=["Style rule"],
            ),
        )

        # Test merge
        merged = _merge_prompts(existing, parsed, "continue")

        # Should keep existing metadata structure but update timestamp
        assert merged.metadata.title == "Existing Assistant"
        assert merged.metadata.description == "Original description"
        assert merged.metadata.updated == "2024-01-02"

        # Should merge targets
        assert "copilot" in merged.targets
        assert "continue" in merged.targets

        # Should merge instructions without duplicates
        assert "Original instruction" in merged.instructions.general
        assert "New instruction" in merged.instructions.general
        assert (
            len([i for i in merged.instructions.general if i == "Original instruction"])
            == 1
        )

        # Should preserve existing testing rules
        assert merged.instructions.testing == ["Original test rule"]

        # Should add new code_style rules
        assert merged.instructions.code_style == ["Style rule"]

    def test_parse_markdown_file(self, tmp_path):
        """Test parsing individual markdown files."""
        adapter = ContinueAdapter()

        md_file = tmp_path / "test.md"
        md_content = """# Test Rules

- Rule one
- Rule two with details
- Rule three

## Additional Guidelines
- Follow project-specific patterns and conventions
- Maintain consistency with existing codebase
- Consider performance and security implications

Some other text that should be ignored.

- Rule four
"""
        md_file.write_text(md_content)

        instructions = adapter._parse_markdown_file(md_file)

        assert len(instructions) == 4
        assert "Rule one" in instructions
        assert "Rule two with details" in instructions
        assert "Rule three" in instructions
        assert "Rule four" in instructions

        # Should not include the generic guidelines
        assert "Follow project-specific patterns and conventions" not in instructions
        assert "Maintain consistency with existing codebase" not in instructions
        assert "Consider performance and security implications" not in instructions

    def test_sync_command_dry_run(self, tmp_path):
        """Test sync command in dry run mode."""
        # Create a simple test directory structure
        rules_dir = tmp_path / ".continue" / "rules"
        rules_dir.mkdir(parents=True)

        general_md = rules_dir / "general.md"
        general_md.write_text("# General\n- Test rule")

        output_file = tmp_path / "output.yaml"

        # Mock click context
        ctx = MagicMock()

        # Test dry run
        sync_command(ctx, tmp_path, "continue", output_file, True, False)

        # Should not create the output file in dry run
        assert not output_file.exists()

    @patch("promptrek.cli.commands.sync.click.confirm")
    def test_sync_command_existing_file_no_force(self, mock_confirm, tmp_path):
        """Test sync command with existing file and no force flag."""
        # Create test files
        rules_dir = tmp_path / ".continue" / "rules"
        rules_dir.mkdir(parents=True)

        general_md = rules_dir / "general.md"
        general_md.write_text("# General\n- Test rule")

        # Create existing output file
        output_file = tmp_path / "output.yaml"
        output_file.write_text("existing content")

        # Mock user saying no to overwrite
        mock_confirm.return_value = False

        ctx = MagicMock()

        # Should exit without making changes
        sync_command(ctx, tmp_path, "continue", output_file, False, False)

        # File should still have original content
        assert output_file.read_text() == "existing content"

    def test_sync_command_unsupported_editor(self, tmp_path):
        """Test sync command with unsupported editor."""
        ctx = MagicMock()

        with pytest.raises(PrompTrekError, match="Unsupported editor: fake_editor"):
            sync_command(
                ctx, tmp_path, "fake_editor", tmp_path / "out.yaml", False, False
            )

    def test_sync_command_adapter_without_parse_files(self, tmp_path):
        """Test sync command with adapter that doesn't support parsing."""
        # Mock registry to return an adapter without parse_files method
        with patch("promptrek.cli.commands.sync.registry") as mock_registry:
            mock_adapter = MagicMock()
            del mock_adapter.parse_files  # Remove the parse_files attribute
            mock_adapter.supports_bidirectional_sync.return_value = False
            mock_registry.get.return_value = mock_adapter

            ctx = MagicMock()

            with pytest.raises(
                PrompTrekError,
                match="Editor 'test' does not support syncing from files",
            ):
                sync_command(ctx, tmp_path, "test", tmp_path / "out.yaml", False, False)

    def test_sync_command_parse_error(self, tmp_path):
        """Test sync command with parse error."""
        # Mock registry to return an adapter that raises an exception
        with patch("promptrek.cli.commands.sync.registry") as mock_registry:
            mock_adapter = MagicMock()
            mock_adapter.parse_files.side_effect = Exception("Parse error")
            mock_registry.get.return_value = mock_adapter

            ctx = MagicMock()

            with pytest.raises(
                PrompTrekError, match="Failed to parse test files: Parse error"
            ):
                sync_command(ctx, tmp_path, "test", tmp_path / "out.yaml", False, False)

    def test_preview_prompt(self, capsys):
        """Test preview prompt functionality."""
        prompt = UniversalPrompt(
            schema_version="1.0.0",
            metadata=PromptMetadata(
                title="Test Prompt",
                description="Test description",
                version="1.0.0",
                author="Test Author",
                created="2024-01-01",
                updated="2024-01-01",
            ),
            targets=["continue"],
            instructions=Instructions(
                general=["Rule 1", "Rule 2"], code_style=["Style 1"]
            ),
        )

        _preview_prompt(prompt)

        captured = capsys.readouterr()
        assert "Test Prompt" in captured.out
        assert "Test description" in captured.out
        assert "General: 2 instructions" in captured.out
        assert "Code_Style: 1 instructions" in captured.out

    def test_write_prompt_file(self, tmp_path):
        """Test writing prompt to file."""
        prompt = UniversalPrompt(
            schema_version="1.0.0",
            metadata=PromptMetadata(
                title="Test Prompt",
                description="Test description",
                version="1.0.0",
                author="Test Author",
                created="2024-01-01",
                updated="2024-01-01",
            ),
            targets=["continue"],
            instructions=Instructions(general=["Rule 1"]),
        )

        output_file = tmp_path / "test.yaml"
        _write_prompt_file(prompt, output_file)

        assert output_file.exists()

        # Check that file contains expected content
        content = yaml.safe_load(output_file.read_text())
        assert content["metadata"]["title"] == "Test Prompt"
        assert content["targets"] == ["continue"]
        assert content["instructions"]["general"] == ["Rule 1"]

    def test_sync_command_force_overwrite(self, tmp_path):
        """Test sync command with force overwrite."""
        # Create test files
        rules_dir = tmp_path / ".continue" / "rules"
        rules_dir.mkdir(parents=True)

        general_md = rules_dir / "general.md"
        general_md.write_text("# General\n- New test rule")

        # Create existing output file
        output_file = tmp_path / "output.yaml"
        output_file.write_text("existing content")

        ctx = MagicMock()

        # Should overwrite without asking
        sync_command(ctx, tmp_path, "continue", output_file, False, True)

        # File should have new content
        content = yaml.safe_load(output_file.read_text())
        assert content["metadata"]["title"] == "Continue AI Assistant"
        assert "New test rule" in content["instructions"]["general"]

    def test_continue_adapter_technology_detection(self, tmp_path):
        """Test technology detection from technology-specific rule files."""
        rules_dir = tmp_path / ".continue" / "rules"
        rules_dir.mkdir(parents=True)

        # Create technology-specific files
        python_rules = rules_dir / "python-rules.md"
        python_rules.write_text("# Python Rules\n- Use type hints\n- Follow PEP 8")

        js_rules = rules_dir / "javascript-rules.md"
        js_rules.write_text("# JavaScript Rules\n- Use const/let\n- Avoid var")

        adapter = ContinueAdapter()
        parsed_prompt = adapter.parse_files(tmp_path)

        # Should detect technologies
        assert parsed_prompt.context is not None
        assert "python" in parsed_prompt.context.technologies
        assert "javascript" in parsed_prompt.context.technologies

        # Should include tech-specific rules in general instructions
        assert "Use type hints" in parsed_prompt.instructions.general
        assert "Use const/let" in parsed_prompt.instructions.general

    def test_write_v2_prompt_with_literal_block_scalar(self, tmp_path):
        """Test that v2 prompts with multi-line content use literal block scalar formatting."""
        content = """# Test Project

## Overview
This is a test project with multiple lines.

## Guidelines
- Follow best practices
- Write tests
- Document code
"""

        prompt = UniversalPromptV2(
            schema_version="2.0.0",
            metadata=PromptMetadata(
                title="Test Prompt",
                description="Test description",
                version="1.0.0",
                author="Test Author",
                created="2024-01-01",
                updated="2024-01-01",
            ),
            content=content,
        )

        output_file = tmp_path / "test.yaml"
        _write_prompt_file(prompt, output_file)

        assert output_file.exists()

        # Read the raw YAML file
        yaml_content = output_file.read_text()

        # Should use literal block scalar (|- or |)
        assert "content: |" in yaml_content or "content: |-" in yaml_content

        # Should NOT have escaped newlines
        assert "\\n" not in yaml_content

        # Should have actual readable content
        assert "# Test Project" in yaml_content
        assert "## Overview" in yaml_content
        assert "- Follow best practices" in yaml_content

        # Also verify it can be parsed back correctly
        parsed_data = yaml.safe_load(yaml_content)
        assert parsed_data["content"] == content
