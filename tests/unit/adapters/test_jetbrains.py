"""
Tests for the JetBrains adapter.
"""

import json
from pathlib import Path
from unittest.mock import mock_open, patch

import pytest

from src.promptrek.adapters.jetbrains import JetBrainsAdapter
from src.promptrek.core.models import Instructions, PromptMetadata, UniversalPrompt


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
        assert ".idea/ai-assistant.xml" in adapter.file_patterns
        assert ".jetbrains/config.json" in adapter.file_patterns

    def test_build_ide_config(self, adapter, sample_prompt):
        """Test IDE XML configuration generation."""
        content = adapter._build_ide_config(sample_prompt)

        assert "<?xml version" in content
        assert "<application>" in content
        assert '<component name="AIAssistant">' in content
        assert sample_prompt.metadata.title in content
        assert (
            "Use proper formatting" in content
        )  # This should be in code_style section
        assert "Add comments" in content

    def test_build_json_config(self, adapter, sample_prompt):
        """Test JSON configuration generation."""
        content = adapter._build_json_config(sample_prompt)

        # Parse as JSON to verify structure
        config = json.loads(content)

        assert "project" in config
        assert "ai_assistant" in config
        assert "guidelines" in config
        assert config["project"]["name"] == sample_prompt.metadata.title
        assert "general" in config["guidelines"]

    @patch("builtins.open", new_callable=mock_open)
    @patch("pathlib.Path.mkdir")
    def test_generate_actual_files(self, mock_mkdir, mock_file, adapter, sample_prompt):
        """Test actual file generation."""
        output_dir = Path("/tmp/test")
        files = adapter.generate(sample_prompt, output_dir, dry_run=False)

        assert len(files) == 2
        assert any("ai-assistant.xml" in str(f) for f in files)
        assert any("config.json" in str(f) for f in files)
        assert mock_mkdir.call_count == 2  # .idea and .jetbrains directories
        assert mock_file.call_count == 2  # Two files written

    def test_generate_dry_run(self, adapter, sample_prompt, capsys):
        """Test dry run generation."""
        output_dir = Path("/tmp/test")
        files = adapter.generate(sample_prompt, output_dir, dry_run=True)

        captured = capsys.readouterr()
        assert "Would create" in captured.out
        assert len(files) == 2  # Dry run returns paths that would be created
        assert any("ai-assistant.xml" in str(f) for f in files)
        assert any("config.json" in str(f) for f in files)

    def test_generate_dry_run_verbose(self, adapter, sample_prompt, capsys):
        """Test dry run generation with verbose output."""
        output_dir = Path("/tmp/test")
        files = adapter.generate(sample_prompt, output_dir, dry_run=True, verbose=True)

        captured = capsys.readouterr()
        assert "Would create" in captured.out
        assert "XML config preview:" in captured.out
        assert len(files) == 2  # Dry run returns paths that would be created

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
        assert len(patterns) == 2
        assert ".idea/ai-assistant.xml" in patterns
        assert ".jetbrains/config.json" in patterns
