# promptrek init

Initialize a new universal prompt file in your project.

## Synopsis

```bash
promptrek init [OPTIONS]
```

## Description

The `init` command creates a new PrompTrek configuration file (`project.promptrek.yaml`) in your project. It sets up a basic template with metadata, content structure, and optional pre-commit hooks for managing AI editor prompts.

This command is your starting point for using PrompTrek in a project. It creates a v3 schema file by default, which uses a markdown-first approach for maximum flexibility.

## Options

### Template Options

**`-t, --template TEMPLATE`**
: Template to use for initialization. Available templates:
  - `basic` (default): Simple project template
  - `react`: React/TypeScript project template
  - `api`: API service template

**`-o, --output PATH`**
: Output file path (default: `project.promptrek.yaml`)

### Schema Version Options

**`--v3`** (default)
: Use v3 schema format (recommended) - markdown-first with top-level plugin fields

**`--v2`**
: Use v2 schema format (legacy) - markdown-first with nested plugins

**`--v1`**
: Use v1 schema format (legacy) - structured fields

### Setup Options

**`--setup-hooks`**
: Automatically set up and activate pre-commit hooks after creating the file

## Examples

### Basic Initialization

Create a basic PrompTrek configuration file:

```bash
promptrek init
```

This creates `project.promptrek.yaml` with:
- Basic metadata (title, description, version, author)
- Sample content with development guidelines
- Example code snippets
- Variable placeholders

### Initialize with Template

Use a specific template for your project type:

```bash
# React/TypeScript project
promptrek init --template react

# API service project
promptrek init --template api

# Basic project (explicit)
promptrek init --template basic
```

### Custom Output Location

Specify a custom output file:

```bash
promptrek init --output custom-config.promptrek.yaml
promptrek init -o configs/ai-prompts.promptrek.yaml
```

### Initialize with Hooks

Create configuration and set up pre-commit hooks in one step:

```bash
promptrek init --setup-hooks
```

This will:
1. Create `project.promptrek.yaml`
2. Configure `.gitignore` to exclude editor files
3. Set up `.pre-commit-config.yaml` with PrompTrek hooks
4. Activate hooks in your git repository

### Legacy Schema Versions

Create configuration using older schema versions:

```bash
# v2 schema (legacy)
promptrek init --v2

# v1 schema (not recommended)
promptrek init --v1
```

!!! warning "Schema Version Compatibility"
    New projects should use v3 (default). Only use v2 or v1 if you need compatibility with older PrompTrek versions or have existing v1/v2 configurations to maintain.

## Created Files and Configuration

### Primary File: project.promptrek.yaml

The init command creates a YAML file with this structure (v3 schema):

```yaml
schema_version: "3.0.0"

metadata:
  title: "My Project Assistant"
  description: "AI assistant configuration for my project"
  version: "1.0.0"
  author: "Your Name <your.email@example.com>"
  created: "2024-01-01"
  updated: "2024-01-01"
  tags:
    - project
    - ai-assistant

content: |
  # My Project Assistant

  AI assistant configuration for my project

  ## Project Details
  **Project Type:** web_application
  **Technologies:** python, javascript, react

  ## Development Guidelines

  ### General Principles
  - Write clean, readable, and maintainable code
  - Follow existing code patterns and conventions
  - Add appropriate comments for complex logic

  [... more content ...]

variables:
  PROJECT_NAME: "My Project"
  AUTHOR_EMAIL: "your.email@example.com"
```

### .gitignore Configuration

The command automatically adds to `.gitignore`:

```
# PrompTrek user-specific config (not committed)
.promptrek/

# Editor-specific generated files (if ignore_editor_files is enabled)
.cursorrules
.claude/
.continue/
.github/copilot-instructions.md
# ... more patterns
```

### Pre-commit Hooks (if --setup-hooks used)

Creates or updates `.pre-commit-config.yaml`:

```yaml
repos:
  - repo: local
    hooks:
      - id: check-promptrek-generated
        name: Check PrompTrek generated files
        entry: promptrek check-generated
        language: system
        files: '\.(cursorrules|claude|continue|copilot)'
```

## Template Details

### Basic Template

General-purpose template suitable for any project:

```yaml
content: |
  # My Project Assistant

  ## Project Details
  **Project Type:** web_application
  **Technologies:** python, javascript, react

  ## Development Guidelines
  - Write clean, readable code
  - Follow existing patterns
  - Add appropriate comments
```

### React Template

Optimized for React/TypeScript projects:

```yaml
content: |
  # React TypeScript Project Assistant

  ## Project Details
  **Project Type:** web_application
  **Technologies:** typescript, react, vite, tailwindcss

  ## Development Guidelines
  - Use TypeScript for all new files
  - Follow React functional component patterns
  - Prefer arrow functions for components
  - Use TypeScript interfaces for props
```

### API Template

Designed for API service projects:

```yaml
content: |
  # API Service Assistant

  ## Project Details
  **Project Type:** api_service
  **Technologies:** python, fastapi, postgresql, sqlalchemy

  ## Development Guidelines
  - Follow RESTful API design principles
  - Implement proper error handling
  - Use async/await for database operations
  - Validate all user inputs
```

## Next Steps

After running `promptrek init`, you should:

1. **Edit the configuration** to match your project:
   ```bash
   vim project.promptrek.yaml
   ```

2. **Validate the configuration**:
   ```bash
   promptrek validate project.promptrek.yaml
   ```

3. **Generate editor configurations**:
   ```bash
   promptrek generate --all
   # or for specific editor
   promptrek generate --editor claude
   ```

4. **Set up git hooks** (if not done during init):
   ```bash
   promptrek install-hooks --activate
   promptrek config-ignores
   ```

## Interactive Workflow

The init command is also available in interactive mode with a guided setup:

```bash
promptrek
# Select: "🚀 Initialize new project"
```

Interactive mode provides:
- Template selection with descriptions
- Schema version choice with recommendations
- Pre-commit hook setup option
- .gitignore configuration option
- Immediate generation option after initialization

## Common Patterns

### Initializing Multiple Projects

For monorepos or multiple configurations:

```bash
# Main project config
promptrek init --output project.promptrek.yaml

# Backend-specific config
promptrek init --output backend.promptrek.yaml --template api

# Frontend-specific config
promptrek init --output frontend.promptrek.yaml --template react
```

### Re-initializing Existing Projects

If `project.promptrek.yaml` exists, you'll be prompted:

```bash
$ promptrek init
File project.promptrek.yaml already exists. Overwrite? [y/N]:
```

To skip the prompt and overwrite:

```bash
# Use --force in newer versions, or
# Delete existing file first
rm project.promptrek.yaml
promptrek init
```

## Troubleshooting

### File Already Exists

**Problem**: `project.promptrek.yaml` already exists

**Solution**:
- Answer 'y' when prompted to overwrite, or
- Use different output path with `--output`, or
- Delete the existing file first

### Permission Denied

**Problem**: Cannot create file due to permissions

**Solution**:
```bash
# Check directory permissions
ls -la

# Make directory writable
chmod u+w .

# Try again
promptrek init
```

### Hook Installation Fails

**Problem**: Pre-commit hooks fail to install with `--setup-hooks`

**Solution**:
```bash
# Install pre-commit first
pip install pre-commit

# Then run init with hooks
promptrek init --setup-hooks

# Or install hooks separately
promptrek install-hooks --activate
```

## Tips and Best Practices

!!! tip "Start Simple"
    Begin with the basic template and customize it for your project rather than starting from scratch.

!!! tip "Use Templates as References"
    Even if none of the templates perfectly match your project, they provide good examples of structure and content.

!!! tip "Customize Immediately"
    After initialization, edit the file to add project-specific guidelines, examples, and requirements.

!!! tip "Version Control"
    Commit `project.promptrek.yaml` to version control, but not the generated editor files (use `--setup-hooks` or `config-ignores` to handle this automatically).

!!! warning "Don't Commit User Config"
    The `.promptrek/` directory contains user-specific configuration and should be in `.gitignore` (automatically added by init).

## See Also

- [generate command](generate.md) - Generate editor configurations from PrompTrek file
- [validate command](validate.md) - Validate PrompTrek configuration
- [UPF Specification](../../user-guide/upf-specification.md) - Detailed schema documentation
- [Getting Started](../../getting-started/quick-start.md) - Complete setup guide
- [install-hooks command](../index.md#install-hooks) - Pre-commit hooks setup
