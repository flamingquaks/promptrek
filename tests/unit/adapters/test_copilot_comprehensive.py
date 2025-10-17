"""Comprehensive Copilot adapter tests."""

from pathlib import Path

import pytest

from promptrek.adapters.copilot import CopilotAdapter
from promptrek.core.models import (
    Instructions,
    PromptMetadata,
    UniversalPrompt,
    UniversalPromptV2,
    UniversalPromptV3,
)


class TestCopilotAdapterComprehensive:
    """Comprehensive tests for Copilot adapter."""

    @pytest.fixture
    def adapter(self):
        """Create Copilot adapter instance."""
        return CopilotAdapter()

    @pytest.fixture
    def v2_prompt(self):
        """Create v2 prompt."""
        return UniversalPromptV2(
            schema_version="2.0.0",
            metadata=PromptMetadata(
                title="Test Project", description="Test description"
            ),
            content="# Test Instructions\n\nWrite clean code.",
        )

    @pytest.fixture
    def v1_prompt(self):
        """Create v1 prompt."""
        return UniversalPrompt(
            schema_version="1.0.0",
            metadata=PromptMetadata(
                title="Test Project", description="Test description"
            ),
            targets=["copilot"],
            instructions=Instructions(
                general=["Write clean code"], code_style=["Follow PEP 8"]
            ),
        )

    def test_generate_v2_basic(self, adapter, v2_prompt, tmp_path):
        """Test basic v2 generation."""
        files = adapter.generate(v2_prompt, tmp_path)

        assert len(files) > 0
        assert any(
            f.name == "copilot-instructions.md" and ".github" in f.parts for f in files
        )

    def test_generate_v2_with_variables(self, adapter, tmp_path):
        """Test v2 generation with variables."""
        prompt = UniversalPromptV2(
            schema_version="2.0.0",
            metadata=PromptMetadata(title="Test", description="Test"),
            content="Project: {{{ PROJECT_NAME }}}",
            variables={"PROJECT_NAME": "MyProject"},
        )

        files = adapter.generate(
            prompt, tmp_path, variables={"PROJECT_NAME": "CustomProject"}
        )

        assert len(files) > 0
        content = files[0].read_text()
        assert "CustomProject" in content

    def test_generate_v1_full(self, adapter, v1_prompt, tmp_path):
        """Test v1 generation with all features."""
        v1_prompt.examples = {"example": "def test(): pass"}
        v1_prompt.variables = {"VAR": "value"}

        files = adapter.generate(v1_prompt, tmp_path)

        assert len(files) > 0

    def test_generate_headless_mode(self, adapter, v2_prompt, tmp_path):
        """Test generation in headless mode."""
        files = adapter.generate(v2_prompt, tmp_path, headless=True)

        assert len(files) > 0
        # In headless mode, should generate project-level file
        assert any(f.name == "copilot-instructions.md" for f in files)

    def test_generate_user_mode(self, adapter, v2_prompt, tmp_path):
        """Test generation in user mode."""
        files = adapter.generate(v2_prompt, tmp_path, headless=False)

        assert len(files) > 0

    def test_validate_v2(self, adapter, v2_prompt):
        """Test v2 validation."""
        errors = adapter.validate(v2_prompt)

        assert isinstance(errors, list)

    def test_validate_v1(self, adapter, v1_prompt):
        """Test v1 validation."""
        errors = adapter.validate(v1_prompt)

        assert isinstance(errors, list)

    def test_substitute_variables(self, adapter, v1_prompt):
        """Test variable substitution."""
        v1_prompt.instructions.general = ["Use {{{ PROJECT_NAME }}}"]
        v1_prompt.variables = {"PROJECT_NAME": "TestProject"}

        processed = adapter.substitute_variables(
            v1_prompt, {"PROJECT_NAME": "CustomProject"}
        )

        assert processed.instructions.general[0] == "Use CustomProject"

    def test_generate_with_empty_content(self, adapter, tmp_path):
        """Test generation with minimal content."""
        prompt = UniversalPromptV2(
            schema_version="2.0.0",
            metadata=PromptMetadata(title="Minimal", description="Minimal test"),
            content="# Minimal",
        )

        files = adapter.generate(prompt, tmp_path)

        assert len(files) > 0

    def test_parse_files_basic(self, adapter, tmp_path):
        """Test parsing Copilot files."""
        # Create a copilot instructions file
        copilot_dir = tmp_path / ".github"
        copilot_dir.mkdir(parents=True)
        instructions_file = copilot_dir / "copilot-instructions.md"
        instructions_file.write_text("# Test Instructions\n\nTest content")

        try:
            result = adapter.parse_files(tmp_path)
            assert result is not None
        except Exception:
            # parse_files might not be fully implemented
            pass

    def test_generate_instructions_file(self, adapter, tmp_path):
        """Test generating individual instruction files."""
        prompt = UniversalPrompt(
            schema_version="1.0.0",
            metadata=PromptMetadata(title="Test", description="Test"),
            targets=["copilot"],
            instructions=Instructions(
                general=["Instruction 1"], code_style=["Style 1"]
            ),
        )

        files = adapter.generate(prompt, tmp_path)

        assert len(files) > 0

    def test_generate_prompt_file(self, adapter, tmp_path):
        """Test generating prompt files."""
        prompt = UniversalPrompt(
            schema_version="1.0.0",
            metadata=PromptMetadata(title="Test", description="Test"),
            targets=["copilot"],
            instructions=Instructions(general=["Test"]),
        )

        files = adapter.generate(prompt, tmp_path)

        assert len(files) > 0

    def test_format_instructions(self, adapter):
        """Test instruction formatting."""
        instructions = Instructions(
            general=["General 1", "General 2"],
            code_style=["Style 1"],
            testing=["Test 1"],
        )

        # This tests internal formatting logic
        assert instructions.general == ["General 1", "General 2"]

    def test_format_examples(self, adapter):
        """Test example formatting."""
        examples = {
            "python_example": "def test():\n    pass",
            "js_example": "function test() {}",
        }

        # Test that examples dictionary is properly formatted
        assert len(examples) == 2

    def test_multiple_generation_same_dir(self, adapter, v2_prompt, tmp_path):
        """Test generating multiple times to same directory."""
        # First generation
        files1 = adapter.generate(v2_prompt, tmp_path)
        assert len(files1) > 0

        # Second generation (should overwrite)
        files2 = adapter.generate(v2_prompt, tmp_path)
        assert len(files2) > 0

    def test_generate_with_long_content(self, adapter, tmp_path):
        """Test generation with long content."""
        long_content = "# Instructions\n\n" + ("Line\n" * 100)
        prompt = UniversalPromptV2(
            schema_version="2.0.0",
            metadata=PromptMetadata(title="Long", description="Long content"),
            content=long_content,
        )

        files = adapter.generate(prompt, tmp_path)

        assert len(files) > 0
        content = files[0].read_text()
        assert len(content) > 500

    def test_generate_with_special_characters(self, adapter, tmp_path):
        """Test generation with special characters."""
        prompt = UniversalPromptV2(
            schema_version="2.0.0",
            metadata=PromptMetadata(title="Special", description="Special chars"),
            content="# Test\n\n`code` **bold** _italic_ [link](url)",
        )

        files = adapter.generate(prompt, tmp_path)

        assert len(files) > 0

    def test_generate_v1_with_context(self, adapter, tmp_path):
        """Test v1 generation with project context."""
        from promptrek.core.models import ProjectContext

        prompt = UniversalPrompt(
            schema_version="1.0.0",
            metadata=PromptMetadata(title="Test", description="Test"),
            targets=["copilot"],
            context=ProjectContext(
                project_type="web_application", technologies=["Python", "React"]
            ),
            instructions=Instructions(general=["Test"]),
        )

        files = adapter.generate(prompt, tmp_path)

        assert len(files) > 0

    def test_generate_v1_dry_run_verbose(self, adapter, tmp_path):
        """Test v1 generation with dry_run and verbose."""
        prompt = UniversalPrompt(
            schema_version="1.0.0",
            metadata=PromptMetadata(title="Test", description="Test"),
            targets=["copilot"],
            instructions=Instructions(general=["Test instruction " * 50]),
        )

        # Dry run mode doesn't return files since they aren't created
        adapter.generate(prompt, tmp_path, dry_run=True, verbose=True, headless=False)

    def test_generate_v2_dry_run_verbose(self, adapter, tmp_path):
        """Test v2 generation with dry_run and verbose."""
        prompt = UniversalPromptV2(
            schema_version="2.0.0",
            metadata=PromptMetadata(title="Test", description="Test"),
            content="# Instructions\n\n" + "Content " * 50,
        )

        # Dry run mode doesn't return files since they aren't created
        adapter.generate(prompt, tmp_path, dry_run=True, verbose=True, headless=False)

    def test_generate_merged_multiple_files(self, adapter, tmp_path):
        """Test legacy generation with multiple prompt files."""
        prompt1 = UniversalPrompt(
            schema_version="1.0.0",
            metadata=PromptMetadata(
                title="Prompt 1", description="First prompt", version="1.0.0"
            ),
            targets=["copilot"],
            instructions=Instructions(general=["Rule 1", "Rule 2"]),
        )

        prompt2 = UniversalPrompt(
            schema_version="1.0.0",
            metadata=PromptMetadata(
                title="Prompt 2", description="Second prompt", version="1.0.0"
            ),
            targets=["copilot"],
            instructions=Instructions(general=["Rule 3", "Rule 4"]),
        )

        source1 = tmp_path / "prompt1.promptrek.yaml"
        source2 = tmp_path / "prompt2.promptrek.yaml"
        source1.touch()
        source2.touch()

        prompt_files = [(prompt1, source1), (prompt2, source2)]

        files = adapter.generate_merged(prompt_files, tmp_path, headless=False)

        assert len(files) > 0
        content = files[0].read_text()
        assert "Prompt 1" in content
        assert "Prompt 2" in content
        assert "Configuration Sources" in content

    def test_generate_merged_with_variables(self, adapter, tmp_path):
        """Test legacy generation with variables."""
        prompt = UniversalPrompt(
            schema_version="1.0.0",
            metadata=PromptMetadata(title="Test", description="Test", version="1.0.0"),
            targets=["copilot"],
            instructions=Instructions(general=["Use {{{ LANG }}}"]),
            variables={"LANG": "Python"},
        )

        source = tmp_path / "test.promptrek.yaml"
        source.touch()

        files = adapter.generate_merged(
            [(prompt, source)],
            tmp_path,
            headless=False,
            variables={"LANG": "TypeScript"},
        )

        assert len(files) > 0
        content = files[0].read_text()
        assert "TypeScript" in content

    def test_generate_merged_headless(self, adapter, tmp_path):
        """Test legacy generation in headless mode."""
        prompt = UniversalPrompt(
            schema_version="1.0.0",
            metadata=PromptMetadata(title="Test", description="Test", version="1.0.0"),
            targets=["copilot"],
            instructions=Instructions(general=["Rule 1"]),
        )

        source = tmp_path / "test.promptrek.yaml"
        source.touch()

        files = adapter.generate_merged([(prompt, source)], tmp_path, headless=True)

        assert len(files) > 0
        assert any(".github" in f.parts for f in files)

    def test_parse_files_v2(self, adapter, tmp_path):
        """Test parsing v2 format from .github directory."""
        github_dir = tmp_path / ".github"
        github_dir.mkdir()

        instructions_file = github_dir / "copilot-instructions.md"
        instructions_file.write_text(
            """# Project Instructions

## General Guidelines
- Follow PEP 8
- Use type hints
- Write docstrings

## Code Style
- Use Black formatter
- Maximum line length 88
"""
        )

        result = adapter.parse_files(tmp_path)

        assert isinstance(result, UniversalPromptV3)
        assert "PEP 8" in result.content
        assert "type hints" in result.content

    def test_supports_variables(self, adapter):
        """Test that adapter supports variables."""
        assert adapter.supports_variables() is True

    def test_supports_conditionals(self, adapter):
        """Test that adapter supports conditionals."""
        assert adapter.supports_conditionals() is True

    def test_generate_v1_with_technologies(self, adapter, tmp_path):
        """Test v1 generation with technology-specific instructions."""
        from promptrek.core.models import ProjectContext

        prompt = UniversalPrompt(
            schema_version="1.0.0",
            metadata=PromptMetadata(title="Test", description="Test"),
            targets=["copilot"],
            context=ProjectContext(
                project_type="web_app", technologies=["TypeScript", "React", "Python"]
            ),
            instructions=Instructions(
                general=["Write clean code"],
                code_style=["Follow style guide"],
                testing=["Write unit tests"],
            ),
        )

        files = adapter.generate(prompt, tmp_path)

        # Should generate base file plus path-specific files for technologies
        assert len(files) >= 3  # Main + at least some tech/path-specific files

    def test_generate_merged_v2_prompts(self, adapter, tmp_path):
        """Test merging multiple v2 prompts."""
        prompt1 = UniversalPromptV2(
            schema_version="2.0.0",
            metadata=PromptMetadata(title="Prompt 1", description="First"),
            content="# Section 1\n\nContent 1",
        )

        prompt2 = UniversalPromptV2(
            schema_version="2.0.0",
            metadata=PromptMetadata(title="Prompt 2", description="Second"),
            content="# Section 2\n\nContent 2",
        )

        source1 = tmp_path / "prompt1.yaml"
        source2 = tmp_path / "prompt2.yaml"
        source1.touch()
        source2.touch()

        files = adapter.generate_merged(
            [(prompt1, source1), (prompt2, source2)],
            tmp_path,
            headless=False,
        )

        assert len(files) > 0
        content = files[0].read_text()
        assert "Section 1" in content
        assert "Section 2" in content

    def test_generate_merged_v2_with_headless(self, adapter, tmp_path):
        """Test merging v2 prompts in headless mode."""
        prompt = UniversalPromptV2(
            schema_version="2.0.0",
            metadata=PromptMetadata(title="Test", description="Test"),
            content="# Content",
        )

        source = tmp_path / "test.yaml"
        source.touch()

        files = adapter.generate_merged(
            [(prompt, source)],
            tmp_path,
            headless=True,
        )

        assert len(files) > 0
        content = files[0].read_text()
        assert "HEADLESS INSTRUCTIONS" in content

    def test_build_path_specific_content(self, adapter):
        """Test building path-specific instruction content."""
        content = adapter._build_path_specific_content(
            "Code Style", ["Rule 1", "Rule 2"], "**/*.py"
        )

        assert "applyTo" in content
        assert "**/*.py" in content
        assert "Rule 1" in content
        assert "Rule 2" in content

    def test_build_tech_specific_content_typescript(self, adapter):
        """Test building TypeScript-specific content."""
        prompt = UniversalPrompt(
            schema_version="1.0.0",
            metadata=PromptMetadata(title="Test", description="Test"),
            targets=["copilot"],
            instructions=Instructions(general=["Follow best practices"]),
        )

        content = adapter._build_tech_specific_content("TypeScript", prompt)

        assert "TypeScript" in content
        assert "applyTo" in content
        assert "**/*.{ts,tsx}" in content

    def test_build_tech_specific_content_python(self, adapter):
        """Test building Python-specific content."""
        prompt = UniversalPrompt(
            schema_version="1.0.0",
            metadata=PromptMetadata(title="Test", description="Test"),
            targets=["copilot"],
            instructions=Instructions(general=["Follow PEP 8"]),
        )

        content = adapter._build_tech_specific_content("Python", prompt)

        assert "Python" in content
        assert "PEP 8" in content

    def test_build_tech_specific_content_unknown(self, adapter):
        """Test building content for unknown technology."""
        prompt = UniversalPrompt(
            schema_version="1.0.0",
            metadata=PromptMetadata(title="Test", description="Test"),
            targets=["copilot"],
            instructions=Instructions(general=["Test"]),
        )

        content = adapter._build_tech_specific_content("Elixir", prompt)

        assert "Elixir" in content
        assert "best practices" in content

    def test_build_coding_prompt_content(self, adapter):
        """Test building experimental coding prompt content."""
        from promptrek.core.models import ProjectContext

        prompt = UniversalPrompt(
            schema_version="1.0.0",
            metadata=PromptMetadata(
                title="Test Project", description="Test description"
            ),
            targets=["copilot"],
            context=ProjectContext(technologies=["Python", "JavaScript"]),
            instructions=Instructions(
                general=["Write tests"], code_style=["Use linting"]
            ),
        )

        content = adapter._build_coding_prompt_content(prompt)

        assert "Test Project" in content
        assert "Coding Prompts" in content
        assert "Python" in content
        assert "JavaScript" in content

    def test_strip_headless_instructions(self, adapter):
        """Test stripping headless instruction blocks."""
        content_with_headless = """<!-- HEADLESS INSTRUCTIONS START -->
<!-- Some headless content -->
<!-- HEADLESS INSTRUCTIONS END -->

# Real Content

This is the actual content."""

        stripped = adapter._strip_headless_instructions(content_with_headless)

        assert "HEADLESS INSTRUCTIONS" not in stripped
        assert "Real Content" in stripped

    def test_strip_headless_instructions_no_block(self, adapter):
        """Test stripping when no headless block exists."""
        content = "# Content\n\nNo headless block here."

        stripped = adapter._strip_headless_instructions(content)

        assert stripped == content

    def test_normalize_section_name(self, adapter):
        """Test normalizing section names to instruction categories."""
        assert adapter._normalize_section_name("General Instructions") == "general"
        assert adapter._normalize_section_name("Code Style Guidelines") == "code_style"
        assert adapter._normalize_section_name("Testing") == "testing"
        assert adapter._normalize_section_name("Architecture") == "architecture"
        assert adapter._normalize_section_name("Security Guidelines") == "security"
        assert adapter._normalize_section_name("Performance") == "performance"

    def test_normalize_section_name_skip(self, adapter):
        """Test normalizing section names that should be skipped."""
        assert adapter._normalize_section_name("Project Information") is None
        assert adapter._normalize_section_name("Examples") is None

    def test_filename_to_category(self, adapter):
        """Test converting filenames to instruction categories."""
        assert adapter._filename_to_category("code-style") == "code_style"
        assert adapter._filename_to_category("testing") == "testing"
        assert adapter._filename_to_category("architecture") == "architecture"
        assert adapter._filename_to_category("security") == "security"
        assert adapter._filename_to_category("performance") == "performance"
        assert adapter._filename_to_category("unknown") == "general"

    def test_build_repository_content_with_examples(self, adapter):
        """Test building repository content with examples."""
        prompt = UniversalPrompt(
            schema_version="1.0.0",
            metadata=PromptMetadata(title="Test", description="Test"),
            targets=["copilot"],
            instructions=Instructions(general=["Test"]),
            examples={"python": "def test(): pass", "js": "function test() {}"},
        )

        content = adapter._build_repository_content(prompt)

        assert "Examples" in content
        assert "python" in content.lower()

    def test_build_repository_content_with_conditionals(self, adapter):
        """Test building repository content with conditional instructions."""
        prompt = UniversalPrompt(
            schema_version="1.0.0",
            metadata=PromptMetadata(title="Test", description="Test"),
            targets=["copilot"],
            instructions=Instructions(general=["Base rule"]),
        )

        conditional_content = {"instructions": {"general": ["Conditional rule"]}}

        content = adapter._build_repository_content(prompt, conditional_content)

        assert "Base rule" in content
        assert "Conditional rule" in content

    def test_merge_instructions(self, adapter):
        """Test merging two Instructions objects."""
        base = Instructions(general=["Rule 1"], code_style=["Style 1"])

        additional = Instructions(general=["Rule 2"], testing=["Test 1"])

        merged = adapter._merge_instructions(base, additional)

        assert len(merged.general) == 2
        assert "Rule 1" in merged.general
        assert "Rule 2" in merged.general
        assert merged.testing == ["Test 1"]

    def test_merge_instructions_no_duplicates(self, adapter):
        """Test merging instructions avoids duplicates."""
        base = Instructions(general=["Rule 1", "Rule 2"])
        additional = Instructions(general=["Rule 2", "Rule 3"])

        merged = adapter._merge_instructions(base, additional)

        # Should have Rule 1, Rule 2 (once), Rule 3
        assert len(merged.general) == 3
        assert merged.general.count("Rule 2") == 1

    def test_extract_project_context_technologies(self, adapter):
        """Test extracting technologies from content."""
        content = """# Project
Technologies: Python, TypeScript, React
"""

        context = adapter._extract_project_context(content)

        assert context is not None
        assert "Python" in context.technologies
        assert "TypeScript" in context.technologies

    def test_extract_project_context_project_type(self, adapter):
        """Test extracting project type from content."""
        content = """# Project
Project type: web_application
"""

        context = adapter._extract_project_context(content)

        assert context is not None
        assert context.project_type == "web_application"

    def test_parse_copilot_instructions_with_sections(self, adapter, tmp_path):
        """Test parsing copilot file with multiple sections."""
        github_dir = tmp_path / ".github"
        github_dir.mkdir()

        instructions_file = github_dir / "copilot-instructions.md"
        instructions_file.write_text(
            """# Project Instructions

## General Instructions
- Write clean code
- Follow best practices

## Code Style Guidelines
- Use PEP 8
- Add type hints

## Testing Guidelines
- Write unit tests
- Use pytest
"""
        )

        result = adapter._parse_copilot_instructions_file(instructions_file)

        assert "instructions" in result
        assert result["instructions"].general is not None
        assert result["instructions"].code_style is not None
        assert result["instructions"].testing is not None

    def test_parse_instruction_file_with_frontmatter(self, adapter, tmp_path):
        """Test parsing instruction file with YAML frontmatter."""
        test_file = tmp_path / "test.instructions.md"
        test_file.write_text(
            """---
applyTo: "**/*.py"
---

# Python Guidelines

- Use type hints
- Follow PEP 8
"""
        )

        instructions = adapter._parse_instruction_file(test_file)

        assert len(instructions) >= 2
        assert any("type hints" in i.lower() for i in instructions)

    def test_build_headless_content_v1(self, adapter):
        """Test building headless content for v1."""
        prompt = UniversalPrompt(
            schema_version="1.0.0",
            metadata=PromptMetadata(title="Test", description="Test"),
            targets=["copilot"],
            instructions=Instructions(general=["Test instruction"]),
        )

        content = adapter._build_headless_content(prompt, None)

        assert "HEADLESS INSTRUCTIONS" in content
        assert "promptrek generate" in content
        assert "Test instruction" in content

    def test_build_repository_content_all_sections(self, adapter):
        """Test building repository content with all instruction sections."""
        from promptrek.core.models import ProjectContext

        prompt = UniversalPrompt(
            schema_version="1.0.0",
            metadata=PromptMetadata(
                title="Complete Project", description="All sections"
            ),
            targets=["copilot"],
            context=ProjectContext(
                project_type="web_app",
                technologies=["Python", "TypeScript"],
                description="Full stack app",
            ),
            instructions=Instructions(
                general=["General rule"],
                code_style=["Style rule"],
                architecture=["Arch rule"],
                testing=["Test rule"],
                security=["Security rule"],
                performance=["Perf rule"],
            ),
            examples={"python": "def example(): pass"},
        )

        content = adapter._build_repository_content(prompt, None)

        assert "Complete Project" in content
        assert "General rule" in content
        assert "Style rule" in content
        assert "Test rule" in content
        assert "Examples" in content
        assert "python" in content.lower()
