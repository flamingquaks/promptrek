# promptrek plugins

Manage and interact with PrompTrek plugins (MCP servers, commands, agents, hooks).

## Synopsis

```bash
# List plugins
promptrek plugins list [FILE]

# Generate plugin configs for editors
promptrek plugins generate [FILE] [OPTIONS]

# Validate plugin configurations
promptrek plugins validate [FILE]
```

## Description

The `plugins` command group provides tools for working with PrompTrek's plugin system, including MCP servers, slash commands, autonomous agents, and event hooks.

## Subcommands

### plugins list

List all configured plugins in a PrompTrek file.

```bash
promptrek plugins list [FILE]
```

**Options**:
- `FILE` (optional): PrompTrek file to inspect (auto-detects if not specified)
- `-v, --verbose`: Show detailed plugin information

**Example**:

```bash
$ promptrek plugins list project.promptrek.yaml

📦 Plugins configured in project.promptrek.yaml:
Schema version: 3.1.0

🔌 MCP Servers (2):
  • github: npx
    GitHub API integration for code analysis
  • filesystem: npx
    Filesystem access for code operations

⚡ Commands (2):
  • review-code: Comprehensive code review
  • generate-tests: Generate unit tests

🤖 Agents (1):
  • test-generator: Automated test generation
    Trust Level: partial

🪝 Hooks (2):
  • pre-commit (on pre-commit)
  • post-merge (on post-merge)
```

### plugins generate

Generate plugin configuration files for specific editors.

```bash
promptrek plugins generate [FILE] [OPTIONS]
```

**Options**:
- `FILE` (optional): PrompTrek file to use
- `-e, --editor EDITOR`: Target editor (or 'all')
- `-o, --output DIR`: Output directory
- `--dry-run`: Preview without creating files
- `--force-system-wide`: Force system-wide configuration
- `--auto-confirm`: Skip confirmation prompts

**Examples**:

```bash
# Generate for specific editor
promptrek plugins generate --editor claude

# Generate for all editors
promptrek plugins generate --editor all

# Preview what would be generated
promptrek plugins generate --editor claude --dry-run

# Force system-wide configuration (for editors that support it)
promptrek plugins generate --editor windsurf --force-system-wide
```

### plugins validate

Validate plugin configurations.

```bash
promptrek plugins validate [FILE]
```

**Options**:
- `FILE` (optional): PrompTrek file to validate
- `-v, --verbose`: Show detailed validation results

**Example**:

```bash
$ promptrek plugins validate project.promptrek.yaml

🔍 Validating plugin configurations in project.promptrek.yaml...

✅ All plugin configurations are valid!
```

## Plugin Types

### MCP Servers

Model Context Protocol servers provide extended capabilities to AI editors.

```yaml
mcp_servers:
  - name: github
    command: npx
    args: ["-y", "@modelcontextprotocol/server-github"]
    env:
      GITHUB_TOKEN: "{{{ GITHUB_TOKEN }}}"
    description: "GitHub API integration"
    trust_metadata:
      trusted: true
      trust_level: full
```

**Validation checks**:
- Server name is unique
- Command is specified
- Environment variables are properly formatted
- Trust metadata is valid

### Commands

Slash commands and workflows for AI editors.

```yaml
commands:
  - name: review-code
    description: "Code review command"
    prompt: |
      Review the selected code for quality and best practices
    output_format: markdown
    requires_approval: false
```

**v3.1 multi-step workflows**:

```yaml
commands:
  - name: release-workflow
    description: "Complete release workflow"
    multi_step: true
    tool_calls: [git, npm, gh]
    prompt: |
      Execute release process
    steps:
      - name: test
        action: execute_command
        params:
          command: "npm test"
```

**Validation checks**:
- Command name is unique
- Prompt is specified
- Multi-step workflows have valid steps
- Tool calls are properly formatted

### Agents

Autonomous agents for complex tasks.

```yaml
agents:
  - name: test-generator
    description: "Automated test generation"
    prompt: |
      # Test Generation Agent
      Generate comprehensive tests...
    tools: [file_read, file_write, run_tests]
    trust_level: partial
    requires_approval: true
```

**Validation checks**:
- Agent name is unique
- Prompt is specified
- Trust level is valid
- Tools are properly listed

### Hooks

Event-driven automation hooks.

```yaml
hooks:
  - name: pre-commit
    event: pre-commit
    command: "npm test"
    conditions:
      path: "**/*.ts"
    requires_reapproval: false
```

**Validation checks**:
- Hook name is unique
- Event is specified
- Command is specified
- Conditions are properly formatted

## Editor Plugin Support

### Project-Level Support

Editors with full project-level plugin support:

- **claude**: `.claude/mcp.json`
- **cursor**: `.cursor/mcp-servers.json`
- **continue**: `.continue/config.json`
- **cline**: `.vscode/settings.json`
- **amazon-q**: `.amazonq/mcp.json`
- **kiro**: `.kiro/settings/mcp.json`

### System-Wide Only

Editors requiring system-wide configuration:

- **windsurf**: `~/.codeium/windsurf/mcp_config.json`

When using system-wide configuration, PrompTrek prompts for confirmation unless `--auto-confirm` is used.

## MCP Configuration Strategy

PrompTrek uses different strategies for different editors:

```bash
$ promptrek --verbose plugins generate --editor all

📋 MCP Configuration Strategy:
  ✅ claude: Project-level (.claude/mcp.json)
  ✅ cursor: Project-level (.cursor/mcp-servers.json)
  ✅ continue: Project-level (.continue/config.json)
  ⚠️  windsurf: System-wide only (~/.codeium/windsurf/mcp_config.json)
  ✅ cline: Project-level (.vscode/settings.json)
  ✅ amazon-q: Project-level (.amazonq/mcp.json)
  ✅ kiro: Project-level (.kiro/settings/mcp.json)

🔌 Generating plugin files for claude, cursor, continue, windsurf, cline, amazon-q, kiro...
```

## Complete Examples

### List Plugins

```bash
# Auto-detect file
promptrek plugins list

# Specific file
promptrek plugins list backend.promptrek.yaml

# Verbose output
promptrek plugins list --verbose
```

### Generate Plugin Configs

```bash
# Generate for Claude (project-level)
promptrek plugins generate --editor claude

# Generate for all editors
promptrek plugins generate --editor all

# Preview first
promptrek plugins generate --editor claude --dry-run

# System-wide for Windsurf
promptrek plugins generate --editor windsurf --force-system-wide --auto-confirm

# Custom output directory
promptrek plugins generate --editor claude --output ./ai-configs
```

### Validate Plugins

```bash
# Validate current file
promptrek plugins validate

# Validate specific file
promptrek plugins validate project.promptrek.yaml

# Verbose validation
promptrek --verbose plugins validate
```

## Common Workflows

### Plugin Development Workflow

```bash
# 1. Add plugins to configuration
vim project.promptrek.yaml

# 2. Validate plugin configuration
promptrek plugins validate

# 3. Preview generation
promptrek plugins generate --editor claude --dry-run

# 4. Generate plugin files
promptrek plugins generate --editor claude

# 5. Test with editor
# (Open your editor and verify plugins work)
```

### Multi-Editor Plugin Setup

```bash
# Generate for all editors that support plugins
promptrek plugins generate --editor all

# Or generate for specific editors
promptrek plugins generate --editor claude
promptrek plugins generate --editor cursor
promptrek plugins generate --editor continue
```

### Troubleshooting Plugins

```bash
# List current plugins
promptrek plugins list

# Validate configuration
promptrek plugins validate

# Check what would be generated
promptrek plugins generate --editor claude --dry-run

# Verbose validation for detailed errors
promptrek --verbose plugins validate
```

## Error Handling

### No Plugins Configured

```bash
$ promptrek plugins list minimal.promptrek.yaml

No plugins configured in this file.
Schema version: 3.1.0
```

### Plugin Validation Errors

```bash
$ promptrek plugins validate broken.promptrek.yaml

❌ Validation errors found:
  • MCP server 'github' missing command
  • Command 'review' missing prompt
  • Agent 'test-gen' missing prompt
```

### Schema Version Too Old

```bash
$ promptrek plugins list old.promptrek.yaml

⚠️  This file uses schema v1.x which doesn't support plugins.
   Run 'promptrek migrate' to upgrade to v2.1.0 or v3.0
```

## Best Practices

!!! tip "Validate Before Generate"
    Always validate plugin configurations before generating:
    ```bash
    promptrek plugins validate && promptrek plugins generate --editor all
    ```

!!! tip "Test One Editor First"
    Test plugin generation with one editor before generating for all:
    ```bash
    promptrek plugins generate --editor claude --dry-run
    promptrek plugins generate --editor claude
    # Test with Claude
    promptrek plugins generate --editor all
    ```

!!! warning "System-Wide Configs"
    Be careful with system-wide plugin configurations (like Windsurf). They affect all projects:
    ```bash
    # Always review what would be changed
    promptrek plugins generate --editor windsurf --dry-run
    ```

!!! note "MCP Server Secrets"
    Use local variables file for MCP server secrets:
    ```yaml
    # .promptrek/variables.promptrek.yaml (gitignored)
    GITHUB_TOKEN: "ghp_actual_token"
    ```

## See Also

- [MCP Servers Documentation](../../user-guide/plugins/index.md)
- [Generate Command](generate.md)
- [Validate Command](validate.md)
- [Variables](../../user-guide/configuration/variables.md)
