# PrompTrek Deprecation Warnings System

## Overview

PrompTrek uses a centralized deprecation warning system to ensure consistent messaging and make future migrations easier. This document explains how the system works and how to handle deprecation warnings.

## Centralized Warning System

### Architecture

All deprecation warnings are managed through the `DeprecationWarnings` class in `src/promptrek/core/exceptions.py`:

```python
class DeprecationWarnings:
    """Centralized deprecation warning messages for PrompTrek."""

    @staticmethod
    def v3_nested_plugins_warning(source: str) -> str:
        """Get deprecation warning for v3.0 nested plugins structure."""
        # Returns detailed warning message

    @staticmethod
    def v3_nested_plugin_field_warning(field_name: str) -> str:
        """Get short deprecation warning for a specific nested plugin field."""
        # Returns concise warning message
```

### Benefits

1. **Single Source of Truth**: All warning messages defined in one location
2. **Consistency**: Identical wording across parser and all adapters
3. **Maintainability**: Easy to update warnings for future versions
4. **Discoverability**: Developers know where to find/add deprecation warnings

## Current Deprecations

### v3.0.0: Nested Plugin Structure

**Deprecated:** Nested `plugins.*` structure in v2.1.0
**Replacement:** Top-level plugin fields in v3.0.0
**Removal:** v4.0.0

#### What's Deprecated

The nested plugin structure from v2.1:

```yaml
schema_version: "2.1.0"
plugins:                    # ❌ Deprecated wrapper
  mcp_servers: [...]        # ❌ Nested field
  commands: [...]           # ❌ Nested field
  agents: [...]             # ❌ Nested field
  hooks: [...]              # ❌ Nested field
```

#### What to Use Instead

Top-level fields in v3.0:

```yaml
schema_version: "3.0.0"
mcp_servers: [...]          # ✅ Top-level field
commands: [...]             # ✅ Top-level field
agents: [...]               # ✅ Top-level field
hooks: [...]                # ✅ Top-level field
```

## Warning Types

### 1. Parser Warning (Detailed)

**When shown:** When parsing a file with nested `plugins.*` structure

**Example output:**
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

**Code location:** `src/promptrek/core/parser.py` (line 226)

**Usage:**
```python
from ..core.exceptions import DeprecationWarnings

warning_msg = DeprecationWarnings.v3_nested_plugins_warning(source)
print(warning_msg, file=sys.stderr)
```

### 2. Adapter Warning (Concise)

**When shown:** When generating editor files from v2.1 files with nested plugins

**Example output:**
```
⚠️  Using deprecated plugins.mcp_servers structure (use top-level mcp_servers in v3.0)
```

**Code locations:** Used in 7 adapters:
- `src/promptrek/adapters/amazon_q.py` (line 187)
- `src/promptrek/adapters/claude.py` (lines 271, 277, 281, 284)
- `src/promptrek/adapters/cline.py` (line 183)
- `src/promptrek/adapters/continue_adapter.py` (lines 188, 191)
- `src/promptrek/adapters/cursor.py` (lines 186, 191, 194)
- `src/promptrek/adapters/kiro.py` (line 183)
- `src/promptrek/adapters/windsurf.py` (line 182)

**Usage:**
```python
from ..core.exceptions import DeprecationWarnings

click.echo(DeprecationWarnings.v3_nested_plugin_field_warning("mcp_servers"))
```

## Backward Compatibility

### Auto-Promotion

When the parser encounters v2.1 files with nested plugins, it automatically:

1. **Emits deprecation warning** to stderr
2. **Promotes nested fields** to top-level internally
3. **Continues processing** normally

This ensures v2.1 files work without modification.

**Implementation:** `src/promptrek/core/parser.py` lines 198-264

```python
def _handle_v3_backward_compatibility(self, data: Dict[str, Any], source: str) -> Dict[str, Any]:
    """Handle backward compatibility for v3.0 files with nested plugins structure."""

    if "plugins" in data and isinstance(data["plugins"], dict):
        old_plugins = data["plugins"]
        has_old_structure = any(
            key in old_plugins
            for key in ["mcp_servers", "commands", "agents", "hooks"]
        )

        if has_old_structure:
            # Emit deprecation warning
            warning_msg = DeprecationWarnings.v3_nested_plugins_warning(source)
            print(warning_msg, file=sys.stderr)

            # Auto-promote nested fields to top-level
            data_copy = data.copy()

            if "mcp_servers" in old_plugins and "mcp_servers" not in data_copy:
                data_copy["mcp_servers"] = old_plugins["mcp_servers"]

            # ... (similar for commands, agents, hooks)

            return data_copy

    return data
```

### Migration Timeline

| Version | Status | Details |
|---------|--------|---------|
| v2.1.0 | Released | Introduced nested `plugins.*` structure |
| v3.0.0 | Current | Nested structure deprecated, top-level recommended |
| v4.0.0 | Future | Nested structure will be removed entirely |

## Handling Warnings

### Option 1: Migrate Files (Recommended)

Use the built-in migration tool:

```bash
# Migrate single file
promptrek migrate project.promptrek.yaml -o project-v3.promptrek.yaml

# Migrate in place
promptrek migrate project.promptrek.yaml --in-place

# Migrate all files
find . -name "*.promptrek.yaml" -exec promptrek migrate {} --in-place \;
```

### Option 2: Suppress Warnings (Temporary)

If you need to suppress warnings temporarily:

```bash
# Redirect stderr to /dev/null
promptrek generate project.promptrek.yaml --editor claude 2>/dev/null

# Or set environment variable (if implemented)
PROMPTREK_SUPPRESS_WARNINGS=1 promptrek generate project.promptrek.yaml
```

**Note:** This is not recommended for long-term use.

### Option 3: Continue Using v2.1 (Not Recommended)

You can continue using v2.1 files until v4.0.0:
- Warnings will be shown but won't block functionality
- You have time to migrate gradually
- Consider setting a migration deadline before v4.0.0

## For Developers

### Adding New Deprecation Warnings

When deprecating features in future versions:

1. **Add warning method** to `DeprecationWarnings` class:
   ```python
   @staticmethod
   def v4_feature_warning(source: str) -> str:
       """Get deprecation warning for v4.0 feature."""
       return (
           f"\n⚠️  DEPRECATION WARNING in {source}:\n"
           f"   Feature X is deprecated in v4.0...\n"
           f"   Please migrate to feature Y\n"
       )
   ```

2. **Use in parser or adapters:**
   ```python
   from ..core.exceptions import DeprecationWarnings

   warning = DeprecationWarnings.v4_feature_warning(source)
   print(warning, file=sys.stderr)
   ```

3. **Document in this file:**
   - Add to "Current Deprecations" section
   - Specify removal version
   - Provide migration path

### Testing Deprecation Warnings

Ensure warnings are tested:

```python
def test_deprecated_feature_warning(capsys):
    """Test that deprecation warning is shown."""
    parser = UPFParser()
    prompt = parser.parse_file("v2_nested_plugins.yaml")

    captured = capsys.readouterr()
    assert "DEPRECATION WARNING" in captured.err
    assert "plugins.mcp_servers" in captured.err
```

## Best Practices

### For Users

1. **Act Early**: Migrate as soon as you see warnings
2. **Test After Migration**: Validate and test migrated files
3. **Update Documentation**: Update your team's docs with new structure
4. **Use Version Control**: Commit v3.0 files separately for easy rollback

### For Contributors

1. **Use Centralized System**: Always use `DeprecationWarnings` class
2. **Consistent Messaging**: Follow existing warning format
3. **Document Thoroughly**: Update this file when adding warnings
4. **Test Warnings**: Add tests for deprecation warning behavior
5. **Provide Migration Path**: Always offer clear migration instructions

## FAQ

### Q: Will v2.1 files stop working immediately?

**A:** No. v2.1 files continue to work in v3.0.0 with deprecation warnings. They will be removed in v4.0.0.

### Q: Can I use both structures in the same file?

**A:** Yes, but top-level fields take precedence. If you have both:
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

### Q: Can I contribute to the deprecation system?

**A:** Yes! We welcome contributions. See [CONTRIBUTING.md](../.github/CONTRIBUTING.md) for guidelines.

## Resources

- [V3 Migration Guide](./V3_MIGRATION_GUIDE.md) - Complete migration instructions
- [User Guide](https://flamingquaks.github.io/promptrek/user-guide.html) - General documentation
- [GitHub Issues](https://github.com/flamingquaks/promptrek/issues) - Report problems
- [Discussions](https://github.com/flamingquaks/promptrek/discussions) - Ask questions

## Changelog

- **2024-10-16**: Initial documentation of centralized warning system
- **2024-10-16**: Documented v3.0 nested plugins deprecation

---

**Note:** This system ensures smooth transitions between versions while maintaining backward compatibility and providing clear migration paths.
