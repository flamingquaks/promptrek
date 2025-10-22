# Development Setup and Getting Started

This guide explains how to set up and use the PrompTrek CLI tool.

## Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager) OR uv (recommended)

### Install from Source with uv (Recommended)

1. Install uv if you haven't already:
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

2. Clone the repository:
```bash
git clone https://github.com/flamingquaks/promptrek.git
cd promptrek
```

3. Set up development environment:
```bash
uv sync --group dev
```

4. Verify installation:
```bash
uv run promptrek --help
```

### Install from Source with pip (Traditional)

1. Clone the repository:
```bash
git clone https://github.com/flamingquaks/promptrek.git
cd promptrek
```

2. Install in development mode:
```bash
pip install -e .
```

3. Verify installation:
```bash
promptrek --help
```

## Quick Start

### 1. Initialize a New Project

Create a new universal prompt file:

```bash
# Basic initialization
promptrek init --output my-project.promptrek.yaml

# Use a template
promptrek init --template react --output my-react-app.promptrek.yaml
promptrek init --template api --output my-api.promptrek.yaml
```

Available templates:
- `basic` - General project template
- `react` - React/TypeScript web application
- `api` - Node.js/Python API service

**Note:** When you run `promptrek init`, it automatically:
- Creates `.gitignore` if it doesn't exist
- Adds `.promptrek/` directory to `.gitignore` (contains user-specific config like `variables.promptrek.yaml`)
- Adds all editor-specific file patterns to `.gitignore` (18 patterns including `.github/copilot-instructions.md`, `.cursor/rules/*.mdc`, etc.)

### 2. Configure .gitignore Management (Optional)

If you have existing editor files already committed to git, clean them up:

```bash
# Add patterns to .gitignore and remove committed files from git
promptrek config-ignores --remove-cached

# Preview what would be done
promptrek config-ignores --dry-run

# Use specific config file
promptrek config-ignores --config custom.promptrek.yaml
```

You can also control this behavior in your `.promptrek.yaml`:
```yaml
# Set to false to disable automatic .gitignore management
ignore_editor_files: false
```

### 3. Validate Your Configuration

```bash
promptrek validate my-project.promptrek.yaml
```

Use `--strict` to treat warnings as errors:
```bash
promptrek validate my-project.promptrek.yaml --strict
```

### 4. Generate Editor-Specific Prompts

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

Preview what would be generated (dry run):
```bash
promptrek generate my-project.promptrek.yaml --editor copilot --dry-run
```

### 5. Preview Generated Output

Preview what will be generated without creating files:
```bash
# Preview for a specific editor
promptrek preview my-project.promptrek.yaml --editor copilot

# Preview with variable overrides
promptrek preview my-project.promptrek.yaml --editor cursor \
  -V PROJECT_NAME="MyApp" \
  -V AUTHOR="Team Lead"
```

The preview command shows:
- Files that would be created
- Output from the generator
- Any warnings or notices
- No actual files are written

### 5. List Supported Editors

```bash
promptrek list-editors
```

## Generated Files

The tool generates sophisticated configuration systems for each editor:

- **GitHub Copilot**: 
  - `.github/copilot-instructions.md` (repository-wide instructions)
  - `.github/instructions/*.instructions.md` (path-specific instructions with YAML frontmatter)
  
- **Cursor**: 
  - `.cursor/rules/*.mdc` (modern rules with YAML frontmatter and glob patterns)
  - `AGENTS.md` (simple agent instructions)
  - `.cursorignore` (files to exclude from analysis)
  - `.cursorindexingignore` (indexing control)
  
- **Continue**: 
  - `config.yaml` (main configuration in modern YAML format)
  - `.continue/rules/*.md` (organized rule files by category and technology)
  
- **Kiro**: 
  - `.kiro/steering/*.md` (steering files: product.md, tech.md, structure.md)
  - `.kiro/specs/*.md` (spec files: requirements.md, design.md, tasks.md)
  
- **Cline**: `.clinerules` (markdown-based rules)

## Example Workflow

```bash
# 1. Create a new React project configuration
promptrek init --template react --output my-react-app.promptrek.yaml

# 2. Edit the file to customize your project
# (Edit my-react-app.promptrek.yaml with your favorite editor)

# 3. Validate the configuration
promptrek validate my-react-app.promptrek.yaml

# 4. Generate prompts for all editors
promptrek generate my-react-app.promptrek.yaml --all

# 5. Your AI editor prompts are ready!
ls .github/copilot-instructions.md
ls .cursor/rules/
ls config.yaml .continue/rules/
```

## Real-World Examples

PrompTrek includes comprehensive example configurations for various project types:

### Basic Examples
- **React TypeScript** ([examples/basic/react-typescript.promptrek.yaml](./examples/basic/react-typescript.promptrek.yaml))
- **Node.js API** ([examples/basic/node-api.promptrek.yaml](./examples/basic/node-api.promptrek.yaml))

### Advanced Examples
The `examples/advanced/` directory contains production-ready configurations:

- **[monorepo-nx.promptrek.yaml](./examples/advanced/monorepo-nx.promptrek.yaml)** - NX/Turborepo monorepo with multiple apps and libraries
- **[microservices-k8s.promptrek.yaml](./examples/advanced/microservices-k8s.promptrek.yaml)** - Kubernetes microservices architecture
- **[mobile-react-native.promptrek.yaml](./examples/advanced/mobile-react-native.promptrek.yaml)** - Cross-platform mobile development
- **[python-fastapi.promptrek.yaml](./examples/advanced/python-fastapi.promptrek.yaml)** - Modern async Python backend
- **[fullstack-nextjs.promptrek.yaml](./examples/advanced/fullstack-nextjs.promptrek.yaml)** - Next.js full-stack with App Router
- **[rust-cli.promptrek.yaml](./examples/advanced/rust-cli.promptrek.yaml)** - Rust command-line tools
- **[golang-backend.promptrek.yaml](./examples/advanced/golang-backend.promptrek.yaml)** - Go backend services
- **[data-science-python.promptrek.yaml](./examples/advanced/data-science-python.promptrek.yaml)** - ML/Data Science projects

Each example includes:
- Comprehensive instructions by category
- Architecture and testing guidelines
- Security and performance best practices
- Real-world code examples
- Technology-specific workflows

Use these as starting points for your own projects:
```bash
# Copy an example to start your project
cp examples/advanced/fullstack-nextjs.promptrek.yaml my-project.promptrek.yaml

# Customize and generate
promptrek generate my-project.promptrek.yaml --all
```

## Universal Prompt Format (UPF)

The `.promptrek.yaml` files use a standardized format. Here's a minimal v3.0 example (recommended):

```yaml
schema_version: "3.0.0"

metadata:
  title: "My Project Assistant"
  description: "AI assistant for my project"
  version: "1.0.0"
  author: "Your Name <your.email@example.com>"
  tags: [python, javascript, react]

content: |
  # My Project Assistant

  ## Project Overview
  Web application built with Python and React.

  ## Development Guidelines

  ### General Principles
  - Write clean, readable code
  - Follow existing patterns

  ### Code Style
  - Use meaningful variable names
  - Add appropriate comments

  ### Example Function
  ```python
  def hello_world():
      return "Hello, World!"
  ```

variables:
  PROJECT_NAME: "my-project"
```

For complete examples using v3.0 schema, see the [`examples/`](./examples/) directory.

## Development

### Running Tests

#### Using uv (Recommended)

```bash
# Install development dependencies
uv sync --group dev

# Run unit tests
uv run python -m pytest tests/unit/

# Run integration tests  
uv run python -m pytest tests/integration/

# Run all tests with coverage
make test
# or manually: uv run python -m pytest --cov=src/promptrek
```

#### Using pip (Traditional)

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run unit tests
pytest tests/unit/

# Run integration tests  
pytest tests/integration/

# Run all tests with coverage
pytest --cov=src/promptrek
```

### Code Quality

#### Using uv (Recommended)

```bash
# Format code
make format
# or manually: uv run black src/ tests/

# Sort imports
uv run isort src/ tests/

# Type checking
make typecheck
# or manually: uv run mypy src/

# Linting
make lint
# or manually: uv run flake8 src/ tests/
```

#### Using pip (Traditional)

```bash
# Format code
black src/ tests/

# Sort imports
isort src/ tests/

# Type checking
mypy src/

# Linting
flake8 src/ tests/
```

### Development Workflows

For comprehensive development workflows using uv, see [UV Workflows Guide](./docs/UV_WORKFLOWS.md).

## Troubleshooting

### Common Issues

1. **Import errors**: Make sure you installed with `pip install -e .`
2. **Command not found**: Check that `promptrek` is in your PATH
3. **Validation errors**: Use `promptrek validate --help` for validation options

### Getting Help

- Use `promptrek --help` for general help
- Use `promptrek <command> --help` for command-specific help
- Check the examples in `examples/basic/` directory
- Enable verbose output with `--verbose` for debugging

## What's Implemented

✅ **Core Features**:
- Universal Prompt Format (UPF) parsing and validation
- CLI interface with init, validate, generate commands
- Advanced template system with technology detection
- **GitHub Copilot**: Path-specific instructions with YAML frontmatter + agent files
- **Cursor**: Modern `.cursor/rules/*.mdc` system with technology-specific rules + ignore files
- **Continue**: Modern `config.yaml` + advanced `.continue/rules/` system
- **Kiro**: Comprehensive steering and specs system
- **Cline**: Modern `.clinerules` configuration
- Variable substitution and conditional instructions
- Technology-specific rule generation
- Advanced glob pattern matching
- Ignore file systems for optimal AI editor performance

✅ **Advanced Features**:
- YAML frontmatter support for precise file targeting
- Dynamic rule generation based on project technologies (TypeScript, React, Python, etc.)
- Comprehensive ignore patterns (.cursorignore, .cursorindexingignore)
- Agent-specific instruction files
- Path-specific configurations with glob patterns
- Technology detection and best practices integration

