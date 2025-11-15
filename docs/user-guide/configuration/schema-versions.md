# Schema Versions Overview

PrompTrek uses semantic versioning for its Universal Prompt Format (UPF) schema. This page provides an overview of all schema versions, their features, and migration paths.

## Current Version

**v3.1.0** is the latest and recommended schema version.

## Version History

### v3.1.0 (Latest)

**Status**: Current, actively maintained
**Released**: 2024

#### Key Features

- Multi-step workflow support for complex commands
- Enhanced command system with `multi_step`, `tool_calls`, and `steps` fields
- Improved agent capabilities with `prompt` field replacing `system_prompt`
- Better workflow orchestration
- Full backward compatibility with v3.0.0

#### What's New

- **Workflow Steps**: Define structured multi-step workflows with the `steps` array
- **Tool Calls**: Specify which tools/commands a workflow uses
- **Enhanced Agents**: Use `prompt` field for full markdown instructions (replaces `system_prompt`)
- **Workflow Metadata**: Better tracking of command execution flows

#### Use Cases

- Complex CI/CD workflows
- Multi-step code generation tasks
- Orchestrated testing procedures
- Advanced agent automation

[View v3.1.0 detailed documentation](schema-v3.1.md)

---

### v3.0.0

**Status**: Stable, maintained
**Released**: 2024

#### Key Features

- Top-level plugin fields (breaking change from v2.1)
- Cleaner, flatter configuration structure
- Removed nested `plugins` wrapper
- Improved IDE autocomplete support
- Better schema validation

#### Migration from v2.1

Plugin fields moved to top level:

```yaml
# v2.1 (old)
plugins:
  mcp_servers: [...]
  commands: [...]

# v3.0 (new)
mcp_servers: [...]
commands: [...]
```

#### Benefits

- **Simpler structure**: No unnecessary nesting
- **Better tooling**: Easier autocomplete and validation
- **Consistency**: Aligns with markdown-first philosophy
- **Future-proof**: Easier to add new plugin types

[Migrate from v2.1 to v3.0](../../user-guide/workflows/migration.md)

---

### v2.1.0

**Status**: Deprecated, supported until v4.0
**Released**: 2023

#### Key Features

- Plugin system introduction
- Nested `plugins` wrapper
- MCP servers, commands, agents, hooks support
- Trust metadata for security

#### Deprecation Notice

!!! warning "Deprecated Structure"
    The nested `plugins.*` structure is deprecated in v3.0 and will be removed in v4.0. Please migrate to v3.0+ for top-level fields.

When using v2.1 files with v3.0+ tools, you'll see warnings:

```
⚠️  DEPRECATION WARNING in project.promptrek.yaml:
   Detected nested plugin structure (plugins.mcp_servers, etc.)
   This structure is deprecated in v3.0 and will be removed in v4.0.
   Run: promptrek migrate project.promptrek.yaml to auto-migrate
```

---

### v2.0.0

**Status**: Legacy, limited support
**Released**: 2023

#### Key Features

- Markdown-first approach
- Multi-document support
- Variable system
- Path-specific rules
- Editor-agnostic design

#### Notable Changes from v1.x

- Removed editor-specific targets in favor of universal generation
- Introduced `documents` array for multi-file support
- Added `variables` section for templating
- Simplified metadata structure

---

### v1.0.0 - v1.2.0

**Status**: Legacy, no longer maintained
**Released**: 2022

#### Key Features

- Basic prompt file support
- Editor targets specification
- Simple variable substitution
- Basic validation

#### Why Upgrade

v1.x is no longer maintained. Benefits of upgrading:

- Better editor support
- Plugin system
- Multi-document support
- Advanced features
- Active development

---

## Feature Comparison Matrix

| Feature | v1.x | v2.0 | v2.1 | v3.0 | v3.1 |
|---------|------|------|------|------|------|
| Basic Prompts | ✅ | ✅ | ✅ | ✅ | ✅ |
| Variables | ✅ | ✅ | ✅ | ✅ | ✅ |
| Multi-document | ❌ | ✅ | ✅ | ✅ | ✅ |
| MCP Servers | ❌ | ❌ | ✅ | ✅ | ✅ |
| Commands | ❌ | ❌ | ✅ | ✅ | ✅ |
| Agents | ❌ | ❌ | ✅ | ✅ | ✅ |
| Hooks | ❌ | ❌ | ✅ | ✅ | ✅ |
| Top-level plugins | ❌ | ❌ | ❌ | ✅ | ✅ |
| Multi-step workflows | ❌ | ❌ | ❌ | ❌ | ✅ |
| Tool calls tracking | ❌ | ❌ | ❌ | ❌ | ✅ |

## Schema Version Selection

### When to Use v3.1.0

Use v3.1.0 if you need:

- ✅ Multi-step workflows
- ✅ Complex command orchestration
- ✅ Enhanced agent instructions
- ✅ Latest features and improvements
- ✅ Future-proof configuration

### When to Use v3.0.0

Use v3.0.0 if you:

- ✅ Want the stable top-level plugin structure
- ✅ Don't need workflow features yet
- ✅ Are migrating from v2.1
- ✅ Need a stable base without cutting-edge features

### When to Migrate

You should migrate if you're using:

- ⚠️ v2.1 or earlier (deprecation warnings)
- ⚠️ v1.x (no longer supported)

## Migration Paths

### From v2.1 to v3.0/v3.1

**Automatic migration**:
```bash
promptrek migrate project.promptrek.yaml -o project-v3.promptrek.yaml
```

**Changes**:
- Move `plugins.mcp_servers` → `mcp_servers`
- Move `plugins.commands` → `commands`
- Move `plugins.agents` → `agents`
- Move `plugins.hooks` → `hooks`
- Update `schema_version: "3.1.0"`

### From v2.0 to v3.1

**Steps**:
1. Update schema version to v3.0.0 or v3.1.0
2. Add plugins if needed (no breaking changes)
3. Validate with `promptrek validate`

### From v1.x to v3.1

**Recommended approach**:
1. Start fresh with `promptrek init --v3`
2. Manually migrate content and metadata
3. Validate thoroughly

!!! tip "Migration Help"
    Use `promptrek migrate --help` to see all migration options. The migrate command handles most conversions automatically.

## Version Detection

PrompTrek automatically detects schema versions:

```yaml
# In your .promptrek.yaml file
schema_version: "3.1.0"  # Explicit version
```

If not specified, PrompTrek attempts to infer the version from file structure and shows warnings.

## Backward Compatibility

### v3.x Compatibility

- ✅ v3.1 tools support v3.0 files (100% compatible)
- ✅ v3.0 tools support v2.1 files (with deprecation warnings)
- ⚠️ v3.x tools support v1.x files (limited, warnings)

### Forward Compatibility

- ❌ v2.1 tools cannot parse v3.0+ files (upgrade required)
- ❌ v1.x tools cannot parse v2.0+ files (upgrade required)

## Validation by Version

Validate your configuration for a specific schema version:

```bash
# Validates using version specified in file
promptrek validate project.promptrek.yaml

# Verbose validation shows schema version
promptrek --verbose validate project.promptrek.yaml
```

## Best Practices

!!! tip "Use Latest Version"
    Always use the latest stable schema version (v3.1.0) for new projects to benefit from latest features and improvements.

!!! tip "Migrate Proactively"
    Don't wait for v4.0 to migrate from v2.1. Migrate now to avoid breaking changes.

!!! warning "Test After Migration"
    Always test generated files after migration:
    ```bash
    promptrek migrate old.yaml -o new.yaml
    promptrek validate new.yaml
    promptrek generate new.yaml --all --dry-run
    ```

!!! note "Keep Documentation Updated"
    When upgrading schema versions, update your project documentation to reflect the new structure.

## Schema Files

JSON Schema files are available for IDE validation:

- [v3.1.0 Schema](/schema/v3.1.0.json)
- [v3.0.0 Schema](/schema/v3.0.0.json)
- [v2.1.0 Schema](/schema/v2.1.0.json)

Configure in your IDE:

```yaml
# yaml-language-server: $schema=https://flamingquaks.github.io/promptrek/schema/v3.1.0.json
schema_version: "3.1.0"
metadata:
  title: "My Project"
  description: "Project description"
```

## Getting Help

- [Migration Guide](../../user-guide/workflows/migration.md) - Step-by-step migration instructions
- [Schema v3.1.0 Reference](../../schema/v3.1.0.md) - Complete v3.1.0 specification
- [Schema v3.0.0 Reference](../../schema/v3.0.0.md) - Complete v3.0.0 specification
- [GitHub Discussions](https://github.com/flamingquaks/promptrek/discussions) - Ask questions

## Version Support Timeline

| Version | Status | Support Until |
|---------|--------|---------------|
| v3.1.x | Current | Ongoing |
| v3.0.x | Stable | Ongoing |
| v2.1.x | Deprecated | v4.0 release |
| v2.0.x | Legacy | Limited |
| v1.x | End of Life | None |

---

**Next Steps**:

- [Learn about Schema v3.1.0](schema-v3.1.md)
- [Migrate your files](../../user-guide/workflows/migration.md)
- [Configure metadata](metadata.md)
