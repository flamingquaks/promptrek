"""
Unit tests for editor adapters.
"""

import json
from pathlib import Path
import pytest
from unittest.mock import patch, mock_open

from src.apm.adapters.claude import ClaudeAdapter
from src.apm.adapters.cline import ClineAdapter
from src.apm.adapters.codeium import CodeiumAdapter
from src.apm.adapters.continue_adapter import ContinueAdapter
from src.apm.adapters.copilot import CopilotAdapter
from src.apm.adapters.cursor import CursorAdapter
from src.apm.core.models import (
    UniversalPrompt, PromptMetadata, ProjectContext, Instructions
)
from src.apm.core.exceptions import ValidationError


class TestAdapterBase:
    """Base test class for all adapters."""
    
    @pytest.fixture
    def sample_prompt(self):
        """Create a sample universal prompt for testing."""
        return UniversalPrompt(
            schema_version="1.0.0",
            metadata=PromptMetadata(
                title="Test Project",
                description="A test project for AI assistance",
                version="1.0.0",
                author="test@example.com",
                created="2024-01-01",
                updated="2024-01-01",
                tags=["test", "example"]
            ),
            targets=["copilot", "cursor", "continue"],
            context=ProjectContext(
                project_type="web_application",
                technologies=["typescript", "react", "nodejs"],
                description="A modern web application"
            ),
            instructions=Instructions(
                general=["Write clean, maintainable code", "Follow TypeScript best practices"],
                code_style=["Use consistent indentation", "Prefer const over let"],
                testing=["Write unit tests for all functions", "Use descriptive test names"]
            ),
            examples={
                "component": "const Button = ({ label }: { label: string }) => <button>{label}</button>;",
                "function": "export const formatDate = (date: Date): string => date.toISOString();"
            },
            variables={
                "project_name": "TestProject",
                "author_name": "Test Author"
            }
        )


class TestContinueAdapter(TestAdapterBase):
    """Test Continue editor adapter."""
    
    @pytest.fixture
    def adapter(self):
        """Create Continue adapter instance."""
        return ContinueAdapter()
    
    def test_init(self, adapter):
        """Test adapter initialization."""
        assert adapter.name == "continue"
        assert adapter.description == "Continue (.continue/config.json)"
        assert adapter.file_patterns == [".continue/config.json"]
    
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
                updated="2024-01-01"
            ),
            targets=["continue"]
        )
        errors = adapter.validate(prompt)
        assert len(errors) == 1
        assert errors[0].field == "metadata.description"
    
    def test_build_content(self, adapter, sample_prompt):
        """Test content generation."""
        content = adapter._build_content(sample_prompt)
        
        # Parse as JSON to verify structure
        config = json.loads(content)
        
        assert "models" in config
        assert "systemMessage" in config
        assert "completionOptions" in config
        assert "allowAnonymousTelemetry" in config
        
        assert sample_prompt.metadata.title in config["systemMessage"]
        assert sample_prompt.metadata.description in config["systemMessage"]
        assert "General Instructions:" in config["systemMessage"]
        
    @patch("builtins.open", new_callable=mock_open)
    @patch("pathlib.Path.mkdir")
    def test_generate_actual_files(self, mock_mkdir, mock_file, adapter, sample_prompt):
        """Test actual file generation."""
        output_dir = Path("/tmp/test")
        files = adapter.generate(sample_prompt, output_dir, dry_run=False)
        
        assert len(files) == 1
        assert files[0] == output_dir / ".continue" / "config.json"
        mock_mkdir.assert_called_once()
        mock_file.assert_called_once()
    
    def test_generate_dry_run(self, adapter, sample_prompt, capsys):
        """Test dry run generation."""
        output_dir = Path("/tmp/test")
        files = adapter.generate(sample_prompt, output_dir, dry_run=True)
        
        captured = capsys.readouterr()
        assert "Would create" in captured.out
        assert len(files) == 1


class TestClaudeAdapter(TestAdapterBase):
    """Test Claude adapter."""
    
    @pytest.fixture
    def adapter(self):
        """Create Claude adapter instance."""
        return ClaudeAdapter()
    
    def test_init(self, adapter):
        """Test adapter initialization."""
        assert adapter.name == "claude"
        assert adapter.description == "Claude Code (context-based)"
        assert ".claude/context.md" in adapter.file_patterns
    
    def test_supports_features(self, adapter):
        """Test feature support."""
        assert adapter.supports_variables() is True
        assert adapter.supports_conditionals() is True
    
    def test_validate_with_context(self, adapter, sample_prompt):
        """Test validation with context."""
        errors = adapter.validate(sample_prompt)
        # Should only have warnings, not errors
        warning_errors = [e for e in errors if getattr(e, 'severity', 'error') == 'warning']
        assert len(warning_errors) == 0  # Has context and examples
    
    def test_validate_missing_context(self, adapter):
        """Test validation with missing context."""
        prompt = UniversalPrompt(
            schema_version="1.0.0",
            metadata=PromptMetadata(
                title="Test",
                description="Test description",
                version="1.0.0",
                author="test@example.com",
                created="2024-01-01",
                updated="2024-01-01"
            ),
            targets=["claude"]
        )
        errors = adapter.validate(prompt)
        assert len(errors) == 2  # Missing context and examples warnings
    
    def test_build_content(self, adapter, sample_prompt):
        """Test content generation."""
        content = adapter._build_content(sample_prompt)
        
        assert sample_prompt.metadata.title in content
        assert sample_prompt.metadata.description in content
        assert "## Project Details" in content
        assert "## Development Guidelines" in content
        assert "## Code Examples" in content
        assert "typescript, react, nodejs" in content


class TestClineAdapter(TestAdapterBase):
    """Test Cline adapter."""
    
    @pytest.fixture
    def adapter(self):
        """Create Cline adapter instance."""
        return ClineAdapter()
    
    def test_init(self, adapter):
        """Test adapter initialization."""
        assert adapter.name == "cline"
        assert adapter.description == "Cline (terminal-based)"
        assert ".cline/config.json" in adapter.file_patterns
        assert "cline-context.md" in adapter.file_patterns
    
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
                updated="2024-01-01"
            ),
            targets=["cline"]
        )
        errors = adapter.validate(prompt)
        assert len(errors) == 1
        assert errors[0].field == "instructions.general"
    
    def test_build_config(self, adapter, sample_prompt):
        """Test configuration generation."""
        config_content = adapter._build_config(sample_prompt)
        config = json.loads(config_content)
        
        assert config["name"] == sample_prompt.metadata.title
        assert config["description"] == sample_prompt.metadata.description
        assert config["contextFile"] == "cline-context.md"
        assert "settings" in config
        assert "project" in config
    
    def test_build_context(self, adapter, sample_prompt):
        """Test context generation."""
        content = adapter._build_context(sample_prompt)
        
        assert sample_prompt.metadata.title in content
        assert "## Project Information" in content
        assert "## Development Instructions" in content
        assert "## Terminal Operations" in content
        assert "typescript, react, nodejs" in content
    
    @patch("builtins.open", new_callable=mock_open)
    @patch("pathlib.Path.mkdir")
    def test_generate_multiple_files(self, mock_mkdir, mock_file, adapter, sample_prompt):
        """Test generation of multiple files."""
        output_dir = Path("/tmp/test")
        files = adapter.generate(sample_prompt, output_dir, dry_run=False)
        
        assert len(files) == 2
        assert output_dir / ".cline" / "config.json" in files
        assert output_dir / "cline-context.md" in files


class TestCodeiumAdapter(TestAdapterBase):
    """Test Codeium adapter."""
    
    @pytest.fixture
    def adapter(self):
        """Create Codeium adapter instance."""
        return CodeiumAdapter()
    
    def test_init(self, adapter):
        """Test adapter initialization."""
        assert adapter.name == "codeium"
        assert adapter.description == "Codeium (context-based)"
        assert ".codeium/context.json" in adapter.file_patterns
        assert ".codeiumrc" in adapter.file_patterns
    
    def test_supports_features(self, adapter):
        """Test feature support."""
        assert adapter.supports_variables() is True
        assert adapter.supports_conditionals() is True
    
    def test_validate_with_instructions(self, adapter, sample_prompt):
        """Test validation with instructions."""
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
                updated="2024-01-01"
            ),
            targets=["codeium"]
        )
        errors = adapter.validate(prompt)
        assert len(errors) == 1
        assert getattr(errors[0], 'severity', 'error') == 'warning'
    
    def test_build_context_json(self, adapter, sample_prompt):
        """Test JSON context generation."""
        content = adapter._build_context_json(sample_prompt)
        context = json.loads(content)
        
        assert context["project"]["name"] == sample_prompt.metadata.title
        assert context["project"]["technologies"] == sample_prompt.context.technologies
        assert len(context["guidelines"]) > 0
        assert len(context["patterns"]) > 0
        assert "preferences" in context
    
    def test_build_rc_file(self, adapter, sample_prompt):
        """Test RC file generation."""
        content = adapter._build_rc_file(sample_prompt)
        
        assert sample_prompt.metadata.title in content
        assert "[settings]" in content
        assert "[languages]" in content
        assert "[style]" in content
        assert "[context]" in content
        assert "typescript_enabled=true" in content
        assert "react_enabled=true" in content
    
    @patch("builtins.open", new_callable=mock_open)
    @patch("pathlib.Path.mkdir")
    def test_generate_multiple_files(self, mock_mkdir, mock_file, adapter, sample_prompt):
        """Test generation of multiple files."""
        output_dir = Path("/tmp/test")
        files = adapter.generate(sample_prompt, output_dir, dry_run=False)
        
        assert len(files) == 2
        assert output_dir / ".codeium" / "context.json" in files
        assert output_dir / ".codeiumrc" in files


class TestCopilotAdapter(TestAdapterBase):
    """Test Copilot adapter."""
    
    @pytest.fixture
    def adapter(self):
        """Create Copilot adapter instance."""
        return CopilotAdapter()
    
    def test_init(self, adapter):
        """Test adapter initialization."""
        assert adapter.name == "copilot"
        assert ".github/copilot-instructions.md" in adapter.file_patterns
    
    def test_supports_features(self, adapter):
        """Test feature support."""
        assert adapter.supports_variables() is True
        assert adapter.supports_conditionals() is True


class TestCursorAdapter(TestAdapterBase):
    """Test Cursor adapter."""
    
    @pytest.fixture
    def adapter(self):
        """Create Cursor adapter instance."""
        return CursorAdapter()
    
    def test_init(self, adapter):
        """Test adapter initialization."""
        assert adapter.name == "cursor"
        assert ".cursorrules" in adapter.file_patterns
    
    def test_supports_features(self, adapter):
        """Test feature support."""
        assert adapter.supports_variables() is True
        assert adapter.supports_conditionals() is True


class TestBaseAdapter(TestAdapterBase):
    """Test base adapter functionality."""
    
    @pytest.fixture
    def adapter(self):
        """Create concrete adapter for testing base functionality."""
        return ContinueAdapter()
    
    def test_get_required_variables(self, adapter, sample_prompt):
        """Test getting required variables."""
        # Base implementation returns empty list
        required = adapter.get_required_variables(sample_prompt)
        assert isinstance(required, list)
    
    def test_substitute_variables(self, adapter, sample_prompt):
        """Test variable substitution."""
        # Test that substitution works with variables
        variables = {"extra_var": "extra_value"}
        processed = adapter.substitute_variables(sample_prompt, variables)
        
        assert isinstance(processed, UniversalPrompt)
        assert processed.schema_version == sample_prompt.schema_version
    
    def test_substitute_variables_no_support(self, sample_prompt):
        """Test variable substitution when not supported."""
        # Create adapter that doesn't support variables
        class NoVariablesAdapter(ContinueAdapter):
            def supports_variables(self):
                return False
        
        adapter = NoVariablesAdapter()
        processed = adapter.substitute_variables(sample_prompt, {"var": "value"})
        
        # Should return original prompt unchanged
        assert processed == sample_prompt