# Validator Module

The validator module provides comprehensive validation for Universal Prompt Format (UPF) files beyond basic schema validation.

## Overview

The `UPFValidator` class performs semantic validation of UPF configurations, checking for:

- **Schema compliance**: Ensures required fields are present and properly formatted
- **Data quality**: Validates semantic version formats, variable naming conventions
- **Editor compatibility**: Checks for unknown editors and mismatched configurations
- **Best practices**: Warns about empty fields, missing content, and potential issues
- **Multi-version support**: Handles validation for v1, v2, and v3 UPF schemas

The validator complements Pydantic's structural validation by checking business rules and best practices. It returns both errors (blocking issues) and warnings (suggestions for improvement).

## API Reference

::: promptrek.core.validator
    options:
      show_root_heading: true
      show_source: true
      members_order: source
      docstring_style: google
      show_if_no_docstring: false

## Usage Examples

### Basic Validation

Validate a parsed UPF object:

```python
from promptrek.core.parser import UPFParser
from promptrek.core.validator import UPFValidator

# Parse a UPF file
parser = UPFParser()
prompt = parser.parse_file(".promptrek.yaml")

# Validate it
validator = UPFValidator()
result = validator.validate(prompt)

# Check results
if result.is_valid:
    print("✓ Configuration is valid")
else:
    print("✗ Validation failed:")
    for error in result.errors:
        print(f"  - {error}")

# Check warnings
if result.has_warnings:
    print("\n⚠ Warnings:")
    for warning in result.warnings:
        print(f"  - {warning}")
```

### Validation Results

Understanding the `ValidationResult` object:

```python
from promptrek.core.validator import UPFValidator, ValidationResult

validator = UPFValidator()
result = validator.validate(prompt)

# Check validation status
print(f"Valid: {result.is_valid}")
print(f"Has warnings: {result.has_warnings}")
print(f"Error count: {len(result.errors)}")
print(f"Warning count: {len(result.warnings)}")

# Access specific issues
for error in result.errors:
    print(f"ERROR: {error}")

for warning in result.warnings:
    print(f"WARNING: {warning}")
```

### Validating V1 Prompts

V1 prompts have comprehensive structured validation:

```python
from promptrek.core.parser import UPFParser
from promptrek.core.validator import UPFValidator

parser = UPFParser()
validator = UPFValidator()

# Parse v1 prompt
prompt = parser.parse_file("v1-config.promptrek.yaml")

# Validate
result = validator.validate(prompt)

# V1 validation checks:
# - Schema version format
# - Target editors (known vs unknown)
# - Metadata completeness
# - Context information
# - Instructions structure
# - Variable naming conventions
# - Editor-specific config alignment
# - Conditional instruction syntax
# - Import paths

if not result.is_valid:
    print("Validation errors found:")
    for error in result.errors:
        print(f"  • {error}")
```

### Validating V2/V3 Prompts

V2 and V3 prompts have simplified validation focused on content and metadata:

```python
from promptrek.core.parser import UPFParser
from promptrek.core.validator import UPFValidator

parser = UPFParser()
validator = UPFValidator()

# Parse v3 prompt
prompt = parser.parse_file("v3-config.promptrek.yaml")

# Validate
result = validator.validate(prompt)

# V2/V3 validation checks:
# - Metadata (title, description, version format)
# - Content is not empty
# - Variable naming conventions
# - Document names and content (if present)
# - MCP server configurations (v3 only)

if result.has_warnings:
    print("Validation warnings:")
    for warning in result.warnings:
        print(f"  ⚠ {warning}")
```

### Editor Target Validation

The validator checks for known editors and warns about unknown ones:

```python
from promptrek.core.models import UniversalPrompt, PromptMetadata
from promptrek.core.validator import UPFValidator

# Create a prompt with various targets
prompt = UniversalPrompt(
    schema_version="1.0.0",
    metadata=PromptMetadata(
        title="Test",
        description="Testing editor validation"
    ),
    targets=["cursor", "claude", "unknown-editor", "copilot"]
)

validator = UPFValidator()
result = validator.validate(prompt)

# Known editors: copilot, cursor, continue, claude, cline,
#                windsurf, amazon-q, jetbrains, kiro
# Unknown editors will generate warnings
for warning in result.warnings:
    if "Unknown target editors" in warning:
        print(f"⚠ {warning}")
```

### Variable Naming Validation

The validator enforces UPPER_SNAKE_CASE for variable names:

```python
from promptrek.core.models import UniversalPromptV3, PromptMetadata
from promptrek.core.validator import UPFValidator

# Create prompt with various variable names
prompt = UniversalPromptV3(
    schema_version="3.0.0",
    metadata=PromptMetadata(
        title="Variable Test",
        description="Testing variable validation"
    ),
    content="# Test",
    variables={
        "PROJECT_NAME": "my-project",      # Valid
        "API_KEY": "secret",                # Valid
        "projectName": "invalid",           # Invalid (camelCase)
        "my_var": "invalid",                # Invalid (lowercase)
        "123_VAR": "invalid",               # Invalid (starts with number)
    }
)

validator = UPFValidator()
result = validator.validate(prompt)

# Check for variable naming warnings
for warning in result.warnings:
    if "Invalid variable names" in warning:
        print(f"⚠ {warning}")
```

### Metadata Validation

The validator checks metadata completeness and format:

```python
from promptrek.core.models import UniversalPromptV3, PromptMetadata
from promptrek.core.validator import UPFValidator

# Test metadata validation
prompt = UniversalPromptV3(
    schema_version="3.0.0",
    metadata=PromptMetadata(
        title="",                    # Empty title (ERROR)
        description="Test",
        version="1.2",              # Invalid semver (WARNING)
        author=""                   # Empty author (ERROR)
    ),
    content="# Test Content"
)

validator = UPFValidator()
result = validator.validate(prompt)

# Errors for empty required fields
print("Errors:")
for error in result.errors:
    print(f"  • {error}")

# Warnings for format issues
print("\nWarnings:")
for warning in result.warnings:
    print(f"  ⚠ {warning}")
```

### MCP Server Validation (V3)

V3 prompts can have MCP server configurations that are validated:

```python
from promptrek.core.models import (
    UniversalPromptV3,
    PromptMetadata,
    MCPServer
)
from promptrek.core.validator import UPFValidator

# Create v3 prompt with MCP servers
prompt = UniversalPromptV3(
    schema_version="3.0.0",
    metadata=PromptMetadata(
        title="MCP Test",
        description="Testing MCP validation"
    ),
    content="# Rules",
    mcp_servers=[
        MCPServer(name="", command="npx"),           # Empty name (ERROR)
        MCPServer(name="filesystem", command=""),    # Empty command (ERROR)
        MCPServer(name="valid", command="npx", args=["-y", "pkg"])
    ]
)

validator = UPFValidator()
result = validator.validate(prompt)

# Check MCP validation errors
for error in result.errors:
    if "MCP server" in error:
        print(f"ERROR: {error}")
```

### Custom Validation Workflow

Integrate validation into your workflow:

```python
from pathlib import Path
from promptrek.core.parser import UPFParser
from promptrek.core.validator import UPFValidator
from promptrek.core.exceptions import UPFParsingError

def validate_upf_file(file_path: Path) -> bool:
    """
    Validate a UPF file and report results.

    Returns:
        True if valid (no errors), False otherwise
    """
    parser = UPFParser()
    validator = UPFValidator()

    try:
        # Parse the file
        prompt = parser.parse_file(file_path)
        print(f"✓ Parsed {file_path}")

        # Validate
        result = validator.validate(prompt)

        # Report errors
        if not result.is_valid:
            print(f"\n✗ Validation failed for {file_path}:")
            for error in result.errors:
                print(f"  ERROR: {error}")
            return False

        # Report warnings
        if result.has_warnings:
            print(f"\n⚠ Validation warnings for {file_path}:")
            for warning in result.warnings:
                print(f"  WARNING: {warning}")

        print(f"✓ Validation passed for {file_path}")
        return True

    except UPFParsingError as e:
        print(f"✗ Parsing error: {e}")
        return False

# Use it
is_valid = validate_upf_file(Path(".promptrek.yaml"))
```

### Validation Categories

The validator checks different aspects of the UPF:

```python
# Schema Version Validation
# - Format: x.y.z (semantic versioning)
# - Warns if not 1.0.0 (v1) or 2.x.x/3.x.x (v2/v3)

# Target Validation (v1 only)
# - At least one target specified
# - Known editors vs unknown editors
# - No duplicates

# Metadata Validation
# - Title not empty
# - Description not empty
# - Author not empty (if provided)
# - Version follows semver format (if provided)

# Content Validation (v2/v3)
# - Content not empty
# - Documents have names and content

# Instructions Validation (v1)
# - At least some instruction content
# - No empty instruction lists

# Variable Validation
# - Variable names follow UPPER_SNAKE_CASE
# - No empty variable values

# Editor-Specific Validation (v1)
# - Editor configs match target editors
# - Warns about configs for non-targets

# Conditional Validation (v1)
# - if clauses not empty
# - Proper syntax

# Import Validation (v1)
# - Import paths not empty
# - Paths end with .promptrek.yaml or .yml
```

## Validation Levels

The validator returns two types of issues:

### Errors

Errors are blocking issues that indicate the configuration is invalid:

- Empty required fields (title, description, content)
- Invalid schema version format
- Empty conditional clauses
- Empty import paths
- Missing MCP server names or commands

### Warnings

Warnings are suggestions for improvement:

- Unknown editor targets
- Non-standard schema versions
- Invalid semantic version format
- Empty optional fields
- Variable naming conventions
- Editor config mismatches

## See Also

- [Parser Module](parser.md) - Parse UPF files before validation
- [Models Module](models.md) - Data model definitions
- [UPF Schema Reference](../../schema/index.md) - Schema documentation
- [CLI Validation](../../cli/validate.md) - Using the validation CLI command
