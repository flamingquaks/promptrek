# promptrek migrate

Migrate PrompTrek configuration files between schema versions.

## Synopsis

```bash
promptrek migrate INPUT_FILE [OPTIONS]
```

## Description

The `migrate` command converts PrompTrek configuration files from older schema versions to newer ones. This is essential when upgrading PrompTrek or when you want to take advantage of new features in later schema versions.

The migration process preserves your configuration while converting it to the new schema format.

## Options

**`INPUT_FILE`** (required)
: Path to the `.promptrek.yaml` file to migrate

**`-o, --output PATH`**
: Output file path (default: `<input>.v3.promptrek.yaml`)

**`-f, --force`**
: Overwrite output file if it exists

## Schema Versions

PrompTrek supports these schema versions:

### v3.0.0 (Current)

**Features**:
- Markdown-first content
- Top-level plugin fields (`mcp_servers`, `commands`, `agents`, `hooks`)
- Simplified structure
- Best for new projects

### v2.1.0 (Legacy)

**Features**:
- Markdown-first content
- Nested plugin structure (`plugins.mcp_servers`, `plugins.commands`, etc.)
- Multi-document support

### v2.0.0 (Legacy)

**Features**:
- Markdown-first content
- No plugin support
- Multi-document support

### v1.0.0 (Deprecated)

**Features**:
- Structured fields (`instructions`, `context`, `examples`)
- Target editor specification
- Legacy format

## Migration Paths

```
v1.0.0 ───────────────────────► v3.0.0 (recommended)
  │
  └──► v2.0.0 ──► v2.1.0 ──► v3.0.0

Current: v2.1.0 ──────────────► v3.0.0
Current: v2.0.0 ──────────────► v3.0.0
```

All migration paths ultimately lead to v3.0.0 (current recommended version).

## Examples

### Basic Migration

Migrate from any older version to v3:

```bash
promptrek migrate project.promptrek.yaml
```

This creates `project.v3.promptrek.yaml` with the migrated content.

### Custom Output File

Specify a custom output file name:

```bash
promptrek migrate old-config.yaml --output new-config.yaml
```

### Force Overwrite

Overwrite existing output file without prompting:

```bash
promptrek migrate project.promptrek.yaml --force
```

### Verbose Migration

See detailed migration information:

```bash
promptrek --verbose migrate project.promptrek.yaml
```

**Output**:
```
ℹ️  Migrating from v1.0.0 to v3.0.0...
   Converting structured fields to markdown...
   Note: v3 format works with all editors (removed targets: copilot, cursor)
✅ Migrated project.promptrek.yaml → project.v3.promptrek.yaml
   Schema version: 1.0.0 → 3.0.0
   Content length: 1543 characters
```

## Migration Details

### v1 → v3 Migration

Converts structured v1 format to markdown-first v3:

**Before (v1)**:
```yaml
schema_version: "1.0.0"
metadata:
  title: "My Project"
  description: "Project description"

targets:
  - copilot
  - cursor
  - continue

context:
  project_type: "web_application"
  technologies:
    - python
    - react

instructions:
  general:
    - "Write clean code"
    - "Follow conventions"
  code_style:
    - "Use meaningful names"
    - "Add comments"

examples:
  function: |
    ```python
    def hello():
        print("Hello")
    ```
```

**After (v3)**:
```yaml
schema_version: "3.0.0"
metadata:
  title: "My Project"
  description: "Project description"

content: |
  # My Project

  Project description

  ## Project Details
  **Project Type:** web_application
  **Technologies:** python, react

  ## Development Guidelines

  ### General Principles
  - Write clean code
  - Follow conventions

  ### Code Style Requirements
  - Use meaningful names
  - Add comments

  ## Code Examples

  ### Function
  ```python
  def hello():
      print("Hello")
  ```

  ## AI Assistant Instructions

  When working on this project:
  - Follow the established patterns and conventions shown above
  - Maintain consistency with the existing codebase
  - Consider the project context and requirements in all suggestions
  - Prioritize code quality, maintainability, and best practices
```

**Changes**:
- Converts structured fields to markdown sections
- Removes `targets` (v3 works with all editors)
- Preserves all content and instructions
- Converts `context` to markdown format
- Converts `instructions` to bullet lists
- Preserves `examples` as code blocks

### v2.0 → v3 Migration

Upgrades v2.0 to v3.0:

**Changes**:
- Updates `schema_version` from "2.0.0" to "3.0.0"
- Preserves markdown `content`
- Preserves `documents`
- Preserves `variables`
- No plugin conversion (v2.0 has no plugins)

### v2.1 → v3 Migration

Converts nested plugins to top-level:

**Before (v2.1)**:
```yaml
schema_version: "2.1.0"
plugins:
  mcp_servers:
    - name: "filesystem"
      command: "npx"
      args: ["-y", "@modelcontextprotocol/server-filesystem"]
  commands:
    - name: "/test"
      prompt: "Run tests"
```

**After (v3)**:
```yaml
schema_version: "3.0.0"
mcp_servers:
  - name: "filesystem"
    command: "npx"
    args: ["-y", "@modelcontextprotocol/server-filesystem"]
commands:
  - name: "/test"
    prompt: "Run tests"
```

**Changes**:
- Promotes `plugins.mcp_servers` to top-level `mcp_servers`
- Promotes `plugins.commands` to top-level `commands`
- Promotes `plugins.agents` to top-level `agents`
- Promotes `plugins.hooks` to top-level `hooks`
- Updates `schema_version`

## Workflow Examples

### Upgrade Existing Project

1. **Backup current file**:
```bash
cp project.promptrek.yaml project.promptrek.yaml.backup
```

2. **Migrate to v3**:
```bash
promptrek migrate project.promptrek.yaml
```

3. **Validate migrated file**:
```bash
promptrek validate project.v3.promptrek.yaml
```

4. **Test generation**:
```bash
promptrek generate project.v3.promptrek.yaml --all --dry-run
```

5. **Replace old file** (if everything works):
```bash
mv project.v3.promptrek.yaml project.promptrek.yaml
```

6. **Regenerate editor configs**:
```bash
promptrek generate --all
```

### Batch Migration

Migrate multiple files:

```bash
# Migrate all v1 files
for file in *.promptrek.yaml; do
    promptrek migrate "$file" --force
done

# Validate all migrated files
for file in *.v3.promptrek.yaml; do
    promptrek validate "$file"
done
```

### Testing Migration

Test migration without committing:

```bash
# Migrate to temp file
promptrek migrate project.promptrek.yaml -o /tmp/test.yaml

# Validate
promptrek validate /tmp/test.yaml

# Test generation
promptrek generate /tmp/test.yaml --editor claude --dry-run

# If good, apply to real file
promptrek migrate project.promptrek.yaml --force
mv project.v3.promptrek.yaml project.promptrek.yaml
```

## Migration Preservation

The migration process preserves:

- **Metadata**: Title, description, version, author, dates, tags
- **Content**: All instructional content (converted to markdown if needed)
- **Variables**: All variable definitions and references
- **Documents**: Multi-document configurations (v2/v3)
- **Plugins**: MCP servers, commands, agents, hooks (v2.1/v3)
- **Examples**: Code examples and demonstrations

The migration process removes or converts:

- **Targets**: Removed (v3 works with all editors)
- **Structure**: Converted to markdown (v1 → v3)
- **Nested plugins**: Promoted to top-level (v2.1 → v3)

## Post-Migration Steps

After migration:

1. **Validate the migrated file**:
```bash
promptrek validate project.v3.promptrek.yaml
```

2. **Review changes**:
```bash
# Compare original and migrated
diff project.promptrek.yaml project.v3.promptrek.yaml
```

3. **Test generation**:
```bash
promptrek generate project.v3.promptrek.yaml --all --dry-run
```

4. **Update references** (if using custom file names):
```bash
# Update scripts, documentation, etc.
grep -r "project.promptrek.yaml" .
```

5. **Regenerate editor configs**:
```bash
promptrek generate --all
```

## Error Handling

### File Already at Latest Version

```
ℹ️  project.promptrek.yaml is already v3.x format, no migration needed
```

**Action**: No migration needed, file is current.

### Output File Exists

```
Error: Output file project.v3.promptrek.yaml already exists. Use --force to overwrite.
```

**Solution**: Use `--force` or choose different output name:
```bash
promptrek migrate project.promptrek.yaml --force
# or
promptrek migrate project.promptrek.yaml -o custom-name.yaml
```

### Invalid Source File

```
Error: Failed to parse project.promptrek.yaml: Invalid YAML syntax
```

**Solution**: Fix syntax errors before migration:
```bash
# Validate YAML syntax
yamllint project.promptrek.yaml

# Fix errors
vim project.promptrek.yaml

# Try migration again
promptrek migrate project.promptrek.yaml
```

## Tips and Best Practices

!!! tip "Always Backup"
    Create a backup before migration:
    ```bash
    cp project.promptrek.yaml project.promptrek.yaml.backup
    promptrek migrate project.promptrek.yaml
    ```

!!! tip "Validate After Migration"
    Always validate the migrated file:
    ```bash
    promptrek migrate old.yaml
    promptrek validate old.v3.promptrek.yaml
    ```

!!! tip "Test Before Replacing"
    Test the migrated file before replacing the original:
    ```bash
    promptrek migrate project.promptrek.yaml
    promptrek generate project.v3.promptrek.yaml --all --dry-run
    # If good:
    mv project.v3.promptrek.yaml project.promptrek.yaml
    ```

!!! warning "Review Complex Migrations"
    For complex v1 → v3 migrations, manually review the generated markdown to ensure instructions are properly formatted.

!!! note "Targets Removed"
    v3 schema doesn't have `targets` field. Migrated files work with all editors automatically.

## When to Migrate

### Required Migration

You must migrate if:
- Using PrompTrek v3.0+ with v1 or v2 files
- Need new v3 features (top-level plugins)
- Receiving deprecation warnings

### Optional Migration

Consider migrating if:
- Want to standardize on latest schema
- Need top-level plugin fields
- Want simpler configuration structure

### Don't Migrate Yet

Keep current version if:
- Everything works fine
- No need for v3 features
- Team is on older PrompTrek version

## Troubleshooting

### Lost Formatting

**Problem**: Migration changes formatting or structure

**Solution**: Review and manually adjust:
```bash
# Compare before and after
diff project.promptrek.yaml project.v3.promptrek.yaml

# Edit migrated file
vim project.v3.promptrek.yaml
```

### Broken Variables

**Problem**: Variable references broken after migration

**Solution**: Check variable section is preserved:
```yaml
variables:
  PROJECT_NAME: "My Project"  # Should be preserved
  VERSION: "1.0.0"            # Should be preserved
```

### Generation Fails

**Problem**: Generate fails after migration

**Solution**:
```bash
# Validate migrated file
promptrek validate project.v3.promptrek.yaml

# Fix any errors
vim project.v3.promptrek.yaml

# Test generation
promptrek generate project.v3.promptrek.yaml --editor claude --dry-run
```

## See Also

- [UPF Specification](../../user-guide/upf-specification.md) - Schema version details
- [validate command](validate.md) - Validate migrated files
- [generate command](generate.md) - Generate from migrated files
- [Migration Guide](../../MIGRATION_GUIDE.md) - Detailed migration guide
