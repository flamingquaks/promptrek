"""
Custom exceptions for PrompTrek.

Defines specific exception types for different error conditions
to provide better error handling and user feedback.
"""


class PrompTrekError(Exception):
    """Base exception for all PrompTrek errors."""

    pass


class UPFError(PrompTrekError):
    """Base exception for UPF-related errors."""

    pass


class UPFParsingError(UPFError):
    """Raised when UPF file parsing fails."""

    pass


class UPFFileNotFoundError(UPFError):
    """Raised when a UPF file is not found."""

    pass


class UPFValidationError(UPFError):
    """Raised when UPF validation fails."""

    pass


class ValidationError(PrompTrekError):
    """Represents a validation error with field and message information."""

    def __init__(self, field: str, message: str, severity: str = "error"):
        """
        Initialize a validation error.

        Args:
            field: The field that failed validation
            message: The validation error message
            severity: The severity level (error, warning)
        """
        self.field = field
        self.message = message
        self.severity = severity
        super().__init__(f"{field}: {message}")


class TemplateError(PrompTrekError):
    """Base exception for template-related errors."""

    pass


class TemplateNotFoundError(TemplateError):
    """Raised when a template file is not found."""

    pass


class TemplateRenderingError(TemplateError):
    """Raised when template rendering fails."""

    pass


class AdapterError(PrompTrekError):
    """Base exception for adapter-related errors."""

    pass


class AdapterNotFoundError(AdapterError):
    """Raised when a requested adapter is not found."""

    pass


class AdapterGenerationError(AdapterError):
    """Raised when adapter generation fails."""

    pass


class ConfigurationError(PrompTrekError):
    """Raised when configuration is invalid or missing."""

    pass


class CLIError(PrompTrekError):
    """Raised for CLI-specific errors."""

    pass
