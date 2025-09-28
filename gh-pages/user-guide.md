---
layout: default
title: User Guide
---

# Comprehensive User Guide

Welcome to the complete PrompTrek user guide! This documentation covers everything you need to know to effectively use PrompTrek for managing AI editor prompts.

## Table of Contents

1. [Installation and Setup](#installation-and-setup)
2. [Universal Prompt Format (UPF)](#universal-prompt-format-upf)
3. [Command Reference](#command-reference)
4. [Editor-Specific Features](#editor-specific-features)
5. [Advanced Features](#advanced-features)
6. [Best Practices](#best-practices)
7. [Troubleshooting](#troubleshooting)

## Installation and Setup

### System Requirements

- Python 3.9 or higher
- Your preferred AI-enabled code editor

### Installation Options

#### Standard Installation
```bash
pip install promptrek
```

#### Development Installation
```bash
git clone https://github.com/flamingquaks/promptrek.git
cd promptrek
pip install -e .
```

#### Using uv (Recommended for Development)
```bash
git clone https://github.com/flamingquaks/promptrek.git
cd promptrek
uv sync
```

### Verification

Verify your installation:
```bash
promptrek --version
promptrek list-editors
```

## Universal Prompt Format (UPF)

The Universal Prompt Format is the core of PrompTrek. It's a YAML-based format that allows you to define prompts once and generate editor-specific configurations.

### Basic Structure

```yaml
schema_version: "1.0.0"

metadata:
  title: "Project Assistant"
  description: "AI assistant configuration"
  version: "1.0.0"
  author: "Your Name <email@example.com>"
  created: "2024-01-01"
  updated: "2024-01-01"

targets: ["copilot", "cursor", "continue"]

context:
  project_type: "web_application"
  technologies: ["typescript", "react", "node.js"]

instructions:
  general:
    - "Write clean, readable code"
    - "Follow existing patterns"
  code_style:
    - "Use meaningful variable names"
    - "Add comprehensive comments"

examples:
  component: |
    ```typescript
    interface Props {
      title: string;
    }
    
    export const Component: React.FC<Props> = ({ title }) => {
      return <div>{title}</div>;
    };
    ```
```

### Field Reference

#### metadata (required)
Project metadata and authorship information.

**Fields:**
- `title` (required): Human-readable title
- `description` (required): Brief description
- `version` (required): Semantic version
- `author` (required): Author name and email
- `created` (optional): Creation date (ISO 8601)
- `updated` (optional): Last update date (ISO 8601)

#### targets (required)
List of target editors for prompt generation.

**Supported values:**
- `copilot` - GitHub Copilot
- `cursor` - Cursor
- `continue` - Continue
- `amazonq` - Amazon Q
- `jetbrains` - JetBrains AI
- `kiro` - Kiro
- `cline` - Cline

#### context (optional)
Project context information that influences prompt generation.

**Fields:**
- `project_type`: Type of project (web_application, api, library, etc.)
- `technologies`: Array of technologies used
- `frameworks`: Array of frameworks used
- `language`: Primary programming language

#### instructions (required)
Structured instructions organized by category.

**Common categories:**
- `general`: General coding guidelines
- `code_style`: Code style and formatting
- `architecture`: Architectural patterns
- `testing`: Testing guidelines
- `security`: Security considerations
- `performance`: Performance guidelines

#### examples (optional)
Code examples organized by type.

#### variables (optional)
Dynamic variables for template substitution.

```yaml
variables:
  PROJECT_NAME: "My Project"
  AUTHOR_NAME: "John Doe"
  TECH_STACK: "React, TypeScript, Node.js"
```

## Command Reference

### `promptrek init`

Initialize a new universal prompt file.

```bash
promptrek init [OPTIONS]
```

**Options:**
- `--output FILE`: Output filename (required)
- `--template TEXT`: Template to use (basic, react, api)
- `--interactive`: Interactive mode for customization

**Examples:**
```bash
promptrek init --output my-project.promptrek.yaml
promptrek init --template react --output react-app.promptrek.yaml
```

### `promptrek validate`

Validate a universal prompt file.

```bash
promptrek validate [OPTIONS] INPUT_FILE
```

**Options:**
- `--strict`: Treat warnings as errors
- `--verbose`: Show detailed validation information

**Examples:**
```bash
promptrek validate my-project.promptrek.yaml
promptrek validate --strict --verbose my-project.promptrek.yaml
```

### `promptrek generate`

Generate editor-specific prompts.

```bash
promptrek generate [OPTIONS]
```

**Options:**
- `--input FILE`: Input universal prompt file (required)
- `--editor TEXT`: Target editor (copilot, cursor, continue, etc.)
- `--all`: Generate for all configured editors
- `--output DIR`: Output directory (default: current directory)
- `--dry-run`: Show what would be generated without creating files
- `--force`: Overwrite existing files

**Examples:**
```bash
# Generate for specific editor
promptrek generate --editor copilot --input my-project.promptrek.yaml

# Generate for all editors
promptrek generate --all --input my-project.promptrek.yaml

# Dry run to see what would be generated
promptrek generate --all --input my-project.promptrek.yaml --dry-run
```

### `promptrek list-editors`

List supported editors and their capabilities.

```bash
promptrek list-editors [OPTIONS]
```

**Options:**
- `--format TEXT`: Output format (table, json, yaml)

## Editor-Specific Features

### GitHub Copilot

PrompTrek generates comprehensive Copilot configurations:

**Generated files:**
- `.github/copilot-instructions.md` - Repository-wide instructions
- `.github/instructions/*.instructions.md` - Path-specific instructions
- `AGENTS.md`, `CLAUDE.md`, `GEMINI.md` - Agent-specific instructions

**Features:**
- Repository-wide prompt configuration
- Path-specific instructions with glob patterns
- Agent-specific customizations
- YAML frontmatter for metadata

### Cursor (Modernized 2025)

Advanced rule system following Cursor IDE's 2025 best practices:

**Generated files:**
- `.cursor/rules/index.mdc` - Main project overview (Always rule)
- `.cursor/rules/*.mdc` - Category-specific rules (Auto Attached)
- `AGENTS.md` - Agent instructions
- `.cursorignore` - Enhanced exclusion patterns
- `.cursorindexingignore` - Intelligent indexing control

**Features:**
- Modern rule types (Always/Auto Attached) with intelligent application
- Project overview with core guidelines always included
- Category-based rule organization (code style, testing, architecture)
- Technology-specific file patterns (20+ languages supported)
- Enhanced ignore files with duplicate prevention
- Context-aware rule application based on conversation and file types

### Continue

Complete YAML-based configuration system:

**Generated files:**
- `config.yaml` - Main configuration
- `.continue/rules/*.md` - Organized rule files

**Features:**
- Structured YAML configuration
- Custom slash commands
- Context providers
- Model configurations

### Amazon Q

Comment-based assistance system:

**Generated files:**
- `.amazonq/context.md` - Context information
- `.amazonq/comments.template` - Comment templates

**Features:**
- Technology-specific comment templates
- Context-aware suggestions
- Integration with AWS tools

### Kiro

Comprehensive AI-powered development assistance system:

**Generated files:**
- `.kiro/steering/*.md` - Project steering documents
- `.kiro/specs/*/requirements.md` - Functional requirements
- `.kiro/specs/*/design.md` - Technical design documents
- `.kiro/specs/*/tasks.md` - Implementation task breakdown
- `.kiro/hooks/*.md` - Automated quality and process hooks
- `.prompts/*.md` - Reusable development prompts

**Features:**
- **Steering System**: Context-aware project guidance with YAML frontmatter
- **Specifications System**: Three-phase workflow (Requirements → Design → Implementation)
- **Hooks System**: Automated quality checks and pre-commit validation
- **Prompts System**: Reusable prompts for common development tasks
- **Multi-file Support**: Merge multiple `.promptrek.yaml` files intelligently
- **Enhanced Content**: Rich context, rationale, and practical examples

**File Structure:**
```
.kiro/
├── steering/
│   ├── product.md                      # Product overview (inclusion: always)
│   ├── tech.md                         # Technology stack guidance
│   ├── structure.md                    # Project organization
│   ├── api-rest-conventions.md         # API-specific rules (fileMatch)
│   └── component-development-patterns.md # Frontend patterns (fileMatch)
├── specs/
│   └── {project-name}/
│       ├── requirements.md             # Functional/non-functional requirements
│       ├── design.md                   # Technical architecture
│       └── tasks.md                    # Implementation breakdown
└── hooks/
    ├── code-quality.md                 # Automated quality checks
    └── pre-commit.md                   # Pre-commit validation

.prompts/
├── development.md                      # Feature development prompts
└── refactoring.md                      # Code improvement prompts
```

**YAML Frontmatter Examples:**
```yaml
---
inclusion: always                       # Always include this steering
---

---
inclusion: fileMatch                    # Include only for matching files
fileMatchPattern: "**/api/**/*.{ts,js,py,go,java}"
---

---
inclusion: manual                       # Include only when explicitly referenced
---
```

## Advanced Features

### Variable Substitution

Use dynamic variables in your prompts:

```yaml
variables:
  PROJECT_NAME: "E-commerce Platform"
  TEAM_EMAIL: "dev-team@company.com"

instructions:
  general:
    - "This is the {{ PROJECT_NAME }} project"
    - "Contact {{ TEAM_EMAIL }} for questions"
```

### Conditional Instructions

Apply different instructions based on context:

```yaml
instructions:
  general:
    - "Write clean, readable code"
    - if: "context.technologies contains 'typescript'"
      then: "Use strict TypeScript types"
    - if: "context.project_type == 'api'"
      then: "Follow RESTful API conventions"
```

### Import System

Organize and reuse prompt components:

```yaml
imports:
  - "common/typescript-rules.yaml"
  - "common/testing-guidelines.yaml"

instructions:
  general:
    - "Follow project-specific patterns"
```

### Multi-File Support

Merge multiple `.promptrek.yaml` files for complex projects:

**File Structure:**
```
project/
├── base.promptrek.yaml              # Core project configuration
├── api/
│   └── api.promptrek.yaml          # API-specific additions
└── frontend/
    └── frontend.promptrek.yaml     # Frontend-specific additions
```

**Base Configuration (`base.promptrek.yaml`):**
```yaml
schema_version: "1.0.0"
metadata:
  title: "E-commerce Platform"
  version: "1.0.0"
  author: "Development Team"

instructions:
  general:
    - "Write clean, maintainable code"
    - "Follow established patterns"

context:
  technologies: ["typescript"]
  project_type: "web_application"

targets: ["kiro"]
```

**API Addition (`api/api.promptrek.yaml`):**
```yaml
schema_version: "1.0.0"
metadata:
  title: "API Module"

instructions:
  general:
    - "Follow RESTful conventions"
    - "Implement proper error handling"

context:
  technologies: ["node", "express"]

targets: ["kiro"]
```

**Generate from Multiple Files:**
```bash
# Specific files
promptrek generate --editor kiro base.promptrek.yaml api/api.promptrek.yaml

# All files in directory
promptrek generate --editor kiro --directory . --recursive
```

**Merging Behavior:**
- **Instructions**: Combined (concatenated)
- **Technologies**: Combined (deduplicated)
- **Variables**: Later files override earlier ones
- **Targets**: Combined (deduplicated)
- **Metadata**: Later files take precedence

### Editor-Specific Customizations

Customize behavior for specific editors:

```yaml
editor_specific:
  copilot:
    additional_instructions:
      - "Focus on code completion suggestions"
      - "Provide comprehensive docstrings"
  
  cursor:
    additional_instructions:
      - "Be concise in explanations"
      - "Focus on quick implementations"
    
    custom_commands:
      - name: "refactor"
        prompt: "Refactor this code for better readability"
```

## Best Practices

### Organizing Instructions

**Use clear categories:**
```yaml
instructions:
  general:
    - "Write clean, maintainable code"
  
  code_style:
    - "Use meaningful variable names"
    - "Follow consistent indentation"
  
  architecture:
    - "Separate concerns into modules"
    - "Use dependency injection"
  
  testing:
    - "Write unit tests for all functions"
    - "Aim for 80%+ code coverage"
```

### Technology-Specific Guidelines

**Organize by technology:**
```yaml
context:
  technologies: ["typescript", "react", "node.js"]

instructions:
  typescript:
    - "Use strict mode"
    - "Define interfaces for all data structures"
  
  react:
    - "Use functional components"
    - "Implement proper state management"
  
  nodejs:
    - "Use async/await for asynchronous operations"
    - "Implement proper error handling"
```

### Team Collaboration

**Share common configurations:**
```yaml
imports:
  - "team/coding-standards.yaml"
  - "team/security-guidelines.yaml"

variables:
  TEAM_SLACK: "#dev-team"
  CODE_REVIEW_CHECKLIST: "https://internal.com/checklist"
```

### Version Management

**Track changes:**
```yaml
metadata:
  version: "2.1.0"
  updated: "2024-01-15"
  changelog:
    - "v2.1.0: Added security guidelines"
    - "v2.0.0: Major refactor of instruction structure"
    - "v1.0.0: Initial version"
```

## Troubleshooting

### Common Issues

#### Installation Problems

**Problem**: `promptrek` command not found
**Solution**: Ensure Python's script directory is in your PATH:
```bash
python -m pip show promptrek
export PATH="$PATH:$(python -m site --user-base)/bin"
```

**Problem**: Import errors when running
**Solution**: Reinstall in development mode:
```bash
pip install -e .
```

#### Validation Errors

**Problem**: Schema validation fails
**Solution**: Check your YAML syntax and required fields:
```bash
promptrek validate --verbose your-file.promptrek.yaml
```

**Problem**: Unsupported editor target
**Solution**: Check supported editors:
```bash
promptrek list-editors
```

#### Generation Issues

**Problem**: Files not generated as expected
**Solution**: Use dry-run to debug:
```bash
promptrek generate --dry-run --verbose --all --input your-file.promptrek.yaml
```

**Problem**: Permission denied when creating files
**Solution**: Check directory permissions or use custom output directory:
```bash
promptrek generate --output ./my-output-dir --all --input your-file.promptrek.yaml
```

#### Template Issues

**Problem**: Variables not substituted
**Solution**: Ensure proper variable syntax and definition:
```yaml
variables:
  MY_VAR: "value"

instructions:
  general:
    - "Use {{ MY_VAR }} in instructions"  # Correct
    - "Use ${MY_VAR} in instructions"     # Incorrect
```

### Debug Mode

Enable verbose output for debugging:
```bash
promptrek --verbose generate --all --input your-file.promptrek.yaml
```

### Getting Help

1. **Documentation**: Read this guide thoroughly
2. **Examples**: Check the `examples/` directory in the repository
3. **Issues**: [Report bugs or request features]({{ site.issues_url }})
4. **Discussions**: Join community discussions in the repository

### Performance Tips

1. **Use specific targets**: Only generate for editors you actually use
2. **Optimize file patterns**: Use precise glob patterns in path-specific rules
3. **Cache configurations**: Reuse common instruction sets via imports
4. **Regular validation**: Validate configurations regularly to catch issues early

---

## Next Steps

- Explore [Advanced Template Features](https://github.com/flamingquaks/promptrek/blob/main/docs/ADVANCED_FEATURES.md)
- Learn about [Editor Adapters](https://github.com/flamingquaks/promptrek/blob/main/docs/ADAPTERS.md)
- Check the [Implementation Roadmap](https://github.com/flamingquaks/promptrek/blob/main/docs/IMPLEMENTATION_ROADMAP.md)
- [Contribute to the project](contributing.html)

Need help? [Create an issue]({{ site.issues_url }}) and we'll help you get started!