# CLI Reference

PrompTrek provides a comprehensive command-line interface for managing universal AI editor prompts. This reference covers all available commands, options, and usage patterns.

## Quick Start

```bash
# Initialize a new project
promptrek init

# Generate editor configurations
promptrek generate --editor claude

# Validate your configuration
promptrek validate project.promptrek.yaml

# Interactive mode
promptrek
```

## Command Overview

| Command | Description |
|---------|-------------|
| [`promptrek init`](commands/init.md) | Initialize a new universal prompt file |
| [`promptrek generate`](commands/generate.md) | Generate editor-specific prompts |
| [`promptrek validate`](commands/validate.md) | Validate universal prompt files |
| [`promptrek sync`](commands/sync.md) | Sync editor files to PrompTrek configuration |
| [`promptrek migrate`](commands/migrate.md) | Migrate between schema versions |
| [`promptrek list-editors`](#list-editors) | List supported editors and capabilities |
| [`promptrek plugins`](#plugins-commands) | Manage plugin configurations |
| [`promptrek install-hooks`](#install-hooks) | Install pre-commit hooks |
| [`promptrek config-ignores`](#config-ignores) | Configure .gitignore for editor files |

## Global Options

All commands support these global options:

```bash
promptrek [OPTIONS] COMMAND [ARGS]...
```

### Options

- **`--version`**: Show the version and exit
- **`-v, --verbose`**: Enable verbose output for detailed logging
- **`-i, --interactive`**: Force interactive mode

### Examples

```bash
# Show version
promptrek --version

# Run with verbose output
promptrek --verbose generate --editor claude

# Force interactive mode
promptrek --interactive
```

## Interactive Mode

When run without a command, PrompTrek enters interactive mode with a menu-driven interface:

```bash
promptrek
```

See [Interactive Mode](interactive.md) for detailed documentation.

## Core Commands

### init

Initialize a new universal prompt file with optional pre-commit hook setup.

[→ Full documentation](commands/init.md)

```bash
promptrek init [OPTIONS]
```

### generate

Generate editor-specific prompts from universal prompt files.

[→ Full documentation](commands/generate.md)

```bash
promptrek generate [FILES]... [OPTIONS]
```

### validate

Validate one or more universal prompt files for correctness.

[→ Full documentation](commands/validate.md)

```bash
promptrek validate FILES... [OPTIONS]
```

### sync

Sync editor-specific files back to PrompTrek configuration.

[→ Full documentation](commands/sync.md)

```bash
promptrek sync [OPTIONS]
```

### migrate

Migrate configuration files between schema versions.

[→ Full documentation](commands/migrate.md)

```bash
promptrek migrate INPUT_FILE [OPTIONS]
```

## Additional Commands

### list-editors

List all supported AI editors and their capabilities.

```bash
promptrek list-editors
```

**Output Categories:**

- **Project Configuration File Support**: Editors that support project-level config files
- **Global Configuration Only**: Editors configured through global settings
- **IDE Configuration Only**: Editors configured through IDE interface

**Example Output:**

```
AI Editor Support Status:

✅ Project Configuration File Support:
   • claude       - Claude Code editor support → .claude/prompts/*.md
   • continue     - Continue VSCode extension → .continue/config.json
   • cursor       - Cursor IDE support → .cursorrules

ℹ️  Global Configuration Only:
   • copilot      - Configure through global settings or admin panel

Usage Examples:
  Generate for specific editor:  promptrek generate config.yaml --editor claude
  Generate for all supported:    promptrek generate config.yaml --all
```

### Plugins Commands

Manage MCP servers, slash commands, agents, and hooks (v2.1.0+ schemas).

#### plugins list

List all configured plugins in your PrompTrek file.

```bash
promptrek plugins list [OPTIONS]
```

**Options:**
- **`-f, --file PATH`**: PrompTrek file to list plugins from (auto-detects if not specified)

**Example:**

```bash
promptrek plugins list
promptrek plugins list --file custom.promptrek.yaml
```

#### plugins generate

Generate plugin files for supported editors.

```bash
promptrek plugins generate [OPTIONS]
```

**Options:**
- **`-f, --file PATH`**: PrompTrek file to generate from
- **`-e, --editor EDITOR`**: Editor to generate for (claude, cursor, continue, windsurf, cline, amazon-q, kiro, or 'all')
- **`-o, --output PATH`**: Output directory (default: current directory)
- **`--dry-run`**: Show what would be generated without creating files
- **`-s, --force-system-wide`**: Force system-wide configuration (skip project-level)
- **`-y, --yes`**: Auto-confirm all prompts (use with caution for system-wide changes)

**Example:**

```bash
# Generate for Claude with project-level config
promptrek plugins generate --editor claude

# Generate for Windsurf (system-wide, with confirmation)
promptrek plugins generate --editor windsurf

# Auto-confirm system-wide changes
promptrek plugins generate --editor windsurf --yes

# Generate for all editors with plugin support
promptrek plugins generate --editor all
```

#### plugins validate

Validate plugin configurations in your PrompTrek file.

```bash
promptrek plugins validate [OPTIONS]
```

**Options:**
- **`-f, --file PATH`**: PrompTrek file to validate

**Example:**

```bash
promptrek plugins validate
promptrek plugins validate --file project.promptrek.yaml
```

### install-hooks

Install PrompTrek pre-commit hooks to prevent committing generated files.

```bash
promptrek install-hooks [OPTIONS]
```

**Options:**
- **`-c, --config PATH`**: Path to .pre-commit-config.yaml (defaults to .pre-commit-config.yaml)
- **`-f, --force`**: Overwrite existing hooks without confirmation
- **`-a, --activate`**: Automatically run 'pre-commit install' to activate hooks in git

**Example:**

```bash
# Install and activate hooks
promptrek install-hooks --activate

# Force overwrite existing hooks
promptrek install-hooks --force --activate

# Install to custom config file
promptrek install-hooks --config .pre-commit-custom.yaml --activate
```

The command:
1. Creates or updates `.pre-commit-config.yaml` with PrompTrek hooks
2. Preserves any existing hooks you have configured
3. Optionally activates the hooks in your git repository

### config-ignores

Configure .gitignore to exclude editor-specific generated files.

```bash
promptrek config-ignores [OPTIONS]
```

**Options:**
- **`-c, --config PATH`**: Path to PrompTrek config file (auto-detects if not specified)
- **`-r, --remove-cached`**: Run 'git rm --cached' on existing committed files
- **`--dry-run`**: Show what would be done without making changes

**Example:**

```bash
# Add patterns to .gitignore
promptrek config-ignores

# Add patterns and remove cached files from git
promptrek config-ignores --remove-cached

# Preview what would be done
promptrek config-ignores --dry-run
```

This command adds editor file patterns to `.gitignore` based on your PrompTrek configuration's `ignore_editor_files` setting.

## Environment Variables

PrompTrek supports these environment variables:

- **`PROMPTREK_CONFIG`**: Default path to configuration file
- **`PROMPTREK_VERBOSE`**: Set to '1' to enable verbose output by default

## Exit Codes

PrompTrek uses standard exit codes:

- **`0`**: Success
- **`1`**: General error (parsing, validation, or generation failure)
- **`2`**: Command-line usage error

## Configuration Files

PrompTrek looks for configuration in multiple locations:

1. Command-line specified file
2. `project.promptrek.yaml` in current directory
3. `.promptrek.yaml` in current directory
4. Search parent directories up to repository root

## Working with Multiple Files

Many commands support processing multiple files:

```bash
# Validate multiple files
promptrek validate file1.yaml file2.yaml file3.yaml

# Generate from multiple files
promptrek generate file1.yaml file2.yaml --editor claude

# Use directory scanning
promptrek generate --directory ./configs --recursive --all
```

## Output Control

### Dry Run Mode

Most generation commands support `--dry-run` to preview changes:

```bash
# Preview without creating files
promptrek generate --editor claude --dry-run
promptrek sync --editor continue --dry-run
promptrek plugins generate --editor all --dry-run
```

### Verbose Mode

Enable detailed logging with `--verbose`:

```bash
promptrek --verbose generate --editor claude
```

## Error Handling

PrompTrek provides clear error messages and suggestions:

```bash
# Missing editor specification
$ promptrek generate
Error: Must specify either --editor or --all

# Invalid file
$ promptrek validate invalid.yaml
❌ Parsing failed: Invalid YAML syntax at line 10

# Editor not found
$ promptrek generate --editor unknown
Error: Editor 'unknown' not available. Available editors: claude, continue, cursor, ...
```

## Tips and Best Practices

!!! tip "Use Interactive Mode for New Projects"
    When starting a new project, use interactive mode (`promptrek`) for a guided setup experience.

!!! tip "Validate Before Generating"
    Always validate your configuration before generating files:
    ```bash
    promptrek validate project.promptrek.yaml
    promptrek generate --all
    ```

!!! tip "Use Dry Run for Safety"
    Test generation commands with `--dry-run` before creating actual files:
    ```bash
    promptrek generate --editor claude --dry-run
    ```

!!! warning "Pre-commit Hooks"
    Install pre-commit hooks to prevent accidentally committing generated files:
    ```bash
    promptrek install-hooks --activate
    ```

!!! note "Variable Overrides"
    You can override variables at generation time:
    ```bash
    promptrek generate --editor claude -V VERSION=2.0.0 -V ENV=production
    ```

## Common Workflows

### Initial Setup

```bash
# 1. Initialize project
promptrek init

# 2. Edit configuration
vim project.promptrek.yaml

# 3. Validate
promptrek validate project.promptrek.yaml

# 4. Generate for all editors
promptrek generate --all

# 5. Set up git hooks
promptrek install-hooks --activate
promptrek config-ignores
```

### Daily Development

```bash
# Update configuration
vim project.promptrek.yaml

# Validate changes
promptrek validate project.promptrek.yaml

# Regenerate for specific editor
promptrek generate --editor claude
```

### Syncing from Editor

```bash
# Made changes in Continue editor
# Sync back to PrompTrek
promptrek sync --editor continue

# Review changes
git diff project.promptrek.yaml

# Generate for other editors
promptrek generate --all
```

## See Also

- [Getting Started Guide](../getting-started/quick-start.md)
- [UPF Specification](../user-guide/upf-specification.md)
- [Adapters Documentation](../user-guide/adapters/index.md)
- [Interactive Mode](interactive.md)
