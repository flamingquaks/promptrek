"""Unit tests for core models."""

import pytest
from pydantic import ValidationError

from src.promptrek.core.models import Instructions, PromptMetadata, UniversalPrompt


class TestPromptMetadata:
    """Test PromptMetadata model."""

    def test_valid_metadata(self):
        """Test valid metadata creation."""
        metadata = PromptMetadata(
            title="Test Title",
            description="Test description",
            version="1.0.0",
            author="Test Author",
            created="2024-01-01",
            updated="2024-01-01",
        )
        assert metadata.title == "Test Title"
        assert metadata.version == "1.0.0"

    def test_invalid_date_format(self):
        """Test invalid date format raises validation error."""
        with pytest.raises(ValidationError):
            PromptMetadata(
                title="Test Title",
                description="Test description",
                version="1.0.0",
                author="Test Author",
                created="invalid-date",
                updated="2024-01-01",
            )


class TestUniversalPrompt:
    """Test UniversalPrompt model."""

    def test_valid_prompt(self, sample_upf_data):
        """Test valid prompt creation."""
        prompt = UniversalPrompt(**sample_upf_data)
        assert prompt.schema_version == "1.0.0"
        assert prompt.metadata.title == "Test Project Assistant"
        assert len(prompt.targets) == 2

    def test_invalid_schema_version(self, sample_upf_data):
        """Test invalid schema version format."""
        sample_upf_data["schema_version"] = "1.0"  # Missing patch version
        with pytest.raises(ValidationError):
            UniversalPrompt(**sample_upf_data)

    def test_empty_targets(self, sample_upf_data):
        """Test empty targets list raises validation error."""
        sample_upf_data["targets"] = []
        with pytest.raises(ValidationError):
            UniversalPrompt(**sample_upf_data)

    def test_missing_required_fields(self):
        """Test missing required fields raises validation error."""
        with pytest.raises(ValidationError):
            UniversalPrompt()

    def test_optional_fields_default_to_none(self):
        """Test optional fields default to None."""
        minimal_data = {
            "schema_version": "1.0.0",
            "metadata": {
                "title": "Test",
                "description": "Test description",
                "version": "1.0.0",
                "author": "Test Author",
                "created": "2024-01-01",
                "updated": "2024-01-01",
            },
            "targets": ["copilot"],
        }
        prompt = UniversalPrompt(**minimal_data)
        assert prompt.context is None
        assert prompt.instructions is None
        assert prompt.examples is None


class TestInstructions:
    """Test Instructions model."""

    def test_custom_categories_allowed(self):
        """Test that custom instruction categories are allowed."""
        instructions_data = {
            "general": ["Write clean code"],
            "custom_category": ["Custom instruction"],
        }
        instructions = Instructions(**instructions_data)
        assert instructions.general == ["Write clean code"]
        # Custom categories should be accessible via getattr
        assert hasattr(instructions, "custom_category")
        assert getattr(instructions, "custom_category") == ["Custom instruction"]
