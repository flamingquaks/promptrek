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
metadata:
  title: "{{{ PROJECT_NAME }}} Assistant"
  description: "AI assistant for {{{ PROJECT_NAME }}}"

instructions:
  general:
    - "Follow {{{ PROJECT_NAME }}} coding standards"
    - "Contact {{{ AUTHOR_EMAIL }}} for questions"

variables:
  PROJECT_NAME: "MyProject" 
  AUTHOR_EMAIL: "team@example.com"
```
{% endraw %}

### Environment Variables

You can also reference environment variables using `${}` syntax:

```yaml
metadata:
  author: "${AUTHOR_NAME}"
  
instructions:
  general:
    - "Deploy to ${ENVIRONMENT} environment"
```

### Local Variables File

PrompTrek supports a `variables.promptrek.yaml` file for user-specific variables that should not be committed to version control. This is perfect for storing local paths, API keys, personal information, or any variable that varies between team members.

**Creating a local variables file:**

```yaml
# variables.promptrek.yaml
# This file contains local variables that should NOT be committed
# Add this file to .gitignore

# User-specific variables
AUTHOR_NAME: "Your Name"
AUTHOR_EMAIL: "your.email@example.com"
API_KEY: "your-api-key-here"
LOCAL_PATH: "/path/to/local/resource"
ENVIRONMENT: "development"
```

**How it works:**

1. When you run `promptrek init`, it automatically:
   - Adds `variables.promptrek.yaml` to `.gitignore`
   - Adds 18 editor-specific file patterns to `.gitignore`
2. Create your local variables file manually with user-specific values
3. PrompTrek automatically loads variables from this file when generating
4. Pre-commit hooks prevent accidental commits of this file

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
- `.tabnine_commands`
- `.vscode/mcp.json`

You can disable this with `ignore_editor_files: false` in your config.

**Variable Precedence (highest to lowest):**

1. CLI overrides (`-V KEY=value`)
2. Local variables file (`variables.promptrek.yaml`)
3. Prompt file variables section

**Example usage:**

{% raw %}
```yaml
# project.promptrek.yaml (committed to git)
metadata:
  title: "{{{ PROJECT_NAME }}} Assistant"
  author: "{{{ AUTHOR_NAME }}}"

variables:
  PROJECT_NAME: "MyProject"
  AUTHOR_NAME: "Team"  # Default fallback
```
{% endraw %}

```yaml
# variables.promptrek.yaml (local, in .gitignore)
AUTHOR_NAME: "John Doe"
AUTHOR_EMAIL: "john@example.com"
```

When generating, `AUTHOR_NAME` will be "John Doe" from the local file, overriding the default in the prompt file.

### CLI Variable Overrides

Override variables from the command line using `-V` or `--var`:

```bash
promptrek generate --editor claude --output ./output project.promptrek.yaml \
  -V PROJECT_NAME="CustomProject" \
  -V AUTHOR_EMAIL="custom@example.com"
```

CLI overrides have the highest precedence and will override both local variables and prompt file variables.

## Conditional Instructions

Conditional instructions allow you to provide different instructions based on the target editor or other conditions.

### Basic Conditionals

```yaml
conditions:
  - if: "EDITOR == \"claude\""
    then:
      instructions:
        general:
          - "Claude-specific: Provide detailed explanations"
          - "Claude-specific: Focus on code clarity"
      examples:
        claude_example: "// Example optimized for Claude"

  - if: "EDITOR == \"continue\""
    then:
      instructions:
        general:
          - "Continue-specific: Generate comprehensive completions"
```

### Supported Conditions

- **Equality**: `EDITOR == "claude"`
- **Inequality**: `EDITOR != "copilot"`  
- **List membership**: `EDITOR in ["claude", "cursor"]`
- **Boolean variables**: `DEBUG_MODE` (checks if variable is truthy)

### Conditional Examples and Variables

Conditionals can modify any part of your configuration:

```yaml
conditions:
  - if: "PROJECT_TYPE == \"mobile\""
    then:
      examples:
        mobile_component: "const Screen = () => <View><Text>Hello</Text></View>;"
      variables:
        PLATFORM: "React Native"

  - if: "ENVIRONMENT == \"production\""
    then:
      instructions:
        general:
          - "Use production-safe coding practices"
          - "Include comprehensive error handling"
```

## Import System

The import system allows you to share common configurations across multiple projects.

### Basic Import

Create a base configuration file:

```yaml
# base-config.promptrek.yaml
schema_version: "1.0.0"

metadata:
  title: "Base Configuration"
  description: "Shared configuration"
  version: "1.0.0"
  author: "team@company.com"
  created: "2024-01-01"
  updated: "2024-01-01"

targets:
  - claude

instructions:
  general:
    - "Follow clean code principles"
    - "Use meaningful variable names"
  code_style:
    - "Use 2-space indentation"
    - "Prefer const over let"

examples:
  util_function: "const capitalize = (str) => str.charAt(0).toUpperCase() + str.slice(1);"

variables:
  STYLE_GUIDE: "Company Standard"
  INDENT_SIZE: "2"
```

Then import it in your main file:

```yaml
# project.promptrek.yaml
schema_version: "1.0.0"

metadata:
  title: "My Project"
  description: "Project with shared configuration"
  # ... other metadata

targets:
  - claude

imports:
  - path: "base-config.promptrek.yaml"
    prefix: "shared"

instructions:
  general:
    - "Project-specific instruction"
  testing:
    - "Write comprehensive tests"
```

### Import with Prefix

The `prefix` option namespaces imported content to avoid conflicts:

- Instructions get prefixed: `[shared] Follow clean code principles`
- Examples get prefixed: `shared_util_function`  
- Variables get prefixed: `shared_STYLE_GUIDE`

### Import Behavior

- **Instructions**: Imported instructions are merged with existing ones
- **Examples**: Imported examples are added with prefixed names
- **Variables**: Imported variables are added with prefixed names (unless already present)
- **Metadata**: Metadata from imported files is ignored (only the main file's metadata is used)

### Relative Paths

Import paths are relative to the importing file:

```
project/
├── config/
│   └── base.promptrek.yaml
├── frontend/
│   └── frontend.promptrek.yaml  # imports: path: "../config/base.promptrek.yaml"
└── backend/
    └── backend.promptrek.yaml   # imports: path: "../config/base.promptrek.yaml"
```

### Circular Import Protection

The import system automatically detects and prevents circular imports:

```yaml
# file-a.promptrek.yaml
imports:
  - path: "file-b.promptrek.yaml"

# file-b.promptrek.yaml  
imports:
  - path: "file-a.promptrek.yaml"  # This will cause an error
```

## Combining Features

All advanced features work together seamlessly:

{% raw %}
```yaml
# base.promptrek.yaml
instructions:
  general:
    - "Use {{{ CODING_STYLE }}} coding style"

conditions:
  - if: "EDITOR == \"claude\""
    then:
      instructions:
        general:
          - "Claude: Use {{{ AI_APPROACH }}} approach"

variables:
  CODING_STYLE: "clean"
  AI_APPROACH: "detailed"

# main.promptrek.yaml
imports:
  - path: "base.promptrek.yaml"
    prefix: "base"

conditions:
  - if: "EDITOR == \"claude\""
    then:
      instructions:
        general:
          - "Main: Use {{{ MAIN_APPROACH }}} methodology"

variables:
  PROJECT_NAME: "AdvancedProject"
  MAIN_APPROACH: "comprehensive"
```
{% endraw %}

Generate with overrides:

```bash
promptrek generate --editor claude --output ./output main.promptrek.yaml \
  -V PROJECT_NAME="CustomProject" \
  -V base_CODING_STYLE="strict" \
  -V base_AI_APPROACH="concise"
```

This will:
1. Import base configuration with "base" prefix
2. Apply variable substitution to both files
3. Process conditionals for Claude editor
4. Override variables via CLI
5. Merge all instructions and content

## .gitignore Management

PrompTrek automatically manages `.gitignore` to prevent committing generated editor files. This keeps your repository clean by ensuring only the source `.promptrek.yaml` files are version controlled.

### Automatic Configuration on Init

When you run `promptrek init`, it automatically:
- Creates `.gitignore` if it doesn't exist
- Adds `variables.promptrek.yaml` to `.gitignore`
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
- **Continue**: `.continue/rules/*.md`
- **Windsurf**: `.windsurf/rules/*.md`
- **Cline**: `.clinerules`, `.clinerules/*.md`
- **Claude**: `.claude/CLAUDE.md`, `.claude-context.md`
- **Amazon Q**: `.amazonq/rules/*.md`, `.amazonq/cli-agents/*.json`
- **JetBrains**: `.assistant/rules/*.md`
- **Kiro**: `.kiro/steering/*.md`
- **Tabnine**: `.tabnine_commands`
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

### Conditionals  
- Keep conditions simple and readable
- Use editor-specific instructions sparingly - most instructions should be universal
- Test your conditionals with different editors

### Imports
- Use prefixes to avoid naming conflicts
- Keep shared configurations focused and minimal
- Document your import structure in README files
- Use relative paths for portability

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
