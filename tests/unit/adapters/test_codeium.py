"""
Unit tests for Codeium adapter.
"""

import json
from pathlib import Path
from unittest.mock import mock_open, patch

import pytest

from src.apm.adapters.codeium import CodeiumAdapter
from src.apm.core.models import PromptMetadata, UniversalPrompt

from .base_test import TestAdapterBase


class TestCodeiumAdapter(TestAdapterBase):
    """Test Codeium adapter."""

    @pytest.fixture
    def adapter(self):
        """Create Codeium adapter instance."""
        return CodeiumAdapter()

    def test_init(self, adapter):
        """Test adapter initialization."""
        assert adapter.name == "codeium"
        assert adapter.description == "Codeium (context-based)"
        assert ".codeium/context.json" in adapter.file_patterns
        assert ".codeiumrc" in adapter.file_patterns

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
            targets=["codeium"],
        )
        errors = adapter.validate(prompt)
        assert len(errors) == 1
        assert getattr(errors[0], "severity", "error") == "warning"

    def test_build_context_json(self, adapter, sample_prompt):
        """Test JSON context generation."""
        content = adapter._build_context_json(sample_prompt)
        context = json.loads(content)

        assert context["project"]["name"] == sample_prompt.metadata.title
        assert context["project"]["technologies"] == sample_prompt.context.technologies
        assert len(context["guidelines"]) > 0
        assert len(context["patterns"]) > 0
        assert "preferences" in context

    def test_build_rc_file(self, adapter, sample_prompt):
        """Test RC file generation."""
        content = adapter._build_rc_file(sample_prompt)

        assert sample_prompt.metadata.title in content
        assert "[settings]" in content
        assert "[languages]" in content
        assert "[style]" in content
        assert "[context]" in content
        assert "typescript_enabled=true" in content
        assert "react_enabled=true" in content

    @patch("builtins.open", new_callable=mock_open)
    @patch("pathlib.Path.mkdir")
    def test_generate_multiple_files(
        self, mock_mkdir, mock_file, adapter, sample_prompt
    ):
        """Test generation of multiple files."""
        output_dir = Path("/tmp/test")
        files = adapter.generate(sample_prompt, output_dir, dry_run=False)

        assert len(files) == 2
        assert output_dir / ".codeium" / "context.json" in files
        assert output_dir / ".codeiumrc" in files
