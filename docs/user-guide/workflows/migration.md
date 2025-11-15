# Migration Guide

This guide helps you migrate PrompTrek configurations between schema versions.

## Overview

PrompTrek provides automated migration tools and clear migration paths for upgrading from older schema versions to the latest format.

**Current recommended version**: v3.1.0

## Migration Paths

```
v1.x → v2.0 → v3.0 → v3.1
  └────────→ v3.0 → v3.1 (recommended)
            └───────→ v3.1 (direct)
```

## Quick Migration

### Automatic Migration

Use the `migrate` command for automatic migration:

```bash
# Migrate to new file
promptrek migrate old-file.promptrek.yaml -o new-file.promptrek.yaml

# Migrate in place
promptrek migrate old-file.promptrek.yaml --in-place

# Migrate multiple files
for file in *.promptrek.yaml; do
  promptrek migrate "$file" --in-place
done
```

### Validation After Migration

Always validate after migration:

```bash
promptrek validate migrated-file.promptrek.yaml
promptrek generate migrated-file.promptrek.yaml --all --dry-run
```

## v2.1 to v3.0/v3.1 Migration

### What Changed

**Major change**: Plugin fields moved to top level

**Before (v2.1)**:
```yaml
schema_version: "2.1.0"

plugins:
  mcp_servers:
    - name: github
      command: npx

  commands:
    - name: review
      prompt: "Review code"

  agents:
    - name: test-gen
      system_prompt: "Generate tests"

  hooks:
    - name: pre-commit
      event: pre-commit
      command: "npm test"
```

**After (v3.0/v3.1)**:
```yaml
schema_version: "3.1.0"

# Plugin fields are now top-level
mcp_servers:
  - name: github
    command: npx

commands:
  - name: review
    prompt: "Review code"

agents:
  - name: test-gen
    prompt: "Generate tests"  # v3.1: renamed from system_prompt

hooks:
  - name: pre-commit
    event: pre-commit
    command: "npm test"
```

### Migration Steps

1. **Update schema version**:
   ```yaml
   schema_version: "3.1.0"
   ```

2. **Move plugin fields to top level**:
   ```yaml
   # Remove plugins wrapper
   # plugins:
   #   mcp_servers: [...]

   # Use top-level fields
   mcp_servers: [...]
   commands: [...]
   agents: [...]
   hooks: [...]
   ```

3. **Update agent prompts** (v3.1 only):
   ```yaml
   # v2.1/v3.0
   agents:
     - name: my-agent
       system_prompt: "Brief instructions"

   # v3.1
   agents:
     - name: my-agent
       prompt: |
         # Full Markdown Instructions
         Detailed guidelines...
   ```

4. **Validate**:
   ```bash
   promptrek validate project.promptrek.yaml
   ```

### Automatic Migration Example

```bash
# Before migration
$ cat project-v2.promptrek.yaml
schema_version: "2.1.0"
metadata:
  title: "My Project"
plugins:
  mcp_servers:
    - name: github
      command: npx

# Run migration
$ promptrek migrate project-v2.promptrek.yaml -o project-v3.promptrek.yaml

✅ Migrated project-v2.promptrek.yaml → project-v3.promptrek.yaml
   Schema version: 2.1.0 → 3.1.0
   Changes:
   - Moved plugins.mcp_servers → mcp_servers
   - Moved plugins.commands → commands
   - Moved plugins.agents → agents
   - Moved plugins.hooks → hooks

# After migration
$ cat project-v3.promptrek.yaml
schema_version: "3.1.0"
metadata:
  title: "My Project"
mcp_servers:
  - name: github
    command: npx
```

## v2.0 to v3.1 Migration

### What Changed

- No breaking changes from v2.0 to v3.0
- Can add plugin fields at top level
- Schema version update required

### Migration Steps

1. **Update schema version**:
   ```yaml
   schema_version: "3.1.0"
   ```

2. **Add plugin fields** (if needed):
   ```yaml
   # v2.0 files work as-is in v3.x
   # Add new plugin features:
   mcp_servers:
     - name: github
       command: npx
   ```

3. **Validate**:
   ```bash
   promptrek validate project.promptrek.yaml
   ```

## v1.x to v3.1 Migration

### What Changed

Major architectural changes:

- `targets` field removed (replaced by adapter system)
- `metadata` structure changed
- `variables` moved to top level
- New `content` and `documents` structure
- Plugin system added

### Migration Approach

**Recommended**: Start fresh with `promptrek init`

```bash
# Create new v3.1 file
promptrek init --v3 -o project-v3.promptrek.yaml

# Manually migrate content:
# 1. Copy metadata (update structure)
# 2. Copy variables
# 3. Copy prompt content
# 4. Validate
promptrek validate project-v3.promptrek.yaml
```

### Manual Migration Example

**Before (v1.x)**:
```yaml
targets: [claude, cursor]

metadata:
  name: "My Project"
  author: "Developer"

variables:
  PROJECT: "MyApp"

prompt: |
  # MyApp
  Development guidelines...
```

**After (v3.1)**:
```yaml
schema_version: "3.1.0"

metadata:
  title: "My Project"              # Renamed from 'name'
  description: "Project description"  # Required
  author: "Developer"

variables:
  PROJECT: "MyApp"

content: |                         # Renamed from 'prompt'
  # MyApp
  Development guidelines...
```

## Backward Compatibility

### Supported Versions

v3.x tools support:

- ✅ v3.1 files (native)
- ✅ v3.0 files (100% compatible)
- ⚠️ v2.1 files (with deprecation warnings)
- ⚠️ v2.0 files (with warnings)
- ❌ v1.x files (limited support, migrate recommended)

### Deprecation Warnings

When using v2.1 files with v3.x tools:

```
⚠️  DEPRECATION WARNING in project.promptrek.yaml:
   Detected nested plugin structure (plugins.mcp_servers, etc.)
   This structure is deprecated in v3.0 and will be removed in v4.0.
   Please migrate to top-level fields:
     - Move 'plugins.mcp_servers' → 'mcp_servers' (top-level)
     - Move 'plugins.commands' → 'commands' (top-level)
     - Move 'plugins.agents' → 'agents' (top-level)
     - Move 'plugins.hooks' → 'hooks' (top-level)
   Run: promptrek migrate project.promptrek.yaml to auto-migrate
```

## Migration Checklist

### Pre-Migration

- [ ] Back up current configuration files
- [ ] Document current editor setup
- [ ] Note any custom workflows

### Migration

- [ ] Run `promptrek migrate` on all files
- [ ] Update schema version to latest (v3.1.0)
- [ ] Validate all migrated files
- [ ] Test generation with `--dry-run`

### Post-Migration

- [ ] Generate for all editors: `promptrek generate --all`
- [ ] Test with actual AI editors
- [ ] Update team documentation
- [ ] Commit migrated files

### Verification

```bash
# Complete verification workflow
promptrek validate *.promptrek.yaml
promptrek generate --all --dry-run
promptrek generate --all
# Test with your editor
git add *.promptrek.yaml
git commit -m "chore: migrate to PrompTrek v3.1.0"
```

## Troubleshooting

### Migration Command Not Found

**Problem**: `promptrek migrate` command not available

**Solution**: Update PrompTrek to latest version

```bash
cd /path/to/promptrek
uv sync
promptrek --version  # Should be v3.x+
```

### Validation Errors After Migration

**Problem**: Validation fails after migration

**Common issues**:

1. **Missing required fields**:
   ```yaml
   # Add required metadata fields
   metadata:
     title: "My Project"         # Required
     description: "Description"  # Required
   ```

2. **Wrong field names**:
   ```yaml
   # Correct field names in v3.x:
   mcp_servers:   # Not mcp_server or mcpServers
   commands:      # Not command
   agents:        # Not agent
   hooks:         # Not hook
   ```

3. **Incorrect structure**:
   ```yaml
   # Ensure plugins fields are at top level
   # Wrong:
   plugins:
     mcp_servers: [...]

   # Correct:
   mcp_servers: [...]
   ```

### Variables Not Working

**Problem**: Variables not substituted after migration

**Solution**: Verify variable syntax

```yaml
# Correct (triple braces)
env:
  TOKEN: "{{{ GITHUB_TOKEN }}}"

# Wrong
env:
  TOKEN: "{{ GITHUB_TOKEN }}"     # Double braces
  TOKEN: "${GITHUB_TOKEN}"        # Dollar sign
```

## Best Practices

!!! tip "Test Before Committing"
    Always test migrations before committing:
    ```bash
    promptrek migrate old.yaml -o new.yaml
    promptrek validate new.yaml
    promptrek generate new.yaml --all --dry-run
    ```

!!! tip "Migrate One File at a Time"
    For complex projects, migrate and test files individually before doing bulk migration.

!!! warning "Update Team Documentation"
    After migration, update team docs to reference new schema version and structure.

!!! note "Keep Old Files Temporarily"
    Keep backup of old files until team confirms new setup works:
    ```bash
    cp project.promptrek.yaml project.promptrek.yaml.v2.1.backup
    promptrek migrate project.promptrek.yaml --in-place
    ```

## See Also

- [Schema Versions Overview](../configuration/schema-versions.md)
- [Schema v3.1.0 Guide](../configuration/schema-v3.1.md)
- [V3 Migration Guide](../../../docs/V3_MIGRATION_GUIDE.md) (detailed)
- [Validate Command](../../cli/commands/validate.md)
