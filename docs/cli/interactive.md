# Interactive Mode

PrompTrek's interactive mode provides a user-friendly, menu-driven interface for managing AI editor prompts without memorizing command-line options.

## Overview

Interactive mode launches automatically when you run `promptrek` without any arguments, or you can force it with the `--interactive` flag.

```bash
# Launch interactive mode
promptrek

# Or explicitly
promptrek --interactive
promptrek -i
```

## Interface

### Welcome Screen

When you launch interactive mode, you're greeted with the PrompTrek banner and main menu:

```
 ____                       _____         _
|  _ \ _ __ ___  _ __ ___  |_   _| __ ___| | __
| |_) | '__/ _ \| '_ ` _ \   | || '__/ _ \ |/ /
|  __/| | | (_) | | | | | |  | || | |  __/   <
|_|   |_|  \___/|_| |_| |_|  |_||_|  \___|_|\_\

Universal AI Editor Prompt Management (v3.0.0)

What would you like to do?
  🚀 Initialize new project
  ⚙️  Generate editor configurations
  🔌 Configure plugins (MCP servers, commands, agents)
  🔄 Migrate schema version
  🔍 Validate configuration
  📤 Sync from editor files
  ❓ Help & Documentation
  👋 Exit
```

### Navigation

- **Arrow keys** (↑↓): Navigate between options
- **Enter**: Select option
- **Ctrl+C**: Exit at any time

## Main Menu Options

### 🚀 Initialize New Project

Creates a new PrompTrek configuration file with guided setup.

**Workflow**:

1. **Check for existing config**
   - If found, prompts for overwrite confirmation
   - If not found, proceeds to setup

2. **Select schema version**
   - v3.0 (Current - Recommended) ✓
   - v2.x (Legacy)
   - v1.0 (Not recommended)

3. **Setup pre-commit hooks**
   - Question: "Setup pre-commit hooks?" (Yes/No)
   - Configures `.pre-commit-config.yaml` if Yes

4. **Configure .gitignore**
   - Question: "Add editor files to .gitignore?" (Yes/No)
   - Updates `.gitignore` with patterns if Yes

5. **Generate configurations**
   - Question: "Generate editor configurations now?" (Yes/No)
   - Launches generation workflow if Yes

**Example session**:
```
🚀 Initialize New Project

✓ No existing project.promptrek.yaml found

Select schema version:
❯ v3.0 (Current - Recommended)
  v2.x (Legacy)
  v1.0 (Not recommended)

Setup pre-commit hooks? (Y/n): y
Add editor files to .gitignore? (Y/n): y

✅ Created project.promptrek.yaml
✅ Configured .gitignore
✅ Installed pre-commit hooks

Generate editor configurations now? (Y/n): y
```

### ⚙️ Generate Editor Configurations

Generate editor-specific configuration files from your PrompTrek file.

**Workflow**:

1. **Check for configuration**
   - Looks for `project.promptrek.yaml`
   - Shows warning if not found

2. **Select editors**
   - Checkbox selection of available editors
   - Multiple selection supported
   - Space to select/deselect, Enter to confirm

3. **Variable overrides** (optional)
   - Question: "Do you want to override any variables?" (Yes/No)
   - If Yes, enter KEY=VALUE pairs (blank to finish)

4. **Headless mode** (optional)
   - Question: "Generate with headless agent instructions?" (Yes/No)

5. **Preview mode** (optional)
   - Question: "Preview mode (show what will be generated)?" (Yes/No)
   - Dry-run if Yes

6. **Generate**
   - Generates for each selected editor
   - Shows progress and results

**Example session**:
```
⚙️  Generate Editor Configurations

✓ Using configuration: project.promptrek.yaml

Select editors to generate for:
❯ ◉ Claude
  ◯ Continue
  ◉ Cursor
  ◯ Cline

Do you want to override any variables? (y/N): y

Enter variable overrides (KEY=VALUE). Leave blank to finish:
Variable (or press Enter to finish): VERSION=2.0.0
Variable (or press Enter to finish):

Generate with headless agent instructions? (y/N): n
Preview mode (show what will be generated)? (y/N): n

Generating for Claude...
Generating for Cursor...

🎉 All done! Your PrompTrek project is ready.
```

### 🔌 Configure Plugins

Manage MCP servers, custom commands, agents, and hooks.

**Sub-menu**:
```
🔌 Configure Plugins

What would you like to do?
  List configured plugins
  Generate plugin files
  Go back
```

#### List Configured Plugins

Displays all plugins defined in your PrompTrek file:

```
MCP Servers:
  • filesystem - Local filesystem access
  • github - GitHub API integration

Commands:
  • /explain - Explain code in detail
  • /test - Generate unit tests

Agents:
  • code-reviewer - Automated code review agent

Hooks:
  • pre-commit - Validate before commit
```

#### Generate Plugin Files

Generate plugin configurations for editors.

**Workflow**:

1. **Select editor**
   - All editors
   - Claude
   - Continue
   - Cursor
   - Windsurf
   - etc.

2. **Preview mode**
   - Question: "Preview mode?" (Yes/No)

3. **Generate**
   - Creates plugin files for selected editor(s)
   - Shows confirmation or warnings

### 🔄 Migrate Schema Version

Convert configuration files between schema versions.

**Workflow**:

1. **Check for configuration**
   - Looks for existing PrompTrek file
   - Shows warning if not found

2. **Confirm migration**
   - Question: "Migrate to v2 format?" (Yes/No)
   - Explains v2 uses markdown content

3. **Backup option**
   - Question: "Create backup of original file?" (Yes/No)

4. **Output file path**
   - Default: `<filename>.v2.promptrek.yaml`
   - Can customize

5. **Execute migration**
   - Migrates file
   - Creates backup if requested
   - Shows results

**Example session**:
```
🔄 Migrate Schema Version

✓ Found configuration: project.promptrek.yaml

Migrate to v2 format? (v2 uses pure markdown content) (Y/n): y
Create backup of original file? (Y/n): y
Output file path: project.v3.promptrek.yaml

✅ Migration completed successfully
✅ Backup saved to project.promptrek.yaml.backup
```

### 🔍 Validate Configuration

Validate your PrompTrek configuration file for errors.

**Workflow**:

1. **Check for configuration**
   - Looks for PrompTrek file
   - Shows warning if not found

2. **Strict mode**
   - Question: "Use strict mode (treat warnings as errors)?" (Yes/No)

3. **Validate**
   - Runs validation
   - Shows results with errors/warnings

4. **Display results**
   - ✅ Success
   - ⚠️ Warnings
   - ❌ Errors

**Example session**:
```
🔍 Validate Configuration

✓ Validating: project.promptrek.yaml

Use strict mode (treat warnings as errors)? (y/N): n

🔍 Validating project.promptrek.yaml...
✅ File parsed successfully
⚠️ Found 1 warning(s):
  • metadata.author: Recommended format is "Name <email@example.com>"
✅ Validation passed with warnings

✅ Validation completed successfully
```

### 📤 Sync from Editor Files

Sync editor-specific files back to PrompTrek configuration.

**Workflow**:

1. **Select editor**
   - Choose from editors with sync support
   - Claude, Continue, Cursor, etc.

2. **Source directory**
   - Default: current directory (`.`)
   - Can specify custom path

3. **Output file**
   - Default: `project.promptrek.yaml`
   - Can customize

4. **Preview mode**
   - Question: "Preview mode?" (Yes/No)
   - Shows what would be updated if Yes

5. **Execute sync**
   - Syncs editor files
   - Updates or creates PrompTrek file
   - Shows results

**Example session**:
```
📤 Sync from Editor Files

Select editor to sync from:
❯ Claude
  Continue
  Cursor

Source directory: .
Output PrompTrek file: project.promptrek.yaml
Preview mode (show what will be updated)? (Y/n): n

✅ Sync completed successfully
```

### ❓ Help & Documentation

Shows help information and links to documentation.

```
❓ Help & Documentation

For detailed documentation, visit:
  https://github.com/flamingquaks/promptrek

Common commands:
  promptrek init              - Initialize new project
  promptrek generate          - Generate editor configs
  promptrek validate          - Validate configuration
  promptrek --help            - Show all commands
```

### 👋 Exit

Exits interactive mode gracefully.

```
👋 Goodbye!
```

## Features

### Auto-Detection

Interactive mode automatically detects:
- Existing PrompTrek configuration files
- Available editors and their capabilities
- Plugin support in your configuration
- Schema version compatibility

### Guided Workflows

Each workflow provides:
- **Step-by-step guidance**: Clear prompts for each decision
- **Defaults**: Sensible defaults for common scenarios
- **Validation**: Input validation before proceeding
- **Confirmation**: Prompts before destructive actions

### Error Recovery

Interactive mode handles errors gracefully:
- **Clear error messages**: Explains what went wrong
- **Return to menu**: Doesn't crash on errors
- **Retry options**: Allows fixing issues and retrying

### Visual Feedback

Provides clear visual indicators:
- **Status symbols**: ✓ success, ⚠️ warning, ❌ error
- **Progress indicators**: Shows what's happening
- **Color coding**: Green for success, yellow for warnings, red for errors

## Tips and Best Practices

!!! tip "Use for Initial Setup"
    Interactive mode is perfect for setting up new projects when you're not familiar with all the options.

!!! tip "Keyboard Shortcuts"
    - `Ctrl+C` exits at any time
    - Arrow keys navigate
    - Space toggles checkboxes
    - Enter confirms selections

!!! tip "Mix Interactive and CLI"
    Use interactive mode for setup and configuration, then CLI commands for automation and scripting.

!!! note "Non-Interactive Environments"
    Interactive mode requires a TTY (terminal). In CI/CD or automated environments, use CLI commands instead.

## Troubleshooting

### Interactive Mode Doesn't Launch

**Problem**: Running `promptrek` shows help instead of interactive menu

**Cause**: Not running in a TTY (terminal)

**Solution**: Ensure you're running in a proper terminal, not via pipe or redirect:
```bash
# This works
promptrek

# This doesn't (shows help)
promptrek < input.txt
echo "" | promptrek
```

### Choices Not Showing

**Problem**: Menu appears but choices don't show

**Cause**: Terminal compatibility issues

**Solution**: Ensure your terminal supports ANSI escape codes:
```bash
# Check terminal type
echo $TERM

# Use CLI commands instead
promptrek init
promptrek generate --editor claude
```

### Canceling Operations

**Problem**: Need to cancel an operation

**Solution**: Press `Ctrl+C` at any prompt to cancel and return to main menu

## See Also

- [CLI Reference](index.md) - Complete command-line reference
- [init command](commands/init.md) - Initialize command details
- [generate command](commands/generate.md) - Generate command details
- [Getting Started](../getting-started/quick-start.md) - Quick start guide
