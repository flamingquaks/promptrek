# Schema Reference

PrompTrek uses JSON Schema to define the Universal Prompt Format (UPF). This reference documents all schema versions and their specifications.

## Current Schema Version

**v3.1.0** is the latest and recommended schema version.

## Available Schemas

### v3.1.0 (Current)

**Released**: 2024
**Status**: Current, actively maintained
**Schema File**: [v3.1.0.json](/schema/v3.1.0.json)

**Key Features**:
- Multi-step workflow support
- Enhanced agent prompts
- Tool call tracking
- Structured workflow steps
- Full backward compatibility with v3.0.0

[View v3.1.0 Reference](v3.1.0.md)

### v3.0.0 (Stable)

**Released**: 2024
**Status**: Stable, maintained
**Schema File**: [v3.0.0.json](/schema/v3.0.0.json)

**Key Features**:
- Top-level plugin fields
- Cleaner structure
- Removed nested `plugins` wrapper
- Better validation support

[View v3.0.0 Reference](v3.0.0.md)

### v2.1.0 (Deprecated)

**Released**: 2023
**Status**: Deprecated, supported until v4.0
**Schema File**: [v2.1.0.json](/schema/v2.1.0.json)

**Key Features**:
- Plugin system introduction
- Nested `plugins` structure
- MCP, commands, agents, hooks

!!! warning "Deprecated"
    v2.1.0 is deprecated. Migrate to v3.0+ for top-level plugin fields.

### v2.0.0 (Legacy)

**Released**: 2023
**Status**: Legacy, limited support
**Schema File**: [v2.0.0.json](/schema/v2.0.0.json)

**Key Features**:
- Markdown-first approach
- Multi-document support
- Variable system

## Schema Structure

All PrompTrek schemas follow this basic structure:

```yaml
schema_version: "3.1.0"       # Required: Schema version

metadata:                      # Required: File metadata
  title: string
  description: string
  version: string (optional)
  author: string (optional)
  created: string (optional)
  updated: string (optional)
  tags: array (optional)

content: string               # Required: Main markdown content

# Optional fields
content_description: string
content_always_apply: boolean
variables: object
documents: array

# Plugin fields (top-level in v3.x)
mcp_servers: array
commands: array
agents: array
hooks: array

ignore_editor_files: boolean
```

## Using Schemas

### IDE Integration

Configure your IDE to use PrompTrek schemas for validation and autocomplete.

#### VSCode / Cursor

Add schema reference to your `.promptrek.yaml` files:

```yaml
# yaml-language-server: $schema=https://flamingquaks.github.io/promptrek/schema/v3.1.0.json
schema_version: "3.1.0"
metadata:
  title: "My Project"
  description: "Project description"
```

Or configure globally in VSCode settings:

```json
{
  "yaml.schemas": {
    "https://flamingquaks.github.io/promptrek/schema/v3.1.0.json": "*.promptrek.yaml"
  }
}
```

#### JetBrains IDEs

1. Open Settings → Languages & Frameworks → Schemas and DTDs → JSON Schema Mappings
2. Add new mapping:
   - **Name**: PrompTrek v3.1.0
   - **Schema file**: `https://flamingquaks.github.io/promptrek/schema/v3.1.0.json`
   - **Schema version**: JSON Schema version 7
   - **File path pattern**: `*.promptrek.yaml`

### CLI Validation

PrompTrek CLI automatically validates against the specified schema version:

```bash
# Validates using schema_version field
promptrek validate project.promptrek.yaml
```

## Schema Features

### Required Fields

All schemas require:

- `schema_version`: Schema version string
- `metadata`: Metadata object with `title` and `description`
- `content`: Main markdown content string

### Optional Fields

Common optional fields across versions:

- `content_description`: Description for main content
- `content_always_apply`: Whether content always applies (default: true)
- `variables`: Template variables object
- `documents`: Additional documents array
- `ignore_editor_files`: Auto-manage .gitignore (default: true)

### Plugin Fields

v3.0+ schemas include top-level plugin fields:

- `mcp_servers`: MCP server configurations
- `commands`: Slash commands and workflows
- `agents`: Autonomous agent configurations
- `hooks`: Event-driven automation hooks

## Version Migration

### Automatic Migration

Use PrompTrek CLI to migrate between versions:

```bash
# Migrate to latest version
promptrek migrate old-file.yaml -o new-file.yaml

# In-place migration
promptrek migrate project.yaml --in-place
```

### Manual Migration

See version-specific migration guides:

- [v2.1 to v3.0/v3.1](../user-guide/workflows/migration.md)
- [v2.0 to v3.x](../user-guide/workflows/migration.md)
- [v1.x to v3.x](../user-guide/workflows/migration.md)

## Schema Validation

### Online Validation

Validate your YAML against the schema online:

1. Copy your `.promptrek.yaml` content
2. Visit [JSON Schema Validator](https://www.jsonschemavalidator.net/)
3. Paste schema URL: `https://flamingquaks.github.io/promptrek/schema/v3.1.0.json`
4. Paste your YAML (converted to JSON)

### CLI Validation

```bash
# Basic validation
promptrek validate project.promptrek.yaml

# Verbose validation with schema details
promptrek --verbose validate project.promptrek.yaml
```

### Pre-commit Validation

Automatically validate on git commit:

```bash
promptrek install-hooks
pre-commit install
```

## Schema Downloads

Download schemas for offline use:

```bash
# v3.1.0
curl -O https://flamingquaks.github.io/promptrek/schema/v3.1.0.json

# v3.0.0
curl -O https://flamingquaks.github.io/promptrek/schema/v3.0.0.json
```

## Schema Development

### Contributing to Schemas

Schema definitions are maintained in the PrompTrek repository:

- Location: `gh-pages/schema/`
- Generated from: Python Pydantic models
- Format: JSON Schema Draft 7

To propose schema changes:

1. Modify Pydantic models in `src/promptrek/core/models.py`
2. Generate updated JSON Schema
3. Submit pull request with tests

### Schema Versioning

PrompTrek follows semantic versioning for schemas:

- **Major**: Breaking changes (e.g., v2.x → v3.x)
- **Minor**: New features, backward compatible (e.g., v3.0 → v3.1)
- **Patch**: Bug fixes, clarifications (e.g., v3.1.0 → v3.1.1)

## Frequently Asked Questions

### Which schema version should I use?

Use **v3.1.0** for new projects. It's the latest version with all features and improvements.

### Can I use an older schema version?

Yes, PrompTrek maintains backward compatibility:

- v3.1 tools support v3.0 files (100%)
- v3.x tools support v2.1 files (with warnings)
- v3.x tools support v2.0 files (with warnings)
- v3.x tools support v1.x files (limited)

### How do I upgrade my schema version?

Use the migrate command:

```bash
promptrek migrate project.promptrek.yaml --in-place
```

### Do I need to understand JSON Schema?

No. PrompTrek provides:

- CLI validation
- IDE autocomplete
- Clear error messages
- Migration tools

Understanding JSON Schema helps for advanced use cases but isn't required.

## See Also

- [v3.1.0 Schema Reference](v3.1.0.md) - Detailed v3.1.0 specification
- [v3.0.0 Schema Reference](v3.0.0.md) - Detailed v3.0.0 specification
- [Schema Versions Guide](../user-guide/configuration/schema-versions.md) - Version comparison
- [Migration Guide](../user-guide/workflows/migration.md) - Version migration
- [Validate Command](../cli/commands/validate.md) - Validation documentation
