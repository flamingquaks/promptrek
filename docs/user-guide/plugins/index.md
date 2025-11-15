# Plugin Ecosystem

PrompTrek supports a comprehensive plugin ecosystem (introduced in schema v2.1, enhanced in v3.0+) that extends AI editor capabilities with external integrations, custom commands, autonomous agents, and event-driven workflows.

## Plugin Types

PrompTrek supports four types of plugins:

1. **MCP Servers** - Model Context Protocol integrations for external services
2. **Custom Commands** - Slash commands for common tasks
3. **Autonomous Agents** - AI agents with specific tools and permissions
4. **Event Hooks** - Automated workflows triggered by events

## Schema Version Notes

!!! info "Schema Version"
    - **v2.1.0**: Plugins nested under `plugins:` field
    - **v3.0.0+**: Plugins are top-level fields (recommended)
    - All examples below use schema v3.1.0 (latest)

## MCP Servers

Model Context Protocol (MCP) servers provide external integrations that extend AI editor capabilities with access to filesystems, APIs, databases, and more.

### Configuration

```yaml
schema_version: "3.1.0"
metadata:
  title: "Project with MCP Servers"
  description: "AI assistant with external integrations"

content: |
  # Project Guidelines
  Use MCP servers for external integrations.

variables:
  GITHUB_TOKEN: "ghp_your_token_here"
  GITHUB_OWNER: "myorg"

# Top-level in v3.0+
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
      GITHUB_OWNER: "{{{ GITHUB_OWNER }}}"
    description: "GitHub integration"
    trust_metadata:
      trusted: true
      trust_level: full
      source: official
```

### MCP Server Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | string | ✅ Yes | Server identifier |
| `command` | string | ✅ Yes | Command to start the server |
| `args` | list[string] | ⚠️ Optional | Command line arguments |
| `env` | dict | ⚠️ Optional | Environment variables |
| `description` | string | ⚠️ Optional | Human-readable description |
| `trust_metadata` | object | ⚠️ Optional | Trust and security metadata |

### Common MCP Servers

**Filesystem Access**:
```yaml
mcp_servers:
  - name: filesystem
    command: npx
    args: ["-y", "@modelcontextprotocol/server-filesystem", "/workspace"]
    description: "Safe filesystem access"
    trust_metadata:
      trust_level: partial
      source: official
```

**GitHub Integration**:
```yaml
mcp_servers:
  - name: github
    command: npx
    args: ["-y", "@modelcontextprotocol/server-github"]
    env:
      GITHUB_TOKEN: "{{{ GITHUB_TOKEN }}}"
    description: "GitHub API access"
```

**PostgreSQL Database**:
```yaml
mcp_servers:
  - name: postgres
    command: npx
    args: ["-y", "@modelcontextprotocol/server-postgres"]
    env:
      POSTGRES_CONNECTION_STRING: "{{{ DB_CONNECTION }}}"
    description: "Database access"
    trust_metadata:
      trust_level: full
      requires_approval: true
```

### Editor Support

MCP servers are supported by:

- ✅ **Claude Code** - `.mcp.json` in project root
- ✅ **Continue** - `.continue/mcpServers/*.yaml`
- ✅ **Cursor** - `.cursor/mcp.json`
- ✅ **GitHub Copilot** - `.vscode/mcp.json`
- ✅ **Cline** - `.vscode/settings.json`
- ✅ **Amazon Q** - `.amazonq/mcp.json`
- ✅ **Kiro** - `.kiro/settings/mcp.json`
- ✅ **Windsurf** - System-wide config
- ⚠️ **JetBrains AI** - Configured via IDE UI

---

## Custom Commands

Custom commands (slash commands) are reusable prompts that can be triggered with a simple command in AI editors.

### Configuration

```yaml
schema_version: "3.1.0"
metadata:
  title: "Project with Custom Commands"
  description: "AI assistant with slash commands"

content: |
  # Project Guidelines
  Use custom commands for common tasks.

# Top-level in v3.0+
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

### Command Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | string | ✅ Yes | Command identifier (without slash) |
| `description` | string | ✅ Yes | Human-readable description |
| `prompt` | string | ✅ Yes | Command prompt template |
| `output_format` | string | ⚠️ Optional | Expected output format |
| `requires_approval` | boolean | ⚠️ Optional | Whether to require approval |
| `system_message` | string | ⚠️ Optional | System-level instructions |
| `examples` | list[string] | ⚠️ Optional | Usage examples |
| `trust_metadata` | object | ⚠️ Optional | Trust metadata |

### Workflow Commands (v3.1.0+)

Schema v3.1.0 adds workflow support for multi-step commands:

```yaml
commands:
  - name: pr-review
    multi_step: true  # Marks this as a workflow
    description: "Complete pull request review workflow"
    prompt: |
      Review the pull request:
      1. Fetch PR details using `gh pr view`
      2. Review changed files
      3. Run tests
      4. Provide feedback
    tool_calls: [gh, read_file, execute_command]
    requires_approval: true
```

### Editor Support

Custom commands are supported by:

- ✅ **Claude Code** - `.claude/commands/*.md`
- ✅ **Continue** - `.continue/prompts/*.md`
- ✅ **Cursor** - Agent functions
- ✅ **Cline** - Workflow prompts
- ✅ **Amazon Q** - `.amazonq/prompts/*.md`
- ⚠️ **Others** - Via general context

---

## Autonomous Agents

Autonomous agents are AI assistants with specific tools, permissions, and trust levels that can perform automated tasks.

### Configuration

```yaml
schema_version: "3.1.0"
metadata:
  title: "Project with Autonomous Agents"
  description: "AI assistant with configured agents"

content: |
  # Project Guidelines
  Use agents for automated tasks.

# Top-level in v3.0+
agents:
  - name: test-generator
    prompt: |
      You are a test automation expert. Generate comprehensive tests that:
      - Cover normal operations
      - Test edge cases
      - Handle error conditions
      - Mock external dependencies appropriately
    description: "Automatically generate unit tests"
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
    prompt: |
      You are a bug-fixing specialist. Identify and fix bugs while:
      - Understanding the root cause
      - Applying minimal, focused changes
      - Adding tests to prevent regression
    description: "Automatically fix common bugs"
    tools:
      - file_read
      - file_write
      - git_diff
    trust_level: untrusted
    requires_approval: true
```

### Agent Fields (v3.1.0)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | string | ✅ Yes | Agent identifier |
| `prompt` | string | ✅ Yes | Full markdown prompt (v3.1.0+) |
| `description` | string | ⚠️ Optional | High-level purpose |
| `tools` | list[string] | ⚠️ Optional | Available tools |
| `trust_level` | string | ⚠️ Optional | 'full', 'partial', 'untrusted' |
| `requires_approval` | boolean | ⚠️ Optional | Whether actions need approval |
| `context` | object | ⚠️ Optional | Additional context |
| `trust_metadata` | object | ⚠️ Optional | Trust metadata |

!!! note "Schema v3.0.0 vs v3.1.0"
    - **v3.0.0**: Uses `system_prompt` field (deprecated)
    - **v3.1.0**: Uses `prompt` field (recommended)
    - Both versions are backward compatible

### Trust Levels

**Full Trust**:
```yaml
agents:
  - name: docs-writer
    prompt: "Generate documentation..."
    trust_level: full
    requires_approval: false  # Can run autonomously
```

**Partial Trust**:
```yaml
agents:
  - name: test-generator
    prompt: "Generate tests..."
    trust_level: partial
    requires_approval: true  # Requires approval for actions
```

**Untrusted**:
```yaml
agents:
  - name: experimental-optimizer
    prompt: "Optimize code..."
    trust_level: untrusted
    requires_approval: true  # Always requires approval
```

### Editor Support

Autonomous agents are supported by:

- ✅ **Claude Code** - `.claude/agents/*.md`
- ✅ **Continue** - Agent configurations
- ✅ **Cursor** - `AGENTS.md`
- ✅ **Amazon Q** - `.amazonq/cli-agents/*.json`
- ⚠️ **Others** - Via commands/prompts

---

## Event Hooks

Event hooks are automated workflows triggered by specific events like pre-commit, post-save, or custom triggers.

### Configuration

```yaml
schema_version: "3.1.0"
metadata:
  title: "Project with Event Hooks"
  description: "AI assistant with automated workflows"

content: |
  # Project Guidelines
  Hooks automate common workflows.

# Top-level in v3.0+
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

  - name: validate-schema
    event: pre-commit
    command: "promptrek validate"
    description: "Validate PrompTrek files before commit"
    requires_reapproval: false
```

### Hook Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | string | ✅ Yes | Hook identifier |
| `event` | string | ✅ Yes | Trigger event |
| `command` | string | ✅ Yes | Command to execute |
| `agent` | string | ⚠️ Optional | Agent to run (v3.1.0+) |
| `conditions` | object | ⚠️ Optional | Execution conditions |
| `requires_reapproval` | boolean | ⚠️ Optional | Require reapproval on changes |
| `description` | string | ⚠️ Optional | Hook description |
| `trust_metadata` | object | ⚠️ Optional | Trust metadata |

### Common Events

**Pre-commit**:
```yaml
hooks:
  - name: lint-and-test
    event: pre-commit
    command: "npm run lint && npm test"
    description: "Quality checks before commit"
```

**Post-save**:
```yaml
hooks:
  - name: auto-format
    event: post-save
    command: "prettier --write {file}"
    conditions:
      file_pattern: "**/*.{js,ts,tsx}"
```

**Custom Events**:
```yaml
hooks:
  - name: deploy-check
    event: pre-deploy
    command: "npm run build && npm run test:e2e"
    requires_reapproval: true
```

### Editor Support

Event hooks are supported by:

- ✅ **Claude Code** - `.claude/settings.local.json` and `.claude/hooks.yaml`
- ⚠️ **Others** - Via pre-commit or custom scripts

---

## CLI Commands for Plugins

### List Plugins

```bash
# List all plugins in a .promptrek.yaml file
promptrek plugins list --file project.promptrek.yaml
```

### Generate Plugin Files

```bash
# Generate plugin files for a specific editor
promptrek plugins generate --file project.promptrek.yaml --editor claude --output .
```

### Validate Plugin Configuration

```bash
# Validate plugin configuration
promptrek plugins validate --file project.promptrek.yaml
```

### Sync Plugins

```bash
# Sync plugins from editor files back to .promptrek.yaml
promptrek plugins sync --editor claude --source-dir . --output synced.promptrek.yaml
```

---

## Best Practices

### Security

**Environment Variables**:
```yaml
variables:
  GITHUB_TOKEN: "ghp_token_here"  # Use variables for secrets

mcp_servers:
  - name: github
    env:
      GITHUB_TOKEN: "{{{ GITHUB_TOKEN }}}"  # Reference variable
```

**Trust Levels**:
```yaml
# Be explicit about trust
agents:
  - name: risky-agent
    trust_level: untrusted
    requires_approval: true
```

### Organization

**Separate Concerns**:
```yaml
# MCP servers for integrations
mcp_servers:
  - name: filesystem
    # ... filesystem config

# Commands for common tasks
commands:
  - name: review
    # ... review command

# Agents for automation
agents:
  - name: test-gen
    # ... agent config

# Hooks for workflows
hooks:
  - name: pre-commit
    # ... hook config
```

### Documentation

**Add Descriptions**:
```yaml
commands:
  - name: deploy
    description: "Deploy to production (requires approval)"
    prompt: |
      # Deployment Workflow
      Detailed deployment instructions...
```

**Provide Examples**:
```yaml
commands:
  - name: review-pr
    examples:
      - "review-pr --pr=123"
      - "review-pr --quick"
```

---

## Migration from v2.1.0 to v3.0.0

### Before (v2.1.0) - Nested Structure

```yaml
schema_version: "2.1.0"
plugins:  # ❌ Wrapper removed in v3.0
  mcp_servers:
    - name: filesystem
      # ...
  commands:
    - name: review
      # ...
```

### After (v3.0.0+) - Top-Level

```yaml
schema_version: "3.1.0"
# No plugins wrapper - top-level fields
mcp_servers:  # ✅ Top-level
  - name: filesystem
    # ...
commands:  # ✅ Top-level
  - name: review
    # ...
```

### Automatic Migration

```bash
# Migrate v2.1.0 to v3.1.0
promptrek migrate project.promptrek.yaml -o project-v3.promptrek.yaml
```

---

## Examples

### Full Plugin Ecosystem

```yaml
schema_version: "3.1.0"

metadata:
  title: "Full Plugin Example"
  description: "Complete plugin ecosystem demonstration"

content: |
  # Project with Full Plugin Support

  This project demonstrates all plugin types.

variables:
  GITHUB_TOKEN: "ghp_token_here"

# MCP Servers
mcp_servers:
  - name: github
    command: npx
    args: ["-y", "@modelcontextprotocol/server-github"]
    env:
      GITHUB_TOKEN: "{{{ GITHUB_TOKEN }}}"

# Custom Commands
commands:
  - name: review
    description: "Code review"
    prompt: "Review for quality and security"

# Autonomous Agents
agents:
  - name: test-gen
    prompt: "Generate comprehensive tests"
    tools: [file_read, file_write]
    trust_level: partial

# Event Hooks
hooks:
  - name: pre-commit
    event: pre-commit
    command: "npm test"
```

---

## Related Documentation

- [UPF Specification](../upf-specification.md) - Detailed schema documentation
- [Adapters](../adapters/index.md) - Editor-specific plugin support
- [Sync Workflow](../workflows/sync.md) - Syncing plugin configurations
- [Pre-commit Integration](../workflows/pre-commit.md) - Hook automation
