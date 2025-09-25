"""
Unit tests for Amazon Q adapter.
"""

from pathlib import Path

import pytest

from src.promptrek.adapters.amazon_q import AmazonQAdapter
from src.promptrek.core.models import PromptMetadata, UniversalPrompt


class TestAmazonQAdapter:
    """Test Amazon Q adapter."""

    @pytest.fixture
    def adapter(self):
        """Create Amazon Q adapter instance."""
        return AmazonQAdapter()

    @pytest.fixture
    def sample_prompt(self):
        """Create sample prompt for testing."""
        return UniversalPrompt(
            schema_version="1.0.0",
            metadata=PromptMetadata(
                title="Test Project",
                description="A test project",
                version="1.0.0",
                author="test@example.com",
                created="2024-01-01",
                updated="2024-01-01",
            ),
            targets=["amazon-q"],
        )

    def test_init(self, adapter):
        """Test adapter initialization."""
        assert adapter.name == "amazon-q"
        assert "Amazon Q" in adapter.description

    def test_supports_variables(self, adapter):
        """Test variable support."""
        assert adapter.supports_variables() is True

    def test_supports_conditionals(self, adapter):
        """Test conditional support."""
        assert adapter.supports_conditionals() is True

    def test_generate_creates_files(self, adapter, sample_prompt):
        """Test that adapter generates files in dry run mode."""
        files = adapter.generate(sample_prompt, Path("/tmp"), dry_run=True)
        assert len(files) >= 1
        assert any(".amazonq" in str(f) for f in files)