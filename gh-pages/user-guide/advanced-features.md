---
layout: guide
title: Advanced Features
---

# Advanced Template Features

PrompTrek supports powerful advanced template features that allow you to create flexible, maintainable prompt configurations.

## Variable Substitution

Variables allow you to create reusable templates that can be customized for different projects or contexts.

### Basic Variable Syntax

Use triple braces to define variable placeholders in your UPF files:

{% raw %}
```yaml
# v3.0 format (recommended)
schema_version: "3.0.0"
metadata:
  title: "{{{ PROJECT_NAME }}} Assistant"
  description: "AI assistant for {{{ PROJECT_NAME }}}"

content: |
  # {{{ PROJECT_NAME }}} Development Guide

  Follow {{{ PROJECT_NAME }}} coding standards.
  Contact {{{ AUTHOR_EMAIL }}} for questions.

variables:
  PROJECT_NAME: "MyProject"
  AUTHOR_EMAIL: "team@example.com"
```
{% endraw %}

### Environment Variables

You can also reference environment variables using `${}` syntax:

```yaml
schema_version: "3.0.0"
metadata:
  author: "${AUTHOR_NAME}"

content: |
  # Project Guidelines

  Deploy to ${ENVIRONMENT} environment.
```

### Local Variables File

PrompTrek supports a `.promptrek/variables.promptrek.yaml` file for user-specific variables that should not be committed to version control. This is perfect for storing local paths, API keys, personal information, or any variable that varies between team members.

**Creating a local variables file:**

```yaml
# .promptrek/variables.promptrek.yaml
# This file contains local variables that should NOT be committed
# The .promptrek/ directory is automatically added to .gitignore

# User-specific variables
AUTHOR_NAME: "Your Name"
AUTHOR_EMAIL: "your.email@example.com"
API_KEY: "your-api-key-here"
LOCAL_PATH: "/path/to/local/resource"
ENVIRONMENT: "development"
```

**How it works:**

1. When you run `promptrek init`, it automatically:
   - Adds `.promptrek/` directory to `.gitignore` (contains user-specific config like `variables.promptrek.yaml` and `user-config.promptrek.yaml`)
   - Adds 18 editor-specific file patterns to `.gitignore`
2. Create your local variables file manually in the `.promptrek/` directory with user-specific values
3. PrompTrek automatically loads variables from this file when generating
4. Pre-commit hooks prevent accidental commits of files in the `.promptrek/` directory

**Editor files automatically excluded:**

When `ignore_editor_files` is enabled (default), PrompTrek adds these patterns to `.gitignore`:
- `.github/copilot-instructions.md`, `.github/instructions/*.instructions.md`, `.github/prompts/*.prompt.md`
- `.cursor/rules/*.mdc`, `.cursor/rules/index.mdc`, `AGENTS.md`
- `.continue/rules/*.md`
- `.windsurf/rules/*.md`
- `.clinerules`, `.clinerules/*.md`
- `.claude/CLAUDE.md`, `.claude-context.md`
- `.amazonq/rules/*.md`, `.amazonq/cli-agents/*.json`
- `.assistant/rules/*.md`
- `.kiro/steering/*.md`
- `.vscode/mcp.json`

You can disable this with `ignore_editor_files: false` in your config.

**Variable Precedence (highest to lowest):**

1. CLI overrides (`-V KEY=value`)
2. Local variables file (`.promptrek/variables.promptrek.yaml`)
3. Prompt file variables section

**Example usage:**

{% raw %}
```yaml
# project.promptrek.yaml (committed to git)
schema_version: "3.0.0"
metadata:
  title: "{{{ PROJECT_NAME }}} Assistant"
  author: "{{{ AUTHOR_NAME }}}"

content: |
  # {{{ PROJECT_NAME }}} Development Guide

  Maintained by {{{ AUTHOR_NAME }}} ({{{ AUTHOR_EMAIL }}}).

variables:
  PROJECT_NAME: "MyProject"
  AUTHOR_NAME: "Team"  # Default fallback
  AUTHOR_EMAIL: "team@example.com"  # Default fallback
```
{% endraw %}

```yaml
# .promptrek/variables.promptrek.yaml (local, gitignored via .promptrek/ directory)
AUTHOR_NAME: "John Doe"
AUTHOR_EMAIL: "john@example.com"
```

**Note:** If you have an old `variables.promptrek.yaml` file in your project root, PrompTrek will automatically offer to migrate it to the new `.promptrek/` directory location when you run any command.

When generating, `AUTHOR_NAME` will be "John Doe" from the local file, overriding the default in the prompt file.

### CLI Variable Overrides

Override variables from the command line using `-V` or `--var`:

```bash
promptrek generate --editor claude --output ./output project.promptrek.yaml \
  -V PROJECT_NAME="CustomProject" \
  -V AUTHOR_EMAIL="custom@example.com"
```

CLI overrides have the highest precedence and will override both local variables and prompt file variables.

## Combining Features with v3.0

In v3.0, you can combine variable substitution with multiple documents:

{% raw %}
```yaml
schema_version: "3.0.0"
metadata:
  title: "{{{ PROJECT_NAME }}} Assistant"

content: |
  # {{{ PROJECT_NAME }}} Development Guide

  Follow {{{ CODING_STYLE }}} coding standards.

documents:
  - name: "testing"
    content: |
      # Testing Standards
      - Use {{{ TEST_FRAMEWORK }}}
      - Aim for {{{ COVERAGE_TARGET }}}% coverage

variables:
  PROJECT_NAME: "AdvancedProject"
  CODING_STYLE: "clean"
  TEST_FRAMEWORK: "Jest"
  COVERAGE_TARGET: "80"
```
{% endraw %}

## Document Metadata

Documents in v2.0+ and v3.0 support metadata fields that control how editors like Cursor apply rules:

{% raw %}
```yaml
schema_version: "3.0.0"
metadata:
  title: "{{{ PROJECT_NAME }}} Assistant"

# Main content metadata (optional)
content_description: "Project overview and core guidelines"  # Default if not specified
content_always_apply: true  # Default: Always Applied rule

content: |
  # {{{ PROJECT_NAME }}} Development Guide

  Follow project coding standards.

documents:
  - name: "typescript"
    content: |
      # TypeScript Guidelines
      - Use strict TypeScript settings
      - Prefer interfaces over types
    description: "TypeScript coding guidelines"  # Shown in Cursor UI
    file_globs: "**/*.{ts,tsx}"  # Files where rule applies
    always_apply: false  # Auto-attached (applies only to matching files)

  - name: "testing"
    content: |
      # Testing Standards
      - Write unit tests for all functions
      - Aim for 80% coverage
    # Omit metadata for smart defaults:
    # - description: "testing guidelines" (inferred from name)
    # - file_globs: "**/*.{test,spec}.*" (inferred for Cursor)
    # - always_apply: false (default for documents)

variables:
  PROJECT_NAME: "AdvancedProject"
```
{% endraw %}

**Metadata Fields**:
- `description`: Human-readable description (used by Cursor, Copilot, etc.)
- `file_globs`: File patterns where rule applies (e.g., `**/*.{ts,tsx}`)
- `always_apply`: `true` = Always Applied, `false` = Auto Attached (file-specific)

**Smart Defaults**:
- Main content: `description="Project overview and core guidelines"`, `always_apply=true`
- Documents: `description="{name} guidelines"`, `always_apply=false`, auto-infer globs from name

**Editor Support**:
- **Cursor**: Maps to MDC frontmatter (`description`, `globs`, `alwaysApply`)
- **Copilot**: Can map `file_globs` to path-specific instructions
- **Other Editors**: Gracefully ignored if not supported

Generate with CLI overrides:

```bash
promptrek generate --editor claude --output ./output project.promptrek.yaml \
  -V PROJECT_NAME="CustomProject" \
  -V CODING_STYLE="strict" \
  -V COVERAGE_TARGET="90"
```

This provides:
1. Variable substitution across all content
2. CLI overrides for customization
3. Multiple document support for organization
4. Clean, maintainable v3.0 format

## .gitignore Management

PrompTrek automatically manages `.gitignore` to prevent committing generated editor files. This keeps your repository clean by ensuring only the source `.promptrek.yaml` files are version controlled.

### Automatic Configuration on Init

When you run `promptrek init`, it automatically:
- Creates `.gitignore` if it doesn't exist
- Adds `.promptrek/` directory to `.gitignore` (contains user-specific config like `variables.promptrek.yaml` and `user-config.promptrek.yaml`)
- Adds 18 editor-specific file patterns to `.gitignore`

### Configuration Option

Control .gitignore management in your `.promptrek.yaml`:

```yaml
schema_version: "2.1.0"
metadata:
  title: "My Project"
  # ...

# Set to false to disable automatic .gitignore management (default: true)
ignore_editor_files: false
```

### Manual Management with config-ignores

If you have existing editor files already committed to git, use the `config-ignores` command:

```bash
# Add patterns to .gitignore
promptrek config-ignores

# Add patterns and remove committed files from git
promptrek config-ignores --remove-cached

# Preview what would be done
promptrek config-ignores --dry-run

# Use specific config file
promptrek config-ignores --config custom.promptrek.yaml
```

**What the `--remove-cached` flag does:**
1. Adds all editor file patterns to `.gitignore`
2. Runs `git rm --cached` on each matching file already in git
3. Files remain in your working directory but are staged for removal from git
4. You need to commit the changes to complete the un-tracking

**Example workflow for cleaning up committed files:**

```bash
# Clean up previously committed editor files
promptrek config-ignores --remove-cached

# Review the changes
git status

# Commit the changes
git commit -m "Untrack generated editor files"
git push
```

### Editor Files Automatically Excluded

When `ignore_editor_files` is enabled (default: true), these patterns are added to `.gitignore`:

- **GitHub Copilot**: `.github/copilot-instructions.md`, `.github/instructions/*.instructions.md`, `.github/prompts/*.prompt.md`
- **Cursor**: `.cursor/rules/*.mdc`, `.cursor/rules/index.mdc`, `AGENTS.md`
- **Continue**: `.continue/config.yaml`, `.continue/mcpServers/*.yaml`, `.continue/prompts/*.md`, `.continue/rules/*.md`
- **Windsurf**: `.windsurf/rules/*.md`
- **Cline**: `.clinerules`, `.clinerules/*.md`
- **Claude**: `.claude/CLAUDE.md`, `.claude-context.md`
- **Amazon Q**: `.amazonq/rules/*.md`, `.amazonq/cli-agents/*.json`
- **JetBrains**: `.assistant/rules/*.md`
- **Kiro**: `.kiro/steering/*.md`
- **MCP Configs**: `.vscode/mcp.json`

### Sync Command Integration

The `promptrek sync` command also respects the `ignore_editor_files` configuration. After syncing editor files back to PrompTrek format, it automatically updates `.gitignore` if enabled.

```bash
# Sync from Continue and update .gitignore
promptrek sync --editor continue --output project.promptrek.yaml
# .gitignore is automatically updated if ignore_editor_files: true
```

## Best Practices

### Variables
- Use UPPER_CASE for variable names
- Provide sensible defaults in the `variables` section
- Use descriptive variable names: `PROJECT_NAME` not `PN`

### Multi-Document Organization
- Use the `documents` field for organizing content by category or technology
- Keep document names descriptive and focused
- Separate general guidelines from technology-specific rules

### Organization
```
project/
├── shared/
│   ├── base-coding-standards.promptrek.yaml
│   ├── base-testing.promptrek.yaml
│   └── base-typescript.promptrek.yaml
├── frontend/
│   └── frontend.promptrek.yaml
├── backend/  
│   └── backend.promptrek.yaml
└── README.md  # Document your configuration structure
```
