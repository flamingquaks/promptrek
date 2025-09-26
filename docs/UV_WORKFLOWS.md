# UV/UVX Workflow Guide

This document explains how to use PrompTrek with `uv` and `uvx` for streamlined development workflows.

## Quick Start with uvx (No Installation Required)

Run PrompTrek commands directly without installing:

```bash
# Run PrompTrek CLI directly
uvx promptrek --help
uvx promptrek init
uvx promptrek generate config.yaml --editor copilot

# Run with specific version
uvx promptrek@0.1.0 --help
```

## Development Setup with uv

### 1. Initial Setup

```bash
# Clone and navigate to project
git clone https://github.com/flamingquaks/promptrek.git
cd promptrek

# Install project with development dependencies
uv sync --extra dev
```

### 2. Available Commands

#### Core PrompTrek Commands
```bash
# Main CLI (after sync)
uv run promptrek --help
uv run promptrek init
uv run promptrek generate config.yaml --editor copilot
uv run promptrek validate config.yaml
uv run promptrek list-editors

# Or using uvx (no sync required)
uvx --from . promptrek --help
```

#### Development Commands

**Testing:**
```bash
# Run all tests
uv run pytest

# Run tests with coverage
uv run pytest --cov=src/promptrek

# Run specific test types
uv run pytest tests/unit/
uv run pytest tests/integration/

# Fast tests (no coverage)
uv run pytest --no-cov
```

**Code Quality:**
```bash
# Format code
uv run black src/ tests/
uv run isort src/ tests/

# Check formatting (CI mode)
uv run black --check src/ tests/
uv run isort --check-only src/ tests/

# Lint code
uv run flake8 src/ tests/

# Type checking
uv run mypy src/
```

**Build & Distribution:**
```bash
# Build package
uv build

# Build wheel only
uv build --wheel

# Build source distribution only
uv build --sdist
```

#### Make Commands (Alternative Interface)

All development workflows are also available through Make:

```bash
# Show all available commands
make help

# Development setup
make install    # or make sync

# Testing
make test
make test-fast
make test-unit
make test-integration

# Code quality
make format
make lint
make typecheck

# Build
make build
make clean
```

#### Shell Script (Legacy)

```bash
# Setup and basic commands
./script.sh help
./script.sh setup
./script.sh test
./script.sh format
./script.sh build
```

## Command Comparison

| Task | uv Command | Make Command | Script Command |
|------|------------|--------------|----------------|
| Install deps | `uv sync --extra dev` | `make install` | `./script.sh setup` |
| Run tests | `uv run pytest` | `make test` | `./script.sh test` |
| Format code | `uv run black src/ tests/` | `make format` | `./script.sh format` |
| Build package | `uv build` | `make build` | `./script.sh build` |
| Run CLI | `uv run promptrek` | - | `./script.sh run` |

## Environment Management

### Virtual Environment

```bash
# uv automatically manages virtual environments
# To see the active environment:
uv info

# To run a shell in the environment:
uv run bash
uv run python  # Interactive Python shell
```

### Dependency Management

```bash
# Add new dependency
uv add click>=8.1.0

# Add development dependency
uv add --group dev pytest-xdist

# Update dependencies
uv sync

# Remove dependency
uv remove click

# Lock dependencies
uv lock
```

## CI/CD Integration

### GitHub Actions Example

```yaml
name: Test
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ['3.8', '3.9', '3.10', '3.11', '3.12']
    steps:
      - uses: actions/checkout@v4
      
      - name: Install uv
        uses: astral-sh/setup-uv@v1
        with:
          version: "latest"
      
      - name: Set up Python ${{ matrix.python-version }}
        run: uv python install ${{ matrix.python-version }}
      
      - name: Install dependencies
        run: uv sync --extra dev
      
      - name: Run tests
        run: uv run pytest tests/ --cov=src/promptrek
      
      - name: Run linting
        run: |
          uv run black --check src/ tests/
          uv run flake8 src/ tests/
          uv run mypy src/
      
      - name: Test CLI functionality
        run: |
          uv run promptrek --help
          uv run promptrek list-editors
          
          # Test uvx functionality
          uvx --from . promptrek --help

  security:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Install uv
        uses: astral-sh/setup-uv@v1
      
      - name: Set up Python
        run: uv python install 3.11
      
      - name: Install security tools
        run: |
          uv add --extra dev bandit safety
          uv sync --extra dev
      
      - name: Run security checks
        run: |
          uv run bandit -r src/
          uv run safety check
```

### Release Workflow Example

```yaml
name: Release
on:
  push:
    tags: ['v*.*.*']

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Install uv
        uses: astral-sh/setup-uv@v1
      
      - name: Set up Python
        run: uv python install 3.11
      
      - name: Install dependencies
        run: uv sync --extra dev
      
      - name: Run tests
        run: uv run pytest tests/ --cov-fail-under=80
      
      - name: Build package
        run: uv build
      
      - name: Upload artifacts
        uses: actions/upload-artifact@v3
        with:
          name: dist
          path: dist/
```

## Troubleshooting

### Common Issues

**`uv: command not found`**
```bash
# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Permission issues with uvx**
```bash
# Ensure uvx cache is writable
export UVTOOLS_DIR=~/.local/uvtools
uvx promptrek --help
```

**Missing dependencies**
```bash
# Reinstall all dependencies
uv sync --group dev --reinstall
```

### Performance Tips

- Use `uv run` for development commands (faster than activating venv)
- Use `uvx` for one-off commands without installation
- Use `--no-dev` flag for production installs: `uv sync --no-dev`
- Use `uv cache clean` to clear cache if needed

## Advanced Usage

### Custom Scripts

Add custom scripts to `pyproject.toml`:

```toml
[project.scripts]
promptrek = "promptrek.cli.main:cli"
# Add more scripts here
```

### Workspace Support

For multi-package projects:

```toml
[tool.uv.workspace]
members = ["packages/*"]
```

### Lock File Management

```bash
# Generate lock file
uv lock

# Update specific dependency
uv lock --update-package click

# Upgrade all dependencies
uv lock --upgrade
```

## Migration from pip/virtualenv

If migrating from pip-based workflow:

```bash
# Instead of:
pip install -e .[dev]

# Use:
uv sync --group dev

# Instead of:
source venv/bin/activate
python -m pytest

# Use:
uv run pytest
