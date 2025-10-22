---
layout: guide
title: Editor Adapters
---

# Editor Adapters

PrompTrek supports 9 AI-powered code editors and assistants. Each adapter generates editor-specific configuration files optimized for that particular tool.

> **📊 Looking for a detailed feature comparison?** See the [Adapter Capabilities Matrix](adapter-capabilities.html) for a comprehensive breakdown of features supported by each adapter.

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
**Generated Files**: `.continue/rules/*.md`
**Features**: ✅ Project Files, ✅ Variables, ✅ Conditionals, ✅ Sync, ✅ Frontmatter Metadata

Continue adapter generates organized markdown rule files with YAML frontmatter for enhanced AI-powered code completion and chat.

**File Generation Behavior**:

- **With `documents` field**: Generates one `.md` file per document using the document's `name` field
- **Without `documents` field**: Generates a single `general.md` file containing the main `content`

**Metadata-Driven Configuration**:

The Continue adapter uses meaningful metadata fields to control rule behavior:

```yaml
# Main content metadata (top-level)
content_description: "General coding guidelines"  # Default if not specified
content_always_apply: true  # Default for main content

# Document metadata (per-document)
documents:
  - name: documentation-standards
    content: "# Documentation Standards..."
    description: "Standards for writing and maintaining Continue Docs"
    file_globs: "docs/**/*.{md,mdx}"  # Files where rule applies
    always_apply: false  # Only applies to matching files
```

**Example Generated Files (.continue/rules/)**:
- With `documents`: Files named according to document `name` field (e.g., `documentation-standards.md`, `typescript-guidelines.md`)
- Without `documents`: `general.md` only

**Example Rule File with Frontmatter (general.md)**:
```markdown
---
name: "General"
alwaysApply: true
description: "General coding guidelines"
---

# General Coding Rules

- Write clean, maintainable code with proper error handling
- Follow SOLID principles and design patterns
- Include comprehensive documentation
```

**Example Document with File Patterns (documentation-standards.md)**:
```markdown
---
name: "documentation-standards"
globs: "docs/**/*.{md,mdx}"
alwaysApply: false
description: "Standards for writing and maintaining Continue Docs"
---

# Documentation Standards

- Use clear, concise language
- Include code examples where appropriate
- Keep documentation up-to-date with code changes
```

**Frontmatter Fields**:
- `name`: Display name for the rule (required)
- `description`: Human-readable description (optional)
- `globs`: File patterns where rule applies (optional, e.g., `**/*.{ts,tsx}`)
- `alwaysApply`: `true` = always applies, `false` = applies only to matching files (default: false for documents, true for main content)

**Sync Support**: Continue adapter supports bidirectional sync - you can import existing Continue configurations back to PrompTrek format using `promptrek sync`.

### ✅ Cline (VSCode Extension)
**Generated Files**: `.clinerules`, `.clinerules/*.md`, `.vscode/settings.json` (MCP)
**Features**: Variable substitution, Conditional instructions, MCP server support, Bidirectional sync

Cline adapter generates markdown-based rules for the Cline VSCode extension - an autonomous AI coding agent with file creation/editing, command execution, and browser automation capabilities.

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

### ✅ Windsurf
**Generated Files**: `.windsurf/rules/*.md`
**Features**: ✅ Project Files, ✅ Variables, ✅ Conditionals

Windsurf adapter generates organized markdown rule files for AI-powered coding assistance.

**File Generation Behavior**:
- **With `documents` field**: Generates one `.md` file per document using the document's `name` field
- **Without `documents` field**: Generates a single `general.md` file containing the main `content`

**Example Generated Files (.windsurf/rules/)**:
- With `documents`: Files named according to document `name` field (e.g., `typescript-guidelines.md`, `testing-standards.md`)
- Without `documents`: `general.md` only

**Example Rule File**:
```markdown
# Code Style Rules

- Use consistent indentation (4 spaces for Python, 2 for JavaScript)
- Follow language-specific style guides (PEP 8 for Python, StandardJS for JavaScript)
- Prefer const and let over var in JavaScript

## Additional Guidelines
- Follow project-specific patterns and conventions
- Maintain consistency with existing codebase
- Consider performance and security implications
```

### ✅ JetBrains AI
**Generated Files**: `.assistant/rules/*.md`
**Features**: ✅ Project Files, ✅ Variables, ✅ Conditionals

JetBrains AI adapter generates markdown rules for AI assistance integrated into JetBrains IDEs (IntelliJ IDEA, PyCharm, WebStorm, etc.).

**File Generation Behavior**:
- **With `documents` field**: Generates one `.md` file per document using the document's `name` field
- **Without `documents` field**: Generates a single `general.md` file containing the main `content`

**Example Generated Files (.assistant/rules/)**:
- With `documents`: Files named according to document `name` field (e.g., `java-guidelines.md`, `kotlin-patterns.md`)
- Without `documents`: `general.md` only

**Note**: Prompts and MCP configurations for JetBrains AI are only configurable through the IDE UI, not via project files.

### ✅ GitHub Copilot
**Generated Files**: `.github/copilot-instructions.md`, `.github/instructions/*.instructions.md`, `.github/prompts/*.prompt.md`
**Features**: Variable substitution, Conditional instructions, Path-specific instructions, Bidirectional sync

GitHub Copilot adapter generates sophisticated instruction systems with repository-wide and path-specific configurations. Supports full bidirectional synchronization for seamless round-trip workflows.

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

**Bidirectional Sync Support**:
```bash
# Round-trip workflow
promptrek generate --editor copilot project.promptrek.yaml
# ... AI modifies Copilot files ...
promptrek sync --editor copilot --source-dir . --output project.promptrek.yaml
```

The sync system provides:
- Smart metadata preservation (user vs auto-generated content)
- Additive instruction merging without data loss
- Context and technology detection from Copilot files
```

### ✅ Cursor (Modernized 2025)
**Generated Files**: `.cursor/rules/index.mdc`, `.cursor/rules/*.mdc`, `AGENTS.md`, `.cursorignore`, `.cursorindexingignore`
**Features**: Variable substitution, Conditional instructions, Modern rule types (Always/Auto Attached), Technology-specific rules, Advanced file targeting, Ignore systems

Cursor adapter generates modern MDC rules system following Cursor IDE's 2025 best practices with intelligent rule types, project overview, and enhanced file organization.

**Metadata-Driven Configuration**:

The Cursor adapter uses meaningful metadata fields to control rule behavior:

```yaml
# Main content metadata (top-level)
content_description: "Project overview and core guidelines"  # Default if not specified
content_always_apply: true  # Default: Always Applied rule

# Document metadata (per-document)
documents:
  - name: typescript
    content: "# TypeScript Guidelines..."
    description: "TypeScript coding guidelines"  # Shown in Cursor UI
    file_globs: "**/*.{ts,tsx}"  # Files where rule applies
    always_apply: false  # Auto Attached (applies only to matching files)

  - name: testing
    content: "# Testing Standards..."
    # Omit metadata for smart defaults:
    # - description: "testing guidelines" (inferred from name)
    # - file_globs: "**/*.{test,spec}.*" (inferred from name)
    # - always_apply: false (default for documents)
```

**Main Project Overview (.cursor/rules/index.mdc)**:
```yaml
---
description: Project overview and core guidelines
alwaysApply: true
---

# My Project

A modern web application built with React and TypeScript.

## Project Context
**Type:** web_application
**Technologies:** typescript, react, vite

**Description:**
A modern web application demonstrating best practices.

## Core Guidelines
- Write clean, maintainable code
- Follow TypeScript best practices
- Use consistent naming conventions
```

**Category-Specific Rules (.cursor/rules/)**:
```yaml
---
description: Code style and formatting guidelines
globs: "**/*.{py,js,ts,tsx,jsx,go,rs,java,cpp,c,h}"
alwaysApply: false
---

# Code Style Guidelines

*Source: project.promptrek.yaml*

- Use meaningful variable names
- Add appropriate comments
- Follow project conventions
```

**Metadata Fields**:
- `description`: Human-readable description shown in Cursor UI (required)
- `file_globs`: File patterns where rule applies (e.g., `**/*.{ts,tsx}`)
- `always_apply`: `true` = Always Applied, `false` = Auto Attached (file-specific)

**Smart Defaults**:
- Main content: `description="Project overview and core guidelines"`, `always_apply=true`
- Documents: `description="{name} guidelines"`, `always_apply=false`, auto-infer globs from name

**Technology-Specific Rules**:
- `typescript-guidelines.mdc` - TypeScript patterns (Auto Attached to `**/*.{ts,tsx}`)
- `python-guidelines.mdc` - Python patterns (Auto Attached to `**/*.{py,pyi}`)
- `testing-guidelines.mdc` - Testing standards (Auto Attached to `**/*.{test,spec}.*`)

**Enhanced Ignore Files**:
- `.cursorignore` - Files to exclude from analysis (no duplicates, technology-aware)
- `.cursorindexingignore` - Files to exclude from indexing (comprehensive coverage)

**Rule Types**:
- **Always** (`alwaysApply: true`) - Project overview, general guidelines, architecture
- **Auto Attached** (`alwaysApply: false` + `globs`) - Technology and category-specific rules
- Intelligent rule application based on file patterns and conversation context

### ✅ Kiro
**Generated Files**: `.kiro/steering/*.md`
**Features**: ✅ Project Files, ✅ Variables, ✅ Conditionals

Kiro adapter generates steering documents that guide AI-powered coding assistants with context-aware instructions.

**File Generation Behavior**:
- **With `documents` field**: Generates one `.md` file per document using the document's `name` field
- **Without `documents` field**: Generates a single `project.md` file containing the main `content`

**Example Generated Files (.kiro/steering/)**:
- With `documents`: Files named according to document `name` field (e.g., `architecture.md`, `api-conventions.md`)
- Without `documents`: `project.md` only

**Example Steering Document**:
```markdown
---
inclusion: always
---

# PrompTrek AI Editor Prompts

AI assistant configuration for developing PrompTrek

## Project Context
**Type:** cli_tool
**Technologies:** python, click, pyyaml, pydantic

## Core Guidelines
- Write clean, maintainable code
- Follow established patterns and conventions
```

Each steering document includes YAML frontmatter with `inclusion: always` to ensure it's always loaded by Kiro.

### ✅ Amazon Q
**Generated Files**: `.amazonq/rules/*.md`, `.amazonq/cli-agents/*.json`
**Features**: ✅ Project Files, ✅ Variables, ✅ Conditionals, ✅ Sync

Amazon Q adapter generates markdown rules for AI assistance and JSON-based CLI agents for AWS development.

**File Generation Behavior**:
- **With `documents` field**: Generates one `.md` file per document using the document's `name` field
- **Without `documents` field**: Generates a single `general.md` file containing the main `content`

**Example Generated Files (.amazonq/rules/)**:
- With `documents`: Files named according to document `name` field (e.g., `python-guidelines.md`, `security-standards.md`)
- Without `documents`: `general.md` only

**CLI Agents (.amazonq/cli-agents/)**:
CLI agents are JSON files that define custom Amazon Q agents for code review, security analysis, and test generation. These are local development tools, not managed cloud agents.

**Example Agent (security-review-agent.json)**:
```json
{
  "name": "security-review-agent",
  "description": "Reviews code for security vulnerabilities",
  "instructions": "Always focus on OWASP Top 10 vulnerabilities. Validate all user inputs..."
}
```

**Generated Agents**:
- `code-review-agent.json` - Reviews code for style and quality
- `security-review-agent.json` - Reviews code for security vulnerabilities
- `test-generation-agent.json` - Generates unit and integration tests

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

  - if: "EDITOR in [\"windsurf\", \"cursor\"]"
    then:
      instructions:
        general:
          - "Focus on performance optimization"
          - "Suggest modern React patterns"
```

### Variable Substitution in Editor Content

All adapters support variable substitution in their generated content:

{% raw %}
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
{% endraw %}

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
- **Cline**: Autonomous VSCode agent with file operations and browser automation
- **Windsurf**: Structures content as modular markdown rules
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
.windsurf/
.clinerules/

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