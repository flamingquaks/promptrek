# Frequently Asked Questions

Common questions about PrompTrek and their answers.

## General Questions

### What is PrompTrek?

PrompTrek is a universal configuration tool for AI coding assistants. It lets you define your project's AI assistant configuration once and generate editor-specific files for multiple AI editors (GitHub Copilot, Cursor, Claude Code, Continue, etc.).

**Benefits:**
- Write configuration once, use everywhere
- Share configurations across teams
- Switch editors without losing your setup
- Version control your AI assistant configuration

### Which AI editors does PrompTrek support?

**Full Support:**
- GitHub Copilot
- Cursor
- Continue
- Cline
- Claude Code
- Kiro
- Windsurf
- Amazon Q
- JetBrains AI

See the [User Guide](../user-guide/adapters.md) for feature comparison.

### Do I need to know YAML?

Basic YAML knowledge is helpful but not required. PrompTrek uses simple YAML structure:

```yaml
schema_version: "3.1.0"
metadata:
  title: "My Project"

content: |
  # My Guidelines
  - Write clean code
  - Add tests

variables:
  PROJECT_NAME: "my-project"
```

See our [examples](../examples/index.md) for templates you can customize.

### Can I use PrompTrek with my existing editor configurations?

Yes! PrompTrek has bidirectional sync:

```bash
# Import existing editor files to PrompTrek format
promptrek sync --editor cursor --output project.promptrek.yaml

# Generate back to editor files
promptrek generate project.promptrek.yaml --editor cursor
```

## Installation & Setup

### How do I install PrompTrek?

**Using uv (recommended):**
```bash
git clone https://github.com/flamingquaks/promptrek.git
cd promptrek
uv sync
```

**Using pip:**
```bash
git clone https://github.com/flamingquaks/promptrek.git
cd promptrek
pip install -e .
```

See [Getting Started](../getting-started/installation.md) for details.

### Why isn't PrompTrek on PyPI yet?

PrompTrek is under active development. A PyPI package will be available when we reach stable v1.0. For now, install from source.

### What are the system requirements?

- **Python:** 3.9 or higher
- **Operating Systems:** Linux, macOS, Windows
- **Dependencies:** See `pyproject.toml` (automatically installed)

### Do I need Node.js?

Only if you want to use MCP servers with `npx` commands. For basic PrompTrek functionality, Node.js is not required.

## Configuration

### What's the difference between schema version and application version?

**Application Version** (e.g., v0.5.0)
- The version of the PrompTrek tool itself
- Check with `promptrek --version`

**Schema Version** (e.g., v3.1.0)
- The format of your `.promptrek.yaml` files
- Specified in `schema_version` field
- Multiple schemas supported for backward compatibility

### Which schema version should I use?

**For new projects:** Use v3.1.0 (latest)

```yaml
schema_version: "3.1.0"
```

**For existing projects:**
- v2.x files work but are deprecated
- Migrate to v3.1: `promptrek migrate config.yaml`

See [Deprecation Guide](deprecation.md) for details.

### What is the `content` field?

The `content` field contains the actual guidelines and instructions for your AI assistant:

```yaml
content: |
  # Project Guidelines

  ## Code Style
  - Use TypeScript
  - Write tests

  ## Architecture
  - Follow MVC pattern
```

It supports markdown formatting and can include code examples.

### How do I use variables?

**Define variables:**
```yaml
variables:
  PROJECT_NAME: "my-app"
  API_URL: "https://api.example.com"
```

**Use in content:**
```yaml
content: |
  Project: {{{ PROJECT_NAME }}}
  API: {{{ API_URL }}}
```

**Override at generation:**
```bash
promptrek generate config.yaml --editor cursor \
  -V PROJECT_NAME=custom-app \
  -V API_URL=https://api.prod.com
```

### What are MCP servers?

Model Context Protocol (MCP) servers extend your AI assistant with external tools:

- **Filesystem** - Read/write files
- **GitHub** - Access repositories
- **Database** - Query PostgreSQL, etc.
- **APIs** - Slack, Jira, etc.

Example:
```yaml
mcp_servers:
  - name: github
    command: npx
    args: ["-y", "@modelcontextprotocol/server-github"]
    env:
      GITHUB_TOKEN: "{{{ GITHUB_TOKEN }}}"
```

See [MCP Server Example](../examples/plugins/mcp-servers.md).

## Usage

### How do I generate editor configurations?

```bash
# For specific editor
promptrek generate project.promptrek.yaml --editor cursor

# For all configured editors
promptrek generate project.promptrek.yaml --all
```

Generated files appear in editor-specific locations:
- Copilot: `.github/copilot-instructions.md`
- Cursor: `.cursor/rules/index.mdc`
- Claude: `.claude/CLAUDE.md`
- etc.

### Should I commit generated files to git?

**No!** Generated files should not be committed. They should be generated locally by each team member.

PrompTrek automatically:
- Adds generated files to `.gitignore`
- Provides pre-commit hooks to prevent accidental commits

```bash
# Set up .gitignore
promptrek config-ignores
```

### Can I have different configurations per directory?

**Path-specific rules** are supported in some editors:

**GitHub Copilot:**
```bash
# Create path-specific instruction
promptrek generate --editor copilot \
  --path src/components \
  --output .github/instructions/components.instructions.md
```

**Cursor:**
Use `documents` with `file_globs`:
```yaml
documents:
  - name: components
    content: "Component guidelines..."
    file_globs: "src/components/**/*.tsx"
    always_apply: false
```

### How do I validate my configuration?

```bash
# Validate syntax and structure
promptrek validate project.promptrek.yaml

# Strict validation
promptrek validate project.promptrek.yaml --strict
```

Validation checks:
- YAML syntax
- Schema compliance
- Required fields
- Variable references

### Can I preview without generating files?

Yes!

```bash
promptrek preview project.promptrek.yaml --editor cursor
```

Shows what would be generated without writing files.

## Plugins & Extensions

### How do I add custom commands?

Define in `commands` section:

```yaml
commands:
  - name: review-code
    description: "Review code quality"
    prompt: |
      Review this code for:
      - Code quality
      - Security
      - Performance
```

Use in editor:
```
/review-code
```

See [Custom Commands Example](../examples/plugins/custom-commands.md).

### Are agents supported?

Yes, in schema v3.0+:

```yaml
agents:
  - name: test-generator
    prompt: "Generate comprehensive tests"
    tools: [file_read, file_write]
    trust_level: partial
```

Generated as:
- Claude: `.claude/agents/*.md`
- Cursor: `AGENTS.md`

### Can I create custom MCP servers?

Yes! Point to your custom server:

```yaml
mcp_servers:
  - name: custom
    command: node
    args: ["/path/to/your/server.js"]
    env:
      API_KEY: "{{{ YOUR_API_KEY }}}"
```

See [MCP Specification](https://modelcontextprotocol.io/) for creating servers.

## Troubleshooting

### Why aren't my generated files updating?

**Solutions:**
1. Delete old files and regenerate:
   ```bash
   rm -rf .cursor/ .github/copilot-instructions.md
   promptrek generate config.yaml --all
   ```

2. Check for validation errors:
   ```bash
   promptrek validate config.yaml
   ```

3. Verify file paths in output

### Variables aren't substituting

**Problem:** `{{{ VAR }}}` appears literally in output

**Solutions:**
1. Check syntax: use triple braces `{{{ VAR }}}`
2. Ensure variable is defined in `variables` section
3. Check spelling matches exactly

### Editor isn't loading my configuration

**By Editor:**

**Copilot:**
- Check `.github/copilot-instructions.md` exists
- Restart VSCode
- Check Copilot extension is enabled

**Cursor:**
- Check `.cursor/rules/index.mdc` exists
- Restart Cursor
- Check rules are enabled in settings

**Claude:**
- Check `.claude/CLAUDE.md` exists
- Restart Claude Code
- Check project is opened correctly

### Getting deprecation warnings

See [Deprecation Guide](deprecation.md) for handling warnings.

**Quick fix:**
```bash
promptrek migrate config.yaml --in-place
```

## Best Practices

### How should I organize my configuration?

**Small Projects:**
Single `project.promptrek.yaml` at root

**Large Projects/Monorepos:**
Use multi-document configuration:

```yaml
# General guidelines
content: |
  # General Guidelines

# Path-specific documents
documents:
  - name: frontend
    content: "Frontend guidelines..."
    file_globs: "apps/web/**/*"

  - name: backend
    content: "Backend guidelines..."
    file_globs: "apps/api/**/*"
```

### Should I share configurations across projects?

**Within a team:** Yes! Store in version control.

**Across different project types:** Create templates:

```
.promptrek-templates/
  react-project.promptrek.yaml
  node-api.promptrek.yaml
  monorepo.promptrek.yaml
```

Copy and customize for new projects.

### How do I handle secrets?

**Never commit secrets!** Use variables:

```yaml
variables:
  GITHUB_TOKEN: "{{{ GITHUB_TOKEN }}}"  # Placeholder
```

**Set at generation time:**
```bash
export GITHUB_TOKEN="ghp_real_token"
promptrek generate config.yaml --editor claude
```

Or override:
```bash
promptrek generate config.yaml --editor claude \
  -V GITHUB_TOKEN=ghp_real_token
```

### Should I use pre-commit hooks?

Yes! Pre-commit hooks:
- Validate `.promptrek.yaml` files
- Prevent committing generated files
- Ensure consistency

```bash
promptrek install-hooks --activate
```

## Integration & Advanced

### Can I use PrompTrek in CI/CD?

Yes!

```yaml
# .github/workflows/validate.yml
name: Validate PrompTrek Config
on: [push, pull_request]
jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - run: pip install -e .
      - run: promptrek validate project.promptrek.yaml --strict
```

### Can I programmatically generate configurations?

Yes! PrompTrek is built with Python. You can:

```python
from promptrek.core.parser import UPFParser
from promptrek.adapters import get_adapter

# Parse configuration
parser = UPFParser()
prompt = parser.parse_file("config.yaml")

# Generate for editor
adapter = get_adapter("cursor")
adapter.generate(prompt, output_dir=".")
```

### How do I contribute to PrompTrek?

See [Contributing Guide](../community/contributing.md):

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

We welcome:
- Bug fixes
- New editor adapters
- Documentation improvements
- Examples

## Getting Help

### Where can I get help?

- **Documentation:** [flamingquaks.github.io/promptrek](https://flamingquaks.github.io/promptrek)
- **GitHub Issues:** [Report bugs](https://github.com/flamingquaks/promptrek/issues)
- **GitHub Discussions:** [Ask questions](https://github.com/flamingquaks/promptrek/discussions)
- **Troubleshooting:** [Common issues](troubleshooting.md)

### How do I report a bug?

1. Check [existing issues](https://github.com/flamingquaks/promptrek/issues)
2. Create new issue with:
   - PrompTrek version (`promptrek --version`)
   - Python version
   - Operating system
   - Steps to reproduce
   - Expected vs actual behavior
   - Error messages

### Can I request a feature?

Yes! [Create a feature request](https://github.com/flamingquaks/promptrek/issues/new?template=feature_request.yml) with:
- Use case description
- Proposed solution
- Benefits
- Example configuration (if applicable)

## Additional Resources

- **[Examples](../examples/index.md)** - Real-world configurations
- **[User Guide](../user-guide/index.md)** - Complete documentation
- **[Troubleshooting](troubleshooting.md)** - Common issues and solutions
- **[Glossary](glossary.md)** - Terms and definitions
- **[Changelog](changelog.md)** - Version history

---

**Still have questions?** Join our [GitHub Discussions](https://github.com/flamingquaks/promptrek/discussions)!
