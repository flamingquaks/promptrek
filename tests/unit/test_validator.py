"""Unit tests for UPF validator."""

from src.promptrek.core.models import UniversalPrompt
from src.promptrek.core.validator import UPFValidator, ValidationResult


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
