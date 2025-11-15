# Glossary

Definitions of terms and concepts used in PrompTrek.

## A

### Adapter
An editor-specific component in PrompTrek that converts the Universal Prompt Format to an editor's native configuration format.

**Example:** The Cursor adapter converts `.promptrek.yaml` to `.cursor/rules/index.mdc`.

**See also:** [Editor Adapter](#editor-adapter)

### Agent
An autonomous AI assistant with specific tools, permissions, and instructions for automated tasks.

**Example:**
```yaml
agents:
  - name: test-generator
    prompt: "Generate comprehensive tests"
    tools: [file_read, file_write]
```

**Supported in:** Claude Code, Cursor

### Application Version
The version number of the PrompTrek tool itself (e.g., v0.5.0), distinct from schema version.

**Check with:** `promptrek --version`

**See also:** [Schema Version](#schema-version)

### Auto-Promotion
Automatic conversion of deprecated schema features to current format during parsing, maintaining backward compatibility.

**Example:** Nested `plugins.mcp_servers` automatically promoted to top-level `mcp_servers`.

## B

### Backward Compatibility
Support for older schema versions in newer PrompTrek releases, allowing gradual migration.

**Example:** Schema v2.1 files work in PrompTrek v0.5.0 with deprecation warnings.

### Barrel Export
An `index.ts` file that re-exports symbols from multiple files, simplifying imports.

**Example:**
```typescript
// index.ts
export * from './Button';
export * from './Input';
```

**Common in:** NX monorepos, shared libraries

### Bidirectional Sync
PrompTrek's ability to both generate editor files from `.promptrek.yaml` and import editor files back to `.promptrek.yaml`.

**Commands:**
- Generate: `promptrek generate config.yaml --editor cursor`
- Sync back: `promptrek sync --editor cursor -o config.yaml`

## C

### Command
A custom slash command that can be invoked in AI editors to execute predefined prompts.

**Example:**
```yaml
commands:
  - name: review-code
    description: "Review code quality"
    prompt: "Review this code for..."
```

**Usage:** `/review-code` in editor

**See also:** [Slash Command](#slash-command)

### Configuration Schema
The YAML structure and rules that define a valid PrompTrek configuration file.

**Validated with:** `promptrek validate config.yaml`

**See also:** [Schema Version](#schema-version), [UPF](#upf-universal-prompt-format)

### Content Field
The main section of a PrompTrek configuration containing guidelines and instructions for AI assistants.

**Example:**
```yaml
content: |
  # Project Guidelines
  - Write clean code
  - Add tests
```

**Supports:** Markdown, code blocks, variable substitution

## D

### Deprecation Warning
A notice that a feature will be removed in a future version, encouraging migration to newer alternatives.

**Example:** "Using deprecated plugins.mcp_servers structure"

**See also:** [Deprecation Guide](deprecation.md)

### Document
A path-specific or context-specific section of guidelines in a PrompTrek configuration.

**Example:**
```yaml
documents:
  - name: typescript
    content: "TypeScript guidelines..."
    file_globs: "**/*.ts"
    always_apply: false
```

**Use for:** Different rules for different file types or directories

### Dynamic Variable
A variable whose value is computed at generation time rather than statically defined.

**Built-in examples:**
- `CURRENT_DATE`
- `GIT_BRANCH`
- `PROJECT_NAME`

**User-defined:** Command-based variables in `.promptrek/variables.promptrek.yaml`

## E

### Editor Adapter
A PrompTrek component that transforms universal configuration to editor-specific formats.

**Available adapters:**
- GitHub Copilot
- Cursor
- Continue
- Cline
- Claude Code
- Kiro
- Windsurf
- Amazon Q
- JetBrains AI

**See also:** [Adapter](#adapter)

### Environment Variable
A system variable used to store configuration values, secrets, or settings outside of version control.

**Example:**
```yaml
env:
  GITHUB_TOKEN: "{{{ GITHUB_TOKEN }}}"
```

**Set with:** `export GITHUB_TOKEN=value` or `-V` flag

## F

### File Globs
Pattern matching syntax for selecting files based on their paths.

**Examples:**
- `**/*.ts` - All TypeScript files
- `src/components/**/*.tsx` - TSX files in components
- `**/*.{test,spec}.ts` - Test files

**Used in:** Documents, path-specific rules

## G

### Generated File
An editor-specific configuration file created by PrompTrek from a `.promptrek.yaml` source.

**Examples:**
- `.github/copilot-instructions.md`
- `.cursor/rules/index.mdc`
- `.claude/CLAUDE.md`

**Should not be committed:** Added to `.gitignore` automatically

## H

### Hook
An event-driven automation that runs at specific points in the development workflow.

**Types:**
- Pre-commit
- Pre-push
- Post-merge

**Example:**
```yaml
hooks:
  - name: validate-types
    event: pre-commit
    command: "tsc --noEmit"
```

## I

### Interactive CLI
PrompTrek's guided command-line interface with menus and prompts for common workflows.

**Launch:** `promptrek` (no arguments)

**Features:** Project initialization, editor configuration, plugin management, validation

## M

### MCP (Model Context Protocol)
A standardized protocol for connecting AI assistants to external tools and data sources.

**Official servers:**
- Filesystem
- GitHub
- PostgreSQL
- Slack

**Configuration:**
```yaml
mcp_servers:
  - name: github
    command: npx
    args: ["-y", "@modelcontextprotocol/server-github"]
```

**Learn more:** [MCP Server Example](../examples/plugins/mcp-servers.md)

### Metadata
Descriptive information about a PrompTrek configuration, including title, description, version, and tags.

**Example:**
```yaml
metadata:
  title: "My Project"
  description: "AI assistant configuration"
  version: "1.0.0"
  tags: [react, typescript]
```

### Migration
The process of updating configuration files from an older schema version to a newer one.

**Command:** `promptrek migrate config.yaml -o new-config.yaml`

**See also:** [V3 Migration Guide](../V3_MIGRATION_GUIDE.md)

### Monorepo
A repository containing multiple projects or packages, often using tools like NX or Turborepo.

**Example structure:**
```
apps/
  web/
  api/
libs/
  shared-ui/
  shared-utils/
```

**See also:** [NX Monorepo Example](../examples/advanced/monorepo.md)

## P

### Plugin
An extension to PrompTrek's core functionality, including MCP servers, commands, agents, and hooks.

**Categories:**
- MCP Servers
- Custom Commands
- Autonomous Agents
- Event Hooks

### Pre-commit Hook
A script that runs automatically before each git commit to validate changes.

**Install:** `promptrek install-hooks --activate`

**Prevents:** Committing generated files, invalid configurations

### Preview Mode
Generating output without writing files, useful for testing configurations.

**Command:** `promptrek preview config.yaml --editor cursor`

### Prompt
Instructions provided to an AI assistant to guide its behavior and responses.

**In PrompTrek:** Defined in `content`, `commands.prompt`, or `agents.prompt` fields

## S

### Schema Version
The version of the configuration file format, independent of the application version.

**Current versions:**
- v3.1.0 (latest)
- v3.0.0 (stable)
- v2.1.0 (deprecated)

**Specified in:**
```yaml
schema_version: "3.1.0"
```

### Slash Command
A command invoked with `/command-name` syntax in AI editors.

**Example:** `/review-pr`, `/generate-tests`

**See also:** [Command](#command), [Custom Commands Example](../examples/plugins/custom-commands.md)

### Sync
The process of converting editor-specific files back to PrompTrek format.

**Command:** `promptrek sync --editor cursor -o config.yaml`

**See also:** [Bidirectional Sync](#bidirectional-sync)

## T

### Trust Level
A security classification for MCP servers and other plugins.

**Levels:**
- `full` - Complete trust, no approval needed
- `partial` - Limited trust, approval for sensitive operations
- `untrusted` - No trust, always require approval

**Example:**
```yaml
trust_metadata:
  trusted: true
  trust_level: partial
  requires_approval: true
```

### Trust Metadata
Security information associated with plugins, including trust level and approval requirements.

**Fields:**
- `trusted`: Boolean
- `trust_level`: full/partial/untrusted
- `requires_approval`: Boolean
- `source`: official/community/local
- `verified_by`: Optional
- `verified_date`: Optional

## U

### Universal Prompt Format (UPF)
PrompTrek's standardized YAML format for defining AI assistant configurations.

**Key sections:**
- `schema_version`
- `metadata`
- `content`
- `variables`
- `documents` (optional)
- Plugin sections (optional)

**File extension:** `.promptrek.yaml`

## V

### Variable
A named value that can be substituted into configuration content.

**Definition:**
```yaml
variables:
  PROJECT_NAME: "my-app"
  API_URL: "https://api.example.com"
```

**Usage:**
```yaml
content: |
  Project: {{{ PROJECT_NAME }}}
  API: {{{ API_URL }}}
```

**Override:** `-V PROJECT_NAME=custom-app`

**See also:** [Dynamic Variable](#dynamic-variable)

### Variable Substitution
The process of replacing `{{{ VARIABLE }}}` placeholders with actual values during generation.

**Syntax:** Triple braces `{{{ VAR }}}`

**When:** During file generation

## W

### Workspace
In monorepo context, the root directory containing multiple projects.

**Structure:**
```
workspace/
  apps/
  libs/
  tools/
  nx.json
  package.json
```

## Y

### YAML (YAML Ain't Markup Language)
A human-readable data serialization format used for PrompTrek configurations.

**Key syntax:**
- Key-value pairs: `key: value`
- Lists: `- item`
- Multi-line strings: `|` or `>`
- Indentation: 2 spaces (not tabs)

**Resources:** [YAML.org](https://yaml.org/)

---

## Acronyms & Abbreviations

| Acronym | Full Form | Description |
|---------|-----------|-------------|
| API | Application Programming Interface | Programming interface for services |
| CLI | Command-Line Interface | Text-based user interface |
| CI/CD | Continuous Integration/Continuous Deployment | Automated build and deployment |
|DTO | Data Transfer Object | Object for transferring data between layers |
| MCP | Model Context Protocol | Protocol for AI tool integration |
| NX | Nx Build System | Monorepo build system |
| ORM | Object-Relational Mapping | Database abstraction layer |
| PR | Pull Request | Code review request in version control |
| REST | Representational State Transfer | API architectural style |
| UPF | Universal Prompt Format | PrompTrek's configuration format |
| VSCode | Visual Studio Code | Microsoft's code editor |
| YAML | YAML Ain't Markup Language | Data serialization format |

---

## Quick Reference

### File Locations by Editor

| Editor | Configuration Files |
|--------|-------------------|
| Copilot | `.github/copilot-instructions.md`<br>`.github/instructions/*.instructions.md` |
| Cursor | `.cursor/rules/index.mdc`<br>`.cursor/rules/*.mdc`<br>`AGENTS.md` |
| Claude Code | `.claude/CLAUDE.md`<br>`.mcp.json`<br>`.claude/agents/*.md`<br>`.claude/commands/*.md` |
| Continue | `.continue/config.json`<br>`.continue/rules/*.md` |
| Cline | `.clinerules/*.md`<br>`.vscode/settings.json` |
| Kiro | `.kiro/steering/*.md`<br>`.kiro/settings/mcp.json` |
| Windsurf | `.windsurf/rules/*.md`<br>`~/.codeium/windsurf/mcp_config.json` |
| Amazon Q | `.amazonq/rules/*.md`<br>`.amazonq/cli-agents/*.json` |

### Common Commands

| Command | Purpose |
|---------|---------|
| `promptrek init` | Create new configuration |
| `promptrek validate` | Check configuration validity |
| `promptrek generate` | Create editor files |
| `promptrek preview` | Preview without generating |
| `promptrek sync` | Import from editor files |
| `promptrek migrate` | Update schema version |
| `promptrek plugins generate` | Generate plugin files |
| `promptrek list-editors` | Show supported editors |

---

**See Also:**
- [FAQ](faq.md) - Frequently asked questions
- [User Guide](../user-guide/index.md) - Complete documentation
- [Examples](../examples/index.md) - Real-world configurations
