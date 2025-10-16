# PrompTrek v3.0.0 Migration Guide

## Overview

PrompTrek v3.0.0 introduces a cleaner, more intuitive plugin architecture by promoting plugin fields to the top level of your `.promptrek.yaml` files. This guide will help you migrate from v2.1 to v3.0.

## What's New in v3.0.0

### Top-Level Plugin Fields

In v3.0.0, plugin configurations are now top-level fields instead of being nested under `plugins`:

**Before (v2.1):**
```yaml
schema_version: "2.1.0"
metadata:
  title: "My Project"
content: |
  # Project Guidelines
  ...

plugins:
  mcp_servers:
    - name: github
      command: npx
      args: ["-y", "@modelcontextprotocol/server-github"]

  commands:
    - name: review-code
      description: "Review code quality"
      prompt: "Review the code for quality issues"

  agents:
    - name: test-generator
      description: "Generate tests"
      system_prompt: "Generate comprehensive tests"

  hooks:
    - name: pre-commit
      event: pre-commit
      command: "uv run pytest"
```

**After (v3.0.0):**
```yaml
schema_version: "3.0.0"
metadata:
  title: "My Project"
content: |
  # Project Guidelines
  ...

# Plugin fields are now top-level
mcp_servers:
  - name: github
    command: npx
    args: ["-y", "@modelcontextprotocol/server-github"]

commands:
  - name: review-code
    description: "Review code quality"
    prompt: "Review the code for quality issues"

agents:
  - name: test-generator
    description: "Generate tests"
    system_prompt: "Generate comprehensive tests"

hooks:
  - name: pre-commit
    event: pre-commit
    command: "uv run pytest"
```

## Migration Path

### Automatic Migration

PrompTrek provides built-in migration tools:

```bash
# Migrate a single file
promptrek migrate project.promptrek.yaml -o project-v3.promptrek.yaml

# Migrate and overwrite
promptrek migrate project.promptrek.yaml --in-place

# Migrate all files in a directory
for file in *.promptrek.yaml; do
  promptrek migrate "$file" --in-place
done
```

### Manual Migration

If you prefer manual migration:

1. **Update schema version:**
   ```yaml
   # Change from:
   schema_version: "2.1.0"
   # To:
   schema_version: "3.0.0"
   ```

2. **Move plugin fields to top level:**
   - `plugins.mcp_servers` → `mcp_servers`
   - `plugins.commands` → `commands`
   - `plugins.agents` → `agents`
   - `plugins.hooks` → `hooks`

3. **Remove the `plugins` wrapper:**
   ```yaml
   # Remove this:
   plugins:
     mcp_servers: [...]
     commands: [...]

   # Keep only this:
   mcp_servers: [...]
   commands: [...]
   ```

## Backward Compatibility

### v2.1 Files Still Work

PrompTrek v3.0.0 maintains **100% backward compatibility** with v2.1 files:

- v2.1 files with nested `plugins.*` structure continue to work
- A deprecation warning is displayed when using the old structure
- The parser automatically promotes nested fields to top-level internally

### Deprecation Warnings

When using the deprecated v2.1 nested structure, you'll see warnings like:

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

### Migration Timeline

- **v3.0.0** (Current): Nested structure deprecated but supported
- **v4.0.0** (Future): Nested structure will be removed

## Benefits of v3.0.0

### 1. Cleaner Structure
```yaml
# v2.1 - Nested (redundant wrapper)
plugins:
  mcp_servers: [...]

# v3.0 - Flat (simpler)
mcp_servers: [...]
```

### 2. Consistency with v2.0 Philosophy

v2.0 introduced a flatter, markdown-first approach. v3.0 extends this to plugins:
- No unnecessary nesting
- Clear, intuitive structure
- Easier to read and write

### 3. Better Tooling Support

Top-level fields are easier for:
- IDE auto-completion
- Schema validation
- Documentation generation
- Static analysis tools

### 4. Future-Proof

The flat structure makes it easier to add new plugin types without introducing more nesting.

## Complete Example

### Full v3.0.0 Configuration

```yaml
schema_version: "3.0.0"

metadata:
  title: "Full-Featured Project"
  description: "Complete example with all v3.0 features"
  version: "1.0.0"
  author: "Your Name"
  tags: [typescript, react, ai-powered]
  created: "2024-10-16"
  updated: "2024-10-16"

content: |
  # Full-Featured Project

  ## Project Overview
  This is a TypeScript React project with comprehensive AI assistance.

  ## Development Guidelines

  ### Code Quality
  - Write TypeScript with strict mode enabled
  - Use functional components with hooks
  - Maintain 80%+ test coverage

  ### Best Practices
  - Follow React best practices
  - Use meaningful variable names
  - Write clear comments for complex logic

variables:
  PROJECT_NAME: "my-app"
  GITHUB_TOKEN: "ghp_your_token"
  API_KEY: "your_api_key"

# MCP Servers - Top level in v3.0
mcp_servers:
  - name: github
    command: npx
    args: ["-y", "@modelcontextprotocol/server-github"]
    env:
      GITHUB_TOKEN: "{{{ GITHUB_TOKEN }}}"
    description: "GitHub API integration for code analysis"
    trust_metadata:
      trusted: true
      trust_level: full

  - name: filesystem
    command: npx
    args: ["-y", "@modelcontextprotocol/server-filesystem", "./src"]
    description: "Filesystem access for code operations"
    trust_metadata:
      trusted: true
      trust_level: partial

# Custom Commands - Top level in v3.0
commands:
  - name: review-code
    description: "Comprehensive code review"
    prompt: |
      Review the selected code for:
      - Code quality and best practices
      - Security vulnerabilities
      - Performance optimizations
      - TypeScript type safety
    output_format: markdown
    requires_approval: false
    examples:
      - "Review this React component"
      - "Check this API endpoint for issues"

  - name: generate-tests
    description: "Generate unit tests"
    prompt: |
      Generate comprehensive unit tests for the selected code:
      - Use Jest and React Testing Library
      - Aim for 100% code coverage
      - Include edge cases
      - Test both happy and error paths
    output_format: code
    requires_approval: true

# Autonomous Agents - Top level in v3.0
agents:
  - name: test-generator
    description: "Automated test generation"
    system_prompt: |
      Generate comprehensive tests with Jest and React Testing Library.
      Focus on component behavior, edge cases, and accessibility.
    tools: [file_read, file_write, run_tests]
    trust_level: partial
    requires_approval: true
    context:
      testing_framework: jest
      coverage_target: 80

  - name: refactoring-assistant
    description: "Code refactoring helper"
    system_prompt: |
      Assist with code refactoring while maintaining functionality.
      Preserve existing behavior and improve code quality.
    tools: [file_read, file_write, run_tests]
    trust_level: partial
    requires_approval: true

# Event Hooks - Top level in v3.0
hooks:
  - name: pre-commit
    event: pre-commit
    command: "uv run pytest tests/ --cov=src"
    conditions:
      - path: "**/*.py"
    requires_reapproval: false

  - name: post-merge
    event: post-merge
    command: "uv sync"
    requires_reapproval: false

# Optional: Multi-file support (unchanged from v2.0)
documents:
  - name: "testing-guidelines"
    content: |
      # Testing Guidelines
      - Write tests for all new features
      - Maintain 80%+ coverage
      - Use meaningful test descriptions

  - name: "architecture-decisions"
    content: |
      # Architecture Decisions
      - Use React functional components
      - State management with Context API
      - API calls with React Query
```

## Validation

After migration, validate your configuration:

```bash
# Validate syntax and structure
promptrek validate project-v3.promptrek.yaml

# Preview generated output
promptrek preview project-v3.promptrek.yaml --editor claude

# Generate for specific editor
promptrek generate project-v3.promptrek.yaml --editor claude
```

## Troubleshooting

### Issue: Migration Command Not Found

**Solution:** Ensure you have the latest version of PrompTrek:
```bash
cd /path/to/promptrek
uv sync
```

### Issue: Validation Errors After Migration

**Solution:** Check for typos in field names:
```bash
# Correct field names:
mcp_servers:  # (not mcp_server or mcpServers)
commands:     # (not command)
agents:       # (not agent)
hooks:        # (not hook)
```

### Issue: Variables Not Working

**Solution:** Variables use `{{{ VAR_NAME }}}` syntax (triple braces):
```yaml
variables:
  GITHUB_TOKEN: "ghp_token"

mcp_servers:
  - name: github
    env:
      GITHUB_TOKEN: "{{{ GITHUB_TOKEN }}}"  # Correct
      # Not: {{ GITHUB_TOKEN }}              # Wrong
      # Not: ${GITHUB_TOKEN}                 # Wrong
```

## Getting Help

- **Documentation:** https://flamingquaks.github.io/promptrek
- **Issues:** https://github.com/flamingquaks/promptrek/issues
- **Discussions:** https://github.com/flamingquaks/promptrek/discussions

## Next Steps

1. Migrate your files to v3.0.0
2. Update your documentation to reference v3.0.0
3. Test with your preferred AI editor
4. Share feedback on the new structure

---

**Note:** The v2.1 nested structure will continue to work until v4.0.0, giving you plenty of time to migrate at your own pace.
