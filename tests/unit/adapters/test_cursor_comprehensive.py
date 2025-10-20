"""Comprehensive Cursor adapter tests."""

import pytest

from promptrek.adapters.cursor import CursorAdapter
from promptrek.core.models import (
    DocumentConfig,
    Instructions,
    PromptMetadata,
    UniversalPrompt,
    UniversalPromptV2,
)


class TestCursorAdapterComprehensive:
    """Comprehensive tests for Cursor adapter."""

    @pytest.fixture
    def adapter(self):
        return CursorAdapter()

    @pytest.fixture
    def v2_prompt(self):
        return UniversalPromptV2(
            schema_version="2.0.0",
            metadata=PromptMetadata(title="Test", description="Test"),
            content="# Test",
        )

    @pytest.fixture
    def v1_prompt(self):
        return UniversalPrompt(
            schema_version="1.0.0",
            metadata=PromptMetadata(title="Test", description="Test"),
            targets=["cursor"],
            instructions=Instructions(general=["Test"]),
        )

    def test_generate_v2_basic(self, adapter, v2_prompt, tmp_path):
        files = adapter.generate(v2_prompt, tmp_path)
        assert len(files) > 0

    def test_generate_v2_with_documents(self, adapter, tmp_path):
        prompt = UniversalPromptV2(
            schema_version="2.0.0",
            metadata=PromptMetadata(title="Test", description="Test"),
            content="# Main",
            documents=[
                DocumentConfig(name="rule1", content="# Rule 1"),
                DocumentConfig(name="rule2", content="# Rule 2"),
            ],
        )

        files = adapter.generate(prompt, tmp_path)
        assert len(files) > 0

    def test_generate_v1(self, adapter, v1_prompt, tmp_path):
        files = adapter.generate(v1_prompt, tmp_path)
        assert len(files) > 0

    def test_validate_v2(self, adapter, v2_prompt):
        errors = adapter.validate(v2_prompt)
        assert isinstance(errors, list)

    def test_validate_v1(self, adapter, v1_prompt):
        errors = adapter.validate(v1_prompt)
        assert isinstance(errors, list)

    def test_generate_with_variables(self, adapter, tmp_path):
        prompt = UniversalPromptV2(
            schema_version="2.0.0",
            metadata=PromptMetadata(title="Test", description="Test"),
            content="{{{ PROJECT }}}",
            variables={"PROJECT": "test"},
        )

        files = adapter.generate(prompt, tmp_path, variables={"PROJECT": "override"})
        assert len(files) > 0

    def test_generate_v1_all_categories(self, adapter, tmp_path):
        prompt = UniversalPrompt(
            schema_version="1.0.0",
            metadata=PromptMetadata(title="Test", description="Test"),
            targets=["cursor"],
            instructions=Instructions(
                general=["G"],
                code_style=["C"],
                architecture=["A"],
                testing=["T"],
                security=["S"],
                performance=["P"],
            ),
        )

        files = adapter.generate(prompt, tmp_path)
        assert len(files) > 0

    def test_generate_v1_with_examples(self, adapter, tmp_path):
        prompt = UniversalPrompt(
            schema_version="1.0.0",
            metadata=PromptMetadata(title="Test", description="Test"),
            targets=["cursor"],
            instructions=Instructions(general=["Test"]),
            examples={"py": "print('test')"},
        )

        files = adapter.generate(prompt, tmp_path)
        assert len(files) > 0

    def test_supports_variables(self, adapter):
        """Test that adapter supports variables."""
        assert adapter.supports_variables() is True

    def test_supports_conditionals(self, adapter):
        """Test that adapter supports conditionals."""
        assert adapter.supports_conditionals() is True

    def test_generate_v1_dry_run(self, adapter, tmp_path):
        """Test v1 generation with dry run."""
        prompt = UniversalPrompt(
            schema_version="1.0.0",
            metadata=PromptMetadata(title="Test", description="Test"),
            targets=["cursor"],
            instructions=Instructions(general=["Test"]),
        )

        files = adapter.generate(prompt, tmp_path, dry_run=True)

        assert len(files) > 0
        for f in files:
            assert not f.exists()

    def test_generate_v1_verbose(self, adapter, tmp_path):
        """Test v1 generation with verbose."""
        prompt = UniversalPrompt(
            schema_version="1.0.0",
            metadata=PromptMetadata(title="Test", description="Test"),
            targets=["cursor"],
            instructions=Instructions(general=["Test"]),
        )

        files = adapter.generate(prompt, tmp_path, verbose=True)

        assert len(files) > 0

    def test_generate_long_content(self, adapter, tmp_path):
        long_content = "# Rules\n\n" + "\n".join([f"Rule {i}" for i in range(100)])
        prompt = UniversalPromptV2(
            schema_version="2.0.0",
            metadata=PromptMetadata(title="Test", description="Test"),
            content=long_content,
        )

        files = adapter.generate(prompt, tmp_path)
        assert len(files) > 0

    def test_parse_files(self, adapter, tmp_path):
        # Create cursor structure
        cursor_file = tmp_path / ".cursorrules"
        cursor_file.write_text("# Rules\nTest rules")

        try:
            result = adapter.parse_files(tmp_path)
        except Exception:
            pass

    def test_generate_v2_documents(self, adapter, tmp_path):
        """Test v2 generation with documents."""
        from promptrek.core.models import DocumentConfig

        prompt = UniversalPromptV2(
            schema_version="2.0.0",
            metadata=PromptMetadata(title="Test", description="Test"),
            content="# Main content",
            documents=[
                DocumentConfig(name="doc1", content="# Document 1 content"),
                DocumentConfig(name="doc2", content="# Document 2 content"),
            ],
        )

        files = adapter.generate(prompt, tmp_path)

        # Should generate index.mdc + doc1.mdc + doc2.mdc = 3 files
        assert len(files) == 3
        assert any("index.mdc" in str(f) for f in files)
        assert any("doc1" in str(f) for f in files)
        assert any("doc2" in str(f) for f in files)

    def test_generate_v1_all_instruction_types(self, adapter, tmp_path):
        """Test v1 generation with all instruction categories."""
        from promptrek.core.models import ProjectContext

        prompt = UniversalPrompt(
            schema_version="1.0.0",
            metadata=PromptMetadata(title="Test", description="Test"),
            targets=["cursor"],
            context=ProjectContext(
                project_type="web_app",
                technologies=["Python", "TypeScript"],
                description="A web application",
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
        # Check that multiple .mdc files were created
        mdc_files = [f for f in files if f.suffix == ".mdc"]
        assert len(mdc_files) >= 3

    def test_generate_v1_with_multiple_examples(self, adapter, tmp_path):
        """Test v1 generation with multiple code examples."""
        prompt = UniversalPrompt(
            schema_version="1.0.0",
            metadata=PromptMetadata(title="Test", description="Test"),
            targets=["cursor"],
            instructions=Instructions(general=["Test"]),
            examples={
                "python_example": "def hello():\n    print('hello')",
                "typescript_example": "function hello() {\n  console.log('hello');\n}",
            },
        )

        files = adapter.generate(prompt, tmp_path)

        assert len(files) > 0

    def test_parse_files_cursorrules(self, adapter, tmp_path):
        """Test parsing from .cursorrules file."""
        cursor_dir = tmp_path / ".cursor"
        cursor_dir.mkdir()

        cursorrules = cursor_dir / ".cursorrules"
        cursorrules.write_text(
            """# Cursor Rules

## General Guidelines
- Follow best practices
- Write clean code
"""
        )

        result = adapter.parse_files(tmp_path)

        assert result is not None
        # Can return either v1 or v2

    def test_parse_files_v2_multiple_mdc(self, adapter, tmp_path):
        """Test parsing v2 from multiple .mdc files."""
        rules_dir = tmp_path / ".cursor" / "rules"
        rules_dir.mkdir(parents=True)

        (rules_dir / "general.mdc").write_text("# General\n\n- Rule 1\n- Rule 2")
        (rules_dir / "code-style.mdc").write_text("# Code Style\n\n- Style 1")
        (rules_dir / "testing.mdc").write_text("# Testing\n\n- Test 1")

        result = adapter.parse_files(tmp_path)

        # Can return either v1 or v2
        assert result is not None
        if hasattr(result, "documents") and result.documents:
            assert len(result.documents) >= 1

    def test_parse_files_v1_fallback(self, adapter, tmp_path):
        """Test v1 parsing fallback."""
        cursor_dir = tmp_path / ".cursor"
        cursor_dir.mkdir()

        # Create old-style rules directory
        rules_dir = cursor_dir / "rules"
        rules_dir.mkdir()

        (rules_dir / "general.md").write_text("# General\n\n- Rule 1")

        result = adapter.parse_files(tmp_path)

        # Should work with either v1 or v2
        assert result is not None

    def test_generate_with_conditionals(self, adapter, tmp_path):
        """Test generation with conditional instructions."""
        from promptrek.core.models import Condition

        prompt = UniversalPrompt(
            schema_version="1.0.0",
            metadata=PromptMetadata(title="Test", description="Test"),
            targets=["cursor"],
            instructions=Instructions(general=["Base rule"]),
            conditions=[
                Condition.model_validate(
                    {
                        "if": "EDITOR == 'cursor'",
                        "then": {"instructions": {"general": ["Cursor-specific rule"]}},
                    }
                )
            ],
        )

        files = adapter.generate(prompt, tmp_path)

        assert len(files) > 0
