"""
Unit tests for sync mixin classes.
"""

import tempfile
from pathlib import Path

import pytest

from promptrek.adapters.sync_mixin import (
    MarkdownSyncMixin,
    SingleFileMarkdownSyncMixin,
)


class TestMarkdownSyncMixin:
    """Test MarkdownSyncMixin functionality."""

    @pytest.fixture
    def mixin(self):
        """Create a MarkdownSyncMixin instance."""
        return MarkdownSyncMixin()

    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory with markdown files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            temp_path = Path(tmpdir)

            # Create .test/rules directory
            rules_dir = temp_path / ".test" / "rules"
            rules_dir.mkdir(parents=True)

            # Create general.md
            (rules_dir / "general.md").write_text(
                "# General Rules\n\n- Follow best practices\n- Write clean code\n"
            )

            # Create code-style.md
            (rules_dir / "code-style.md").write_text(
                "# Code Style\n\n- Use proper indentation\n- Follow PEP 8\n"
            )

            # Create testing.md
            (rules_dir / "testing.md").write_text(
                "# Testing\n\n- Write unit tests\n- Use pytest\n"
            )

            # Create python-rules.md
            (rules_dir / "python-rules.md").write_text(
                "# Python Rules\n\n- Use type hints\n- Follow conventions\n"
            )

            yield temp_path

    def test_parse_markdown_rules_files(self, mixin, temp_dir):
        """Test parsing markdown rules files."""
        result = mixin.parse_markdown_rules_files(
            source_dir=temp_dir,
            rules_subdir=".test/rules",
            file_extension="md",
            editor_name="Test Editor",
        )

        # Should return v3 format
        assert result.schema_version == "3.1.0"
        assert result.metadata.title == "Test Editor Configuration"
        assert "Test Editor" in result.metadata.description

        # Check content and documents
        assert result.content is not None
        # First file (general.md) becomes main content
        assert (
            "Follow best practices" in result.content
            or "Use proper indentation" in result.content
        )

        # Other files become documents
        if result.documents:
            doc_names = [doc.name for doc in result.documents]
            # At least one document should exist
            assert len(doc_names) > 0

    def test_parse_markdown_file(self, mixin, temp_dir):
        """Test parsing a single markdown file."""
        md_file = temp_dir / "test.md"
        md_file.write_text(
            "# Test\n\n- First item\n- Second item\n\n## Section\n\n- Third item\n"
        )

        result = mixin._parse_markdown_file(md_file)

        assert "First item" in result
        assert "Second item" in result
        assert "Third item" in result
        assert len(result) == 3

    def test_parse_markdown_file_with_frontmatter(self, mixin, temp_dir):
        """Test parsing markdown file with YAML frontmatter."""
        md_file = temp_dir / "test.md"
        md_file.write_text(
            "---\ntitle: Test\n---\n\n# Content\n\n- First item\n- Second item\n"
        )

        result = mixin._parse_markdown_file(md_file)

        # Frontmatter should be skipped
        assert "title: Test" not in result
        assert "First item" in result
        assert "Second item" in result

    def test_parse_empty_directory(self, mixin, temp_dir):
        """Test parsing when directory is empty."""
        empty_dir = temp_dir / ".empty" / "rules"
        empty_dir.mkdir(parents=True)

        result = mixin.parse_markdown_rules_files(
            source_dir=temp_dir,
            rules_subdir=".empty/rules",
            file_extension="md",
            editor_name="Test",
        )

        # Should return valid v3 prompt with default content
        assert result.schema_version == "3.1.0"
        assert result.metadata.title == "Test Configuration"
        assert result.content is not None
        assert "No rules found" in result.content

    def test_parse_nonexistent_directory(self, mixin, temp_dir):
        """Test parsing when directory doesn't exist."""
        result = mixin.parse_markdown_rules_files(
            source_dir=temp_dir,
            rules_subdir=".nonexistent/rules",
            file_extension="md",
            editor_name="Test",
        )

        # Should return valid v3 prompt even if directory doesn't exist
        assert result.schema_version == "3.1.0"
        assert result.metadata.title == "Test Configuration"
        assert result.content is not None

    def test_extract_technology_from_filename(self, mixin):
        """Test extracting technology from filename."""
        assert mixin._extract_technology_from_filename("python-rules") == "python"
        assert (
            mixin._extract_technology_from_filename("typescript-guidelines")
            == "typescript"
        )
        assert mixin._extract_technology_from_filename("react-guide") == "react"


class TestSingleFileMarkdownSyncMixin:
    """Test SingleFileMarkdownSyncMixin functionality."""

    @pytest.fixture
    def mixin(self):
        """Create a SingleFileMarkdownSyncMixin instance."""
        return SingleFileMarkdownSyncMixin()

    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory with single markdown file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            temp_path = Path(tmpdir)

            # Create .test directory
            test_dir = temp_path / ".test"
            test_dir.mkdir()

            # Create CLAUDE.md style file
            (test_dir / "RULES.md").write_text(
                """# Test Project

## General Guidelines
- Follow best practices
- Write clean code

## Code Style
- Use proper indentation
- Follow conventions

## Testing Guidelines
- Write unit tests
- Use pytest fixtures
"""
            )

            yield temp_path

    def test_parse_single_markdown_file(self, mixin, temp_dir):
        """Test parsing single markdown file."""
        result = mixin.parse_single_markdown_file(
            source_dir=temp_dir,
            file_path=".test/RULES.md",
            editor_name="Test Editor",
        )

        assert result.metadata.title == "Test Editor Configuration"
        assert "Test Editor" in result.metadata.description
        assert result.targets == ["test-editor"]

        # Check instructions were parsed from sections
        assert "Follow best practices" in result.instructions.general
        assert "Write clean code" in result.instructions.general
        assert "Use proper indentation" in result.instructions.code_style

    def test_parse_nonexistent_file(self, mixin, temp_dir):
        """Test parsing when file doesn't exist."""
        result = mixin.parse_single_markdown_file(
            source_dir=temp_dir,
            file_path=".test/NONEXISTENT.md",
            editor_name="Test",
        )

        # Should return valid prompt even if file doesn't exist
        assert result.metadata.title == "Test Configuration"

    def test_parse_markdown_sections(self, mixin):
        """Test parsing sections from markdown content."""
        content = """# Title

## General Guidelines
- First instruction
- Second instruction

## Code Style Rules
- Style rule one
- Style rule two

## Testing
- Test instruction
"""

        result = mixin._parse_markdown_sections(content)

        assert "general" in result
        assert "First instruction" in result["general"]
        assert "Second instruction" in result["general"]
        assert "code_style" in result
        assert "Style rule one" in result["code_style"]
        assert "testing" in result
        assert "Test instruction" in result["testing"]
