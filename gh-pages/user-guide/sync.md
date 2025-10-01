---
layout: guide
title: Sync Feature
---

# PrompTrek Sync Feature

The sync feature allows you to read AI editor-specific configuration files and create or update PrompTrek configuration from them. This enables bidirectional synchronization between PrompTrek and AI editors.

## Overview

Many AI editors can self-update their markdown configuration files based on project context and user interactions. The sync feature allows you to capture these changes back into your PrompTrek configuration, creating a feedback loop that keeps your universal prompts up-to-date.

## Supported Editors

Currently, the sync feature supports:

- **Continue**: Reads from `config.yaml` and `.continue/rules/*.md` files
- **GitHub Copilot**: Reads from `.github/copilot-instructions.md`, `.github/instructions/*.instructions.md`, and `.github/prompts/*.prompt.md` files

## Usage

### Basic Sync

```bash
# Sync from Continue editor files to PrompTrek configuration
promptrek sync --source-dir . --editor continue --output project.promptrek.yaml

# Sync from GitHub Copilot files to PrompTrek configuration
promptrek sync --source-dir . --editor copilot --output project.promptrek.yaml
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

- **Preserves user-defined metadata**: Keeps custom titles/descriptions over auto-generated ones
- **Merges instructions additively**: Combines new instructions with existing ones without data loss
- **Smart duplicate detection**: Ensures no instruction appears twice across categories
- **Context preservation**: Merges technologies and project information intelligently
- **Timestamp tracking**: Updates sync timestamps while preserving creation dates
- **Source attribution**: Distinguishes between user-defined and auto-generated content

### 3. Instruction Categories

The sync feature maps editor files to PrompTrek instruction categories:

#### Continue Editor
| Editor File | PrompTrek Category |
|-------------|-------------------|
| `general.md` | `instructions.general` |
| `code-style.md` | `instructions.code_style` |
| `testing.md` | `instructions.testing` |
| `security.md` | `instructions.security` |
| `performance.md` | `instructions.performance` |
| `architecture.md` | `instructions.architecture` |
| `*-rules.md` | `instructions.general` (with tech detection) |

#### GitHub Copilot
| Editor File | PrompTrek Category |
|-------------|-------------------|
| `.github/copilot-instructions.md` → `## General Instructions` | `instructions.general` |
| `.github/copilot-instructions.md` → `## Code Style Guidelines` | `instructions.code_style` |
| `.github/instructions/testing.instructions.md` | `instructions.testing` |
| `.github/instructions/code-style.instructions.md` | `instructions.code_style` |
| `.github/prompts/*.prompt.md` | `instructions.general` |

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

## Advanced Features

### Headless Agent Instructions

GitHub Copilot supports headless agent instructions that provide autonomous regeneration capability:

```bash
# Generate Copilot files with headless instructions
promptrek generate project.promptrek.yaml --editor copilot --headless
```

This creates files with embedded instructions for Copilot to regenerate its own configuration:
```markdown
<!-- HEADLESS INSTRUCTIONS START -->
<!--
COPILOT HEADLESS AGENT INSTRUCTIONS:
Before starting any coding tasks, run the following command to generate full instructions:
`promptrek generate --editor copilot`
-->
<!-- HEADLESS INSTRUCTIONS END -->
```

### Round-trip Compatibility

The sync system ensures complete round-trip compatibility:
- **Generate → Sync → Generate** maintains data integrity
- No information loss during bidirectional conversion
- User customizations are preserved across sync operations

## Future Enhancements

Planned improvements include:

- Support for more AI editors (Cursor, Claude Code, etc.)
- Conflict resolution strategies with user preferences
- Selective sync (choose which categories to sync)
- Backup and restore functionality
- Integration with version control workflows
- Smart sync scheduling and automation