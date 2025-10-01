"""
Unit tests for Windsurf adapter.
"""

from pathlib import Path
from unittest.mock import mock_open, patch

import pytest

from promptrek.adapters.windsurf import WindsurfAdapter
from promptrek.core.models import PromptMetadata, UniversalPrompt

from .base_test import TestAdapterBase


class TestWindsurfAdapter(TestAdapterBase):
    """Test Windsurf adapter."""

    @pytest.fixture
    def adapter(self):
        """Create Windsurf adapter instance."""
        return WindsurfAdapter()

    def test_init(self, adapter):
        """Test adapter initialization."""
        assert adapter.name == "windsurf"
        assert adapter.description == "Windsurf (.windsurf/rules/)"
        assert ".windsurf/rules/*.md" in adapter.file_patterns

    def test_supports_features(self, adapter):
        """Test feature support."""
        assert adapter.supports_variables() is True
        assert adapter.supports_conditionals() is True

    def test_validate_with_instructions(self, adapter, sample_prompt):
        """Test validation with instructions."""
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
            targets=["windsurf"],
        )
        errors = adapter.validate(prompt)
        assert len(errors) == 1
        assert getattr(errors[0], "severity", "error") == "warning"

    def test_build_rules_content(self, adapter):
        """Test markdown rules content generation."""
        instructions = ["Follow best practices", "Write clean code"]
        content = adapter._build_rules_content("General Rules", instructions)

        assert "# General Rules" in content
        assert "- Follow best practices" in content
        assert "- Write clean code" in content
        assert "## Additional Guidelines" in content

    def test_build_tech_rules_content(self, adapter, sample_prompt):
        """Test technology-specific rules content generation."""
        content = adapter._build_tech_rules_content("python", sample_prompt)

        assert "# Python Rules" in content
        assert "## General Guidelines" in content
        assert "## Python Best Practices" in content
        assert "Follow PEP 8 style guidelines" in content

    @patch("builtins.open", new_callable=mock_open)
    @patch("pathlib.Path.mkdir")
    def test_generate_multiple_files(
        self, mock_mkdir, mock_file, adapter, sample_prompt
    ):
        """Test generation of multiple markdown rule files."""
        output_dir = Path("/tmp/test")
        files = adapter.generate(sample_prompt, output_dir, dry_run=False)

        assert len(files) > 0
        # Should generate general, code-style, testing, and tech-specific rules
        file_names = [f.name for f in files]
        assert "general.md" in file_names
        assert "code-style.md" in file_names
