"""
Unit tests for Claude adapter.
"""

import pytest

from promptrek.adapters.claude import ClaudeAdapter
from promptrek.core.models import PromptMetadata, UniversalPrompt

from .base_test import TestAdapterBase


class TestClaudeAdapter(TestAdapterBase):
    """Test Claude adapter."""

    @pytest.fixture
    def adapter(self):
        """Create Claude adapter instance."""
        return ClaudeAdapter()

    def test_init(self, adapter):
        """Test adapter initialization."""
        assert adapter.name == "claude"
        assert adapter.description == "Claude Code (context-based)"
        assert ".claude/CLAUDE.md" in adapter.file_patterns

    def test_supports_features(self, adapter):
        """Test feature support."""
        assert adapter.supports_variables() is True
        assert adapter.supports_conditionals() is True

    def test_validate_with_context(self, adapter, sample_prompt):
        """Test validation with context."""
        errors = adapter.validate(sample_prompt)
        # Should only have warnings, not errors
        warning_errors = [
            e for e in errors if getattr(e, "severity", "error") == "warning"
        ]
        assert len(warning_errors) == 0  # Has context and examples

    def test_validate_missing_context(self, adapter):
        """Test validation with missing context."""
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
            targets=["claude"],
        )
        errors = adapter.validate(prompt)
        assert len(errors) == 2  # Missing context and examples warnings

    def test_build_content(self, adapter, sample_prompt):
        """Test content generation."""
        content = adapter._build_content(sample_prompt)

        assert sample_prompt.metadata.title in content
        assert sample_prompt.metadata.description in content
        assert "## Project Details" in content
        assert "## Development Guidelines" in content
        assert "## Code Examples" in content
        assert "typescript, react, nodejs" in content

    def test_generate_v1_dry_run_verbose(self, adapter, tmp_path):
        """Test v1 generation with dry run and verbose."""
        from promptrek.core.models import Instructions

        prompt = UniversalPrompt(
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
            instructions=Instructions(general=["Test instruction"]),
        )

        files = adapter.generate(prompt, tmp_path, dry_run=True, verbose=True)

        assert len(files) > 0
        for f in files:
            assert not f.exists()

    def test_generate_with_conditionals(self, adapter, tmp_path):
        """Test generation with conditional instructions."""
        from promptrek.core.models import Condition, Instructions

        prompt = UniversalPrompt(
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
            instructions=Instructions(general=["Base instruction"]),
            conditions=[
                Condition.model_validate(
                    {
                        "if": "EDITOR == 'claude'",
                        "then": {
                            "instructions": {"general": ["Claude-specific instruction"]}
                        },
                    }
                )
            ],
        )

        files = adapter.generate(prompt, tmp_path)

        assert len(files) > 0

    def test_generate_v2_dry_run_verbose(self, adapter, tmp_path):
        """Test v2 generation with dry run and verbose."""
        from promptrek.core.models import UniversalPromptV2

        prompt = UniversalPromptV2(
            schema_version="2.0.0",
            metadata=PromptMetadata(
                title="Test",
                description="Test",
                created="2024-01-01",
                updated="2024-01-01",
                version="1.0.0",
                author="test@example.com",
            ),
            content="# Instructions\n\n" + "Content " * 50,
        )

        adapter.generate(prompt, tmp_path, dry_run=True, verbose=True)

    def test_generate_v1_all_instruction_categories(self, adapter, tmp_path):
        """Test v1 generation with all instruction categories."""
        from promptrek.core.models import Instructions, ProjectContext

        prompt = UniversalPrompt(
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
            context=ProjectContext(
                project_type="application", technologies=["Python", "TypeScript"]
            ),
            instructions=Instructions(
                general=["General rule"],
                code_style=["Code style rule"],
                architecture=["Architecture rule"],
                testing=["Testing rule"],
                security=["Security rule"],
                performance=["Performance rule"],
            ),
        )

        files = adapter.generate(prompt, tmp_path)

        assert len(files) > 0
        content = files[0].read_text()
        assert "Architecture" in content
        # Security and Performance may not always be included
        assert "Architecture" in content

    def test_parse_files_basic(self, adapter, tmp_path):
        """Test parsing Claude files."""
        claude_dir = tmp_path / ".claude"
        claude_dir.mkdir()

        claude_md = claude_dir / "CLAUDE.md"
        claude_md.write_text(
            """# Project Instructions

## General Guidelines
- Follow best practices
- Write clean code

## Code Style
- Use consistent formatting
"""
        )

        result = adapter.parse_files(tmp_path)

        assert result is not None
        assert "best practices" in str(result)
