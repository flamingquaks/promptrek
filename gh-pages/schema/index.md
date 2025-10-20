---
layout: default
title: UPF JSON Schemas
---

# Universal Prompt Format (UPF) JSON Schemas

This page provides JSON Schema files for the Universal Prompt Format (UPF) used by PrompTrek.

## Available Schemas

<div class="schema-list">

### v3.0 (Current Stable) ✨

**Schema Version**: 3.0.x

Latest stable schema with top-level plugin fields and plugin marketplace support.

- **Schema URL**: [`https://promptrek.ai/schema/v3.0.json`](v3.0.json)
- **Features**:
  - Top-level plugin fields: `mcp_servers`, `commands`, `agents`, `hooks`
  - Plugin marketplace support via `plugins` field
  - Markdown-first content approach
  - Lossless bidirectional sync
- **Recommended**: Use this for all new projects

[Download v3.0 Schema](v3.0.json){: .btn .btn-primary}

---

### v2.1 (Legacy)

**Schema Version**: 2.1.x

Legacy schema with nested plugin structure.

- **Schema URL**: [`https://promptrek.ai/schema/v2.1.json`](v2.1.json)
- **Features**:
  - Nested plugin structure: `plugins.mcp_servers`, `plugins.commands`, etc.
  - Markdown-first content approach
  - Lossless bidirectional sync
- **Note**: Consider migrating to v3.0

[Download v2.1 Schema](v2.1.json){: .btn}

---

### v2.0 (Legacy)

**Schema Version**: 2.0.x

Simplified markdown-first schema without plugin support.

- **Schema URL**: [`https://promptrek.ai/schema/v2.0.json`](v2.0.json)
- **Features**:
  - Markdown-first content approach
  - No plugin support
- **Note**: Consider migrating to v3.0

[Download v2.0 Schema](v2.0.json){: .btn}

</div>

## Usage in Your Editor

### VS Code

Add a schema reference at the top of your `project.promptrek.yaml`:

```yaml
# yaml-language-server: $schema=https://promptrek.ai/schema/v3.0.json
schema_version: 3.0.0
metadata:
  title: My Project
  description: Project description
content: |
  # Your markdown content here
```

### IntelliJ IDEA / WebStorm

1. Go to **Settings** → **Languages & Frameworks** → **Schemas and DTDs** → **JSON Schema Mappings**
2. Add a new mapping:
   - **Name**: PrompTrek UPF v3.0
   - **Schema file or URL**: `https://promptrek.ai/schema/v3.0.json`
   - **File path pattern**: `*.promptrek.yaml`

## Programmatic Validation

### Python

```python
import json
import yaml
from jsonschema import validate

# Load the schema
with open('v3.0.json') as f:
    schema = json.load(f)

# Load your YAML file
with open('project.promptrek.yaml') as f:
    data = yaml.safe_load(f)

# Validate
validate(instance=data, schema=schema)
```

### JavaScript/TypeScript

```javascript
const Ajv = require('ajv');
const yaml = require('js-yaml');
const fs = require('fs');

// Load schema
const schema = JSON.parse(fs.readFileSync('v3.0.json', 'utf8'));

// Load YAML
const data = yaml.load(fs.readFileSync('project.promptrek.yaml', 'utf8'));

// Validate
const ajv = new Ajv();
const validate = ajv.compile(schema);
const valid = validate(data);

if (!valid) console.log(validate.errors);
```

## Migration

To migrate between schema versions, use the PrompTrek CLI:

```bash
# Migrate from v2.x to v3.0
promptrek migrate project.promptrek.yaml -o project.v3.promptrek.yaml

# Or migrate in-place
promptrek migrate project.promptrek.yaml --in-place
```

## Schema Generation

These schemas are automatically generated from the Pydantic models in the PrompTrek codebase.

To regenerate schemas (for contributors):

```bash
cd /path/to/promptrek
python scripts/generate_schemas.py
```

## Resources

- [PrompTrek Documentation]({{ site.baseurl }}/)
- [Quick Start Guide]({{ site.baseurl }}/quick-start)
- [User Guide]({{ site.baseurl }}/user-guide)
- [GitHub Repository](https://github.com/flamingquaks/promptrek)

## Questions?

If you have questions or need help with the schemas, please:

- Check the [documentation]({{ site.baseurl }}/)
- Open an [issue on GitHub](https://github.com/flamingquaks/promptrek/issues)
- Join the discussion in [GitHub Discussions](https://github.com/flamingquaks/promptrek/discussions)
