# Interactive CLI Workflows

PrompTrek's interactive mode provides a guided, user-friendly interface for common tasks.

## Overview

Interactive mode launches when you run `promptrek` without arguments, providing a menu-driven interface for:

- Initializing new configurations
- Generating editor files
- Validating configurations
- Managing plugins
- Setting up pre-commit hooks

## Launching Interactive Mode

### Automatic Launch

```bash
# Just run promptrek
promptrek

# Or explicitly
promptrek --interactive
promptrek -i
```

### Interactive Menu

```
PrompTrek - Universal AI Editor Prompt Management

What would you like to do?

  1. Initialize new configuration
  2. Generate editor files
  3. Validate configuration
  4. List available editors
  5. Manage plugins
  6. Install pre-commit hooks
  7. Exit

Select an option (1-7):
```

## Common Workflows

### Initialize New Project

```
Select: 1 (Initialize new configuration)

→ Which schema version?
  1. v3.1.0 (recommended - latest features)
  2. v3.0.0 (stable)
  3. v2.1.0 (legacy)

Select: 1

→ Use a template?
  1. Blank configuration
  2. Web application
  3. API service
  4. CLI tool
  5. Library

Select: 2

→ Output file name:
  [project.promptrek.yaml]:

→ Set up pre-commit hooks?
  [Y/n]: y

✅ Created project.promptrek.yaml
✅ Installed pre-commit hooks
```

### Generate for Editors

```
Select: 2 (Generate editor files)

→ Select configuration file:
  1. project.promptrek.yaml
  2. backend.promptrek.yaml
  3. Browse...

Select: 1

→ Select editor(s):
  [ ] Claude
  [ ] Cursor
  [ ] Continue
  [ ] All editors

Selected: Claude, Cursor

→ Output directory:
  [current directory]:

✅ Generated files for Claude
✅ Generated files for Cursor
```

### Manage Plugins

```
Select: 5 (Manage plugins)

→ Plugin operation:
  1. List configured plugins
  2. Generate plugin configs
  3. Validate plugins

Select: 1

📦 Plugins in project.promptrek.yaml:

🔌 MCP Servers (2):
  • github
  • filesystem

⚡ Commands (3):
  • review-code
  • generate-tests
  • deploy

Press Enter to continue...
```

## Benefits of Interactive Mode

### Beginner-Friendly

- No need to memorize commands
- Guided workflows
- Clear prompts and options
- Helpful error messages

### Efficient

- Quick access to common tasks
- Smart defaults
- Auto-completion where applicable
- Multi-select options

### Safe

- Confirmation prompts for destructive operations
- Preview before generation
- Validation before proceeding

## Advanced Features

### Context Awareness

Interactive mode detects:

- Existing `.promptrek.yaml` files
- Git repository status
- Installed editors
- Pre-commit configuration

### Smart Suggestions

Based on your project:

- Recommends appropriate templates
- Suggests relevant editors
- Proposes common configurations

## See Also

- [CLI Commands](../../cli/index.md)
- [Getting Started](/getting-started/)
- [Initialize Command](../../cli/commands/init.md)
