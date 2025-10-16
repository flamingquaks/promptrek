"""Unit tests for UPF validator."""

from promptrek.core.models import PromptMetadata, UniversalPrompt, UniversalPromptV3
from promptrek.core.validator import UPFValidator, ValidationResult


class TestValidationResult:
    """Test ValidationResult class."""

    def test_empty_result_is_valid(self):
        """Test empty result is valid."""
        result = ValidationResult()
        assert result.is_valid is True
        assert result.has_warnings is False

    def test_result_with_errors_is_invalid(self):
        """Test result with errors is invalid."""
        result = ValidationResult()
        result.add_error("Test error")
        assert result.is_valid is False

    def test_result_with_warnings_has_warnings(self):
        """Test result with warnings."""
        result = ValidationResult()
        result.add_warning("Test warning")
        assert result.has_warnings is True
        assert result.is_valid is True  # warnings don't make it invalid


class TestUPFValidator:
    """Test UPFValidator functionality."""

    def test_validate_valid_prompt(self, sample_upf_data):
        """Test validation of valid prompt."""
        prompt = UniversalPrompt(**sample_upf_data)
        validator = UPFValidator()
        result = validator.validate(prompt)

        assert result.is_valid is True

    def test_validate_empty_title_error(self, sample_upf_data):
        """Test validation catches empty title."""
        sample_upf_data["metadata"]["title"] = ""
        prompt = UniversalPrompt(**sample_upf_data)
        validator = UPFValidator()
        result = validator.validate(prompt)

        assert result.is_valid is False
        assert any("title cannot be empty" in error for error in result.errors)

    def test_validate_unknown_editor_warning(self, sample_upf_data):
        """Test validation warns about unknown editors."""
        sample_upf_data["targets"] = ["unknown_editor"]
        prompt = UniversalPrompt(**sample_upf_data)
        validator = UPFValidator()
        result = validator.validate(prompt)

        assert result.has_warnings is True
        assert any("Unknown target editors" in warning for warning in result.warnings)

    def test_validate_unknown_project_type_warning(self, sample_upf_data):
        """Test validation warns about unknown project types."""
        sample_upf_data["context"]["project_type"] = "unknown_type"
        prompt = UniversalPrompt(**sample_upf_data)
        validator = UPFValidator()
        result = validator.validate(prompt)

        assert result.has_warnings is True
        assert any("Unknown project type" in warning for warning in result.warnings)

    def test_validate_invalid_variable_names(self, sample_upf_data):
        """Test validation warns about invalid variable names."""
        sample_upf_data["variables"] = {
            "lowercase_var": "value",  # Should be UPPER_SNAKE_CASE
            "VALID_VAR": "value",
        }
        prompt = UniversalPrompt(**sample_upf_data)
        validator = UPFValidator()
        result = validator.validate(prompt)

        assert result.has_warnings is True
        assert any("Invalid variable names" in warning for warning in result.warnings)

    def test_validate_empty_examples(self, sample_upf_data):
        """Test validation warns about empty examples."""
        sample_upf_data["examples"] = {
            "empty_example": "",
            "valid_example": "some content",
        }
        prompt = UniversalPrompt(**sample_upf_data)
        validator = UPFValidator()
        result = validator.validate(prompt)

        assert result.has_warnings is True
        assert any("Empty examples found" in warning for warning in result.warnings)

    def test_validate_no_instructions_warning(self, sample_upf_data):
        """Test validation warns when no instructions provided."""
        del sample_upf_data["instructions"]
        prompt = UniversalPrompt(**sample_upf_data)
        validator = UPFValidator()
        result = validator.validate(prompt)

        assert result.has_warnings is True
        assert any("No instructions provided" in warning for warning in result.warnings)

    def test_validate_editor_specific_mismatch(self, sample_upf_data):
        """Test validation warns about editor-specific config for non-target editors."""
        sample_upf_data["editor_specific"] = {
            "vim": {"additional_instructions": ["Test instruction"]}  # Not in targets
        }
        prompt = UniversalPrompt(**sample_upf_data)
        validator = UPFValidator()
        result = validator.validate(prompt)

        assert result.has_warnings is True
        assert any("non-target editors" in warning for warning in result.warnings)


class TestUPFValidatorV3:
    """Test UPFValidator functionality for v3 schema."""

    def test_validate_v3_valid_prompt(self):
        """Test validation of valid v3 prompt."""
        prompt = UniversalPromptV3(
            schema_version="3.0.0",
            metadata=PromptMetadata(
                title="Test V3", description="Test v3 validation", version="1.0.0"
            ),
            content="# Test Content\n\nValid content here.",
        )
        validator = UPFValidator()
        result = validator.validate(prompt)

        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_v3_empty_content_error(self):
        """Test validation catches empty content in v3."""
        prompt = UniversalPromptV3.model_construct(
            schema_version="3.0.0",
            metadata=PromptMetadata(
                title="Test V3", description="Test v3 validation", version="1.0.0"
            ),
            content="   ",  # Whitespace only
        )
        validator = UPFValidator()
        result = validator.validate(prompt)

        assert result.is_valid is False
        assert any("Content cannot be empty" in error for error in result.errors)

    def test_validate_v3_with_mcp_servers(self):
        """Test validation of v3 prompt with MCP servers."""
        prompt = UniversalPromptV3(
            schema_version="3.0.0",
            metadata=PromptMetadata(
                title="Test MCP", description="Test MCP validation", version="1.0.0"
            ),
            content="# Test\n\nContent.",
            mcp_servers=[
                {"name": "filesystem", "command": "npx", "args": ["-y", "server"]},
                {"name": "api", "command": "node", "args": ["api.js"]},
            ],
        )
        validator = UPFValidator()
        result = validator.validate(prompt)

        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_v3_mcp_server_missing_name(self):
        """Test validation catches MCP server without name."""
        prompt = UniversalPromptV3(
            schema_version="3.0.0",
            metadata=PromptMetadata(
                title="Test MCP", description="Test MCP validation", version="1.0.0"
            ),
            content="# Test\n\nContent.",
            mcp_servers=[
                {"name": "", "command": "npx"},  # Empty name
            ],
        )
        validator = UPFValidator()
        result = validator.validate(prompt)

        assert result.is_valid is False
        assert any("MCP server 1 has no name" in error for error in result.errors)

    def test_validate_v3_mcp_server_missing_command(self):
        """Test validation catches MCP server without command."""
        prompt = UniversalPromptV3(
            schema_version="3.0.0",
            metadata=PromptMetadata(
                title="Test MCP", description="Test MCP validation", version="1.0.0"
            ),
            content="# Test\n\nContent.",
            mcp_servers=[
                {"name": "test", "command": ""},  # Empty command
            ],
        )
        validator = UPFValidator()
        result = validator.validate(prompt)

        assert result.is_valid is False
        assert any("MCP server 1 has no command" in error for error in result.errors)

    def test_validate_v3_with_documents(self):
        """Test validation of v3 prompt with documents."""
        from promptrek.core.models import DocumentConfig

        prompt = UniversalPromptV3(
            schema_version="3.0.0",
            metadata=PromptMetadata(
                title="Test Docs", description="Test docs validation", version="1.0.0"
            ),
            content="# Main\n\nMain content.",
            documents=[
                DocumentConfig(name="general", content="# General\n\nGeneral rules."),
                DocumentConfig(name="style", content="# Style\n\nStyle rules."),
            ],
        )
        validator = UPFValidator()
        result = validator.validate(prompt)

        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_v3_document_empty_name(self):
        """Test validation catches document with empty name."""
        from promptrek.core.models import DocumentConfig

        prompt = UniversalPromptV3.model_construct(
            schema_version="3.0.0",
            metadata=PromptMetadata(
                title="Test Docs", description="Test docs validation", version="1.0.0"
            ),
            content="# Main\n\nMain content.",
            documents=[
                DocumentConfig(name="", content="# Content\n\nContent."),
            ],
        )
        validator = UPFValidator()
        result = validator.validate(prompt)

        assert result.is_valid is False
        assert any("Document 1 has empty name" in error for error in result.errors)
