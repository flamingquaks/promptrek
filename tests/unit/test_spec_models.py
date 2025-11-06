"""Tests for Universal Spec Format (USF) models."""

import pytest
from pydantic import ValidationError

from promptrek.core.models import SpecMetadata, UniversalSpecFormat


class TestSpecMetadata:
    """Tests for SpecMetadata model."""

    def test_valid_spec_metadata(self):
        """Test creating valid spec metadata."""
        metadata = SpecMetadata(
            id="abc123",
            title="Test Specification",
            path="test-spec.md",
            source_command="/promptrek.spec.create",
            created="2025-11-05T10:00:00",
        )

        assert metadata.id == "abc123"
        assert metadata.title == "Test Specification"
        assert metadata.path == "test-spec.md"
        assert metadata.source_command == "/promptrek.spec.create"
        assert metadata.created == "2025-11-05T10:00:00"
        assert metadata.updated is None
        assert metadata.summary is None
        assert metadata.linked_specs is None
        assert metadata.tags is None

    def test_spec_metadata_with_optional_fields(self):
        """Test spec metadata with all optional fields."""
        metadata = SpecMetadata(
            id="xyz789",
            title="Complete Spec",
            path="complete-spec.md",
            source_command="/promptrek.spec.plan",
            created="2025-11-05T10:00:00",
            updated="2025-11-05T12:00:00",
            summary="A complete specification",
            linked_specs=["abc123", "def456"],
            tags=["api", "auth", "oauth"],
        )

        assert metadata.updated == "2025-11-05T12:00:00"
        assert metadata.summary == "A complete specification"
        assert metadata.linked_specs == ["abc123", "def456"]
        assert metadata.tags == ["api", "auth", "oauth"]

    def test_spec_metadata_timestamp_validation(self):
        """Test timestamp validation for created and updated fields."""
        # Valid ISO 8601 timestamps
        metadata = SpecMetadata(
            id="test1",
            title="Test",
            path="test.md",
            source_command="/test",
            created="2025-11-05T10:00:00",
            updated="2025-11-05T12:00:00.123456",
        )
        assert metadata.created == "2025-11-05T10:00:00"
        assert metadata.updated == "2025-11-05T12:00:00.123456"

        # Invalid timestamp for created
        with pytest.raises(ValidationError) as exc_info:
            SpecMetadata(
                id="test2",
                title="Test",
                path="test.md",
                source_command="/test",
                created="invalid-date",
            )
        assert "Timestamp must be in ISO 8601 format" in str(exc_info.value)

        # Invalid timestamp for updated
        with pytest.raises(ValidationError) as exc_info:
            SpecMetadata(
                id="test3",
                title="Test",
                path="test.md",
                source_command="/test",
                created="2025-11-05T10:00:00",
                updated="11/05/2025",
            )
        assert "Timestamp must be in ISO 8601 format" in str(exc_info.value)

    def test_spec_metadata_required_fields(self):
        """Test that required fields are enforced."""
        # Missing id
        with pytest.raises(ValidationError):
            SpecMetadata(
                title="Test",
                path="test.md",
                source_command="/test",
                created="2025-11-05T10:00:00",
            )

        # Missing title
        with pytest.raises(ValidationError):
            SpecMetadata(
                id="test",
                path="test.md",
                source_command="/test",
                created="2025-11-05T10:00:00",
            )

        # Missing path
        with pytest.raises(ValidationError):
            SpecMetadata(
                id="test",
                title="Test",
                source_command="/test",
                created="2025-11-05T10:00:00",
            )

        # Missing source_command
        with pytest.raises(ValidationError):
            SpecMetadata(
                id="test",
                title="Test",
                path="test.md",
                created="2025-11-05T10:00:00",
            )

        # Missing created
        with pytest.raises(ValidationError):
            SpecMetadata(
                id="test",
                title="Test",
                path="test.md",
                source_command="/test",
            )

    def test_spec_metadata_no_extra_fields(self):
        """Test that extra fields are not allowed."""
        with pytest.raises(ValidationError):
            SpecMetadata(
                id="test",
                title="Test",
                path="test.md",
                source_command="/test",
                created="2025-11-05T10:00:00",
                extra_field="not allowed",
            )


class TestUniversalSpecFormat:
    """Tests for UniversalSpecFormat model."""

    def test_valid_usf_empty(self):
        """Test creating valid USF with no specs."""
        usf = UniversalSpecFormat(schema_version="1.0.0", specs=[])

        assert usf.schema_version == "1.0.0"
        assert usf.specs == []

    def test_usf_default_values(self):
        """Test USF defaults."""
        usf = UniversalSpecFormat()

        assert usf.schema_version == "1.0.0"
        assert usf.specs == []

    def test_usf_with_specs(self):
        """Test USF with multiple specs."""
        spec1 = SpecMetadata(
            id="spec1",
            title="Spec 1",
            path="spec1.md",
            source_command="/promptrek.spec.create",
            created="2025-11-05T10:00:00",
        )
        spec2 = SpecMetadata(
            id="spec2",
            title="Spec 2",
            path="spec2.md",
            source_command="/promptrek.spec.plan",
            created="2025-11-05T11:00:00",
            linked_specs=["spec1"],
        )

        usf = UniversalSpecFormat(
            schema_version="1.0.0",
            specs=[spec1, spec2],
        )

        assert len(usf.specs) == 2
        assert usf.specs[0].id == "spec1"
        assert usf.specs[1].id == "spec2"
        assert usf.specs[1].linked_specs == ["spec1"]

    def test_usf_schema_version_validation(self):
        """Test schema version validation."""
        # Valid versions
        usf1 = UniversalSpecFormat(schema_version="1.0.0")
        assert usf1.schema_version == "1.0.0"

        usf2 = UniversalSpecFormat(schema_version="2.1.3")
        assert usf2.schema_version == "2.1.3"

        # Invalid version (not x.y.z format - missing dots)
        with pytest.raises(ValidationError) as exc_info:
            UniversalSpecFormat(schema_version="1.0")
        assert "Schema version must be in format 'x.y.z'" in str(exc_info.value)

        # Too many dots
        with pytest.raises(ValidationError) as exc_info:
            UniversalSpecFormat(schema_version="1.0.0.0")
        assert "Schema version must be in format 'x.y.z'" in str(exc_info.value)

    def test_usf_serialization(self):
        """Test USF model serialization."""
        spec = SpecMetadata(
            id="test",
            title="Test Spec",
            path="test.md",
            source_command="/promptrek.spec.create",
            created="2025-11-05T10:00:00",
            tags=["test", "example"],
        )
        usf = UniversalSpecFormat(
            schema_version="1.0.0",
            specs=[spec],
        )

        data = usf.model_dump(exclude_none=True)

        assert data["schema_version"] == "1.0.0"
        assert len(data["specs"]) == 1
        assert data["specs"][0]["id"] == "test"
        assert data["specs"][0]["title"] == "Test Spec"
        assert data["specs"][0]["tags"] == ["test", "example"]
        # None values should be excluded
        assert "updated" not in data["specs"][0]
        assert "summary" not in data["specs"][0]
        assert "linked_specs" not in data["specs"][0]
