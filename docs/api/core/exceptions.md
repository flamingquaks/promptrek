# Exceptions Module

The exceptions module defines custom exception types for PrompTrek, providing clear error handling and user feedback.

## Overview

PrompTrek uses a hierarchical exception system to categorize different types of errors:

- **PrompTrekError**: Base exception for all PrompTrek errors
- **UPFError**: Base for UPF-related errors (parsing, validation)
- **TemplateError**: Template rendering and variable substitution errors
- **AdapterError**: Editor adapter-related errors
- **ConfigurationError**: Configuration file errors
- **CLIError**: Command-line interface errors

This structured approach allows for precise error handling and helpful error messages.

## API Reference

::: promptrek.core.exceptions
    options:
      show_root_heading: true
      show_source: true
      members_order: source
      docstring_style: google
      show_if_no_docstring: false

## Usage Examples

### Basic Exception Handling

Handle different exception types:

```python
from promptrek.core.parser import UPFParser
from promptrek.core.exceptions import (
    UPFFileNotFoundError,
    UPFParsingError,
    UPFError,
    PrompTrekError
)

parser = UPFParser()

try:
    prompt = parser.parse_file("config.promptrek.yaml")
except UPFFileNotFoundError as e:
    # Specific handler for missing files
    print(f"File not found: {e}")
    print("Please create a .promptrek.yaml file")
except UPFParsingError as e:
    # Specific handler for parsing errors
    print(f"Invalid UPF format: {e}")
    print("Check your YAML syntax")
except UPFError as e:
    # Generic UPF error handler
    print(f"UPF error: {e}")
except PrompTrekError as e:
    # Catch-all for any PrompTrek error
    print(f"PrompTrek error: {e}")
```

### File Not Found Errors

Handle missing configuration files:

```python
from pathlib import Path
from promptrek.core.parser import UPFParser
from promptrek.core.exceptions import UPFFileNotFoundError

def load_config(config_path: Path):
    """Load configuration with proper error handling."""
    parser = UPFParser()

    try:
        return parser.parse_file(config_path)
    except UPFFileNotFoundError:
        # Try default locations
        default_paths = [
            Path(".promptrek.yaml"),
            Path(".promptrek/config.promptrek.yaml"),
            Path("project.promptrek.yaml")
        ]

        for path in default_paths:
            try:
                return parser.parse_file(path)
            except UPFFileNotFoundError:
                continue

        # No config found
        raise UPFFileNotFoundError(
            f"No configuration file found. Tried: {config_path}, "
            f"{', '.join(str(p) for p in default_paths)}"
        )

# Use it
try:
    config = load_config(Path("custom.promptrek.yaml"))
except UPFFileNotFoundError as e:
    print(f"Error: {e}")
```

### Parsing Errors

Handle YAML and validation errors:

```python
from promptrek.core.parser import UPFParser
from promptrek.core.exceptions import UPFParsingError

parser = UPFParser()

try:
    prompt = parser.parse_file(".promptrek.yaml")
except UPFParsingError as e:
    # Parsing errors include helpful context
    print(f"Failed to parse configuration:")
    print(str(e))

    # Example error messages:
    # - "YAML parsing error in .promptrek.yaml: ..."
    # - "Validation errors in .promptrek.yaml:\n  metadata -> title: field required"
    # - "File must have .yaml or .yml extension: config.txt"

    # Suggest fixes
    print("\nCommon issues:")
    print("  - Check YAML syntax (indentation, colons)")
    print("  - Ensure required fields are present")
    print("  - Verify schema_version format (x.y.z)")
```

### Validation Errors

Work with the ValidationError exception:

```python
from promptrek.core.exceptions import ValidationError

# ValidationError is different from Pydantic's ValidationError
# It represents a single validation issue with field and message

try:
    # Some validation logic
    error = ValidationError(
        field="metadata.title",
        message="Title cannot be empty",
        severity="error"
    )
    raise error
except ValidationError as e:
    print(f"Field: {e.field}")
    print(f"Message: {e.message}")
    print(f"Severity: {e.severity}")
```

### Template Errors

Handle variable substitution errors:

```python
from promptrek.utils.variables import VariableSubstitution
from promptrek.core.exceptions import TemplateError

substitution = VariableSubstitution()
content = "Project: {{{ PROJECT_NAME }}}\nEnv: {{{ ENVIRONMENT }}}"
variables = {"PROJECT_NAME": "my-app"}  # ENVIRONMENT missing

try:
    # Strict mode raises error for undefined variables
    result = substitution.substitute(
        content,
        variables,
        strict=True
    )
except TemplateError as e:
    print(f"Template error: {e}")
    # Output: "Template error: Undefined variable: ENVIRONMENT"

    # Non-strict mode leaves variables unchanged
    result = substitution.substitute(
        content,
        variables,
        strict=False
    )
    print(result)
    # Output: "Project: my-app\nEnv: {{{ ENVIRONMENT }}}"
```

### Command Execution Errors

Handle dynamic variable command failures:

```python
from promptrek.utils.variables import CommandExecutor, DynamicVariable
from promptrek.core.exceptions import TemplateError

executor = CommandExecutor(allow_commands=True, timeout=5)
var = DynamicVariable(
    name="COMMIT_HASH",
    command="git rev-parse --short HEAD"
)

try:
    value = var.evaluate(executor)
    print(f"Commit: {value}")
except TemplateError as e:
    # Possible errors:
    # - Command not found
    # - Command timed out
    # - Command failed (non-zero exit)
    # - Command execution disabled
    print(f"Command failed: {e}")
```

### Adapter Errors

Handle adapter-related errors:

```python
from promptrek.adapters.registry import registry
from promptrek.core.exceptions import (
    AdapterNotFoundError,
    AdapterGenerationError
)

try:
    # Get unknown adapter
    adapter = registry.get("unknown-editor")
except AdapterNotFoundError as e:
    print(f"Adapter error: {e}")
    # Output: "No adapter found for 'unknown-editor'"

    # Show available adapters
    available = registry.list_adapters()
    print(f"Available adapters: {', '.join(available)}")

try:
    # Generation might fail
    adapter = registry.get("cursor")
    files = adapter.generate(prompt, output_dir, dry_run=False)
except AdapterGenerationError as e:
    print(f"Generation failed: {e}")
```

### Configuration Errors

Handle configuration file errors:

```python
from promptrek.core.exceptions import ConfigurationError

def load_user_config(config_path):
    """Load user configuration with validation."""
    if not config_path.exists():
        raise ConfigurationError(
            f"User configuration not found: {config_path}\n"
            f"Run 'promptrek init' to create it"
        )

    # Additional validation
    import yaml
    with open(config_path) as f:
        data = yaml.safe_load(f)

    if not isinstance(data, dict):
        raise ConfigurationError(
            f"Invalid configuration format in {config_path}\n"
            f"Expected a YAML dictionary"
        )

    required_fields = ["schema_version"]
    missing = [f for f in required_fields if f not in data]
    if missing:
        raise ConfigurationError(
            f"Missing required fields in {config_path}: "
            f"{', '.join(missing)}"
        )

    return data

try:
    config = load_user_config(Path("user-config.yaml"))
except ConfigurationError as e:
    print(f"Configuration error: {e}")
```

### CLI Errors

Handle command-line interface errors:

```python
from promptrek.core.exceptions import CLIError
import sys

def run_command(args):
    """Run CLI command with error handling."""
    try:
        # Validate arguments
        if not args.file:
            raise CLIError(
                "Missing required argument: --file\n"
                "Usage: promptrek generate --file config.yaml"
            )

        if not Path(args.file).exists():
            raise CLIError(
                f"File not found: {args.file}\n"
                f"Please check the file path"
            )

        # Run command
        # ... command logic ...

    except CLIError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
```

### Exception Hierarchy

Catch exceptions at different levels:

```python
from promptrek.core.exceptions import (
    PrompTrekError,
    UPFError,
    TemplateError,
    AdapterError
)

try:
    # Some PrompTrek operation
    pass
except UPFError as e:
    # Handle all UPF-related errors
    print(f"UPF Error: {e}")
except TemplateError as e:
    # Handle template errors
    print(f"Template Error: {e}")
except AdapterError as e:
    # Handle adapter errors
    print(f"Adapter Error: {e}")
except PrompTrekError as e:
    # Catch any other PrompTrek error
    print(f"PrompTrek Error: {e}")
except Exception as e:
    # Catch non-PrompTrek errors
    print(f"Unexpected error: {e}")
```

### Custom Error Messages

Create informative error messages:

```python
from promptrek.core.exceptions import UPFParsingError, ConfigurationError

# Good error message - specific and actionable
raise UPFParsingError(
    f"Invalid schema version '2.0' in {file_path}.\n"
    f"Expected format: 'x.y.z' (e.g., '3.0.0')\n"
    f"See: https://docs.promptrek.dev/schema/"
)

# Good configuration error with context
raise ConfigurationError(
    f"Invalid MCP server configuration at index {idx}:\n"
    f"  Server name: {server.get('name', '<missing>')}\n"
    f"  Issue: Missing 'command' field\n"
    f"  Required fields: name, command"
)
```

### Deprecation Warnings

Use the centralized deprecation warning system:

```python
from promptrek.core.exceptions import DeprecationWarnings
import sys

# V3 nested plugins deprecation warning
source_file = ".promptrek.yaml"
warning = DeprecationWarnings.v3_nested_plugins_warning(source_file)
print(warning, file=sys.stderr)

# Specific field warning
field_name = "mcp_servers"
warning = DeprecationWarnings.v3_nested_plugin_field_warning(field_name)
print(warning, file=sys.stderr)
```

### Error Recovery

Implement graceful error recovery:

```python
from pathlib import Path
from promptrek.core.parser import UPFParser
from promptrek.core.exceptions import (
    UPFFileNotFoundError,
    UPFParsingError
)

def safe_parse(file_path: Path, fallback_content: str = None):
    """
    Parse UPF file with fallback on error.

    Returns:
        Tuple of (prompt, error_message)
    """
    parser = UPFParser()

    try:
        prompt = parser.parse_file(file_path)
        return prompt, None

    except UPFFileNotFoundError as e:
        error_msg = f"File not found: {e}"

        # Try fallback
        if fallback_content:
            try:
                prompt = parser.parse_string(fallback_content)
                return prompt, f"{error_msg} (using fallback)"
            except UPFParsingError:
                pass

        return None, error_msg

    except UPFParsingError as e:
        return None, f"Parsing error: {e}"

# Use it
prompt, error = safe_parse(Path(".promptrek.yaml"))
if error:
    print(f"Warning: {error}")
if prompt:
    print(f"Loaded: {prompt.metadata.title}")
```

## Exception Reference

### PrompTrek Exception Hierarchy

```
Exception (built-in)
└── PrompTrekError
    ├── UPFError
    │   ├── UPFParsingError
    │   ├── UPFFileNotFoundError
    │   └── UPFValidationError
    ├── ValidationError
    ├── TemplateError
    │   ├── TemplateNotFoundError
    │   └── TemplateRenderingError
    ├── AdapterError
    │   ├── AdapterNotFoundError
    │   └── AdapterGenerationError
    ├── ConfigurationError
    └── CLIError
```

### When to Use Each Exception

- **PrompTrekError**: Catch-all for any PrompTrek error
- **UPFError**: Any UPF file-related error
- **UPFFileNotFoundError**: Missing UPF file
- **UPFParsingError**: Invalid YAML syntax or schema validation failure
- **UPFValidationError**: Semantic validation failure
- **ValidationError**: Single validation issue with field context
- **TemplateError**: Variable substitution or template rendering error
- **TemplateNotFoundError**: Missing template file
- **TemplateRenderingError**: Template rendering failure
- **AdapterError**: Adapter-related error
- **AdapterNotFoundError**: Unknown adapter requested
- **AdapterGenerationError**: File generation failure
- **ConfigurationError**: Invalid configuration file
- **CLIError**: Command-line interface error

## See Also

- [Parser Module](parser.md) - Raises UPF exceptions
- [Validator Module](validator.md) - Validation error handling
- [Variables Module](../utils/variables.md) - Template error handling
- [Error Handling Guide](../../user-guide/error-handling.md) - Error handling patterns
