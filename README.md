# PrompTrek

[![CI](https://github.com/flamingquaks/promptrek/actions/workflows/ci.yml/badge.svg)](https://github.com/flamingquaks/promptrek/actions/workflows/ci.yml)
[![PR Validation](https://github.com/flamingquaks/promptrek/actions/workflows/pr.yml/badge.svg)](https://github.com/flamingquaks/promptrek/actions/workflows/pr.yml)
[![Python Versions](https://img.shields.io/badge/python-3.9%20%7C%203.10%20%7C%203.11%20%7C%203.12-blue)](https://github.com/flamingquaks/promptrek)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

*Taking your coding prompts on a journey to every AI editor!*

A universal AI Editor prompt storage solution that dynamically maps prompt data to a wide-range of agentic/AI editors and tools. This tool allows you to create generic prompts and workflows in a standardized format, then generate editor-specific prompts for your preferred AI coding assistant.

## 🎯 Problem It Solves

AI coding assistants like GitHub Copilot, Cursor, Continue, and others all use different prompt formats and configuration methods. When working across teams or switching between editors, you have to maintain separate prompt configurations for each tool. PrompTrek solves this by:

- **Universal Format**: Create prompts once in a standardized format
- **Multi-Editor Support**: Generate prompts for any supported AI editor
- **Team Consistency**: Share prompt configurations across team members regardless of their editor choice
- **Easy Migration**: Switch between AI editors without losing your prompt configurations

## 🚀 Quick Example

1. Create a universal prompt file (`.promptrek.yaml`):
```yaml
schema_version: "1.0.0"
metadata:
  title: "My Project Assistant"
  description: "AI assistant for React TypeScript project"
targets: [copilot, cursor, continue]
instructions:
  general:
    - "Use TypeScript for all new files"
    - "Follow React functional component patterns"
    - "Write comprehensive tests"
```

2. Generate editor-specific prompts:
```bash
# Generate for GitHub Copilot
promptrek generate --editor copilot

# Generate for Cursor
promptrek generate --editor cursor

# Generate for all configured editors
promptrek generate --all
```

3. Use the generated prompts in your preferred editor!

## 📖 Documentation

Comprehensive documentation is available in the [`docs/`](https://github.com/flamingquaks/promptrek/tree/main/docs) directory:

### Getting Started
- [Getting Started Guide](./GETTING_STARTED.md) - Complete setup and usage guide
- [Universal Prompt Format](./docs/UPF_SPECIFICATION.md) - UPF specification and examples

### Features & Usage
- [Advanced Features](https://github.com/flamingquaks/promptrek/tree/main/docs/ADVANCED_FEATURES.md) - Variables, conditionals, and imports
- [Editor Adapters](https://github.com/flamingquaks/promptrek/tree/main/docs/ADAPTERS.md) - Detailed guide to all supported editors
- [Adapter Capabilities](https://github.com/flamingquaks/promptrek/tree/main/docs/ADAPTER_CAPABILITIES.md) - Feature comparison matrix
- [Sync Feature](https://github.com/flamingquaks/promptrek/tree/main/docs/SYNC_FEATURE.md) - Bidirectional synchronization guide

### Architecture & Planning
- [System Architecture](https://github.com/flamingquaks/promptrek/tree/main/docs/ARCHITECTURE.md) - Technical design and structure
- [Implementation Roadmap](https://github.com/flamingquaks/promptrek/tree/main/docs/IMPLEMENTATION_ROADMAP.md) - Development status and future plans
- [Project Structure](https://github.com/flamingquaks/promptrek/tree/main/docs/PROJECT_STRUCTURE.md) - Repository organization

## 🎨 Supported Editors

### ✅ All Implemented
- **GitHub Copilot** - `.github/copilot-instructions.md`, `.github/instructions/*.instructions.md`, `.github/prompts/*.prompt.md` - Repository-wide and path-specific instructions
- **Cursor** - `.cursor/rules/index.mdc`, `.cursor/rules/*.mdc`, `AGENTS.md` - Modern 2025 rules system with Always/Auto Attached rule types and project overview
- **Continue** - `config.yaml`, `.continue/rules/*.md` - Modern YAML configuration with advanced rules directory
- **Kiro** - `.kiro/steering/*.md`, `.kiro/specs/*.md` - Comprehensive steering and specs system with YAML frontmatter
- **Cline** - `.clinerules` - Simple rules-based configuration
- **Claude Code** - `.claude/context.md` - Context-based prompts with detailed project information
- **Codeium** - `.codeium/context.json`, `.codeiumrc` - Context-based prompts with team patterns
- **Tabnine** - `.tabnine/config.json`, `.tabnine/team.yaml` - Team-specific configurations
- **Amazon Q** - `.amazonq/context.md`, `.amazonq/comments.template` - Comment-based prompts
- **JetBrains AI** - `.idea/ai-assistant.xml`, `.jetbrains/config.json` - IDE-integrated prompts

## 🗂️ Example Configurations

See the [`examples/`](.https://github.com/flamingquaks/promptrek/tree/main/examples/) directory for sample configurations:

### Basic Examples
- [React TypeScript Project](https://github.com/flamingquaks/promptrek/tree/main/examples/basic/react-typescript.promptrek.yaml)
- [Node.js API Service](https://github.com/flamingquaks/promptrek/tree/main/examples/basic/node-api.promptrek.yaml)

### Advanced Examples
- [NX Monorepo](https://github.com/flamingquaks/promptrek/tree/main/examples/advanced/monorepo-nx.promptrek.yaml) - Multi-package workspace with NX
- [Microservices + Kubernetes](https://github.com/flamingquaks/promptrek/tree/main/examples/advanced/microservices-k8s.promptrek.yaml) - Cloud-native architecture
- [React Native Mobile](https://github.com/flamingquaks/promptrek/tree/main/examples/advanced/mobile-react-native.promptrek.yaml) - Cross-platform mobile apps
- [FastAPI Backend](https://github.com/flamingquaks/promptrek/tree/main/examples/advanced/python-fastapi.promptrek.yaml) - Modern Python async API
- [Next.js Full-Stack](https://github.com/flamingquaks/promptrek/tree/main/examples/advanced/fullstack-nextjs.promptrek.yaml) - App Router with SSR
- [Rust CLI Tool](https://github.com/flamingquaks/promptrek/tree/main/examples/advanced/rust-cli.promptrek.yaml) - Systems programming
- [Go Backend Service](https://github.com/flamingquaks/promptrek/tree/main/examples/advanced/golang-backend.promptrek.yaml) - High-performance APIs
- [Data Science ML](https://github.com/flamingquaks/promptrek/tree/main/examples/advanced/data-science-python.promptrek.yaml) - MLOps and experiments

## 🚀 Installation & Quick Start

### Installation

#### Option 1: Using uv (Recommended)

```bash
# Install uv if you haven't already
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install from source with uv
git clone https://github.com/flamingquaks/promptrek.git
cd promptrek
uv sync --group dev
```

#### Option 2: Traditional pip

```bash
# Install from source (recommended for now)
git clone https://github.com/flamingquaks/promptrek.git
cd promptrek
uv sync
# or with pip: pip install -e .
```

### Quick Start

```bash
# 1. Initialize a new project with pre-commit hooks (recommended)
uv run promptrek init --template react --output my-project.promptrek.yaml --setup-hooks
# or with traditional pip: promptrek init --template react --output my-project.promptrek.yaml --setup-hooks

# 2. Validate your configuration
uv run promptrek validate my-project.promptrek.yaml

# 3. Generate editor-specific prompts
uv run promptrek generate my-project.promptrek.yaml --all

# 4. Your AI editor prompts are ready!
ls .github/copilot-instructions.md
ls .cursorrules
ls .continue/config.json
```

**Note:** The `--setup-hooks` flag automatically configures pre-commit hooks to validate your `.promptrek.yaml` files and prevent accidental commits of generated files.

### Available Commands

- `promptrek init` - Create a new universal prompt file with templates (use `--setup-hooks` to automatically configure pre-commit)
- `promptrek validate` - Check your configuration for errors
- `promptrek generate` - Create editor-specific prompts
- `promptrek preview` - Preview generated output without creating files
- `promptrek sync` - Sync editor files back to PrompTrek format
- `promptrek agents` - Generate agent-specific instructions
- `promptrek install-hooks` - Set up pre-commit hooks (use `--activate` to activate automatically)
- `promptrek list-editors` - Show supported editors and their status

For detailed usage instructions, see [`GETTING_STARTED.md`](./GETTING_STARTED.md).

## 🔧 Development Setup

### Pre-commit Hooks

PrompTrek includes pre-commit hooks to ensure code quality and prevent accidental commits of generated files:

```bash
# Install development dependencies
uv sync --group dev
# or with pip: pip install -e .[dev]

# Install pre-commit hooks
uv run pre-commit install

# Run hooks manually (optional)
uv run pre-commit run --all-files
```

The pre-commit hooks will:
- Validate `.promptrek.yaml` files using `promptrek validate`
- Prevent committing generated prompt files (they should be generated locally)
- Run code formatting (black, isort) and linting (flake8, yamllint)
- Check for common issues (trailing whitespace, merge conflicts, etc.)

### Generated Files

PrompTrek generates editor-specific files that should **not** be committed to version control:

- `.github/copilot-instructions.md` - GitHub Copilot prompts
- `.cursor/` - Cursor editor configuration (modern .mdc rules)
- `config.yaml`, `.continue/` - Continue editor configuration
- `.claude/` - Claude/Anthropic configuration
- And more...

These files are automatically ignored via `.gitignore` and the pre-commit hooks will prevent accidental commits.

## 🤝 Contributing

This project is actively developing! We welcome:
- Bug reports and feature requests
- Pull requests for additional editor support
- Documentation improvements
- Testing and feedback on the UPF format
- Ideas for advanced features

### Conventional Commits & Changelog

PrompTrek uses [Conventional Commits](https://www.conventionalcommits.org/) for automated changelog generation:

```bash
# Commit format
type(scope): description

# Examples
feat(adapters): add support for new editor
fix(parser): handle edge case in YAML parsing
docs(readme): update installation instructions
```

All commit messages are validated in CI. See [CHANGELOG_PROCESS.md](./docs/CHANGELOG_PROCESS.md) for detailed guidelines.

See the [Implementation Roadmap](./docs/IMPLEMENTATION_ROADMAP.md) for planned features and current progress.

## 🧪 Testing and Quality Assurance

PrompTrek maintains high quality standards with comprehensive testing:

### Automated Testing
- **Continuous Integration**: Tests run on every push and PR across multiple Python versions (3.8-3.12)
- **Cross-Platform Testing**: Validates functionality on Linux, macOS, and Windows
- **Security Scanning**: Automated security vulnerability detection
- **Code Quality**: Enforced formatting (black), import sorting (isort), and linting (flake8)
- **Coverage**: Maintains >80% test coverage with detailed reporting

### Test Categories
- **Unit Tests**: Test individual components and functions
- **Integration Tests**: Test complete workflows and CLI functionality
- **Performance Tests**: Monitor memory usage and execution speed
- **Compatibility Tests**: Ensure compatibility across Python versions and platforms

### Running Tests Locally

#### Using uv (Recommended)

```bash
# Install development dependencies
uv sync --group dev

# Run all tests
make test-fast  # Fast tests without coverage
make test       # All tests with coverage

# Run specific test categories
uv run python -m pytest tests/unit/        # Unit tests only
uv run python -m pytest tests/integration/ # Integration tests only

# Code quality checks
make format     # Format code
make lint       # Run linters
make typecheck  # Type checking
```

#### Using pip (Traditional)

```bash
# Install development dependencies
uv sync --group dev
# or with pip: pip install -e ".[dev]"

# Run all tests
uv run pytest

# Run with coverage
pytest --cov=src/promptrek --cov-report=html

# Run specific test categories
pytest tests/unit/        # Unit tests only
pytest tests/integration/ # Integration tests only

# Code quality checks
black src/ tests/         # Format code
isort src/ tests/         # Sort imports
flake8 src/ tests/        # Lint code
mypy src/                # Type checking
```

For detailed uv workflows, see [UV Workflows Guide](./docs/UV_WORKFLOWS.md).

For contribution guidelines, see [CONTRIBUTING.md](./.github/CONTRIBUTING.md).

## 📚 Documentation

### Core Documentation
- **[Getting Started Guide](./GETTING_STARTED.md)** - Comprehensive setup and usage guide
- **[Advanced Template Features](./docs/ADVANCED_FEATURES.md)** - Variables, conditionals, and imports
- **[Editor Adapters](./docs/ADAPTERS.md)** - Detailed guide to all supported AI editors
- **[Implementation Roadmap](./docs/IMPLEMENTATION_ROADMAP.md)** - Development progress and plans

### Key Features

#### 🔄 Variable Substitution
Use template variables to create reusable, customizable prompts:

```yaml
metadata:
  title: "{{{ PROJECT_NAME }}} Assistant"
  author: "{{{ AUTHOR_EMAIL }}}"

variables:
  PROJECT_NAME: "MyProject"
  AUTHOR_EMAIL: "team@example.com"
```

Override variables from CLI:
```bash
promptrek generate --editor claude project.promptrek.yaml \
  -V PROJECT_NAME="CustomProject" \
  -V AUTHOR_EMAIL="custom@example.com"
```

#### 🎯 Conditional Instructions
Provide editor-specific instructions:

```yaml
conditions:
  - if: "EDITOR == \"claude\""
    then:
      instructions:
        general:
          - "Claude: Provide detailed explanations"
  - if: "EDITOR == \"continue\""
    then:
      instructions:
        general:
          - "Continue: Generate comprehensive completions"
```

#### 📦 Import System
Share common configurations across projects:

```yaml
imports:
  - path: "shared/base-config.promptrek.yaml"
    prefix: "shared"

# Imported instructions get prefixed: [shared] Follow coding standards
# Imported examples get prefixed: shared_example_name
# Imported variables get prefixed: shared_VARIABLE_NAME
```

#### 🎨 Multiple Editor Support
Generate optimized configurations for all major AI coding assistants:

- **GitHub Copilot** → `.github/copilot-instructions.md` + path-specific instructions
- **Cursor** → `.cursor/rules/index.mdc` + `.cursor/rules/*.mdc` + `AGENTS.md` with modern rule types and project overview
- **Continue** → `config.yaml` + `.continue/rules/*.md` with advanced rule system
- **Kiro** → `.kiro/steering/*.md` + `.kiro/specs/*.md` with comprehensive guidance
- **Cline** → `.clinerules` with project-specific rules
- **Claude Code** → `.claude/context.md`
- **Codeium** → `.codeium/context.json` + `.codeiumrc`

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🌐 Website

Visit our comprehensive [GitHub Pages site](https://flamingquaks.github.io/promptrek) for:
- Detailed documentation and user guides
- Quick start tutorials
- Contributing guidelines
- Community feedback and support
