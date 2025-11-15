# Deprecation Warnings

This page explains PrompTrek's deprecation warning system and how to handle deprecation notices.

## Overview

PrompTrek uses a centralized deprecation warning system to ensure consistent messaging and make future migrations easier. When features become deprecated, you'll receive clear warnings with migration paths.

## Current Deprecations

### Schema v2.x Nested Plugins (Deprecated in v3.0)

**Status:** Deprecated in v3.0.0, will be removed in v4.0.0

**What's Deprecated:**
The nested `plugins.*` structure from schema v2.1:

```yaml
schema_version: "2.1.0"
plugins:                    # Deprecated wrapper
  mcp_servers: [...]        # Nested field
  commands: [...]           # Nested field
  agents: [...]             # Nested field
  hooks: [...]              # Nested field
```

**Replacement:**
Top-level plugin fields in schema v3.0+:

```yaml
schema_version: "3.1.0"
mcp_servers: [...]          # Top-level field
commands: [...]             # Top-level field
agents: [...]               # Top-level field
hooks: [...]                # Top-level field
```

**Migration:**
```bash
# Auto-migrate to v3.0
promptrek migrate project.promptrek.yaml -o project-v3.promptrek.yaml

# Or migrate in place
promptrek migrate project.promptrek.yaml --in-place
```

**Timeline:**
- v2.1.0 (Oct 2025): Introduced nested structure
- v3.0.0 (Oct 2025): **Deprecated**, still works with warnings
- v4.0.0 (Future): Will be removed entirely

### Schema v3.0 Agent `system_prompt` Field (Deprecated in v3.1)

**Status:** Deprecated in v3.1.0, will be removed in v4.0.0

**What's Deprecated:**
The `system_prompt` field in agent definitions:

```yaml
agents:
  - name: code-reviewer
    system_prompt: "You are a code reviewer..."  # Deprecated
```

**Replacement:**
Use the `prompt` field instead:

```yaml
agents:
  - name: code-reviewer
    prompt: "You are a code reviewer..."  # New in v3.1
```

**Why Changed:**
Consistency with the `commands.prompt` field and clearer naming.

**Migration:**
```bash
# Auto-migrate to v3.1
promptrek migrate project.promptrek.yaml -o project-v3.1.promptrek.yaml
```

## Warning Types

### Parser Warnings (Detailed)

**When Shown:** When parsing a file with deprecated features

**Example Output:**
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

**Where:** Printed to stderr during parsing

### Adapter Warnings (Concise)

**When Shown:** When generating editor files from deprecated configurations

**Example Output:**
```
⚠️  Using deprecated plugins.mcp_servers structure (use top-level mcp_servers in v3.0)
```

**Where:** Printed during file generation

## Backward Compatibility

### Auto-Promotion

PrompTrek automatically handles deprecated features:

1. **Emits deprecation warning** to stderr
2. **Promotes nested fields** to top-level internally
3. **Continues processing** normally

This ensures schema v2.x files work without modification while encouraging migration.

**Example:**
```yaml
# v2.1 file with deprecated structure
schema_version: "2.1.0"
plugins:
  mcp_servers:
    - name: github
      command: npx
      args: ["-y", "@modelcontextprotocol/server-github"]
```

**Automatically promoted to:**
```yaml
# Internal representation (v3.0 compatible)
schema_version: "2.1.0"  # Original version preserved
mcp_servers:              # Promoted to top-level
  - name: github
    command: npx
    args: ["-y", "@modelcontextprotocol/server-github"]
```

### Compatibility Matrix

| PrompTrek Version | Schema v1.x | Schema v2.x | Schema v3.0 | Schema v3.1 |
|-------------------|-------------|-------------|-------------|-------------|
| v0.3.x | ✅ Full | ✅ Full | ✅ Full | ❌ Not supported |
| v0.4.x | ✅ Full | ⚠️ Deprecated | ✅ Full | ✅ Full |
| v0.5.x+ | ✅ Full | ⚠️ Deprecated | ✅ Full | ✅ Full |
| v1.0.0 (future) | ⚠️ Deprecated | ❌ Removed | ✅ Full | ✅ Full |

✅ Full support | ⚠️ Works with warnings | ❌ Not supported

## Handling Warnings

### Option 1: Migrate Files (Recommended)

Use the built-in migration tool:

```bash
# Migrate single file
promptrek migrate project.promptrek.yaml -o project-v3.promptrek.yaml

# Migrate in place
promptrek migrate project.promptrek.yaml --in-place

# Migrate all files in directory
find . -name "*.promptrek.yaml" -exec promptrek migrate {} --in-place \;
```

**Benefits:**
- Future-proof configuration
- No warnings
- Access to new features
- Easier to read and maintain

### Option 2: Suppress Warnings (Temporary)

If you need to suppress warnings temporarily:

```bash
# Redirect stderr to /dev/null
promptrek generate project.promptrek.yaml --editor claude 2>/dev/null

# Or use a future environment variable (if implemented)
PROMPTREK_SUPPRESS_WARNINGS=1 promptrek generate project.promptrek.yaml
```

!!! warning "Not Recommended"
    Suppressing warnings doesn't fix the underlying issue. Migrate when possible.

### Option 3: Continue Using Deprecated Features

You can continue using deprecated features until they're removed:

```bash
# v2.1 files work in v0.4.x and v0.5.x
promptrek generate old-v2.promptrek.yaml --all
```

**Considerations:**
- Warnings will be shown
- Features may be removed in future versions
- Missing out on new features
- Consider setting a migration deadline

## Migration Guide

### v2.x to v3.0 Migration

**Step 1:** Check current schema version:
```bash
head -1 project.promptrek.yaml
# schema_version: "2.1.0"
```

**Step 2:** Run migration:
```bash
promptrek migrate project.promptrek.yaml -o project-v3.promptrek.yaml
```

**Step 3:** Review changes:
```bash
diff project.promptrek.yaml project-v3.promptrek.yaml
```

**Step 4:** Test with validators:
```bash
promptrek validate project-v3.promptrek.yaml
```

**Step 5:** Generate and test:
```bash
promptrek generate project-v3.promptrek.yaml --all
```

**Step 6:** Commit updated file:
```bash
mv project-v3.promptrek.yaml project.promptrek.yaml
git add project.promptrek.yaml
git commit -m "chore: migrate to schema v3.0"
```

### v3.0 to v3.1 Migration

**What Changes:**
- `agents[].system_prompt` → `agents[].prompt`
- Workflow support added (optional)

**Migration:**
```bash
promptrek migrate project-v3.0.promptrek.yaml -o project-v3.1.promptrek.yaml
```

## For Developers

### Adding Deprecation Warnings

When deprecating features in future versions:

**1. Add warning method** to `DeprecationWarnings` class:
```python
# src/promptrek/core/exceptions.py
@staticmethod
def v4_feature_warning(source: str) -> str:
    """Get deprecation warning for v4.0 feature."""
    return (
        f"\n⚠️  DEPRECATION WARNING in {source}:\n"
        f"   Feature X is deprecated in v4.0...\n"
        f"   Please migrate to feature Y\n"
    )
```

**2. Use in parser or adapters:**
```python
from ..core.exceptions import DeprecationWarnings

warning = DeprecationWarnings.v4_feature_warning(source)
print(warning, file=sys.stderr)
```

**3. Document in this file:**
- Add to "Current Deprecations" section
- Specify removal version
- Provide migration path

**4. Add tests:**
```python
def test_deprecated_feature_warning(capsys):
    """Test that deprecation warning is shown."""
    parser = UPFParser()
    prompt = parser.parse_file("v2_nested_plugins.yaml")

    captured = capsys.readouterr()
    assert "DEPRECATION WARNING" in captured.err
```

## FAQ

### Q: Will v2.x files stop working immediately?

**A:** No. v2.x files continue to work in v3.x with deprecation warnings. They will be removed in v4.0.0.

### Q: Can I use both old and new structures in the same file?

**A:** Yes, but top-level fields take precedence:
```yaml
plugins:
  mcp_servers: [...]    # Ignored if top-level exists
mcp_servers: [...]      # Takes precedence
```

### Q: How do I know if my files are using deprecated features?

**A:** Run validation:
```bash
promptrek validate project.promptrek.yaml
```
Any deprecation warnings will be shown.

### Q: Will this affect my CI/CD pipelines?

**A:** Warnings are printed to stderr but don't cause failures. Your pipelines should continue to work. Consider migrating proactively to avoid warnings in logs.

### Q: When should I migrate?

**A:** As soon as possible:
- Migrating is easy with the built-in tool
- Future versions may not support deprecated features
- New features require new schema versions
- Cleaner, more maintainable configuration

## Best Practices

### For Users

1. **Act Early** - Migrate as soon as you see warnings
2. **Test After Migration** - Validate and test migrated files thoroughly
3. **Update Documentation** - Update team docs with new structure
4. **Use Version Control** - Commit v3.0 files separately for easy rollback
5. **Communicate** - Inform team members about migration

### For Contributors

1. **Use Centralized System** - Always use `DeprecationWarnings` class
2. **Consistent Messaging** - Follow existing warning format
3. **Document Thoroughly** - Update this file when adding warnings
4. **Test Warnings** - Add tests for deprecation warning behavior
5. **Provide Migration Path** - Always offer clear migration instructions
6. **Give Notice** - Deprecate first, remove later (at least one major version gap)

## Resources

- **[V3 Migration Guide](../V3_MIGRATION_GUIDE.md)** - Complete migration instructions
- **[Changelog](changelog.md)** - Version history and changes
- **[GitHub Issues](https://github.com/flamingquaks/promptrek/issues)** - Report problems
- **[Discussions](https://github.com/flamingquaks/promptrek/discussions)** - Ask questions

## Changelog

- **2025-10-16**: Initial documentation of centralized warning system
- **2025-10-16**: Documented v3.0 nested plugins deprecation
- **2025-10-27**: Added v3.1 agent `system_prompt` deprecation

---

**Remember:** Deprecation warnings are helpful reminders to keep your configuration up-to-date. PrompTrek maintains backward compatibility while guiding you toward better, cleaner configurations.
