# MCP Server Configuration Example

This example demonstrates how to configure Model Context Protocol (MCP) servers with PrompTrek to extend your AI editor's capabilities.

## Overview

**Use Case:** Integrate external tools and services with AI editors through MCP servers

**What You'll Learn:**
- What MCP servers are and how they work
- Configuring MCP servers in PrompTrek
- Security and trust management
- Environment variables and secrets
- Editor-specific MCP integration

## What are MCP Servers?

Model Context Protocol (MCP) servers provide AI assistants with access to external tools and data sources through a standardized protocol.

**Common Use Cases:**
- **File System Access** - Read/write project files
- **Database Queries** - Query PostgreSQL, MySQL, etc.
- **API Integration** - GitHub, Slack, Jira, etc.
- **Custom Tools** - Project-specific functionality

**Supported Editors:**
- Claude Code (full support)
- Cursor (full support)
- Continue (full support)
- Cline (VSCode settings)
- Windsurf (system-wide config)
- Amazon Q (project-level)

## Complete Configuration

```yaml
# yaml-language-server: $schema=https://promptrek.ai/schema/v3.1.0.json
schema_version: "3.1.0"
metadata:
  title: MCP Servers Example
  description: Model Context Protocol server integration
  version: 1.0.0
  author: PrompTrek Team
  tags: [mcp, plugins, integration]

content: |
  # MCP Servers Configuration

  This project uses Model Context Protocol (MCP) servers to extend
  AI assistant capabilities with external tools and data sources.

  ## Available MCP Servers

  ### Filesystem
  Provides read/write access to project directories.

  ### GitHub
  Access repositories, issues, and pull requests.

  ### PostgreSQL
  Query and manage database.

  ### Slack
  Send messages and manage workspace.

  ## Security Notes

  - Filesystem server has partial trust (requires approval)
  - GitHub server has full trust
  - PostgreSQL server is untrusted (always requires approval)
  - All servers use environment variables for secrets

# MCP Server configurations
mcp_servers:
  # Filesystem server - controlled file access
  - name: filesystem
    command: npx
    args:
      - "-y"
      - "@modelcontextprotocol/server-filesystem"
      - "/path/to/allowed/directory"
    description: Provides read/write access to specified directories
    trust_metadata:
      trusted: true
      trust_level: partial
      requires_approval: true
      source: official
      verified_by: Anthropic
      verified_date: "2025-01-15"

  # GitHub server - repository access
  - name: github
    command: npx
    args:
      - "-y"
      - "@modelcontextprotocol/server-github"
    env:
      GITHUB_TOKEN: "{{{ GITHUB_TOKEN }}}"
      GITHUB_OWNER: "{{{ GITHUB_OWNER }}}"
    description: Access GitHub repositories, issues, and pull requests
    trust_metadata:
      trusted: true
      trust_level: full
      requires_approval: false
      source: official

  # PostgreSQL server - database access
  - name: postgres
    command: npx
    args:
      - "-y"
      - "@modelcontextprotocol/server-postgres"
    env:
      POSTGRES_CONNECTION_STRING: "{{{ DATABASE_URL }}}"
    description: Query and manage PostgreSQL databases
    trust_metadata:
      trusted: false
      trust_level: untrusted
      requires_approval: true
      source: community

  # Slack server - workspace integration
  - name: slack
    command: npx
    args:
      - "-y"
      - "@modelcontextprotocol/server-slack"
    env:
      SLACK_BOT_TOKEN: "{{{ SLACK_BOT_TOKEN }}}"
      SLACK_TEAM_ID: "{{{ SLACK_TEAM_ID }}}"
    description: Send messages and manage Slack workspace

variables:
  GITHUB_TOKEN: "your-github-token"
  GITHUB_OWNER: "your-username"
  DATABASE_URL: "postgresql://localhost/mydb"
  SLACK_BOT_TOKEN: "xoxb-your-token"
  SLACK_TEAM_ID: "T1234567"
```

## Configuration Breakdown

### MCP Server Structure

Each MCP server configuration includes:

```yaml
- name: server-name              # Unique identifier
  command: npx                   # Command to run
  args: [...]                    # Command arguments
  env:                           # Environment variables
    VAR_NAME: "{{{ VALUE }}}"   # Use variable substitution
  description: "What it does"   # Human-readable description
  trust_metadata:                # Security settings
    trusted: true/false
    trust_level: full/partial/untrusted
    requires_approval: true/false
```

### Trust Levels

**full** - Complete trust, no approval needed
- Use for official, verified servers
- Example: GitHub server from Anthropic

**partial** - Limited trust, approval for sensitive operations
- Use for filesystem access
- Example: File server with restricted paths

**untrusted** - No trust, always require approval
- Use for community servers
- Example: Custom database servers

## Usage Instructions

### Step 1: Save Configuration

Save to `mcp-config.promptrek.yaml`.

### Step 2: Configure Secrets

**Option A:** Use environment variables

```bash
export GITHUB_TOKEN="ghp_your_token"
export DATABASE_URL="postgresql://user:pass@localhost/db"
```

**Option B:** Override at generation time

```bash
promptrek plugins generate mcp-config.promptrek.yaml \
  --editor claude \
  -V GITHUB_TOKEN=ghp_your_actual_token \
  -V DATABASE_URL=postgresql://prod-db:5432/mydb
```

### Step 3: Generate MCP Files

```bash
# For Claude Code
promptrek plugins generate mcp-config.promptrek.yaml --editor claude

# For Cursor
promptrek plugins generate mcp-config.promptrek.yaml --editor cursor

# For all supported editors
promptrek plugins generate mcp-config.promptrek.yaml --all
```

### Step 4: Verify Generated Files

**Claude Code:** `.mcp.json`
```json
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "/path/to/allowed/directory"]
    },
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_TOKEN": "ghp_your_token",
        "GITHUB_OWNER": "your-username"
      }
    }
  }
}
```

**Cursor:** `.cursor/mcp.json`

**Continue:** `.continue/config.json` (merged with existing config)

## Official MCP Servers

### Filesystem Server

```yaml
- name: filesystem
  command: npx
  args:
    - "-y"
    - "@modelcontextprotocol/server-filesystem"
    - "/path/to/project"
    - "/path/to/docs"
  description: Access project files and documentation
```

**Use Cases:**
- Read configuration files
- Generate code files
- Update documentation

### GitHub Server

```yaml
- name: github
  command: npx
  args: ["-y", "@modelcontextprotocol/server-github"]
  env:
    GITHUB_TOKEN: "{{{ GITHUB_TOKEN }}}"
  description: GitHub repository integration
```

**Capabilities:**
- List issues and PRs
- Create/update issues
- Read repository contents
- Create pull requests

**Setup:**
1. Create GitHub Personal Access Token
2. Add to environment or variables
3. Generate configuration

### PostgreSQL Server

```yaml
- name: postgres
  command: npx
  args: ["-y", "@modelcontextprotocol/server-postgres"]
  env:
    POSTGRES_CONNECTION_STRING: "{{{ DATABASE_URL }}}"
  description: PostgreSQL database access
```

**Capabilities:**
- Run SELECT queries
- Read schema information
- Execute safe queries

**Security:** Always use `requires_approval: true`

### Slack Server

```yaml
- name: slack
  command: npx
  args: ["-y", "@modelcontextprotocol/server-slack"]
  env:
    SLACK_BOT_TOKEN: "{{{ SLACK_BOT_TOKEN }}}"
    SLACK_TEAM_ID: "{{{ SLACK_TEAM_ID }}}"
  description: Slack workspace integration
```

**Capabilities:**
- Send messages to channels
- List channels and users
- Read messages

## Advanced Configuration

### Multiple Filesystem Paths

```yaml
- name: filesystem-project
  command: npx
  args:
    - "-y"
    - "@modelcontextprotocol/server-filesystem"
    - "/home/user/project/src"
    - "/home/user/project/tests"
    - "/home/user/project/docs"
  description: Access project source, tests, and docs
```

### Custom MCP Server

```yaml
- name: custom-api
  command: node
  args:
    - "/path/to/custom-mcp-server/index.js"
  env:
    API_KEY: "{{{ CUSTOM_API_KEY }}}"
    API_URL: "{{{ CUSTOM_API_URL }}}"
  description: Custom API integration
  trust_metadata:
    trusted: false
    trust_level: untrusted
    requires_approval: true
    source: local
```

### Environment-Specific Configuration

```yaml
# Development
variables:
  DATABASE_URL: "postgresql://localhost:5432/dev_db"
  GITHUB_TOKEN: "ghp_dev_token"

# Override for production
# promptrek plugins generate --editor claude \
#   -V DATABASE_URL=postgresql://prod:5432/prod_db \
#   -V GITHUB_TOKEN=ghp_prod_token
```

## Security Best Practices

### Secrets Management

!!! warning "Never Commit Secrets"
    Never commit actual secrets to version control. Use:
    - Environment variables
    - Variable substitution
    - Secret management tools

**Good:**
```yaml
variables:
  GITHUB_TOKEN: "{{{ GITHUB_TOKEN }}}"  # Placeholder
```

**Bad:**
```yaml
variables:
  GITHUB_TOKEN: "ghp_actualsecrettoken123"  # Actual secret
```

### Trust Configuration

!!! tip "Conservative Trust Levels"
    Start with more restrictive trust levels:

    ```yaml
    trust_metadata:
      trusted: false
      trust_level: untrusted
      requires_approval: true
    ```

### File System Restrictions

!!! tip "Limit File Access"
    Only grant access to necessary directories:

    ```yaml
    args:
      - "-y"
      - "@modelcontextprotocol/server-filesystem"
      - "/project/src"           # Only src
      # Not entire filesystem!
    ```

## Editor-Specific Notes

### Claude Code

**Location:** `.mcp.json` (project root)

**Format:**
```json
{
  "mcpServers": {
    "server-name": {
      "command": "npx",
      "args": [...],
      "env": {...}
    }
  }
}
```

**Reload:** Restart Claude Code to load new servers

### Cursor

**Location:** `.cursor/mcp.json` (project-level)

**Fallback:** `~/.cursor/mcp.json` (user-level)

**Note:** Project-level preferred for team sharing

### Continue

**Location:** `.continue/config.json` (merged)

**Format:** Integrated into unified config file

**Note:** Supports both MCP and custom context providers

### Cline (VSCode)

**Location:** `.vscode/settings.json`

**Format:**
```json
{
  "cline.mcpServers": {
    "server-name": {
      "command": "npx",
      "args": [...]
    }
  }
}
```

## Troubleshooting

### MCP Server Not Loading

**Problem:** Server doesn't appear in editor

**Solutions:**
1. Check file location (`.mcp.json`, `.cursor/mcp.json`, etc.)
2. Verify JSON syntax is valid
3. Restart editor
4. Check editor logs for errors

### Authentication Errors

**Problem:** GitHub/API servers can't authenticate

**Solutions:**
1. Verify token/API key is correct
2. Check token has required permissions
3. Ensure environment variable is set
4. Test token with curl/API client first

### Command Not Found

**Problem:** `npx: command not found`

**Solutions:**
1. Install Node.js and npm
2. Use absolute path: `/usr/local/bin/npx`
3. Or specify full path to server

## Real-World Example

### Full-Stack Development Setup

```yaml
schema_version: "3.1.0"
metadata:
  title: Full-Stack Dev Environment

content: |
  # Development Environment with MCP

  This configuration provides access to:
  - Project source code
  - GitHub for issues/PRs
  - PostgreSQL development database
  - Slack for notifications

mcp_servers:
  # Source code access
  - name: filesystem
    command: npx
    args:
      - "-y"
      - "@modelcontextprotocol/server-filesystem"
      - "{{{ PROJECT_ROOT }}}/src"
      - "{{{ PROJECT_ROOT }}}/tests"
    description: Project source and tests

  # GitHub for workflow
  - name: github
    command: npx
    args: ["-y", "@modelcontextprotocol/server-github"]
    env:
      GITHUB_TOKEN: "{{{ GITHUB_TOKEN }}}"
      GITHUB_OWNER: "{{{ GITHUB_OWNER }}}"
      GITHUB_REPO: "{{{ GITHUB_REPO }}}"

  # Database access
  - name: postgres
    command: npx
    args: ["-y", "@modelcontextprotocol/server-postgres"]
    env:
      POSTGRES_CONNECTION_STRING: "{{{ DATABASE_URL }}}"
    trust_metadata:
      trusted: false
      requires_approval: true

  # Team notifications
  - name: slack
    command: npx
    args: ["-y", "@modelcontextprotocol/server-slack"]
    env:
      SLACK_BOT_TOKEN: "{{{ SLACK_BOT_TOKEN }}}"
      SLACK_TEAM_ID: "{{{ SLACK_TEAM_ID }}}"

variables:
  PROJECT_ROOT: "/home/user/my-project"
  GITHUB_TOKEN: "ghp_xxx"
  GITHUB_OWNER: "acme"
  GITHUB_REPO: "my-project"
  DATABASE_URL: "postgresql://localhost:5432/dev_db"
  SLACK_BOT_TOKEN: "xoxb-xxx"
  SLACK_TEAM_ID: "T1234567"
```

## Related Examples

- **[Custom Commands](custom-commands.md)** - Slash commands for AI editors
- **[Node.js API](../basic/node-api.md)** - Backend with database
- **[React TypeScript](../basic/react-typescript.md)** - Frontend development

## Additional Resources

- [MCP Specification](https://modelcontextprotocol.io/)
- [Official MCP Servers](https://github.com/modelcontextprotocol/servers)
- [Creating Custom MCP Servers](https://modelcontextprotocol.io/docs/building-servers)
- [Claude Code MCP Guide](https://docs.anthropic.com/claude/docs/mcp)

---

**Next Steps:**
1. Choose MCP servers for your project
2. Set up authentication tokens
3. Configure trust levels appropriately
4. Generate and test with your editor
5. Share configuration with team
