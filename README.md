<div align="center">
  <img src="gh-pages/assets/promptrek-logo-with-text.png" alt="PrompTrek" width="400">

  [![CI](https://github.com/flamingquaks/promptrek/actions/workflows/ci.yml/badge.svg)](https://github.com/flamingquaks/promptrek/actions/workflows/ci.yml)
  [![PR Validation](https://github.com/flamingquaks/promptrek/actions/workflows/pr.yml/badge.svg)](https://github.com/flamingquaks/promptrek/actions/workflows/pr.yml)
  [![Python Versions](https://img.shields.io/badge/python-3.9%20%7C%203.10%20%7C%203.11%20%7C%203.12-blue)](https://github.com/flamingquaks/promptrek)
  [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

  *Taking your AI editor configurations on a journey across every platform!*
</div>

A universal configuration solution that takes your prompts, MCP servers, custom commands, autonomous agents, and event hooks on a journey across every AI editor. Define your complete AI editor setup once in a standardized format, then PrompTrek automatically generates optimized configurations for GitHub Copilot, Cursor, Continue, Claude Code, and more.

## 🎯 Problem It Solves

AI coding assistants like GitHub Copilot, Cursor, Continue, and others all use different prompt formats and configuration methods. When working across teams or switching between editors, you have to maintain separate prompt configurations for each tool. PrompTrek solves this by:

- **Universal Format**: Create prompts once in a standardized format (now with **schema v3.0.0** - cleaner architecture!)
- **Multi-Editor Support**: Generate prompts for any supported AI editor automatically (no `targets` field needed!)
- **Bidirectional Sync**: Parse editor files back to `.promptrek.yaml` without data loss (lossless sync)
- **Plugin Ecosystem**: Configure MCP servers, custom commands, autonomous agents, and event hooks with clean top-level fields (mcp_servers, commands, agents, hooks)
- **Auto .gitignore Management**: Automatically exclude generated editor files from version control
- **Team Consistency**: Share prompt configurations across team members regardless of their editor choice
- **Easy Migration**: Switch between AI editors without losing your prompt configurations

> **Note on Versioning**: PrompTrek has two version numbers:
> - **Application version** (currently **0.4.0**): The version of the PrompTrek tool itself
> - **Schema version** (v1.x, v2.x, v3.x): The format version of your `.promptrek.yaml` configuration files
>
> Throughout this documentation, version numbers like "v3.0.0" or "v2.1" refer to **schema versions**, not application versions.

## 🚀 Quick Example

1. Create a universal prompt file (`.promptrek.yaml`) using the **schema v3.1 format** (recommended):
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

## 🧙 Interactive CLI Wizard

**New in v0.4.0!** PrompTrek now features an interactive CLI mode that guides you through common workflows without memorizing commands.

### Launch Interactive Mode

Simply run `promptrek` without any command:

```bash
promptrek
```

You'll see a beautiful ASCII banner and an interactive menu:

```
 ____                       _____         _
|  _ \ _ __ ___  _ __ ___  |_   _| __ ___| | __
| |_) | '__/ _ \| '_ ` _ \   | || '__/ _ \ |/ /
|  __/| | | (_) | | | | | |  | || | |  __/   <
|_|   |_|  \___/|_| |_| |_|  |_||_|  \___|_|\_\

Universal AI Editor Prompt Management (v0.4.0)

? What would you like to do?
  ❯ 🚀 Initialize new project
    ⚙️  Generate editor configurations
    🔌 Configure plugins (MCP servers, commands, agents)
    🔄 Migrate schema version
    🔍 Validate configuration
    📤 Sync from editor files
    ❓ Help & Documentation
    👋 Exit
```

### Interactive Workflows

The wizard guides you through:

1. **🚀 Project Initialization**
   - Detects existing configurations
   - Helps you choose schema version (v3.0 recommended)
   - Sets up pre-commit hooks automatically
   - Configures .gitignore for editor files

2. **⚙️ Editor Configuration**
   - Auto-detects your PrompTrek config
   - Interactive editor selection (multi-select)
   - Variable override prompts
   - Headless mode option for autonomous agents
   - Preview mode before generating files

3. **🔌 Plugin Management**
   - List configured MCP servers, commands, agents, and hooks
   - Generate plugin files for selected editors
   - Auto-confirm options for batch operations

4. **🔄 Schema Migration**
   - Guides through v1 → v2 → v3 migration
   - Shows what will change before migrating
   - Optional backup of original files
   - Validates migrated output

5. **🔍 Validation & Sync**
   - Interactive configuration validation
   - Strict mode option
   - Sync editor files back to PrompTrek config
   - Preview changes before applying

### Benefits

- **No memorization required** - Discover features through the interface
- **Guided workflows** - Step-by-step prompts reduce errors
- **Fast onboarding** - New users can start without reading docs
- **Power user friendly** - All CLI commands still work as before
- **CI/CD compatible** - Use `--yes` flag to skip interactive prompts

### Backward Compatibility

All existing CLI commands continue to work exactly as before:

```bash
# Traditional commands still work
promptrek init --template react
promptrek generate --editor cursor
promptrek validate config.yaml

# Force interactive mode with flag
promptrek --interactive
promptrek -i
```

The interactive mode automatically detects if you're in a CI/CD environment (non-TTY) and falls back to showing help text.

## 🔐 Automatic .gitignore Management

PrompTrek automatically manages `.gitignore` to prevent committing generated editor files:

```bash
# Initialize project - automatically adds editor files to .gitignore
promptrek init --output project.promptrek.yaml

# Configure .gitignore manually
promptrek config-ignores

# Remove already-committed editor files from git
promptrek config-ignores --remove-cached
```

**What gets ignored:**
- Generated editor configurations (`.github/copilot-instructions.md`, `.cursor/rules/*.mdc`, etc.)
- User-specific configuration directory (`.promptrek/`) containing `variables.promptrek.yaml` and `user-config.promptrek.yaml`

**Configuration option:**
```yaml
# Disable automatic .gitignore management
ignore_editor_files: false
```

## 📖 Documentation

**📚 Complete documentation is available on our [GitHub Pages site](https://flamingquaks.github.io/promptrek):**

- **[Quick Start Guide](https://flamingquaks.github.io/promptrek/quick-start.html)** - Get up and running in minutes
- **[JSON Schema Files](https://promptrek.ai/schema/)** - Published schemas for v2.0, v2.1, and v3.0 with editor autocompletion support
- **[User Guide](https://flamingquaks.github.io/promptrek/user-guide.html)** - Comprehensive documentation covering:
  - UPF Specification - Universal Prompt Format details
  - Advanced Features - Variables and multi-document support
  - Editor Adapters - All supported AI editors
  - Adapter Capabilities - Feature comparison matrix
  - Sync Feature - Bidirectional synchronization
  - Pre-commit Integration - Automated workflows
- **[Contributing Guide](https://flamingquaks.github.io/promptrek/contributing.html)** - How to contribute to the project

### Developer Resources
For technical architecture and development planning, see the developer documentation on our website:
- [System Architecture](https://flamingquaks.github.io/promptrek/developer/architecture.html) - Technical design and structure
- [Project Structure](https://flamingquaks.github.io/promptrek/developer/project-structure.html) - Repository organization
- [Changelog Process](https://flamingquaks.github.io/promptrek/developer/changelog-process.html) - Contribution guidelines
- [Pre-commit Implementation](https://flamingquaks.github.io/promptrek/developer/pre-commit-implementation.html) - Technical implementation details
- [UV Workflows](https://flamingquaks.github.io/promptrek/developer/uv-workflows.html) - Developer workflows

## 🎨 Supported Editors

### ✅ All Implemented
- **GitHub Copilot** - `.github/copilot-instructions.md`, `.github/instructions/*.instructions.md`, `.github/prompts/*.prompt.md` - Repository-wide and path-specific instructions with bidirectional sync
- **Cursor** - `.cursor/rules/index.mdc`, `.cursor/rules/*.mdc`, `AGENTS.md`, `.cursorignore`, `.cursorindexingignore` - Modern 2025 rules system with metadata-driven configuration (Always/Auto Attached rule types) and project overview
- **Continue** - `.continue/rules/*.md` - Organized markdown rules directory with bidirectional sync support
- **Kiro** - `.kiro/steering/*.md` - Comprehensive steering system with YAML frontmatter
- **Cline** - `.clinerules/*.md`, `.vscode/settings.json` (MCP) - VSCode autonomous AI agent with markdown rules
- **Claude Code** - `.claude/CLAUDE.md`, `.mcp.json`, `.claude/agents/*.md`, `.claude/commands/*.md`, `.claude/settings.local.json` - Rich context format with full plugin ecosystem (MCP servers, custom commands, autonomous agents, event hooks)
- **Windsurf** - `.windsurf/rules/*.md` - Organized markdown rule files for AI-powered coding assistance
- **Amazon Q** - `.amazonq/rules/*.md`, `.amazonq/cli-agents/*.json` - Rules directory and CLI agents with sync support
- **JetBrains AI** - `.assistant/rules/*.md` - Markdown rules for IDE-integrated AI assistance

## 🗂️ Example Configurations

See the [`examples/`](https://github.com/flamingquaks/promptrek/tree/main/examples/) directory for sample configurations:

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

# Clone and install from source
git clone https://github.com/flamingquaks/promptrek.git
cd promptrek
uv sync
```

#### Option 2: Traditional pip

```bash
# Clone and install from source
git clone https://github.com/flamingquaks/promptrek.git
cd promptrek
pip install -e .
```

**Note:** PrompTrek is not yet available on PyPI. Install from source using the methods above.

### Quick Start

```bash
# 1. Initialize a new project with pre-commit hooks (v2 format by default)
uv run promptrek init --template react --output my-project.promptrek.yaml --setup-hooks
# or with traditional pip: promptrek init --template react --output my-project.promptrek.yaml --setup-hooks

# 2. Validate your configuration
uv run promptrek validate my-project.promptrek.yaml

# 3. Generate editor-specific prompts
uv run promptrek generate my-project.promptrek.yaml --all

# 4. Your AI editor prompts are ready!
ls .github/copilot-instructions.md
ls .cursor/rules/index.mdc
ls .continue/rules/
```

**Note:** The `--setup-hooks` flag automatically configures pre-commit hooks to validate your `.promptrek.yaml` files and prevent accidental commits of generated files.

### 🆕 Schema v3.1.0 (Current Configuration Format)

PrompTrek supports schema v3.1.0, which refines the agent model and adds workflow support while maintaining full backward compatibility with schema v3.0.x:

> **Application vs Schema Versions**: PrompTrek application version 0.4.0 supports schema versions v1.x, v2.x, v3.0.x, and v3.1.x. The schema version is specified in your `.promptrek.yaml` file's `schema_version` field.

**What's New in Schema v3.1.0:**
- ✨ **Refined Agent Model** - `prompt` field replaces `system_prompt` for consistency with commands
- 🔄 **Workflow Support** - Multi-step workflows with `multi_step`, `tool_calls`, and structured steps
- ✅ **100% Backward Compatible** - schema v3.0.x and v2.x files continue to work with automatic migration
- 📋 **Production Ready** - Latest stable configuration schema for all new projects

**Before (schema v2.x) vs After (schema v3.1):**
```yaml
# v2.x - Nested structure (legacy)
schema_version: "2.1.0"
plugins:                    # ❌ Wrapper (removed in v3.0)
  mcp_servers: [...]
  commands: [...]

# v3.1 - Flat structure with refined agent model (recommended)
schema_version: "3.1.0"
# No plugins wrapper
mcp_servers: [...]          # ✅ Top-level
commands: [...]             # ✅ Top-level
agents:                     # ✅ Refined model with 'prompt' field
  - name: code-reviewer
    prompt: "You are a code reviewer..."  # ✅ New field name
```

**Migration Between Schema Versions:**
```bash
# Auto-migrate schema v2.x/v3.0 to v3.1
promptrek migrate project.promptrek.yaml -o project-v3.1.promptrek.yaml

# Migrate in place
promptrek migrate project.promptrek.yaml --in-place
```

**Documentation:**
- 📖 [V3 Migration Guide](./docs/V3_MIGRATION_GUIDE.md) - Complete migration instructions
- ⚠️ [Deprecation Warnings](./docs/DEPRECATION_WARNINGS.md) - Understanding deprecation messages
- 🎯 **Recommended for all new projects** - Use v3.1 schema for latest features

### Schema v2.x (Legacy Configuration Format - Deprecated)

The schema v2.x format with nested plugin support (superseded by schema v3.1):

**Migration to Schema v3.1:**
All schema v2.x features are available in schema v3.1 with cleaner syntax:
```bash
# Migrate schema v2.x files to v3.1
uv run promptrek migrate old.promptrek.yaml -o new.promptrek.yaml

# Create new schema v3.1 file (default)
uv run promptrek init

# Schema v2.x files still work but show migration suggestions
uv run promptrek generate old-v2.promptrek.yaml --all
```

**Schema v3.1 Format Example:**
```yaml
schema_version: "3.1.0"
metadata:
  title: "My Project"
  description: "AI assistant"
  version: "1.0.0"
  author: "Your Name"
  tags: [ai, project]

content: |
  # My Project

  ## Guidelines
  - Write clean code
  - Follow best practices

variables:
  PROJECT_NAME: "my-project"
  GITHUB_TOKEN: "ghp_your_token_here"

# Top-level plugin configurations (v3.0 clean structure)
mcp_servers:
    - name: github
      command: npx
      args: ["-y", "@modelcontextprotocol/server-github"]
      env:
        GITHUB_TOKEN: "{{{ GITHUB_TOKEN }}}"
      description: "GitHub API integration"
      trust_metadata:
        trusted: true
        trust_level: full

commands:
    - name: review-code
      description: "Review code for quality"
      prompt: |
        Review the selected code for:
        - Code quality and best practices
        - Security vulnerabilities
        - Performance optimizations
      output_format: markdown

agents:
    - name: test-generator
      description: "Generate unit tests"
      system_prompt: "Generate comprehensive tests with Jest"
      tools: [file_read, file_write, run_tests]
      trust_level: partial
      requires_approval: true

# Optional: For multi-file editors with metadata support
documents:
  - name: "typescript"
    content: |
      # TypeScript Guidelines
      - Use strict TypeScript settings
      - Prefer interfaces over types
    description: "TypeScript coding guidelines"
    file_globs: "**/*.{ts,tsx}"
    always_apply: false  # Auto-attached to TypeScript files only

  - name: "testing"
    content: |
      # Testing Standards
      - Write unit tests for all functions
      - Aim for 80% coverage
    # Metadata fields are optional - smart defaults will be used
```

####  🔌 Plugin Configuration (Schema v3.0+)

PrompTrek supports schema v3.0+ which provides MCP server integration with **clean top-level fields** (no `plugins` wrapper):

**Supported Plugin Types:**
- **MCP Servers** (`mcp_servers`) - Model Context Protocol servers for external tools (filesystem, GitHub, databases, etc.)
- **Custom Commands** (`commands`) - Slash commands for AI editors
- **Autonomous Agents** (`agents`) - AI agents with specific tools and permissions
- **Event Hooks** (`hooks`) - Event-driven automation workflows

**Editor Support Matrix:**

| Editor | MCP Servers | Custom Commands | Agents | Config Location |
|--------|-------------|-----------------|--------|-----------------|
| **Claude Code** | ✅ | ✅ | ✅ | `.mcp.json` (project root) |
| **Cursor** | ✅ | ✅ | ✅ | `.cursor/mcp.json` (project) |
| **Continue** | ✅ | ✅ | ⚠️ | `.continue/config.json` (unified) |
| **Cline** | ✅ | ⚠️ | ⚠️ | `.vscode/settings.json` (project) |
| **Kiro** | ✅ | ⚠️ | ⚠️ | `.kiro/settings/mcp.json` (project) |
| **Windsurf** | ✅ | ⚠️ | ⚠️ | `~/.codeium/windsurf/mcp_config.json` (system-wide) |
| **Amazon Q** | ✅ | ⚠️ | ⚠️ | `.amazonq/mcp.json` (project) |

✅ = Full support | ⚠️ = Partial/Planned

**MCP Server Configuration Strategy:**

PrompTrek uses a **project-first** strategy with system-wide fallback:

1. **Try project-level first** (`.editor/mcp.json`) - Preferred for team collaboration
2. **Fall back to system-wide** (`~/.editor/mcp.json`) - Only when project-level isn't supported
3. **User confirmation required** - For system-wide changes (especially Windsurf)

**Plugin Commands:**

```bash
# Generate MCP servers for an editor
promptrek plugins generate project.promptrek.yaml -e claude

# Generate for all supported editors
promptrek plugins generate project.promptrek.yaml --all

# Force system-wide generation (skip project-level)
promptrek plugins generate project.promptrek.yaml -e windsurf --force-system-wide

# Auto-confirm system-wide changes (skip prompts)
promptrek plugins generate project.promptrek.yaml -e windsurf --yes

# Dry run to preview without writing
promptrek plugins generate project.promptrek.yaml -e cursor --dry-run -v

# Override variables at generation time
promptrek plugins generate project.promptrek.yaml -e claude \
  -V GITHUB_TOKEN=ghp_newtoken \
  -V API_KEY=secret123
```

**Example Files:**

See [`examples/v21-plugins/`](https://github.com/flamingquaks/promptrek/tree/main/examples/v21-plugins) for comprehensive examples:
- `mcp-servers.promptrek.yaml` - MCP server configurations
- `custom-commands.promptrek.yaml` - Slash command examples
- `autonomous-agents.promptrek.yaml` - Agent configurations
- `complete-example.promptrek.yaml` - All features combined

### Available Commands

- `promptrek init` - Create a new universal prompt file with templates (use `--setup-hooks` to automatically configure pre-commit)
- `promptrek validate` - Check your configuration for errors
- `promptrek generate` - Create editor-specific prompts
- `promptrek preview` - Preview generated output without creating files
- `promptrek sync` - Sync editor files back to PrompTrek format
- `promptrek migrate` - Migrate v1/v2.x files to v3.0 format
- `promptrek plugins list` - List all plugins in a .promptrek.yaml file
- `promptrek plugins generate` - Generate plugin files for a specific editor
- `promptrek plugins validate` - Validate plugin configuration
- `promptrek plugins sync` - Sync plugins from editor files
- `promptrek agents` - ⚠️ **[DEPRECATED]** Generate agent-specific instructions (use `promptrek generate --all` instead)
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

- `.github/copilot-instructions.md`, `.github/instructions/`, `.github/prompts/` - GitHub Copilot
- `.cursor/`, `AGENTS.md`, `.cursorignore`, `.cursorindexingignore` - Cursor
- `.continue/` - Continue
- `.claude/` - Claude Code
- `.windsurf/` - Windsurf
- `.clinerules/` - Cline
- `.kiro/` - Kiro
- `.amazonq/` - Amazon Q
- `.assistant/` - JetBrains AI

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

All commit messages are validated in CI. See [Changelog Process](https://flamingquaks.github.io/promptrek/developer/changelog-process.html) for detailed guidelines.

## 🧪 Testing and Quality Assurance

PrompTrek maintains high quality standards with comprehensive testing:

### Automated Testing
- **Continuous Integration**: Tests run on every push and PR across multiple Python versions (3.9-3.12)
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

For detailed uv workflows, see [UV Workflows Guide](https://flamingquaks.github.io/promptrek/developer/uv-workflows.html).

For contribution guidelines, see [CONTRIBUTING.md](./.github/CONTRIBUTING.md).

## 📚 Documentation

### Core Documentation
- **[Getting Started Guide](./GETTING_STARTED.md)** - Comprehensive setup and usage guide
- **[Advanced Template Features](https://flamingquaks.github.io/promptrek/user-guide/advanced-features.html)** - Variables and multi-document support
- **[Editor Adapters](https://flamingquaks.github.io/promptrek/user-guide/adapters.html)** - Detailed guide to all supported AI editors

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

#### 🎨 Multiple Editor Support
Generate optimized configurations for all major AI coding assistants:

- **GitHub Copilot** → `.github/copilot-instructions.md` + path-specific instructions + bidirectional sync
- **Cursor** → `.cursor/rules/index.mdc` + `.cursor/rules/*.mdc` + `AGENTS.md` with metadata-driven rules (Always/Auto Attached)
- **Continue** → `.continue/rules/*.md` with organized rules + bidirectional sync
- **Kiro** → `.kiro/steering/*.md` with YAML frontmatter
- **Cline** → `.clinerules/*.md` with project-specific rules
- **Claude Code** → `.claude/CLAUDE.md`, `.mcp.json`, `.claude/agents/*.md`, `.claude/commands/*.md`, `.claude/settings.local.json` with full plugin ecosystem
- **Windsurf** → `.windsurf/rules/*.md` with organized guidelines
- **Amazon Q** → `.amazonq/rules/*.md` + CLI agents + sync support
- **JetBrains AI** → `.assistant/rules/*.md` for IDE integration

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🌐 Website

Visit our comprehensive [GitHub Pages site](https://flamingquaks.github.io/promptrek) for:
- Detailed documentation and user guides
- Quick start tutorials
- Contributing guidelines
- Community feedback and support
