"""
Test cases for sync command functionality.
"""

import tempfile
from pathlib import Path

import pytest
import yaml

from promptrek.cli.commands.sync import sync_command, _merge_prompts
from promptrek.adapters.continue_adapter import ContinueAdapter
from promptrek.core.models import UniversalPrompt, PromptMetadata, Instructions


class TestSyncCommand:
    """Test sync command functionality."""

    def test_continue_adapter_parse_files(self, tmp_path):
        """Test Continue adapter can parse its own generated files."""
        # Create test Continue files
        config_content = {
            "name": "Test Assistant",
            "systemMessage": "Test Assistant\n\nA test configuration",
            "rules": [
                "Write clean code",
                "Follow conventions",
                "Add comments"
            ]
        }
        
        config_file = tmp_path / "config.yaml"
        with open(config_file, 'w') as f:
            yaml.dump(config_content, f)
            
        # Create rules directory with markdown files
        rules_dir = tmp_path / ".continue" / "rules"
        rules_dir.mkdir(parents=True)
        
        general_md = rules_dir / "general.md"
        general_md.write_text("""# General Coding Rules

- Use descriptive variable names
- Follow project patterns
- Implement error handling

## Additional Guidelines
- Follow project-specific patterns and conventions
- Maintain consistency with existing codebase
- Consider performance and security implications
""")
        
        code_style_md = rules_dir / "code-style.md"
        code_style_md.write_text("""# Code Style Rules

- Use consistent indentation
- Follow linting rules
- Prefer explicit code

## Additional Guidelines
- Follow project-specific patterns and conventions
- Maintain consistency with existing codebase
- Consider performance and security implications
""")
        
        # Test parsing
        adapter = ContinueAdapter()
        parsed_prompt = adapter.parse_files(tmp_path)
        
        assert isinstance(parsed_prompt, UniversalPrompt)
        assert parsed_prompt.metadata.title == "Test Assistant"
        assert parsed_prompt.metadata.description == "A test configuration"
        assert "continue" in parsed_prompt.targets
        
        # Check instructions were parsed
        assert parsed_prompt.instructions is not None
        assert parsed_prompt.instructions.general is not None
        assert len(parsed_prompt.instructions.general) >= 5  # 3 from config + 3 from markdown (minus generic ones)
        assert "Write clean code" in parsed_prompt.instructions.general
        assert "Use descriptive variable names" in parsed_prompt.instructions.general
        
        assert parsed_prompt.instructions.code_style is not None
        assert "Use consistent indentation" in parsed_prompt.instructions.code_style

    def test_merge_prompts(self):
        """Test merging of existing and parsed prompts."""
        # Create existing prompt
        existing = UniversalPrompt(
            schema_version="1.0.0",
            metadata=PromptMetadata(
                title="Existing Assistant",
                description="Original description",
                version="1.0.0",
                author="Original Author",
                created="2024-01-01",
                updated="2024-01-01"
            ),
            targets=["copilot"],
            instructions=Instructions(
                general=["Original instruction"],
                testing=["Original test rule"]
            )
        )
        
        # Create parsed prompt
        parsed = UniversalPrompt(
            schema_version="1.0.0",
            metadata=PromptMetadata(
                title="Parsed Assistant",
                description="Parsed description",
                version="1.0.0",
                author="PrompTrek Sync",
                created="2024-01-02",
                updated="2024-01-02"
            ),
            targets=["continue"],
            instructions=Instructions(
                general=["New instruction", "Original instruction"],  # Duplicate
                code_style=["Style rule"]
            )
        )
        
        # Test merge
        merged = _merge_prompts(existing, parsed, "continue")
        
        # Should keep existing metadata structure but update timestamp
        assert merged.metadata.title == "Existing Assistant"
        assert merged.metadata.description == "Original description"
        assert merged.metadata.updated == "2024-01-02"
        
        # Should merge targets
        assert "copilot" in merged.targets
        assert "continue" in merged.targets
        
        # Should merge instructions without duplicates
        assert "Original instruction" in merged.instructions.general
        assert "New instruction" in merged.instructions.general
        assert len([i for i in merged.instructions.general if i == "Original instruction"]) == 1
        
        # Should preserve existing testing rules
        assert merged.instructions.testing == ["Original test rule"]
        
        # Should add new code_style rules
        assert merged.instructions.code_style == ["Style rule"]

    def test_parse_markdown_file(self, tmp_path):
        """Test parsing individual markdown files."""
        adapter = ContinueAdapter()
        
        md_file = tmp_path / "test.md"
        md_content = """# Test Rules

- Rule one
- Rule two with details
- Rule three

## Additional Guidelines
- Follow project-specific patterns and conventions
- Maintain consistency with existing codebase
- Consider performance and security implications

Some other text that should be ignored.

- Rule four
"""
        md_file.write_text(md_content)
        
        instructions = adapter._parse_markdown_file(md_file)
        
        assert len(instructions) == 4
        assert "Rule one" in instructions
        assert "Rule two with details" in instructions  
        assert "Rule three" in instructions
        assert "Rule four" in instructions
        
        # Should not include the generic guidelines
        assert "Follow project-specific patterns and conventions" not in instructions
        assert "Maintain consistency with existing codebase" not in instructions
        assert "Consider performance and security implications" not in instructions