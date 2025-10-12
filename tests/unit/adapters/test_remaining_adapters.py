"""Tests for remaining adapters."""

import pytest

from promptrek.adapters.amazon_q import AmazonQAdapter
from promptrek.adapters.cline import ClineAdapter
from promptrek.adapters.jetbrains import JetBrainsAdapter
from promptrek.adapters.kiro import KiroAdapter
from promptrek.core.models import (
    DocumentConfig,
    Instructions,
    PromptMetadata,
    UniversalPrompt,
    UniversalPromptV2,
)


class TestKiroAdapter:
    """Test Kiro adapter."""

    @pytest.fixture
    def adapter(self):
        return KiroAdapter()

    def test_generate_v2(self, adapter, tmp_path):
        prompt = UniversalPromptV2(
            schema_version="2.0.0",
            metadata=PromptMetadata(title="Test", description="Test"),
            content="# Test",
            documents=[DocumentConfig(name="steer", content="# Steering")],
        )

        files = adapter.generate(prompt, tmp_path)
        assert len(files) > 0

    def test_generate_v1(self, adapter, tmp_path):
        prompt = UniversalPrompt(
            schema_version="1.0.0",
            metadata=PromptMetadata(title="Test", description="Test"),
            targets=["kiro"],
            instructions=Instructions(general=["Test"]),
        )

        files = adapter.generate(prompt, tmp_path)
        assert len(files) > 0

    def test_validate_v2(self, adapter):
        prompt = UniversalPromptV2(
            schema_version="2.0.0",
            metadata=PromptMetadata(title="Test", description="Test"),
            content="# Test",
        )

        errors = adapter.validate(prompt)
        assert isinstance(errors, list)

    def test_generate_with_variables(self, adapter, tmp_path):
        prompt = UniversalPromptV2(
            schema_version="2.0.0",
            metadata=PromptMetadata(title="Test", description="Test"),
            content="{{{ VAR }}}",
            variables={"VAR": "value"},
        )

        files = adapter.generate(prompt, tmp_path, variables={"VAR": "override"})
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
            targets=["kiro"],
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
            targets=["kiro"],
            instructions=Instructions(general=["Test"]),
        )

        files = adapter.generate(prompt, tmp_path, verbose=True)

        assert len(files) > 0


class TestAmazonQAdapter:
    """Test Amazon Q adapter."""

    @pytest.fixture
    def adapter(self):
        return AmazonQAdapter()

    def test_generate_v2(self, adapter, tmp_path):
        prompt = UniversalPromptV2(
            schema_version="2.0.0",
            metadata=PromptMetadata(title="Test", description="Test"),
            content="# Test",
        )

        files = adapter.generate(prompt, tmp_path)
        assert len(files) > 0

    def test_generate_v1(self, adapter, tmp_path):
        prompt = UniversalPrompt(
            schema_version="1.0.0",
            metadata=PromptMetadata(title="Test", description="Test"),
            targets=["amazonq"],
            instructions=Instructions(general=["Test"]),
        )

        files = adapter.generate(prompt, tmp_path)
        assert len(files) > 0

    def test_validate_v2(self, adapter):
        prompt = UniversalPromptV2(
            schema_version="2.0.0",
            metadata=PromptMetadata(title="Test", description="Test"),
            content="# Test",
        )

        errors = adapter.validate(prompt)
        assert isinstance(errors, list)

    def test_generate_with_documents(self, adapter, tmp_path):
        prompt = UniversalPromptV2(
            schema_version="2.0.0",
            metadata=PromptMetadata(title="Test", description="Test"),
            content="# Main",
            documents=[DocumentConfig(name="extra", content="# Extra")],
        )

        files = adapter.generate(prompt, tmp_path)
        assert len(files) > 0


class TestJetBrainsAdapter:
    """Test JetBrains adapter."""

    @pytest.fixture
    def adapter(self):
        return JetBrainsAdapter()

    def test_generate_v2(self, adapter, tmp_path):
        prompt = UniversalPromptV2(
            schema_version="2.0.0",
            metadata=PromptMetadata(title="Test", description="Test"),
            content="# Test",
        )

        files = adapter.generate(prompt, tmp_path)
        assert len(files) > 0

    def test_generate_v1(self, adapter, tmp_path):
        prompt = UniversalPrompt(
            schema_version="1.0.0",
            metadata=PromptMetadata(title="Test", description="Test"),
            targets=["jetbrains"],
            instructions=Instructions(general=["Test"]),
        )

        files = adapter.generate(prompt, tmp_path)
        assert len(files) > 0

    def test_validate_v2(self, adapter):
        prompt = UniversalPromptV2(
            schema_version="2.0.0",
            metadata=PromptMetadata(title="Test", description="Test"),
            content="# Test",
        )

        errors = adapter.validate(prompt)
        assert isinstance(errors, list)

    def test_generate_with_documents(self, adapter, tmp_path):
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


class TestClineAdapter:
    """Test Cline adapter."""

    @pytest.fixture
    def adapter(self):
        return ClineAdapter()

    def test_generate_v2(self, adapter, tmp_path):
        prompt = UniversalPromptV2(
            schema_version="2.0.0",
            metadata=PromptMetadata(title="Test", description="Test"),
            content="# Test",
        )

        files = adapter.generate(prompt, tmp_path)
        assert len(files) > 0

    def test_generate_v1(self, adapter, tmp_path):
        prompt = UniversalPrompt(
            schema_version="1.0.0",
            metadata=PromptMetadata(title="Test", description="Test"),
            targets=["cline"],
            instructions=Instructions(general=["Test"]),
        )

        files = adapter.generate(prompt, tmp_path)
        assert len(files) > 0

    def test_validate_v2(self, adapter):
        prompt = UniversalPromptV2(
            schema_version="2.0.0",
            metadata=PromptMetadata(title="Test", description="Test"),
            content="# Test",
        )

        errors = adapter.validate(prompt)
        assert isinstance(errors, list)

    def test_generate_with_variables(self, adapter, tmp_path):
        prompt = UniversalPromptV2(
            schema_version="2.0.0",
            metadata=PromptMetadata(title="Test", description="Test"),
            content="Project: {{{ NAME }}}",
            variables={"NAME": "test"},
        )

        files = adapter.generate(prompt, tmp_path, variables={"NAME": "override"})
        assert len(files) > 0

    def test_generate_v1_with_examples(self, adapter, tmp_path):
        prompt = UniversalPrompt(
            schema_version="1.0.0",
            metadata=PromptMetadata(title="Test", description="Test"),
            targets=["cline"],
            instructions=Instructions(general=["Test"]),
            examples={"code": "print('hi')"},
        )

        files = adapter.generate(prompt, tmp_path)
        assert len(files) > 0


class TestAmazonQAdapterExtended:
    """Extended tests for Amazon Q adapter."""

    @pytest.fixture
    def adapter(self):
        from promptrek.adapters.amazon_q import AmazonQAdapter

        return AmazonQAdapter()

    def test_generate_v2_documents(self, adapter, tmp_path):
        """Test v2 generation with documents."""
        prompt = UniversalPromptV2(
            schema_version="2.0.0",
            metadata=PromptMetadata(title="Test", description="Test"),
            content="# Main",
            documents=[
                DocumentConfig(name="doc1", content="# Doc 1"),
                DocumentConfig(name="doc2", content="# Doc 2"),
            ],
        )

        files = adapter.generate(prompt, tmp_path)

        assert len(files) == 2

    def test_generate_v1_all_categories(self, adapter, tmp_path):
        """Test v1 generation with all instruction categories."""
        from promptrek.core.models import ProjectContext

        prompt = UniversalPrompt(
            schema_version="1.0.0",
            metadata=PromptMetadata(title="Test", description="Test"),
            targets=["amazonq"],
            context=ProjectContext(
                project_type="application", technologies=["Python", "Java"]
            ),
            instructions=Instructions(
                general=["General"],
                code_style=["Style"],
                architecture=["Arch"],
                testing=["Test"],
                security=["Sec"],
                performance=["Perf"],
            ),
        )

        files = adapter.generate(prompt, tmp_path)

        assert len(files) > 0

    def test_generate_v1_with_examples(self, adapter, tmp_path):
        """Test v1 generation with examples."""
        prompt = UniversalPrompt(
            schema_version="1.0.0",
            metadata=PromptMetadata(title="Test", description="Test"),
            targets=["amazonq"],
            instructions=Instructions(general=["Test"]),
            examples={"ex1": "code example"},
        )

        files = adapter.generate(prompt, tmp_path)

        assert len(files) > 0

    def test_generate_v1_dry_run(self, adapter, tmp_path):
        """Test v1 generation with dry run."""
        prompt = UniversalPrompt(
            schema_version="1.0.0",
            metadata=PromptMetadata(title="Test", description="Test"),
            targets=["amazonq"],
            instructions=Instructions(general=["Test"]),
        )

        files = adapter.generate(prompt, tmp_path, dry_run=True)

        for f in files:
            assert not f.exists()

    def test_generate_v1_verbose(self, adapter, tmp_path):
        """Test v1 generation with verbose."""
        prompt = UniversalPrompt(
            schema_version="1.0.0",
            metadata=PromptMetadata(title="Test", description="Test"),
            targets=["amazonq"],
            instructions=Instructions(general=["Test"]),
        )

        files = adapter.generate(prompt, tmp_path, verbose=True)

        assert len(files) > 0

    def test_parse_files_v2(self, adapter, tmp_path):
        """Test parsing v2 format."""
        rules_dir = tmp_path / ".aws" / "rules"
        rules_dir.mkdir(parents=True)

        (rules_dir / "general.md").write_text("# General\n\n- Rule 1")
        (rules_dir / "code-style.md").write_text("# Style\n\n- Style 1")

        result = adapter.parse_files(tmp_path)

        # Can return either v1 or v2
        assert result is not None
        if hasattr(result, "documents") and result.documents:
            assert len(result.documents) >= 2

    def test_validate_v2_with_documents(self, adapter):
        """Test v2 validation with documents."""
        prompt = UniversalPromptV2(
            schema_version="2.0.0",
            metadata=PromptMetadata(title="Test", description="Test"),
            content="# Main",
            documents=[DocumentConfig(name="doc1", content="# Content")],
        )

        errors = adapter.validate(prompt)

        assert isinstance(errors, list)


class TestJetBrainsAdapterExtended:
    """Extended tests for JetBrains adapter."""

    @pytest.fixture
    def adapter(self):
        from promptrek.adapters.jetbrains import JetBrainsAdapter

        return JetBrainsAdapter()

    def test_generate_v2_documents(self, adapter, tmp_path):
        """Test v2 generation with documents."""
        prompt = UniversalPromptV2(
            schema_version="2.0.0",
            metadata=PromptMetadata(title="Test", description="Test"),
            content="# Main",
            documents=[
                DocumentConfig(name="doc1", content="# Doc 1"),
                DocumentConfig(name="doc2", content="# Doc 2"),
            ],
        )

        files = adapter.generate(prompt, tmp_path)

        assert len(files) == 2

    def test_generate_v1_all_categories(self, adapter, tmp_path):
        """Test v1 generation with all categories."""
        prompt = UniversalPrompt(
            schema_version="1.0.0",
            metadata=PromptMetadata(title="Test", description="Test"),
            targets=["jetbrains"],
            instructions=Instructions(
                general=["General"], code_style=["Style"], testing=["Test"]
            ),
        )

        files = adapter.generate(prompt, tmp_path)

        assert len(files) > 0

    def test_generate_v1_dry_run(self, adapter, tmp_path):
        """Test v1 dry run."""
        prompt = UniversalPrompt(
            schema_version="1.0.0",
            metadata=PromptMetadata(title="Test", description="Test"),
            targets=["jetbrains"],
            instructions=Instructions(general=["Test"]),
        )

        adapter.generate(prompt, tmp_path, dry_run=True)

    def test_generate_v1_verbose(self, adapter, tmp_path):
        """Test v1 verbose."""
        prompt = UniversalPrompt(
            schema_version="1.0.0",
            metadata=PromptMetadata(title="Test", description="Test"),
            targets=["jetbrains"],
            instructions=Instructions(general=["Test"]),
        )

        files = adapter.generate(prompt, tmp_path, verbose=True)

        assert len(files) > 0


class TestClineAdapterExtended:
    """Extended tests for Cline adapter."""

    @pytest.fixture
    def adapter(self):
        from promptrek.adapters.cline import ClineAdapter

        return ClineAdapter()

    def test_generate_v2_basic(self, adapter, tmp_path):
        """Test v2 generation."""
        prompt = UniversalPromptV2(
            schema_version="2.0.0",
            metadata=PromptMetadata(title="Test", description="Test"),
            content="# Instructions",
        )

        files = adapter.generate(prompt, tmp_path)

        assert len(files) > 0

    def test_generate_v2_documents(self, adapter, tmp_path):
        """Test v2 generation with documents."""
        prompt = UniversalPromptV2(
            schema_version="2.0.0",
            metadata=PromptMetadata(title="Test", description="Test"),
            content="# Main",
            documents=[
                DocumentConfig(name="doc1", content="# Doc 1"),
                DocumentConfig(name="doc2", content="# Doc 2"),
            ],
        )

        files = adapter.generate(prompt, tmp_path)

        assert len(files) >= 2

    def test_generate_v1_all_categories(self, adapter, tmp_path):
        """Test v1 generation with all categories."""
        prompt = UniversalPrompt(
            schema_version="1.0.0",
            metadata=PromptMetadata(title="Test", description="Test"),
            targets=["cline"],
            instructions=Instructions(
                general=["General"], code_style=["Style"], testing=["Test"]
            ),
        )

        files = adapter.generate(prompt, tmp_path)

        assert len(files) > 0

    def test_generate_v1_dry_run(self, adapter, tmp_path):
        """Test v1 dry run."""
        prompt = UniversalPrompt(
            schema_version="1.0.0",
            metadata=PromptMetadata(title="Test", description="Test"),
            targets=["cline"],
            instructions=Instructions(general=["Test"]),
        )

        adapter.generate(prompt, tmp_path, dry_run=True)

    def test_generate_v1_verbose(self, adapter, tmp_path):
        """Test v1 verbose."""
        prompt = UniversalPrompt(
            schema_version="1.0.0",
            metadata=PromptMetadata(title="Test", description="Test"),
            targets=["cline"],
            instructions=Instructions(general=["Test"]),
        )

        files = adapter.generate(prompt, tmp_path, verbose=True)

        assert len(files) > 0

    def test_supports_variables(self, adapter):
        """Test that adapter supports variables."""
        assert adapter.supports_variables() is True

    def test_supports_conditionals(self, adapter):
        """Test that adapter supports conditionals."""
        assert adapter.supports_conditionals() is True
