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
# Basic initialization
promptrek init --output my-project.promptrek.yaml

# Use a specific template
promptrek init --template react --output my-react-app.promptrek.yaml
promptrek init --template api --output my-api.promptrek.yaml
```

**Available templates:**
- `basic` - General project template
- `react` - React/TypeScript web application
- `api` - Node.js/Python API service

### 2. Customize Your Prompt

Edit the generated `.promptrek.yaml` file to match your project needs:

```yaml
schema_version: "1.0.0"

metadata:
  title: "My Project Assistant"
  description: "AI assistant for my project"
  version: "1.0.0"
  author: "Your Name <your.email@example.com>"

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

### 4. Generate Editor-Specific Prompts

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
- `AGENTS.md`, `CLAUDE.md`, `GEMINI.md` - Agent-specific instructions

### Cursor (Modernized 2025)
- `.cursor/rules/index.mdc` - Main project overview (Always rule)
- `.cursor/rules/*.mdc` - Category-specific rules (Auto Attached)
- `AGENTS.md` - Simple agent instructions
- `.cursorignore` - Enhanced exclusion patterns
- `.cursorindexingignore` - Intelligent indexing control

### Continue
- `config.yaml` - Main configuration in modern YAML format
- `.continue/rules/*.md` - Organized rule files by category and technology

### Other Editors
- **Amazon Q**: `.amazonq/context.md`, `.amazonq/comments.template`
- **JetBrains AI**: `.idea/ai-assistant.xml`, `.jetbrains/config.json`
- **Kiro**: `.kiro/steering/*.md`, `.kiro/specs/*/requirements.md`, `.kiro/hooks/*.md`, `.prompts/*.md`
- **Cline**: `.clinerules`

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

## Common Commands Reference

### Initialization
```bash
promptrek init --output <filename>                    # Basic init
promptrek init --template <template> --output <file>  # From template
```

### Validation
```bash
promptrek validate <file>           # Basic validation
promptrek validate <file> --strict  # Strict validation
```

### Generation
```bash
promptrek generate --editor <editor> --input <file>   # Single editor
promptrek generate --all --input <file>               # All editors
promptrek generate --all --input <file> --output <dir> # Custom output
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