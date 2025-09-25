"""
Unit tests for Cursor adapter.
"""

import pytest

from src.promptrek.adapters.cursor import CursorAdapter

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
        assert adapter.description == "Cursor (.cursor/rules/, AGENTS.md)"
        assert adapter.file_patterns == [".cursor/rules/*.mdc", "AGENTS.md"]

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
        from src.promptrek.core.models import PromptMetadata, UniversalPrompt
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
            "TypeScript coding guidelines"
        )
        
        assert "---" in content  # YAML frontmatter
        assert "description: TypeScript coding guidelines" in content
        assert "globs: \"**/*.{ts,tsx}\"" in content
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

        # Should generate AGENTS.md + rules files
        assert len(files) >= 1
        agents_file = output_dir / "AGENTS.md"
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
        assert len(files) >= 1  # Should generate multiple files
