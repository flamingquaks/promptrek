"""
Unit tests for Cursor adapter.
"""

import pytest

from promptrek.adapters.cursor import CursorAdapter

from .base_test import TestAdapterBase


class TestCursorAdapter(TestAdapterBase):
    """Test Cursor adapter."""

    @pytest.fixture
    def adapter(self):
        """Create Cursor adapter instance."""
        return CursorAdapter()

    def test_init(self, adapter):
        """Test adapter initialization."""
        assert adapter.name == "cursor"
        assert (
            adapter.description
            == "Cursor (.cursor/rules/index.mdc, .cursor/rules/*.mdc, AGENTS.md)"
        )
        assert adapter.file_patterns == [
            ".cursor/rules/index.mdc",
            ".cursor/rules/*.mdc",
            "AGENTS.md",
        ]

    def test_supports_features(self, adapter):
        """Test feature support."""
        assert adapter.supports_variables() is True
        assert adapter.supports_conditionals() is True

    def test_validate_valid_prompt(self, adapter, sample_prompt):
        """Test validation of valid prompt."""
        errors = adapter.validate(sample_prompt)
        assert len(errors) == 0

    def test_validate_missing_instructions(self, adapter):
        """Test validation with missing instructions."""
        from promptrek.core.models import PromptMetadata, UniversalPrompt

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
            targets=["cursor"],
        )
        errors = adapter.validate(prompt)
        assert len(errors) == 1
        assert errors[0].field == "instructions"

    def test_build_mdc_content(self, adapter):
        """Test MDF file content generation."""
        instructions = ["Follow TypeScript best practices", "Use strict mode"]
        content = adapter._build_mdc_content(
            "TypeScript Rules",
            instructions,
            "**/*.{ts,tsx}",
            "TypeScript coding guidelines",
        )

        assert "---" in content  # YAML frontmatter
        assert "description: TypeScript coding guidelines" in content
        assert 'globs: "**/*.{ts,tsx}"' in content
        assert "alwaysApply: false" in content
        assert "# TypeScript Rules" in content
        assert "- Follow TypeScript best practices" in content

    def test_build_agents_content(self, adapter, sample_prompt):
        """Test AGENTS.md content generation."""
        content = adapter._build_agents_content(sample_prompt)

        assert sample_prompt.metadata.title in content
        assert sample_prompt.metadata.description in content
        assert "## Project Context" in content
        assert "## General Instructions" in content

    from unittest.mock import mock_open, patch

    @patch("builtins.open", new_callable=mock_open)
    @patch("pathlib.Path.mkdir")
    def test_generate_actual_files(self, mock_mkdir, mock_file, adapter, sample_prompt):
        """Test actual file generation."""
        from pathlib import Path

        output_dir = Path("/tmp/test")
        files = adapter.generate(sample_prompt, output_dir, dry_run=False)

        # Should generate index.mdc, AGENTS.md + rules files
        assert len(files) >= 2

        # Check for modern files
        index_file = output_dir / ".cursor" / "rules" / "index.mdc"
        agents_file = output_dir / "AGENTS.md"
        assert index_file in files
        assert agents_file in files

        # Check that mkdir and file operations were called
        assert mock_mkdir.called
        assert mock_file.called

    def test_generate_dry_run(self, adapter, sample_prompt, capsys):
        """Test dry run generation."""
        from pathlib import Path

        output_dir = Path("/tmp/test")
        files = adapter.generate(sample_prompt, output_dir, dry_run=True)

        captured = capsys.readouterr()
        assert "Would create" in captured.out
        assert len(files) >= 2  # Should generate multiple files including index.mdc

    def test_generate_index_mdc_content(self, adapter, sample_prompt):
        """Test that index.mdc is generated with correct content."""
        content = adapter._build_single_index_content(sample_prompt)

        # Check YAML frontmatter
        assert "---" in content
        assert "description: Project overview and core guidelines" in content
        assert "alwaysApply: true" in content

        # Check project metadata
        assert sample_prompt.metadata.title in content
        assert sample_prompt.metadata.description in content

        # Check project context if present
        if sample_prompt.context:
            assert "## Project Context" in content

        # Check core guidelines if present
        if sample_prompt.instructions and sample_prompt.instructions.general:
            assert "## Core Guidelines" in content

    def test_generate_merged_creates_modern_files(self, adapter, sample_prompt):
        """Test that generate_merged creates modern .mdc files instead of legacy .cursorrules."""
        from pathlib import Path

        output_dir = Path("/tmp/test")
        prompt_files = [(sample_prompt, Path("test.promptrek.yaml"))]

        files = adapter.generate_merged(prompt_files, output_dir, dry_run=True)

        # Should generate modern index.mdc file
        index_file = output_dir / ".cursor" / "rules" / "index.mdc"
        assert index_file in files

        # Should NOT generate legacy .cursorrules
        legacy_file = output_dir / ".cursorrules"
        assert legacy_file not in files

    def test_generate_v2_with_content_metadata(self, adapter):
        """Test v2 generation with content metadata fields."""
        from pathlib import Path

        from promptrek.core.models import PromptMetadata, UniversalPromptV2

        prompt = UniversalPromptV2(
            schema_version="2.0.0",
            metadata=PromptMetadata(
                title="Test Project",
                description="Test description",
            ),
            content="# Main Guidelines\n\n- Write clean code\n- Follow best practices",
            content_description="Custom project overview",
            content_always_apply=False,  # Test non-default value
        )

        output_dir = Path("/tmp/test")
        files = adapter.generate(prompt, output_dir, dry_run=True)

        # Should generate index.mdc
        index_file = output_dir / ".cursor" / "rules" / "index.mdc"
        assert index_file in files

    def test_generate_v2_with_documents_and_metadata(self, adapter):
        """Test v2 generation with documents using metadata fields."""
        from pathlib import Path

        from promptrek.core.models import (
            DocumentConfig,
            PromptMetadata,
            UniversalPromptV2,
        )

        prompt = UniversalPromptV2(
            schema_version="2.0.0",
            metadata=PromptMetadata(
                title="Test Project",
                description="Test description",
            ),
            content="# Main Guidelines\n\n- General rules",
            documents=[
                DocumentConfig(
                    name="typescript",
                    content="# TypeScript Rules\n\n- Use strict mode",
                    description="TypeScript coding guidelines",
                    file_globs="**/*.{ts,tsx}",
                    always_apply=False,
                ),
                DocumentConfig(
                    name="testing",
                    content="# Testing Standards\n\n- Write unit tests",
                    # No explicit metadata - should use defaults and inference
                ),
            ],
        )

        output_dir = Path("/tmp/test")
        files = adapter.generate(prompt, output_dir, dry_run=True)

        # Should generate index.mdc + 2 document files
        assert len(files) >= 3
        assert (output_dir / ".cursor" / "rules" / "index.mdc") in files
        assert (output_dir / ".cursor" / "rules" / "typescript.mdc") in files
        assert (output_dir / ".cursor" / "rules" / "testing.mdc") in files

    def test_generate_v3_with_content_metadata(self, adapter):
        """Test v3 generation with content metadata fields."""
        from pathlib import Path

        from promptrek.core.models import PromptMetadata, UniversalPromptV3

        prompt = UniversalPromptV3(
            schema_version="3.0.0",
            metadata=PromptMetadata(
                title="Test Project",
                description="Test description",
            ),
            content="# Main Guidelines\n\n- Write clean code",
            content_description="Project overview and standards",
            content_always_apply=True,
        )

        output_dir = Path("/tmp/test")
        files = adapter.generate(prompt, output_dir, dry_run=True)

        # Should generate index.mdc
        index_file = output_dir / ".cursor" / "rules" / "index.mdc"
        assert index_file in files

    def test_generate_v3_with_documents_and_metadata(self, adapter):
        """Test v3 generation with documents using metadata fields."""
        from pathlib import Path

        from promptrek.core.models import (
            DocumentConfig,
            PromptMetadata,
            UniversalPromptV3,
        )

        prompt = UniversalPromptV3(
            schema_version="3.0.0",
            metadata=PromptMetadata(
                title="Test Project",
                description="Test description",
            ),
            content="# Main Guidelines\n\n- General rules",
            content_description="Core project standards",
            documents=[
                DocumentConfig(
                    name="python",
                    content="# Python Rules\n\n- Follow PEP 8",
                    description="Python coding standards",
                    file_globs="**/*.{py,pyi}",
                    always_apply=False,
                ),
            ],
        )

        output_dir = Path("/tmp/test")
        files = adapter.generate(prompt, output_dir, dry_run=True)

        # Should generate index.mdc + python.mdc
        assert len(files) >= 2
        assert (output_dir / ".cursor" / "rules" / "index.mdc") in files
        assert (output_dir / ".cursor" / "rules" / "python.mdc") in files

    def test_build_cursor_frontmatter(self, adapter):
        """Test Cursor frontmatter building helper."""
        # With globs
        fm = adapter._build_cursor_frontmatter(
            description="TypeScript guidelines",
            always_apply=False,
            file_globs="**/*.{ts,tsx}",
        )
        assert fm["description"] == "TypeScript guidelines"
        assert fm["alwaysApply"] is False
        assert fm["globs"] == "**/*.{ts,tsx}"

        # Without globs (main content)
        fm = adapter._build_cursor_frontmatter(
            description="Project overview",
            always_apply=True,
            file_globs=None,
        )
        assert fm["description"] == "Project overview"
        assert fm["alwaysApply"] is True
        assert "globs" not in fm

    def test_build_mdc_file(self, adapter):
        """Test MDC file building with frontmatter and content."""
        frontmatter = {
            "description": "Test guidelines",
            "alwaysApply": False,
            "globs": "**/*.py",
        }
        content = "# Test\n\nSome content with {{{ VAR }}}"
        variables = {"VAR": "replaced"}

        result = adapter._build_mdc_file(frontmatter, content, variables)

        # Check frontmatter
        assert "---" in result
        assert 'description: "Test guidelines"' in result
        assert "alwaysApply: false" in result
        assert 'globs: "**/*.py"' in result

        # Check content with variable substitution
        assert "# Test" in result
        assert "Some content with replaced" in result
        assert "{{{ VAR }}}" not in result

    def test_infer_globs_from_name(self, adapter):
        """Test glob pattern inference from document name."""
        assert adapter._infer_globs_from_name("typescript") == "**/*.{ts,tsx}"
        assert adapter._infer_globs_from_name("python") == "**/*.{py,pyi}"
        assert adapter._infer_globs_from_name("testing") == "**/*.{test,spec}.*"
        assert (
            adapter._infer_globs_from_name("code-style")
            == "**/*.{py,js,ts,tsx,jsx,go,rs,java,cpp,c,h}"
        )
        assert adapter._infer_globs_from_name("unknown") is None

    def test_generate_v2_default_metadata(self, adapter):
        """Test v2 generation with default metadata values."""
        from pathlib import Path

        from promptrek.core.models import (
            DocumentConfig,
            PromptMetadata,
            UniversalPromptV2,
        )

        prompt = UniversalPromptV2(
            schema_version="2.0.0",
            metadata=PromptMetadata(
                title="Test Project",
                description="Test description",
            ),
            content="# Main Guidelines",
            # No content_description or content_always_apply - should use defaults
            documents=[
                DocumentConfig(
                    name="typescript",
                    content="# TypeScript Rules",
                    # No metadata fields - should use defaults and inference
                ),
            ],
        )

        output_dir = Path("/tmp/test")
        files = adapter.generate(prompt, output_dir, dry_run=True)

        # Verify files are generated
        assert len(files) >= 2

    def test_validate_v2_prompt(self, adapter):
        """Test validation of v2 prompts."""
        from pydantic import ValidationError as PydanticValidationError

        from promptrek.core.models import PromptMetadata, UniversalPromptV2

        # Valid v2 prompt
        prompt = UniversalPromptV2(
            schema_version="2.0.0",
            metadata=PromptMetadata(
                title="Test",
                description="Test description",
            ),
            content="# Guidelines\n\n- Rule 1",
        )
        errors = adapter.validate(prompt)
        assert len(errors) == 0

        # Invalid v2 prompt - empty content (caught by Pydantic)
        with pytest.raises(PydanticValidationError) as exc_info:
            UniversalPromptV2(
                schema_version="2.0.0",
                metadata=PromptMetadata(
                    title="Test",
                    description="Test description",
                ),
                content="",
            )
        assert "content" in str(exc_info.value)

    def test_validate_v3_prompt(self, adapter):
        """Test validation of v3 prompts."""
        from pydantic import ValidationError as PydanticValidationError

        from promptrek.core.models import PromptMetadata, UniversalPromptV3

        # Valid v3 prompt
        prompt = UniversalPromptV3(
            schema_version="3.0.0",
            metadata=PromptMetadata(
                title="Test",
                description="Test description",
            ),
            content="# Guidelines\n\n- Rule 1",
        )
        errors = adapter.validate(prompt)
        assert len(errors) == 0

        # Invalid v3 prompt - empty content (caught by Pydantic)
        with pytest.raises(PydanticValidationError) as exc_info:
            UniversalPromptV3(
                schema_version="3.0.0",
                metadata=PromptMetadata(
                    title="Test",
                    description="Test description",
                ),
                content="   ",  # Whitespace only
            )
        assert "content" in str(exc_info.value).lower()
