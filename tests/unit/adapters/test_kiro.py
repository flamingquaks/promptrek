"""
Unit tests for Kiro adapter.
"""

from pathlib import Path
from unittest.mock import mock_open, patch

import pytest

from promptrek.adapters.kiro import KiroAdapter

from .base_test import TestAdapterBase


class TestKiroAdapter(TestAdapterBase):
    """Test Kiro adapter."""

    @pytest.fixture
    def adapter(self):
        """Create Kiro adapter instance."""
        return KiroAdapter()

    def test_init(self, adapter):
        """Test adapter initialization."""
        assert adapter.name == "kiro"
        assert "Kiro" in adapter.description
        assert ".kiro/steering/*.md" in adapter.file_patterns

    def test_supports_variables(self, adapter):
        """Test variable support."""
        assert adapter.supports_variables() is True

    def test_supports_conditionals(self, adapter):
        """Test conditional support."""
        assert adapter.supports_conditionals() is True

    def test_validate_valid_prompt(self, adapter, sample_prompt):
        """Test validation of valid prompt."""
        errors = adapter.validate(sample_prompt)
        # Should only have warnings, no critical errors
        assert all(error.severity == "warning" for error in errors)

    @patch("builtins.open", new_callable=mock_open)
    @patch("pathlib.Path.mkdir")
    def test_generate_actual_files(self, mock_mkdir, mock_file, adapter, sample_prompt):
        """Test actual file generation."""
        output_dir = Path("/tmp/test")
        files = adapter.generate(sample_prompt, output_dir, dry_run=False)

        # Should generate steering files only
        assert len(files) >= 1
        # Check using path components for cross-platform compatibility
        file_strs = [str(f) for f in files]
        assert any("kiro" in f and "steering" in f for f in file_strs)
        assert mock_mkdir.called
        assert mock_file.called

    def test_generate_dry_run(self, adapter, sample_prompt, capsys):
        """Test dry run generation."""
        output_dir = Path("/tmp/test")
        files = adapter.generate(sample_prompt, output_dir, dry_run=True)

        captured = capsys.readouterr()
        assert "Would create" in captured.out
        assert len(files) >= 1  # Dry run returns paths that would be created


class TestKiroAdapterSpecInclusion:
    """Test v3.1+ spec document inclusion."""

    @pytest.fixture
    def adapter(self):
        from promptrek.adapters.kiro import KiroAdapter

        return KiroAdapter()

    @pytest.fixture
    def spec_dir(self, tmp_path):
        """Create spec directory with sample spec using SpecManager."""
        from promptrek.utils.spec_manager import SpecManager

        spec_manager = SpecManager(tmp_path)
        spec_manager.create_spec(
            title="Test Spec",
            content="# Test Spec\n\nThis is a test specification.\n\n## Content\n- Item 1\n- Item 2",
            summary="Test spec for adapter",
            tags=["test"],
            source_command="spec",
        )
        return tmp_path

    def test_v3_1_generates_spec_files(self, adapter, spec_dir):
        from promptrek.core.models import PromptMetadata, UniversalPromptV3

        prompt = UniversalPromptV3(
            schema_version="3.1.0",
            metadata=PromptMetadata(
                title="Test",
                description="Test",
                created="2024-01-01",
                updated="2024-01-01",
                version="1.0.0",
                author="test",
            ),
            content="# Test",
            include_specs=True,
        )
        adapter.generate(prompt, spec_dir, dry_run=False)
        # Check that at least one spec file was created
        spec_files = list((spec_dir / ".kiro/steering").glob("spec-*.md"))
        assert len(spec_files) > 0

        # Check first spec file has USF format
        spec_file = spec_files[0]
        spec_content = spec_file.read_text()
        # Check for USF format elements
        assert "**ID:**" in spec_content
        assert "**Created:**" in spec_content
        assert "---" in spec_content

    def test_v3_1_disabled_no_spec_files(self, adapter, spec_dir):
        from promptrek.core.models import PromptMetadata, UniversalPromptV3

        prompt = UniversalPromptV3(
            schema_version="3.1.0",
            metadata=PromptMetadata(
                title="Test",
                description="Test",
                created="2024-01-01",
                updated="2024-01-01",
                version="1.0.0",
                author="test",
            ),
            content="# Test",
            include_specs=False,
        )
        adapter.generate(prompt, spec_dir, dry_run=False)
        # Check that no spec files were created
        if (spec_dir / ".kiro/steering").exists():
            spec_files = list((spec_dir / ".kiro/steering").glob("spec-*.md"))
            assert len(spec_files) == 0

    def test_v3_0_no_spec_files(self, adapter, spec_dir):
        from promptrek.core.models import PromptMetadata, UniversalPromptV3

        prompt = UniversalPromptV3(
            schema_version="3.0.0",
            metadata=PromptMetadata(
                title="Test",
                description="Test",
                created="2024-01-01",
                updated="2024-01-01",
                version="1.0.0",
                author="test",
            ),
            content="# Test",
        )
        adapter.generate(prompt, spec_dir, dry_run=False)
        # Check that no spec files were created
        if (spec_dir / ".kiro/steering").exists():
            spec_files = list((spec_dir / ".kiro/steering").glob("spec-*.md"))
            assert len(spec_files) == 0
