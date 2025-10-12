"""Test exception classes."""

import pytest

from promptrek.core.exceptions import (
    AdapterError,
    AdapterGenerationError,
    CLIError,
    PrompTrekError,
    UPFError,
    UPFFileNotFoundError,
    UPFParsingError,
)


class TestExceptions:
    """Test exception hierarchy."""

    def test_base_exception(self):
        """Test PrompTrekError base exception."""
        with pytest.raises(PrompTrekError) as exc_info:
            raise PrompTrekError("Base error")

        assert "Base error" in str(exc_info.value)

    def test_cli_error(self):
        """Test CLIError exception."""
        with pytest.raises(CLIError) as exc_info:
            raise CLIError("CLI error")

        assert "CLI error" in str(exc_info.value)
        assert isinstance(exc_info.value, PrompTrekError)

    def test_upf_error(self):
        """Test UPFError exception."""
        with pytest.raises(UPFError) as exc_info:
            raise UPFError("UPF error")

        assert "UPF error" in str(exc_info.value)
        assert isinstance(exc_info.value, PrompTrekError)

    def test_upf_parsing_error(self):
        """Test UPFParsingError exception."""
        with pytest.raises(UPFParsingError) as exc_info:
            raise UPFParsingError("UPF parsing failed")

        assert "UPF parsing failed" in str(exc_info.value)
        assert isinstance(exc_info.value, UPFError)

    def test_upf_file_not_found_error(self):
        """Test UPFFileNotFoundError exception."""
        with pytest.raises(UPFFileNotFoundError) as exc_info:
            raise UPFFileNotFoundError("File not found")

        assert "File not found" in str(exc_info.value)
        assert isinstance(exc_info.value, UPFError)

    def test_adapter_error(self):
        """Test AdapterError exception."""
        with pytest.raises(AdapterError) as exc_info:
            raise AdapterError("Adapter error")

        assert "Adapter error" in str(exc_info.value)
        assert isinstance(exc_info.value, PrompTrekError)

    def test_adapter_generation_error(self):
        """Test AdapterGenerationError exception."""
        with pytest.raises(AdapterGenerationError) as exc_info:
            raise AdapterGenerationError("Generation error")

        assert "Generation error" in str(exc_info.value)
        assert isinstance(exc_info.value, AdapterError)

    def test_exception_inheritance(self):
        """Test exception inheritance chain."""
        # All custom exceptions should inherit from PrompTrekError
        assert issubclass(CLIError, PrompTrekError)
        assert issubclass(UPFError, PrompTrekError)
        assert issubclass(AdapterError, PrompTrekError)

        # UPF exception hierarchy
        assert issubclass(UPFParsingError, UPFError)
        assert issubclass(UPFFileNotFoundError, UPFError)

        # Adapter exception hierarchy
        assert issubclass(AdapterGenerationError, AdapterError)

    def test_exception_with_cause(self):
        """Test exception chaining."""
        try:
            try:
                raise ValueError("Original error")
            except ValueError as e:
                raise UPFParsingError("Parsing failed") from e
        except UPFParsingError as exc:
            assert "Parsing failed" in str(exc)
            assert exc.__cause__ is not None
            assert isinstance(exc.__cause__, ValueError)
