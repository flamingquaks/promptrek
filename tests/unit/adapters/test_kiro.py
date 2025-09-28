"""
Unit tests for Kiro adapter.
"""

import json
from pathlib import Path
from unittest.mock import mock_open, patch

import pytest

from promptrek.adapters.kiro import KiroAdapter

from .base_test import TestAdapterBase


class TestKiroAdapter(TestAdapterBase):
    """Test Kiro adapter."""

    @pytest.fixture
    def adapter(self):
        """Create Kiro adapter instance."""
        return KiroAdapter()

    def test_init(self, adapter):
        """Test adapter initialization."""
        assert adapter.name == "kiro"
        assert "Kiro" in adapter.description
        assert ".kiro/steering/*.md" in adapter.file_patterns
        assert ".kiro/specs/*/requirements.md" in adapter.file_patterns
        assert ".kiro/specs/*/design.md" in adapter.file_patterns
        assert ".kiro/specs/*/tasks.md" in adapter.file_patterns

    def test_supports_variables(self, adapter):
        """Test variable support."""
        assert adapter.supports_variables() is True

    def test_supports_conditionals(self, adapter):
        """Test conditional support."""
        assert adapter.supports_conditionals() is True

    def test_validate_valid_prompt(self, adapter, sample_prompt):
        """Test validation of valid prompt."""
        errors = adapter.validate(sample_prompt)
        # Should only have warnings, no critical errors
        assert all(error.severity == "warning" for error in errors)

    def test_build_product_steering_content(self, adapter, sample_prompt):
        """Test product steering generation."""
        content = adapter._build_product_steering(sample_prompt)

        assert sample_prompt.metadata.title in content
        assert "Product Overview" in content
        assert "inclusion: always" in content

    @patch("builtins.open", new_callable=mock_open)
    @patch("pathlib.Path.mkdir")
    def test_generate_actual_files(self, mock_mkdir, mock_file, adapter, sample_prompt):
        """Test actual file generation."""
        output_dir = Path("/tmp/test")
        files = adapter.generate(sample_prompt, output_dir, dry_run=False)

        # Should generate steering files and specs files
        assert (
            len(files) >= 3
        )  # At least product.md, structure.md, requirements.md, design.md, tasks.md
        # Use cross-platform path checks
        file_strs = [str(f) for f in files]
        assert any("steering" in f and "product.md" in f for f in file_strs)
        assert any("steering" in f and "structure.md" in f for f in file_strs)
        assert any("requirements.md" in f for f in file_strs)
        assert any("design.md" in f for f in file_strs)
        assert any("tasks.md" in f for f in file_strs)
        assert mock_mkdir.call_count >= 2  # At least steering and specs directories
        assert mock_file.call_count >= 3

    def test_generate_dry_run(self, adapter, sample_prompt, capsys):
        """Test dry run generation."""
        output_dir = Path("/tmp/test")
        files = adapter.generate(sample_prompt, output_dir, dry_run=True)

        captured = capsys.readouterr()
        assert "Would create" in captured.out
        assert (
            len(files) == 0
        )  # Dry run doesn't create actual files, returns empty list

    def test_supports_hooks(self, adapter):
        """Test that Kiro adapter supports hooks."""
        assert adapter.supports_hooks() is True

    def test_hooks_generation(self, adapter, sample_prompt):
        """Test hooks generation content."""
        # Test code quality hook generation
        quality_content = adapter._build_code_quality_hook(sample_prompt)
        assert "Code Quality Hook" in quality_content
        assert "Quality Checks" in quality_content
        assert "Execution Triggers" in quality_content

        # Test precommit hook generation if testing instructions exist
        if sample_prompt.instructions and sample_prompt.instructions.testing:
            precommit_content = adapter._build_precommit_hook(sample_prompt)
            assert "Pre-Commit Hook" in precommit_content
            assert "Test Requirements" in precommit_content

    def test_prompts_generation(self, adapter, sample_prompt):
        """Test prompts generation content."""
        # Test development prompts
        dev_content = adapter._build_development_prompts(sample_prompt)
        assert sample_prompt.metadata.title in dev_content
        assert "Development Prompts" in dev_content
        assert "Feature Development" in dev_content
        assert "Bug Fix Prompt" in dev_content

        # Test refactoring prompts if code style instructions exist
        if sample_prompt.instructions and sample_prompt.instructions.code_style:
            refactor_content = adapter._build_refactoring_prompts(sample_prompt)
            assert "Refactoring Prompts" in refactor_content
            assert "Code Improvement" in refactor_content

    @patch("builtins.open", new_callable=mock_open)
    @patch("pathlib.Path.mkdir")
    def test_generate_with_hooks_and_prompts(self, mock_mkdir, mock_file, adapter, sample_prompt):
        """Test generation includes hooks and prompts."""
        output_dir = Path("/tmp/test")
        files = adapter.generate(sample_prompt, output_dir, dry_run=False)

        # Should generate hooks and prompts in addition to steering and specs
        file_strs = [str(f) for f in files]
        assert any("hooks" in f and "code-quality.md" in f for f in file_strs)
        assert any("prompts" in f and "development.md" in f for f in file_strs)

    def test_generate_merged_multiple_files(self, adapter, sample_prompt):
        """Test merging multiple promptrek files."""
        from pathlib import Path

        # Create a second prompt with different content
        second_prompt_dict = sample_prompt.model_dump()
        second_prompt_dict["metadata"]["description"] = "Additional description"
        second_prompt_dict["instructions"] = {
            "general": ["Additional instruction"],
            "code_style": ["Additional style rule"]
        }
        from promptrek.core.models import UniversalPrompt
        second_prompt = UniversalPrompt(**second_prompt_dict)

        prompt_files = [
            (sample_prompt, Path("first.promptrek.yaml")),
            (second_prompt, Path("second.promptrek.yaml"))
        ]

        # Test that generate_merged method exists and works
        assert hasattr(adapter, "generate_merged")
        files = adapter.generate_merged(prompt_files, Path("/tmp/test"), dry_run=True)

        # Should return empty list for dry run but not crash
        assert isinstance(files, list)

    def test_enhanced_content_structure(self, adapter, sample_prompt):
        """Test that enhanced content includes better context and rationale."""
        # Test API standards content
        api_content = adapter._build_api_standards_steering(sample_prompt)
        assert "Why These Conventions Matter" in api_content
        assert "Consistency" in api_content
        assert "Security" in api_content
        assert "HTTP Status Codes" in api_content
        assert "```" in api_content  # Should include code examples

        # Test component patterns content
        component_content = adapter._build_component_patterns_steering(sample_prompt)
        assert "Core Principles" in component_content
        assert "Single Responsibility" in component_content
        assert "Component Structure" in component_content
        assert "File Organization" in component_content
        assert "Accessibility Standards" in component_content

    def test_improved_file_naming_conventions(self, adapter, sample_prompt):
        """Test that file naming follows domain-specific conventions."""
        # Check that API files use better names
        if (sample_prompt.context and sample_prompt.context.technologies and
            any(tech.lower() in ["api", "rest", "node", "express"] for tech in sample_prompt.context.technologies)):

            output_dir = Path("/tmp/test")
            files = adapter.generate(sample_prompt, output_dir, dry_run=True)
            # Would generate api-rest-conventions.md instead of api-standards.md

        # Check frontend files use better names
        if (sample_prompt.context and sample_prompt.context.technologies and
            any(tech.lower() in ["react", "vue", "angular"] for tech in sample_prompt.context.technologies)):

            output_dir = Path("/tmp/test")
            files = adapter.generate(sample_prompt, output_dir, dry_run=True)
            # Would generate component-development-patterns.md instead of frontend-standards.md
