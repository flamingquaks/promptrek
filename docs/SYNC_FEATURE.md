# PrompTrek Sync Feature

The sync feature allows you to read AI editor-specific configuration files and create or update PrompTrek configuration from them. This enables bidirectional synchronization between PrompTrek and AI editors.

## Overview

Many AI editors can self-update their markdown configuration files based on project context and user interactions. The sync feature allows you to capture these changes back into your PrompTrek configuration, creating a feedback loop that keeps your universal prompts up-to-date.

## Supported Editors

Currently, the sync feature supports:

- **Continue**: Reads from `config.yaml` and `.continue/rules/*.md` files

## Usage

### Basic Sync

```bash
# Sync from Continue editor files to PrompTrek configuration
promptrek sync --source-dir . --editor continue --output project.promptrek.yaml
```

### Preview Changes (Dry Run)

```bash
# See what would be changed without making modifications
promptrek sync --source-dir . --editor continue --dry-run
```

### Force Overwrite

```bash
# Overwrite existing configuration without confirmation
promptrek sync --source-dir . --editor continue --force
```

## How It Works

### 1. Parsing Editor Files

The sync command reads editor-specific files and extracts:

- **Instructions**: From markdown bullet points and YAML config
- **Metadata**: Project title, description, and context
- **Technologies**: Detected from technology-specific rule files

### 2. Intelligent Merging

When syncing to an existing PrompTrek file:

- **Preserves existing data**: Examples, variables, and custom configuration
- **Merges instructions**: Combines new instructions with existing ones
- **Avoids duplicates**: Ensures no instruction appears twice
- **Updates metadata**: Refreshes timestamps and adds sync information

### 3. Instruction Categories

The sync feature maps editor files to PrompTrek instruction categories:

| Editor File | PrompTrek Category |
|-------------|-------------------|
| `general.md` | `instructions.general` |
| `code-style.md` | `instructions.code_style` |
| `testing.md` | `instructions.testing` |
| `security.md` | `instructions.security` |
| `performance.md` | `instructions.performance` |
| `architecture.md` | `instructions.architecture` |
| `*-rules.md` | `instructions.general` (with tech detection) |

## Example Workflow

1. **Start with PrompTrek configuration**:
   ```bash
   promptrek init --output project.promptrek.yaml
   ```

2. **Generate Continue files**:
   ```bash
   promptrek generate project.promptrek.yaml --editor continue --output continue_config
   ```

3. **AI editor modifies markdown files** (simulated):
   ```bash
   echo "- Always validate user input" >> continue_config/.continue/rules/security.md
   ```

4. **Sync changes back**:
   ```bash
   promptrek sync --source-dir continue_config --editor continue --output project.promptrek.yaml --force
   ```

5. **Result**: PrompTrek configuration now includes the new security instruction.

## Benefits

- **Bidirectional sync**: Changes flow both ways between PrompTrek and editors
- **AI-driven updates**: Capture improvements made by AI editors
- **Centralized configuration**: Maintain a single source of truth
- **Version control friendly**: All changes are captured in PrompTrek YAML files
- **Flexible merging**: Preserves manual customizations while adding AI improvements

## Error Handling

The sync command provides clear error messages for common issues:

- **Missing directory**: Validates that source directory exists
- **Unsupported editor**: Checks that the specified editor has sync support
- **Parse errors**: Continues processing even if some files can't be parsed
- **Permission issues**: Handles file access problems gracefully

## Future Enhancements

Planned improvements include:

- Support for more AI editors (Cursor, Copilot, etc.)
- Conflict resolution strategies
- Selective sync (choose which categories to sync)
- Backup and restore functionality
- Integration with version control workflows