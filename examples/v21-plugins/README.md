# PrompTrek v2.1 Plugin Examples

This directory contains comprehensive examples demonstrating PrompTrek v2.1 plugin features, including MCP servers, custom commands, and autonomous agents.

## Overview

PrompTrek v2.1 introduces plugin support for extending AI editor capabilities:

| Feature | Description | Editors |
|---------|-------------|---------|
| **MCP Servers** | External tools and data sources via Model Context Protocol | Claude, Cursor, Continue, Cline, Windsurf |
| **Custom Commands** | Slash commands for common development tasks | Cursor, Continue (partial support in others) |
| **Autonomous Agents** | AI agents that can work independently | Cursor (experimental in others) |

## Example Files

### 1. `complete-example.promptrek.yaml`
**The most comprehensive example** - Shows all v2.1 features working together:
- Multiple MCP servers (filesystem, GitHub, web search)
- Custom slash commands for code review, testing, documentation
- Autonomous agents for bug fixing, quality monitoring, doc maintenance

**Best for:** Understanding the full power of v2.1 plugins

### 2. `mcp-servers.promptrek.yaml`
Focused example of MCP server integration:
- Filesystem server for file access
- GitHub server for repository integration
- PostgreSQL server for database access
- Slack server for team communication
- Variable substitution for sensitive data

**Best for:** Learning MCP server configuration

### 3. `custom-commands.promptrek.yaml`
Examples of powerful slash commands:
- `/review-pr` - Comprehensive pull request review
- `/generate-tests` - Unit test generation
- `/write-docs` - Documentation generation
- `/security-audit` - Security vulnerability scanning

**Best for:** Creating custom editor commands

### 4. `autonomous-agents.promptrek.yaml`
Autonomous agent configurations:
- Code reviewer agent with trust controls
- Documentation generator agent
- Test generator agent
- Bug fixer agent with safety limits
- Refactoring agent

**Best for:** Setting up automated workflows

## Quick Start

### 1. Choose an Example

```bash
cd examples/v21-plugins
```

### 2. Set Environment Variables

For MCP servers that need credentials:

```bash
export GITHUB_TOKEN="your-github-token"
export DATABASE_URL="postgresql://localhost/mydb"
export SLACK_BOT_TOKEN="xoxb-your-token"
```

### 3. Generate Plugin Configuration

For **Claude Code**:
```bash
promptrek plugins generate complete-example.promptrek.yaml -e claude
# Creates .claude/mcp.json
```

For **Cursor**:
```bash
promptrek plugins generate complete-example.promptrek.yaml -e cursor
# Creates .cursor/mcp.json, .cursor/agents.json, .cursor/commands.json
```

For **Continue**:
```bash
promptrek plugins generate complete-example.promptrek.yaml -e continue
# Creates .continue/config.json (unified config)
```

For **all editors**:
```bash
promptrek plugins generate complete-example.promptrek.yaml --all
```

### 4. Use in Your Editor

**MCP Servers:**
- Load automatically when editor starts
- Access via AI assistant context
- Check editor logs for connection status

**Custom Commands:**
- Type `/` in your editor to see available commands
- Example: `/review src/api/users.ts`
- Some editors may require restart

**Agents:**
- Configure in editor settings
- Enable/disable specific agents
- Set trust levels and approval requirements

## Editor-Specific Notes

### Claude Code (claude.ai/code)

**Supported:**
- ✅ MCP servers (`.claude/mcp.json`)
- ⚠️ Commands (experimental)
- ⚠️ Agents (planned)

**Configuration:**
```bash
promptrek plugins generate mcp-servers.promptrek.yaml -e claude
```

**Location:** `.claude/mcp.json`

### Cursor

**Supported:**
- ✅ MCP servers
- ✅ Custom commands
- ✅ Autonomous agents

**Configuration:**
```bash
promptrek plugins generate complete-example.promptrek.yaml -e cursor
```

**Locations:**
- `.cursor/mcp.json` - MCP servers
- `.cursor/commands.json` - Custom commands
- `.cursor/agents.json` - Agent configurations

### Continue

**Supported:**
- ✅ MCP servers
- ✅ Custom slash commands
- ⚠️ Agents (limited)

**Configuration:**
```bash
promptrek plugins generate complete-example.promptrek.yaml -e continue
```

**Location:** `.continue/config.json` (unified config)

**Special:** Continue uses a unified config format combining all plugin types.

### Cline

**Supported:**
- ✅ MCP servers (via VS Code settings)
- ⚠️ Commands (limited)
- ⚠️ Agents (planned)

**Configuration:**
```bash
promptrek plugins generate mcp-servers.promptrek.yaml -e cline
```

**Location:** `.vscode/settings.json` under `cline.mcpServers`

### Windsurf

**Supported:**
- ✅ MCP servers (system-wide only)
- ⚠️ Commands (planned)
- ⚠️ Agents (planned)

**Configuration:**
```bash
promptrek plugins generate mcp-servers.promptrek.yaml -e windsurf
# User confirmation required for system-wide config
```

**Location:** `~/.codeium/windsurf/mcp_config.json` (system-wide)

**Note:** Windsurf requires user confirmation for system-wide changes. Use `--yes` flag to skip:
```bash
promptrek plugins generate mcp-servers.promptrek.yaml -e windsurf --yes
```

## Advanced Usage

### Variable Substitution

Use `{{{ VARIABLE_NAME }}}` syntax for sensitive data:

```yaml
plugins:
  mcp_servers:
    - name: github
      env:
        GITHUB_TOKEN: "{{{ GITHUB_TOKEN }}}"
        GITHUB_OWNER: "{{{ GITHUB_OWNER }}}"

variables:
  GITHUB_TOKEN: "your-token"
  GITHUB_OWNER: "your-username"
```

Override variables at generation time:
```bash
promptrek plugins generate example.yaml -e claude \
  -V GITHUB_TOKEN=ghp_newtoken \
  -V GITHUB_OWNER=myorg
```

### Dry Run

Preview generated files without writing:
```bash
promptrek plugins generate complete-example.yaml -e cursor --dry-run -v
```

### Trust Metadata

Control plugin trust levels:

```yaml
trust_metadata:
  trusted: true
  trust_level: full  # full | partial | untrusted
  requires_approval: false
  source: official  # official | community | local
  verified_by: Anthropic
  verified_date: "2025-01-15"
```

**Trust Levels:**
- `full` - Run without user approval
- `partial` - Approve sensitive operations only
- `untrusted` - Approve all operations

### Project vs System-Wide

**Project-level** (default):
- Configurations stored in project directory
- Version controlled with code
- Different per project

**System-wide** (some editors):
- Configurations in home directory
- Shared across all projects
- Requires user confirmation

Force system-wide generation:
```bash
promptrek plugins generate example.yaml -e windsurf --force-system-wide --yes
```

### Merging with Existing Configs

PrompTrek automatically merges new plugins with existing configurations:

```bash
# First generation
promptrek plugins generate mcp-servers.yaml -e claude

# Add more servers (merges automatically)
promptrek plugins generate additional-servers.yaml -e claude
```

## Troubleshooting

### MCP Server Not Loading

1. Check editor logs for connection errors
2. Verify npx is installed: `npx --version`
3. Test server manually: `npx -y @modelcontextprotocol/server-filesystem /tmp`
4. Check environment variables are set

### Command Not Appearing

1. Restart your editor
2. Check command syntax in config
3. Verify editor supports custom commands
4. Look for errors in editor console

### Permission Denied

1. Check file permissions: `ls -la .claude/mcp.json`
2. Verify you own the config directory
3. For system-wide configs, ensure no admin access required

### Variables Not Substituted

1. Check variable syntax: `{{{ VAR_NAME }}}` (three braces!)
2. Ensure variable is defined in `variables:` section
3. Pass via CLI: `-V VAR_NAME=value`
4. Check for typos in variable names

## Best Practices

### Security

- ✅ Use environment variables for secrets
- ✅ Never commit tokens to git
- ✅ Set appropriate trust levels
- ✅ Review untrusted plugins before use
- ❌ Don't share plugin configs with hardcoded secrets

### Organization

- ✅ Create separate configs for different workflows
- ✅ Use meaningful server/command names
- ✅ Document custom commands with examples
- ✅ Group related plugins together

### Performance

- ✅ Only enable MCP servers you need
- ✅ Use lazy loading for heavy servers
- ✅ Monitor server startup time
- ✅ Limit agent autonomy in large projects

## Resources

- [PrompTrek Documentation](https://github.com/addierudy/promptrek)
- [MCP Protocol Specification](https://modelcontextprotocol.io)
- [Official MCP Servers](https://github.com/modelcontextprotocol/servers)
- [Claude Code Docs](https://docs.claude.com/claude-code)
- [Cursor Docs](https://docs.cursor.com)
- [Continue Docs](https://docs.continue.dev)

## Contributing

Found a great plugin configuration? Share it!

1. Add your example to this directory
2. Update this README
3. Submit a pull request

## License

These examples are provided as-is for educational purposes. Adapt them to your needs!
