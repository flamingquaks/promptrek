# Installation

This guide covers all the ways to install PrompTrek.

## System Requirements

- **Python**: 3.9 or higher
- **Package Manager**: pip or [uv](https://github.com/astral-sh/uv) (recommended)
- **Operating Systems**: Linux, macOS, Windows

## Installation Methods

### Using uv (Recommended)

[uv](https://github.com/astral-sh/uv) is a fast Python package installer and resolver. It's the recommended way to install PrompTrek for development.

#### 1. Install uv

```bash
# On Linux and macOS
curl -LsSf https://astral.sh/uv/install.sh | sh

# On Windows (PowerShell)
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

#### 2. Clone and Install PrompTrek

```bash
# Clone the repository
git clone https://github.com/flamingquaks/promptrek.git
cd promptrek

# Install with all dependencies
uv sync

# Install with dev dependencies
uv sync --group dev

# Install with docs dependencies
uv sync --group docs
```

#### 3. Verify Installation

```bash
uv run promptrek --version
uv run promptrek --help
```

### Using pip (Traditional)

#### 1. Clone the Repository

```bash
git clone https://github.com/flamingquaks/promptrek.git
cd promptrek
```

#### 2. Install

```bash
# Basic installation
pip install -e .

# With development dependencies
pip install -e ".[dev]"
```

#### 3. Verify Installation

```bash
promptrek --version
promptrek --help
```

## Virtual Environment Setup

### With uv

uv automatically manages virtual environments for you:

```bash
uv sync  # Creates and activates .venv automatically
```

### With pip

Create and activate a virtual environment:

```bash
# Create virtual environment
python -m venv .venv

# Activate on Linux/macOS
source .venv/bin/activate

# Activate on Windows
.venv\Scripts\activate

# Install PrompTrek
pip install -e .
```

## Development Installation

For contributing to PrompTrek, install with development dependencies:

### Using uv

```bash
# Clone the repository
git clone https://github.com/flamingquaks/promptrek.git
cd promptrek

# Install with dev and docs dependencies
uv sync --group dev --group docs

# Install pre-commit hooks
uv run pre-commit install
```

### Using pip

```bash
# Clone the repository
git clone https://github.com/flamingquaks/promptrek.git
cd promptrek

# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows

# Install with dev dependencies
pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install
```

## Verifying Your Installation

After installation, verify that PrompTrek is working correctly:

```bash
# Check version
promptrek --version

# Run a basic command
promptrek list-editors

# Run tests (development installation only)
pytest

# Or with uv
uv run pytest
```

## Updating PrompTrek

### Using uv

```bash
cd promptrek
git pull origin main
uv sync
```

### Using pip

```bash
cd promptrek
git pull origin main
pip install -e .
```

## Uninstalling

### Using uv

Simply delete the project directory:

```bash
cd ..
rm -rf promptrek
```

### Using pip

```bash
pip uninstall promptrek
```

## Troubleshooting Installation

### Python Version Issues

Ensure you're using Python 3.9 or higher:

```bash
python --version
# or
python3 --version
```

### Permission Errors

On Linux/macOS, you may need to use `sudo` or install in a virtual environment:

```bash
# Don't use sudo - use a virtual environment instead
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

### PATH Issues

If the `promptrek` command is not found after installation:

```bash
# With uv, always use:
uv run promptrek

# Or activate the virtual environment:
source .venv/bin/activate  # Linux/macOS
.venv\Scripts\activate     # Windows
```

### Dependency Conflicts

If you encounter dependency conflicts:

```bash
# With uv (automatically resolves conflicts)
uv sync --reinstall

# With pip (create a fresh virtual environment)
rm -rf .venv
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

## Next Steps

- Follow the [Quick Start Guide](quick-start.md) to create your first configuration
- Learn about [basic usage](basic-usage.md)
- Explore the [CLI Reference](../cli/index.md)
- Check out the [Developer Guide](../developer/setup.md) if you want to contribute
