# Development Setup and Getting Started

This guide explains how to set up and use the Agent Prompt Mapper CLI tool.

## Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### Install from Source

1. Clone the repository:
```bash
git clone https://github.com/flamingquaks/agent-prompt-mapper.git
cd agent-prompt-mapper
```

2. Install in development mode:
```bash
pip install -e .
```

3. Verify installation:
```bash
apm --help
```

## Quick Start

### 1. Initialize a New Project

Create a new universal prompt file:

```bash
# Basic initialization
apm init --output my-project.apm.yaml

# Use a template
apm init --template react --output my-react-app.apm.yaml
apm init --template api --output my-api.apm.yaml
```

Available templates:
- `basic` - General project template
- `react` - React/TypeScript web application
- `api` - Node.js/Python API service

### 2. Validate Your Configuration

```bash
apm validate my-project.apm.yaml
```

Use `--strict` to treat warnings as errors:
```bash
apm validate my-project.apm.yaml --strict
```

### 3. Generate Editor-Specific Prompts

Generate for a specific editor:
```bash
apm generate my-project.apm.yaml --editor copilot
apm generate my-project.apm.yaml --editor cursor
apm generate my-project.apm.yaml --editor continue
```

Generate for all target editors:
```bash
apm generate my-project.apm.yaml --all
```

Preview what would be generated (dry run):
```bash
apm generate my-project.apm.yaml --editor copilot --dry-run
```

### 4. List Supported Editors

```bash
apm list-editors
```

## Generated Files

The tool generates the following files for each editor:

- **GitHub Copilot**: `.github/copilot-instructions.md`
- **Cursor**: `.cursorrules`
- **Continue**: `.continue/config.json`

## Example Workflow

```bash
# 1. Create a new React project configuration
apm init --template react --output my-react-app.apm.yaml

# 2. Edit the file to customize your project
# (Edit my-react-app.apm.yaml with your favorite editor)

# 3. Validate the configuration
apm validate my-react-app.apm.yaml

# 4. Generate prompts for all editors
apm generate my-react-app.apm.yaml --all

# 5. Your AI editor prompts are ready!
ls .github/copilot-instructions.md
ls .cursorrules
ls .continue/config.json
```

## Universal Prompt Format (UPF)

The `.apm.yaml` files use a standardized format. Here's a minimal example:

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

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run unit tests
pytest tests/unit/

# Run integration tests  
pytest tests/integration/

# Run all tests with coverage
pytest --cov=src/apm
```

### Code Quality

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

## Troubleshooting

### Common Issues

1. **Import errors**: Make sure you installed with `pip install -e .`
2. **Command not found**: Check that `apm` is in your PATH
3. **Validation errors**: Use `apm validate --help` for validation options

### Getting Help

- Use `apm --help` for general help
- Use `apm <command> --help` for command-specific help
- Check the examples in `examples/basic/` directory
- Enable verbose output with `--verbose` for debugging

## What's Implemented

✅ **Core Features**:
- Universal Prompt Format (UPF) parsing and validation
- CLI interface with init, validate, generate commands
- Basic template system
- GitHub Copilot support (`.github/copilot-instructions.md`)
- Cursor support (`.cursorrules`)
- Continue support (`.continue/config.json`)

⏳ **Planned Features**:
- Advanced template engine with Jinja2
- More editor adapters (Claude, Kiro, Cline, etc.)
- Variable substitution
- Import/include system
- Configuration management
- Plugin architecture

## Contributing

This project is in active development. See the planning documents in `docs/` for roadmap and architecture details.