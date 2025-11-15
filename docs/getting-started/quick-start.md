# Quick Start Guide

This guide will get you up and running with PrompTrek in just a few minutes.

## Installation

### Prerequisites

- Python 3.9 or higher
- pip or [uv](https://github.com/astral-sh/uv) (recommended)

### Install from Source with uv (Recommended)

```bash
# Install uv if you haven't already
curl -LsSf https://astral.sh/uv/install.sh | sh

# Clone the repository
git clone https://github.com/flamingquaks/promptrek.git
cd promptrek

# Set up development environment
uv sync
```

### Install from Source with pip

```bash
# Clone the repository
git clone https://github.com/flamingquaks/promptrek.git
cd promptrek

# Install in development mode
pip install -e .
```

## Your First PrompTrek Configuration

### 1. Initialize a New Project

Create a new universal prompt file using the interactive wizard:

```bash
# Interactive mode
promptrek

# Or use a template directly
promptrek init --template react --output my-project.promptrek.yaml
```

Available templates:
- `basic` - General project template
- `react` - React/TypeScript web application
- `api` - Node.js/Python API service

### 2. Validate Your Configuration

```bash
promptrek validate my-project.promptrek.yaml
```

Use `--strict` to treat warnings as errors:

```bash
promptrek validate my-project.promptrek.yaml --strict
```

### 3. Generate Editor-Specific Prompts

Generate for a specific editor:

```bash
promptrek generate my-project.promptrek.yaml --editor copilot
promptrek generate my-project.promptrek.yaml --editor cursor
promptrek generate my-project.promptrek.yaml --editor continue
```

Generate for all target editors:

```bash
promptrek generate my-project.promptrek.yaml --all
```

### 4. Use in Your Editor

The generated files are automatically placed in the correct locations:

- **GitHub Copilot**: `.github/copilot-instructions.md`
- **Cursor**: `.cursor/rules/index.mdc`
- **Continue**: `.continue/rules/*.md`
- **Claude Code**: `.claude/CLAUDE.md`
- And more...

## Example Workflow

Here's a complete workflow for setting up a React project:

```bash
# 1. Create a new React project configuration
promptrek init --template react --output my-react-app.promptrek.yaml

# 2. Validate the configuration
promptrek validate my-react-app.promptrek.yaml

# 3. Generate prompts for all editors
promptrek generate my-react-app.promptrek.yaml --all

# 4. Your AI editor prompts are ready!
ls .github/copilot-instructions.md
ls .cursor/rules/
ls .continue/rules/
```

## Basic Configuration Example

Here's a minimal `.promptrek.yaml` file using schema v3.1.0:

```yaml
schema_version: "3.1.0"

metadata:
  title: "My Project Assistant"
  description: "AI assistant for React TypeScript project"
  tags: [react, typescript, web]

content: |
  # My Project Assistant

  ## Project Details
  **Technologies:** React, TypeScript, Node.js

  ## Development Guidelines

  ### General Principles
  - Use TypeScript for all new files
  - Follow React functional component patterns
  - Write comprehensive tests

  ### Code Style
  - Use functional components with hooks
  - Prefer const over let
  - Use meaningful variable names

variables:
  PROJECT_NAME: "my-react-app"
```

## Next Steps

- Learn about [advanced features](../user-guide/advanced/variables.md) like variable substitution
- Explore [editor adapters](../user-guide/adapters/index.md) to understand each editor's capabilities
- Check out [examples](../examples/index.md) for real-world configurations
- Set up [pre-commit hooks](../user-guide/workflows/pre-commit.md) for automatic validation

## Interactive CLI Mode

New in v0.4.0! Launch the interactive wizard:

```bash
promptrek
```

The wizard guides you through:
- 🚀 Project initialization
- ⚙️ Editor configuration
- 🔌 Plugin management
- 🔄 Schema migration
- 🔍 Validation & sync

## Common Issues

### Command Not Found

If `promptrek` is not found, ensure it's in your PATH:

```bash
# With uv
uv run promptrek --help

# Or activate the virtual environment
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate     # Windows
promptrek --help
```

### Validation Errors

Use verbose mode to see detailed error messages:

```bash
promptrek validate my-project.promptrek.yaml --verbose
```

## Getting Help

- Use `promptrek --help` for general help
- Use `promptrek <command> --help` for command-specific help
- Check the [FAQ](../reference/faq.md)
- Visit the [troubleshooting guide](../reference/troubleshooting.md)
- Open an [issue on GitHub](https://github.com/flamingquaks/promptrek/issues)
