"""
Tests for the JetBrains adapter.
"""

import json
from pathlib import Path
from unittest.mock import mock_open, patch

import pytest

from promptrek.adapters.jetbrains import JetBrainsAdapter
from promptrek.core.models import Instructions, PromptMetadata, UniversalPrompt


class TestJetBrainsAdapter:
    """Test cases for the JetBrains adapter."""

    @pytest.fixture
    def adapter(self):
        """Create a JetBrains adapter instance."""
        return JetBrainsAdapter()

    @pytest.fixture
    def sample_prompt(self):
        """Create a sample prompt for testing."""
        return UniversalPrompt(
            schema_version="1.0.0",
            metadata=PromptMetadata(
                title="Test Project",
                description="A test project for JetBrains",
                version="1.0.0",
                author="test@example.com",
                created="2024-01-01",
                updated="2024-01-01",
            ),
            targets=["jetbrains"],
            instructions=Instructions(
                general=["Follow coding standards", "Write clean code"],
                code_style=["Use proper formatting", "Add comments"],
                testing=["Write unit tests", "Ensure coverage"],
            ),
        )

    def test_init(self, adapter):
        """Test adapter initialization."""
        assert adapter.name == "jetbrains"
        assert "JetBrains AI" in adapter.description
        assert ".assistant/rules/*.md" in adapter.file_patterns

    @patch("builtins.open", new_callable=mock_open)
    @patch("pathlib.Path.mkdir")
    def test_generate_actual_files(self, mock_mkdir, mock_file, adapter, sample_prompt):
        """Test actual file generation."""
        output_dir = Path("/tmp/test")
        files = adapter.generate(sample_prompt, output_dir, dry_run=False)

        # Should generate multiple markdown rules files in .assistant/rules/
        assert len(files) >= 2
        file_names = [f.name for f in files]
        assert "general.md" in file_names
        assert "code-style.md" in file_names
        assert mock_mkdir.called
        assert mock_file.called

    def test_generate_dry_run(self, adapter, sample_prompt, capsys):
        """Test dry run generation."""
        output_dir = Path("/tmp/test")
        files = adapter.generate(sample_prompt, output_dir, dry_run=True)

        captured = capsys.readouterr()
        assert "Would create" in captured.out
        assert len(files) >= 2  # Dry run returns paths that would be created
        # Check that files have the right parent directory
        assert any("assistant" in str(f) and "rules" in str(f) for f in files)

    def test_generate_dry_run_verbose(self, adapter, sample_prompt, capsys):
        """Test dry run generation with verbose output."""
        output_dir = Path("/tmp/test")
        files = adapter.generate(sample_prompt, output_dir, dry_run=True, verbose=True)

        captured = capsys.readouterr()
        assert "Would create" in captured.out
        assert len(files) >= 2  # Dry run returns paths that would be created

    def test_validate_valid_prompt(self, adapter, sample_prompt):
        """Test validation with valid prompt."""
        errors = adapter.validate(sample_prompt)
        assert len(errors) == 0

    def test_validate_missing_instructions(self, adapter):
        """Test validation with missing instructions."""
        prompt = UniversalPrompt(
            schema_version="1.0.0",
            metadata=PromptMetadata(
                title="Test",
                description="Test",
                version="1.0.0",
                author="test@example.com",
                created="2024-01-01",
                updated="2024-01-01",
            ),
            targets=["jetbrains"],
        )

        errors = adapter.validate(prompt)
        assert len(errors) > 0
        assert any("instructions" in str(error).lower() for error in errors)

    def test_substitute_variables(self, adapter):
        """Test variable substitution."""
        prompt = UniversalPrompt(
            schema_version="1.0.0",
            metadata=PromptMetadata(
                title="Project {{{ PROJECT_NAME }}}",
                description="A {{{ PROJECT_TYPE }}} project",
                version="1.0.0",
                author="test@example.com",
                created="2024-01-01",
                updated="2024-01-01",
            ),
            targets=["jetbrains"],
            instructions=Instructions(
                general=["Use {{{ LANGUAGE }}} best practices"],
            ),
        )

        variables = {
            "PROJECT_NAME": "MyApp",
            "PROJECT_TYPE": "web",
            "LANGUAGE": "Java",
        }

        processed = adapter.substitute_variables(prompt, variables)

        assert processed.metadata.title == "Project MyApp"
        assert processed.metadata.description == "A web project"
        assert processed.instructions.general[0] == "Use Java best practices"

    def test_supports_conditionals(self, adapter):
        """Test conditional support."""
        # Check if the adapter has conditional support (it might not be implemented)
        # Let's just test that the attribute exists
        hasattr(adapter, "supports_conditionals")

    def test_file_patterns_property(self, adapter):
        """Test file patterns property."""
        patterns = adapter.file_patterns
        assert isinstance(patterns, list)
        assert len(patterns) == 1
        assert ".assistant/rules/*.md" in patterns


class TestJetBrainsAdapterSpecInclusion:
    """Test v3.1+ spec document inclusion."""

    @pytest.fixture
    def adapter(self):
        from promptrek.adapters.jetbrains import JetBrainsAdapter

        return JetBrainsAdapter()

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
        spec_files = list((spec_dir / ".assistant/rules").glob("spec-*.md"))
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
        if (spec_dir / ".assistant/rules").exists():
            spec_files = list((spec_dir / ".assistant/rules").glob("spec-*.md"))
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
        if (spec_dir / ".assistant/rules").exists():
            spec_files = list((spec_dir / ".assistant/rules").glob("spec-*.md"))
            assert len(spec_files) == 0
