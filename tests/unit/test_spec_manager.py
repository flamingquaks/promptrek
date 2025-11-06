"""Tests for SpecManager utility."""

import uuid
from datetime import datetime
from pathlib import Path

import pytest
import yaml

from promptrek.core.models import SpecMetadata, UniversalSpecFormat
from promptrek.utils.spec_manager import SpecManager


class TestSpecManagerInit:
    """Tests for SpecManager initialization."""

    def test_init(self, tmp_path):
        """Test SpecManager initialization."""
        manager = SpecManager(tmp_path)

        assert manager.project_root == tmp_path
        assert manager.specs_dir == tmp_path / ".promptrek" / "specs"
        assert manager.registry_path == tmp_path / ".promptrek" / "specs.yaml"

    def test_ensure_specs_directory(self, tmp_path):
        """Test creating specs directory."""
        manager = SpecManager(tmp_path)

        assert not manager.specs_dir.exists()

        manager.ensure_specs_directory()

        assert manager.specs_dir.exists()
        assert manager.specs_dir.is_dir()

    def test_ensure_specs_directory_idempotent(self, tmp_path):
        """Test that ensure_specs_directory is idempotent."""
        manager = SpecManager(tmp_path)

        manager.ensure_specs_directory()
        manager.ensure_specs_directory()  # Call twice

        assert manager.specs_dir.exists()


class TestSpecManagerRegistry:
    """Tests for registry loading and saving."""

    def test_load_registry_empty(self, tmp_path):
        """Test loading registry when file doesn't exist."""
        manager = SpecManager(tmp_path)

        usf = manager.load_registry()

        assert isinstance(usf, UniversalSpecFormat)
        assert usf.schema_version == "1.0.0"
        assert usf.specs == []

    def test_load_registry_with_data(self, tmp_path):
        """Test loading registry with existing data."""
        manager = SpecManager(tmp_path)
        manager.ensure_specs_directory()

        # Create a registry file manually
        registry_data = {
            "schema_version": "1.0.0",
            "specs": [
                {
                    "id": "test1",
                    "title": "Test Spec 1",
                    "path": "test1.md",
                    "source_command": "/promptrek.spec.create",
                    "created": "2025-11-05T10:00:00",
                }
            ],
        }

        with open(manager.registry_path, "w") as f:
            yaml.dump(registry_data, f)

        usf = manager.load_registry()

        assert usf.schema_version == "1.0.0"
        assert len(usf.specs) == 1
        assert usf.specs[0].id == "test1"
        assert usf.specs[0].title == "Test Spec 1"

    def test_load_registry_malformed_yaml(self, tmp_path):
        """Test loading registry with malformed YAML."""
        manager = SpecManager(tmp_path)
        manager.ensure_specs_directory()

        # Create malformed YAML
        with open(manager.registry_path, "w") as f:
            f.write("{ invalid yaml ][")

        with pytest.raises(ValueError) as exc_info:
            manager.load_registry()

        assert "Failed to parse specs.yaml" in str(exc_info.value)

    def test_load_registry_empty_file(self, tmp_path):
        """Test loading registry from empty file."""
        manager = SpecManager(tmp_path)
        manager.ensure_specs_directory()

        # Create empty file
        manager.registry_path.touch()

        usf = manager.load_registry()

        assert usf.schema_version == "1.0.0"
        assert usf.specs == []

    def test_save_registry(self, tmp_path):
        """Test saving registry."""
        manager = SpecManager(tmp_path)

        spec = SpecMetadata(
            id="test",
            title="Test Spec",
            path="test.md",
            source_command="/promptrek.spec.create",
            created="2025-11-05T10:00:00",
        )
        usf = UniversalSpecFormat(schema_version="1.0.0", specs=[spec])

        manager.save_registry(usf)

        assert manager.registry_path.exists()

        # Load and verify
        with open(manager.registry_path) as f:
            content = f.read()
            # Check for header comments
            assert "Universal Spec Format (USF) Registry" in content
            assert "do not edit manually" in content

            # Parse YAML (skip comments)
            f.seek(0)
            lines = [line for line in f if not line.strip().startswith("#")]
            data = yaml.safe_load("".join(lines))

        assert data["schema_version"] == "1.0.0"
        assert len(data["specs"]) == 1
        assert data["specs"][0]["id"] == "test"


class TestSpecManagerCreate:
    """Tests for creating specs."""

    def test_create_spec_basic(self, tmp_path):
        """Test creating a basic spec."""
        manager = SpecManager(tmp_path)

        spec = manager.create_spec(
            title="Test Specification",
            content="This is test content.",
            source_command="/promptrek.spec.create",
        )

        # Check metadata
        assert len(spec.id) == 8  # UUID prefix is 8 chars
        assert spec.title == "Test Specification"
        assert spec.source_command == "/promptrek.spec.create"
        assert spec.created is not None
        assert spec.path.endswith(".md")

        # Check file was created
        spec_file = manager.specs_dir / spec.path
        assert spec_file.exists()

        content = spec_file.read_text()
        assert "# Test Specification" in content
        assert f"**ID:** {spec.id}" in content
        assert "**Source:** /promptrek.spec.create" in content
        assert "This is test content." in content

        # Check registry was updated
        usf = manager.load_registry()
        assert len(usf.specs) == 1
        assert usf.specs[0].id == spec.id

    def test_create_spec_with_optional_fields(self, tmp_path):
        """Test creating spec with optional fields."""
        manager = SpecManager(tmp_path)

        spec = manager.create_spec(
            title="Complete Spec",
            content="Complete content.",
            source_command="/promptrek.spec.plan",
            summary="A test summary",
            tags=["test", "example"],
        )

        assert spec.summary == "A test summary"
        assert spec.tags == ["test", "example"]

        # Check file content
        spec_file = manager.specs_dir / spec.path
        content = spec_file.read_text()
        assert "**Summary:** A test summary" in content
        assert "**Tags:** test, example" in content

    def test_create_multiple_specs(self, tmp_path):
        """Test creating multiple specs."""
        manager = SpecManager(tmp_path)

        spec1 = manager.create_spec(
            title="Spec 1",
            content="Content 1",
            source_command="/promptrek.spec.create",
        )
        spec2 = manager.create_spec(
            title="Spec 2",
            content="Content 2",
            source_command="/promptrek.spec.create",
        )

        # Check both exist in registry
        usf = manager.load_registry()
        assert len(usf.specs) == 2

        ids = {s.id for s in usf.specs}
        assert spec1.id in ids
        assert spec2.id in ids


class TestSpecManagerUpdate:
    """Tests for updating specs."""

    def test_update_spec_content(self, tmp_path):
        """Test updating spec content."""
        manager = SpecManager(tmp_path)

        # Create initial spec
        spec = manager.create_spec(
            title="Original Title",
            content="Original content",
            source_command="/promptrek.spec.create",
        )

        # Update content
        updated = manager.update_spec(
            spec_id=spec.id,
            content="Updated content",
        )

        assert updated.id == spec.id
        assert updated.updated is not None

        # Check file was updated
        spec_file = manager.specs_dir / spec.path
        content = spec_file.read_text()
        assert "Updated content" in content
        assert "**Updated:**" in content

    def test_update_spec_metadata(self, tmp_path):
        """Test updating spec metadata."""
        manager = SpecManager(tmp_path)

        spec = manager.create_spec(
            title="Original",
            content="Content",
            source_command="/promptrek.spec.create",
        )

        # Update metadata
        updated = manager.update_spec(
            spec_id=spec.id,
            title="New Title",
            summary="New summary",
            tags=["new", "tags"],
        )

        assert updated.title == "New Title"
        assert updated.summary == "New summary"
        assert updated.tags == ["new", "tags"]

        # Verify in registry
        usf = manager.load_registry()
        found = next((s for s in usf.specs if s.id == spec.id), None)
        assert found.title == "New Title"

    def test_update_nonexistent_spec(self, tmp_path):
        """Test updating a spec that doesn't exist."""
        manager = SpecManager(tmp_path)

        with pytest.raises(ValueError) as exc_info:
            manager.update_spec(
                spec_id="nonexistent",
                content="New content",
            )

        assert "not found" in str(exc_info.value)


class TestSpecManagerQuery:
    """Tests for querying specs."""

    def test_get_spec_by_id(self, tmp_path):
        """Test getting spec by ID."""
        manager = SpecManager(tmp_path)

        spec1 = manager.create_spec(
            title="Spec 1",
            content="Content 1",
            source_command="/promptrek.spec.create",
        )
        spec2 = manager.create_spec(
            title="Spec 2",
            content="Content 2",
            source_command="/promptrek.spec.create",
        )

        # Get spec1
        found = manager.get_spec_by_id(spec1.id)
        assert found is not None
        assert found.id == spec1.id
        assert found.title == "Spec 1"

        # Get spec2
        found = manager.get_spec_by_id(spec2.id)
        assert found is not None
        assert found.id == spec2.id

        # Nonexistent spec
        found = manager.get_spec_by_id("nonexistent")
        assert found is None

    def test_list_specs(self, tmp_path):
        """Test listing all specs."""
        manager = SpecManager(tmp_path)

        # Empty list
        specs = manager.list_specs()
        assert specs == []

        # Create some specs
        spec1 = manager.create_spec(
            title="Spec 1",
            content="Content 1",
            source_command="/promptrek.spec.create",
        )
        spec2 = manager.create_spec(
            title="Spec 2",
            content="Content 2",
            source_command="/promptrek.spec.create",
        )

        specs = manager.list_specs()
        assert len(specs) == 2

        ids = {s.id for s in specs}
        assert spec1.id in ids
        assert spec2.id in ids

    def test_get_spec_content(self, tmp_path):
        """Test getting spec content."""
        manager = SpecManager(tmp_path)

        spec = manager.create_spec(
            title="Test Spec",
            content="This is the content.",
            source_command="/promptrek.spec.create",
        )

        content = manager.get_spec_content(spec.id)

        assert "# Test Spec" in content
        assert "This is the content." in content
        assert f"**ID:** {spec.id}" in content

    def test_get_spec_content_nonexistent(self, tmp_path):
        """Test getting content of nonexistent spec."""
        manager = SpecManager(tmp_path)

        with pytest.raises(ValueError) as exc_info:
            manager.get_spec_content("nonexistent")

        assert "not found" in str(exc_info.value)

    def test_get_spec_content_missing_file(self, tmp_path):
        """Test getting content when file is missing."""
        manager = SpecManager(tmp_path)

        # Create spec then delete file
        spec = manager.create_spec(
            title="Test",
            content="Content",
            source_command="/test",
        )

        spec_file = manager.specs_dir / spec.path
        spec_file.unlink()

        with pytest.raises(FileNotFoundError):
            manager.get_spec_content(spec.id)


class TestSpecManagerExport:
    """Tests for exporting specs."""

    def test_export_spec_clean(self, tmp_path):
        """Test exporting spec with clean option."""
        manager = SpecManager(tmp_path)

        spec = manager.create_spec(
            title="Export Test",
            content="Export content here.",
            source_command="/promptrek.spec.create",
            summary="Test summary",
        )

        output_path = tmp_path / "exported.md"
        manager.export_spec(spec.id, output_path, clean=True)

        assert output_path.exists()

        content = output_path.read_text()
        # Should not have metadata header
        assert "**ID:**" not in content
        assert "**Created:**" not in content
        # Should have content
        assert "Export content here." in content

    def test_export_spec_with_metadata(self, tmp_path):
        """Test exporting spec with metadata."""
        manager = SpecManager(tmp_path)

        spec = manager.create_spec(
            title="Export Test",
            content="Export content.",
            source_command="/promptrek.spec.create",
        )

        output_path = tmp_path / "exported.md"
        manager.export_spec(spec.id, output_path, clean=False)

        content = output_path.read_text()
        # Should have metadata
        assert "# Export Test" in content
        assert f"**ID:** {spec.id}" in content
        assert "Export content." in content

    def test_export_nonexistent_spec(self, tmp_path):
        """Test exporting nonexistent spec."""
        manager = SpecManager(tmp_path)

        output_path = tmp_path / "exported.md"

        with pytest.raises(ValueError) as exc_info:
            manager.export_spec("nonexistent", output_path, clean=True)

        assert "not found" in str(exc_info.value)


class TestSpecManagerSync:
    """Tests for syncing specs from disk."""

    def test_sync_specs_from_disk_empty(self, tmp_path):
        """Test syncing when no new files exist."""
        manager = SpecManager(tmp_path)
        manager.ensure_specs_directory()

        new_specs = manager.sync_specs_from_disk()

        assert new_specs == []

    def test_sync_specs_from_disk_no_directory(self, tmp_path):
        """Test syncing when specs directory doesn't exist."""
        manager = SpecManager(tmp_path)

        new_specs = manager.sync_specs_from_disk()

        assert new_specs == []

    def test_sync_specs_from_disk_new_files(self, tmp_path):
        """Test syncing new markdown files."""
        manager = SpecManager(tmp_path)
        manager.ensure_specs_directory()

        # Create manual spec files
        spec1_path = manager.specs_dir / "manual-spec-1.md"
        spec1_path.write_text("# Manual Spec 1\n\nContent here.")

        spec2_path = manager.specs_dir / "manual-spec-2.md"
        spec2_path.write_text("# Manual Spec 2\n\nMore content.")

        new_specs = manager.sync_specs_from_disk()

        assert len(new_specs) == 2

        # Check registry was updated
        usf = manager.load_registry()
        assert len(usf.specs) == 2

        titles = {s.title for s in usf.specs}
        assert "Manual Spec 1" in titles
        assert "Manual Spec 2" in titles

        # All synced specs should have source_command = "sync"
        for spec in usf.specs:
            assert spec.source_command == "sync"
            assert spec.summary == "Synced from disk"

    def test_sync_specs_from_disk_mixed(self, tmp_path):
        """Test syncing when some files are already registered."""
        manager = SpecManager(tmp_path)

        # Create a spec through the manager
        existing = manager.create_spec(
            title="Existing",
            content="Existing content",
            source_command="/promptrek.spec.create",
        )

        # Create a manual file
        manual_path = manager.specs_dir / "manual.md"
        manual_path.write_text("# Manual Spec\n\nManual content.")

        new_specs = manager.sync_specs_from_disk()

        # Should only sync the new manual file
        assert len(new_specs) == 1
        assert new_specs[0].title == "Manual Spec"

        # Registry should have both
        usf = manager.load_registry()
        assert len(usf.specs) == 2

    def test_sync_specs_from_disk_no_title(self, tmp_path):
        """Test syncing file without title."""
        manager = SpecManager(tmp_path)
        manager.ensure_specs_directory()

        # Create file without title
        spec_path = manager.specs_dir / "no-title.md"
        spec_path.write_text("Some content without title.")

        new_specs = manager.sync_specs_from_disk()

        assert len(new_specs) == 1
        assert new_specs[0].title == "Untitled Spec"


class TestSpecManagerFilenameGeneration:
    """Tests for filename generation."""

    def test_generate_filename(self, tmp_path):
        """Test filename generation from title."""
        manager = SpecManager(tmp_path)

        # Test basic slug generation
        filename = manager._generate_filename("Test Specification", "abc123")
        assert filename == "test-specification-abc123.md"

        # Test with special characters
        filename = manager._generate_filename("API: Auth & OAuth", "xyz789")
        assert filename == "api-auth-oauth-xyz789.md"

        # Test with very long title (should be truncated)
        long_title = "This is a very long title that should be truncated to prevent extremely long filenames"
        filename = manager._generate_filename(long_title, "test")
        assert len(filename) <= 60  # 50 char slug + dash + 8 char id + .md

    def test_extract_title_from_content(self, tmp_path):
        """Test title extraction from content."""
        manager = SpecManager(tmp_path)

        # Test with valid title
        content = "# My Spec Title\n\nContent here."
        title = manager._extract_title_from_content(content)
        assert title == "My Spec Title"

        # Test with no title
        content = "Content without title."
        title = manager._extract_title_from_content(content)
        assert title == "Untitled Spec"

        # Test with multiple headings (should get first)
        content = "# First Title\n\n## Second Title\n\nContent."
        title = manager._extract_title_from_content(content)
        assert title == "First Title"
