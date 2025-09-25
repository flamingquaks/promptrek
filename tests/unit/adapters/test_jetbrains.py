"""
Unit tests for JetBrains adapter.
"""

from pathlib import Path

import pytest

from src.promptrek.adapters.jetbrains import JetBrainsAdapter
from src.promptrek.core.models import PromptMetadata, UniversalPrompt


class TestJetBrainsAdapter:
    """Test JetBrains adapter."""

    @pytest.fixture
    def adapter(self):
        """Create JetBrains adapter instance."""
        return JetBrainsAdapter()

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
            targets=["jetbrains"],
        )

    def test_init(self, adapter):
        """Test adapter initialization."""
        assert adapter.name == "jetbrains"
        assert "JetBrains" in adapter.description

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
        assert any(".idea" in str(f) or ".jetbrains" in str(f) for f in files)