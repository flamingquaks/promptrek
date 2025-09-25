# UV/UVX Development Workflows

This document describes how to use `uv` and `uvx` for building, testing, and installing the PrompTrek project.

## What is uv?

[uv](https://github.com/astral-sh/uv) is a fast Python package installer and resolver, designed as a drop-in replacement for pip and pip-tools. It provides:

- **Fast dependency resolution and installation**
- **Virtual environment management**
- **Project dependencies via pyproject.toml**
- **Development workflow automation**

### uvx

`uvx` is a companion tool that allows you to run Python packages directly without installing them globally.

## Project Configuration

The project has been configured to work seamlessly with uv:

### pyproject.toml Configuration

```toml
[dependency-groups]
dev = [
    "pytest>=7.0.0",
    "pytest-cov>=4.0.0",
    "black>=22.0.0",
    "flake8>=5.0.0",
    "mypy>=1.0.0",
    "isort>=5.0.0",
]

[tool.uv.workspace]
# Mark this as the root of a uv workspace

[tool.uv]
# uv-specific configuration and shortcuts
package = true
```

## Development Workflows

### 1. Initial Setup

```bash
# Install uv if not already installed
curl -LsSf https://astral.sh/uv/install.sh | sh

# Set up the development environment
uv sync --group dev
```

### 2. Development Commands

#### Using Makefile (Recommended)

```bash
# Show all available commands
make help

# Install dependencies
make install

# Run tests (fast, no coverage)
make test-fast

# Run all tests with coverage
make test

# Run only unit tests
make test-unit

# Run only integration tests  
make test-integration

# Format code
make format

# Run linters
make lint

# Type checking
make typecheck

# Build the package
make build

# Clean artifacts
make clean

# Run CLI
make run
```

#### Using the Helper Script

```bash
# Show available commands
./scripts help

# Set up development environment
./scripts setup

# Run tests
./scripts test

# Format code
./scripts format

# Run the CLI
./scripts run --help
```

#### Using uv directly

```bash
# Install dependencies
uv sync --group dev

# Run tests
uv run python -m pytest

# Run tests without coverage
uv run python -m pytest --no-cov

# Run formatters
uv run black src/ tests/
uv run isort src/ tests/

# Run linters
uv run flake8 src/ tests/

# Type checking
uv run mypy src/

# Build package
uv build

# Run CLI
uv run promptrek --help
```

### 3. Working with Dependencies

#### Adding Dependencies

```bash
# Add a new runtime dependency
# Edit pyproject.toml to add it to the dependencies list

# Add a new development dependency
# Edit pyproject.toml to add it to dependency-groups.dev

# Sync after changes
uv sync --group dev
```

#### Updating Dependencies

```bash
# Update all dependencies
uv sync --upgrade

# Update specific dependency group
uv sync --group dev --upgrade
```

### 4. Running the CLI

#### Development Mode

```bash
# Run from source (development)
uv run promptrek --help

# Run with the Makefile
make run -- --help

# Run with the helper script
./scripts run --help
```

#### Installing Globally with uvx

```bash
# Install and run from PyPI (when published)
uvx promptrek --help

# Install and run from local build
uv build
uvx --from ./dist/promptrek-*.whl promptrek --help
```

## Testing Workflows

### Running Tests

```bash
# All tests with coverage (default)
make test

# Fast tests without coverage
make test-fast

# Unit tests only
make test-unit

# Integration tests only
make test-integration

# CI-style tests (for automation)
make ci-test
```

### Coverage Reports

Coverage reports are generated in HTML format:

```bash
# Run tests with coverage
make test

# View coverage report
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
```

## Build and Distribution

### Building the Package

```bash
# Build source and wheel distributions
make build
# or
uv build

# Outputs:
# - dist/promptrek-0.1.0.tar.gz (source distribution)
# - dist/promptrek-0.1.0-py3-none-any.whl (wheel)
```

### Installation from Built Package

```bash
# Install from wheel with uv
uv pip install dist/promptrek-*.whl

# Install with uvx for global usage
uvx --from ./dist/promptrek-*.whl promptrek
```

## CI/CD Integration

The project includes CI-friendly commands:

```bash
# Lint check for CI
make ci-lint

# Test with coverage for CI
make ci-test

# Full workflow
make all
```

Example GitHub Actions workflow:

```yaml
name: Test
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Install uv
        uses: astral-sh/setup-uv@v2
      - name: Set up Python
        run: uv python install
      - name: Install dependencies
        run: uv sync --group dev
      - name: Run tests
        run: uv run python -m pytest
      - name: Run linting
        run: |
          uv run black --check src/ tests/
          uv run isort --check-only src/ tests/
          uv run flake8 src/ tests/
      - name: Type check
        run: uv run mypy src/
```

## Advantages of Using uv

1. **Speed**: Much faster than pip for dependency resolution and installation
2. **Reliability**: Better dependency resolution with conflict detection
3. **Reproducibility**: Lock files ensure consistent environments
4. **Developer Experience**: Integrated virtual environment and project management
5. **Modern Standards**: Built for modern Python packaging standards

## Migrating from pip

If you were previously using pip:

```bash
# Old way
pip install -e ".[dev]"
python -m pytest

# New way with uv
uv sync --group dev
uv run python -m pytest
```

The uv approach provides better isolation, faster installation, and more reliable dependency resolution.

## Troubleshooting

### Common Issues

1. **Module not found errors**: Make sure you're using `uv run` or have activated the virtual environment
2. **Dependency conflicts**: Run `uv sync --upgrade` to resolve conflicts
3. **Build failures**: Check that all build dependencies are available

### Getting Help

```bash
# uv help
uv --help

# Project-specific help
make help
./scripts help
```

## References

- [uv Documentation](https://docs.astral.sh/uv/)
- [uvx Documentation](https://docs.astral.sh/uv/guides/tools/)
- [Python Packaging Guide](https://packaging.python.org/)