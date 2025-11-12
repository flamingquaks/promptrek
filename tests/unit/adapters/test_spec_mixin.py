"""
Unit tests for SpecInclusionMixin.
"""

import pytest

from promptrek.adapters.spec_mixin import SpecInclusionMixin
from promptrek.core.models import (
    PromptMetadata,
    UniversalPrompt,
    UniversalPromptV2,
    UniversalPromptV3,
)


class TestSpecInclusionMixin:
    """Test SpecInclusionMixin functionality."""

    @pytest.fixture
    def mixin(self):
        """Create SpecInclusionMixin instance."""
        return SpecInclusionMixin()

    @pytest.fixture
    def v3_prompt_with_specs(self):
        """Create v3.1.0 prompt with specs enabled."""
        return UniversalPromptV3(
            schema_version="3.1.0",
            metadata=PromptMetadata(
                title="Test",
                description="Test",
                created="2024-01-01",
                updated="2024-01-01",
                version="1.0.0",
                author="test@example.com",
            ),
            content="# Test content",
            include_specs=True,
        )

    @pytest.fixture
    def v3_prompt_without_specs(self):
        """Create v3.1.0 prompt with specs disabled."""
        return UniversalPromptV3(
            schema_version="3.1.0",
            metadata=PromptMetadata(
                title="Test",
                description="Test",
                created="2024-01-01",
                updated="2024-01-01",
                version="1.0.0",
                author="test@example.com",
            ),
            content="# Test content",
            include_specs=False,
        )

    @pytest.fixture
    def v3_0_prompt(self):
        """Create v3.0.0 prompt (no spec support)."""
        return UniversalPromptV3(
            schema_version="3.0.0",
            metadata=PromptMetadata(
                title="Test",
                description="Test",
                created="2024-01-01",
                updated="2024-01-01",
                version="1.0.0",
                author="test@example.com",
            ),
            content="# Test content",
        )

    @pytest.fixture
    def v2_prompt(self):
        """Create v2 prompt (no spec support)."""
        return UniversalPromptV2(
            schema_version="2.0.0",
            metadata=PromptMetadata(
                title="Test",
                description="Test",
                created="2024-01-01",
                updated="2024-01-01",
                version="1.0.0",
                author="test@example.com",
            ),
            content="# Test content",
        )

    @pytest.fixture
    def v1_prompt(self):
        """Create v1 prompt (no spec support)."""
        return UniversalPrompt(
            schema_version="1.0.0",
            metadata=PromptMetadata(
                title="Test",
                description="Test",
                created="2024-01-01",
                updated="2024-01-01",
                version="1.0.0",
                author="test@example.com",
            ),
            targets=["claude"],
        )

    @pytest.fixture
    def spec_dir_with_specs(self, tmp_path):
        """Create spec directory with sample spec files using SpecManager."""
        from promptrek.utils.spec_manager import SpecManager

        spec_manager = SpecManager(tmp_path)

        # Create specs using SpecManager to ensure proper registry
        spec_manager.create_spec(
            title="Test Spec 1",
            content="# Authentication Specification\n\nThis spec defines authentication requirements.\n\n## Requirements\n- OAuth 2.0 support\n- JWT tokens",
            summary="Test spec for authentication",
            tags=["api", "auth"],
            source_command="spec",
        )

        spec_manager.create_spec(
            title="Test Spec 2",
            content="# Database Schema\n\nThis spec defines the database schema.\n\n## Tables\n- users\n- sessions",
            summary="Database schema design",
            tags=["database", "schema"],
            source_command="spec",
        )

        return tmp_path

    def test_should_include_specs_v3_1_enabled(self, mixin, v3_prompt_with_specs):
        """Test that specs are included for v3.1.0+ with include_specs=True."""
        assert mixin.should_include_specs(v3_prompt_with_specs) is True

    def test_should_include_specs_v3_1_disabled(self, mixin, v3_prompt_without_specs):
        """Test that specs are not included when include_specs=False."""
        assert mixin.should_include_specs(v3_prompt_without_specs) is False

    def test_should_include_specs_v3_0(self, mixin, v3_0_prompt):
        """Test that specs are not included for v3.0.0."""
        assert mixin.should_include_specs(v3_0_prompt) is False

    def test_should_include_specs_v2(self, mixin, v2_prompt):
        """Test that specs are not included for v2 prompts."""
        assert mixin.should_include_specs(v2_prompt) is False

    def test_should_include_specs_v1(self, mixin, v1_prompt):
        """Test that specs are not included for v1 prompts."""
        assert mixin.should_include_specs(v1_prompt) is False

    def test_should_include_specs_v3_2(self, mixin):
        """Test that specs are included for v3.2.0+ (future versions)."""
        prompt = UniversalPromptV3(
            schema_version="3.2.0",
            metadata=PromptMetadata(
                title="Test",
                description="Test",
                created="2024-01-01",
                updated="2024-01-01",
                version="1.0.0",
                author="test@example.com",
            ),
            content="# Test content",
            include_specs=True,
        )
        assert mixin.should_include_specs(prompt) is True

    def test_should_include_specs_v3_5(self, mixin):
        """Test that specs are included for v3.5+ (future minor versions)."""
        prompt = UniversalPromptV3(
            schema_version="3.5.0",
            metadata=PromptMetadata(
                title="Test",
                description="Test",
                created="2024-01-01",
                updated="2024-01-01",
                version="1.0.0",
                author="test@example.com",
            ),
            content="# Test content",
            include_specs=True,
        )
        assert mixin.should_include_specs(prompt) is True

    def test_should_include_specs_default_value(self, mixin):
        """Test that include_specs defaults to True for v3.1+."""
        prompt = UniversalPromptV3(
            schema_version="3.1.0",
            metadata=PromptMetadata(
                title="Test",
                description="Test",
                created="2024-01-01",
                updated="2024-01-01",
                version="1.0.0",
                author="test@example.com",
            ),
            content="# Test content",
            # include_specs not explicitly set (should default to True)
        )
        assert mixin.should_include_specs(prompt) is True

    def test_get_spec_documents_with_specs(self, mixin, spec_dir_with_specs):
        """Test retrieving spec documents from directory."""
        spec_docs = mixin.get_spec_documents(spec_dir_with_specs)

        assert len(spec_docs) == 2

        # Check that both specs have required fields
        for spec in spec_docs:
            assert "id" in spec
            assert "title" in spec
            assert "summary" in spec
            assert "content" in spec
            assert "tags" in spec

        # Check first spec by title
        spec1 = next((s for s in spec_docs if s["title"] == "Test Spec 1"), None)
        assert spec1 is not None
        assert spec1["summary"] == "Test spec for authentication"
        assert "api" in spec1["tags"]
        assert "auth" in spec1["tags"]
        assert "Authentication Specification" in spec1["content"]

        # Check second spec by title
        spec2 = next((s for s in spec_docs if s["title"] == "Test Spec 2"), None)
        assert spec2 is not None
        assert spec2["summary"] == "Database schema design"
        assert "database" in spec2["tags"]
        assert "schema" in spec2["tags"]

    def test_get_spec_documents_no_specs_dir(self, mixin, tmp_path):
        """Test retrieving spec documents when directory doesn't exist."""
        spec_docs = mixin.get_spec_documents(tmp_path)
        assert spec_docs == []

    def test_get_spec_documents_empty_dir(self, mixin, tmp_path):
        """Test retrieving spec documents from empty directory."""
        specs_dir = tmp_path / "promptrek" / "specs"
        specs_dir.mkdir(parents=True)

        spec_docs = mixin.get_spec_documents(tmp_path)
        assert spec_docs == []

    def test_format_spec_as_document_frontmatter(self, mixin, spec_dir_with_specs):
        """Test formatting spec with YAML frontmatter."""
        spec_docs = mixin.get_spec_documents(spec_dir_with_specs)
        assert len(spec_docs) > 0

        spec_doc = spec_docs[0]
        filename, content = mixin.format_spec_as_document_frontmatter(spec_doc)

        assert filename.startswith("spec-")
        assert filename.endswith(".md")
        assert "---" in content
        # Format uses "name:" not "title:"
        assert "name:" in content
        assert spec_doc["title"] in content
        # Content should be included after frontmatter
        assert "Authentication Specification" in content or "Database Schema" in content

    def test_format_spec_as_document_frontmatter_structure(self, mixin):
        """Test formatting spec structure."""
        spec_doc = {
            "id": "test123",
            "title": "Test Spec",
            "summary": "Test summary",
            "tags": ["api"],
            "content": "# Test\n\nContent",
        }

        filename, content = mixin.format_spec_as_document_frontmatter(spec_doc)

        assert filename == "spec-test123.md"
        assert content.startswith("---")
        parts = content.split("---")
        assert len(parts) >= 3  # Start ---, frontmatter, end ---, content

    def test_format_spec_references_section_with_specs(
        self, mixin, spec_dir_with_specs
    ):
        """Test formatting spec references section."""
        spec_docs = mixin.get_spec_documents(spec_dir_with_specs)

        section = mixin.format_spec_references_section(spec_docs)

        assert section is not None
        assert "## Project Specifications" in section
        # Should contain spec titles
        assert "Test Spec 1" in section or "Test Spec 2" in section
        # Should contain path references
        assert "**Path:**" in section

    def test_format_spec_references_section_empty(self, mixin):
        """Test formatting spec references with no specs."""
        section = mixin.format_spec_references_section([])
        assert section is None

    def test_format_spec_references_section_no_summary(self, mixin):
        """Test formatting spec references without summaries."""
        spec_docs = [
            {
                "id": "abc123",
                "title": "Test Spec",
                "summary": "",  # Empty string instead of None
                "path": "promptrek/specs/test.md",
                "tags": [],
                "content": "# Test\n\nSome content here.",
            }
        ]

        section = mixin.format_spec_references_section(spec_docs)

        assert section is not None
        assert "### Test Spec" in section
        assert "abc123" in section
        # Summary line should not appear for empty summary
        lines = section.split("\n")
        assert not any("**Summary:**" in line for line in lines)

    def test_spec_metadata_fields_complete(self, mixin, spec_dir_with_specs):
        """Test that spec documents have all required fields."""
        spec_docs = mixin.get_spec_documents(spec_dir_with_specs)

        assert len(spec_docs) == 2

        for spec in spec_docs:
            # Verify all required fields are present
            assert "id" in spec
            assert "title" in spec
            assert "summary" in spec
            assert "content" in spec
            assert "tags" in spec
            assert "path" in spec

            # Verify field types
            assert isinstance(spec["id"], str)
            assert isinstance(spec["title"], str)
            assert isinstance(spec["summary"], str)
            assert isinstance(spec["content"], str)
            assert isinstance(spec["tags"], list)

    def test_spec_content_retrieval(self, mixin, spec_dir_with_specs):
        """Test that spec content is properly retrieved."""
        spec_docs = mixin.get_spec_documents(spec_dir_with_specs)

        assert len(spec_docs) > 0

        # Check that content is not empty
        for spec in spec_docs:
            assert len(spec["content"]) > 0
            # Content should be markdown with USF format
            assert "#" in spec["content"]
