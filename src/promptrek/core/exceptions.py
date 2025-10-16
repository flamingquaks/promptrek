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


class DeprecationWarnings:
    """Centralized deprecation warning messages for PrompTrek."""

    @staticmethod
    def v3_nested_plugins_warning(source: str) -> str:
        """
        Get deprecation warning for v3.0 nested plugins structure.

        Args:
            source: The source file or context where the deprecated structure was found

        Returns:
            Formatted deprecation warning message
        """
        return (
            f"\n⚠️  DEPRECATION WARNING in {source}:\n"
            f"   Detected nested plugin structure (plugins.mcp_servers, etc.)\n"
            f"   This structure is deprecated in v3.0 and will be removed in v4.0.\n"
            f"   Please migrate to top-level fields:\n"
            f"     - Move 'plugins.mcp_servers' → 'mcp_servers' (top-level)\n"
            f"     - Move 'plugins.commands' → 'commands' (top-level)\n"
            f"     - Move 'plugins.agents' → 'agents' (top-level)\n"
            f"     - Move 'plugins.hooks' → 'hooks' (top-level)\n"
            f"   Run: promptrek migrate {source} to auto-migrate\n"
        )

    @staticmethod
    def v3_nested_plugin_field_warning(field_name: str) -> str:
        """
        Get short deprecation warning for a specific nested plugin field.

        Args:
            field_name: The plugin field name (e.g., 'mcp_servers', 'commands')

        Returns:
            Formatted short deprecation warning
        """
        return f"⚠️  Using deprecated plugins.{field_name} structure (use top-level {field_name} in v3.0)"
