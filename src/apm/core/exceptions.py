"""
Custom exceptions for Agent Prompt Mapper.

Defines specific exception types for different error conditions
to provide better error handling and user feedback.
"""


class APMError(Exception):
    """Base exception for all APM errors."""
    pass


class UPFError(APMError):
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


class TemplateError(APMError):
    """Base exception for template-related errors."""
    pass


class TemplateNotFoundError(TemplateError):
    """Raised when a template file is not found."""
    pass


class TemplateRenderingError(TemplateError):
    """Raised when template rendering fails."""
    pass


class AdapterError(APMError):
    """Base exception for adapter-related errors."""
    pass


class AdapterNotFoundError(AdapterError):
    """Raised when a requested adapter is not found."""
    pass


class AdapterGenerationError(AdapterError):
    """Raised when adapter generation fails."""
    pass


class ConfigurationError(APMError):
    """Raised when configuration is invalid or missing."""
    pass


class CLIError(APMError):
    """Raised for CLI-specific errors."""
    pass