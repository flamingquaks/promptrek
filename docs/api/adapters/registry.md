# Adapter Registry

The adapter registry manages all available editor adapters and provides discovery and capability-based lookup.

## Overview

The `AdapterRegistry` class provides:

- **Centralized adapter management**: Single registry for all adapters
- **Lazy initialization**: Adapters are instantiated only when needed
- **Capability-based queries**: Find adapters by capabilities
- **Adapter information**: Get metadata without instantiating
- **Type safety**: Properly typed adapter instances

The registry is the primary way to access adapters in PrompTrek. A global `registry` instance is available for immediate use.

## API Reference

::: promptrek.adapters.registry
    options:
      show_root_heading: true
      show_source: true
      members_order: source
      docstring_style: google
      show_if_no_docstring: false

## Usage Examples

### Getting Adapters

Access adapters through the global registry:

```python
from promptrek.adapters.registry import registry

# Get a specific adapter by name
cursor_adapter = registry.get("cursor")
print(f"Got: {cursor_adapter.name}")

# Get multiple adapters
adapters = [registry.get(name) for name in ["cursor", "claude", "copilot"]]

# List all available adapters
all_adapters = registry.list_adapters()
print(f"Available: {', '.join(all_adapters)}")
```

### Handling Unknown Adapters

Handle cases where an adapter doesn't exist:

```python
from promptrek.adapters.registry import registry
from promptrek.core.exceptions import AdapterNotFoundError

try:
    adapter = registry.get("unknown-editor")
except AdapterNotFoundError as e:
    print(f"Error: {e}")

    # Show available alternatives
    available = registry.list_adapters()
    print(f"Available adapters: {', '.join(available)}")
    print("\nDid you mean one of these?")
    for name in available:
        if "unknown" in name or name.startswith("u"):
            print(f"  - {name}")
```

### Getting Adapter Information

Get adapter metadata without instantiating:

```python
from promptrek.adapters.registry import registry

# Get info without creating the adapter instance
adapter_names = registry.list_adapters()

for name in adapter_names:
    info = registry.get_adapter_info(name)

    print(f"\n{info['name']}:")
    print(f"  Description: {info['description']}")
    print(f"  File patterns: {', '.join(info['file_patterns'])}")
    print(f"  Capabilities: {', '.join(info['capabilities'])}")
    print(f"  Status: {info['status']}")
```

### Querying by Capability

Find adapters that support specific features:

```python
from promptrek.adapters.registry import registry, AdapterCapability

# Get adapters that generate project files
project_adapters = registry.get_adapters_by_capability(
    AdapterCapability.GENERATES_PROJECT_FILES
)
print(f"Project file adapters: {', '.join(project_adapters)}")

# Get adapters that support variables
variable_adapters = registry.get_adapters_by_capability(
    AdapterCapability.SUPPORTS_VARIABLES
)
print(f"Variable support: {', '.join(variable_adapters)}")

# Get global config only adapters
global_adapters = registry.get_adapters_by_capability(
    AdapterCapability.GLOBAL_CONFIG_ONLY
)
print(f"Global config only: {', '.join(global_adapters)}")
```

### Checking Capabilities

Check if a specific adapter has a capability:

```python
from promptrek.adapters.registry import registry, AdapterCapability

# Check if cursor supports variables
has_variables = registry.has_capability(
    "cursor",
    AdapterCapability.SUPPORTS_VARIABLES
)
print(f"Cursor supports variables: {has_variables}")

# Check multiple capabilities
adapter_name = "claude"
capabilities_to_check = [
    AdapterCapability.GENERATES_PROJECT_FILES,
    AdapterCapability.SUPPORTS_VARIABLES,
    AdapterCapability.SUPPORTS_CONDITIONALS,
]

print(f"\n{adapter_name} capabilities:")
for cap in capabilities_to_check:
    has_cap = registry.has_capability(adapter_name, cap)
    status = "✓" if has_cap else "✗"
    print(f"  {status} {cap.value}")
```

### Adapter Capabilities

Available capability types:

```python
from promptrek.adapters.registry import AdapterCapability

# Capability enumeration
capabilities = [
    AdapterCapability.GENERATES_PROJECT_FILES,
    AdapterCapability.GLOBAL_CONFIG_ONLY,
    AdapterCapability.IDE_PLUGIN_ONLY,
    AdapterCapability.SUPPORTS_VARIABLES,
    AdapterCapability.SUPPORTS_CONDITIONALS,
    AdapterCapability.MULTIPLE_FILE_GENERATION,
]

for cap in capabilities:
    print(f"{cap.name}: {cap.value}")

# Example output:
# GENERATES_PROJECT_FILES: generates_project_files
# GLOBAL_CONFIG_ONLY: global_config_only
# IDE_PLUGIN_ONLY: ide_plugin_only
# SUPPORTS_VARIABLES: supports_variables
# SUPPORTS_CONDITIONALS: supports_conditionals
# MULTIPLE_FILE_GENERATION: multiple_file_generation
```

### Registering Custom Adapters

Register your own adapter instances:

```python
from promptrek.adapters.registry import registry, AdapterCapability
from promptrek.adapters.base import EditorAdapter

class MyCustomAdapter(EditorAdapter):
    def __init__(self):
        super().__init__(
            name="my-editor",
            description="My custom editor adapter",
            file_patterns=[".myeditor/config.yaml"]
        )

    # Implement required methods...
    def generate(self, prompt, output_dir, **kwargs):
        pass

    def validate(self, prompt):
        return []

# Create and register
adapter = MyCustomAdapter()
registry.register(
    adapter,
    capabilities=[
        AdapterCapability.GENERATES_PROJECT_FILES,
        AdapterCapability.SUPPORTS_VARIABLES,
    ]
)

# Now it's available
my_adapter = registry.get("my-editor")
```

### Registering Adapter Classes

Register adapter classes for lazy instantiation:

```python
from promptrek.adapters.registry import registry, AdapterCapability

class LazyAdapter(EditorAdapter):
    def __init__(self):
        super().__init__(
            name="lazy-editor",
            description="Lazy-loaded adapter",
            file_patterns=[".lazy/config.yaml"]
        )

    # ... implement methods ...

# Register the class (not an instance)
registry.register_class(
    name="lazy-editor",
    adapter_class=LazyAdapter,
    capabilities=[AdapterCapability.GENERATES_PROJECT_FILES]
)

# Adapter is only instantiated when first accessed
adapter = registry.get("lazy-editor")  # Instantiated here
```

### Getting Project File Adapters

Get adapters that generate project-level files:

```python
from promptrek.adapters.registry import registry

# Get adapters that create files in the project
project_adapters = registry.get_project_file_adapters()

print("Adapters that generate project files:")
for name in project_adapters:
    adapter = registry.get(name)
    print(f"  - {name}: {', '.join(adapter.file_patterns)}")

# Example output:
#   - cursor: .cursor/rules/*.mdc, AGENTS.md
#   - claude: .claude/CLAUDE.md, .claude/commands/*.md
#   - copilot: .github/copilot-instructions.md
```

### Getting Global Config Adapters

Get adapters that only support global configuration:

```python
from promptrek.adapters.registry import registry

# Get adapters that use global/user-level config
global_adapters = registry.get_global_config_adapters()

print("Global config only adapters:")
for name in global_adapters:
    info = registry.get_adapter_info(name)
    print(f"  - {name}: {info['description']}")
```

### Listing All Adapters

List and display all registered adapters:

```python
from promptrek.adapters.registry import registry

# Get all adapter names
all_adapters = registry.list_adapters()

print(f"Total adapters: {len(all_adapters)}\n")

# Display details for each
for name in sorted(all_adapters):
    try:
        info = registry.get_adapter_info(name)
        print(f"{name}")
        print(f"  Description: {info['description']}")
        print(f"  Capabilities: {len(info['capabilities'])}")

        # Get the adapter to check additional features
        adapter = registry.get(name)
        print(f"  Variables: {'✓' if adapter.supports_variables() else '✗'}")
        print(f"  Conditionals: {'✓' if adapter.supports_conditionals() else '✗'}")
        print(f"  Sync: {'✓' if adapter.supports_bidirectional_sync() else '✗'}")
        print()
    except Exception as e:
        print(f"  Error: {e}\n")
```

### Iterating Over Adapters

Process all adapters:

```python
from promptrek.adapters.registry import registry

# Get all adapter names
adapter_names = registry.list_adapters()

# Process each adapter
for name in adapter_names:
    adapter = registry.get(name)

    # Generate files with each adapter
    try:
        files = adapter.generate(
            prompt,
            output_dir=Path("."),
            dry_run=True  # Preview mode
        )
        print(f"{name}: would generate {len(files)} files")
    except Exception as e:
        print(f"{name}: error - {e}")
```

### Registry State

The registry maintains adapter state:

```python
from promptrek.adapters.registry import registry

# Registry is a singleton - same instance everywhere
from promptrek.adapters.registry import registry as registry2
assert registry is registry2

# Registry tracks:
# - _adapters: Instantiated adapter instances
# - _adapter_classes: Registered adapter classes (not yet instantiated)
# - _capabilities: Capability mapping for each adapter

# Check what's loaded
print(f"Instantiated adapters: {len(registry._adapters)}")
print(f"Registered classes: {len(registry._adapter_classes)}")
```

### Discovering Adapters

Automatic adapter discovery (placeholder for future):

```python
from pathlib import Path
from promptrek.adapters.registry import registry

# Future feature: Auto-discover adapters in a package
# registry.discover_adapters(Path("promptrek/adapters"))

# For now, adapters are manually registered in __init__.py
```

### Practical Example: Multi-Editor Generation

Generate files for multiple editors:

```python
from pathlib import Path
from promptrek.core.parser import UPFParser
from promptrek.adapters.registry import registry

# Parse configuration
parser = UPFParser()
prompt = parser.parse_file(".promptrek.yaml")

# Define target editors
target_editors = ["cursor", "claude", "copilot"]

# Generate for each
results = {}
for editor_name in target_editors:
    try:
        adapter = registry.get(editor_name)
        files = adapter.generate(
            prompt,
            output_dir=Path("."),
            dry_run=False,
            verbose=True
        )
        results[editor_name] = {
            "success": True,
            "files": files
        }
        print(f"✓ {editor_name}: {len(files)} files")
    except Exception as e:
        results[editor_name] = {
            "success": False,
            "error": str(e)
        }
        print(f"✗ {editor_name}: {e}")

# Summary
successful = [e for e, r in results.items() if r["success"]]
print(f"\nGenerated for {len(successful)}/{len(target_editors)} editors")
```

### Error Handling

Handle registry errors gracefully:

```python
from promptrek.adapters.registry import registry
from promptrek.core.exceptions import AdapterNotFoundError

def get_adapter_safe(name: str):
    """Get adapter with fallback."""
    try:
        return registry.get(name)
    except AdapterNotFoundError:
        # Try common alternatives
        alternatives = {
            "vscode": "copilot",
            "anthropic": "claude",
            "github-copilot": "copilot",
        }

        if name in alternatives:
            alt_name = alternatives[name]
            print(f"Note: Using '{alt_name}' for '{name}'")
            return registry.get(alt_name)

        raise

# Use it
adapter = get_adapter_safe("vscode")  # Returns copilot adapter
```

## Global Registry Instance

PrompTrek provides a pre-configured global registry:

```python
from promptrek.adapters.registry import registry

# This is a global singleton instance with all built-in adapters registered
# You can use it directly without creating your own registry
```

All built-in adapters are automatically registered at import time.

## See Also

- [Base Adapter](base.md) - Adapter interface and base class
- [MCP Mixin](mcp_mixin.md) - MCP configuration generation
- [Sync Mixin](sync_mixin.md) - Bidirectional sync utilities
- [CLI Generate Command](../../cli/generate.md) - Using adapters from CLI
