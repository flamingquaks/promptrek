# Developer Guide

Welcome to the PrompTrek developer guide. This documentation is designed for contributors, maintainers, and developers who want to understand or extend PrompTrek's architecture and functionality.

## Overview

PrompTrek is a Python-based CLI tool that provides universal prompt management for AI coding assistants. It converts a single universal prompt format into editor-specific configurations, supporting bidirectional sync and advanced features like plugins, MCP servers, and dynamic variables.

## Quick Links

- **[Architecture](architecture.md)** - System design and components
- **[Project Structure](project-structure.md)** - File organization and conventions
- **[Contributing Guide](contributing.md)** - How to contribute to PrompTrek
- **[Changelog Process](changelog-process.md)** - Commit conventions and release workflow

## Getting Started with Development

### Prerequisites

- **Python 3.9+** (3.11 recommended)
- **uv** (recommended) or pip for package management
- **Git** for version control
- **Pre-commit** for code quality checks

### Setup Development Environment

1. **Clone the repository**:
```bash
git clone https://github.com/flamingquaks/promptrek.git
cd promptrek
```

2. **Install with development dependencies**:
```bash
# Using uv (recommended)
uv sync

# Or using pip
pip install -e ".[dev]"
```

3. **Install pre-commit hooks**:
```bash
pre-commit install
```

4. **Run tests to verify setup**:
```bash
# Using uv
uv run pytest

# Or using pytest directly
pytest
```

### Project Structure Overview

```
promptrek/
├── src/promptrek/           # Source code
│   ├── cli/                 # Command-line interface
│   ├── core/                # Core functionality (models, parser, validator)
│   ├── adapters/            # Editor-specific adapters
│   ├── templates/           # Built-in templates
│   └── utils/               # Utility functions
├── tests/                   # Test suite
│   ├── unit/                # Unit tests
│   ├── integration/         # Integration tests
│   └── fixtures/            # Test data
├── docs/                    # Documentation
├── examples/                # Example configurations
└── scripts/                 # Development scripts
```

See [Project Structure](project-structure.md) for detailed information.

## Core Concepts

### Universal Prompt Format (UPF)

PrompTrek uses a schema-versioned YAML format for storing prompts:

- **v3.0.0** (current): Markdown-first with top-level plugin fields
- **v2.1.0**: Markdown-first with nested plugins
- **v2.0.0**: Markdown-first, no plugins
- **v1.0.0**: Structured fields (deprecated)

### Adapter System

PrompTrek uses an adapter pattern to support different AI editors:

```python
from promptrek.adapters.base import EditorAdapter

class MyEditorAdapter(EditorAdapter):
    def generate(self, prompt, output_dir, dry_run, verbose, variables):
        # Generate editor-specific files
        pass

    def supports_bidirectional_sync(self):
        return True

    def parse_files(self, source_dir):
        # Parse editor files back to UPF
        pass
```

### Variable Substitution

PrompTrek supports multiple variable types:

1. **Built-in variables**: `{{CURRENT_DATE}}`, `{{CURRENT_YEAR}}`, etc.
2. **Local variables**: `.promptrek/variables.promptrek.yaml`
3. **Prompt variables**: `variables:` section in UPF
4. **CLI overrides**: `-V KEY=VALUE` flags

Variables are applied in order of precedence (CLI > Prompt > Local > Built-in).

## Development Workflow

### Making Changes

1. **Create a feature branch**:
```bash
git checkout -b feature/my-feature
```

2. **Make your changes** following our [coding standards](#coding-standards)

3. **Write tests** for your changes:
```bash
# Create test file
touch tests/unit/test_my_feature.py
```

4. **Run tests locally**:
```bash
# All tests
pytest

# Specific test file
pytest tests/unit/test_my_feature.py

# With coverage
pytest --cov=promptrek --cov-report=html
```

5. **Format and lint**:
```bash
# Format code
black src/ tests/

# Sort imports
isort src/ tests/

# Lint
flake8 src/ tests/

# Type check
mypy src/
```

6. **Commit with conventional format**:
```bash
git commit -m "feat(adapters): add support for new editor"
```

See [Changelog Process](changelog-process.md) for commit conventions.

### Testing

PrompTrek uses pytest for testing:

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=promptrek --cov-report=html

# Run specific tests
pytest tests/unit/test_parser.py
pytest -k "test_validate"

# Run with verbose output
pytest -v

# Run integration tests only
pytest tests/integration/
```

### Code Quality

All code must meet these standards:

- **Format**: Black (line length 88)
- **Import sorting**: isort
- **Linting**: flake8 (no errors)
- **Type checking**: mypy (strict mode)
- **Coverage**: Minimum 90% for new code
- **Documentation**: Docstrings for all public APIs

Pre-commit hooks enforce these automatically.

## Coding Standards

### Python Style

Follow PEP 8 with these specifics:

- **Line length**: 88 characters (Black default)
- **Quotes**: Double quotes for strings
- **Imports**: Grouped and sorted by isort
- **Type hints**: Required for all public functions

### Naming Conventions

```python
# Classes: PascalCase
class EditorAdapter:
    pass

# Functions/methods: snake_case
def parse_file(file_path: Path) -> UniversalPrompt:
    pass

# Variables: snake_case
output_directory = Path("./output")

# Constants: UPPER_SNAKE_CASE
DEFAULT_SCHEMA_VERSION = "3.0.0"

# Private members: _leading_underscore
def _internal_function():
    pass
```

### Documentation

All public APIs require docstrings:

```python
def generate_prompt(
    prompt: UniversalPrompt,
    editor: str,
    output_dir: Path,
    variables: dict[str, str] | None = None,
) -> list[Path]:
    """Generate editor-specific prompt files.

    Args:
        prompt: Universal prompt configuration
        editor: Target editor name
        output_dir: Directory for generated files
        variables: Optional variable overrides

    Returns:
        List of generated file paths

    Raises:
        AdapterNotFoundError: If editor adapter not found
        GenerationError: If generation fails

    Example:
        >>> prompt = parser.parse_file("config.yaml")
        >>> files = generate_prompt(prompt, "claude", Path("."))
        >>> print(f"Generated {len(files)} files")
    """
    pass
```

## Adding Features

### Adding a New Editor Adapter

1. **Create adapter class** in `src/promptrek/adapters/`:

```python
# src/promptrek/adapters/myeditor.py
from pathlib import Path
from typing import Union

from .base import EditorAdapter
from ..core.models import UniversalPrompt, UniversalPromptV2, UniversalPromptV3


class MyEditorAdapter(EditorAdapter):
    """Adapter for MyEditor IDE."""

    def generate(
        self,
        prompt: Union[UniversalPrompt, UniversalPromptV2, UniversalPromptV3],
        output_dir: Path,
        dry_run: bool,
        verbose: bool,
        variables: dict[str, str] | None = None,
    ) -> None:
        """Generate MyEditor configuration files."""
        # Implementation here
        pass

    def supports_bidirectional_sync(self) -> bool:
        """Whether this adapter supports syncing from editor files."""
        return True

    def parse_files(self, source_dir: Path) -> UniversalPromptV3:
        """Parse MyEditor files to universal format."""
        # Implementation here
        pass
```

2. **Register adapter** in `src/promptrek/adapters/registry.py`:

```python
from .myeditor import MyEditorAdapter

# Register adapter
registry.register("myeditor", MyEditorAdapter)
```

3. **Add tests** in `tests/unit/adapters/test_myeditor.py`:

```python
import pytest
from pathlib import Path
from promptrek.adapters.myeditor import MyEditorAdapter
from promptrek.core.models import UniversalPromptV3

def test_myeditor_generate():
    """Test MyEditor generation."""
    adapter = MyEditorAdapter()
    prompt = UniversalPromptV3(...)

    adapter.generate(prompt, Path("/tmp"), dry_run=False, verbose=False)

    # Assert files created
    assert Path("/tmp/.myeditor/config.json").exists()
```

4. **Update documentation**:
   - Add to `docs/user-guide/adapters/index.md`
   - Create `docs/user-guide/adapters/myeditor.md`

### Adding a New CLI Command

1. **Create command module** in `src/promptrek/cli/commands/`:

```python
# src/promptrek/cli/commands/mycommand.py
import click
from pathlib import Path

def my_command(ctx: click.Context, option: str) -> None:
    """Execute my custom command."""
    # Implementation here
    pass
```

2. **Register command** in `src/promptrek/cli/main.py`:

```python
from .commands.mycommand import my_command

@cli.command()
@click.option("--option", help="My option")
@click.pass_context
def mycommand(ctx: click.Context, option: str) -> None:
    """My custom command description."""
    try:
        my_command(ctx, option)
    except PrompTrekError as e:
        click.echo(f"Error: {e}", err=True)
        ctx.exit(1)
```

3. **Add tests** in `tests/unit/cli/test_mycommand.py`

4. **Update documentation** in `docs/cli/commands/mycommand.md`

## Testing Guidelines

### Unit Tests

Test individual functions and classes:

```python
def test_parse_yaml_file():
    """Test YAML file parsing."""
    parser = UPFParser()
    prompt = parser.parse_file("test.yaml")

    assert prompt.metadata.title == "Test Project"
    assert prompt.schema_version == "3.0.0"
```

### Integration Tests

Test complete workflows:

```python
def test_full_generation_workflow(tmp_path):
    """Test complete generation workflow."""
    # Create test file
    config_file = tmp_path / "config.yaml"
    config_file.write_text(TEST_CONFIG)

    # Generate
    result = runner.invoke(cli, ["generate", str(config_file), "--editor", "claude"])

    # Verify
    assert result.exit_code == 0
    assert (tmp_path / ".claude/prompts/project.md").exists()
```

### Fixtures

Reuse test data:

```python
# tests/conftest.py
import pytest

@pytest.fixture
def sample_prompt():
    """Sample Universal Prompt for testing."""
    return UniversalPromptV3(
        schema_version="3.0.0",
        metadata=PromptMetadata(
            title="Test Project",
            description="Test description",
            version="1.0.0",
        ),
        content="# Test Content",
    )
```

## Release Process

See [Changelog Process](changelog-process.md) for details on:

- Conventional commits
- Version bumping
- Changelog generation
- Publishing releases

## Resources

### Internal Documentation

- [Architecture](architecture.md) - System architecture and design
- [Project Structure](project-structure.md) - File organization
- [Contributing Guide](contributing.md) - Contribution guidelines
- [Changelog Process](changelog-process.md) - Release workflow

### External Resources

- [PrompTrek Repository](https://github.com/flamingquaks/promptrek)
- [Issue Tracker](https://github.com/flamingquaks/promptrek/issues)
- [Discussions](https://github.com/flamingquaks/promptrek/discussions)
- [Python Packaging Guide](https://packaging.python.org/)

## Getting Help

- **Bug Reports**: [GitHub Issues](https://github.com/flamingquaks/promptrek/issues/new?template=bug_report.yml)
- **Feature Requests**: [GitHub Issues](https://github.com/flamingquaks/promptrek/issues/new?template=feature_request.yml)
- **Questions**: [GitHub Discussions](https://github.com/flamingquaks/promptrek/discussions)
- **Documentation Issues**: Open an issue or submit a PR

## Community

- **Code of Conduct**: See `CODE_OF_CONDUCT.md`
- **License**: MIT License
- **Contributors**: See `CONTRIBUTORS.md`

Thank you for contributing to PrompTrek!
