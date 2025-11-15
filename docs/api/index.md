# API Reference

Welcome to the PrompTrek API reference documentation. This section provides detailed documentation for all modules, classes, and functions in the PrompTrek codebase.

## Overview

PrompTrek's API is organized into several main modules:

- **[Core](core/parser.md)** - Core parsing, validation, and data models
- **[Adapters](adapters/base.md)** - Editor-specific adapters and registry
- **[Utils](utils/variables.md)** - Utility functions for variables, conditionals, and gitignore

## Core Modules

### Parser

The parser module handles reading and parsing `.promptrek.yaml` files.

::: promptrek.core.parser
    options:
      show_root_heading: true
      show_source: true

See [Parser Documentation](core/parser.md) for details.

### Validator

The validator ensures configurations meet schema requirements.

::: promptrek.core.validator
    options:
      show_root_heading: true
      show_source: true

See [Validator Documentation](core/validator.md) for details.

### Models

Pydantic models for configuration data structures.

::: promptrek.core.models
    options:
      show_root_heading: true
      show_source: true

See [Models Documentation](core/models.md) for details.

## Adapters

### Base Adapter

All editor adapters inherit from the base adapter class.

::: promptrek.adapters.base
    options:
      show_root_heading: true
      show_source: true

See [Base Adapter Documentation](adapters/base.md) for details.

### Adapter Registry

The registry manages all available editor adapters.

::: promptrek.adapters.registry
    options:
      show_root_heading: true
      show_source: true

See [Registry Documentation](adapters/registry.md) for details.

## Utilities

### Variables

Variable substitution and management.

::: promptrek.utils.variables
    options:
      show_root_heading: true
      show_source: true

See [Variables Documentation](utils/variables.md) for details.

### Conditionals

Conditional instruction processing.

::: promptrek.utils.conditionals
    options:
      show_root_heading: true
      show_source: true

See [Conditionals Documentation](utils/conditionals.md) for details.

## Usage Examples

### Parsing a Configuration

```python
from promptrek.core.parser import Parser

# Parse a PrompTrek configuration
parser = Parser()
config = parser.parse_file(".promptrek.yaml")

print(f"Title: {config.metadata.title}")
print(f"Schema: {config.schema_version}")
```

### Validating a Configuration

```python
from promptrek.core.validator import Validator

# Validate configuration
validator = Validator()
result = validator.validate(config)

if result.is_valid:
    print("✓ Configuration is valid")
else:
    for error in result.errors:
        print(f"✗ {error}")
```

### Using an Adapter

```python
from promptrek.adapters.registry import AdapterRegistry

# Get an adapter
registry = AdapterRegistry()
adapter = registry.get_adapter("cursor")

# Generate configuration
adapter.generate(config, output_dir=".")
```

### Variable Substitution

```python
from promptrek.utils.variables import substitute_variables

content = "Project: {{{ PROJECT_NAME }}}"
variables = {"PROJECT_NAME": "my-app"}

result = substitute_variables(content, variables)
print(result)  # "Project: my-app"
```

## Type Hints

PrompTrek uses type hints throughout the codebase. All public APIs include proper type annotations for better IDE support and type checking.

```python
from typing import Dict, List, Optional
from promptrek.core.models import PromptConfig

def process_config(
    config: PromptConfig,
    variables: Optional[Dict[str, str]] = None
) -> List[str]:
    """Process configuration with optional variables."""
    pass
```

## Next Steps

- Browse the [Core API](core/parser.md) documentation
- Learn about [Adapters](adapters/base.md)
- Explore [Utility Functions](utils/variables.md)
- Check the [Developer Guide](../developer/index.md) for contribution guidelines
