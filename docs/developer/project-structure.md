# Project Structure and Conventions

This document describes PrompTrek's file organization, naming conventions, and development standards.

## Repository Structure

```
promptrek/
├── README.md                     # Project overview and quick start
├── LICENSE                       # MIT License
├── .gitignore                    # Git ignore patterns
├── pyproject.toml                # Python project configuration (PEP 518)
├── uv.lock                       # UV dependency lock file
├── MANIFEST.in                   # Package manifest for sdist
├── Makefile                      # Development shortcuts
│
├── src/                          # Source code (PEP 420 namespace)
│   └── promptrek/                # Main package
│       ├── __init__.py           # Package exports and version
│       ├── __main__.py           # CLI entry point
│       ├── cli/                  # Command-line interface
│       ├── core/                 # Core functionality
│       ├── adapters/             # Editor adapters
│       └── utils/                # Utility functions
│
├── tests/                        # Test suite
│   ├── unit/                     # Unit tests
│   ├── integration/              # Integration tests
│   ├── fixtures/                 # Test data
│   └── conftest.py               # Pytest configuration
│
├── docs/                         # Documentation (MkDocs)
│   ├── index.md                  # Documentation home
│   ├── cli/                      # CLI reference
│   ├── developer/                # Developer guides
│   ├── getting-started/          # User guides
│   └── user-guide/               # User documentation
│
├── examples/                     # Example configurations
│   ├── basic/                    # Simple examples
│   ├── advanced/                 # Complex examples
│   └── v21-plugins/              # Plugin examples
│
├── scripts/                      # Development and build scripts
│   ├── build.sh                  # Build script
│   ├── test.sh                   # Test runner
│   └── release.sh                # Release preparation
│
├── .github/                      # GitHub-specific files
│   ├── workflows/                # GitHub Actions
│   ├── ISSUE_TEMPLATE/           # Issue templates
│   ├── PULL_REQUEST_TEMPLATE.md  # PR template
│   ├── CONTRIBUTING.md           # Contribution guidelines
│   └── dependabot.yml            # Dependabot configuration
│
├── gh-pages/                     # Legacy documentation (being migrated)
│
├── .pre-commit-config.yaml       # Pre-commit hooks config
├── .pre-commit-hooks.yaml        # PrompTrek's own hooks
├── mkdocs.yml                    # MkDocs configuration
└── project.promptrek.yaml        # PrompTrek's own configuration
```

## Source Code Structure

### Main Package: `src/promptrek/`

```
src/promptrek/
├── __init__.py                   # Package info, version, exports
├── __main__.py                   # Entry point: python -m promptrek
│
├── cli/                          # Command-line interface
│   ├── __init__.py
│   ├── main.py                   # Main CLI entry point with Click
│   ├── interactive.py            # Interactive mode with questionary
│   ├── yaml_writer.py            # YAML formatting utilities
│   └── commands/                 # Individual commands
│       ├── __init__.py
│       ├── init.py               # `promptrek init` command
│       ├── generate.py           # `promptrek generate` command
│       ├── validate.py           # `promptrek validate` command
│       ├── sync.py               # `promptrek sync` command
│       ├── migrate.py            # `promptrek migrate` command
│       ├── plugins.py            # `promptrek plugins` commands
│       ├── agents.py             # `promptrek agents` command (deprecated)
│       ├── hooks.py              # `promptrek install-hooks` command
│       ├── config_ignores.py     # `promptrek config-ignores` command
│       ├── preview.py            # `promptrek preview` command
│       └── refresh.py            # `promptrek refresh` command
│
├── core/                         # Core functionality
│   ├── __init__.py
│   ├── models.py                 # Data models (Pydantic)
│   │                             # - UniversalPrompt (v1)
│   │                             # - UniversalPromptV2 (v2.x)
│   │                             # - UniversalPromptV3 (v3.x)
│   │                             # - PromptMetadata
│   │                             # - MCPServer, Command, Agent, Hook
│   ├── parser.py                 # UPF file parsing
│   ├── validator.py              # UPF validation logic
│   └── exceptions.py             # Custom exceptions
│
├── adapters/                     # Editor-specific adapters
│   ├── __init__.py
│   ├── base.py                   # Base adapter interface
│   ├── registry.py               # Adapter registration and discovery
│   ├── sync_mixin.py             # Bidirectional sync support
│   ├── mcp_mixin.py              # MCP server support
│   ├── claude.py                 # Claude Code adapter
│   ├── continue_adapter.py       # Continue extension adapter
│   ├── cursor.py                 # Cursor IDE adapter
│   ├── cline.py                  # Cline adapter
│   ├── windsurf.py               # Windsurf adapter
│   ├── amazon_q.py               # Amazon Q adapter
│   ├── copilot.py                # GitHub Copilot adapter
│   ├── kiro.py                   # Kiro adapter
│   └── jetbrains.py              # JetBrains AI adapter
│
└── utils/                        # Utility modules
    ├── __init__.py
    ├── variables.py              # Variable substitution
    ├── gitignore.py              # .gitignore management
    ├── conditionals.py           # Conditional logic
    └── imports.py                # Dynamic imports
```

## Naming Conventions

### File and Directory Names

| Type | Convention | Example |
|------|------------|---------|
| Python files | `snake_case.py` | `yaml_writer.py` |
| Directories | `snake_case/` | `cli/commands/` |
| Configuration | `.config-name` | `.pre-commit-config.yaml` |
| UPF files | `*.promptrek.yaml` | `project.promptrek.yaml` |
| Test files | `test_*.py` | `test_parser.py` |

### Python Code Conventions

Follow PEP 8 with these specifics:

```python
# Classes: PascalCase
class EditorAdapter:
    pass

class UniversalPromptV3:
    pass

# Functions/methods: snake_case
def parse_file(file_path: Path) -> UniversalPrompt:
    pass

def generate_editor_files() -> None:
    pass

# Variables: snake_case
output_directory = Path("./output")
schema_version = "3.0.0"
is_valid = True

# Constants: UPPER_SNAKE_CASE
DEFAULT_SCHEMA_VERSION = "3.0.0"
MAX_FILE_SIZE = 1024 * 1024
SUPPORTED_EDITORS = ["claude", "cursor", "continue"]

# Private members: _leading_underscore
def _internal_helper():
    pass

_cache = {}

# Module-level "constants": UPPER_SNAKE_CASE
__version__ = "3.0.0"
__all__ = ["EditorAdapter", "parse_file"]
```

### Import Organization

Imports should be grouped and sorted:

```python
# Standard library imports
import os
import sys
from pathlib import Path
from typing import Optional, Union

# Third-party imports
import click
import yaml
from pydantic import BaseModel

# Local application imports
from ..core.models import UniversalPrompt
from ..core.exceptions import PrompTrekError
from .base import EditorAdapter
```

Enforced by `isort` with configuration:

```toml
# pyproject.toml
[tool.isort]
profile = "black"
line_length = 88
```

## Configuration Files

### pyproject.toml

Modern Python project configuration (PEP 518):

```toml
[project]
name = "promptrek"
version = "3.0.0"
description = "Universal AI editor prompt management"
requires-python = ">=3.9"
dependencies = [
    "click>=8.1.0",
    "pydantic>=2.0.0",
    "pyyaml>=6.0.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.4.0",
    "pytest-cov>=4.1.0",
    "black>=23.0.0",
    "flake8>=6.0.0",
    "mypy>=1.5.0",
]

[project.scripts]
promptrek = "promptrek.cli.main:cli"

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]

[tool.black]
line-length = 88
target-version = ['py39', 'py310', 'py311']

[tool.mypy]
python_version = "3.9"
strict = true
```

### mkdocs.yml

Documentation site configuration:

```yaml
site_name: PrompTrek
site_description: Universal AI Editor Prompt Management
site_url: https://flamingquaks.github.io/promptrek/

theme:
  name: material
  features:
    - navigation.tabs
    - navigation.sections
    - toc.integrate
    - search.suggest

nav:
  - Home: index.md
  - Getting Started:
      - Quick Start: getting-started/quick-start.md
      - Installation: getting-started/installation.md
  - CLI Reference:
      - Overview: cli/index.md
      - Commands:
          - init: cli/commands/init.md
          - generate: cli/commands/generate.md
  - Developer Guide:
      - Overview: developer/index.md
      - Architecture: developer/architecture.md
```

### .pre-commit-config.yaml

Pre-commit hooks for code quality:

```yaml
repos:
  - repo: https://github.com/psf/black
    rev: 23.7.0
    hooks:
      - id: black
        language_version: python3.11

  - repo: https://github.com/pycqa/isort
    rev: 5.12.0
    hooks:
      - id: isort

  - repo: https://github.com/pycqa/flake8
    rev: 6.0.0
    hooks:
      - id: flake8

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.5.0
    hooks:
      - id: mypy
```

## Test Structure

### Unit Tests

```
tests/unit/
├── test_parser.py                # Parser tests
├── test_validator.py             # Validator tests
├── test_models.py                # Model tests
├── cli/
│   ├── test_main.py              # CLI main tests
│   └── commands/
│       ├── test_init.py          # Init command tests
│       └── test_generate.py      # Generate command tests
├── adapters/
│   ├── test_base.py              # Base adapter tests
│   ├── test_claude.py            # Claude adapter tests
│   └── test_continue.py          # Continue adapter tests
└── utils/
    ├── test_variables.py         # Variable substitution tests
    └── test_gitignore.py         # Gitignore utility tests
```

### Integration Tests

```
tests/integration/
├── test_full_workflow.py         # End-to-end workflow tests
├── test_cli_integration.py       # CLI integration tests
└── test_sync_workflow.py         # Sync workflow tests
```

### Test Fixtures

```
tests/fixtures/
├── valid_prompts/                # Valid UPF files for testing
│   ├── v1_basic.yaml
│   ├── v2_basic.yaml
│   └── v3_basic.yaml
├── invalid_prompts/              # Invalid UPF files
│   ├── missing_metadata.yaml
│   └── invalid_syntax.yaml
└── expected_outputs/             # Expected generation outputs
    ├── claude/
    └── continue/
```

## Documentation Structure

### MkDocs Structure

```
docs/
├── index.md                      # Documentation home
├── getting-started/              # Getting started guides
│   ├── index.md
│   ├── installation.md
│   ├── quick-start.md
│   ├── basic-usage.md
│   └── first-project.md
├── cli/                          # CLI reference
│   ├── index.md                  # CLI overview
│   ├── interactive.md            # Interactive mode
│   └── commands/                 # Individual commands
│       ├── init.md
│       ├── generate.md
│       ├── validate.md
│       ├── sync.md
│       └── migrate.md
├── user-guide/                   # User documentation
│   ├── index.md
│   ├── upf-specification.md      # UPF schema spec
│   ├── adapters/                 # Adapter documentation
│   │   ├── index.md
│   │   └── capabilities.md
│   ├── plugins/                  # Plugin documentation
│   │   └── index.md
│   └── workflows/                # Workflow guides
│       ├── sync.md
│       └── pre-commit.md
├── developer/                    # Developer guides
│   ├── index.md                  # Developer overview
│   ├── architecture.md           # System architecture
│   ├── project-structure.md      # This file
│   ├── contributing.md           # Contribution guide
│   └── changelog-process.md      # Release process
└── reference/                    # API reference (auto-generated)
```

## Development Conventions

### Branch Strategy

- **main**: Production-ready code
- **feature/***: New features
- **fix/***: Bug fixes
- **docs/***: Documentation updates
- **refactor/***: Code refactoring
- **test/***: Test improvements

### Commit Message Format

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
type(scope): description

[optional body]

[optional footer]
```

**Types**:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `style`: Code style (formatting)
- `refactor`: Code refactoring
- `test`: Tests
- `chore`: Maintenance
- `ci`: CI/CD changes
- `build`: Build system
- `perf`: Performance
- `revert`: Revert commit

**Scopes**:
- `cli`: CLI components
- `core`: Core functionality
- `adapters`: Editor adapters
- `docs`: Documentation
- `tests`: Tests
- `deps`: Dependencies
- `changelog`: Changelog

**Examples**:
```
feat(adapters): add Windsurf editor support
fix(parser): handle empty instructions gracefully
docs(cli): add migration command documentation
test(adapters): add Claude adapter integration tests
ci(changelog): automate changelog generation
```

### Code Quality Standards

All code must pass:

1. **Black**: Code formatting
   ```bash
   black src/ tests/
   ```

2. **isort**: Import sorting
   ```bash
   isort src/ tests/
   ```

3. **flake8**: Linting
   ```bash
   flake8 src/ tests/ --max-line-length=88
   ```

4. **mypy**: Type checking
   ```bash
   mypy src/ --strict
   ```

5. **pytest**: Tests with coverage
   ```bash
   pytest --cov=promptrek --cov-fail-under=90
   ```

Pre-commit hooks enforce these automatically.

### Documentation Standards

- **Docstrings**: All public APIs (Google style)
- **Type hints**: All function signatures
- **Examples**: In docstrings and docs
- **Cross-references**: Link related documentation

Example docstring:

```python
def generate_editor_files(
    prompt: UniversalPromptV3,
    editor: str,
    output_dir: Path,
    variables: dict[str, str] | None = None,
) -> list[Path]:
    """Generate editor-specific configuration files.

    Args:
        prompt: Universal prompt configuration
        editor: Target editor name (e.g., 'claude', 'cursor')
        output_dir: Directory for generated files
        variables: Optional variable overrides

    Returns:
        List of generated file paths

    Raises:
        AdapterNotFoundError: If editor adapter not found
        GenerationError: If generation fails

    Example:
        ```python
        prompt = parser.parse_file("config.yaml")
        files = generate_editor_files(
            prompt,
            "claude",
            Path("."),
            variables={"VERSION": "2.0.0"}
        )
        print(f"Generated {len(files)} files")
        ```
    """
    pass
```

## Version Control

### .gitignore Patterns

```gitignore
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual environments
venv/
ENV/
env/

# Testing
.pytest_cache/
.coverage
htmlcov/
.tox/

# IDEs
.vscode/
.idea/
*.swp
*.swo
*~

# PrompTrek
.promptrek/
*.promptrek.yaml.backup

# MkDocs
site/

# OS
.DS_Store
Thumbs.db
```

## See Also

- [Architecture](architecture.md) - System architecture and design
- [Contributing Guide](contributing.md) - How to contribute
- [Changelog Process](changelog-process.md) - Release workflow
