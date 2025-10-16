"""
UPF validation module.

Provides comprehensive validation for Universal Prompt Format files
beyond basic schema validation.
"""

from typing import Any, Dict, List, Union, cast

from .models import UniversalPrompt, UniversalPromptV2, UniversalPromptV3


class ValidationResult:
    """Result of UPF validation."""

    def __init__(self) -> None:
        self.errors: List[str] = []
        self.warnings: List[str] = []

    def add_error(self, message: str) -> None:
        """Add a validation error."""
        self.errors.append(message)

    def add_warning(self, message: str) -> None:
        """Add a validation warning."""
        self.warnings.append(message)

    @property
    def is_valid(self) -> bool:
        """Check if validation passed (no errors)."""
        return len(self.errors) == 0

    @property
    def has_warnings(self) -> bool:
        """Check if there are any warnings."""
        return len(self.warnings) > 0


class UPFValidator:
    """Validator for Universal Prompt Format files."""

    # Supported editors
    KNOWN_EDITORS = {
        "copilot",
        "cursor",
        "continue",
        "claude",
        "kiro",
        "cline",
        "windsurf",
        "tabnine",
        "amazon-q",
        "jetbrains",
    }

    # Common project types
    KNOWN_PROJECT_TYPES = {
        "web_application",
        "api",
        "api_service",
        "library",
        "mobile_app",
        "desktop_app",
        "cli_tool",
        "data_science",
        "machine_learning",
    }

    def __init__(self) -> None:
        """Initialize the UPF validator."""
        pass

    def validate(
        self, prompt: Union[UniversalPrompt, UniversalPromptV2, UniversalPromptV3]
    ) -> ValidationResult:
        """
        Perform comprehensive validation of a UPF object.

        Args:
            prompt: The UniversalPrompt (v1), UniversalPromptV2, or UniversalPromptV3 to validate

        Returns:
            ValidationResult with errors and warnings
        """
        result = ValidationResult()

        # V2/V3 has simpler validation
        if isinstance(prompt, (UniversalPromptV2, UniversalPromptV3)):
            self._validate_metadata(prompt, result)

            # V2/V3 specific: check content exists
            if not prompt.content or not prompt.content.strip():
                result.add_error("Content cannot be empty")

            # Validate variables if present
            if prompt.variables:
                self._validate_variables(prompt, result)

            # Validate documents if present
            if prompt.documents:
                for i, doc in enumerate(prompt.documents):
                    if not doc.name.strip():
                        result.add_error(f"Document {i+1} has empty name")
                    if not doc.content.strip():
                        result.add_error(f"Document {i+1} has empty content")

            # V3 specific: validate plugin fields
            if isinstance(prompt, UniversalPromptV3):
                if prompt.mcp_servers:
                    for i, server in enumerate(prompt.mcp_servers):
                        # Access fields directly (TypedDict at type level, but could be dict or object at runtime)
                        server_name = server["name"] if isinstance(server, dict) else server.name  # type: ignore
                        server_command = server["command"] if isinstance(server, dict) else server.command  # type: ignore

                        if not server_name:
                            result.add_error(f"MCP server {i+1} has no name")
                        if not server_command:
                            result.add_error(f"MCP server {i+1} has no command")

            return result

        # V1 full validation
        self._validate_schema_version(prompt, result)
        self._validate_targets(prompt, result)
        self._validate_metadata(prompt, result)
        self._validate_context(prompt, result)
        self._validate_instructions(prompt, result)
        self._validate_examples(prompt, result)
        self._validate_variables(prompt, result)
        self._validate_editor_specific(prompt, result)
        self._validate_conditions(prompt, result)
        self._validate_imports(prompt, result)

        return result

    def _validate_schema_version(
        self, prompt: UniversalPrompt, result: ValidationResult
    ) -> None:
        """Validate schema version."""
        version = prompt.schema_version

        # Check if it's a supported version
        if version != "1.0.0":
            result.add_warning(
                f"Schema version '{version}' may not be fully supported. "
                f"Current supported version: 1.0.0"
            )

    def _validate_targets(
        self, prompt: UniversalPrompt, result: ValidationResult
    ) -> None:
        """Validate target editors."""
        targets = prompt.targets

        # Skip validation if targets is None (optional)
        if targets is None:
            return

        if not targets:
            result.add_error("At least one target editor must be specified")
            return
        # Check for unknown editors
        unknown_editors = set(targets) - self.KNOWN_EDITORS
        if unknown_editors:
            result.add_warning(
                f"Unknown target editors: {', '.join(sorted(unknown_editors))}"
            )

        # Check for duplicates
        if len(targets) != len(set(targets)):
            result.add_warning("Duplicate target editors found")

    def _validate_metadata(
        self,
        prompt: Union[UniversalPrompt, UniversalPromptV2, UniversalPromptV3],
        result: ValidationResult,
    ) -> None:
        """Validate metadata section."""
        metadata = prompt.metadata

        # Check for empty fields
        if not metadata.title.strip():
            result.add_error("Metadata title cannot be empty")

        if not metadata.description.strip():
            result.add_error("Metadata description cannot be empty")

        if metadata.author is not None and not metadata.author.strip():
            result.add_error("Metadata author cannot be empty")

        # Check version format
        version = metadata.version
        if version is not None and (not version or not self._is_valid_semver(version)):
            result.add_warning(
                f"Metadata version '{version}' is not a valid semantic " f"version"
            )

    def _validate_context(
        self, prompt: UniversalPrompt, result: ValidationResult
    ) -> None:
        """Validate context section."""
        if not prompt.context:
            return

        context = prompt.context

        # Check project type
        if (
            context.project_type
            and context.project_type not in self.KNOWN_PROJECT_TYPES
        ):
            result.add_warning(f"Unknown project type: {context.project_type}")

        # Check technologies list
        if context.technologies:
            if len(context.technologies) == 0:
                result.add_warning("Context technologies list is empty")

    def _validate_instructions(
        self, prompt: UniversalPrompt, result: ValidationResult
    ) -> None:
        """Validate instructions section."""
        if not prompt.instructions:
            result.add_warning("No instructions provided")
            return

        instructions = prompt.instructions

        # Check if any instruction categories are provided
        has_content = any(
            [
                instructions.general,
                instructions.code_style,
                instructions.architecture,
                instructions.testing,
                instructions.security,
                instructions.performance,
            ]
        )

        if not has_content:
            result.add_warning("Instructions section contains no content")

        # Check for empty lists
        for field_name in [
            "general",
            "code_style",
            "architecture",
            "testing",
            "security",
            "performance",
        ]:
            field_value = getattr(instructions, field_name, None)
            if field_value is not None and len(field_value) == 0:
                result.add_warning(f"Instructions.{field_name} is an empty list")

    def _validate_examples(
        self, prompt: UniversalPrompt, result: ValidationResult
    ) -> None:
        """Validate examples section."""
        if not prompt.examples:
            return

        examples = prompt.examples

        # Check for empty examples
        empty_examples = [key for key, value in examples.items() if not value.strip()]
        if empty_examples:
            result.add_warning(f"Empty examples found: {', '.join(empty_examples)}")

    def _validate_variables(
        self,
        prompt: Union[UniversalPrompt, UniversalPromptV2, UniversalPromptV3],
        result: ValidationResult,
    ) -> None:
        """Validate variables section."""
        if not prompt.variables:
            return

        variables = prompt.variables

        # Check for empty variable values
        empty_vars = [key for key, value in variables.items() if not value.strip()]
        if empty_vars:
            result.add_warning(f"Empty variable values: {', '.join(empty_vars)}")

        # Check for variable naming conventions
        invalid_names = [
            key for key in variables.keys() if not self._is_valid_variable_name(key)
        ]
        if invalid_names:
            result.add_warning(
                f"Invalid variable names (should be UPPER_SNAKE_CASE): {', '.join(invalid_names)}"
            )

    def _validate_editor_specific(
        self, prompt: UniversalPrompt, result: ValidationResult
    ) -> None:
        """Validate editor-specific configurations."""
        if not prompt.editor_specific:
            return

        editor_configs = prompt.editor_specific

        # Check if editor-specific configs match target editors
        target_set = set(prompt.targets) if prompt.targets else set()
        config_set = set(editor_configs.keys())

        unknown_configs = config_set - target_set
        if unknown_configs:
            result.add_warning(
                f"Editor-specific configs for non-target editors: {', '.join(unknown_configs)}"
            )

    def _validate_conditions(
        self, prompt: UniversalPrompt, result: ValidationResult
    ) -> None:
        """Validate conditional instructions."""
        if not prompt.conditions:
            return

        # For now, just check basic structure
        for i, condition in enumerate(prompt.conditions):
            if not condition.if_condition.strip():
                result.add_error(f"Condition {i+1} has empty 'if' clause")

    def _validate_imports(
        self, prompt: UniversalPrompt, result: ValidationResult
    ) -> None:
        """Validate import configurations."""
        if not prompt.imports:
            return

        for i, import_config in enumerate(prompt.imports):
            path = import_config.path

            if not path.strip():
                result.add_error(f"Import {i+1} has empty path")
                continue

            # Check if path looks like a valid file path
            if not path.endswith((".promptrek.yaml", ".promptrek.yml")):
                result.add_warning(
                    f"Import {i+1} path should end with .promptrek.yaml or .promptrek.yml: {path}"
                )

    def _is_valid_semver(self, version: str) -> bool:
        """Check if string is a valid semantic version."""
        try:
            parts = version.split(".")
            if len(parts) != 3:
                return False

            for part in parts:
                int(part)  # Will raise ValueError if not numeric

            return True
        except (ValueError, AttributeError):
            return False

    def _is_valid_variable_name(self, name: str) -> bool:
        """Check if variable name follows UPPER_SNAKE_CASE convention."""
        if not name:
            return False

        # Should contain only uppercase letters, numbers, and underscores
        # Should start with a letter
        return (
            name.isupper()
            and name.replace("_", "")
            .replace("0", "")
            .replace("1", "")
            .replace("2", "")
            .replace("3", "")
            .replace("4", "")
            .replace("5", "")
            .replace("6", "")
            .replace("7", "")
            .replace("8", "")
            .replace("9", "")
            .isalpha()
            and name[0].isalpha()
        )
