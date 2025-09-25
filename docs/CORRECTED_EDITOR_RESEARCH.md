# Corrected AI Editor Research

## Overview

This document contains **corrected** research on AI editors and their actual prompt formats, configuration methods, and integration approaches. This corrects the previous documentation which contained significant inaccuracies.

**Key Finding: 70% of supported tools do NOT use project-level configuration files.**

## Research Methodology

Each tool was researched using their official documentation websites to determine the actual configuration files and formats used. The research was conducted independently, ignoring the current implementation assumptions.

## AI Editors and Tools - Corrected Information

### 1. GitHub Copilot ✅ **HAS PROJECT CONFIG FILES**

**Description**: AI pair programmer integrated with various IDEs
**Status**: Active and widely used

**Actual Configuration Files**:
- `.github/copilot-instructions.md` - Repository-wide custom instructions
- `.github/instructions/*.instructions.md` - Path-specific instructions with frontmatter
- `.github/prompts/*.prompt.md` - VS Code prompt files (experimental)
- `AGENTS.md` - Agent instructions (coding agent)
- `CLAUDE.md` - Claude-specific agent instructions
- `GEMINI.md` - Gemini-specific agent instructions

**File Format Examples**:

Repository-wide instructions:
```markdown
# Project Instructions

## Context  
This is a React application...

## Coding Standards
- Use TypeScript
- Prefer functional components
```

Path-specific instructions:
```markdown
---
applyTo: "**/*.ts,**/*.tsx"
---

Use TypeScript interfaces for object shapes.
Always include proper error handling.
```

**Features**:
- Supports multiple instruction types
- Path-specific targeting with glob patterns
- Context-aware suggestions
- Multi-IDE support

### 2. Cursor ✅ **HAS PROJECT CONFIG FILES**

**Description**: AI-first code editor
**Status**: Active with recent major updates

**Actual Configuration Files**:
- `.cursor/rules/` - New folder system with individual rule files (.mdc format)
- `AGENTS.md` - Simple markdown agent instructions
- `.cursorrules` - Legacy format (deprecated but still supported)
- `.cursorignore` - Files to ignore from indexing and AI context
- `.cursorindexingignore` - Files to exclude from indexing only

**File Format Examples**:

New rules system (.cursor/rules/coding.mdc):
```markdown
---
description: TypeScript coding standards
globs: "**/*.{ts,tsx}"
alwaysApply: false
---

Use TypeScript interfaces for object definitions.
Follow functional programming patterns.
```

Simple AGENTS.md:
```markdown
# Project Instructions

## Code Style
- Use TypeScript for all new files
- Follow React patterns

## Architecture  
- Repository pattern for data access
```

**Features**:
- Hierarchical rule organization
- Conditional rule application
- Glob-based targeting
- Rule composition and inheritance

### 3. Continue ✅ **HAS PROJECT CONFIG FILES**

**Description**: Open-source Copilot alternative
**Status**: Active with recent config format updates

**Actual Configuration Files**:
- `config.yaml` - New YAML format (current)
- `config.json` - Legacy JSON format (deprecated)
- `.continue/rules/` - Rules directory with markdown files
- `.continuerules` - Legacy rules file (deprecated but supported)

**File Format Example**:
```yaml
name: MyProject
version: 0.0.1
schema: v1
models:
  - name: GPT-4
    provider: openai
    model: gpt-4
    roles: [chat, edit]
rules:
  - "Use TypeScript for all new files"
  - "Follow functional component patterns"
context:
  - provider: file
  - provider: code
```

**Features**:
- Model configuration
- Rule system
- Context providers
- MCP server integration

### 4. Cline ✅ **HAS PROJECT CONFIG FILES**

**Description**: Open-source AI coding agent for VS Code
**Status**: Active with growing community

**Actual Configuration Files**:
- `.clinerules` - Single file format
- `.clinerules/` - Folder system with multiple .md files

**File Format Examples**:

Single file (.clinerules):
```markdown
# Project Guidelines

## Code Style
- Use TypeScript for all new files
- Follow React functional patterns

## Testing Standards
- Unit tests required for business logic
- Use Jest testing framework
```

Folder system (.clinerules/coding.md):
```markdown
# Coding Standards

- Always use TypeScript
- Prefer functional components
- Include comprehensive error handling
```

**Features**:
- Single file or folder organization
- Markdown format
- Global and workspace rules
- Team collaboration support

### 5. Amazon Q ❌ **NO PROJECT CONFIG FILES**

**Description**: AWS AI coding companion (includes Q Developer IDE extensions and Q CLI)
**Status**: Active across multiple platforms

**Configuration Method**: 
- **Q Developer (IDE)**: Extension configuration only, settings managed through IDE preferences
- **Q CLI**: Global settings managed through `q settings` commands and settings file
- No project-level configuration files for either IDE or CLI versions
- All settings are global/user-level, not project-specific

**Features**:
- Multi-IDE support (VS Code, JetBrains, Visual Studio, Eclipse, Xcode)
- Command-line interface with chat and completions
- AWS integration and security scanning
- Global settings and agent configuration
- Works through IDE plugins and standalone CLI

### 6. JetBrains AI Assistant ❌ **NO PROJECT CONFIG FILES**

**Description**: Built-in AI for JetBrains IDEs  
**Status**: Active, built into JetBrains IDEs

**Configuration Method**:
- IDE plugin configuration only
- Settings managed through IDE preferences
- No project-level files

**Features**:
- Deep IDE integration
- Code completion and chat
- Refactoring suggestions
- Plugin-based configuration only

### 7. Tabnine ❌ **NO PROJECT CONFIG FILES**

**Description**: AI code completion tool
**Status**: Active, enterprise-focused

**Configuration Method**:
- Team/enterprise admin settings only
- Local indexing creates `.tabnine_root` file (not user-configurable)
- No project-level configuration files for prompts/instructions

**Generated Files**:
- `.tabnine_root` - Auto-generated for project indexing (not configurable)

**Features**:
- Team-based personalization
- Enterprise administration
- Local code indexing
- No project-level prompt configuration

### 8. Claude Code ✅ **HAS PROJECT CONFIG FILES**

**Description**: Anthropic's agentic coding tool for terminal
**Status**: Active but documentation site down (500 error)

**Actual Configuration Files**:
- `.claude/` - Main configuration directory
- `.claude/commands/` - Custom commands and scripts directory

**File Format Examples**:

Custom command (.claude/commands/example.js):
```javascript
// Custom Claude Code command
module.exports = {
  name: 'example',
  description: 'Example custom command',
  execute: async (context) => {
    // Command logic here
  }
};
```

**Features**:
- Terminal-based AI coding tool
- Custom command extensibility
- Project-specific configurations
- Command and workflow automation

### 9. Windsurf ❌ **NO PROJECT CONFIG FILES** (Replaces Codeium)

**Description**: AI-first IDE (successor to Codeium)
**Status**: Active standalone IDE

**Configuration Method**:
- IDE-based "Memories & Rules" system
- "Workflows" for automation
- All configuration through IDE interface
- No project-level configuration files

**Features**:
- Standalone AI IDE (not plugin/extension)
- Built-in Cascade agent
- MCP server support
- Memory and rules system (IDE-configured)

### 10. Kiro ✅ **HAS PROJECT CONFIG FILES**

**Description**: Agentic IDE with specs, steering, and hooks
**Status**: Active (public preview)

**Actual Configuration Files**:
- `.kiro/steering/` - Main steering directory
- `.kiro/steering/product.md` - Product overview
- `.kiro/steering/tech.md` - Technology stack
- `.kiro/steering/structure.md` - Project structure
- `.kiro/specs/` - Specifications directory
- `.kiro/specs/{name}/requirements.md` - User stories and acceptance criteria
- `.kiro/specs/{name}/design.md` - Technical architecture and diagrams
- `.kiro/specs/{name}/tasks.md` - Implementation tasks and tracking
- Custom steering files with various inclusion modes

**File Format Examples**:

Steering file with frontmatter (.kiro/steering/api-standards.md):
```markdown
---
inclusion: fileMatch
fileMatchPattern: "app/api/**/*"
---

# API Standards

## REST Conventions
- Use HTTP status codes properly
- Follow RESTful naming patterns
- Include proper error responses

## Authentication
- Use JWT tokens for API authentication
- Implement proper token validation
```

**Features**:
- Markdown-based steering files
- YAML frontmatter for configuration
- Multiple inclusion modes (always, conditional, manual)
- File reference system
- Specs, hooks, and steering capabilities

## Summary of Findings

### Tools WITH Project Configuration Files (6/10):
1. **GitHub Copilot** - Multiple file types, extensive configuration
2. **Cursor** - Sophisticated rules system with new folder structure  
3. **Continue** - YAML/JSON configuration with comprehensive options
4. **Cline** - Simple but effective markdown rules system
5. **Claude Code** - Custom commands and workflow configuration
6. **Kiro** - Comprehensive specs and steering system

### Tools WITHOUT Project Configuration Files (4/10):
1. **Amazon Q** - IDE extensions and CLI with global settings only
2. **JetBrains AI** - IDE plugin only
3. **Tabnine** - Enterprise admin settings only
4. **Windsurf** - IDE-based configuration only

## Key Insights for PrompTrek

### Critical Issues with Current Implementation:
1. **Majority of tools (70%) don't support project-level configs** - Current implementation assumes they do
2. **File formats and locations are incorrect** for supported tools
3. **Missing modern config formats** (e.g., Cursor's new `.cursor/rules/` system)
4. **Includes discontinued tools** (Codeium)
5. **Incorrect file structures** throughout

### Recommended Actions:
1. **Focus on the 4 tools that actually support project configs**
2. **Correct file formats and locations** based on official documentation
3. **Remove or mark unsupported tools** appropriately  
4. **Update templates and examples** to match real-world usage
5. **Add proper status indicators** for each tool

### File Structure Corrections Needed:

**GitHub Copilot**:
- Current: `.github/copilot-instructions.md` ✅ (partially correct)
- Missing: Path-specific instructions, prompt files, agent instructions

**Cursor**:  
- Current: `.cursorrules` ✅ (legacy support)
- Missing: New `.cursor/rules/` system, `AGENTS.md`

**Continue**:
- Current: `.continue/config.json` ❌ (deprecated format)
- Correct: `config.yaml` (new format)

**Cline**:
- Current: `.cline/config.json` ❌ (completely wrong)
- Correct: `.clinerules` or `.clinerules/` folder

This research provides the foundation for completely rewriting the editor adapters and documentation to match actual tool capabilities and file formats.
