# Adapter Capabilities Matrix

This document provides a comprehensive comparison of features supported by each PrompTrek adapter.

## Quick Reference Table

| Editor | Variable Substitution | Conditional Instructions | Bidirectional Sync | Headless Mode | Project Files | Global Config | IDE Plugin |
|--------|:--------------------:|:-----------------------:|:------------------:|:-------------:|:-------------:|:-------------:|:----------:|
| **GitHub Copilot** | ✅ | ✅ | ✅ | ✅ | ✅ | - | - |
| **Cursor** | ✅ | ✅ | - | - | ✅ | - | - |
| **Continue** | ✅ | ✅ | ✅ | - | ✅ | - | - |
| **Kiro** | ✅ | ✅ | - | - | ✅ | - | - |
| **Cline** | ✅ | ✅ | - | - | ✅ | - | - |
| **Claude Code** | ✅ | ✅ | - | - | ✅ | - | - |
| **Windsurf** | ✅ | ✅ | - | - | ✅ | - | - |
| **Tabnine** | ✅ | ✅ | - | - | - | ✅ | - |
| **Amazon Q** | ✅ | ✅ | - | - | ✅ | - | - |
| **JetBrains AI** | ✅ | ✅ | - | - | ✅ | - | - |

## Feature Descriptions

### Variable Substitution
Ability to replace template variables (e.g., `{{{ PROJECT_NAME }}}`) with actual values during generation.

**Supported by**: All adapters

**Example**:
```yaml
metadata:
  title: "{{{ PROJECT_NAME }}} Assistant"
variables:
  PROJECT_NAME: "MyProject"
```

### Conditional Instructions
Ability to provide editor-specific instructions using conditional logic.

**Supported by**: All adapters

**Example**:
```yaml
conditions:
  - if: "EDITOR == \"copilot\""
    then:
      instructions:
        general:
          - "Copilot-specific instruction"
```

### Bidirectional Sync
Ability to read editor-specific files and create/update PrompTrek configuration from them.

**Supported by**: GitHub Copilot, Continue

**Command**:
```bash
promptrek sync --editor copilot --output project.promptrek.yaml
```

### Headless Mode
Support for generating agent-specific instructions for headless/autonomous AI assistants.

**Supported by**: GitHub Copilot

**Command**:
```bash
promptrek generate project.promptrek.yaml --editor copilot --headless
```

### Project Files
Generates project-level configuration files that can be committed to version control.

**Supported by**: Most adapters except Tabnine

**Examples**:
- `.github/copilot-instructions.md`
- `.cursor/rules/index.mdc`
- `.clinerules`

### Global Config Only
Editor configuration is managed globally, not per-project.

**Supported by**: Tabnine

**Note**: PrompTrek can still generate configuration guidance, but setup is done through the editor's global settings.

## Detailed Adapter Capabilities

### GitHub Copilot

**Files Generated**:
- `.github/copilot-instructions.md` (repository-wide)
- `.github/instructions/*.instructions.md` (path-specific)
- `.github/prompts/*.prompt.md` (agent prompts)

**Unique Features**:
- ✅ Path-specific instructions with YAML frontmatter
- ✅ Headless agent file generation
- ✅ Bidirectional sync
- ✅ Advanced glob pattern matching

**Best For**: Large teams using GitHub, multi-component projects

---

### Cursor

**Files Generated**:
- `.cursor/rules/index.mdc` (project overview)
- `.cursor/rules/*.mdc` (category-specific rules)
- `.cursorignore` (indexing control)
- `AGENTS.md` (agent instructions)

**Unique Features**:
- ✅ Modern `.mdc` rules system
- ✅ Always/Auto Attached rule types
- ✅ Technology-specific rule generation
- ✅ Advanced ignore file support

**Best For**: AI-first development workflows, focused coding sessions

---

### Continue

**Files Generated**:
- `config.yaml` (main configuration)
- `.continue/rules/*.md` (rule files)

**Unique Features**:
- ✅ YAML-based configuration
- ✅ Bidirectional sync
- ✅ Advanced rules directory
- ✅ Context provider configuration

**Best For**: VS Code users, customizable AI workflows

---

### Kiro

**Files Generated**:
- `.kiro/steering/*.md` (steering files)
- `.kiro/specs/*.md` (specification files)

**Unique Features**:
- ✅ Comprehensive steering system
- ✅ YAML frontmatter support
- ✅ Separate specs for features
- ✅ Structured guidance approach

**Best For**: Structured development processes, specification-driven projects

---

### Cline

**Files Generated**:
- `.clinerules` (markdown rules)

**Unique Features**:
- ✅ Simple markdown format
- ✅ Terminal-based AI assistance
- ✅ Straightforward configuration

**Best For**: Terminal-focused developers, simple setups

---

### Claude Code

**Files Generated**:
- `.claude/context.md`

**Unique Features**:
- ✅ Rich context format
- ✅ Detailed project information
- ✅ Markdown-based guidance

**Best For**: Projects using Claude, comprehensive context needs

---

### Windsurf

**Files Generated**:
- `.windsurf/rules/*.md`

**Unique Features**:
- ✅ Markdown rules format
- ✅ Technology-specific rules
- ✅ Modular rule organization

**Best For**: Teams using Windsurf, organized AI assistance

---

### Tabnine

**Files Generated**:
- None (global configuration only)

**Configuration Method**:
- Team configuration via admin panel
- Global settings per-user

**Best For**: Organizations with centralized configuration

---

### Amazon Q

**Files Generated**:
- `.amazonq/context.md`
- `.amazonq/comments.template`

**Unique Features**:
- ✅ Comment-based prompts
- ✅ AWS-integrated workflows

**Best For**: AWS-centric projects, cloud development

---

### JetBrains AI

**Files Generated**:
- `.idea/ai-assistant.xml`
- `.jetbrains/config.json`

**Unique Features**:
- ✅ IDE-integrated configuration
- ✅ XML and JSON formats

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

## Capability Planning

### Future Enhancements (v0.1.0+)

Planned capability improvements:

- **More Bidirectional Sync**: Extend sync support to Cursor, Kiro, and others
- **Enhanced Headless Mode**: Add headless support for more editors
- **Plugin System**: Allow custom adapters with configurable capabilities
- **Capability Discovery**: Runtime capability detection for installed editors

## Related Documentation

- [Editor Adapters Guide](./ADAPTERS.md) - Detailed adapter documentation
- [Advanced Features](./ADVANCED_FEATURES.md) - Variables and conditionals
- [Sync Feature](./SYNC_FEATURE.md) - Bidirectional sync guide
- [Getting Started](../GETTING_STARTED.md) - Quick start guide
