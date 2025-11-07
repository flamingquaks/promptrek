---
layout: default
title: Quick Start Guide
---

# Quick Start Guide

<div style="background: #f0f9ff; border-left: 4px solid #0ea5e9; padding: 1rem; margin-bottom: 2rem;">
  <strong>📦 Already have editor prompts and rules?</strong> Jump to <a href="#working-with-existing-projects">Working with Existing Projects</a> to learn how to import and consolidate them with PrompTrek.
</div>

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

## Interactive CLI Wizard (New!)

**New in v0.4.0**: PrompTrek now includes an interactive CLI wizard that guides you through all common workflows!

### Launch Interactive Mode

Simply run `promptrek` without any arguments:

```bash
promptrek
```

You'll see a beautiful ASCII banner and a menu-driven interface:

```
 ____                       _____         _
|  _ \ _ __ ___  _ __ ___  |_   _| __ ___| | __
| |_) | '__/ _ \| '_ ` _ \   | || '__/ _ \ |/ /
|  __/| | | (_) | | | | | |  | || | |  __/   <
|_|   |_|  \___/|_| |_| |_|  |_||_|  \___|_|\_\

Universal AI Editor Prompt Management (v0.4.0)

? What would you like to do?
  ❯ 🚀 Initialize new project
    ⚙️  Generate editor configurations
    🔌 Configure plugins (MCP servers, commands, agents)
    🔄 Migrate schema version
    🔍 Validate configuration
    📤 Sync from editor files
    ❓ Help & Documentation
    👋 Exit
```

The wizard will guide you through:
- **Project initialization** with schema selection and pre-commit hooks
- **Editor configuration** with multi-select and variable overrides
- **Plugin management** for MCP servers, commands, and agents
- **Schema migration** with backup options
- **Validation and sync** workflows

**Benefits:**
- No need to memorize command syntax
- Step-by-step guidance reduces errors
- Perfect for beginners and experienced users alike
- All traditional commands still work as before

### Traditional CLI Mode

If you prefer traditional commands or are in a CI/CD environment, all commands continue to work:

```bash
# Initialize project (traditional way)
promptrek init --setup-hooks --output project.promptrek.yaml

# Generate configurations
promptrek generate --editor cursor

# Force interactive mode
promptrek --interactive
```

## Your First Universal Prompt

### 1. Initialize a New Project

Create a new universal prompt file using one of our templates:

```bash
# Basic initialization with pre-commit hooks (creates schema v3.1 format by default)
promptrek init --setup-hooks --output my-project.promptrek.yaml

# Use a specific template with hooks (schema v3.1 format)
promptrek init --template react --setup-hooks --output my-react-app.promptrek.yaml
promptrek init --template api --setup-hooks --output my-api.promptrek.yaml

# Create schema v1 format (legacy)
promptrek init --v1 --output legacy.promptrek.yaml

# Migrate existing schema v1 or v2.x file to v3.1
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

**Using Schema v3.1 Format (Latest Stable - Default)**:

> **Note on Versioning**: Schema versions (v1.x, v2.x, v3.x) define the configuration file format specified in the `schema_version` field. These are independent of the PrompTrek application version.

{% raw %}
```yaml
schema_version: "3.1.0"

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

**Benefits of Schema v3.1**:
- ✅ **No `targets` field** - Works with ALL editors automatically
- ✅ **Simpler format** - Just markdown content with clean plugin structure
- ✅ **Lossless sync** - Parse editor files back without data loss
- ✅ **Editor-friendly** - Matches how AI editors use markdown
- ✅ **Top-level plugins** - MCP servers, commands, agents, and hooks at the top level (cleaner than schema v2.x)
- ✅ **Refined agent model** - Consistent `prompt` field instead of `system_prompt`

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
# yaml-language-server: $schema=https://promptrek.ai/schema/v3.1.0.json
schema_version: 3.1.0
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

### 5. (Optional) Use Dynamic Variables

PrompTrek supports powerful dynamic variables to make your prompts adaptive:

**Built-in Variables** (automatically available, all can be overridden):
- `CURRENT_DATE` - Current date (YYYY-MM-DD)
- `CURRENT_TIME` - Current time (HH:MM:SS)
- `CURRENT_DATETIME` - ISO 8601 datetime
- `CURRENT_YEAR`, `CURRENT_MONTH`, `CURRENT_DAY` - Date components
- `PROJECT_NAME` - Extracted from git remote URL (supports HTTPS/SSH formats), falls back to directory name
- `PROJECT_ROOT` - Absolute path to project
- `GIT_BRANCH`, `GIT_COMMIT_SHORT` - Git info (if in git repo)

💡 **Tip:** You can override any built-in variable by defining it in your variables file or via CLI.

**Command-based Variables** (execute shell commands):

```yaml
# .promptrek/variables.promptrek.yaml (automatically gitignored via .promptrek/ directory)
# Static user variables
AUTHOR_NAME: "Your Name"
AUTHOR_EMAIL: "your.email@example.com"

# Override built-in PROJECT_NAME (optional)
PROJECT_NAME: "MyCustomProjectName"

# Dynamic command-based variables
GIT_BRANCH:
  type: command
  value: git rev-parse --abbrev-ref HEAD
  cache: false

GIT_COMMIT:
  type: command
  value: git rev-parse --short HEAD
  cache: true

CURRENT_USER:
  type: command
  value: whoami
  cache: true
```

Add `allow_commands: true` to your `.promptrek.yaml` to enable command-based variables.

**CLI Overrides** (highest priority):

```bash
# Override variables for specific generations
promptrek generate -e claude -V ENVIRONMENT=staging
promptrek generate --all -V PROJECT_NAME=MyApp -V DEBUG=true
```

**Variable Priority Order:**
1. CLI flags (`-V`) - highest priority
2. File-based (`.promptrek/variables.promptrek.yaml`)
3. Inline (`variables:` in your `.promptrek.yaml`)
4. Built-in (`CURRENT_*`, `PROJECT_*`, `GIT_*`) - lowest priority

**Note:** The `.promptrek/` directory is automatically added to `.gitignore` when you run `promptrek init`, so all files in this directory (including `variables.promptrek.yaml`) will not be committed to version control.

See [Variable Substitution](user-guide/advanced-features.html#variable-substitution) for complete documentation.

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
- **Sync support**: Import existing Copilot files or sync generated files back to PrompTrek

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
- **Sync support**: Lossless round-trip including all plugins (MCP servers, commands, agents, hooks)

### Windsurf
- `.windsurf/rules/*.md` - Organized markdown rule files by category and technology

### Amazon Q
- `.amazonq/rules/*.md` - Rules directory for coding guidelines
- `.amazonq/cli-agents/*.json` - CLI agents for code review, security, and testing
- **Sync support**: Import existing Amazon Q configurations or sync generated files back

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

## Spec-Driven Development Workflow

PrompTrek includes a complete spec-driven development system with eight specialized commands that take you from project values to production code. This workflow is inspired by GitHub's Spec-Kit methodology and is automatically available in all supported editors after generation.

### The 8-Command Workflow

1. **Constitution** (`/promptrek.spec.constitution`) - Define project-wide values and working agreements
2. **Specify** (`/promptrek.spec.specify <topic>`) - Create structured feature specifications
3. **Plan** (`/promptrek.spec.plan <topic>`) - Generate technical implementation plans
4. **Tasks** (`/promptrek.spec.tasks <topic>`) - Break plans into actionable checklists
5. **Implement** (`/promptrek.spec.implement <topic>`) - Generate production-ready code
6. **Analyze** (`/promptrek.spec.analyze [topic]`) - Review consistency across artifacts
7. **History** (`/promptrek.spec.history [topic]`) - Track changes and evolution
8. **Feedback** (`/promptrek.spec.feedback <topic>`) - Provide structured PR reviews

### Quick Example

```bash
# After running promptrek generate, use these commands in your AI editor:

# 1. Establish project values (once per project)
/promptrek.spec.constitution

# 2. Create a feature specification
/promptrek.spec.specify user-authentication

# 3. Generate implementation plan
/promptrek.spec.plan user-authentication

# 4. Break down into tasks
/promptrek.spec.tasks user-authentication

# 5. Check consistency before coding
/promptrek.spec.analyze user-authentication

# 6. Implement specific tasks
/promptrek.spec.implement JWT token generation

# 7. Track changes
/promptrek.spec.history user-authentication

# 8. Review implementation
/promptrek.spec.feedback auth PR #42
```

All spec artifacts are stored in `promptrek/specs/` (committed to git) with a registry at `promptrek/specs.yaml`. The constitution lives at `promptrek/constitution.md`.

**📋 Learn More:** See the complete [Spec-Driven Development Guide](user-guide/spec-driven-development.html) for detailed examples, best practices, and command reference.

## Working with Existing Projects

Already have editor prompts and rules? PrompTrek makes it easy to consolidate them into a universal format and maintain them across editors.

### Scenario 1: Import Existing Editor Configurations

If you already have `.github/copilot-instructions.md`, `.cursor/rules/*.mdc`, `.claude/CLAUDE.md`, or other editor files, you can sync them into PrompTrek format:

```bash
# Sync from GitHub Copilot
promptrek sync --editor copilot # By default this creates project.promptrek.yaml

# Sync from Cursor
promptrek sync --editor cursor --output project.promptrek.yaml # Specifying output allows you to save to a custom file name

# Sync from Claude Code
promptrek sync --editor claude 

# Sync from Continue
promptrek sync --editor continue 

# Preview what would be synced (dry run)
promptrek sync --editor copilot --dry-run
```

**Supported editors for sync**: GitHub Copilot, Cursor, Continue, Windsurf, Kiro, Cline, Claude Code, Amazon Q, JetBrains AI

This creates a `project.promptrek.yaml` file from your existing editor configuration. You can then:
1. Edit this file to refine your prompts
2. Generate for other editors: `promptrek generate --all`
3. Keep everything in sync going forward

### Scenario 2: Migrate and Clean Up

If you want to migrate from editor-specific files to PrompTrek as your single source of truth:

```bash
# Step 1: Sync your existing configuration
promptrek sync --editor copilot --source-dir . --output project.promptrek.yaml

# Step 2: Validate the imported configuration
promptrek validate project.promptrek.yaml

# Step 3: Generate for all editors (optional - if your team uses multiple editors)
promptrek generate --all --input project.promptrek.yaml

# Step 4: Remove old editor files from git and add to .gitignore
promptrek config-ignores --remove-cached

# Step 5: Commit the PrompTrek configuration
git add project.promptrek.yaml .gitignore
git commit -m "chore: migrate to PrompTrek universal prompt format"
```

**Benefits of this approach**:
- ✅ Single source of truth for all prompts
- ✅ Works with any editor your team prefers
- ✅ Version control only the source (`.promptrek.yaml`)
- ✅ Auto-generated files are gitignored
- ✅ Easy to switch editors or add new ones

### Scenario 3: Add PrompTrek to Project with Committed Editor Files

If your project already has editor files committed to git, here's the cleanest migration path:

```bash
# Step 1: Initialize PrompTrek configuration
promptrek init --setup-hooks --output project.promptrek.yaml

# Step 2: Import your existing editor configuration
promptrek sync --editor copilot --source-dir . --output imported.promptrek.yaml

# Step 3: Merge the imported content into your project.promptrek.yaml
# (Edit project.promptrek.yaml and copy the content from imported.promptrek.yaml)

# Step 4: Clean up committed editor files and update .gitignore
promptrek config-ignores --remove-cached

# Step 5: Regenerate files from your PrompTrek source
promptrek generate --all --input project.promptrek.yaml

# Step 6: Commit the new setup
git add project.promptrek.yaml .gitignore .pre-commit-config.yaml
git commit -m "chore: migrate to PrompTrek with pre-commit hooks"
```

**What happens**:
- Old editor files are removed from git tracking (`git rm --cached`)
- `.gitignore` is updated to exclude editor files
- PrompTrek becomes the source of truth
- Pre-commit hooks ensure no one accidentally commits editor files again
- Team members can generate for their preferred editor

### Scenario 4: Keep Existing Editor Files (No Migration)

If you want to use PrompTrek alongside your existing editor files:

```bash
# Step 1: Initialize with --no-gitignore to preserve existing files
promptrek init --output project.promptrek.yaml

# Step 2: Configure to not ignore editor files
# Edit project.promptrek.yaml and add:
# ignore_editor_files: false

# Step 3: Generate without conflicts
promptrek generate --all --input project.promptrek.yaml --output ./promptrek-generated
```

This keeps your existing workflow intact while experimenting with PrompTrek.

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

### Deprecated Commands
```bash
# ⚠️ DEPRECATED: Use 'promptrek generate --all' instead
# promptrek agents                               # Legacy agent generation (schema v3.1.0+)
```

**Note**: The `agents` command is deprecated as of schema v3.1.0 and will be removed in a future version. All functionality is available through `promptrek generate --all`.

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
