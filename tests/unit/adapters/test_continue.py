"""
Unit tests for Continue adapter.
"""

from pathlib import Path
from unittest.mock import mock_open, patch

import pytest

from promptrek.adapters.continue_adapter import ContinueAdapter
from promptrek.core.models import PromptMetadata, UniversalPrompt

from .base_test import TestAdapterBase


class TestContinueAdapter(TestAdapterBase):
    """Test Continue editor adapter."""

    @pytest.fixture
    def adapter(self):
        """Create Continue adapter instance."""
        return ContinueAdapter()

    def test_init(self, adapter):
        """Test adapter initialization."""
        assert adapter.name == "continue"
        assert adapter.description == "Continue (config.yaml, .continue/rules/)"
        assert adapter.file_patterns == ["config.yaml", ".continue/rules/*.md"]

    def test_supports_variables(self, adapter):
        """Test variable support."""
        assert adapter.supports_variables() is True

    def test_supports_conditionals(self, adapter):
        """Test conditional support."""
        assert adapter.supports_conditionals() is True

    def test_validate_valid_prompt(self, adapter, sample_prompt):
        """Test validation of valid prompt."""
        errors = adapter.validate(sample_prompt)
        assert len(errors) == 0

    def test_validate_missing_description(self, adapter):
        """Test validation with missing description."""
        prompt = UniversalPrompt(
            schema_version="1.0.0",
            metadata=PromptMetadata(
                title="Test",
                description="",  # Empty description
                version="1.0.0",
                author="test@example.com",
                created="2024-01-01",
                updated="2024-01-01",
            ),
            targets=["continue"],
        )
        errors = adapter.validate(prompt)
        assert len(errors) == 1
        assert errors[0].field == "metadata.description"

    def test_build_content(self, adapter, sample_prompt):
        """Test content generation."""
        content = adapter._build_content(sample_prompt)

        # Parse as YAML to verify structure
        import yaml

        config = yaml.safe_load(content)

        assert "name" in config
        assert "systemMessage" in config
        assert "completionOptions" in config
        assert "allowAnonymousTelemetry" in config

        assert sample_prompt.metadata.title == config["name"]
        assert sample_prompt.metadata.title in config["systemMessage"]
        assert sample_prompt.metadata.description in config["systemMessage"]

    @patch("builtins.open", new_callable=mock_open)
    @patch("pathlib.Path.mkdir")
    def test_generate_actual_files(self, mock_mkdir, mock_file, adapter, sample_prompt):
        """Test actual file generation."""
        output_dir = Path("/tmp/test")
        files = adapter.generate(sample_prompt, output_dir, dry_run=False)

        # Should generate config.yaml + rules files
        assert len(files) >= 1
        config_file = output_dir / "config.yaml"
        assert config_file in files

        # Check that mkdir and file operations were called
        assert mock_mkdir.called
        assert mock_file.called

    def test_generate_dry_run(self, adapter, sample_prompt, capsys):
        """Test dry run generation."""
        output_dir = Path("/tmp/test")
        files = adapter.generate(sample_prompt, output_dir, dry_run=True)

        captured = capsys.readouterr()
        assert "Would create" in captured.out
        assert len(files) >= 1  # Should generate multiple files

    def test_parse_files_comprehensive(self, adapter, tmp_path):
        """Test comprehensive parsing of Continue files."""
        import yaml
        
        # Create comprehensive test data
        config_content = {
            "name": "Full Test Assistant",
            "version": "2.0.0",
            "systemMessage": "Full Test Assistant\n\nA comprehensive test configuration",
            "rules": [
                "Write comprehensive tests",
                "Use descriptive names",
                "Handle errors gracefully"
            ]
        }
        
        config_file = tmp_path / "config.yaml"
        with open(config_file, "w") as f:
            yaml.dump(config_content, f)
            
        # Create multiple rule files
        rules_dir = tmp_path / ".continue" / "rules"
        rules_dir.mkdir(parents=True)
        
        # General rules
        (rules_dir / "general.md").write_text("""# General Rules
- Use meaningful variable names
- Follow project conventions
- Document complex logic
""")
        
        # Code style rules
        (rules_dir / "code-style.md").write_text("""# Code Style
- Consistent indentation
- Clear naming conventions
- Avoid magic numbers
""")
        
        # Testing rules
        (rules_dir / "testing.md").write_text("""# Testing Guidelines
- Write unit tests for all functions
- Use descriptive test names
- Mock external dependencies
""")
        
        # Security rules
        (rules_dir / "security.md").write_text("""# Security Guidelines
- Validate all inputs
- Use parameterized queries
- Encrypt sensitive data
""")
        
        # Performance rules
        (rules_dir / "performance.md").write_text("""# Performance Guidelines
- Optimize database queries
- Use caching where appropriate
- Profile before optimizing
""")
        
        # Architecture rules
        (rules_dir / "architecture.md").write_text("""# Architecture Guidelines
- Follow SOLID principles
- Use design patterns appropriately
- Maintain loose coupling
""")
        
        # Technology-specific rules
        (rules_dir / "python-rules.md").write_text("""# Python Rules
- Use type hints
- Follow PEP 8
- Prefer list comprehensions
""")
        
        # Unknown category should go to general
        (rules_dir / "custom.md").write_text("""# Custom Rules
- Custom rule one
- Custom rule two
""")
        
        # Test parsing
        parsed = adapter.parse_files(tmp_path)
        
        # Verify metadata
        assert parsed.metadata.title == "Full Test Assistant"
        assert parsed.metadata.description == "A comprehensive test configuration"
        assert parsed.metadata.version == "1.0.0"  # Default version for parsed
        
        # Verify targets
        assert "continue" in parsed.targets
        
        # Verify technologies detected
        assert parsed.context is not None
        assert "python" in parsed.context.technologies
        
        # Verify all instruction categories
        assert parsed.instructions.general is not None
        assert parsed.instructions.code_style is not None
        assert parsed.instructions.testing is not None
        assert parsed.instructions.security is not None
        assert parsed.instructions.performance is not None
        assert parsed.instructions.architecture is not None
        
        # Verify specific instructions
        assert "Write comprehensive tests" in parsed.instructions.general
        assert "Use meaningful variable names" in parsed.instructions.general
        
        assert "Consistent indentation" in parsed.instructions.code_style
        assert "Write unit tests for all functions" in parsed.instructions.testing
        assert "Validate all inputs" in parsed.instructions.security
        assert "Optimize database queries" in parsed.instructions.performance
        assert "Follow SOLID principles" in parsed.instructions.architecture

    def test_parse_files_invalid_yaml(self, adapter, tmp_path):
        """Test parsing with invalid YAML config."""
        # Create invalid YAML
        config_file = tmp_path / "config.yaml"
        config_file.write_text("invalid: yaml: content: [")
        
        # Should handle gracefully and continue with default values
        parsed = adapter.parse_files(tmp_path)
        assert parsed.metadata.title == "Continue AI Assistant"

    def test_parse_files_malformed_markdown(self, adapter, tmp_path):
        """Test parsing with malformed markdown files."""
        rules_dir = tmp_path / ".continue" / "rules"
        rules_dir.mkdir(parents=True)
        
        # Create a file that can't be read (simulate permission error)
        general_md = rules_dir / "general.md"
        general_md.write_text("# General\n- Valid rule")
        
        # Create another markdown file with unusual content
        weird_md = rules_dir / "weird.md"
        weird_md.write_text("No bullet points here\njust random text")
        
        # Should parse successfully, ignoring malformed content
        parsed = adapter.parse_files(tmp_path)
        assert "Valid rule" in parsed.instructions.general

    def test_build_rules_content(self, adapter):
        """Test building markdown rules content."""
        instructions = ["Rule one", "Rule two", "Rule three"]
        content = adapter._build_rules_content("Test Rules", instructions)
        
        assert "# Test Rules" in content
        assert "- Rule one" in content
        assert "- Rule two" in content
        assert "- Rule three" in content
        assert "## Additional Guidelines" in content

    def test_build_tech_rules_content(self, adapter, sample_prompt):
        """Test building technology-specific rules content."""
        content = adapter._build_tech_rules_content("python", sample_prompt)
        
        assert "# Python Rules" in content
        assert "## General Guidelines" in content
        assert "## Python Best Practices" in content
        assert "Use strict TypeScript configuration" not in content  # Should not have TS rules

    def test_build_tech_rules_typescript(self, adapter, sample_prompt):
        """Test building TypeScript-specific rules."""
        content = adapter._build_tech_rules_content("typescript", sample_prompt)
        
        assert "# Typescript Rules" in content
        assert "Use strict TypeScript configuration" in content
        assert "Prefer interfaces over types" in content

    def test_parse_markdown_file_edge_cases(self, adapter, tmp_path):
        """Test markdown parsing edge cases."""
        md_file = tmp_path / "edge_cases.md"
        content = """# Edge Cases

- Normal rule
-Malformed bullet (no space)
- Another normal rule

Not a bullet point

- Rule with trailing spaces   
- Rule with "quotes" and symbols!@#

## Some section
Text that's not a bullet

- Final rule
"""
        md_file.write_text(content)
        
        instructions = adapter._parse_markdown_file(md_file)
        
        # Should only get properly formatted bullet points
        expected_rules = [
            "Normal rule",
            "Another normal rule", 
            "Rule with trailing spaces",
            'Rule with "quotes" and symbols!@#',
            "Final rule"
        ]
        
        for rule in expected_rules:
            assert rule in instructions

        # Should not include malformed bullets  
        assert "Malformed bullet (no space)" not in instructions
