---
layout: default
title: Project Structure
---

# Project Structure and Conventions

## Repository Structure

```
promptrek/
├── README.md                     # Project overview and quick start
├── LICENSE                       # MIT License
├── .gitignore                    # Git ignore patterns
├── pyproject.toml               # Python project configuration
├── requirements.txt             # Python dependencies
├── setup.py                     # Python package setup (if needed)
│
├── src/                         # Source code
│   └── promptrek/                  # Main package
│       ├── __init__.py          # Package initialization
│       ├── cli/                 # Command-line interface
│       ├── core/                # Core functionality
│       ├── adapters/            # Editor adapters
│       ├── templates/           # Built-in templates
│       └── utils/               # Utility functions
│
├── tests/                       # Test suite
│   ├── unit/                    # Unit tests
│   ├── integration/             # Integration tests
│   ├── fixtures/                # Test data and fixtures
│   └── conftest.py              # Pytest configuration
│
├── docs/                        # Documentation
│   ├── PLANNING.md              # Project planning (this phase)
│   ├── EDITOR_RESEARCH.md       # Editor research and findings
│   ├── ARCHITECTURE.md          # System architecture
│   ├── UPF_SPECIFICATION.md     # Universal Prompt Format spec
│   ├── IMPLEMENTATION_ROADMAP.md # Development roadmap
│   ├── USER_GUIDE.md            # User documentation
│   ├── DEVELOPER_GUIDE.md       # Developer documentation
│   ├── EDITOR_GUIDES/           # Editor-specific guides
│   │   ├── copilot.md
│   │   ├── cursor.md
│   │   └── continue.md
│   └── API_REFERENCE.md         # API documentation
│
├── examples/                    # Example configurations
│   ├── basic/                   # Simple examples
│   │   ├── web-app.promptrek.yaml
│   │   ├── api-service.promptrek.yaml
│   │   └── library.promptrek.yaml
│   ├── advanced/                # Complex examples
│   │   ├── monorepo.promptrek.yaml
│   │   ├── microservices.promptrek.yaml
│   │   └── enterprise.promptrek.yaml
│   └── templates/               # Project templates
│       ├── react-typescript/
│       ├── node-api/
│       └── python-fastapi/
│
├── scripts/                     # Development and build scripts
│   ├── build.sh                 # Build script
│   ├── test.sh                  # Test runner
│   ├── lint.sh                  # Linting script
│   └── release.sh               # Release preparation
│
├── .github/                     # GitHub-specific files
│   ├── workflows/               # GitHub Actions
│   │   ├── ci.yml               # Continuous integration
│   │   ├── release.yml          # Release automation
│   │   └── docs.yml             # Documentation deployment
│   ├── ISSUE_TEMPLATE/          # Issue templates
│   ├── PULL_REQUEST_TEMPLATE.md # PR template
│   └── CONTRIBUTING.md          # Contribution guidelines
│
└── .promptrek/                    # Project's own prompt configuration
    ├── project.promptrek.yaml     # Universal prompt for this project
    └── .promptrek.config.json     # Project-specific configuration
```

## Source Code Structure

### `src/promptrek/` - Main Package

```
src/promptrek/
├── __init__.py                  # Package info, version, exports
├── cli/                         # Command-line interface
│   ├── __init__.py
│   ├── main.py                  # Main CLI entry point
│   ├── commands/                # Individual commands
│   │   ├── __init__.py
│   │   ├── init.py              # `promptrek init` command
│   │   ├── generate.py          # `promptrek generate` command
│   │   ├── validate.py          # `promptrek validate` command
│   │   ├── list_editors.py      # `promptrek list-editors` command
│   │   └── preview.py           # `promptrek preview` command
│   └── utils.py                 # CLI utility functions
├── core/                        # Core functionality
│   ├── __init__.py
│   ├── models.py                # Data models (UniversalPrompt, etc.)
│   ├── parser.py                # UPF file parsing
│   ├── validator.py             # UPF validation logic
│   ├── config.py                # Configuration management
│   └── exceptions.py            # Custom exceptions
├── adapters/                    # Editor adapters
│   ├── __init__.py
│   ├── base.py                  # Base adapter interface
│   ├── registry.py              # Adapter registration system
│   ├── copilot.py               # GitHub Copilot adapter
│   ├── cursor.py                # Cursor editor adapter
│   ├── continue.py              # Continue extension adapter
│   ├── codeium.py               # Codeium adapter
│   └── utils.py                 # Adapter utilities
├── templates/                   # Built-in templates
│   ├── __init__.py
│   ├── copilot/                 # Copilot templates
│   │   ├── instructions.md.j2
│   │   └── config.json.j2
│   ├── cursor/                  # Cursor templates
│   │   ├── index.mdc.j2         # Main project overview template
│   │   └── rule.mdc.j2          # Category-specific rule template
│   ├── continue/                # Continue templates
│   │   └── config.json.j2
│   └── shared/                  # Shared template components
│       ├── common.md.j2
│       └── examples.md.j2
└── utils/                       # Utility modules
    ├── __init__.py
    ├── file_utils.py            # File system operations
    ├── template_utils.py        # Template processing
    ├── variable_utils.py        # Variable substitution
    └── validation_utils.py      # Validation helpers
```

## Naming Conventions

### File and Directory Names
- **Python files**: `snake_case.py`
- **Directories**: `snake_case` or `kebab-case` for docs
- **Templates**: `template_name.extension.j2`
- **UPF files**: `*.promptrek.yaml` or `*.promptrek.yml`
- **Configuration files**: `.promptrek.config.json`

### Python Code Conventions
- **Classes**: `PascalCase`
- **Functions/Methods**: `snake_case`
- **Variables**: `snake_case`
- **Constants**: `UPPER_SNAKE_CASE`
- **Private members**: `_leading_underscore`

### Template Conventions
- **Template files**: Jinja2 format with `.j2` extension
- **Variable names**: `{{ variable_name }}`
- **Filters**: Use built-in Jinja2 filters when possible
- **Comments**: `{# This is a comment #}`

## Configuration File Locations

### Global Configuration
```
~/.promptrek/
├── config.json              # Global user configuration
├── templates/               # User-defined templates
│   ├── copilot/
│   ├── cursor/
│   └── custom/
└── cache/                   # Template and validation cache
```

### Project Configuration
```
project-root/
├── .promptrek.yaml                # Universal prompt file
├── .promptrek.config.json     # Project-specific configuration
└── .promptrek/                # Project-specific PrompTrek files
    ├── templates/           # Project templates
    └── overrides/           # Template overrides
```

### Generated Files
```
project-root/
├── .github/
│   └── copilot-instructions.md    # Generated Copilot prompts
├── .copilot/
│   └── instructions.md             # Alternative Copilot location
├── .cursor/
│   └── rules/
│       ├── index.mdc               # Main project overview (Always rule)
│       └── *.mdc                   # Category-specific rules (Auto Attached)
├── .continue/
│   └── config.json                 # Generated Continue prompts
└── .ai-prompts/                    # Centralized output (optional)
    ├── copilot/
    ├── cursor/
    └── continue/
```

## Development Conventions

### Testing Structure
```
tests/
├── unit/                    # Unit tests (one file per module)
│   ├── test_parser.py
│   ├── test_validator.py
│   ├── test_adapters.py
│   └── test_cli.py
├── integration/             # Integration tests
│   ├── test_full_workflow.py
│   ├── test_editor_generation.py
│   └── test_cli_integration.py
├── fixtures/                # Test data
│   ├── valid_prompts/
│   ├── invalid_prompts/
│   ├── templates/
│   └── expected_outputs/
└── conftest.py              # Pytest configuration and fixtures
```

### Documentation Structure
```
docs/
├── planning/                # Planning documents (this phase)
│   ├── PLANNING.md
│   ├── EDITOR_RESEARCH.md
│   ├── ARCHITECTURE.md
│   ├── UPF_SPECIFICATION.md
│   └── IMPLEMENTATION_ROADMAP.md
├── user/                    # User documentation
│   ├── USER_GUIDE.md
│   ├── QUICK_START.md
│   ├── INSTALLATION.md
│   └── TROUBLESHOOTING.md
├── developer/               # Developer documentation
│   ├── DEVELOPER_GUIDE.md
│   ├── CONTRIBUTING.md
│   ├── API_REFERENCE.md
│   └── TESTING.md
└── editors/                 # Editor-specific guides
    ├── copilot.md
    ├── cursor.md
    ├── continue.md
    └── adding_new_editor.md
```

## Quality Standards

### Code Quality
- **Type Hints**: All public functions must have type hints
- **Docstrings**: All public classes and functions must have docstrings
- **Error Handling**: Proper exception handling with custom exceptions
- **Logging**: Use structured logging throughout the application

### Testing Standards
- **Coverage**: Minimum 90% test coverage
- **Unit Tests**: Test individual functions and classes
- **Integration Tests**: Test complete workflows
- **Fixtures**: Reusable test data and configurations

### Documentation Standards
- **API Documentation**: Auto-generated from docstrings
- **User Guide**: Step-by-step instructions with examples
- **Developer Guide**: Setup, architecture, and contribution guidelines
- **Editor Guides**: Specific setup for each supported editor

## Version Control Conventions

### Branching Strategy
- **main**: Production-ready code
- **develop**: Integration branch for features
- **feature/**: Individual feature branches
- **hotfix/**: Critical bug fixes
- **release/**: Release preparation

### Commit Messages
```
type(scope): description

[optional body]

[optional footer]
```

**Types**: feat, fix, docs, style, refactor, test, chore, ci, build, perf, revert
**Scopes**: cli, core, adapters, templates, docs, parser, validator, utils, tests, deps, changelog

**Examples**:
```
feat(adapters): add Cursor editor support
fix(parser): handle empty instructions gracefully
docs(guides): add Copilot setup instructions
chore(deps): update dependencies to latest versions
ci(changelog): add automated changelog generation
```

### Automated Changelog Generation
The project uses conventional commits to automatically generate changelogs:
- **Changelog format**: Based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/)
- **Automation**: GitHub Actions automatically update `CHANGELOG.md` on releases
- **Commit validation**: Pull requests validate commit message format with commitlint
- **Configuration**: `.commitlintrc.json` and `.conventional-changelog.json` define rules

### Release Versioning
- **Semantic Versioning**: MAJOR.MINOR.PATCH
- **Pre-release**: alpha, beta, rc suffixes
- **Tags**: v1.0.0, v1.1.0-beta.1
- **Automated releases**: Release workflow generates changelog and creates GitHub releases

## Performance and Scalability

### File Organization
- **Lazy Loading**: Load adapters and templates only when needed
- **Caching**: Cache parsed templates and validation results
- **Streaming**: Process large files without loading entirely into memory

### Resource Management
- **Memory**: Minimize memory usage for large configurations
- **Disk I/O**: Batch file operations when possible
- **Network**: No network dependencies for core functionality

## Security Considerations

### Template Security
- **Sandboxing**: Restrict template execution capabilities
- **Input Validation**: Validate all user inputs
- **Path Traversal**: Prevent writing outside project boundaries

### Configuration Security
- **File Permissions**: Set appropriate permissions on generated files
- **Sensitive Data**: Never log or cache sensitive information
- **User Input**: Sanitize all user-provided data