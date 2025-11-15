# promptrek generate

Generate editor-specific prompts from universal prompt files.

## Synopsis

```bash
promptrek generate [FILES]... [OPTIONS]
```

## Description

The `generate` command converts your universal PrompTrek configuration into editor-specific prompt files. It reads `.promptrek.yaml` files and creates native configuration files for AI editors like Claude, Cursor, Continue, and others.

This is the core command you'll use after setting up your PrompTrek configuration to deploy it across different AI coding assistants.

## Options

### File Selection

**`FILES...`**
: One or more `.promptrek.yaml` files to process (optional if using `--directory`)

**`-d, --directory PATH`**
: Directory to search for `.promptrek.yaml` files

**`-r, --recursive`**
: Search recursively in directories

### Editor Selection

**`-e, --editor EDITOR`**
: Target editor for generation. Supported editors:
  - `claude` - Claude Code editor
  - `continue` - Continue VSCode extension
  - `cursor` - Cursor IDE
  - `cline` - Cline extension
  - `windsurf` - Windsurf IDE
  - `amazon-q` - Amazon Q Developer
  - `kiro` - Kiro editor

**`--all`**
: Generate for all supported editors (project file adapters only)

### Output Options

**`-o, --output PATH`**
: Output directory (default: current directory)

**`--dry-run`**
: Show what would be generated without creating files

### Variable Options

**`-V, --var KEY=VALUE`**
: Override variables (can be used multiple times)

**`--headless`**
: Generate with headless agent instructions for autonomous operation

## Examples

### Basic Generation

Generate for a specific editor:

```bash
# Generate for Claude
promptrek generate --editor claude

# Generate for Cursor
promptrek generate --editor cursor

# Generate for Continue
promptrek generate --editor continue
```

### Generate for All Editors

Create configurations for all supported editors:

```bash
promptrek generate --all
```

This creates editor-specific files:
- `.claude/prompts/*.md` (Claude)
- `.cursorrules` (Cursor)
- `.continue/config.json` (Continue)
- `.cline/prompts/*.md` (Cline)
- `.windsurf/rules/*.md` (Windsurf)
- And more...

### Specify Input Files

Process specific PrompTrek files:

```bash
# Single file
promptrek generate project.promptrek.yaml --editor claude

# Multiple files
promptrek generate backend.yaml frontend.yaml --editor claude

# All files in directory
promptrek generate --directory ./configs --editor claude

# Recursive search
promptrek generate --directory ./configs --recursive --all
```

### Custom Output Directory

Specify where generated files should be created:

```bash
promptrek generate --editor claude --output ./ai-configs

promptrek generate --all --output ~/my-project/.ai
```

### Dry Run Mode

Preview what would be generated without creating files:

```bash
# Preview for one editor
promptrek generate --editor claude --dry-run

# Preview for all editors
promptrek generate --all --dry-run
```

Output shows:
```
🔍 Dry run mode - showing what would be generated:
Generating for claude:
  Would create: .claude/prompts/project.md
  Would create: .claude/config.json
```

### Variable Overrides

Override variables defined in your PrompTrek file:

```bash
# Single variable
promptrek generate --editor claude -V VERSION=2.0.0

# Multiple variables
promptrek generate --editor claude \
  -V PROJECT_NAME="My App" \
  -V ENVIRONMENT=production \
  -V VERSION=2.0.0

# Using with generation
promptrek generate --all \
  -V AUTHOR_EMAIL=dev@example.com \
  -V YEAR=2024
```

### Headless Mode

Generate with headless agent instructions for autonomous AI operation:

```bash
promptrek generate --editor claude --headless
```

Headless mode adds special instructions for AI agents to:
- Operate autonomously without user interaction
- Follow strict guidelines for decision-making
- Provide detailed logs and reasoning
- Handle edge cases gracefully

## Generated Files by Editor

### Claude Code

```
.claude/
├── prompts/
│   └── project.md          # Main project prompt
└── config.json             # Claude configuration
```

### Cursor IDE

```
.cursorrules                # Single rules file with all content
```

### Continue Extension

```
.continue/
├── config.json             # Main configuration
├── prompts/
│   └── *.md                # Slash command prompts
└── rules/
    └── *.md                # Rule files
```

### Cline Extension

```
.cline/
└── prompts/
    └── *.md                # Cline prompts
```

### Windsurf IDE

```
.windsurf/
└── rules/
    └── *.md                # Windsurf rules
```

## Variable Substitution

PrompTrek supports three types of variables, applied in this order of precedence:

1. **Built-in variables** (lowest priority)
2. **Local file variables** (`.promptrek/variables.promptrek.yaml`)
3. **Prompt file variables** (`variables:` section)
4. **CLI overrides** (highest priority, `-V` flag)

### Built-in Variables

Always available:

- `{{CURRENT_DATE}}` - Current date (YYYY-MM-DD)
- `{{CURRENT_YEAR}}` - Current year
- `{{CURRENT_MONTH}}` - Current month name
- `{{CURRENT_TIME}}` - Current time (HH:MM:SS)
- `{{CURRENT_DATETIME}}` - Current date and time

### Variable Examples

In your `project.promptrek.yaml`:

```yaml
variables:
  PROJECT_NAME: "MyApp"
  VERSION: "1.0.0"
  ENVIRONMENT: "development"

content: |
  # {{PROJECT_NAME}} v{{VERSION}}

  Current environment: {{ENVIRONMENT}}
  Generated on: {{CURRENT_DATE}}
```

Override at generation time:

```bash
promptrek generate --editor claude \
  -V VERSION=2.0.0 \
  -V ENVIRONMENT=production
```

Result:
```markdown
# MyApp v2.0.0

Current environment: production
Generated on: 2024-01-15
```

## Multiple File Generation

### Merging Multiple Files

When processing multiple PrompTrek files:

```bash
promptrek generate file1.yaml file2.yaml file3.yaml --editor claude
```

**Behavior**:
- For adapters supporting merging (like Claude, Continue): Combines all files into a unified configuration
- For adapters without merge support: Uses the last file only with a warning

### Use Cases

**Monorepo structure**:
```bash
# Generate from separate backend and frontend configs
promptrek generate \
  backend/backend.promptrek.yaml \
  frontend/frontend.promptrek.yaml \
  --editor claude
```

**Layered configuration**:
```bash
# Combine base config with environment-specific overrides
promptrek generate \
  base.promptrek.yaml \
  production.promptrek.yaml \
  --editor continue
```

## Metadata and Refresh

Generation creates metadata for the `refresh` command:

```
.promptrek/
└── last-generation.yaml    # Metadata for refresh command
```

This enables:

```bash
# Later, regenerate with updated dynamic variables
promptrek refresh

# Or refresh specific editor
promptrek refresh --editor claude
```

See [`promptrek refresh`](../index.md#refresh) for details.

## Editor Support Levels

### Project Configuration Files

Editors with full PrompTrek support (generate files):

- **claude** - Project-level prompts and configuration
- **continue** - Full config with MCP servers, prompts, rules
- **cursor** - .cursorrules file
- **cline** - Prompt files
- **windsurf** - Rule files
- **amazon-q** - Project configuration

### Global Configuration Only

Editors requiring global/manual setup (informational only):

- **copilot** - Configure through GitHub settings
- **jetbrains** - Configure through IDE preferences

When specifying these editors, PrompTrek shows configuration instructions instead of generating files.

## Common Workflows

### Initial Generation

After creating a PrompTrek configuration:

```bash
# 1. Validate first
promptrek validate project.promptrek.yaml

# 2. Generate for all editors
promptrek generate --all

# 3. Verify created files
ls -la .claude/ .cursorrules .continue/

# 4. Commit PrompTrek file (not generated files)
git add project.promptrek.yaml
git commit -m "feat: add PrompTrek configuration"
```

### Update and Regenerate

After modifying your configuration:

```bash
# Edit configuration
vim project.promptrek.yaml

# Validate changes
promptrek validate project.promptrek.yaml

# Regenerate for specific editor
promptrek generate --editor claude

# Or regenerate for all
promptrek generate --all
```

### Environment-Specific Generation

Generate different configurations for different environments:

```bash
# Development
promptrek generate --editor claude -V ENVIRONMENT=development

# Production
promptrek generate --editor claude -V ENVIRONMENT=production

# Staging
promptrek generate --editor claude -V ENVIRONMENT=staging
```

## Error Handling

### Common Errors

**No files specified**:
```bash
$ promptrek generate --editor claude
Error: No UPF files found. Specify files directly or use --directory option.
```

**Solution**: Specify files or use `--directory`:
```bash
promptrek generate project.promptrek.yaml --editor claude
# or
promptrek generate --directory . --editor claude
```

**Editor not specified**:
```bash
$ promptrek generate
Error: Must specify either --editor or --all
```

**Solution**: Add editor flag:
```bash
promptrek generate --editor claude --all
```

**Editor not available**:
```bash
$ promptrek generate --editor unknown
Error: Editor 'unknown' not available. Available editors: claude, continue, cursor, ...
```

**Solution**: Use `promptrek list-editors` to see supported editors.

### Validation Errors

If your PrompTrek file has errors:

```bash
$ promptrek generate --editor claude
❌ Error processing project.promptrek.yaml: Validation failed: metadata.version is required
```

**Solution**: Fix errors identified by validation:
```bash
# First validate to see all errors
promptrek validate project.promptrek.yaml

# Fix issues
vim project.promptrek.yaml

# Try generation again
promptrek generate --editor claude
```

## Performance Considerations

### Large Configurations

For large PrompTrek files or many files:

```bash
# Use verbose mode to see progress
promptrek --verbose generate --directory ./configs --recursive --all

# Process incrementally for testing
promptrek generate file1.yaml --editor claude --dry-run
promptrek generate file1.yaml --editor claude
```

### Caching

PrompTrek caches:
- Parsed YAML files
- Template compilations
- Variable evaluations

Cache is stored in `.promptrek/cache/` and cleared on schema changes.

## Tips and Best Practices

!!! tip "Always Validate First"
    Run `promptrek validate` before `promptrek generate` to catch errors early:
    ```bash
    promptrek validate project.promptrek.yaml && promptrek generate --all
    ```

!!! tip "Use Dry Run for Testing"
    Test generation with `--dry-run` before creating actual files:
    ```bash
    promptrek generate --all --dry-run
    ```

!!! tip "Version Control"
    Only commit the PrompTrek file, not generated files. Use `.gitignore` patterns:
    ```gitignore
    .claude/
    .cursorrules
    .continue/
    .cline/
    .windsurf/
    ```

!!! warning "Headless Mode"
    Only use `--headless` when generating for autonomous AI agents. It changes the behavior and instructions significantly.

!!! note "Multiple Files"
    When using multiple PrompTrek files, ensure they're compatible and don't have conflicting configurations.

## See Also

- [init command](init.md) - Initialize PrompTrek configuration
- [validate command](validate.md) - Validate before generating
- [sync command](sync.md) - Sync editor files back to PrompTrek
- [refresh command](../index.md#refresh) - Regenerate with updated variables
- [Adapters Documentation](../../user-guide/adapters/index.md) - Editor adapter capabilities
