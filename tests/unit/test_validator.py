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

    def test_validate_empty_targets_list(self):
        """Test validation catches empty targets list."""
        from promptrek.core.models import PromptMetadata, UniversalPrompt

        # Create prompt with empty targets list
        prompt = UniversalPrompt.model_construct(
            schema_version="1.0.0",
            metadata=PromptMetadata(
                title="Test", description="Test", version="1.0.0", author="Test"
            ),
            targets=[],  # Empty list
            instructions=None,
        )
        validator = UPFValidator()
        result = validator.validate(prompt)

        assert result.is_valid is False
        assert any("At least one target editor" in error for error in result.errors)

    def test_validate_empty_condition_if_clause(self):
        """Test validation catches empty if clause in conditions."""
        from promptrek.core.models import Condition, PromptMetadata, UniversalPrompt

        # Create condition with empty if_condition
        condition = Condition.model_construct(
            if_condition="   ", then={"test": "value"}
        )

        prompt = UniversalPrompt.model_construct(
            schema_version="1.0.0",
            metadata=PromptMetadata(
                title="Test", description="Test", version="1.0.0", author="Test"
            ),
            targets=["claude"],
            conditions=[condition],
        )
        validator = UPFValidator()
        result = validator.validate(prompt)

        assert result.is_valid is False
        assert any("empty 'if' clause" in error for error in result.errors)

    def test_validate_empty_import_path(self):
        """Test validation catches empty import path."""
        from promptrek.core.models import ImportConfig, PromptMetadata, UniversalPrompt

        # Create import with empty path
        import_config = ImportConfig.model_construct(path="   ")

        prompt = UniversalPrompt.model_construct(
            schema_version="1.0.0",
            metadata=PromptMetadata(
                title="Test", description="Test", version="1.0.0", author="Test"
            ),
            targets=["claude"],
            imports=[import_config],
        )
        validator = UPFValidator()
        result = validator.validate(prompt)

        assert result.is_valid is False
        assert any("empty path" in error for error in result.errors)

    def test_validate_import_wrong_extension(self):
        """Test validation warns about import with wrong extension."""
        from promptrek.core.models import ImportConfig, PromptMetadata, UniversalPrompt

        # Create import with wrong extension
        import_config = ImportConfig(path="other.yaml")

        prompt = UniversalPrompt.model_construct(
            schema_version="1.0.0",
            metadata=PromptMetadata(
                title="Test", description="Test", version="1.0.0", author="Test"
            ),
            targets=["claude"],
            imports=[import_config],
        )
        validator = UPFValidator()
        result = validator.validate(prompt)

        assert result.has_warnings is True
        assert any(
            "should end with .promptrek" in warning for warning in result.warnings
        )


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

    def test_validate_v3_document_empty_content(self):
        """Test validation catches document with empty content."""
        from promptrek.core.models import DocumentConfig

        prompt = UniversalPromptV3.model_construct(
            schema_version="3.0.0",
            metadata=PromptMetadata(
                title="Test Docs", description="Test docs validation", version="1.0.0"
            ),
            content="# Main\n\nMain content.",
            documents=[
                DocumentConfig(name="test", content="   "),
            ],
        )
        validator = UPFValidator()
        result = validator.validate(prompt)

        assert result.is_valid is False
        assert any("Document 1 has empty content" in error for error in result.errors)

    def test_validate_v3_with_multiple_documents(self):
        """Test validation with multiple documents."""
        from promptrek.core.models import DocumentConfig

        prompt = UniversalPromptV3(
            schema_version="3.0.0",
            metadata=PromptMetadata(
                title="Test Docs", description="Test docs validation", version="1.0.0"
            ),
            content="# Main\n\nMain content.",
            documents=[
                DocumentConfig(name="doc1", content="# Doc1\n\nContent 1."),
                DocumentConfig(name="doc2", content="# Doc2\n\nContent 2."),
                DocumentConfig(name="doc3", content="# Doc3\n\nContent 3."),
            ],
        )
        validator = UPFValidator()
        result = validator.validate(prompt)

        assert result.is_valid is True
        assert len(result.errors) == 0


class TestValidationEdgeCases:
    """Test edge cases in validator."""

    def test_validate_duplicate_targets(self, sample_upf_data):
        """Test validation when targets contains duplicates."""
        sample_upf_data["targets"] = ["claude", "claude", "cursor"]
        prompt = UniversalPrompt(**sample_upf_data)
        validator = UPFValidator()
        result = validator.validate(prompt)

        assert result.has_warnings is True
        assert any("Duplicate target editors" in warning for warning in result.warnings)

    def test_is_valid_variable_name_empty(self):
        """Test variable name validation with empty string."""
        validator = UPFValidator()
        assert validator._is_valid_variable_name("") is False

    def test_is_valid_variable_name_valid(self):
        """Test variable name validation with valid names."""
        validator = UPFValidator()
        assert validator._is_valid_variable_name("PROJECT_NAME") is True
        assert validator._is_valid_variable_name("API_KEY_123") is True
        assert validator._is_valid_variable_name("TEST_VAR") is True

    def test_is_valid_variable_name_invalid(self):
        """Test variable name validation with invalid names."""
        validator = UPFValidator()
        assert validator._is_valid_variable_name("lowercase") is False
        assert validator._is_valid_variable_name("MixedCase") is False
        assert validator._is_valid_variable_name("123STARTS_WITH_NUMBER") is False

    def test_is_valid_variable_name_with_numbers(self):
        """Test variable name validation with numbers."""
        validator = UPFValidator()
        assert validator._is_valid_variable_name("VAR_123") is True
        assert validator._is_valid_variable_name("API_V2_KEY") is True
