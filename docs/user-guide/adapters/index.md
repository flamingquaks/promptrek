# Editor Adapters

PrompTrek supports 9 AI-powered code editors and assistants. Each adapter generates editor-specific configuration files optimized for that particular tool.

!!! info "Feature Comparison"
    Looking for a detailed feature comparison? See the [Adapter Capabilities Matrix](capabilities.md) for a comprehensive breakdown of features supported by each adapter.

## Supported Editors

### Claude Code

**Generated Files**:

- `.claude/CLAUDE.md` - Main project context and guidelines
- `.mcp.json` - MCP server configurations (project root)
- `.claude/commands/*.md` - Custom slash commands
- `.claude/agents/*.md` - Autonomous agents
- `.claude/settings.local.json` - Hooks with tool matchers (Claude Code native format)
- `.claude/hooks.yaml` - Hooks without matchers (PrompTrek format)

**Features**: ✅ Project Files, ✅ Variables, ✅ Conditionals, ✅ Sync Support, ✅ MCP Servers, ✅ Custom Commands, ✅ Autonomous Agents, ✅ Event Hooks

Claude Code adapter generates comprehensive markdown context files with full plugin ecosystem support including MCP servers, custom commands, autonomous agents, and event-driven hooks.

**Main Context File (.claude/CLAUDE.md)**:
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

**MCP Server Configuration (.mcp.json in project root)**:
```json
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "/path/to/allowed/files"],
      "type": "stdio"
    }
  }
}
```

**Custom Commands (.claude/commands/review.md)**:
```markdown
# review

**Description:** Review code for quality and best practices

## Prompt
Review the current file or selection for:
- Code quality and maintainability
- Adherence to project standards
- Potential bugs or issues
- Performance optimizations
```

!!! note "Command File Format"
    Command files use markdown headings (not YAML frontmatter) for compatibility with Claude Code's native format.

**Autonomous Agents (.claude/agents/test-guardian.md)**:
```markdown
# test-guardian

**Description:** Ensures comprehensive test coverage for all code changes

## System Prompt
You are a test coverage specialist. Your mission is to:
1. Identify untested code paths
2. Generate comprehensive test cases
3. Ensure 80%+ code coverage
4. Validate edge cases and error handling

## Configuration
- Trust Level: untrusted
- Requires Approval: True
```

!!! note "Agent File Format"
    Agent files use markdown headings (not YAML frontmatter) for compatibility with Claude Code's native format.

**Event Hooks - Claude Code Native Format (.claude/settings.local.json)**:

For hooks that need to match specific tools (using `matcher` conditions), Claude generates the native `settings.local.json` format:

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "echo 'Running bash command...'"
          }
        ]
      }
    ]
  }
}
```

**Event Hooks - PrompTrek Format (.claude/hooks.yaml)**:

For hooks without tool matchers, Claude generates the PrompTrek YAML format:

```yaml
hooks:
  - name: pre-commit-validator
    event: PreCommit
    command: npm run lint
    requires_reapproval: true
    description: Validate code before commits
```

**Sync Support**:
```bash
# Generate from PrompTrek to Claude files
promptrek generate --editor claude project.promptrek.yaml

# Sync from Claude files back to PrompTrek
promptrek sync --editor claude --source-dir . --output project.promptrek.yaml
```

The sync system preserves all plugin configurations including MCP servers, commands, agents, and hooks in both native Claude Code and PrompTrek formats.

---

### Continue

**Generated Files**:

- `.continue/config.yaml` - Main configuration with metadata and prompt references
- `.continue/mcpServers/*.yaml` - Individual MCP server configurations
- `.continue/prompts/*.md` - Individual slash command prompts
- `.continue/rules/*.md` - Rule files with frontmatter

**Features**: ✅ Project Files, ✅ Variables, ✅ Conditionals, ✅ Sync, ✅ MCP Servers, ✅ Slash Commands, ✅ Frontmatter Metadata

Continue adapter generates a modular configuration system with separate files for MCP servers, slash commands, and rules, following Continue's recommended best practices.

**File Generation Behavior**:

**Rules Directory** (`.continue/rules/*.md`):

- **With `documents` field**: Generates one `.md` file per document using the document's `name` field
- **Without `documents` field**: Generates a single `general.md` file containing the main `content`

!!! warning "Important for Sync"
    The `general.md` file has special meaning - it maps to the main `content` field during sync. Do not rename this file if you want round-trip sync to work correctly. All other `.md` files in `.continue/rules/` become `documents`.

**MCP Servers Directory** (`.continue/mcpServers/*.yaml`):

- Generates one YAML file per MCP server configuration
- Continue-specific format with metadata fields: `name`, `version`, `schema`
- Example: `filesystem.yaml`, `github.yaml`

**Prompts Directory** (`.continue/prompts/*.md`):

- Generates one markdown file per slash command
- Includes YAML frontmatter with `name`, `description`, `invokable: true`
- Referenced in `config.yaml` for automatic loading

**Configuration File** (`.continue/config.yaml`):

- Contains project metadata and prompt file references
- Automatically links to individual prompt files using `uses: file://...` syntax

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

**Example Generated Files**:

**Rule File with Frontmatter** (`.continue/rules/general.md`):
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

**MCP Server YAML** (`.continue/mcpServers/filesystem.yaml`):
```yaml
name: Filesystem MCP Server
version: 0.0.1
schema: v1
mcpServers:
  - name: filesystem
    command: npx
    args:
      - "-y"
      - "@modelcontextprotocol/server-filesystem"
      - "/path/to/workspace"
```

**Slash Command Prompt** (`.continue/prompts/refactor.md`):
```markdown
---
name: refactor
description: Refactor code for better quality
invokable: true
---

Refactor the selected code following these principles:
1. Simplification - Break down complex functions
2. Naming - Use descriptive variable names
3. DRY Principle - Eliminate code duplication
```

**Config YAML** (`.continue/config.yaml`):
```yaml
name: PrompTrek Generated Configuration
version: 1.0.0
schema: v1
prompts:
  - uses: file://.continue/prompts/refactor.md
  - uses: file://.continue/prompts/explain.md
```

**Frontmatter Fields**:

- **Rules**: `name`, `description`, `globs`, `alwaysApply`
- **Prompts**: `name`, `description`, `invokable`
- **MCP Servers**: Top-level metadata includes `name`, `version`, `schema`

**Sync Support**: Continue adapter supports round-trip sync - you can import existing Continue configurations back to PrompTrek format using `promptrek sync`.

---

### Cline (VSCode Extension)

**Generated Files**: `.clinerules`, `.clinerules/*.md`, `.vscode/settings.json` (MCP)

**Features**: Variable substitution, Conditional instructions, MCP server support, Round-trip sync

Cline adapter generates markdown-based rules for the Cline VSCode extension - an autonomous AI coding agent with file creation/editing, command execution, and browser automation capabilities.

**File Generation Behavior**:

- **With `documents` field**: Generates one `.md` file per document using the document's `name` field
- **Without `documents` field**: Generates a single `default-rules.md` file containing the main `content`

!!! warning "Important for Sync"
    The `default-rules.md` file has special meaning - it maps to the main `content` field during sync. Do not rename this file if you want round-trip sync to work correctly. All other `.md` files in `.clinerules/` become `documents`.

**Example Output (.clinerules/default-rules.md)**:
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

---

### Windsurf

**Generated Files**: `.windsurf/rules/*.md`

**Features**: ✅ Project Files, ✅ Variables, ✅ Conditionals, ✅ Sync Support

Windsurf adapter generates organized markdown rule files for AI-powered coding assistance.

**File Generation Behavior**:

- **With `documents` field**: Generates one `.md` file per document using the document's `name` field
- **Without `documents` field**: Generates a single `general.md` file containing the main `content`

!!! warning "Important for Sync"
    The `general.md` file has special meaning - it maps to the main `content` field during sync. Do not rename this file if you want round-trip sync to work correctly. All other `.md` files in `.windsurf/rules/` become `documents`.

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

**Sync Support**:
```bash
# Generate from PrompTrek to Windsurf files
promptrek generate --editor windsurf project.promptrek.yaml

# Sync from Windsurf files back to PrompTrek
promptrek sync --editor windsurf --source-dir . --output project.promptrek.yaml
```

The sync system preserves the main content in `general.md` and treats all other rule files as documents in the `documents` array.

---

### GitHub Copilot

**Generated Files**: `.github/copilot-instructions.md`, `.github/instructions/*.instructions.md`, `.github/prompts/*.prompt.md`

**Features**: Variable substitution, Conditional instructions, Path-specific instructions, Round-trip sync

GitHub Copilot adapter generates sophisticated instruction systems with repository-wide and path-specific configurations. Supports full round-trip synchronization for seamless workflows.

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

**Sync Support**:
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

---

### Cursor (Modernized 2025)

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

---

### Kiro

**Generated Files**: `.kiro/steering/*.md`

**Features**: ✅ Project Files, ✅ Variables, ✅ Conditionals

Kiro adapter generates steering documents that guide AI-powered coding assistants with context-aware instructions.

**File Generation Behavior**:

- **With `documents` field**: Generates one `.md` file per document using the document's `name` field
- **Without `documents` field**: Generates a single `project.md` file containing the main `content`

!!! warning "Important for Sync"
    The `project.md` file has special meaning - it maps to the main `content` field during sync. Do not rename this file if you want round-trip sync to work correctly. All other `.md` files in `.kiro/steering/` become `documents`.

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

---

### Amazon Q

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

---

### JetBrains AI

**Generated Files**: `.assistant/rules/*.md`

**Features**: ✅ Project Files, ✅ Variables, ✅ Conditionals

JetBrains AI adapter generates markdown rules for AI assistance integrated into JetBrains IDEs (IntelliJ IDEA, PyCharm, WebStorm, etc.).

**File Generation Behavior**:

- **With `documents` field**: Generates one `.md` file per document using the document's `name` field
- **Without `documents` field**: Generates a single `general.md` file containing the main `content`

**Example Generated Files (.assistant/rules/)**:

- With `documents`: Files named according to document `name` field (e.g., `java-guidelines.md`, `kotlin-patterns.md`)
- Without `documents`: `general.md` only

!!! note "IDE UI Configuration"
    Prompts and MCP configurations for JetBrains AI are only configurable through the IDE UI, not via project files.

---

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
promptrek generate --editor claude --output ./output project.promptrek.yaml \
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

```yaml
metadata:
  title: "{{{ PROJECT_NAME }}} Assistant"
  description: "AI assistant for {{{ PROJECT_NAME }}}"

content: |
  # {{{ PROJECT_NAME }}} Development Guide

  Follow {{{ PROJECT_NAME }}} coding standards.
  Contact {{{ AUTHOR_EMAIL }}} for questions.

variables:
  PROJECT_NAME: "MyProject"
  AUTHOR_EMAIL: "team@example.com"
```

## File Organization

Generated files are organized by editor:

```
project/
├── .claude/
│   ├── CLAUDE.md                      # Main context file
│   ├── settings.local.json            # Hooks with matchers (native format)
│   ├── hooks.yaml                     # Hooks without matchers
│   ├── agents/
│   │   ├── test-guardian.md
│   │   └── code-reviewer.md
│   └── commands/
│       ├── review.md
│       └── analyze.md
├── .mcp.json                          # MCP servers (project root)
├── .continue/
│   ├── config.yaml                    # Main configuration
│   ├── mcpServers/
│   │   ├── filesystem.yaml
│   │   └── github.yaml
│   ├── prompts/
│   │   ├── refactor.md
│   │   └── explain.md
│   └── rules/
│       ├── general.md
│       ├── code-style.md
│       ├── testing.md
│       └── typescript-rules.md
├── .cursor/
│   └── rules/
│       ├── index.mdc
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
│   └── steering/
│       ├── product.md
│       ├── tech.md
│       ├── structure.md
│       ├── api-rest-conventions.md
│       └── component-development-patterns.md
├── .windsurf/
│   └── rules/
│       ├── general.md
│       └── typescript-guidelines.md
├── .clinerules                        # Cline rules (single file or directory)
└── project.promptrek.yaml             # Source configuration
```

## Version Control

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

## Best Practices

### Universal Instructions

- Write instructions that work well across all editors
- Use editor-specific conditionals sparingly
- Focus on code quality and project-specific guidance

### Editor Selection

- Choose editors based on your development workflow
- Consider team preferences and tool availability
- Test generated configurations with actual editor installations

## Related Documentation

- [Adapter Capabilities](capabilities.md) - Detailed feature comparison
- [UPF Specification](../upf-specification.md) - Schema documentation
- [Sync Workflow](../workflows/sync.md) - Round-trip sync guide
- [Plugins](../plugins/index.md) - MCP servers, commands, agents, and hooks
