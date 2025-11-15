# Basic Usage

This guide covers the fundamental usage patterns of PrompTrek.

## The PrompTrek Workflow

PrompTrek follows a simple three-step workflow:

```
Create/Edit → Validate → Generate
   .promptrek.yaml → ✓ → Editor Configs
```

## Step 1: Create a Configuration

### Using the Interactive Wizard

The easiest way to get started:

```bash
promptrek
```

This launches an interactive menu where you can:
- 🚀 Initialize new project
- ⚙️ Generate editor configurations
- 🔌 Configure plugins
- 🔄 Migrate schema versions
- 🔍 Validate configuration

### Using the CLI

Create a configuration file manually:

```bash
# Basic initialization
promptrek init --output my-project.promptrek.yaml

# Use a template
promptrek init --template react --output my-react-app.promptrek.yaml

# Available templates: basic, react, api
```

### Manual Creation

Create a `.promptrek.yaml` file with this minimal structure:

```yaml
schema_version: "3.1.0"

metadata:
  title: "My Project"
  description: "AI assistant for my project"

content: |
  # Project Instructions

  Write clean, well-documented code.

variables:
  PROJECT_NAME: "my-project"
```

## Step 2: Validate

Always validate your configuration before generating:

```bash
# Basic validation
promptrek validate my-project.promptrek.yaml

# Strict mode (warnings become errors)
promptrek validate my-project.promptrek.yaml --strict

# Verbose output
promptrek validate my-project.promptrek.yaml --verbose
```

### Understanding Validation Output

```bash
✓ Configuration is valid!
  Schema: v3.1.0
  Metadata: ✓
  Variables: 1 defined
  Documents: None
  Plugins: MCP Servers (1), Commands (0), Agents (0)
```

## Step 3: Generate

Generate editor-specific configurations:

```bash
# Generate for a specific editor
promptrek generate my-project.promptrek.yaml --editor copilot
promptrek generate my-project.promptrek.yaml --editor cursor

# Generate for all editors
promptrek generate my-project.promptrek.yaml --all

# Preview without writing files
promptrek generate my-project.promptrek.yaml --editor copilot --dry-run
```

### Generated Files

PrompTrek creates files in the appropriate locations:

| Editor | Files Created |
|--------|---------------|
| GitHub Copilot | `.github/copilot-instructions.md`<br>`.github/instructions/*.instructions.md` |
| Cursor | `.cursor/rules/*.mdc`<br>`AGENTS.md`<br>`.cursorignore` |
| Continue | `.continue/rules/*.md` |
| Claude Code | `.claude/CLAUDE.md`<br>`.claude/commands/*.md`<br>`.claude/agents/*.md` |
| Windsurf | `.windsurf/rules/*.md` |
| Cline | `.clinerules/*.md` |
| Kiro | `.kiro/steering/*.md`<br>`.kiro/specs/*.md` |
| Amazon Q | `.amazonq/rules/*.md`<br>`.amazonq/cli-agents/*.json` |
| JetBrains | `.assistant/rules/*.md` |

## Working with Variables

### Define Variables

Variables make your configurations reusable:

```yaml
variables:
  PROJECT_NAME: "my-app"
  AUTHOR: "Team Name"
  VERSION: "1.0.0"
```

### Use Variables

Reference variables in your content:

```yaml
content: |
  # {{{ PROJECT_NAME }}} - Version {{{ VERSION }}}

  Maintained by {{{ AUTHOR }}}
```

### Override Variables

Override variables at generation time:

```bash
promptrek generate my-project.promptrek.yaml --all \
  -V PROJECT_NAME="CustomApp" \
  -V VERSION="2.0.0"
```

## Working with Multiple Documents

Schema v3.1 supports multiple documents for path-specific instructions:

```yaml
schema_version: "3.1.0"

# Main content (always applied)
content: |
  # General Guidelines
  Write clean code.

# Additional documents (path-specific)
documents:
  - name: "typescript"
    content: |
      # TypeScript Guidelines
      Use strict mode.
    file_globs: "**/*.{ts,tsx}"

  - name: "testing"
    content: |
      # Testing Guidelines
      Aim for 80% coverage.
    file_globs: "**/*.test.{js,ts}"
```

## Preview Before Generating

Use the preview command to see what will be generated:

```bash
# Preview for a specific editor
promptrek preview my-project.promptrek.yaml --editor copilot

# Preview with variable overrides
promptrek preview my-project.promptrek.yaml --editor cursor \
  -V PROJECT_NAME="MyApp"
```

## Managing .gitignore

PrompTrek automatically manages `.gitignore` for generated files:

```bash
# Configure .gitignore (done automatically during init)
promptrek config-ignores

# Remove already-committed files from git
promptrek config-ignores --remove-cached

# Preview changes
promptrek config-ignores --dry-run
```

## Syncing from Editor Files

If you've edited files in your editor, sync them back:

```bash
# Sync from Cursor
promptrek sync --editor cursor --output my-project.promptrek.yaml

# Sync from GitHub Copilot
promptrek sync --editor copilot --output my-project.promptrek.yaml
```

## Common Patterns

### Single Editor Workflow

If you only use one editor:

```bash
promptrek init --output project.promptrek.yaml
promptrek generate project.promptrek.yaml --editor cursor
```

### Multi-Editor Team Workflow

For teams using different editors:

```bash
promptrek init --output project.promptrek.yaml
promptrek generate project.promptrek.yaml --all
# Add .github/copilot-instructions.md, .cursor/rules/, etc. to .gitignore
```

### Development Workflow with Pre-commit

Automate validation with pre-commit hooks:

```bash
# Set up hooks during init
promptrek init --output project.promptrek.yaml --setup-hooks

# Or install hooks later
promptrek install-hooks --activate
```

## Best Practices

1. **Always validate before generating**
   ```bash
   promptrek validate config.yaml && promptrek generate config.yaml --all
   ```

2. **Use templates as starting points**
   ```bash
   promptrek init --template react --output my-app.promptrek.yaml
   # Then customize my-app.promptrek.yaml
   ```

3. **Keep generated files out of version control**
   ```bash
   promptrek config-ignores  # Automatically configures .gitignore
   ```

4. **Use variables for reusability**
   ```yaml
   variables:
     FRAMEWORK: "React"
     LANG: "TypeScript"
   ```

5. **Enable pre-commit hooks**
   ```bash
   promptrek install-hooks --activate
   ```

## Next Steps

- Learn about [advanced features](../user-guide/advanced/variables.md)
- Explore [editor adapters](../user-guide/adapters/index.md)
- Check out [plugin configuration](../user-guide/plugins/index.md)
- Review [workflow guides](../user-guide/workflows/sync.md)
- See [real-world examples](../examples/index.md)
