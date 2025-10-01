---
layout: default
title: Quick Start Guide
---

# Quick Start Guide

Get up and running with PrompTrek in just a few minutes!

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
# Basic initialization with pre-commit hooks (recommended)
promptrek init --setup-hooks --output my-project.promptrek.yaml

# Use a specific template with hooks
promptrek init --template react --setup-hooks --output my-react-app.promptrek.yaml
promptrek init --template api --setup-hooks --output my-api.promptrek.yaml

# Without hooks setup (manual)
promptrek init --output my-project.promptrek.yaml
```

**💡 Tip:** The `--setup-hooks` flag automatically configures pre-commit hooks to validate your `.promptrek.yaml` files and prevent accidental commits of generated files. This ensures your team maintains clean version control!

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

Edit the generated `.promptrek.yaml` file to match your project needs:

```yaml
schema_version: "1.0.0"

metadata:
  title: "My Project Assistant"
  description: "AI assistant for my project"
  # Optional fields:
  # version: "1.0.0"
  # author: "Your Name <your.email@example.com>"

# Optional - defaults to all supported editors if not specified
targets: ["copilot", "cursor", "continue"]

context:
  project_type: "web_application"
  technologies: ["python", "javascript", "react"]

instructions:
  general:
    - "Write clean, readable code"
    - "Follow existing patterns"
  code_style:
    - "Use meaningful variable names"
    - "Add appropriate comments"

examples:
  function: |
    ```python
    def hello_world():
        return "Hello, World!"
    ```
```

### 3. Validate Your Configuration

Before generating prompts, validate your configuration:

```bash
promptrek validate my-project.promptrek.yaml
```

Use `--strict` to treat warnings as errors:

```bash
promptrek validate my-project.promptrek.yaml --strict
```

### 4. (Optional) Create Local Variables File

For user-specific variables like names, emails, or API keys that should NOT be committed:

```yaml
# variables.promptrek.yaml (automatically added to .gitignore by init)
AUTHOR_NAME: "Your Name"
AUTHOR_EMAIL: "your.email@example.com"
API_KEY: "your-secret-key"
```

Variables from this file override defaults in your `.promptrek.yaml` file. See [Local Variables](user-guide.html#local-variables-file) for details.

### 5. Preview Generated Output (Optional)

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

### 6. Generate Editor-Specific Prompts

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
- **Headless agent instructions**: Autonomous regeneration capability for background tasks

### Cursor
- `.cursor/rules/index.mdc` - Main project overview (Always rule)
- `.cursor/rules/*.mdc` - Category-specific rules (Auto Attached)
- `AGENTS.md` - Simple agent instructions
- `.cursorignore` - Enhanced exclusion patterns
- `.cursorindexingignore` - Intelligent indexing control

### Continue
- `config.yaml` - Main configuration in modern YAML format
- `.continue/rules/*.md` - Organized rule files by category and technology

### Kiro
- `.kiro/steering/*.md` - Steering files (product, tech, structure)
- `.kiro/specs/*.md` - Specification files (requirements, design, tasks)

### Cline
- `.clinerules/*.md` - Markdown-based rules configuration

### Claude Code
- `.claude/context.md` - Rich context format with project information

### Codeium
- `.codeium/context.json` - JSON context with team patterns
- `.codeiumrc` - Configuration file

### Tabnine
- Global configuration only (configured through admin panel)

### Amazon Q
- `.amazonq/context.md` - Context information
- `.amazonq/comments.template` - Comment-based templates

### JetBrains AI
- `.idea/ai-assistant.xml` - IDE-integrated configuration
- `.jetbrains/config.json` - JSON configuration

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

See the [Pre-commit User Guide](https://github.com/flamingquaks/promptrek/blob/main/docs/PRE_COMMIT_USER_GUIDE.md) for detailed documentation.

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
promptrek generate --editor copilot --headless <file>   # Generate with headless instructions
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

- Read the [User Guide](user-guide.html) for comprehensive documentation
- Explore [Advanced Features](user-guide.html#advanced-features) like variables and conditionals
- Learn about [Editor-Specific Features](user-guide.html#editor-specific-features)
- [Contribute](contributing.html) to the project

Ready to dive deeper? Check out our [comprehensive User Guide](user-guide.html)!
