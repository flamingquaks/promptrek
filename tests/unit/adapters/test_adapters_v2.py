"""
Unit tests for adapter v2 schema support.
"""

from pathlib import Path

import pytest

from promptrek.adapters.amazon_q import AmazonQAdapter
from promptrek.adapters.claude import ClaudeAdapter
from promptrek.adapters.cline import ClineAdapter
from promptrek.adapters.copilot import CopilotAdapter
from promptrek.adapters.cursor import CursorAdapter
from promptrek.adapters.jetbrains import JetBrainsAdapter
from promptrek.adapters.kiro import KiroAdapter
from promptrek.core.models import DocumentConfig, PromptMetadata, UniversalPromptV2


class TestAdapterV2Base:
    """Base class for v2 adapter tests."""

    @pytest.fixture
    def sample_v2_prompt(self):
        """Create a sample v2 prompt."""
        return UniversalPromptV2(
            schema_version="2.0.0",
            metadata=PromptMetadata(
                title="Test Project",
                description="Test v2 schema",
                version="1.0.0",
                author="Test Author",
                tags=["test", "v2"],
            ),
            content="""# Test Project

## Project Details
**Technologies:** Python, React, TypeScript

## Development Guidelines

### General Principles
- Write clean, maintainable code
- Follow existing patterns
- Add tests for new features

### Code Style
- Use meaningful variable names
- Follow PEP 8 for Python
- Use TypeScript for type safety

## Code Examples

### Function Example
```python
def example_function(param: str) -> str:
    \"\"\"Example function with docstring.\"\"\"
    return param.upper()
```
""",
            variables={"PROJECT_NAME": "test-project", "AUTHOR": "Test Author"},
        )

    @pytest.fixture
    def sample_v2_prompt_with_docs(self):
        """Create a sample v2 prompt with documents."""
        return UniversalPromptV2(
            schema_version="2.0.0",
            metadata=PromptMetadata(
                title="Multi-Doc Project",
                description="Test with multiple documents",
                version="1.0.0",
                author="Test",
            ),
            content="# Main Project Content\n\nThis is the primary content.",
            documents=[
                DocumentConfig(
                    name="general-rules",
                    content="# General Rules\n\n- Rule 1\n- Rule 2\n- Rule 3",
                ),
                DocumentConfig(
                    name="code-style",
                    content="# Code Style Guidelines\n\n- Style 1\n- Style 2",
                ),
                DocumentConfig(
                    name="testing",
                    content="# Testing Standards\n\n- Write unit tests\n- Aim for 80% coverage",
                ),
            ],
        )


class TestClaudeAdapterV2(TestAdapterV2Base):
    """Test Claude adapter with v2 schema."""

    @pytest.fixture
    def adapter(self):
        """Create Claude adapter instance."""
        return ClaudeAdapter()

    def test_generate_v2_basic(self, adapter, sample_v2_prompt, tmp_path):
        """Test basic v2 generation."""
        files = adapter.generate(sample_v2_prompt, tmp_path)

        assert len(files) == 1
        claude_file = tmp_path / ".claude" / "CLAUDE.md"
        assert claude_file.exists()

        content = claude_file.read_text()
        assert "# Test Project" in content
        assert "Python, React, TypeScript" in content
        assert "Write clean, maintainable code" in content

    def test_generate_v2_with_variables(self, adapter, sample_v2_prompt, tmp_path):
        """Test v2 generation with variable substitution."""
        # Modify prompt to include variable placeholders
        sample_v2_prompt.content = (
            "# {{{ PROJECT_TITLE }}}\n\nAuthor: {{{ AUTHOR_NAME }}}"
        )

        variables = {"PROJECT_TITLE": "My App", "AUTHOR_NAME": "John Doe"}
        files = adapter.generate(sample_v2_prompt, tmp_path, variables=variables)

        claude_file = tmp_path / ".claude" / "CLAUDE.md"
        content = claude_file.read_text()

        # Variables should be substituted
        assert "# My App" in content
        assert "Author: John Doe" in content
        assert "{{{ PROJECT_TITLE }}}" not in content

    def test_validate_v2(self, adapter, sample_v2_prompt):
        """Test v2 validation."""
        errors = adapter.validate(sample_v2_prompt)
        # Should have no errors for valid prompt
        assert len(errors) == 0

    def test_validate_v2_missing_content(self, adapter):
        """Test v2 validation with missing content."""
        # Use model_construct to bypass pydantic validation
        # since we want to test the adapter's validation logic specifically
        prompt = UniversalPromptV2.model_construct(
            schema_version="2.0.0",
            metadata=PromptMetadata(
                title="Test",
                description="Test",
                version="1.0.0",
                author="Test",
            ),
            content="",  # Empty content
        )
        errors = adapter.validate(prompt)
        assert len(errors) > 0
        assert any("content" in str(e.field).lower() for e in errors)


class TestCopilotAdapterV2(TestAdapterV2Base):
    """Test Copilot adapter with v2 schema."""

    @pytest.fixture
    def adapter(self):
        """Create Copilot adapter instance."""
        return CopilotAdapter()

    def test_generate_v2_basic(self, adapter, sample_v2_prompt, tmp_path):
        """Test basic v2 generation."""
        files = adapter.generate(sample_v2_prompt, tmp_path)

        assert len(files) == 1
        copilot_file = tmp_path / ".github" / "copilot-instructions.md"
        assert copilot_file.exists()

        content = copilot_file.read_text()
        assert "# Test Project" in content

    def test_generate_v2_headless(self, adapter, sample_v2_prompt, tmp_path):
        """Test v2 generation in headless mode."""
        files = adapter.generate(sample_v2_prompt, tmp_path, headless=True)

        copilot_file = tmp_path / ".github" / "copilot-instructions.md"
        content = copilot_file.read_text()

        # Headless mode includes HTML comments with instructions
        assert "<!-- HEADLESS INSTRUCTIONS START -->" in content
        assert "COPILOT HEADLESS AGENT INSTRUCTIONS:" in content


class TestCursorAdapterV2(TestAdapterV2Base):
    """Test Cursor adapter with v2 schema."""

    @pytest.fixture
    def adapter(self):
        """Create Cursor adapter instance."""
        return CursorAdapter()

    def test_generate_v2_single_file(self, adapter, sample_v2_prompt, tmp_path):
        """Test v2 generation with single file (no documents)."""
        files = adapter.generate(sample_v2_prompt, tmp_path)

        assert len(files) >= 1
        index_file = tmp_path / ".cursor" / "rules" / "index.mdc"
        assert index_file.exists()

        content = index_file.read_text()
        assert "# Test Project" in content

    def test_generate_v2_multi_file(
        self, adapter, sample_v2_prompt_with_docs, tmp_path
    ):
        """Test v2 generation with multiple documents."""
        files = adapter.generate(sample_v2_prompt_with_docs, tmp_path)

        # Should create one file per document
        assert len(files) >= 3
        rules_dir = tmp_path / ".cursor" / "rules"

        general_file = rules_dir / "general-rules.mdc"
        assert general_file.exists()
        assert "Rule 1" in general_file.read_text()

        style_file = rules_dir / "code-style.mdc"
        assert style_file.exists()
        assert "Style 1" in style_file.read_text()


class TestClineAdapterV2(TestAdapterV2Base):
    """Test Cline adapter with v2 schema."""

    @pytest.fixture
    def adapter(self):
        """Create Cline adapter instance."""
        return ClineAdapter()

    def test_generate_v2_single_file(self, adapter, sample_v2_prompt, tmp_path):
        """Test v2 generation with single file."""
        files = adapter.generate(sample_v2_prompt, tmp_path)

        assert len(files) == 1
        cline_file = tmp_path / ".clinerules"
        assert cline_file.exists()

        content = cline_file.read_text()
        assert "# Test Project" in content

    def test_generate_v2_multi_file(
        self, adapter, sample_v2_prompt_with_docs, tmp_path
    ):
        """Test v2 generation with multiple documents."""
        files = adapter.generate(sample_v2_prompt_with_docs, tmp_path)

        # Should create directory format with multiple files
        assert len(files) >= 3
        rules_dir = tmp_path / ".clinerules"

        general_file = rules_dir / "general-rules.md"
        assert general_file.exists()


class TestKiroAdapterV2(TestAdapterV2Base):
    """Test Kiro adapter with v2 schema."""

    @pytest.fixture
    def adapter(self):
        """Create Kiro adapter instance."""
        return KiroAdapter()

    def test_generate_v2_single_file(self, adapter, sample_v2_prompt, tmp_path):
        """Test v2 generation with single file."""
        files = adapter.generate(sample_v2_prompt, tmp_path)

        assert len(files) == 1
        project_file = tmp_path / ".kiro" / "steering" / "project.md"
        assert project_file.exists()

        content = project_file.read_text()
        assert "# Test Project" in content or "Test Project" in content

    def test_generate_v2_multi_file(
        self, adapter, sample_v2_prompt_with_docs, tmp_path
    ):
        """Test v2 generation with multiple documents."""
        files = adapter.generate(sample_v2_prompt_with_docs, tmp_path)

        # Should create one file per document
        assert len(files) >= 3
        steering_dir = tmp_path / ".kiro" / "steering"

        general_file = steering_dir / "general-rules.md"
        assert general_file.exists()
        assert "Rule 1" in general_file.read_text()


class TestJetBrainsAdapterV2(TestAdapterV2Base):
    """Test JetBrains adapter with v2 schema."""

    @pytest.fixture
    def adapter(self):
        """Create JetBrains adapter instance."""
        return JetBrainsAdapter()

    def test_generate_v2_single_file(self, adapter, sample_v2_prompt, tmp_path):
        """Test v2 generation with single file."""
        files = adapter.generate(sample_v2_prompt, tmp_path)

        assert len(files) >= 1
        general_file = tmp_path / ".assistant" / "rules" / "general.md"
        assert general_file.exists()

    def test_generate_v2_multi_file(
        self, adapter, sample_v2_prompt_with_docs, tmp_path
    ):
        """Test v2 generation with multiple documents."""
        files = adapter.generate(sample_v2_prompt_with_docs, tmp_path)

        assert len(files) >= 3
        rules_dir = tmp_path / ".assistant" / "rules"

        general_file = rules_dir / "general-rules.md"
        assert general_file.exists()


class TestAmazonQAdapterV2(TestAdapterV2Base):
    """Test Amazon Q adapter with v2 schema."""

    @pytest.fixture
    def adapter(self):
        """Create Amazon Q adapter instance."""
        return AmazonQAdapter()

    def test_generate_v2_single_file(self, adapter, sample_v2_prompt, tmp_path):
        """Test v2 generation with single file."""
        files = adapter.generate(sample_v2_prompt, tmp_path)

        assert len(files) >= 1
        general_file = tmp_path / ".amazonq" / "rules" / "general.md"
        assert general_file.exists()

    def test_generate_v2_multi_file(
        self, adapter, sample_v2_prompt_with_docs, tmp_path
    ):
        """Test v2 generation with multiple documents."""
        files = adapter.generate(sample_v2_prompt_with_docs, tmp_path)

        assert len(files) >= 3
        rules_dir = tmp_path / ".amazonq" / "rules"

        general_file = rules_dir / "general-rules.md"
        assert general_file.exists()


class TestAdapterV2VariableSubstitution:
    """Test variable substitution in v2 adapters."""

    @pytest.fixture
    def v2_prompt_with_vars(self):
        """Create v2 prompt with variable placeholders."""
        return UniversalPromptV2(
            schema_version="2.0.0",
            metadata=PromptMetadata(
                title="Variable Test",
                description="Test variables",
                version="1.0.0",
                author="Test",
            ),
            content="""# {{{ PROJECT_NAME }}}

Project for {{{ COMPANY }}}

## Technologies
- {{{ TECH_STACK }}}
""",
            variables={
                "PROJECT_NAME": "MyApp",
                "COMPANY": "Acme Corp",
                "TECH_STACK": "Python, React",
            },
        )

    def test_claude_variable_substitution(self, v2_prompt_with_vars, tmp_path):
        """Test Claude adapter variable substitution."""
        adapter = ClaudeAdapter()
        variables = {
            "PROJECT_NAME": "SuperApp",
            "COMPANY": "TechCorp",
            "TECH_STACK": "Go, Vue",
        }
        files = adapter.generate(v2_prompt_with_vars, tmp_path, variables=variables)

        claude_file = tmp_path / ".claude" / "CLAUDE.md"
        content = claude_file.read_text()

        # Variables should be substituted
        assert "# SuperApp" in content
        assert "TechCorp" in content
        assert "Go, Vue" in content
        # Original placeholders should not appear
        assert "{{{ PROJECT_NAME }}}" not in content

    def test_cursor_variable_substitution(self, v2_prompt_with_vars, tmp_path):
        """Test Cursor adapter variable substitution."""
        adapter = CursorAdapter()
        variables = {
            "PROJECT_NAME": "CursorApp",
            "COMPANY": "StartupCo",
            "TECH_STACK": "TypeScript, Node",
        }
        files = adapter.generate(v2_prompt_with_vars, tmp_path, variables=variables)

        index_file = tmp_path / ".cursor" / "rules" / "index.mdc"
        content = index_file.read_text()

        assert "CursorApp" in content
        assert "StartupCo" in content
