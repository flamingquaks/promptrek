"""
Unit tests for Cline adapter.
"""

from pathlib import Path
from unittest.mock import mock_open, patch

import pytest

from promptrek.adapters.cline import ClineAdapter
from promptrek.core.models import (
    Instructions,
    ProjectContext,
    PromptMetadata,
    UniversalPrompt,
)

from .base_test import TestAdapterBase


class TestClineAdapter(TestAdapterBase):
    """Test Cline adapter."""

    @pytest.fixture
    def adapter(self):
        """Create Cline adapter instance."""
        return ClineAdapter()

    def test_init(self, adapter):
        """Test adapter initialization."""
        assert adapter.name == "cline"
        assert adapter.description == "Cline (.clinerules, .clinerules/*.md)"
        assert ".clinerules" in adapter.file_patterns
        assert ".clinerules/*.md" in adapter.file_patterns

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
            targets=["cline"],
        )
        errors = adapter.validate(prompt)
        assert len(errors) == 1
        assert errors[0].field == "instructions.general"

    def test_validate_missing_title(self, adapter):
        """Test validation with missing title."""
        prompt = UniversalPrompt(
            schema_version="1.0.0",
            metadata=PromptMetadata(
                title="",  # Empty title should fail
                description="Test description",
            ),
        )
        errors = adapter.validate(prompt)
        assert len(errors) >= 1
        # Should have error for missing title or instructions

    def test_should_use_directory_format_simple(self, adapter):
        """Test format selection for simple project."""
        simple_metadata = PromptMetadata(
            title="Simple App", description="Basic web app"
        )
        simple_context = ProjectContext(project_type="web", technologies=["HTML"])
        simple_instructions = Instructions(general=["Keep it simple"])

        simple_prompt = UniversalPrompt(
            schema_version="1.0.0",
            metadata=simple_metadata,
            context=simple_context,
            instructions=simple_instructions,
        )

        # Simple project should use single file format
        assert adapter._should_use_directory_format(simple_prompt) is False

    def test_should_use_directory_format_complex(self, adapter):
        """Test format selection for complex project."""
        complex_metadata = PromptMetadata(
            title="Complex App", description="Complex application"
        )
        complex_context = ProjectContext(
            project_type="enterprise_application",
            technologies=["React", "TypeScript", "Node.js", "PostgreSQL"],
            description="Multi-service architecture",
        )
        complex_instructions = Instructions(
            general=[
                "Follow SOLID principles",
                "Use dependency injection",
                "Implement error handling",
            ],
            code_style=["Use TypeScript", "Follow ESLint", "Use Prettier"],
        )
        complex_examples = {
            "api_endpoint": 'app.get("/users/:id", handler)',
            "component": "const App = () => <div>Hello</div>",
        }

        complex_prompt = UniversalPrompt(
            schema_version="1.0.0",
            metadata=complex_metadata,
            context=complex_context,
            instructions=complex_instructions,
            examples=complex_examples,
        )

        # Complex project should use directory format
        assert adapter._should_use_directory_format(complex_prompt) is True

    def test_generate_rule_files(self, adapter, sample_prompt):
        """Test rule files generation."""
        rule_files = adapter._generate_rule_files(sample_prompt)

        # Should generate at least project overview and coding guidelines
        assert len(rule_files) >= 2
        assert "01-project-overview.md" in rule_files

        # Check project overview content
        overview_content = rule_files["01-project-overview.md"]
        assert sample_prompt.metadata.title in overview_content
        assert "## Project Overview" in overview_content
        assert sample_prompt.metadata.description in overview_content

    @patch("builtins.open", new_callable=mock_open)
    @patch("pathlib.Path.mkdir")
    def test_generate_complex_project_directory_format(
        self, mock_mkdir, mock_file, adapter
    ):
        """Test generation for complex project (directory format)."""
        # Create complex prompt that should trigger directory format
        complex_metadata = PromptMetadata(
            title="Complex App", description="Complex application"
        )
        complex_context = ProjectContext(
            project_type="enterprise_application",
            technologies=["React", "TypeScript", "Node.js", "PostgreSQL"],
            description="Multi-service architecture",
        )
        complex_instructions = Instructions(
            general=[
                "Follow SOLID principles",
                "Use dependency injection",
                "Implement error handling",
            ],
            code_style=["Use TypeScript", "Follow ESLint", "Use Prettier"],
        )
        complex_examples = {
            "api_endpoint": 'app.get("/users/:id", handler)',
            "component": "const App = () => <div>Hello</div>",
        }

        complex_prompt = UniversalPrompt(
            schema_version="1.0.0",
            metadata=complex_metadata,
            context=complex_context,
            instructions=complex_instructions,
            examples=complex_examples,
        )

        output_dir = Path("/tmp/test")
        files = adapter.generate(complex_prompt, output_dir, dry_run=False)

        # Should generate multiple files for complex project
        assert len(files) >= 3

        # Check that files are in .clinerules directory
        for file_path in files:
            assert file_path.parent.name == ".clinerules"
            assert file_path.suffix == ".md"

        # Verify directory creation was called
        mock_mkdir.assert_called_once()

        # Verify files were written (once for each generated file)
        assert mock_file.call_count == len(files)

    @patch("builtins.open", new_callable=mock_open)
    def test_generate_simple_project_single_file_format(self, mock_file, adapter):
        """Test generation for simple project (single file format)."""
        # Create simple prompt that should trigger single file format
        simple_metadata = PromptMetadata(
            title="Simple App", description="Basic web app"
        )
        simple_context = ProjectContext(project_type="web", technologies=["HTML"])
        simple_instructions = Instructions(general=["Keep it simple"])

        simple_prompt = UniversalPrompt(
            schema_version="1.0.0",
            metadata=simple_metadata,
            context=simple_context,
            instructions=simple_instructions,
        )

        output_dir = Path("/tmp/test")
        files = adapter.generate(simple_prompt, output_dir, dry_run=False)

        # Should generate single file for simple project
        assert len(files) == 1
        assert files[0].name == ".clinerules"

        # Verify file was written
        mock_file.assert_called_once()

    def test_build_unified_content(self, adapter):
        """Test unified content generation for single file format."""
        metadata = PromptMetadata(title="Test Project", description="Test description")
        context = ProjectContext(project_type="web", technologies=["React"])
        instructions = Instructions(
            general=["Write clean code"], code_style=["Use TypeScript"]
        )

        prompt = UniversalPrompt(
            schema_version="1.0.0",
            metadata=metadata,
            context=context,
            instructions=instructions,
        )

        content = adapter._build_unified_content(prompt)

        # Check that unified content contains expected sections
        assert "# Test Project" in content
        assert "## Project Overview" in content
        assert "## Project Context" in content
        assert "## Coding Guidelines" in content
        assert "## Code Style" in content
        assert "Test description" in content
        assert "Write clean code" in content
        assert "Use TypeScript" in content
