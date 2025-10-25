# Universal Prompt Format (UPF) JSON Schemas

This directory contains JSON Schema files for the Universal Prompt Format (UPF) used by PrompTrek.

## Available Schemas

### v3.1 (Current Stable)
- **File**: [`v3.1.0.json`](v3.1.0.json)
- **Schema Version**: 3.1.x
- **Description**: Latest stable schema with refined agent model (`prompt` field), workflow support, and top-level plugin fields
- **Recommended**: Use this for all new projects

### v3.0 (Stable)
- **File**: [`v3.0.0.json`](v3.0.0.json)
- **Schema Version**: 3.0.x
- **Description**: Stable schema with top-level plugin fields (`mcp_servers`, `commands`, `agents`, `hooks`)
- **Note**: Consider migrating to v3.1 for refined agent model and workflows

### v2.1 (Legacy)
- **File**: [`v2.1.json`](v2.1.json)
- **Schema Version**: 2.1.x
- **Description**: Legacy schema with nested plugin structure (`plugins.mcp_servers`, etc.)
- **Note**: Consider migrating to v3.1

### v2.0 (Legacy)
- **File**: [`v2.0.json`](v2.0.json)
- **Schema Version**: 2.0.x
- **Description**: Simplified markdown-first schema without plugin support
- **Note**: Consider migrating to v3.1

## Using the Schemas

### In Your Editor

Many editors support JSON Schema for YAML files. You can reference these schemas to get autocompletion and validation.

#### VS Code

Add this to your `project.promptrek.yaml` file at the top:

```yaml
# yaml-language-server: $schema=https://promptrek.ai/schema/v3.1.0.json
schema_version: 3.1.0
metadata:
  title: My Project
  description: Project description
content: |
  # Your markdown content here
```

#### YAML Linters

Configure your YAML linter (e.g., `yamllint`, `yaml-language-server`) to use these schemas for validation.

### Programmatic Usage

You can use these schemas programmatically for validation:

```python
import json
import yaml
from jsonschema import validate

# Load the schema
with open('v3.1.0.json') as f:
    schema = json.load(f)

# Load your YAML file
with open('project.promptrek.yaml') as f:
    data = yaml.safe_load(f)

# Validate
validate(instance=data, schema=schema)
```

### Schema URLs

The schemas are accessible at:

- v3.1: `https://promptrek.ai/schema/v3.1.0.json`
- v3.0: `https://promptrek.ai/schema/v3.0.0.json`
- v2.1: `https://promptrek.ai/schema/v2.1.json`
- v2.0: `https://promptrek.ai/schema/v2.0.json`

## Migration

To migrate between schema versions, use the PrompTrek CLI:

```bash
# Migrate from v2.x/v3.0 to v3.1
promptrek migrate project.promptrek.yaml -o project.v3.1.promptrek.yaml

# Or migrate in-place
promptrek migrate project.promptrek.yaml --in-place
```

## Schema Generation

These schemas are automatically generated from the Pydantic models in the PrompTrek codebase using the `scripts/generate_schemas.py` script.

To regenerate schemas:

```bash
cd /path/to/promptrek
python scripts/generate_schemas.py
```

## Documentation

For more information about the Universal Prompt Format and PrompTrek:

- [PrompTrek Documentation](https://flamingquaks.github.io/promptrek/)
- [GitHub Repository](https://github.com/flamingquaks/promptrek)
- [Quick Start Guide](https://flamingquaks.github.io/promptrek/quick-start.html)

## License

These schemas are part of the PrompTrek project and are available under the same license.
