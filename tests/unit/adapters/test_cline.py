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
        assert adapter.description == "Cline (terminal-based)"
        assert ".cline/config.json" in adapter.file_patterns
        assert "cline-context.md" in adapter.file_patterns

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

    def test_build_config(self, adapter, sample_prompt):
        """Test configuration generation."""
        config_content = adapter._build_config(sample_prompt)
        config = json.loads(config_content)

        assert config["name"] == sample_prompt.metadata.title
        assert config["description"] == sample_prompt.metadata.description
        assert config["contextFile"] == "cline-context.md"
        assert "settings" in config
        assert "project" in config

    def test_build_context(self, adapter, sample_prompt):
        """Test context generation."""
        content = adapter._build_context(sample_prompt)

        assert sample_prompt.metadata.title in content
        assert "## Project Information" in content
        assert "## Development Instructions" in content
        assert "## Terminal Operations" in content
        assert "typescript, react, nodejs" in content

    @patch("builtins.open", new_callable=mock_open)
    @patch("pathlib.Path.mkdir")
    def test_generate_multiple_files(
        self, mock_mkdir, mock_file, adapter, sample_prompt
    ):
        """Test generation of multiple files."""
        output_dir = Path("/tmp/test")
        files = adapter.generate(sample_prompt, output_dir, dry_run=False)

        assert len(files) == 2
        assert output_dir / ".cline" / "config.json" in files
        assert output_dir / "cline-context.md" in files
