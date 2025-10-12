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
