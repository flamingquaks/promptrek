---
layout: default
title: Quick Start Guide
---

# Quick Start Guide


## Prerequisites

- Python 3.9 or higher
- Your favorite AI-enabled code editor (GitHub Copilot, Cursor, Continue, etc.)

## Installation

Install PrompTrek using pip:

```bash
pip install promptrek
```

Verify the installation:

```bash
promptrek --version
```

## Your First Universal Prompt

### 1. Initialize a New Project

Create a new universal prompt file using one of our templates:

```bash
# Basic initialization with pre-commit hooks (creates v3.0 format by default)
promptrek init --setup-hooks --output my-project.promptrek.yaml

# Use a specific template with hooks (v3.0 format)
promptrek init --template react --setup-hooks --output my-react-app.promptrek.yaml
promptrek init --template api --setup-hooks --output my-api.promptrek.yaml

# Create v1 format (legacy)
promptrek init --v1 --output legacy.promptrek.yaml

# Migrate existing v1 or v2.x file to v3.0
promptrek migrate old.promptrek.yaml -o new.promptrek.yaml
```

**💡 Tip:** The `--setup-hooks` flag automatically configures pre-commit hooks to validate your `.promptrek.yaml` files and prevent accidental commits of generated files. This ensures your team maintains clean version control!

**🔐 .gitignore Management:** When you run `promptrek init`, it automatically:
- Creates `.gitignore` if it doesn't exist
- Adds `.promptrek/` directory to `.gitignore` (contains user-specific config like `variables.promptrek.yaml` and `user-config.promptrek.yaml`)
- Adds 18 editor-specific file patterns to `.gitignore` (including `.github/copilot-instructions.md`, `.cursor/rules/*.mdc`, `.continue/rules/*.md`, etc.)

This prevents generated editor files from being committed to version control. You can disable this with `ignore_editor_files: false` in your config.

**Available templates:**
- `basic` - General project template
- `react` - React/TypeScript web application
- `api` - Node.js/Python API service

**Advanced Examples**: PrompTrek includes 8 production-ready examples for complex projects:
- `monorepo-nx` - NX/Turborepo monorepo with multiple apps
- `microservices-k8s` - Kubernetes microservices architecture
- `mobile-react-native` - Cross-platform mobile development
- `python-fastapi` - Modern async Python backend
- `fullstack-nextjs` - Next.js full-stack with App Router
- `rust-cli` - Rust command-line tools
- `golang-backend` - Go backend services
- `data-science-python` - ML/Data Science projects

See [examples on GitHub](https://github.com/flamingquaks/promptrek/tree/main/examples)

### 2. Customize Your Prompt

Edit the generated `.promptrek.yaml` file to match your project needs.

**Using v3.0 Format (Recommended - Default)**:

{% raw %}
```yaml
schema_version: "3.0.0"

metadata:
  title: "My Project Assistant"
  description: "AI assistant for my project"
  version: "1.0.0"
  author: "Your Name <your.email@example.com>"
  tags: [web, python, react]

content: |
  # {{{ PROJECT_NAME }}} Assistant

  ## Project Details
  **Project Type:** web_application
  **Technologies:** Python, JavaScript, React

  ## Development Guidelines

  ### General Principles
  - Write clean, readable code for {{{ PROJECT_NAME }}}
  - Follow existing patterns
  - Add comprehensive documentation
  - Contact {{{ AUTHOR_EMAIL }}} for questions

  ### Code Style
  - Use meaningful variable names
  - Add appropriate comments for complex logic
  - Follow language-specific best practices

  ## Code Examples

  ### Function Example
  ```python
  def hello_world():
      """Example function with docstring."""
      return "Hello, World!"
  `` `

variables:
  PROJECT_NAME: "my-project"
  AUTHOR_EMAIL: "your.email@example.com"
```
{% endraw %}

**Benefits of v3.0**:
- ✅ **No `targets` field** - Works with ALL editors automatically
- ✅ **Simpler format** - Just markdown content with clean plugin structure
- ✅ **Lossless sync** - Parse editor files back without data loss
- ✅ **Editor-friendly** - Matches how AI editors use markdown
- ✅ **Top-level plugins** - MCP servers, commands, agents, and hooks at the top level (cleaner than v2.x)

### 3. Validate Your Configuration

Before generating prompts, validate your configuration:

```bash
promptrek validate my-project.promptrek.yaml
```

Use `--strict` to treat warnings as errors:

```bash
promptrek validate my-project.promptrek.yaml --strict
```

**💡 Editor Integration:** Enable schema validation in your editor for instant feedback while editing `.promptrek.yaml` files. Add this comment at the top of your file:

```yaml
# yaml-language-server: $schema=https://promptrek.ai/schema/v3.0.0.json
schema_version: 3.0.0
# ... rest of your configuration
```

This provides autocompletion, inline documentation, and validation in editors like VS Code, IntelliJ IDEA, and others that support YAML language servers. See the [Schema Documentation](https://promptrek.ai/schema/) for more details.

### 4. Configure .gitignore (Optional)

If you have existing editor files already committed to git, you can clean them up:

```bash
# Add patterns to .gitignore and remove committed files from git
promptrek config-ignores --remove-cached

# Preview what would be done
promptrek config-ignores --dry-run

# Use specific config file
promptrek config-ignores --config my-project.promptrek.yaml
```

**What this command does:**
- Adds all editor file patterns to `.gitignore` (18 patterns)
- With `--remove-cached`: Runs `git rm --cached` on existing committed editor files
- Respects the `ignore_editor_files` setting in your config

You can control this behavior in your `.promptrek.yaml`:
```yaml
# Set to false to disable automatic .gitignore management
ignore_editor_files: false
```

### 5. (Optional) Create Local Variables File

For user-specific variables like names, emails, or API keys that should NOT be committed:

```yaml
# .promptrek/variables.promptrek.yaml (automatically gitignored via .promptrek/ directory)
AUTHOR_NAME: "Your Name"
AUTHOR_EMAIL: "your.email@example.com"
API_KEY: "your-secret-key"
```

**Note:** The `.promptrek/` directory is automatically added to `.gitignore` when you run `promptrek init`, so all files in this directory (including `variables.promptrek.yaml`) will not be committed to version control.

Variables from this file override defaults in your `.promptrek.yaml` file. See [Local Variables](user-guide.html#local-variables-file) for details.

### 6. Preview Generated Output (Optional)

Preview what will be generated without creating files:

```bash
# Preview for a specific editor
promptrek preview my-project.promptrek.yaml --editor copilot

# Preview with variable overrides
promptrek preview my-project.promptrek.yaml --editor cursor \
  -V PROJECT_NAME="MyApp" \
  -V AUTHOR="Team Lead"
```

The preview shows:
- Files that would be created
- Output from the generator
- Any warnings or notices
- No actual files are written

### 7. Generate Editor-Specific Prompts

Now generate prompts for your preferred editors:

```bash
# Generate for a specific editor
promptrek generate --editor copilot --input my-project.promptrek.yaml

# Generate for all configured editors
promptrek generate --all --input my-project.promptrek.yaml

# Generate with custom output directory
promptrek generate --all --input my-project.promptrek.yaml --output ./ai-config
```

## Generated Files Overview

PrompTrek generates sophisticated configuration files for each editor:

### GitHub Copilot
- `.github/copilot-instructions.md` - Repository-wide instructions
- `.github/instructions/*.instructions.md` - Path-specific instructions with YAML frontmatter
- `.github/prompts/*.prompt.md` - Reusable prompt templates
- **Bidirectional sync support**: Changes can be synced back to PrompTrek configuration

### Cursor
- `.cursor/rules/index.mdc` - Main project overview with metadata (Always rule)
- `.cursor/rules/*.mdc` - Category-specific rules with metadata (Auto Attached)
- `AGENTS.md` - Simple agent instructions
- `.cursorignore` - Enhanced exclusion patterns
- `.cursorindexingignore` - Intelligent indexing control
- **Metadata support**: Rules use `description`, `file_globs`, and `always_apply` fields

### Continue
- `.continue/config.yaml` - Main configuration with metadata and prompt references
- `.continue/mcpServers/*.yaml` - Individual MCP server YAML files
- `.continue/prompts/*.md` - Individual slash command prompts with frontmatter
- `.continue/rules/*.md` - Organized rule files by category and technology

### Kiro
- `.kiro/steering/*.md` - Steering files (product, tech, structure)
- `.kiro/specs/*.md` - Specification files (requirements, design, tasks)

### Cline
- `.clinerules/*.md` - Markdown-based rules configuration

### Claude Code
- `.claude/CLAUDE.md` - Main project context and guidelines
- `.mcp.json` - MCP server configurations (project root)
- `.claude/commands/*.md` - Custom slash commands
- `.claude/agents/*.md` - Autonomous agents
- `.claude/settings.local.json` - Event hooks with tool matchers
- **Bidirectional sync support**: Full lossless sync including plugins

### Windsurf
- `.windsurf/rules/*.md` - Organized markdown rule files by category and technology

### Amazon Q
- `.amazonq/rules/*.md` - Rules directory for coding guidelines
- `.amazonq/cli-agents/*.json` - CLI agents for code review, security, and testing
- **Bidirectional sync support**: Import existing Amazon Q configurations

### JetBrains AI
- `.assistant/rules/*.md` - Markdown rules for IDE assistance (prompts/MCP configured via IDE UI)

## Example Workflow

Here's a typical workflow using PrompTrek:

### 1. Project Setup
```bash
# Create a new React project prompt
promptrek init --template react --output react-app.promptrek.yaml

# Customize for your specific needs
# Edit react-app.promptrek.yaml...

# Validate the configuration
promptrek validate react-app.promptrek.yaml --strict
```

### 2. Generate Prompts
```bash
# Generate for GitHub Copilot
promptrek generate --editor copilot --input react-app.promptrek.yaml

# Team members can generate for their preferred editors
promptrek generate --editor cursor --input react-app.promptrek.yaml
promptrek generate --editor continue --input react-app.promptrek.yaml
```

### 3. Use in Your Editor
- **GitHub Copilot**: The generated instructions will be automatically picked up
- **Cursor**: Use the generated rules files for enhanced AI assistance
- **Continue**: Load the generated configuration in your Continue settings

## Pre-commit Integration (Recommended)

PrompTrek includes pre-commit hooks to ensure code quality and prevent accidental commits of generated files.

### Setup Options

**Option 1: During Initialization (Easiest)**
```bash
promptrek init --setup-hooks --output project.promptrek.yaml
# ✅ Creates .promptrek.yaml
# ✅ Configures .pre-commit-config.yaml
# ✅ Activates git hooks automatically
```

**Option 2: For Existing Projects**
```bash
pip install pre-commit
promptrek install-hooks --activate
```

**Option 3: Manual Setup**
```bash
promptrek install-hooks        # Configure only
pre-commit install            # Activate manually
```

### What the Hooks Do

1. **Validate PrompTrek files** - Automatically validates `.promptrek.yaml` files before commit
2. **Prevent generated files** - Blocks accidental commits of AI editor config files (`.cursor/`, `.claude/`, etc.)

See the [Pre-commit Integration Guide](user-guide/pre-commit.html) for detailed documentation.

## Common Commands Reference

### Initialization
```bash
promptrek init --output <filename>                          # Basic init
promptrek init --template <template> --output <file>        # From template
promptrek init --setup-hooks --output <file>                # With pre-commit hooks
```

### Pre-commit Hooks
```bash
promptrek install-hooks                    # Configure hooks
promptrek install-hooks --activate         # Configure and activate
promptrek check-generated <files>          # Check if files are generated
```

### Validation
```bash
promptrek validate <file>           # Basic validation
promptrek validate <file> --strict  # Strict validation
```

### Generation
```bash
promptrek generate --editor <editor> --input <file>     # Single editor
promptrek generate --all --input <file>                 # All editors
promptrek generate --all --input <file> --output <dir>  # Custom output
```

### Synchronization
```bash
promptrek sync --editor copilot --source-dir . --output <file>  # Sync editor changes back
promptrek sync --editor continue --source-dir . --dry-run       # Preview sync changes
```

### Information
```bash
promptrek list-editors              # Show supported editors
promptrek --help                    # General help
promptrek <command> --help          # Command-specific help
```

## Troubleshooting

### Common Issues

1. **Import errors**: Make sure you installed with `pip install promptrek`
2. **Command not found**: Check that `promptrek` is in your PATH
3. **Validation errors**: Use `promptrek validate --help` for validation options

### Getting Help

- Use `promptrek --help` for general help
- Use `promptrek <command> --help` for command-specific help
- Check the examples in your installation
- Enable verbose output with `--verbose` for debugging
- [Report issues]({{ site.issues_url }}) for bugs or feature requests

## Next Steps

- Learn about [Multi-Step Workflows](user-guide/workflows.html) for automated task sequences
- Read the [User Guide](user-guide.html) for comprehensive documentation
- Explore [Advanced Features](user-guide.html#advanced-features) like variables and conditionals
- Learn about [Editor-Specific Features](user-guide.html#editor-specific-features)
- [Contribute](contributing.html) to the project

Ready to dive deeper? Check out our [comprehensive User Guide](user-guide.html)!
