# Base Adapter

The base adapter module defines the abstract interface that all editor adapters must implement.

## Overview

The `EditorAdapter` abstract base class provides:

- **Standard interface**: All adapters implement the same methods
- **Capability declaration**: Adapters declare what features they support
- **Variable substitution**: Built-in support for template variables
- **Conditional processing**: Built-in support for conditional instructions
- **Bidirectional sync**: Optional support for parsing editor files back to UPF
- **Multi-file generation**: Optional support for generating separate files per prompt

All editor-specific adapters (Cursor, Claude, Copilot, etc.) inherit from this base class and implement the abstract methods.

## API Reference

::: promptrek.adapters.base
    options:
      show_root_heading: true
      show_source: true
      members_order: source
      docstring_style: google
      show_if_no_docstring: false

## Usage Examples

### Getting an Adapter

Access adapters through the registry:

```python
from promptrek.adapters.registry import registry

# Get a specific adapter
cursor_adapter = registry.get("cursor")
print(f"Adapter: {cursor_adapter.name}")
print(f"Description: {cursor_adapter.description}")
print(f"File patterns: {cursor_adapter.file_patterns}")
```

### Generating Files

Use an adapter to generate editor-specific files:

```python
from pathlib import Path
from promptrek.core.parser import UPFParser
from promptrek.adapters.registry import registry

# Parse UPF file
parser = UPFParser()
prompt = parser.parse_file(".promptrek.yaml")

# Get adapter and generate
adapter = registry.get("cursor")
files = adapter.generate(
    prompt=prompt,
    output_dir=Path("."),
    dry_run=False,
    verbose=True,
    variables={"ENVIRONMENT": "production"}
)

print(f"Generated {len(files)} files:")
for file in files:
    print(f"  - {file}")
```

### Dry Run Mode

Preview what would be generated without creating files:

```python
from pathlib import Path
from promptrek.adapters.registry import registry

adapter = registry.get("claude")

# Dry run - shows what would be created
files = adapter.generate(
    prompt=prompt,
    output_dir=Path("."),
    dry_run=True,  # Don't actually create files
    verbose=True
)

print("\nWould generate:")
for file in files:
    print(f"  - {file}")
```

### Checking Adapter Capabilities

Check what features an adapter supports:

```python
from promptrek.adapters.registry import registry

adapter = registry.get("cursor")

# Check capabilities
print(f"Supports variables: {adapter.supports_variables()}")
print(f"Supports conditionals: {adapter.supports_conditionals()}")
print(f"Supports hooks: {adapter.supports_hooks()}")
print(f"Supports bidirectional sync: {adapter.supports_bidirectional_sync()}")

# Example output for Cursor:
# Supports variables: True
# Supports conditionals: True
# Supports hooks: False
# Supports bidirectional sync: True
```

### Variable Substitution

Adapters can substitute variables in prompts:

```python
from promptrek.adapters.registry import registry

adapter = registry.get("copilot")

# Check if adapter supports variables
if adapter.supports_variables():
    # Substitute variables in prompt
    substituted_prompt = adapter.substitute_variables(
        prompt,
        variables={
            "API_VERSION": "v2",
            "DATABASE_NAME": "prod_db"
        }
    )

    # Generate with substituted prompt
    files = adapter.generate(substituted_prompt, output_dir=Path("."))
```

### Processing Conditionals

Adapters can process conditional instructions:

```python
from promptrek.adapters.registry import registry

adapter = registry.get("cursor")

if adapter.supports_conditionals():
    # Process conditionals with editor context
    additional_content = adapter.process_conditionals(
        prompt,
        variables={"EDITOR": "cursor", "ENVIRONMENT": "production"}
    )

    print("Additional content from conditionals:")
    print(additional_content)
```

### Validating Prompts

Adapters can validate prompts for editor-specific requirements:

```python
from promptrek.adapters.registry import registry

adapter = registry.get("claude")

# Validate prompt for this editor
validation_errors = adapter.validate(prompt)

if validation_errors:
    print(f"Validation errors for {adapter.name}:")
    for error in validation_errors:
        print(f"  - {error.field}: {error.message}")
else:
    print(f"✓ Valid for {adapter.name}")
```

### Bidirectional Sync

Some adapters support parsing editor files back to UPF:

```python
from pathlib import Path
from promptrek.adapters.registry import registry

adapter = registry.get("cursor")

if adapter.supports_bidirectional_sync():
    # Parse editor files back to UPF
    prompt = adapter.parse_files(source_dir=Path("."))

    print(f"Parsed from {adapter.name}:")
    print(f"  Title: {prompt.metadata.title}")
    print(f"  Schema: {prompt.schema_version}")

    # Save as UPF file
    import yaml
    with open(".promptrek.yaml", "w") as f:
        yaml.safe_dump(prompt.model_dump(), f)
```

### Creating a Custom Adapter

Implement a custom adapter by extending EditorAdapter:

```python
from pathlib import Path
from typing import List, Optional, Dict, Any
from promptrek.adapters.base import EditorAdapter
from promptrek.core.models import UniversalPrompt
from promptrek.core.exceptions import ValidationError

class MyCustomAdapter(EditorAdapter):
    """Custom adapter for MyEditor."""

    def __init__(self):
        super().__init__(
            name="my-editor",
            description="Adapter for MyEditor",
            file_patterns=[".myeditor/config.yaml"]
        )

    def generate(
        self,
        prompt: UniversalPrompt,
        output_dir: Path,
        dry_run: bool = False,
        verbose: bool = False,
        variables: Optional[Dict[str, Any]] = None,
        headless: bool = False,
    ) -> List[Path]:
        """Generate MyEditor configuration files."""
        generated_files = []

        # Apply variable substitution if supported
        if self.supports_variables() and variables:
            prompt = self.substitute_variables(prompt, variables)

        # Process conditionals if supported
        if self.supports_conditionals():
            additional = self.process_conditionals(prompt, variables)
            # Merge additional content...

        # Generate editor-specific files
        config_file = output_dir / ".myeditor" / "config.yaml"

        if not dry_run:
            config_file.parent.mkdir(parents=True, exist_ok=True)
            # Write configuration...
            generated_files.append(config_file)

        if verbose:
            print(f"Generated: {config_file}")

        return generated_files

    def validate(self, prompt: UniversalPrompt) -> List[ValidationError]:
        """Validate prompt for MyEditor."""
        errors = []

        # Custom validation logic
        if not prompt.instructions:
            errors.append(ValidationError(
                field="instructions",
                message="MyEditor requires instructions",
                severity="error"
            ))

        return errors

    def supports_variables(self) -> bool:
        """MyEditor supports variable substitution."""
        return True

    def supports_conditionals(self) -> bool:
        """MyEditor supports conditional instructions."""
        return True

# Register the adapter
from promptrek.adapters.registry import registry, AdapterCapability

adapter = MyCustomAdapter()
registry.register(
    adapter,
    capabilities=[
        AdapterCapability.GENERATES_PROJECT_FILES,
        AdapterCapability.SUPPORTS_VARIABLES,
        AdapterCapability.SUPPORTS_CONDITIONALS
    ]
)
```

### Multi-File Generation

Some adapters support generating separate files for each prompt:

```python
from pathlib import Path
from promptrek.adapters.registry import registry

adapter = registry.get("cursor")

# List of (prompt, source_path) tuples
prompt_files = [
    (python_prompt, Path("python.promptrek.yaml")),
    (typescript_prompt, Path("typescript.promptrek.yaml")),
    (general_prompt, Path("general.promptrek.yaml"))
]

try:
    # Generate separate files for each prompt
    files = adapter.generate_multiple(
        prompt_files,
        output_dir=Path("."),
        dry_run=False,
        verbose=True
    )

    print(f"Generated {len(files)} files")
except NotImplementedError:
    print(f"{adapter.name} doesn't support multiple file generation")
```

### Merged File Generation

Some adapters support merging multiple prompts into one configuration:

```python
from pathlib import Path
from promptrek.adapters.registry import registry

adapter = registry.get("claude")

prompt_files = [
    (base_prompt, Path("base.promptrek.yaml")),
    (project_prompt, Path("project.promptrek.yaml"))
]

try:
    # Merge prompts and generate
    files = adapter.generate_merged(
        prompt_files,
        output_dir=Path("."),
        dry_run=False,
        verbose=True
    )

    print(f"Generated merged configuration: {files}")
except NotImplementedError:
    print(f"{adapter.name} doesn't support merged file generation")
```

### Getting Required Variables

Check what variables an adapter needs:

```python
from promptrek.adapters.registry import registry

adapter = registry.get("copilot")

# Get required variables for this prompt
required = adapter.get_required_variables(prompt)

if required:
    print(f"{adapter.name} requires these variables:")
    for var in required:
        print(f"  - {var}")

    # Check if all required variables are present
    missing = [v for v in required if v not in prompt.variables]
    if missing:
        print(f"\nMissing variables: {', '.join(missing)}")
```

### Working with File Patterns

Access adapter file patterns:

```python
from promptrek.adapters.registry import registry

# Get all adapters
adapters = [registry.get(name) for name in registry.list_adapters()]

print("Adapter file patterns:")
for adapter in adapters:
    print(f"\n{adapter.name}:")
    for pattern in adapter.file_patterns:
        print(f"  - {pattern}")

# Example output:
# cursor:
#   - .cursor/rules/*.mdc
#   - AGENTS.md
#
# claude:
#   - .claude/CLAUDE.md
#   - .claude/commands/*.md
```

### Headless Mode

Some adapters support headless mode for agent-based workflows:

```python
from pathlib import Path
from promptrek.adapters.registry import registry

adapter = registry.get("cursor")

# Generate with headless mode enabled
files = adapter.generate(
    prompt=prompt,
    output_dir=Path("."),
    dry_run=False,
    verbose=True,
    headless=True  # Include headless agent instructions
)

# Headless mode might include additional agent prompts
# or modified instructions for non-interactive use
```

## Adapter Interface

### Required Methods

All adapters must implement:

- `generate()` - Generate editor-specific files
- `validate()` - Validate prompt for the editor

### Optional Methods

Adapters may implement:

- `parse_files()` - Parse editor files back to UPF (bidirectional sync)
- `generate_multiple()` - Generate separate files per prompt
- `generate_merged()` - Merge and generate multiple prompts
- `get_required_variables()` - List required variables

### Capability Methods

Adapters can override to declare capabilities:

- `supports_variables()` - Returns True if variable substitution is supported
- `supports_conditionals()` - Returns True if conditional instructions are supported
- `supports_hooks()` - Returns True if hooks system is supported
- `supports_bidirectional_sync()` - Returns True if parse_files() is implemented

## See Also

- [Adapter Registry](registry.md) - Manage and discover adapters
- [MCP Mixin](mcp_mixin.md) - MCP server configuration generation
- [Sync Mixin](sync_mixin.md) - Bidirectional sync utilities
- [Editor Guides](../../user-guide/editors/index.md) - Editor-specific documentation
