"""Comprehensive Windsurf adapter tests."""

import pytest

from promptrek.adapters.windsurf import WindsurfAdapter
from promptrek.core.models import (
    DocumentConfig,
    Instructions,
    PromptMetadata,
    UniversalPrompt,
    UniversalPromptV2,
)


class TestWindsurfAdapterComprehensive:
    """Comprehensive tests for Windsurf adapter."""

    @pytest.fixture
    def adapter(self):
        return WindsurfAdapter()

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
            targets=["windsurf"],
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
            documents=[DocumentConfig(name="extra", content="# Extra")],
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
            content="{{{ VAR }}}",
            variables={"VAR": "value"},
        )

        files = adapter.generate(prompt, tmp_path, variables={"VAR": "test"})
        assert len(files) > 0

    def test_generate_v1_with_all_instructions(self, adapter, tmp_path):
        prompt = UniversalPrompt(
            schema_version="1.0.0",
            metadata=PromptMetadata(title="Test", description="Test"),
            targets=["windsurf"],
            instructions=Instructions(
                general=["A"],
                code_style=["B"],
                architecture=["C"],
                testing=["D"],
                security=["E"],
                performance=["F"],
            ),
        )

        files = adapter.generate(prompt, tmp_path)
        assert len(files) > 0

    def test_generate_v1_with_examples(self, adapter, tmp_path):
        prompt = UniversalPrompt(
            schema_version="1.0.0",
            metadata=PromptMetadata(title="Test", description="Test"),
            targets=["windsurf"],
            instructions=Instructions(general=["Test"]),
            examples={"ex": "code"},
        )

        files = adapter.generate(prompt, tmp_path)
        assert len(files) > 0

    def test_generate_multiple_times(self, adapter, v2_prompt, tmp_path):
        files1 = adapter.generate(v2_prompt, tmp_path)
        files2 = adapter.generate(v2_prompt, tmp_path)
        assert len(files1) > 0 and len(files2) > 0

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
            targets=["windsurf"],
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
            targets=["windsurf"],
            instructions=Instructions(general=["Test"]),
        )

        files = adapter.generate(prompt, tmp_path, verbose=True)

        assert len(files) > 0
