# User Guide

Welcome to the PrompTrek User Guide! This comprehensive guide covers everything you need to know to effectively use PrompTrek for managing AI editor configurations.

## Getting Started

PrompTrek is a universal prompt management system that allows you to define AI assistant prompts once and generate configurations for multiple AI-powered code editors. This guide will help you understand and leverage all of PrompTrek's features.

## What's in This Guide

### Core Concepts

- **[UPF Specification](upf-specification.md)** - Learn about the Universal Prompt Format, including all schema versions (v2.0, v2.1, v3.0, v3.1) and how to structure your prompt files
- **[Adapters](adapters/index.md)** - Understand how PrompTrek supports different AI editors through adapters
- **[Adapter Capabilities](adapters/capabilities.md)** - Compare features across different editor adapters

### Features & Workflows

- **[Plugins](plugins/index.md)** - Learn about MCP servers, custom commands, autonomous agents, and event hooks
- **[Sync Workflow](workflows/sync.md)** - Import and synchronize editor configurations back to PrompTrek format
- **[Pre-commit Integration](workflows/pre-commit.md)** - Automate validation and prevent committing generated files

## Quick Reference

### Supported Editors

PrompTrek supports 9 AI-powered code editors:

- **Claude Code** - Comprehensive markdown context with full plugin ecosystem
- **GitHub Copilot** - Repository-wide and path-specific instructions
- **Cursor** - Modern .mdc rules system with metadata
- **Continue** - Modular YAML-based configuration
- **Cline** - Autonomous VSCode agent
- **Windsurf** - Organized markdown rules
- **Kiro** - Steering documents for AI guidance
- **Amazon Q** - AWS-integrated workflows
- **JetBrains AI** - IDE-integrated configuration

### Common Tasks

#### Generate Editor Configurations

```bash
# Generate for a specific editor
promptrek generate --editor claude project.promptrek.yaml

# Generate for all configured editors
promptrek generate --all project.promptrek.yaml

# Generate with variable overrides
promptrek generate --editor cursor project.promptrek.yaml \
  -V PROJECT_NAME="MyProject" \
  -V ENVIRONMENT="production"
```

#### Sync Editor Files Back

```bash
# Sync from Continue editor files
promptrek sync --editor continue --source-dir . --output project.promptrek.yaml

# Sync from GitHub Copilot files
promptrek sync --editor copilot --source-dir . --output project.promptrek.yaml
```

#### Validate Configuration

```bash
# Validate a PrompTrek file
promptrek validate project.promptrek.yaml

# Validate all .promptrek.yaml files in a directory
find . -name "*.promptrek.yaml" | xargs -I {} promptrek validate {}
```

## Schema Versions

PrompTrek supports multiple schema versions for backward compatibility:

- **v3.1.0** (Current) - Refined agent model with `prompt` field, workflow support
- **v3.0.0** (Stable) - Top-level plugin fields, cleaner architecture
- **v2.1.0** (Legacy) - Markdown-first with nested plugin support
- **v2.0.0** (Legacy) - Markdown-first, simpler format

**Recommendation**: Use schema v3.1.0 for all new projects.

## Key Features

### Variable Substitution

Use template variables for dynamic content:

```yaml
schema_version: "3.1.0"
metadata:
  title: "{{{ PROJECT_NAME }}} Assistant"

content: |
  # {{{ PROJECT_NAME }}} Development Guide

  Maintained by {{{ AUTHOR_NAME }}} ({{{ AUTHOR_EMAIL }}).

variables:
  PROJECT_NAME: "MyProject"
  AUTHOR_NAME: "Development Team"
  AUTHOR_EMAIL: "dev@example.com"
```

### Multi-Document Support

Organize content across multiple documents:

```yaml
schema_version: "3.1.0"
content: |
  # General Guidelines
  - Write clean code
  - Follow best practices

documents:
  - name: "typescript"
    content: |
      # TypeScript Guidelines
      - Use strict TypeScript settings
    description: "TypeScript coding guidelines"
    file_globs: "**/*.{ts,tsx}"
```

### Plugin Ecosystem

Configure the full plugin ecosystem (schema v3.0+):

- **MCP Servers** - Model Context Protocol integrations
- **Custom Commands** - Slash commands for common tasks
- **Autonomous Agents** - AI agents with specific tools and permissions
- **Event Hooks** - Automated workflows triggered by events

## Migration Guides

### Migrating to v3.1.0

```bash
# Automatic migration
promptrek migrate project.promptrek.yaml --output project-v3.1.promptrek.yaml

# Manual update: Change agent field names
# Before (v3.0.0)
agents:
  - name: my-agent
    system_prompt: "You are..."

# After (v3.1.0)
agents:
  - name: my-agent
    prompt: "You are..."
```

### Migrating to v3.0.0

```bash
# Migrate from v2.1.0 to v3.0.0
promptrek migrate project.promptrek.yaml -o project-v3.promptrek.yaml
```

## Best Practices

### Version Control

1. **Commit** only `.promptrek.yaml` source files
2. **Gitignore** generated editor configuration files
3. **Use** pre-commit hooks to prevent accidental commits

### Organization

Structure your prompts for maintainability:

```
project/
├── .promptrek.yaml              # Main project prompt
├── shared/
│   ├── coding-standards.promptrek.yaml
│   └── testing-guidelines.promptrek.yaml
└── README.md
```

### Team Collaboration

For teams using PrompTrek:

1. **Document** your prompt structure in the README
2. **Share** variable definitions via `.promptrek/variables.promptrek.yaml`
3. **Use** pre-commit hooks for consistency
4. **Generate** locally - don't commit generated files

## Getting Help

- **Documentation**: [https://promptrek.ai](https://promptrek.ai)
- **GitHub Issues**: [Report bugs and request features](https://github.com/flamingquaks/promptrek/issues)
- **GitHub Discussions**: [Ask questions and share ideas](https://github.com/flamingquaks/promptrek/discussions)

## Next Steps

Ready to dive deeper? Check out:

1. **[UPF Specification](upf-specification.md)** - Understand the schema in detail
2. **[Adapters](adapters/index.md)** - Learn about editor-specific configurations
3. **[Sync Workflow](workflows/sync.md)** - Master the round-trip workflow
4. **[Pre-commit Integration](workflows/pre-commit.md)** - Set up automated validation
