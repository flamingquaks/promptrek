---
layout: guide
title: Adapter Capabilities
---

# Adapter Capabilities Matrix

This document provides a comprehensive comparison of features supported by each PrompTrek adapter.

## Quick Reference Table

| Editor | Variable Substitution | Multi-Document Support | Bidirectional Sync | Project Files | v3.0 Schema |
|--------|:--------------------:|:----------------------:|:------------------:|:-------------:|:-------------:|
| **GitHub Copilot** | ✅ | ✅ | ✅ | ✅  | ✅ |
| **Cursor** | ✅ | ✅ | ✅ | ✅  | ✅ |
| **Continue** | ✅ | ✅ | ✅ | ✅  | ✅ |
| **Kiro** | ✅ | ✅ | ✅ | ✅  | ✅ |
| **Cline** | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Claude Code** | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Windsurf** | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Amazon Q** | ✅ | ✅ | ✅ | ✅ | ✅ |
| **JetBrains AI** | ✅ | ✅ | ✅ | ✅ | ✅ |

## Feature Descriptions

### Variable Substitution
Ability to replace template variables (e.g., `{% raw %}{{{ PROJECT_NAME }}}{% endraw %}`) with actual values during generation.

**Supported by**: All adapters

**Example**:
{% raw %}
```yaml
metadata:
  title: "{{{ PROJECT_NAME }}} Assistant"
variables:
  PROJECT_NAME: "MyProject"
```
{% endraw %}

### Multi-Document Support
Ability to organize content across multiple documents using the `documents` field.

**Supported by**: All adapters

**Example**:
```yaml
schema_version: "3.0.0"
content: |
  # Main guidelines
  - General project rules

documents:
  - name: "testing"
    content: |
      # Testing Standards
      - Use Jest for unit tests
      - Maintain 80% coverage
```

### Bidirectional Sync
Ability to read editor-specific files and create/update PrompTrek configuration from them.

**Supported by**: All adapters

**Command**:
```bash
promptrek sync --editor copilot --output project.promptrek.yaml
promptrek sync --editor claude --output project.promptrek.yaml
promptrek sync --editor cursor --output project.promptrek.yaml
```

### Project Files
Generates project-level configuration files that can be committed to version control.

**Supported by**: All adapters

**Examples**:
- `.github/copilot-instructions.md`
- `.cursor/rules/index.mdc`
- `.clinerules/*.md`

### v3.0 Schema Support
Full support for PrompTrek v3.0 schema with top-level plugin fields.

**Supported by**: All adapters

**Features**:
- Top-level `mcp_servers`, `commands`, `agents`, `hooks` fields
- 100% backward compatible with v2.x nested structure
- Automatic migration for legacy v2.x files
- Production-ready stable schema

**Learn more**: [v3.0 Schema Specification](./upf-specification.html#schema-v30-stable)

## Detailed Adapter Capabilities

### GitHub Copilot

**Files Generated**:
- `.github/copilot-instructions.md` (repository-wide)
- `.github/instructions/*.instructions.md` (path-specific)
- `.github/prompts/*.prompt.md` (agent prompts)
- `.vscode/mcp.json` (MCP server configuration)

**Unique Features**:
- ✅ Path-specific instructions with YAML frontmatter
- ✅ Bidirectional sync (v2 lossless format)
- ✅ Advanced glob pattern matching
- ✅ MCP server integration
- ✅ v3.0 schema with top-level plugins

**Best For**: Large teams using GitHub, multi-component projects

---

### Cursor

**Files Generated**:
- `.cursor/rules/index.mdc` (project overview)
- `.cursor/rules/*.mdc` (category-specific rules)
- `.cursorignore` (indexing control)
- `.cursorindexingignore` (indexing control)
- `AGENTS.md` (agent instructions)
- `.cursor/mcp.json` (MCP server configuration)

**Unique Features**:
- ✅ Modern `.mdc` rules system
- ✅ Always/Auto Attached rule types
- ✅ Technology-specific rule generation
- ✅ Advanced ignore file support
- ✅ Bidirectional sync
- ✅ MCP server, commands, and agents support
- ✅ v3.0 schema with top-level plugins

**Best For**: AI-first development workflows, focused coding sessions

---

### Continue

**Files Generated**:
- `.continue/config.json` (main configuration)
- `.continue/rules/*.md` (rule files)

**Unique Features**:
- ✅ JSON-based configuration
- ✅ Bidirectional sync
- ✅ Advanced rules directory
- ✅ Context provider configuration
- ✅ MCP server and commands support
- ✅ v3.0 schema with top-level plugins

**Best For**: VS Code users, customizable AI workflows

---

### Kiro

**Files Generated**:
- `.kiro/steering/*.md` (steering files)
- `.kiro/specs/*.md` (specification files)
- `.kiro/settings/mcp.json` (MCP server configuration)

**Unique Features**:
- ✅ Comprehensive steering system
- ✅ YAML frontmatter support
- ✅ Separate specs for features
- ✅ Structured guidance approach
- ✅ Bidirectional sync
- ✅ MCP server support
- ✅ v3.0 schema with top-level plugins

**Best For**: Structured development processes, specification-driven projects

---

### Cline

**Files Generated**:
- `.clinerules/*.md` (markdown rules)
- `.vscode/settings.json` (MCP configuration)

**Unique Features**:
- ✅ Simple markdown format
- ✅ VSCode-integrated autonomous agent
- ✅ File creation/editing with user approval
- ✅ Command execution and browser automation
- ✅ Bidirectional sync
- ✅ MCP server support (via VSCode settings)
- ✅ v3.0 schema with top-level plugins

**Best For**: VSCode users wanting autonomous AI assistance, task automation workflows

---

### Claude Code

**Files Generated**:
- `.claude/context.md`
- `.claude/mcp.json` (MCP server configuration)

**Unique Features**:
- ✅ Rich context format
- ✅ Detailed project information
- ✅ Markdown-based guidance
- ✅ Bidirectional sync (v2 lossless format)
- ✅ MCP server support
- ✅ v3.0 schema with top-level plugins

**Best For**: Projects using Claude, comprehensive context needs

---

### Windsurf

**Files Generated**:
- `.windsurf/rules/*.md`
- `~/.codeium/windsurf/mcp_config.json` (system-wide MCP)

**Unique Features**:
- ✅ Markdown rules format
- ✅ Technology-specific rules
- ✅ Modular rule organization
- ✅ Bidirectional sync
- ✅ MCP server support (system-wide)
- ✅ v3.0 schema with top-level plugins

**Best For**: Teams using Windsurf, organized AI assistance

---

### Amazon Q

**Files Generated**:
- `.amazonq/rules/*.md`
- `.amazonq/cli-agents/*.json` (CLI agents)
- `.amazonq/mcp.json` (MCP server configuration)

**Unique Features**:
- ✅ Rules directory support
- ✅ CLI agents for code review, security, testing
- ✅ AWS-integrated workflows
- ✅ Bidirectional sync
- ✅ MCP server support
- ✅ v3.0 schema with top-level plugins

**Best For**: AWS-centric projects, cloud development

---

### JetBrains AI

**Files Generated**:
- `.assistant/rules/*.md`

**Unique Features**:
- ✅ IDE-integrated configuration
- ✅ Markdown rules format
- ✅ Bidirectional sync
- ✅ v3.0 schema with top-level plugins
- ⚠️ MCP/prompts configured via IDE UI

**Best For**: JetBrains IDE users (IntelliJ, PyCharm, etc.)

---

## Migration Guide

### Moving Between Editors

PrompTrek makes it easy to switch between editors while maintaining your prompts:

```bash
# Generate for your new editor
promptrek generate project.promptrek.yaml --editor <new-editor>

# Your existing Universal Prompt File works with all editors
```

### Using Multiple Editors

Generate for all configured editors at once:

```bash
promptrek generate project.promptrek.yaml --all
```

### Upgrading to v3.0 Schema

All adapters support the v3.0 schema with top-level plugin fields:

```bash
# Migrate v2.x to v3.0
promptrek migrate project.promptrek.yaml -o project-v3.promptrek.yaml

# V2.x files still work with automatic migration
promptrek generate project-v2.promptrek.yaml --all
```

## Related Documentation

- [UPF Specification](./upf-specification.html) - Schema documentation
- [Advanced Features](./advanced-features.html) - Variables and multi-document support
- [Sync Feature](./sync.html) - Bidirectional sync guide
- [Getting Started](../quick-start.html) - Quick start guide
