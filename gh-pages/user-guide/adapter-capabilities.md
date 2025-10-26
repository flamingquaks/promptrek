---
layout: guide
title: Adapter Capabilities
---

# Adapter Capabilities Matrix

This document provides a comprehensive comparison of features supported by each PrompTrek adapter.

## Quick Reference Table

| Editor | Variable Substitution | Multi-Document Support | Sync Support | Project Files | v3.0 Schema |
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
schema_version: "3.1.0"
content: |
  # Main guidelines
  - General project rules

documents:
  - name: "typescript"
    content: |
      # TypeScript Guidelines
      - Use strict TypeScript settings
      - Prefer interfaces over types
    description: "TypeScript coding guidelines"
    file_globs: "**/*.{ts,tsx}"
    always_apply: false

  - name: "testing"
    content: |
      # Testing Standards
      - Use Jest for unit tests
      - Maintain 80% coverage
    # Metadata fields optional - smart defaults used
```

### Sync Support
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
- ✅ Path-specific instructions with YAML frontmatter (applyTo field)
- ✅ Round-trip sync (v2 lossless format)
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
- ✅ Modern `.mdc` rules system with metadata (description, file_globs, always_apply)
- ✅ Always/Auto Attached rule types via metadata
- ✅ Technology-specific rule generation with smart defaults
- ✅ Advanced ignore file support
- ✅ Round-trip sync
- ✅ MCP server, commands, and agents support
- ✅ v3.0 schema with top-level plugins

**Best For**: AI-first development workflows, focused coding sessions

---

### Continue

**Files Generated**:
- `.continue/config.yaml` (main configuration with metadata)
- `.continue/mcpServers/*.yaml` (individual MCP server configurations)
- `.continue/prompts/*.md` (individual slash command prompts)
- `.continue/rules/*.md` (rule files with frontmatter)

**Unique Features**:
- ✅ Modular file structure (one file per server/command)
- ✅ YAML-based configuration following Continue's recommendations
- ✅ Individual MCP server files with Continue metadata format
- ✅ Individual prompt markdown files with frontmatter
- ✅ Round-trip sync
- ✅ Advanced rules directory
- ✅ v3.0 schema with top-level plugins

**Best For**: VS Code users, customizable AI workflows, modular configuration management

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
- ✅ Round-trip sync
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
- ✅ Round-trip sync
- ✅ MCP server support (via VSCode settings)
- ✅ v3.0 schema with top-level plugins

**Best For**: VSCode users wanting autonomous AI assistance, task automation workflows

---

### Claude Code

**Files Generated**:
- `.claude/CLAUDE.md` - Main project context and guidelines
- `.mcp.json` - MCP server configurations (project root)
- `.claude/commands/*.md` - Custom slash commands
- `.claude/agents/*.md` - Autonomous agents
- `.claude/settings.local.json` - Event hooks with tool matchers (Claude Code native format)
- `.claude/hooks.yaml` - Event hooks without matchers (PrompTrek format)

**Unique Features**:
- ✅ Rich markdown context format
- ✅ Full plugin ecosystem support (MCP, commands, agents, hooks)
- ✅ Round-trip sync (v2/v3 lossless format)
- ✅ Dual hooks format (native + PrompTrek)
- ✅ v3.0 schema with top-level plugins
- ✅ Autonomous agent support with trust levels
- ✅ Custom slash command support

**Best For**: Projects using Claude Code, comprehensive context needs, teams requiring full plugin ecosystem (MCP servers, custom commands, autonomous agents, event hooks)

---

### Windsurf

**Files Generated**:
- `.windsurf/rules/*.md`
- `~/.codeium/windsurf/mcp_config.json` (system-wide MCP)

**Unique Features**:
- ✅ Markdown rules format
- ✅ Technology-specific rules
- ✅ Modular rule organization
- ✅ Round-trip sync
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
- ✅ Round-trip sync
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
- ✅ Round-trip sync
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
- [Sync Feature](./sync.html) - Import Round-trip sync guide sync guide
- [Getting Started](../quick-start.html) - Quick start guide
