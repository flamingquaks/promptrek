"""Additional validator tests for coverage."""

import pytest

from promptrek.core.models import (
    Condition,
    ImportConfig,
    Instructions,
    ProjectContext,
    PromptMetadata,
    UniversalPrompt,
    UniversalPromptV2,
)
from promptrek.core.validator import UPFValidator, ValidationResult


class TestValidatorCoverage:
    """Additional tests for validator coverage."""

    def test_validation_result(self):
        """Test ValidationResult class."""
        result = ValidationResult()
        
        assert result.is_valid
        assert not result.has_warnings
        
        result.add_error("Error message")
        assert not result.is_valid
        assert len(result.errors) == 1
        
        result.add_warning("Warning message")
        assert result.has_warnings
        assert len(result.warnings) == 1

    def test_validate_v2_with_empty_document_name(self):
        """Test v2 validation with empty document name."""
        from promptrek.core.models import DocumentConfig
        
        validator = UPFValidator()
        prompt = UniversalPromptV2(
            schema_version="2.0.0",
            metadata=PromptMetadata(title="Test", description="Test"),
            content="# Test",
            documents=[
                DocumentConfig(name="", content="Test content")
            ]
        )
        
        result = validator.validate(prompt)
        assert not result.is_valid
        assert any("empty name" in str(err).lower() for err in result.errors)

    def test_validate_v2_with_empty_document_content(self):
        """Test v2 validation with empty document content."""
        from promptrek.core.models import DocumentConfig
        
        validator = UPFValidator()
        prompt = UniversalPromptV2(
            schema_version="2.0.0",
            metadata=PromptMetadata(title="Test", description="Test"),
            content="# Test",
            documents=[
                DocumentConfig(name="doc1", content="   ")
            ]
        )
        
        result = validator.validate(prompt)
        assert not result.is_valid
        assert any("empty content" in str(err).lower() for err in result.errors)

    def test_validate_v2_with_empty_variables(self):
        """Test v2 validation with empty variable values."""
        validator = UPFValidator()
        prompt = UniversalPromptV2(
            schema_version="2.0.0",
            metadata=PromptMetadata(title="Test", description="Test"),
            content="# Test",
            variables={"EMPTY_VAR": ""}
        )
        
        result = validator.validate(prompt)
        assert result.has_warnings

    def test_validate_schema_version_warning(self):
        """Test schema version validation warning."""
        validator = UPFValidator()
        prompt = UniversalPrompt(
            schema_version="99.0.0",  # Unsupported version
            metadata=PromptMetadata(title="Test", description="Test"),
            targets=["claude"]
        )
        
        result = validator.validate(prompt)
        assert result.has_warnings
        assert any("not be fully supported" in str(w) for w in result.warnings)

    def test_validate_duplicate_targets(self):
        """Test validation with duplicate targets."""
        validator = UPFValidator()
        prompt = UniversalPrompt(
            schema_version="1.0.0",
            metadata=PromptMetadata(title="Test", description="Test"),
            targets=["claude", "claude", "cursor"]
        )
        
        result = validator.validate(prompt)
        assert result.has_warnings
        assert any("duplicate" in str(w).lower() for w in result.warnings)

    def test_validate_empty_metadata_author(self):
        """Test validation with empty author."""
        validator = UPFValidator()
        prompt = UniversalPrompt(
            schema_version="1.0.0",
            metadata=PromptMetadata(
                title="Test",
                description="Test",
                author=""  # Empty author
            ),
            targets=["claude"]
        )
        
        result = validator.validate(prompt)
        assert not result.is_valid

    def test_validate_invalid_semver(self):
        """Test validation with invalid semantic version."""
        validator = UPFValidator()
        prompt = UniversalPrompt(
            schema_version="1.0.0",
            metadata=PromptMetadata(
                title="Test",
                description="Test",
                version="invalid"
            ),
            targets=["claude"]
        )
        
        result = validator.validate(prompt)
        assert result.has_warnings
        assert any("semantic version" in str(w).lower() for w in result.warnings)

    def test_validate_unknown_project_type(self):
        """Test validation with unknown project type."""
        validator = UPFValidator()
        prompt = UniversalPrompt(
            schema_version="1.0.0",
            metadata=PromptMetadata(title="Test", description="Test"),
            targets=["claude"],
            context=ProjectContext(project_type="unknown_type")
        )
        
        result = validator.validate(prompt)
        assert result.has_warnings
        assert any("unknown project type" in str(w).lower() for w in result.warnings)

    def test_validate_empty_technologies(self):
        """Test validation with empty technologies list."""
        validator = UPFValidator()
        prompt = UniversalPrompt(
            schema_version="1.0.0",
            metadata=PromptMetadata(title="Test", description="Test"),
            targets=["claude"],
            context=ProjectContext(technologies=[])
        )
        
        result = validator.validate(prompt)
        assert result.has_warnings

    def test_validate_no_instructions(self):
        """Test validation with no instructions."""
        validator = UPFValidator()
        prompt = UniversalPrompt(
            schema_version="1.0.0",
            metadata=PromptMetadata(title="Test", description="Test"),
            targets=["claude"]
        )
        
        result = validator.validate(prompt)
        assert result.has_warnings
        assert any("no instructions" in str(w).lower() for w in result.warnings)

    def test_validate_empty_instruction_categories(self):
        """Test validation with empty instruction lists."""
        validator = UPFValidator()
        prompt = UniversalPrompt(
            schema_version="1.0.0",
            metadata=PromptMetadata(title="Test", description="Test"),
            targets=["claude"],
            instructions=Instructions(
                general=[],
                code_style=[],
                testing=[]
            )
        )
        
        result = validator.validate(prompt)
        assert result.has_warnings

    def test_validate_empty_examples(self):
        """Test validation with empty examples."""
        validator = UPFValidator()
        prompt = UniversalPrompt(
            schema_version="1.0.0",
            metadata=PromptMetadata(title="Test", description="Test"),
            targets=["claude"],
            examples={"empty_example": ""}
        )
        
        result = validator.validate(prompt)
        assert result.has_warnings

    def test_validate_invalid_variable_names(self):
        """Test validation with invalid variable names."""
        validator = UPFValidator()
        prompt = UniversalPrompt(
            schema_version="1.0.0",
            metadata=PromptMetadata(title="Test", description="Test"),
            targets=["claude"],
            variables={"lowercase_var": "value", "MixedCase": "value"}
        )
        
        result = validator.validate(prompt)
        assert result.has_warnings
        assert any("UPPER_SNAKE_CASE" in str(w) for w in result.warnings)

    def test_validate_import_empty_path(self):
        """Test validation with empty import path."""
        validator = UPFValidator()
        prompt = UniversalPrompt(
            schema_version="1.0.0",
            metadata=PromptMetadata(title="Test", description="Test"),
            targets=["claude"],
            imports=[ImportConfig(path="")]
        )
        
        result = validator.validate(prompt)
        assert not result.is_valid

    def test_validate_import_wrong_extension(self):
        """Test validation with wrong import file extension."""
        validator = UPFValidator()
        prompt = UniversalPrompt(
            schema_version="1.0.0",
            metadata=PromptMetadata(title="Test", description="Test"),
            targets=["claude"],
            imports=[ImportConfig(path="wrong.txt")]
        )
        
        result = validator.validate(prompt)
        assert result.has_warnings

    def test_is_valid_semver(self):
        """Test semver validation helper."""
        validator = UPFValidator()
        
        assert validator._is_valid_semver("1.0.0")
        assert validator._is_valid_semver("2.5.3")
        assert validator._is_valid_semver("10.20.30")
        
        assert not validator._is_valid_semver("1.0")
        assert not validator._is_valid_semver("1.0.0.0")
        assert not validator._is_valid_semver("invalid")
        assert not validator._is_valid_semver("")
        assert not validator._is_valid_semver(None)

    def test_is_valid_variable_name(self):
        """Test variable name validation helper."""
        validator = UPFValidator()
        
        assert validator._is_valid_variable_name("VALID_NAME")
        assert validator._is_valid_variable_name("API_KEY")
        assert validator._is_valid_variable_name("VERSION_1")
        
        assert not validator._is_valid_variable_name("lowercase")
        assert not validator._is_valid_variable_name("MixedCase")
        assert not validator._is_valid_variable_name("123_START")
        assert not validator._is_valid_variable_name("")
        assert not validator._is_valid_variable_name("SPECIAL-CHAR")
