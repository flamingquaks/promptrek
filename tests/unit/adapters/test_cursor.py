"""
Unit tests for Cursor adapter.
"""

import pytest

from promptrek.adapters.cursor import CursorAdapter

from .base_test import TestAdapterBase


class TestCursorAdapter(TestAdapterBase):
    """Test Cursor adapter."""

    @pytest.fixture
    def adapter(self):
        """Create Cursor adapter instance."""
        return CursorAdapter()

    def test_init(self, adapter):
        """Test adapter initialization."""
        assert adapter.name == "cursor"
        assert (
            adapter.description
            == "Cursor (.cursor/rules/index.mdc, .cursor/rules/*.mdc, AGENTS.md)"
        )
        assert adapter.file_patterns == [
            ".cursor/rules/index.mdc",
            ".cursor/rules/*.mdc",
            "AGENTS.md",
        ]

    def test_supports_features(self, adapter):
        """Test feature support."""
        assert adapter.supports_variables() is True
        assert adapter.supports_conditionals() is True

    def test_validate_valid_prompt(self, adapter, sample_prompt):
        """Test validation of valid prompt."""
        errors = adapter.validate(sample_prompt)
        assert len(errors) == 0

    def test_validate_missing_instructions(self, adapter):
        """Test validation with missing instructions."""
        from promptrek.core.models import PromptMetadata, UniversalPrompt

        prompt = UniversalPrompt(
            schema_version="1.0.0",
            metadata=PromptMetadata(
                title="Test",
                description="Test description",
                version="1.0.0",
                author="test@example.com",
                created="2024-01-01",
                updated="2024-01-01",
            ),
            targets=["cursor"],
        )
        errors = adapter.validate(prompt)
        assert len(errors) == 1
        assert errors[0].field == "instructions"

    def test_build_mdc_content(self, adapter):
        """Test MDF file content generation."""
        instructions = ["Follow TypeScript best practices", "Use strict mode"]
        content = adapter._build_mdc_content(
            "TypeScript Rules",
            instructions,
            "**/*.{ts,tsx}",
            "TypeScript coding guidelines",
        )

        assert "---" in content  # YAML frontmatter
        assert "description: TypeScript coding guidelines" in content
        assert 'globs: "**/*.{ts,tsx}"' in content
        assert "alwaysApply: false" in content
        assert "# TypeScript Rules" in content
        assert "- Follow TypeScript best practices" in content

    def test_build_agents_content(self, adapter, sample_prompt):
        """Test AGENTS.md content generation."""
        content = adapter._build_agents_content(sample_prompt)

        assert sample_prompt.metadata.title in content
        assert sample_prompt.metadata.description in content
        assert "## Project Context" in content
        assert "## General Instructions" in content

    from unittest.mock import mock_open, patch

    @patch("builtins.open", new_callable=mock_open)
    @patch("pathlib.Path.mkdir")
    def test_generate_actual_files(self, mock_mkdir, mock_file, adapter, sample_prompt):
        """Test actual file generation."""
        from pathlib import Path

        output_dir = Path("/tmp/test")
        files = adapter.generate(sample_prompt, output_dir, dry_run=False)

        # Should generate index.mdc, AGENTS.md + rules files
        assert len(files) >= 2

        # Check for modern files
        index_file = output_dir / ".cursor" / "rules" / "index.mdc"
        agents_file = output_dir / "AGENTS.md"
        assert index_file in files
        assert agents_file in files

        # Check that mkdir and file operations were called
        assert mock_mkdir.called
        assert mock_file.called

    def test_generate_dry_run(self, adapter, sample_prompt, capsys):
        """Test dry run generation."""
        from pathlib import Path

        output_dir = Path("/tmp/test")
        files = adapter.generate(sample_prompt, output_dir, dry_run=True)

        captured = capsys.readouterr()
        assert "Would create" in captured.out
        assert len(files) >= 2  # Should generate multiple files including index.mdc

    def test_generate_index_mdc_content(self, adapter, sample_prompt):
        """Test that index.mdc is generated with correct content."""
        content = adapter._build_single_index_content(sample_prompt)

        # Check YAML frontmatter
        assert "---" in content
        assert "description: Project overview and core guidelines" in content
        assert "alwaysApply: true" in content

        # Check project metadata
        assert sample_prompt.metadata.title in content
        assert sample_prompt.metadata.description in content

        # Check project context if present
        if sample_prompt.context:
            assert "## Project Context" in content

        # Check core guidelines if present
        if sample_prompt.instructions and sample_prompt.instructions.general:
            assert "## Core Guidelines" in content

    def test_generate_merged_creates_modern_files(self, adapter, sample_prompt):
        """Test that generate_merged creates modern .mdc files instead of legacy .cursorrules."""
        from pathlib import Path

        output_dir = Path("/tmp/test")
        prompt_files = [(sample_prompt, Path("test.promptrek.yaml"))]

        files = adapter.generate_merged(prompt_files, output_dir, dry_run=True)

        # Should generate modern index.mdc file
        index_file = output_dir / ".cursor" / "rules" / "index.mdc"
        assert index_file in files

        # Should NOT generate legacy .cursorrules
        legacy_file = output_dir / ".cursorrules"
        assert legacy_file not in files
