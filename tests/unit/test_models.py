"""Unit tests for core models."""

import pytest
from pydantic import ValidationError

from promptrek.core.models import (
    DocumentConfig,
    Instructions,
    PromptMetadata,
    UniversalPrompt,
    UniversalPromptV2,
)


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

    def test_optional_dates(self):
        """Test metadata can be created without dates."""
        metadata = PromptMetadata(
            title="Test Title",
            description="Test description",
            version="1.0.0",
            author="Test Author",
        )
        assert metadata.created is None
        assert metadata.updated is None
        assert metadata.title == "Test Title"

    def test_partial_dates(self):
        """Test metadata can have only one date field."""
        metadata = PromptMetadata(
            title="Test Title",
            description="Test description",
            version="1.0.0",
            author="Test Author",
            created="2024-01-01",
        )
        assert metadata.created == "2024-01-01"
        assert metadata.updated is None


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

    def test_metadata_without_dates(self):
        """Test UniversalPrompt works with metadata that has no dates."""
        minimal_data = {
            "schema_version": "1.0.0",
            "metadata": {
                "title": "Test Without Dates",
                "description": "Test description",
                "version": "1.0.0",
                "author": "Test Author",
            },
            "targets": ["copilot"],
        }
        prompt = UniversalPrompt(**minimal_data)
        assert prompt.metadata.created is None
        assert prompt.metadata.updated is None
        assert prompt.metadata.title == "Test Without Dates"


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


class TestDocumentConfig:
    """Test DocumentConfig model (v2 schema)."""

    def test_valid_document(self):
        """Test valid document creation."""
        doc = DocumentConfig(
            name="general-rules",
            content="# General Rules\n\n- Write clean code\n- Follow best practices",
        )
        assert doc.name == "general-rules"
        assert "Write clean code" in doc.content

    def test_document_with_markdown(self):
        """Test document with complex markdown content."""
        markdown_content = """# Project Guidelines

## Code Style
- Use meaningful variable names
- Follow PEP 8 for Python

## Testing
- Write unit tests for all functions
- Aim for 80% coverage

## Examples

### Function Example
```python
def example():
    pass
```
"""
        doc = DocumentConfig(name="guidelines", content=markdown_content)
        assert doc.name == "guidelines"
        assert "## Code Style" in doc.content
        assert "```python" in doc.content

    def test_missing_required_fields(self):
        """Test missing required fields raises validation error."""
        with pytest.raises(ValidationError):
            DocumentConfig(name="test")  # Missing content

        with pytest.raises(ValidationError):
            DocumentConfig(content="test content")  # Missing name


class TestUniversalPromptV2:
    """Test UniversalPromptV2 model (v2 schema)."""

    def test_valid_v2_prompt(self):
        """Test valid v2 prompt creation."""
        prompt = UniversalPromptV2(
            schema_version="2.0.0",
            metadata=PromptMetadata(
                title="My Project",
                description="Test project",
                version="1.0.0",
                author="Test Author",
                created="2024-01-01",
                updated="2024-01-01",
                tags=["test", "v2"],
            ),
            content="# My Project\n\n## Guidelines\n- Write clean code",
            variables={"PROJECT_NAME": "MyProject"},
        )
        assert prompt.schema_version == "2.0.0"
        assert prompt.metadata.title == "My Project"
        assert "Write clean code" in prompt.content
        assert prompt.variables["PROJECT_NAME"] == "MyProject"

    def test_v2_prompt_with_documents(self):
        """Test v2 prompt with multiple documents."""
        prompt = UniversalPromptV2(
            schema_version="2.0.0",
            metadata=PromptMetadata(
                title="Multi-Document Project",
                description="Test with documents",
                version="1.0.0",
                author="Test Author",
            ),
            content="# Main Content\n\nThis is the main content.",
            documents=[
                DocumentConfig(
                    name="general", content="# General Rules\n- Rule 1\n- Rule 2"
                ),
                DocumentConfig(
                    name="code-style", content="# Code Style\n- Style 1\n- Style 2"
                ),
            ],
        )
        assert len(prompt.documents) == 2
        assert prompt.documents[0].name == "general"
        assert prompt.documents[1].name == "code-style"

    def test_v2_prompt_minimal(self):
        """Test minimal v2 prompt (only required fields)."""
        prompt = UniversalPromptV2(
            schema_version="2.0.0",
            metadata=PromptMetadata(
                title="Minimal",
                description="Minimal test",
                version="1.0.0",
                author="Test",
            ),
            content="# Minimal content",
        )
        assert prompt.schema_version == "2.0.0"
        assert prompt.documents is None
        assert prompt.variables is None

    def test_v2_invalid_schema_version(self):
        """Test v2 prompt with invalid schema version."""
        with pytest.raises(ValidationError):
            UniversalPromptV2(
                schema_version="1.0.0",  # Should be 2.0.0
                metadata=PromptMetadata(
                    title="Test",
                    description="Test",
                    version="1.0.0",
                    author="Test",
                ),
                content="# Content",
            )

    def test_v2_missing_content(self):
        """Test v2 prompt without content raises error."""
        with pytest.raises(ValidationError):
            UniversalPromptV2(
                schema_version="2.0.0",
                metadata=PromptMetadata(
                    title="Test",
                    description="Test",
                    version="1.0.0",
                    author="Test",
                ),
            )

    def test_v2_no_targets_field(self):
        """Test v2 prompt does not have targets field."""
        prompt = UniversalPromptV2(
            schema_version="2.0.0",
            metadata=PromptMetadata(
                title="Test",
                description="Test",
                version="1.0.0",
                author="Test",
            ),
            content="# Content",
        )
        assert not hasattr(prompt, "targets")

    def test_v2_with_variable_placeholders(self):
        """Test v2 content with variable placeholders."""
        prompt = UniversalPromptV2(
            schema_version="2.0.0",
            metadata=PromptMetadata(
                title="{{{ PROJECT_TITLE }}}",
                description="Project for {{{ COMPANY }}}",
                version="1.0.0",
                author="Test",
            ),
            content="""# {{{ PROJECT_TITLE }}}

This project uses {{{ TECHNOLOGY }}} for {{{ PURPOSE }}}.

## Variables
- PROJECT_NAME: {{{ PROJECT_NAME }}}
""",
            variables={
                "PROJECT_TITLE": "My App",
                "COMPANY": "Acme Corp",
                "TECHNOLOGY": "Python",
                "PURPOSE": "data processing",
                "PROJECT_NAME": "my-app",
            },
        )
        assert "{{{ PROJECT_TITLE }}}" in prompt.content
        assert prompt.variables["TECHNOLOGY"] == "Python"
