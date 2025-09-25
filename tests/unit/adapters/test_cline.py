"""
Unit tests for Cline adapter.
"""

import json
from pathlib import Path
from unittest.mock import mock_open, patch

import pytest

from src.promptrek.adapters.cline import ClineAdapter
from src.promptrek.core.models import PromptMetadata, UniversalPrompt

from .base_test import TestAdapterBase


class TestClineAdapter(TestAdapterBase):
    """Test Cline adapter."""

    @pytest.fixture
    def adapter(self):
        """Create Cline adapter instance."""
        return ClineAdapter()

    def test_init(self, adapter):
        """Test adapter initialization."""
        assert adapter.name == "cline"
        assert adapter.description == "Cline (.cline-rules/default-rules.md)"
        assert ".cline-rules/default-rules.md" in adapter.file_patterns

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
            targets=["cline"],
        )
        errors = adapter.validate(prompt)
        assert len(errors) == 1
        assert errors[0].field == "instructions.general"

    def test_build_content(self, adapter, sample_prompt):
        """Test content generation."""
        content = adapter._build_content(sample_prompt)

        assert sample_prompt.metadata.title in content
        assert "## Project Overview" in content
        assert "## Coding Guidelines" in content
        assert sample_prompt.metadata.description in content

    @patch("builtins.open", new_callable=mock_open)
    @patch("pathlib.Path.mkdir")
    def test_generate_single_file(
        self, mock_mkdir, mock_file, adapter, sample_prompt
    ):
        """Test generation of single rules file."""
        output_dir = Path("/tmp/test")
        files = adapter.generate(sample_prompt, output_dir, dry_run=False)

        assert len(files) == 1
        assert output_dir / ".cline-rules" / "default-rules.md" in files
        
        # Verify directory creation was called
        mock_mkdir.assert_called_once()
        
        # Verify file was written
        mock_file.assert_called_once()
