# promptrek sync

Sync editor-specific files back to PrompTrek configuration.

## Synopsis

```bash
promptrek sync [OPTIONS]
```

## Description

The `sync` command allows you to reverse the generation process by reading editor-specific prompt files and updating or creating a PrompTrek configuration from them. This is useful when you've made changes directly in an editor's native format and want to preserve those changes in your universal PrompTrek file.

Sync supports bidirectional workflows, allowing you to maintain your prompts in either PrompTrek format or editor-native format.

## Options

**`-s, --source-dir PATH`**
: Directory containing editor files to sync from (default: current directory `.`)

**`-e, --editor EDITOR`** (required)
: Editor type to sync from (e.g., `continue`, `cursor`, `claude`)

**`-o, --output PATH`**
: Output PrompTrek file (defaults to `project.promptrek.yaml`)

**`--dry-run`**
: Show what would be updated without making changes

**`-f, --force`**
: Overwrite existing files without confirmation

## Examples

### Basic Sync

Sync from Continue editor files:

```bash
promptrek sync --editor continue
```

This reads `.continue/` directory and updates `project.promptrek.yaml`.

### Sync from Specific Directory

Sync from a custom location:

```bash
promptrek sync --editor continue --source-dir ~/my-project
```

### Custom Output File

Specify a different output file:

```bash
promptrek sync --editor continue --output custom-config.promptrek.yaml
```

### Dry Run Mode

Preview changes without modifying files:

```bash
promptrek sync --editor continue --dry-run
```

**Output**:
```
🔍 Dry run mode - would write to: project.promptrek.yaml
📄 Preview of configuration that would be written:
  Title: Continue AI Assistant
  Description: AI assistant configuration
  Content length: 1234 characters
  Documents: 2 files
```

### Force Overwrite

Sync without confirmation prompts:

```bash
promptrek sync --editor continue --force
```

## Supported Editors

Not all editors support bidirectional sync. Editors with sync support:

### Continue Extension

**Sync capability**: Full support

**Files read**:
- `.continue/config.json` - Main configuration
- `.continue/prompts/*.md` - Slash command prompts
- `.continue/rules/*.md` - Rule files

**Example**:
```bash
promptrek sync --editor continue
```

### Cursor IDE

**Sync capability**: Full support

**Files read**:
- `.cursorrules` - Main rules file

**Example**:
```bash
promptrek sync --editor cursor
```

### Claude Code

**Sync capability**: Full support

**Files read**:
- `.claude/prompts/*.md` - Prompt files
- `.claude/config.json` - Configuration

**Example**:
```bash
promptrek sync --editor claude
```

### Other Editors

Editors without sync support will show an error:
```
Error: Editor 'copilot' does not support syncing from files
```

## Sync Behavior

### New PrompTrek File

If no PrompTrek file exists, sync creates a new one:

```bash
$ promptrek sync --editor continue
✅ Synced continue configuration to: project.promptrek.yaml
```

Creates a v3 schema file with content from editor files.

### Existing PrompTrek File

If `project.promptrek.yaml` exists, you'll be prompted:

```bash
$ promptrek sync --editor continue
File project.promptrek.yaml exists. Update it? [y/N]:
```

**Options**:
- Press `y` to update (merges changes)
- Press `n` to cancel
- Use `--force` to skip prompt

### Merging Strategy

When updating an existing file:

1. **Preserve metadata**: Keeps your custom metadata (title, description, author, etc.)
2. **Update content**: Replaces content with editor file content
3. **Merge documents**: Updates documents from editor files
4. **Preserve variables**: Restores variable references where possible
5. **Keep plugins**: Preserves plugin configurations

## Variable Restoration

Sync automatically restores variable references when merging:

**Before sync** (in editor file):
```markdown
# My App v2.0.0

Author: john@example.com
Environment: production
Generated on: 2024-01-15
```

**After sync** (in PrompTrek file):
```markdown
# {{PROJECT_NAME}} v{{VERSION}}

Author: {{AUTHOR_EMAIL}}
Environment: {{ENVIRONMENT}}
Generated on: {{CURRENT_DATE}}
```

This preserves your variable-driven configuration.

## Schema Handling

### Schema Version Compatibility

Sync creates files in the same schema version as your existing PrompTrek file:

- **V3 existing** → V3 output
- **V2 existing** → V2 output
- **V1 existing** → V1 output (if applicable)
- **No existing** → V3 output (default)

### Cross-Schema Syncing

If editor format doesn't match existing schema:

```
⚠️  Existing file is V2 schema, parsed files are V3. Replacing with V3 schema.
```

The file is replaced with the new schema version.

## Workflow Examples

### Making Changes in Editor

1. Edit files directly in your editor:
```bash
# Edit Continue prompts
vim .continue/prompts/explain-code.md

# Edit Cursor rules
vim .cursorrules
```

2. Sync changes back to PrompTrek:
```bash
promptrek sync --editor continue
# or
promptrek sync --editor cursor
```

3. Validate the synced configuration:
```bash
promptrek validate project.promptrek.yaml
```

4. Generate for other editors:
```bash
promptrek generate --all
```

### Switching Between Editors

If you're switching primary editors:

```bash
# 1. Sync from old editor
promptrek sync --editor cursor

# 2. Validate
promptrek validate project.promptrek.yaml

# 3. Generate for new editor
promptrek generate --editor continue
```

### Team Collaboration

When team members use different editors:

```bash
# Team member using Continue syncs their changes
promptrek sync --editor continue

# Commit PrompTrek file
git add project.promptrek.yaml
git commit -m "Update: sync from Continue editor changes"

# Other team members pull and generate for their editor
git pull
promptrek generate --editor claude
```

## .gitignore Configuration

After syncing, PrompTrek automatically updates `.gitignore`:

```bash
$ promptrek sync --editor continue
✅ Synced continue configuration to: project.promptrek.yaml
📝 Added editor file patterns to .gitignore
```

This ensures generated editor files aren't committed to version control.

## Common Scenarios

### Recovering from Manual Edits

If you edited editor files instead of PrompTrek:

```bash
# Sync changes back
promptrek sync --editor continue --dry-run

# Review changes
# If good, apply
promptrek sync --editor continue

# Validate
promptrek validate project.promptrek.yaml
```

### Importing Existing Editor Configuration

If you have existing editor files but no PrompTrek config:

```bash
# Create PrompTrek file from editor files
promptrek sync --editor continue

# Now you have a universal configuration
ls project.promptrek.yaml

# Generate for other editors
promptrek generate --all
```

### Periodic Sync

Set up a workflow to periodically sync editor changes:

```bash
#!/bin/bash
# sync-and-update.sh

# Sync from Continue
promptrek sync --editor continue --force

# Validate
if promptrek validate project.promptrek.yaml; then
    # Generate for all other editors
    promptrek generate --all

    # Commit changes
    git add project.promptrek.yaml
    git commit -m "chore: sync from Continue editor updates"
fi
```

## Error Handling

### Editor Not Supported

```
Error: Editor 'copilot' does not support syncing from files
```

**Solution**: Only sync from editors with bidirectional support (continue, cursor, claude).

### Files Not Found

```
Error: No editor files found in directory '.'
```

**Solution**: Ensure you're in the correct directory with editor files:
```bash
# Check for editor files
ls -la .continue/ .cursorrules .claude/

# Specify correct directory
promptrek sync --editor continue --source-dir ~/my-project
```

### Parsing Errors

```
Error: Failed to parse continue files: Invalid JSON in .continue/config.json
```

**Solution**: Fix syntax errors in editor files:
```bash
# Validate JSON files
jsonlint .continue/config.json

# Fix errors
vim .continue/config.json

# Try sync again
promptrek sync --editor continue
```

## Tips and Best Practices

!!! tip "Always Dry Run First"
    Use `--dry-run` to preview changes before applying:
    ```bash
    promptrek sync --editor continue --dry-run
    ```

!!! tip "Validate After Sync"
    Always validate the synced configuration:
    ```bash
    promptrek sync --editor continue
    promptrek validate project.promptrek.yaml
    ```

!!! tip "Commit PrompTrek File"
    After syncing, commit the PrompTrek file (not editor files):
    ```bash
    git add project.promptrek.yaml
    git commit -m "sync: update from editor changes"
    ```

!!! warning "Variable Loss Risk"
    Manual edits in editor files may lose variable references. PrompTrek tries to restore them, but complex variables might need manual review.

!!! note "One-Way Editors"
    Some editors (like Copilot) don't support sync. You must maintain configuration in PrompTrek and generate only.

## Advanced Usage

### Custom Sync Workflows

```bash
# Sync from multiple editors (run separately)
promptrek sync --editor continue -o from-continue.yaml
promptrek sync --editor cursor -o from-cursor.yaml

# Manually merge the best parts
vim project.promptrek.yaml
```

### Automated Sync

```bash
# Watch for changes and auto-sync
while inotifywait -e modify .continue/prompts/*.md; do
    promptrek sync --editor continue --force
    promptrek validate project.promptrek.yaml
done
```

## Troubleshooting

### Sync Overwrites Changes

**Problem**: Sync overwrites custom changes in PrompTrek file

**Solution**: Use version control:
```bash
# Before sync, commit current state
git add project.promptrek.yaml
git commit -m "checkpoint before sync"

# Sync
promptrek sync --editor continue

# Review changes
git diff project.promptrek.yaml

# Revert if needed
git checkout project.promptrek.yaml
```

### Variables Not Restored

**Problem**: Variable references lost during sync

**Solution**: Manually restore variables:
```bash
# Review original file
git diff project.promptrek.yaml

# Manually fix variable references
vim project.promptrek.yaml

# Or report as a bug if pattern should be supported
```

## See Also

- [generate command](generate.md) - Generate editor configurations
- [validate command](validate.md) - Validate synced configuration
- [UPF Specification](../../user-guide/upf-specification.md) - Schema documentation
- [Sync Workflows](../../user-guide/workflows/sync.md) - Detailed sync workflows
