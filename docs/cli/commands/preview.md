# promptrek preview

Preview what would be generated without creating files.

## Synopsis

```bash
promptrek preview FILE [OPTIONS]
```

## Description

The `preview` command shows you exactly what PrompTrek would generate for a specific editor without actually creating any files. This is useful for:

- Verifying configuration before generation
- Debugging variable substitution
- Understanding editor-specific output
- Testing changes safely

## Options

**`FILE`** (required)
: Path to the `.promptrek.yaml` file to preview

**`-e, --editor EDITOR`** (required)
: Target editor to preview for

**`-V, --var KEY=VALUE`**
: Override variables (can be used multiple times)

**`-v, --verbose`**
: Show detailed preview information

## Examples

### Basic Preview

Preview for Claude:

```bash
promptrek preview project.promptrek.yaml --editor claude
```

Output:
```
================================================================================
Preview for: claude
Source file: project.promptrek.yaml
================================================================================

Would create 2 file(s):
  📄 .claude/prompts/project.md
  📄 .claude/config.json

================================================================================
Preview complete. No files were created.
Run 'promptrek generate' to create files.
================================================================================
```

### Preview for Different Editors

```bash
# Preview for Cursor
promptrek preview project.promptrek.yaml --editor cursor

# Preview for Continue
promptrek preview project.promptrek.yaml --editor continue

# Preview for all editors (run separately)
for editor in claude cursor continue; do
  promptrek preview project.promptrek.yaml --editor $editor
done
```

### Preview with Variable Overrides

Test variable substitution:

```bash
promptrek preview project.promptrek.yaml \
  --editor claude \
  -V ENVIRONMENT=production \
  -V VERSION=2.0.0
```

### Verbose Preview

See detailed information including file contents:

```bash
promptrek preview project.promptrek.yaml --editor claude --verbose
```

Output includes:
- File paths
- File contents (truncated)
- Variable substitutions
- Metadata information

## Use Cases

### Before First Generation

Preview before generating for the first time:

```bash
# 1. Validate
promptrek validate project.promptrek.yaml

# 2. Preview
promptrek preview project.promptrek.yaml --editor claude

# 3. If looks good, generate
promptrek generate project.promptrek.yaml --editor claude
```

### Testing Configuration Changes

After modifying configuration:

```bash
# Edit config
vim project.promptrek.yaml

# Preview changes
promptrek preview project.promptrek.yaml --editor claude

# Check diff with existing files
promptrek preview project.promptrek.yaml --editor claude > /tmp/preview.txt
diff /tmp/preview.txt .claude/prompts/project.md
```

### Debugging Variables

Verify variable substitution:

```bash
# Check default variables
promptrek preview project.promptrek.yaml --editor claude

# Test with overrides
promptrek preview project.promptrek.yaml \
  --editor claude \
  -V DEBUG=true \
  -V ENVIRONMENT=staging
```

### Comparing Editors

See how different editors receive the same configuration:

```bash
# Compare Claude and Cursor output
promptrek preview project.promptrek.yaml --editor claude > claude-preview.txt
promptrek preview project.promptrek.yaml --editor cursor > cursor-preview.txt
diff claude-preview.txt cursor-preview.txt
```

## Output Format

### Standard Output

```
================================================================================
Preview for: <editor>
Source file: <file>
================================================================================

<Generated content preview>

Would create N file(s):
  📄 <file-path-1>
  📄 <file-path-2>
  ...

================================================================================
Preview complete. No files were created.
Run 'promptrek generate' to create files.
================================================================================
```

### Verbose Output

Includes:
- Parsed configuration details
- Variable resolution
- File contents (truncated if large)
- Metadata and frontmatter
- Adapter-specific transformations

## Editor-Specific Previews

### Claude Code Preview

```bash
promptrek preview project.promptrek.yaml --editor claude
```

Shows:
- `.claude/prompts/*.md` files
- `.claude/config.json` if MCP servers configured

### Cursor Preview

```bash
promptrek preview project.promptrek.yaml --editor cursor
```

Shows:
- `.cursorrules` content
- `.cursor/rules/*.mdc` files if using multi-document

### Continue Preview

```bash
promptrek preview project.promptrek.yaml --editor continue
```

Shows:
- `.continue/config.json` merged content
- MCP server configurations
- Slash commands

## Common Workflows

### Safe Testing Workflow

```bash
# 1. Validate syntax
promptrek validate project.promptrek.yaml

# 2. Preview output
promptrek preview project.promptrek.yaml --editor claude

# 3. Review and approve

# 4. Generate (with dry-run first)
promptrek generate project.promptrek.yaml --editor claude --dry-run

# 5. Generate for real
promptrek generate project.promptrek.yaml --editor claude
```

### Variable Testing Workflow

```bash
# Test different variable values
for env in development staging production; do
  echo "=== Testing $env ==="
  promptrek preview project.promptrek.yaml \
    --editor claude \
    -V ENVIRONMENT=$env
done
```

### Multi-Editor Preview

```bash
# Preview for all editors
EDITORS="claude cursor continue cline windsurf"
for editor in $EDITORS; do
  echo "=== $editor ==="
  promptrek preview project.promptrek.yaml --editor $editor
done
```

## Differences from Generate

| Feature | Preview | Generate |
|---------|---------|----------|
| Creates files | ❌ No | ✅ Yes |
| Shows output | ✅ Yes | ⚠️ Optional |
| Validates config | ✅ Yes | ✅ Yes |
| Substitutes variables | ✅ Yes | ✅ Yes |
| Updates metadata | ❌ No | ✅ Yes |
| Safe to run | ✅ Always | ⚠️ Overwrites |

## Best Practices

!!! tip "Preview Before Generate"
    Always preview before generating, especially when:
    - Testing new configurations
    - Using variable overrides
    - Generating for a new editor

!!! tip "Use with Dry-Run"
    Combine with `generate --dry-run` for comprehensive testing:
    ```bash
    promptrek preview project.promptrek.yaml --editor claude
    promptrek generate project.promptrek.yaml --editor claude --dry-run
    ```

!!! warning "Large Files"
    Preview truncates very large output. Use `--verbose` to see more, or generate to files to see complete output.

!!! note "CI/CD Integration"
    Use preview in CI to verify configurations:
    ```bash
    # In CI pipeline
    promptrek preview project.promptrek.yaml --editor claude
    if [ $? -eq 0 ]; then
      echo "Preview successful"
    fi
    ```

## Error Handling

### File Not Found

```bash
$ promptrek preview missing.yaml --editor claude
❌ Error: File not found: missing.yaml
```

**Solution**: Check file path is correct

### Editor Not Specified

```bash
$ promptrek preview project.promptrek.yaml
❌ Error: Missing option '--editor'
```

**Solution**: Specify editor with `--editor`

### Invalid Editor

```bash
$ promptrek preview project.promptrek.yaml --editor unknown
❌ Error: Editor 'unknown' not available
Available editors: claude, cursor, continue, ...
```

**Solution**: Use `promptrek list-editors` to see available editors

### Validation Errors

```bash
$ promptrek preview broken.yaml --editor claude
❌ Failed to parse broken.yaml: Validation failed: metadata.title is required
```

**Solution**: Fix validation errors, then retry preview

## See Also

- [generate command](generate.md) - Generate files for real
- [validate command](validate.md) - Validate configuration
- [list-editors command](list-editors.md) - See available editors
- [Variables Documentation](../../user-guide/configuration/variables.md)
