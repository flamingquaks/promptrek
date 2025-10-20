---
layout: guide
title: UPF Specification
---

# Universal Prompt Format (UPF) Specification

## Overview

The Universal Prompt Format (UPF) is a standardized YAML-based format for defining AI assistant prompts that can be converted to various editor-specific formats.

PrompTrek supports **three schema versions**:
- **v3.0.0** (Stable): Top-level plugin fields (mcp_servers, commands, agents, hooks), cleaner architecture (backward compatible with v2.x)
- **v2.1.0** (Legacy): Markdown-first with nested plugin support (superseded by v3.0)
- **v2.0.0** (Legacy): Markdown-first, simpler format with lossless bidirectional sync

## File Extension

`.promptrek.yaml`

## JSON Schema Validation

JSON Schemas are available for all versions to enable autocompletion and validation in your editor:

- **v3.0**: [`https://promptrek.ai/schema/v3.0.json`](https://promptrek.ai/schema/v3.0.json)
- **v2.1**: [`https://promptrek.ai/schema/v2.1.json`](https://promptrek.ai/schema/v2.1.json)
- **v2.0**: [`https://promptrek.ai/schema/v2.0.json`](https://promptrek.ai/schema/v2.0.json)

**Enable in your editor**: Add a schema reference at the top of your `.promptrek.yaml` file:

```yaml
# yaml-language-server: $schema=https://promptrek.ai/schema/v3.0.json
schema_version: 3.0.0
# ... rest of your configuration
```

See the [Schema Documentation](https://promptrek.ai/schema/) for more details.

## Schema Versions

- **Stable**: `3.0.0` - [Jump to v3.0 Specification](#schema-v30-stable)
- **Legacy**: `2.1.0` - [Jump to v2.1 Specification](#schema-v21-legacy)
- **Legacy**: `2.0.0` - [Jump to v2.0 Specification](#schema-v20-legacy)

---

## Schema v3.0 (Stable)

**v3.0.0**: Cleaner architecture by promoting plugin fields (mcp_servers, commands, agents, hooks) to the top level.

### What's New in v3.0

- ✨ **Top-Level Plugin Fields** - No `plugins` wrapper (removed entirely), cleaner YAML structure
- ✅ **100% Backward Compatible** - v2.x files continue to work with automatic migration
- 🔄 **Automatic Migration** - Built-in tools to convert v2.x → v3.0
- 📋 **Production Ready** - Stable schema for all new projects
- 🎯 **Recommended** - Use v3.0 for all new projects

### Key Changes from v2.1

**Before (v2.1) - Nested structure:**
```yaml
schema_version: "2.1.0"
plugins:                    # ❌ Wrapper (removed in v3.0)
  mcp_servers: [...]
  commands: [...]
  agents: [...]
  hooks: [...]
```

**After (v3.0) - Flat structure:**
```yaml
schema_version: "3.0.0"
# No plugins wrapper - fields are top-level
mcp_servers: [...]          # ✅ Top-level
commands: [...]             # ✅ Top-level
agents: [...]               # ✅ Top-level
hooks: [...]                # ✅ Top-level
```

### Complete v3.0 Schema

```yaml
# Schema version (required)
schema_version: "3.0.0"

# Metadata about the prompt file (required)
metadata:
  title: string                    # Human-readable title (required)
  description: string              # Brief description of purpose (required)
  version: string                  # Semantic version of this prompt (optional)
  author: string                   # Author name or email (optional)
  created: string                  # ISO 8601 date (YYYY-MM-DD) (optional)
  updated: string                  # ISO 8601 date (YYYY-MM-DD) (optional)
  tags: [string]                   # Tags for categorization (optional)

# Main markdown content (required)
content: string                    # Raw markdown content

# Optional: Main content metadata
content_description: string        # Description for main content (used in editor frontmatter)
content_always_apply: boolean      # Whether main content always applies (default: True)

# Optional: Multi-file support for editors like Continue, Windsurf, Kiro, Cursor
documents:
  - name: string                   # Document name (becomes filename)
    content: string                # Raw markdown content for this document
    description: string            # Human-readable description (optional)
    file_globs: string             # File patterns where this applies (optional)
    always_apply: boolean          # Whether to always apply this rule (optional)

# Template variables (optional)
variables:
  variable_name: string            # Variable value

# MCP (Model Context Protocol) servers - NOW TOP-LEVEL in v3.0
mcp_servers:
  - name: string                   # Server name/identifier (required)
    command: string                # Command to start the server (required)
    args: [string]                 # Command line arguments (optional)
    env:                           # Environment variables (optional)
      VAR_NAME: string
    description: string            # Human-readable description (optional)
    trust_metadata:                # Trust and security metadata (optional)
      trusted: boolean             # Whether this plugin is trusted
      trust_level: string          # 'full', 'partial', or 'untrusted'
      requires_approval: boolean   # Whether actions require approval
      source: string               # Source of the plugin
      verified_by: string          # Who verified this plugin
      verified_date: string        # When verified (ISO 8601)

# Custom slash commands - NOW TOP-LEVEL in v3.0
commands:
  - name: string                   # Command name (required, e.g., 'review-code')
    description: string            # Command description (required)
    prompt: string                 # Prompt template (required)
    output_format: string          # Expected output format (optional)
    requires_approval: boolean     # Whether execution requires approval (optional)
    system_message: string         # Optional system message (optional)
    examples: [string]             # Usage examples (optional)
    trust_metadata: {}             # Trust metadata (optional)

# Autonomous agents - NOW TOP-LEVEL in v3.0
agents:
  - name: string                   # Agent name (required)
    description: string            # Agent description (required)
    system_prompt: string          # System prompt for the agent (required)
    tools: [string]                # Available tools (optional)
    trust_level: string            # Trust level: 'full', 'partial', 'untrusted'
    requires_approval: boolean     # Whether actions require approval
    context: {}                    # Additional context (optional)
    trust_metadata: {}             # Trust metadata (optional)

# Event-driven hooks - NOW TOP-LEVEL in v3.0
hooks:
  - name: string                   # Hook name (required)
    event: string                  # Trigger event (required, e.g., 'pre-commit')
    command: string                # Command to execute (required)
    conditions: {}                 # Execution conditions (optional)
    requires_reapproval: boolean   # Whether hook requires reapproval (optional)
    description: string            # Hook description (optional)
    trust_metadata: {}             # Trust metadata (optional)
```

### Complete v3.0 Example

```yaml
schema_version: "3.0.0"

metadata:
  title: "Full Stack TypeScript Project"
  description: "AI assistant with MCP servers, commands, and agents"
  version: "1.0.0"
  author: "dev-team@company.com"
  tags: ["typescript", "fullstack", "ai-enhanced"]

content: |
  # Full Stack TypeScript Project

  ## Project Overview
  Modern full-stack application with TypeScript, React, and Node.js.
  Enhanced with MCP servers for GitHub integration and filesystem access.

  **Tech Stack:**
  - React 18 with TypeScript
  - Node.js with Express
  - PostgreSQL database
  - Jest for testing

  ## Development Guidelines

  ### General Principles
  - Write type-safe code with strict TypeScript
  - Use functional programming patterns
  - Add comprehensive tests for all features
  - Document complex business logic

  ### Code Style
  - Use named exports
  - Prefer arrow functions
  - Follow ESLint and Prettier configs
  - Use meaningful variable names

variables:
  PROJECT_NAME: "FullStack App"
  GITHUB_TOKEN: "ghp_token_here"
  GITHUB_OWNER: "myorg"

# Top-level plugin fields (v3.0 flat structure)
mcp_servers:
  - name: github
    command: npx
    args: ["-y", "@modelcontextprotocol/server-github"]
    env:
      GITHUB_TOKEN: "{{{ GITHUB_TOKEN }}}"
      GITHUB_OWNER: "{{{ GITHUB_OWNER }}}"
    description: "GitHub API integration"
    trust_metadata:
      trusted: true
      trust_level: full
      source: official

commands:
  - name: review-code
    description: "Review code for quality and best practices"
    prompt: |
      Review the selected code for:
      - TypeScript best practices
      - Code quality and maintainability
      - Security vulnerabilities
      - Performance optimizations
    output_format: markdown
    requires_approval: false

agents:
  - name: test-generator
    description: "Generate comprehensive unit tests"
    system_prompt: |
      Generate Jest tests with TypeScript that cover:
      - Normal operations
      - Edge cases
      - Error handling
      Target 80% coverage.
    tools: [file_read, file_write, run_tests]
    trust_level: partial
    requires_approval: true
    context:
      framework: jest
      coverage_target: 80

hooks:
  - name: pre-commit
    event: pre-commit
    command: "npm run lint && npm test"
    description: "Run linting and tests before commit"
    requires_reapproval: true
```

### Migration from v2.1 to v3.0

Use the `promptrek migrate` command to convert v2.1 files to v3.0:

```bash
# Migrate to v3.0 format
promptrek migrate project.promptrek.yaml -o project-v3.promptrek.yaml

# Migrate in place
promptrek migrate project.promptrek.yaml --in-place
```

The migration tool:
- ✅ Promotes nested `plugins.mcp_servers` → `mcp_servers` (top-level)
- ✅ Promotes nested `plugins.commands` → `commands` (top-level)
- ✅ Promotes nested `plugins.agents` → `agents` (top-level)
- ✅ Promotes nested `plugins.hooks` → `hooks` (top-level)
- ✅ Preserves all metadata, content, variables, and documents
- ✅ Updates schema_version from "2.1.0" to "3.0.0"

### Backward Compatibility

**v2.1 files continue to work in v3.0!**

When you use a v2.1 file (with nested `plugins.*` structure) in PrompTrek v3.0:
1. ⚠️ A deprecation warning is displayed
2. ✅ The parser automatically promotes nested fields to top-level internally
3. ✅ Your file works without modification

**Deprecation Warning Example:**
```
⚠️  DEPRECATION WARNING in project.promptrek.yaml:
   Detected nested plugin structure (plugins.mcp_servers, etc.)
   This structure is deprecated in v3.0 and will be removed in v4.0.
   Please migrate to top-level fields:
     - Move 'plugins.mcp_servers' → 'mcp_servers' (top-level)
     - Move 'plugins.commands' → 'commands' (top-level)
     - Move 'plugins.agents' → 'agents' (top-level)
     - Move 'plugins.hooks' → 'hooks' (top-level)
   Run: promptrek migrate project.promptrek.yaml to auto-migrate
```

**Migration Timeline:**
- **v2.1.0** (Released): Introduced nested `plugins.*` structure
- **v3.0.0** (Current): Nested structure deprecated, top-level recommended
- **v4.0.0** (Future): Nested structure will be removed entirely

### Benefits of v3.0

1. **Cleaner YAML Structure**
   ```yaml
   # v2.1 - Extra nesting
   plugins:
     mcp_servers: [...]

   # v3.0 - Flat and clean
   mcp_servers: [...]
   ```

2. **Consistency with v2.0 Philosophy**
   - v2.0 introduced a flatter, markdown-first approach
   - v3.0 extends this philosophy to plugins

3. **Easier to Read and Write**
   - Less indentation
   - More intuitive structure
   - Follows YAML best practices

4. **Future-Proof**
   - Easier to add new plugin types without more nesting
   - Better tooling support (IDE auto-completion, validation)

### Documentation

For detailed migration information:
- 📖 [V3 Migration Guide](../../docs/V3_MIGRATION_GUIDE.md) - Complete migration instructions
- ⚠️ [Deprecation Warnings](../../docs/DEPRECATION_WARNINGS.md) - Understanding deprecation system
- 🎯 Migration timeline and backward compatibility details

---

## Schema v2.1 (Legacy)

**v2.1.0** (Superseded by v3.0): Plugin support for MCP servers, custom commands, autonomous agents, and event-driven hooks with nested structure.

### Migration to v3.0

**All v2.1 features are available in v3.0 with cleaner top-level structure.**

Migrate to v3.0 for:
- ✅ Cleaner YAML structure (no `plugins` wrapper)
- ✅ Easier to read and maintain
- ✅ Better IDE support and auto-completion
- ✅ Production-ready stable schema

```bash
# Migrate v2.1 to v3.0
promptrek migrate project.promptrek.yaml -o project-v3.promptrek.yaml
```

### Complete v2.1 Schema

```yaml
# Schema version (required)
schema_version: "2.1.0"

# Metadata about the prompt file (required)
metadata:
  title: string                    # Human-readable title (required)
  description: string              # Brief description of purpose (required)
  version: string                  # Semantic version of this prompt (optional)
  author: string                   # Author name or email (optional)
  created: string                  # ISO 8601 date (YYYY-MM-DD) (optional)
  updated: string                  # ISO 8601 date (YYYY-MM-DD) (optional)
  tags: [string]                   # Tags for categorization (optional)

# Main markdown content (required)
content: string                    # Raw markdown content

# Optional: Main content metadata
content_description: string        # Description for main content (used in editor frontmatter)
content_always_apply: boolean      # Whether main content always applies (default: True)

# Optional: Multi-file support for editors like Continue, Windsurf, Kiro, Cursor
documents:
  - name: string                   # Document name (becomes filename)
    content: string                # Raw markdown content for this document
    description: string            # Human-readable description (optional)
    file_globs: string             # File patterns where this applies (optional)
    always_apply: boolean          # Whether to always apply this rule (optional)

# Template variables (optional)
variables:
  variable_name: string            # Variable value

# .gitignore management (optional)
ignore_editor_files: boolean       # Auto-exclude generated editor files (default: true)

# Plugin configurations (optional, new in v2.1.0)
plugins:
  # MCP (Model Context Protocol) servers
  mcp_servers:
    - name: string                 # Server name/identifier (required)
      command: string              # Command to start the server (required)
      args: [string]               # Command line arguments (optional)
      env:                         # Environment variables (optional)
        VAR_NAME: string
      description: string          # Human-readable description (optional)
      trust_metadata:              # Trust and security metadata (optional)
        trusted: boolean           # Whether this plugin is trusted
        trust_level: string        # 'full', 'partial', or 'untrusted'
        requires_approval: boolean # Whether actions require approval
        source: string             # Source of the plugin
        verified_by: string        # Who verified this plugin
        verified_date: string      # When verified (ISO 8601)

  # Custom slash commands
  commands:
    - name: string                 # Command name (required, e.g., 'review-code')
      description: string          # Command description (required)
      prompt: string               # Prompt template (required)
      output_format: string        # Expected output format (optional)
      requires_approval: boolean   # Whether execution requires approval (optional)
      system_message: string       # Optional system message (optional)
      examples: [string]           # Usage examples (optional)
      trust_metadata: {}           # Trust metadata (optional)

  # Autonomous agents
  agents:
    - name: string                 # Agent name (required)
      description: string          # Agent description (required)
      system_prompt: string        # System prompt for the agent (required)
      tools: [string]              # Available tools (optional)
      trust_level: string          # Trust level: 'full', 'partial', 'untrusted'
      requires_approval: boolean   # Whether actions require approval
      context: {}                  # Additional context (optional)
      trust_metadata: {}           # Trust metadata (optional)

  # Event-driven hooks
  hooks:
    - name: string                 # Hook name (required)
      event: string                # Trigger event (required, e.g., 'pre-commit')
      command: string              # Command to execute (required)
      conditions: {}               # Execution conditions (optional)
      requires_reapproval: boolean # Whether hook requires reapproval (optional)
      description: string          # Hook description (optional)
      trust_metadata: {}           # Trust metadata (optional)
```

### v2.1 Plugin Examples

#### MCP Servers

Configure Model Context Protocol servers for external integrations:

```yaml
schema_version: "2.1.0"
metadata:
  title: "Project with MCP Servers"
  description: "AI assistant with GitHub and filesystem access"
  version: "1.0.0"
content: |
  # Project Guidelines
  Use MCP servers for external integrations.

variables:
  GITHUB_TOKEN: "ghp_your_token_here"

plugins:
  mcp_servers:
    - name: filesystem
      command: npx
      args:
        - "-y"
        - "@modelcontextprotocol/server-filesystem"
        - "/path/to/allowed/directory"
      description: "Filesystem access for the AI"
      trust_metadata:
        trusted: true
        trust_level: partial
        source: official

    - name: github
      command: npx
      args:
        - "-y"
        - "@modelcontextprotocol/server-github"
      env:
        GITHUB_TOKEN: "{{{ GITHUB_TOKEN }}}"
      description: "GitHub integration"
      trust_metadata:
        trusted: true
        trust_level: full
        source: official
```

#### Custom Commands

Define slash commands for your AI editor:

```yaml
schema_version: "2.1.0"
metadata:
  title: "Project with Custom Commands"
  description: "AI assistant with custom slash commands"
  version: "1.0.0"
content: |
  # Project Guidelines
  Use custom commands for common tasks.

plugins:
  commands:
    - name: review-pr
      description: "Review pull request for code quality"
      prompt: |
        Review this pull request for:
        - Code quality and best practices
        - Security vulnerabilities
        - Performance issues
        - Test coverage

        Provide specific, actionable feedback.
      output_format: markdown
      requires_approval: false
      system_message: "You are an expert code reviewer"
      examples:
        - "review-pr --pr=123"
        - "review-pr --detailed"

    - name: generate-tests
      description: "Generate unit tests for selected code"
      prompt: |
        Generate comprehensive unit tests for the selected code.
        Include:
        - Normal operation tests
        - Edge cases
        - Error handling
        - Mocking external dependencies
      requires_approval: false
```

#### Autonomous Agents

Configure AI agents with specific tools and permissions:

```yaml
schema_version: "2.1.0"
metadata:
  title: "Project with Autonomous Agents"
  description: "AI assistant with configured agents"
  version: "1.0.0"
content: |
  # Project Guidelines
  Use agents for automated tasks.

plugins:
  agents:
    - name: test-generator
      description: "Automatically generate unit tests"
      system_prompt: |
        You are a test automation expert. Generate comprehensive tests that:
        - Cover normal operations
        - Test edge cases
        - Handle error conditions
        - Mock external dependencies appropriately
      tools:
        - file_read
        - file_write
        - run_tests
      trust_level: partial
      requires_approval: true
      context:
        framework: pytest
        coverage_target: 80

    - name: bug-fixer
      description: "Automatically fix common bugs"
      system_prompt: |
        You are a bug-fixing specialist. Identify and fix bugs while:
        - Understanding the root cause
        - Applying minimal, focused changes
        - Adding tests to prevent regression
      tools:
        - file_read
        - file_write
        - git_diff
      trust_level: untrusted
      requires_approval: true
```

#### Event Hooks

Automate workflows with event-driven hooks:

```yaml
schema_version: "2.1.0"
metadata:
  title: "Project with Event Hooks"
  description: "AI assistant with automated workflows"
  version: "1.0.0"
content: |
  # Project Guidelines
  Hooks automate common workflows.

plugins:
  hooks:
    - name: pre-commit-tests
      event: pre-commit
      command: "npm test"
      description: "Run tests before every commit"
      requires_reapproval: true

    - name: auto-regenerate
      event: post-save
      command: "promptrek generate --all"
      conditions:
        file_pattern: "*.promptrek.yaml"
      requires_reapproval: false
      description: "Auto-regenerate editor files when .promptrek.yaml changes"
```

### Complete v2.1 Example

```yaml
schema_version: "2.1.0"

metadata:
  title: "Full Stack TypeScript Project"
  description: "AI assistant with MCP servers, commands, and agents"
  version: "1.0.0"
  author: "dev-team@company.com"
  tags: ["typescript", "fullstack", "ai-enhanced"]

content: |
  # Full Stack TypeScript Project

  ## Project Overview
  Modern full-stack application with TypeScript, React, and Node.js.
  Enhanced with MCP servers for GitHub integration and filesystem access.

  **Tech Stack:**
  - React 18 with TypeScript
  - Node.js with Express
  - PostgreSQL database
  - Jest for testing

  ## Development Guidelines

  ### General Principles
  - Write type-safe code with strict TypeScript
  - Use functional programming patterns
  - Add comprehensive tests for all features
  - Document complex business logic

  ### Code Style
  - Use named exports
  - Prefer arrow functions
  - Follow ESLint and Prettier configs
  - Use meaningful variable names

variables:
  PROJECT_NAME: "FullStack App"
  GITHUB_TOKEN: "ghp_token_here"
  GITHUB_OWNER: "myorg"

plugins:
  mcp_servers:
    - name: github
      command: npx
      args: ["-y", "@modelcontextprotocol/server-github"]
      env:
        GITHUB_TOKEN: "{{{ GITHUB_TOKEN }}}"
        GITHUB_OWNER: "{{{ GITHUB_OWNER }}}"
      description: "GitHub API integration"
      trust_metadata:
        trusted: true
        trust_level: full
        source: official

  commands:
    - name: review-code
      description: "Review code for quality and best practices"
      prompt: |
        Review the selected code for:
        - TypeScript best practices
        - Code quality and maintainability
        - Security vulnerabilities
        - Performance optimizations
      output_format: markdown
      requires_approval: false

  agents:
    - name: test-generator
      description: "Generate comprehensive unit tests"
      system_prompt: |
        Generate Jest tests with TypeScript that cover:
        - Normal operations
        - Edge cases
        - Error handling
        Target 80% coverage.
      tools: [file_read, file_write, run_tests]
      trust_level: partial
      requires_approval: true
      context:
        framework: jest
        coverage_target: 80

  hooks:
    - name: pre-commit
      event: pre-commit
      command: "npm run lint && npm test"
      description: "Run linting and tests before commit"
      requires_reapproval: true
```

### CLI Commands for Plugins

```bash
# List all plugins in a .promptrek.yaml file
promptrek plugins list --file project.promptrek.yaml

# Generate plugin files for a specific editor
promptrek plugins generate --file project.promptrek.yaml --editor claude --output .

# Validate plugin configuration
promptrek plugins validate --file project.promptrek.yaml

# Sync plugins from editor files back to .promptrek.yaml
promptrek plugins sync --editor claude --source-dir . --output synced.promptrek.yaml
```

### Migration from v2.0 to v2.1

v2.0 files are **100% compatible** with v2.1 - no migration needed! Simply add the `plugins` field when you're ready:

```bash
# Optional: Explicitly migrate to v2.1
promptrek migrate old.promptrek.yaml -o new.promptrek.yaml

# v2.0 files work as-is (plugins field is optional)
promptrek generate v2.0-file.promptrek.yaml --editor claude
```

---

## Schema v2.0 (Legacy)

**v2.0.0** (Superseded by v3.0): Simpler markdown-first approach that aligns with how AI editors actually work.

### Key Benefits

- ✅ **No `targets` field** - Works with ALL editors automatically
- ✅ **Lossless bidirectional sync** - Parse editor files back without data loss
- ✅ **Simpler format** - Just markdown content, no complex nested structures
- ✅ **Editor-friendly** - Matches how Claude Code, Copilot, and others use markdown
- ✅ **Multi-file support** - Use `documents` field for multi-file editors

### Complete v2 Schema

```yaml
# Schema version (required)
schema_version: "2.0.0"

# Metadata about the prompt file (required)
metadata:
  title: string                    # Human-readable title (required)
  description: string              # Brief description of purpose (required)
  version: string                  # Semantic version of this prompt (optional)
  author: string                   # Author name or email (optional)
  created: string                  # ISO 8601 date (YYYY-MM-DD) (optional)
  updated: string                  # ISO 8601 date (YYYY-MM-DD) (optional)
  tags: [string]                   # Tags for categorization (optional)

# Main markdown content (required)
content: string                    # Raw markdown content

# Optional: Main content metadata
content_description: string        # Description for main content (used in editor frontmatter)
content_always_apply: boolean      # Whether main content always applies (default: True)

# Optional: Multi-file support for editors like Continue, Windsurf, Kiro, Cursor
documents:
  - name: string                   # Document name (becomes filename)
    content: string                # Raw markdown content for this document
    description: string            # Human-readable description (optional)
    file_globs: string             # File patterns where this applies (optional)
    always_apply: boolean          # Whether to always apply this rule (optional)

# Template variables (optional)
variables:
  variable_name: string            # Variable value

# .gitignore management (optional)
ignore_editor_files: boolean       # Auto-exclude generated editor files (default: true)
```

### v2 Field Descriptions

#### metadata (required)


**Example**:
```yaml
metadata:
  title: "My Project Assistant"
  description: "AI assistant for my project"
  version: "1.0.0"
  author: "Your Name <your.email@example.com>"
  created: "2024-01-01"
  updated: "2024-01-15"
  tags: ["project", "ai-assistant"]
```

#### content (required)

The main markdown content that will be used by AI editors. This is where you write your comprehensive guidelines, examples, and instructions in natural markdown format.

**Example**:
```yaml
content: |
  # My Project Assistant

  ## Project Details
  **Technologies:** Python, React, TypeScript

  ## Development Guidelines

  ### General Principles
  - Write clean, maintainable code
  - Follow existing patterns
  - Add tests for new features

  ### Code Style
  - Use functional components with hooks
  - Prefer const over let
  - Use meaningful variable names

  ## Code Examples

  ### Function Example
  ```python
  def calculate_total(items: list[float]) -> float:
      """Calculate the total sum of items."""
      return sum(items)
  `` `
  
```

#### documents (optional)

For multi-file editors like Continue, Windsurf, Kiro, and Cursor, you can split content into separate documents with metadata.

**Metadata Fields**:
- `description` (optional): Human-readable description (used by Cursor, etc.)
- `file_globs` (optional): File patterns where this applies (e.g., `**/*.{ts,tsx}`)
- `always_apply` (optional): Whether to always apply this rule (Cursor alwaysApply)

**Example**:
```yaml
documents:
  - name: "general-rules"
    content: |
      # General Coding Rules
      - Write clean code
      - Follow best practices
    description: "General coding guidelines"
    always_apply: true

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
    # Omit metadata for smart defaults:
    # - description: "testing guidelines" (inferred from name)
    # - file_globs: "**/*.{test,spec}.*" (inferred for Cursor)
    # - always_apply: false (default for documents)
```

#### variables (optional)

Template variables using `{``{``{``VARIABLE_NAME``}``}``}` syntax (triple braces to distinguish from Jinja2).

**Example**:
```yaml
content: |
  # { { { PROJECT_NAME } } }

  Project for { { { COMPANY } } }.

  Technologies: { { { TECH_STACK } } }

variables:
  PROJECT_NAME: "My App"
  COMPANY: "Acme Corp"
  TECH_STACK: "Python, React"
```
*Note: due to a rendering bug in the example, spaces are added between each curly bracket for variables. Don't actually add spaces in real usage.*

### Complete v2 Example

```yaml
schema_version: "2.0.0"

metadata:
  title: "React TypeScript Project"
  description: "AI assistant for React TypeScript development"
  version: "1.0.0"
  author: "dev-team@company.com"
  tags: ["react", "typescript", "frontend"]

content: |
  # React TypeScript Project

  ## Project Overview
  Modern React application with TypeScript, focusing on clean architecture and best practices.

  **Tech Stack:**
  - React 18
  - TypeScript
  - Vite
  - React Router
  - TanStack Query

  ## Development Guidelines

  ### General Principles
  - Write type-safe code with strict TypeScript settings
  - Use functional components with hooks
  - Follow React best practices and patterns
  - Add comprehensive JSDoc comments

  ### Code Style
  - Use named exports for components
  - Prefer arrow functions for components
  - Use destructuring for props
  - Follow existing ESLint and Prettier configurations

  ### Testing
  - Write tests using Vitest and React Testing Library
  - Test user interactions, not implementation details
  - Aim for 80%+ test coverage
  - Mock external dependencies

  ## Code Examples

  ### Component Example
  ```typescript
  interface ButtonProps {
    label: string;
    onClick: () => void;
    variant?: 'primary' | 'secondary';
  }

  export const Button: React.FC<ButtonProps> = ({
    label,
    onClick,
    variant = 'primary'
  }) => {
    return (
      <button
        className={`btn btn--${variant}`}
        onClick={onClick}
      >
        {label}
      </button>
    );
  };
  `` `

  ### Hook Example
  ```typescript
  export const useUser = (userId: string) => {
    return useQuery({
      queryKey: ['user', userId],
      queryFn: () => fetchUser(userId),
      staleTime: 5 * 60 * 1000,
    });
  };
  `` `

variables:
  PROJECT_NAME: "react-app"
  TEAM_EMAIL: "dev-team@company.com"
```



### Why Migrate to v3.0?

**v3.0 offers:**
- ✅ Simple markdown-first format
- ✅ Top-level plugin fields (cleaner than v2.x nested structure)
- ✅ Lossless bidirectional sync
- ✅ Works with ALL editors without `targets`
- ✅ Matches how AI editors use markdown natively

---

📋 [Complete v3.0 Examples](../../examples/) in the repository


