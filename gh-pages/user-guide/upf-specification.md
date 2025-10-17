---
layout: guide
title: UPF Specification
---

# Universal Prompt Format (UPF) Specification

## Overview

The Universal Prompt Format (UPF) is a standardized YAML-based format for defining AI assistant prompts that can be converted to various editor-specific formats.

PrompTrek supports **four schema versions**:
- **v3.0.0** (Stable): Top-level plugin fields, cleaner architecture (backward compatible with v2.x)
- **v2.1.0** (Legacy): Markdown-first with nested plugin support (superseded by v3.0)
- **v2.0.0** (Legacy): Markdown-first, simpler format with lossless bidirectional sync
- **v1.0.0** (Legacy): Structured format with complex nested fields

## File Extension

`.promptrek.yaml`

## Schema Versions

- **Stable**: `3.0.0` - [Jump to v3.0 Specification](#schema-v30-stable)
- **Legacy**: `2.1.0` - [Jump to v2.1 Specification](#schema-v21-legacy)
- **Legacy**: `2.0.0` - [Jump to v2.0 Specification](#schema-v20-legacy)
- **Legacy**: `1.0.0` - [Jump to v1 Specification](#schema-v10-legacy)

---

## Schema v3.0 (Stable)

**v3.0.0**: Cleaner plugin architecture by promoting plugin fields to the top level.

### What's New in v3.0

- ✨ **Top-Level Plugin Fields** - No more `plugins` wrapper, cleaner YAML structure
- ✅ **100% Backward Compatible** - v2.x files continue to work with automatic migration
- 🔄 **Automatic Migration** - Built-in tools to convert v2.x → v3.0
- 📋 **Production Ready** - Stable schema for all new projects
- 🎯 **Recommended** - Use v3.0 for all new projects

### Key Changes from v2.1

**Before (v2.1) - Nested structure:**
```yaml
schema_version: "2.1.0"
plugins:                    # ❌ Unnecessary wrapper
  mcp_servers: [...]
  commands: [...]
  agents: [...]
  hooks: [...]
```

**After (v3.0) - Flat structure:**
```yaml
schema_version: "3.0.0"
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

# Optional: Multi-file support for editors like Continue, Windsurf, Kiro
documents:
  - name: string                   # Document name (becomes filename)
    content: string                # Raw markdown content for this document

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

# Optional: Multi-file support for editors like Continue, Windsurf, Kiro
documents:
  - name: string                   # Document name (becomes filename)
    content: string                # Raw markdown content for this document

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

  # Marketplace metadata
  marketplace_metadata:
    plugin_id: string              # Unique plugin identifier (optional)
    marketplace_url: string        # URL to marketplace listing (optional)
    rating: number                 # User rating 0-5 (optional)
    downloads: number              # Number of downloads (optional)
    last_updated: string           # Last update date (optional)
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

# Optional: Multi-file support for editors like Continue, Windsurf, Kiro
documents:
  - name: string                   # Document name (becomes filename)
    content: string                # Raw markdown content for this document

# Template variables (optional)
variables:
  variable_name: string            # Variable value

# .gitignore management (optional)
ignore_editor_files: boolean       # Auto-exclude generated editor files (default: true)
```

### v2 Field Descriptions

#### metadata (required)

Same as v1 - contains information about the prompt file.

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
  ```
```

#### documents (optional)

For multi-file editors like Continue, Windsurf, and Kiro, you can split content into separate documents.

**Example**:
```yaml
documents:
  - name: "general-rules"
    content: |
      # General Coding Rules
      - Write clean code
      - Follow best practices

  - name: "code-style"
    content: |
      # Code Style Guidelines
      - Use meaningful variable names
      - Follow PEP 8 for Python

  - name: "testing"
    content: |
      # Testing Standards
      - Write unit tests for all functions
      - Aim for 80% coverage
```

#### variables (optional)

Template variables using `{{{ VARIABLE_NAME }}}` syntax (triple braces to distinguish from Jinja2).

**Example**:
```yaml
content: |
  # {{{ PROJECT_NAME }}}

  Project for {{{ COMPANY }}}.

  Technologies: {{{ TECH_STACK }}}

variables:
  PROJECT_NAME: "My App"
  COMPANY: "Acme Corp"
  TECH_STACK: "Python, React"
```

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
  ```

  ### Hook Example
  ```typescript
  export const useUser = (userId: string) => {
    return useQuery({
      queryKey: ['user', userId],
      queryFn: () => fetchUser(userId),
      staleTime: 5 * 60 * 1000,
    });
  };
  ```

variables:
  PROJECT_NAME: "react-app"
  TEAM_EMAIL: "dev-team@company.com"
```

### Migration from v1 to v2

Use the `promptrek migrate` command to convert v1 files to v2:

```bash
promptrek migrate old.promptrek.yaml -o new.promptrek.yaml
```

The migration tool:
- ✅ Converts structured `instructions` to markdown `content`
- ✅ Converts `examples` to markdown code blocks
- ✅ Preserves `metadata` and `variables`
- ✅ Removes `targets` field (no longer needed in v2)
- ✅ Optionally splits into `documents` for multi-file editors

---

## Schema v1.0 (Legacy)

## Complete Schema

```yaml
# Schema version (required)
schema_version: "1.0.0"

# Metadata about the prompt file (required)
metadata:
  title: string                    # Human-readable title (required)
  description: string              # Brief description of purpose (required)
  version: string                  # Semantic version of this prompt (optional)
  author: string                   # Author name or email (optional)
  created: string                  # ISO 8601 date (YYYY-MM-DD) (optional)
  updated: string                  # ISO 8601 date (YYYY-MM-DD) (optional)
  tags: [string]                   # Tags for categorization (optional)

# Target editors this prompt supports (optional)
targets:
  - string                         # List of supported editor names (optional)

# Project context information (optional)
context:
  project_type: string             # e.g., "web_application", "api", "library"
  technologies: [string]           # List of technologies used
  description: string              # Detailed project description
  repository_url: string           # Optional repository URL
  documentation_url: string        # Optional documentation URL

# Main instructions (required)
instructions:
  general: [string]                # General coding guidelines
  code_style: [string]             # Code style and formatting rules
  architecture: [string]           # Architectural patterns and principles
  testing: [string]                # Testing guidelines
  documentation: [string]          # Documentation requirements
  security: [string]               # Security considerations
  performance: [string]            # Performance guidelines

# Workflows and automation (optional)
workflows:
  development: [string]            # Development workflow steps
  review: [string]                 # Code review workflow
  testing: [string]               # Testing workflow steps
  deployment: [string]             # Deployment workflow
  collaboration: [string]          # Team collaboration workflows

# Code examples and templates (optional)
examples:
  example_name: string             # Code example in markdown format
  # ... more examples

# Template variables (optional)
variables:
  variable_name: string            # Default value or placeholder
  # ... more variables

# .gitignore management (optional)
ignore_editor_files: boolean       # Auto-exclude generated editor files (default: true)

# Editor-specific configurations (optional)
editor_specific:
  editor_name:
    additional_instructions: [string]
    custom_commands: 
      - name: string
        prompt: string
        description: string
    templates:
      template_name: string
    # ... editor-specific fields

# Conditional instructions (optional)
conditions:
  - if: string                     # Condition expression
    then:
      instructions: [string]
      examples: {}
    else:                          # Optional
      instructions: [string]
      examples: {}

# Import other prompt files (optional)
imports:
  - path: string                   # Relative path to another .promptrek.yaml file
    prefix: string                 # Optional namespace prefix
```

## Detailed Field Descriptions

### metadata (required)

Contains information about the prompt file itself.

**Fields**:
- `title`: Human-readable title for the prompt set
- `description`: Brief description of what this prompt configuration is for
- `version`: Semantic version of this prompt file (for tracking changes)
- `author`: Author name or email address
- `created`: Creation date in ISO 8601 format (YYYY-MM-DD)
- `updated`: Last update date in ISO 8601 format (YYYY-MM-DD)
- `tags`: Array of tags for categorization and filtering

**Example**:
```yaml
metadata:
  title: "React TypeScript Project Assistant"
  description: "AI assistant configuration for React projects with TypeScript"
  version: "1.2.0"
  author: "john.doe@example.com"
  created: "2024-01-01"
  updated: "2024-01-15"
  tags: ["react", "typescript", "frontend"]
```

### targets (required)

List of AI editors/tools that this prompt configuration supports.

**Supported Values**:
- `copilot`: GitHub Copilot
- `cursor`: Cursor editor
- `continue`: Continue extension
- `claude_code`: Claude Code
- `kiro`: Kiro AI assistant
- `cline`: Cline VSCode extension (autonomous AI coding agent)
- `windsurf`: Windsurf
- `tabnine`: Tabnine
- `amazon_q`: Amazon Q (formerly CodeWhisperer)
- `jetbrains_ai`: JetBrains AI Assistant

**Example**:
```yaml
targets:
  - copilot
  - cursor
  - continue
```

### context (optional)

Provides context about the project to help AI assistants understand the codebase.

**Fields**:
- `project_type`: Type of project (web_application, api, library, mobile_app, etc.)
- `technologies`: Array of technologies, frameworks, and languages used
- `description`: Detailed description of the project's purpose and architecture
- `repository_url`: URL to the project repository
- `documentation_url`: URL to project documentation

**Example**:
```yaml
context:
  project_type: "web_application"
  technologies:
    - "typescript"
    - "react"
    - "node.js"
    - "express"
    - "postgresql"
  description: |
    A modern e-commerce web application built with React and TypeScript.
    Uses a microservices architecture with Node.js backends and PostgreSQL databases.
  repository_url: "https://github.com/company/ecommerce-app"
  documentation_url: "https://docs.company.com/ecommerce-app"
```

### instructions (required)

The main set of instructions for AI assistants. At least one instruction category must be present.

**Categories**:
- `general`: General coding guidelines and principles
- `code_style`: Code style, formatting, and naming conventions
- `architecture`: Architectural patterns and design principles
- `testing`: Testing strategies and requirements
- `documentation`: Documentation standards and requirements
- `security`: Security considerations and best practices
- `performance`: Performance optimization guidelines

**Example**:
```yaml
instructions:
  general:
    - "Write clean, readable, and maintainable code"
    - "Use TypeScript for all new files"
    - "Follow existing code patterns and conventions"
    - "Add comprehensive comments for complex logic"
  
  code_style:
    - "Use functional components in React"
    - "Prefer arrow functions over function declarations"
    - "Use meaningful and descriptive variable names"
    - "Follow the existing ESLint configuration"
  
  architecture:
    - "Follow the existing folder structure"
    - "Separate concerns into different modules"
    - "Use custom hooks for reusable React logic"
    - "Keep components small and focused on a single responsibility"
  
  testing:
    - "Write unit tests for all new functions and components"
    - "Use React Testing Library for component tests"
    - "Aim for at least 80% code coverage"
  
  security:
    - "Sanitize all user inputs"
    - "Use parameterized queries for database operations"
    - "Implement proper authentication and authorization"
```

### workflows (optional)

Defines development workflows and automation guidelines that AI assistants should understand and support.

**Categories**:
- `development`: Development workflow steps and practices
- `review`: Code review workflow and standards
- `testing`: Testing workflow and automation
- `deployment`: Deployment workflow and procedures
- `collaboration`: Team collaboration workflows

**Example**:
```yaml
workflows:
  development:
    - "Start by creating a feature branch from main"
    - "Write tests before implementing functionality (TDD)"
    - "Make small, focused commits with descriptive messages"
    - "Run linting and tests before pushing changes"
  
  review:
    - "Create pull requests with clear descriptions and context"
    - "Request reviews from at least two team members"
    - "Address all review comments before merging"
    - "Ensure CI/CD checks pass before merging"
  
  testing:
    - "Run unit tests locally before committing"
    - "Ensure integration tests pass in CI environment"
    - "Perform manual testing for UI changes"
    - "Update test documentation when adding new test scenarios"
  
  deployment:
    - "Deploy to staging environment first"
    - "Run smoke tests after deployment"
    - "Monitor application logs and metrics"
    - "Have rollback plan ready for production deployments"
  
  collaboration:
    - "Use standardized commit message format"
    - "Update team on progress during daily standups"
    - "Document architectural decisions in ADRs"
    - "Share knowledge through code comments and documentation"
```

### examples (optional)

Code examples and templates that demonstrate best practices.

**Format**: Key-value pairs where the key is a descriptive name and the value is a markdown-formatted code example.

**Example**:
```yaml
examples:
  react_component: |
    ```typescript
    interface ButtonProps {
      title: string;
      onClick: () => void;
      variant?: 'primary' | 'secondary';
    }
    
    export const Button: React.FC<ButtonProps> = ({ 
      title, 
      onClick, 
      variant = 'primary' 
    }) => {
      return (
        <button 
          onClick={onClick} 
          className={`btn btn--${variant}`}
        >
          {title}
        </button>
      );
    };
    ```
  
  api_endpoint: |
    ```typescript
    export const getUserById = async (id: string): Promise<User> => {
      const response = await fetch(`/api/users/${id}`);
      if (!response.ok) {
        throw new Error(`Failed to fetch user: ${response.statusText}`);
      }
      return response.json();
    };
    ```
```

### variables (optional)

Template variables that can be substituted in generated prompts.

**Usage**: Variables are referenced in instructions and examples using `${VARIABLE_NAME}` syntax.

**Example**:
```yaml
variables:
  PROJECT_NAME: "My Awesome Project"
  AUTHOR_NAME: "John Doe"
  TECH_STACK: "React, TypeScript, Node.js"
  API_BASE_URL: "https://api.example.com"

instructions:
  general:
    - "This is the ${PROJECT_NAME} codebase"
    - "Contact ${AUTHOR_NAME} for questions about architecture"
```

### editor_specific (optional)

Editor-specific configurations and additional instructions.

**Structure**: Each editor can have its own section with custom fields.

**Common Fields**:
- `additional_instructions`: Extra instructions specific to this editor
- `custom_commands`: Custom commands or shortcuts (for editors that support them)
- `templates`: Editor-specific templates
- `settings`: Editor-specific settings

**Example**:
{% raw %}
```yaml
editor_specific:
  copilot:
    additional_instructions:
      - "Focus on code completion and suggestions"
      - "Provide context-aware variable names"
      - "Generate comprehensive docstrings"
  
  cursor:
    additional_instructions:
      - "Be concise in explanations"
      - "Focus on quick implementations"
    custom_commands:
      - name: "refactor"
        prompt: "Refactor this code to improve readability"
        description: "Improves code structure and readability"
  
  continue:
    custom_commands:
      - name: "explain"
        prompt: "Explain this code in detail: {{{ input }}}"
        description: "Provides detailed code explanation"
      - name: "optimize"
        prompt: "Suggest optimizations for this code: {{{ input }}}"
        description: "Suggests performance improvements"
    settings:
      temperature: 0.7
      max_tokens: 1000
```
{% endraw %}

### conditions (optional)

Conditional instructions that are applied based on certain criteria.

**Use Cases**:
- Different instructions for different file types
- Environment-specific guidelines (development vs production)
- Technology-specific rules

**Example**:
```yaml
conditions:
  - if: "file_extension == '.test.ts'"
    then:
      instructions:
        - "Focus on comprehensive test coverage"
        - "Use descriptive test names"
        - "Mock external dependencies"
  
  - if: "editor == 'cursor'"
    then:
      instructions:
        - "Provide quick, actionable suggestions"
    else:
      instructions:
        - "Provide detailed explanations"
```

### imports (optional)

Import configurations from other UPF files for modularity and reusability.

**Use Cases**:
- Shared team standards
- Technology-specific configurations
- Organization-wide guidelines

**Example**:
```yaml
imports:
  - path: "../shared/typescript-standards.promptrek.yaml"
    prefix: "ts"
  - path: "./team-conventions.promptrek.yaml"
```

## Validation Rules

1. **Required Fields**: `schema_version`, `metadata`, `targets`, `instructions`
2. **Schema Version**: Must be a valid semantic version string
3. **Targets**: Must contain at least one supported editor name
4. **Instructions**: Must contain at least one instruction category with at least one instruction
5. **Workflows**: All workflow categories are optional, but if present, must contain at least one workflow step
6. **Variables**: Variable names must be valid identifiers (alphanumeric + underscore)
7. **Imports**: Imported files must exist and be valid UPF files

## Example Complete File

```yaml
schema_version: "1.0.0"

metadata:
  title: "React TypeScript E-commerce Project"
  description: "AI assistant configuration for our e-commerce platform"
  version: "2.1.0"
  author: "development-team@company.com"
  created: "2024-01-01"
  updated: "2024-01-15"
  tags: ["react", "typescript", "ecommerce", "frontend"]

targets:
  - copilot
  - cursor
  - continue

context:
  project_type: "web_application"
  technologies:
    - "typescript"
    - "react"
    - "node.js"
    - "express"
    - "postgresql"
    - "redis"
  description: |
    A modern e-commerce platform built with React and TypeScript.
    Features include user authentication, product catalog, shopping cart,
    and payment processing. Uses microservices architecture.

instructions:
  general:
    - "Write clean, readable, and maintainable code"
    - "Use TypeScript for all new files"
    - "Follow existing code patterns and conventions"
    - "Add comprehensive comments for complex business logic"
  
  code_style:
    - "Use functional components in React"
    - "Prefer arrow functions over function declarations"
    - "Use meaningful and descriptive variable names"
    - "Follow the existing ESLint and Prettier configuration"
  
  architecture:
    - "Follow the existing folder structure: features/components/hooks/utils"
    - "Separate concerns into different modules"
    - "Use custom hooks for reusable React logic"
    - "Keep components small and focused on a single responsibility"

workflows:
  development:
    - "Create feature branches from main for new features"
    - "Write component tests before implementing React components"
    - "Use Storybook for component documentation and testing"
    - "Run npm run lint and npm run test before committing"
  
  review:
    - "Create detailed PR descriptions with screenshots for UI changes"
    - "Ensure all TypeScript types are properly defined"
    - "Check that new components are properly exported and documented"
    - "Verify accessibility compliance for new UI components"
  
  testing:
    - "Write unit tests for all business logic functions"
    - "Create integration tests for user workflows"
    - "Test components in isolation using React Testing Library"
    - "Ensure e2e tests cover critical user paths"

examples:
  react_component: |
    ```typescript
    interface ProductCardProps {
      product: Product;
      onAddToCart: (product: Product) => void;
    }
    
    export const ProductCard: React.FC<ProductCardProps> = ({ 
      product, 
      onAddToCart 
    }) => {
      return (
        <div className="product-card">
          <img src={product.imageUrl} alt={product.name} />
          <h3>{product.name}</h3>
          <p className="price">${product.price}</p>
          <button onClick={() => onAddToCart(product)}>
            Add to Cart
          </button>
        </div>
      );
    };
    ```

variables:
  PROJECT_NAME: "E-commerce Platform"
  TEAM_EMAIL: "development-team@company.com"

editor_specific:
  copilot:
    additional_instructions:
      - "Generate comprehensive JSDoc comments for public APIs"
      - "Suggest appropriate React hooks for state management"
  
  cursor:
    additional_instructions:
      - "Focus on quick implementations and fixes"
      - "Prioritize performance optimizations"
```
