"""
Unit tests for Claude adapter.
"""

import pytest

from src.apm.adapters.claude import ClaudeAdapter
from src.apm.core.models import PromptMetadata, UniversalPrompt

from .base_test import TestAdapterBase


class TestClaudeAdapter(TestAdapterBase):
    """Test Claude adapter."""

    @pytest.fixture
    def adapter(self):
        """Create Claude adapter instance."""
        return ClaudeAdapter()

    def test_init(self, adapter):
        """Test adapter initialization."""
        assert adapter.name == "claude"
        assert adapter.description == "Claude Code (context-based)"
        assert ".claude/context.md" in adapter.file_patterns

    def test_supports_features(self, adapter):
        """Test feature support."""
        assert adapter.supports_variables() is True
        assert adapter.supports_conditionals() is True

    def test_validate_with_context(self, adapter, sample_prompt):
        """Test validation with context."""
        errors = adapter.validate(sample_prompt)
        # Should only have warnings, not errors
        warning_errors = [
            e for e in errors if getattr(e, "severity", "error") == "warning"
        ]
        assert len(warning_errors) == 0  # Has context and examples

    def test_validate_missing_context(self, adapter):
        """Test validation with missing context."""
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
            targets=["claude"],
        )
        errors = adapter.validate(prompt)
        assert len(errors) == 2  # Missing context and examples warnings

    def test_build_content(self, adapter, sample_prompt):
        """Test content generation."""
        content = adapter._build_content(sample_prompt)

        assert sample_prompt.metadata.title in content
        assert sample_prompt.metadata.description in content
        assert "## Project Details" in content
        assert "## Development Guidelines" in content
        assert "## Code Examples" in content
        assert "typescript, react, nodejs" in content
