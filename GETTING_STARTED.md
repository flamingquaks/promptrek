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

Preview what would be generated (dry run):
```bash
promptrek generate my-project.promptrek.yaml --editor copilot --dry-run
```

### 4. List Supported Editors

```bash
promptrek list-editors
```

## Generated Files

The tool generates sophisticated configuration systems for each editor:

- **GitHub Copilot**: 
  - `.github/copilot-instructions.md` (repository-wide instructions)
  - `.github/instructions/*.instructions.md` (path-specific instructions with YAML frontmatter)
  - `AGENTS.md`, `CLAUDE.md`, `GEMINI.md` (agent-specific instructions)
  
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

## Universal Prompt Format (UPF)

The `.promptrek.yaml` files use a standardized format. Here's a minimal example:

```yaml
schema_version: "1.0.0"

metadata:
  title: "My Project Assistant"
  description: "AI assistant for my project"
  version: "1.0.0"
  author: "Your Name <your.email@example.com>"
  created: "2024-01-01"
  updated: "2024-01-01"

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

## Contributing

This project is in active development. See the planning documents in `docs/` for roadmap and architecture details.
