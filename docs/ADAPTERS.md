# Editor Adapters

PrompTrek supports multiple AI-powered code editors and assistants. Each adapter generates editor-specific configuration files optimized for that particular tool.

## Supported Editors

### ✅ Claude Code
**Generated Files**: `.claude/context.md`  
**Features**: Variable substitution, Conditional instructions

Claude Code adapter generates comprehensive context files in Markdown format that provide detailed project information and coding guidelines optimized for Claude's understanding.

**Example Output**:
```markdown
# My Project

## Project Overview
A modern web application built with React and TypeScript.

## Project Details
**Project Type:** web_application
**Technologies:** typescript, react, vite

## Development Guidelines
### General Principles
- Write clean, maintainable code
- Follow TypeScript best practices

### Code Style Requirements
- Use consistent indentation
- Prefer const over let

## Code Examples
### Component Example
const Button = ({ label }: { label: string }) => <button>{label}</button>;

## AI Assistant Instructions
When working on this project:
- Follow the established patterns and conventions shown above
- Maintain consistency with the existing codebase
- Consider the project context and requirements in all suggestions
```

### ✅ Continue
**Generated Files**: `config.yaml`, `.continue/rules/*.md`  
**Features**: Variable substitution, Conditional instructions, Technology-specific rules

Continue adapter generates modern YAML configuration with organized rule files for enhanced AI-powered code completion and chat.

**Main Configuration (config.yaml)**:
```yaml
name: My Project
version: 0.0.1
schema: v1
models: []
systemMessage: "My Project\n\nA modern web application"
completionOptions: {}
allowAnonymousTelemetry: false
rules:
  - "Write clean, maintainable code"
  - "Follow TypeScript best practices"
context:
  - provider: file
  - provider: code
  - provider: docs
    query: "documentation for typescript, react"
```

**Rule Files (.continue/rules/)**:
- `general.md` - General coding guidelines
- `code-style.md` - Code style rules
- `testing.md` - Testing guidelines  
- `{technology}-rules.md` - Technology-specific rules (typescript-rules.md, react-rules.md)

### ✅ Cline (Terminal-based AI)
**Generated Files**: `.clinerules`  
**Features**: Variable substitution, Conditional instructions

Cline adapter generates markdown-based rules file for terminal-based AI assistance with project context and coding guidelines.

**Example Output (.clinerules)**:
```markdown
# My Project

## Project Overview
A modern web application built with React and TypeScript.

## Project Context
- **Project Type:** web_application
- **Technologies:** typescript, react, vite

## Coding Guidelines
- Write clean, readable code
- Follow existing patterns
- Use TypeScript for all new files

## Code Style
- Use meaningful variable names
- Add appropriate comments
```

### ✅ Codeium
**Generated Files**: `.codeium/context.json`, `.codeiumrc`  
**Features**: Variable substitution, Conditional instructions

Codeium adapter generates structured JSON context files and RC configuration files that integrate with Codeium's AI code assistance.

**Context JSON Example**:
```json
{
  "project": {
    "name": "My Project",
    "technologies": ["typescript", "react"],
    "type": "web_application"
  },
  "guidelines": [
    {"category": "general", "rule": "Write clean code"},
    {"category": "style", "rule": "Use consistent indentation"}
  ],
  "patterns": [
    {
      "name": "component",
      "description": "Example component",
      "example": "const Button = ..."
    }
  ],
  "preferences": {
    "style": "consistent",
    "verbosity": "medium",
    "languages": ["typescript", "react"]
  }
}
```

### ✅ GitHub Copilot
**Generated Files**: `.github/copilot-instructions.md`, `.github/instructions/*.instructions.md`, `AGENTS.md`, `CLAUDE.md`, `GEMINI.md`  
**Features**: Variable substitution, Conditional instructions, Path-specific instructions, Agent-specific configurations

GitHub Copilot adapter generates sophisticated instruction systems with repository-wide and path-specific configurations.

**Repository Instructions (.github/copilot-instructions.md)**:
```markdown
# My Project

A modern web application built with React and TypeScript.

## Project Information
- Type: web_application
- Technologies: typescript, react, vite

## General Instructions
- Write clean, readable code
- Follow existing patterns
```

**Path-Specific Instructions (.github/instructions/typescript.instructions.md)**:
```yaml
---
applyTo: "**/*.{ts,tsx}"
---

# TypeScript Guidelines

- Use strict TypeScript configuration
- Prefer interfaces over types for object shapes
- Use proper typing for all function parameters
```

### ✅ Cursor
**Generated Files**: `.cursor/rules/*.mdc`, `AGENTS.md`, `.cursorignore`, `.cursorindexingignore`  
**Features**: Variable substitution, Conditional instructions, Technology-specific rules, Advanced file targeting, Ignore systems

Cursor adapter generates modern rules system with YAML frontmatter, technology-specific guidelines, and indexing control.

**Rule Files (.cursor/rules/)**:
```yaml
---
description: Apply coding standards to all source files
globs: "**/*.{ts,tsx,js,jsx,py,java,go,rs,cpp,c,h}"
alwaysApply: false
---

# Coding Standards

- Use meaningful variable names
- Add appropriate comments
- Follow project conventions
```

**Ignore Files**:
- `.cursorignore` - Files to exclude from analysis
- `.cursorindexingignore` - Files to exclude from indexing

### ✅ Kiro
**Generated Files**: `.kiro/steering/*.md`, `.kiro/specs/*/requirements.md`, `.kiro/specs/*/design.md`, `.kiro/specs/*/tasks.md`, `.kiro/hooks/*.md`, `.prompts/*.md`
**Features**: Variable substitution, Conditional instructions, Hooks system, Multi-file merging, Enhanced content structure

Kiro adapter generates comprehensive AI-powered development assistance with steering files, specifications, hooks, and reusable prompts.

**Steering System (.kiro/steering/)**:
```yaml
---
inclusion: always
---

# Product Overview

This steering file provides comprehensive guidelines for the project...

## Why These Conventions Matter
- **Consistency**: Predictable patterns improve developer experience
- **Security**: Proper implementation prevents common vulnerabilities
- **Maintainability**: Clear patterns reduce cognitive load
```

**Specifications System (.kiro/specs/)**:
- `requirements.md` - Functional and non-functional requirements with acceptance criteria
- `design.md` - Technical architecture and implementation guidelines
- `tasks.md` - Implementation task breakdown with progress tracking

**Hooks System (.kiro/hooks/)**:
- `code-quality.md` - Automated quality checks triggered on file save and commits
- `pre-commit.md` - Pre-commit validation with test requirements and quality gates

**Prompts System (.prompts/)**:
- `development.md` - Reusable prompts for feature development and bug fixes
- `refactoring.md` - Structured prompts for code improvement and optimization

**Multi-File Support**:
Kiro adapter supports merging multiple `.promptrek.yaml` files, combining:
- Instructions (concatenated)
- Technologies (deduplicated)
- Variables (later files take precedence)
- Targets (combined)

## Using Adapters

### Generate for Single Editor
```bash
promptrek generate --editor claude --output ./output project.promptrek.yaml
```

### Generate for All Target Editors
```bash
promptrek generate --all --output ./output project.promptrek.yaml
```

### Generate from Multiple Files
```bash
promptrek generate --editor kiro --output ./output base.promptrek.yaml additional.promptrek.yaml
```

### Generate from Directory (All .promptrek.yaml files)
```bash
promptrek generate --editor kiro --directory ./configs --output ./output
```

### Dry Run (Preview Mode)
```bash
promptrek generate --editor claude --output ./output --dry-run project.promptrek.yaml
```

### With Variable Overrides
```bash
promptrek generate --editor claude --output ./output project.amp.yaml \
  -V PROJECT_NAME="CustomProject" \
  -V AUTHOR="Custom Author"
```

## Editor-Specific Features

### Conditional Instructions

Different editors have different strengths. Use conditionals to provide editor-specific guidance:

```yaml
conditions:
  - if: "EDITOR == \"claude\""
    then:
      instructions:
        general:
          - "Provide detailed explanations for complex logic"
          - "Focus on code clarity and readability"

  - if: "EDITOR == \"continue\""
    then:
      instructions:
        general:
          - "Generate comprehensive code completions"
          - "Suggest appropriate TypeScript types"

  - if: "EDITOR in [\"codeium\", \"cursor\"]"
    then:
      instructions:
        general:
          - "Focus on performance optimization"
          - "Suggest modern React patterns"
```

### Variable Substitution in Editor Content

All adapters support variable substitution in their generated content:

```yaml
metadata:
  title: "{{{ PROJECT_NAME }}} Assistant"
  description: "AI assistant for {{{ PROJECT_NAME }}}"

instructions:
  general:
    - "Follow {{{ PROJECT_NAME }}} coding standards"
    - "Contact {{{ AUTHOR_EMAIL }}} for questions"

variables:
  PROJECT_NAME: "MyProject"
  AUTHOR_EMAIL: "team@example.com"
```

## Adapter Architecture

### Built-in Capabilities

All adapters inherit these capabilities from the base adapter:

- **Variable Substitution**: Replace template variables with actual values
- **Conditional Processing**: Apply different instructions based on conditions
- **Content Validation**: Validate prompt structure for editor compatibility
- **File Generation**: Create editor-specific files with appropriate structure

### Editor-Specific Optimizations

Each adapter optimizes content for its target editor:

- **Claude**: Emphasizes detailed context and examples for better understanding
- **Continue**: Focuses on system messages and completion hints
- **Cline**: Includes safety settings and terminal-specific guidance
- **Codeium**: Structures content for AI code assistance patterns
- **Copilot**: Uses GitHub's instruction format and conventions
- **Cursor**: Follows Cursor's rules file format

## Adding New Adapters

To add support for new AI editors:

1. Create a new adapter class inheriting from `EditorAdapter`
2. Implement required methods: `generate()`, `validate()`
3. Define editor-specific file patterns and content builders  
4. Register the adapter in the adapter registry
5. Add tests for the new adapter

Example adapter structure:

```python
class NewEditorAdapter(EditorAdapter):
    def __init__(self):
        super().__init__(
            name="neweditor",
            description="New Editor (config-based)",
            file_patterns=[".neweditor/config.json"]
        )
    
    def generate(self, prompt, output_dir, dry_run=False, verbose=False, variables=None):
        # Apply variable substitution and conditionals
        processed_prompt = self.substitute_variables(prompt, variables)
        conditional_content = self.process_conditionals(processed_prompt, variables)
        
        # Generate editor-specific content
        content = self._build_content(processed_prompt, conditional_content)
        
        # Create output file
        # ... implementation
    
    def validate(self, prompt):
        # Editor-specific validation
        # ... implementation
    
    def supports_variables(self):
        return True
    
    def supports_conditionals(self):
        return True
```

## Best Practices

### Universal Instructions
- Write instructions that work well across all editors
- Use editor-specific conditionals sparingly
- Focus on code quality and project-specific guidance

### Editor Selection
- Choose editors based on your development workflow
- Consider team preferences and tool availability
- Test generated configurations with actual editor installations

### File Organization
Generated files are organized by editor:

```
project/
├── .claude/
│   └── context.md
├── .continue/
│   ├── rules/
│   │   ├── general.md
│   │   ├── code-style.md
│   │   ├── testing.md
│   │   └── typescript-rules.md
├── config.yaml
├── .cursor/
│   └── rules/
│       ├── coding-standards.mdc
│       ├── testing-guidelines.mdc
│       └── typescript-guidelines.mdc
├── .cursorignore
├── .cursorindexingignore
├── .github/
│   ├── copilot-instructions.md
│   └── instructions/
│       ├── typescript.instructions.md
│       └── testing.instructions.md
├── .kiro/
│   ├── steering/
│   │   ├── product.md
│   │   ├── tech.md
│   │   ├── structure.md
│   │   ├── api-rest-conventions.md
│   │   └── component-development-patterns.md
│   ├── specs/
│   │   ├── {project-name}/
│   │   │   ├── requirements.md
│   │   │   ├── design.md
│   │   │   └── tasks.md
│   └── hooks/
│       ├── code-quality.md
│       └── pre-commit.md
├── .prompts/
│   ├── development.md
│   └── refactoring.md
├── AGENTS.md
├── CLAUDE.md
└── .clinerules
```

### Version Control
Add generated files to `.gitignore` if they contain sensitive information or are environment-specific:

```gitignore
# Generated AI configuration files
.claude/
.continue/
.codeium/
.codeiumrc
cline-context.md

# Keep these if they're project-wide
# .github/copilot-instructions.md
# .cursorrules
```

## Troubleshooting

### Common Issues

**Missing Editor Support**: Check that the editor is in your `targets` list:
```bash
Error: Editor 'claude' not in targets: copilot, cursor
```

**File Generation Errors**: Ensure output directory exists and is writable:
```bash
promptrek generate --editor claude --output ./output project.promptrek.yaml
```

**Conditional Not Working**: Check condition syntax and variable names:
```yaml
# Correct
- if: "EDITOR == \"claude\""

# Incorrect  
- if: "EDITOR = \"claude\""  # Single = instead of ==
```

### Getting Help

- Use `promptrek list-editors` to see all supported editors
- Use `--dry-run` to preview generated content
- Use `--verbose` for detailed operation logs
- Check the generated files match your editor's expected format
