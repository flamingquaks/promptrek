# Troubleshooting

Common issues and their solutions when using PrompTrek.

## Installation Issues

### Python Version Errors

**Problem:** `Python 3.8 is not supported` or similar version errors

**Solution:**
PrompTrek requires Python 3.9 or higher.

```bash
# Check your Python version
python --version

# Install Python 3.9+ if needed
# On Ubuntu/Debian:
sudo apt-get install python3.11

# On macOS with Homebrew:
brew install python@3.11
```

### Dependencies Not Installing

**Problem:** `pip install` fails with dependency errors

**Solution 1:** Use uv (recommended):
```bash
# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install PrompTrek
cd promptrek
uv sync
```

**Solution 2:** Update pip:
```bash
pip install --upgrade pip
pip install -e .
```

**Solution 3:** Clear pip cache:
```bash
pip cache purge
pip install -e .
```

### Command Not Found After Installation

**Problem:** `promptrek: command not found`

**Solutions:**

**If installed with pip:**
```bash
# Check if in PATH
which promptrek

# Or use full path
python -m promptrek --help

# Add to PATH (bash)
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

**If installed with uv:**
```bash
# Use uv run
uv run promptrek --help

# Or activate virtual environment
source .venv/bin/activate
promptrek --help
```

## Configuration Issues

### YAML Syntax Errors

**Problem:** `YAML syntax error at line X`

**Common Issues:**

**1. Indentation (use spaces, not tabs):**
```yaml
# ❌ Wrong (mixed spaces/tabs)
metadata:
	title: "My Project"

# ✅ Correct (consistent spaces)
metadata:
  title: "My Project"
```

**2. Missing colons:**
```yaml
# ❌ Wrong
metadata
  title "My Project"

# ✅ Correct
metadata:
  title: "My Project"
```

**3. String quoting:**
```yaml
# ❌ Wrong (special characters need quotes)
content: This: has: colons

# ✅ Correct
content: "This: has: colons"

# ✅ Best (use block scalar for multi-line)
content: |
  This can have: any: characters
```

**Validate syntax:**
```bash
# Check YAML syntax
promptrek validate config.yaml

# Use online validator
cat config.yaml | python -c 'import yaml, sys; yaml.safe_load(sys.stdin)'
```

### Schema Validation Errors

**Problem:** `Invalid schema version` or `Required field missing`

**Solution:**

**Check schema version:**
```yaml
# Use correct schema version
schema_version: "3.1.0"  # Not "v3.1.0" or "3.1"
```

**Check required fields:**
```yaml
# Minimum valid configuration
schema_version: "3.1.0"
metadata:
  title: "My Project"       # Required
  description: "..."        # Required
content: |                  # Required
  # Guidelines here
```

**Use strict validation:**
```bash
promptrek validate config.yaml --strict
```

### Variable Substitution Not Working

**Problem:** Variables appear as `{{{ VAR }}}` literally in output

**Solutions:**

**1. Check syntax (triple braces):**
```yaml
# ❌ Wrong
content: "Project: {{ PROJECT_NAME }}"  # Double braces

# ✅ Correct
content: "Project: {{{ PROJECT_NAME }}}"  # Triple braces
```

**2. Ensure variable is defined:**
```yaml
variables:
  PROJECT_NAME: "my-project"  # Must be defined

content: |
  Project: {{{ PROJECT_NAME }}}  # Now works
```

**3. Check variable name matches:**
```yaml
variables:
  PROJECT_NAME: "my-project"  # Defined

content: |
  Project: {{{ project_name }}}  # ❌ Wrong case
  Project: {{{ PROJECT_NAME }}}  # ✅ Correct
```

**4. Override at generation time:**
```bash
promptrek generate config.yaml --editor cursor \
  -V PROJECT_NAME="custom-name"
```

### Deprecation Warnings

**Problem:** `DEPRECATION WARNING: nested plugin structure...`

**Solution:**

**Quick fix (migrate):**
```bash
promptrek migrate config.yaml --in-place
```

**Manual fix:**
```yaml
# ❌ Old (v2.x)
schema_version: "2.1.0"
plugins:
  mcp_servers: [...]

# ✅ New (v3.0+)
schema_version: "3.1.0"
mcp_servers: [...]  # Top-level
```

See [Deprecation Guide](deprecation.md) for details.

## Generation Issues

### Generated Files Not Updating

**Problem:** Changes to config don't appear in generated files

**Solutions:**

**1. Delete and regenerate:**
```bash
# Remove old files
rm -rf .cursor/
rm .github/copilot-instructions.md
rm -rf .claude/

# Regenerate
promptrek generate config.yaml --all
```

**2. Check for errors:**
```bash
# Validate first
promptrek validate config.yaml

# Generate with verbose output
promptrek generate config.yaml --editor cursor -v
```

**3. Check file permissions:**
```bash
# Ensure output directory is writable
ls -la .cursor/
chmod -R u+w .cursor/
```

### No Files Generated

**Problem:** `promptrek generate` completes but no files appear

**Solutions:**

**1. Check output location:**
```bash
# List generated files
ls -R .cursor/ .github/ .claude/

# Check current directory
pwd
```

**2. Run with verbose flag:**
```bash
promptrek generate config.yaml --editor cursor -v
```

**3. Try preview mode:**
```bash
# See what would be generated
promptrek preview config.yaml --editor cursor
```

**4. Check editor adapter:**
```bash
# List available editors
promptrek list-editors

# Verify adapter exists
promptrek list-editors | grep cursor
```

### Wrong Content in Generated Files

**Problem:** Generated files don't match configuration

**Solutions:**

**1. Check variable substitution:**
```bash
# Use preview to see final output
promptrek preview config.yaml --editor cursor
```

**2. Verify schema version:**
```bash
head -1 config.yaml
# Should be: schema_version: "3.1.0"
```

**3. Check for multiple config files:**
```bash
# Ensure you're using the right file
find . -name "*.promptrek.yaml"
```

## Editor-Specific Issues

### GitHub Copilot

**Problem:** Copilot doesn't use instructions

**Solutions:**

**1. Check file location:**
```bash
ls -la .github/copilot-instructions.md
```

**2. Restart VSCode:**
- Close all VSCode windows
- Reopen project
- Check Copilot extension is enabled

**3. Check Copilot settings:**
```
VSCode → Settings → Copilot
Enable: "Use Instruction Files"
```

**4. Verify GitHub authentication:**
- Check Copilot is activated
- Sign out and sign in again

### Cursor

**Problem:** Cursor doesn't load rules

**Solutions:**

**1. Check files:**
```bash
ls -la .cursor/rules/index.mdc
cat .cursor/rules/index.mdc
```

**2. Check metadata:**
```yaml
# index.mdc should have frontmatter
---
alwaysApply: true
---

# Rest of content...
```

**3. Restart Cursor:**
- Close completely
- Clear cache: `rm -rf ~/.cursor/Cache`
- Reopen project

**4. Enable rules in settings:**
```
Cursor → Settings → Features → Rules
✓ Enable Rules
```

### Claude Code

**Problem:** Claude doesn't see context or MCP servers

**Solutions:**

**1. Check files:**
```bash
ls -la .claude/CLAUDE.md
ls -la .mcp.json
cat .mcp.json
```

**2. Verify MCP server config:**
```json
{
  "mcpServers": {
    "server-name": {
      "command": "npx",
      "args": [...]
    }
  }
}
```

**3. Check environment variables:**
```bash
# For MCP servers with env vars
echo $GITHUB_TOKEN
```

**4. Restart Claude Code:**
- Close completely
- Reopen project
- Check status bar for MCP servers

### Continue

**Problem:** Continue doesn't load config

**Solutions:**

**1. Check config location:**
```bash
ls -la .continue/config.json
cat .continue/config.json
```

**2. Verify JSON syntax:**
```bash
cat .continue/config.json | python -m json.tool
```

**3. Restart VSCode:**
- Reload window: `Ctrl+Shift+P` → "Reload Window"

**4. Check Continue extension:**
- Ensure extension is enabled
- Update to latest version

## Plugin Issues

### MCP Servers Not Loading

**Problem:** MCP server doesn't appear in editor

**Solutions:**

**1. Check file location:**
```bash
# Claude Code
cat .mcp.json

# Cursor
cat .cursor/mcp.json

# Cline
cat .vscode/settings.json | grep mcp
```

**2. Verify command exists:**
```bash
# Test npx command
npx -y @modelcontextprotocol/server-github --help

# Or check Node.js
which node
which npx
```

**3. Check environment variables:**
```bash
# For servers requiring auth
echo $GITHUB_TOKEN
echo $DATABASE_URL
```

**4. Test server manually:**
```bash
# Run server command directly
npx -y @modelcontextprotocol/server-github
```

**5. Check JSON syntax:**
```bash
cat .mcp.json | python -m json.tool
```

### Custom Commands Not Working

**Problem:** `/command-name` doesn't appear or work

**Solutions:**

**1. Check generated files:**
```bash
# Claude Code
ls -la .claude/commands/
cat .claude/commands/command-name.md

# Continue
cat .continue/config.json | grep -A 10 slashCommands
```

**2. Verify command name:**
```yaml
# Use kebab-case
commands:
  - name: review-code  # ✅ Correct
  # NOT: reviewCode, review_code
```

**3. Restart editor:**
- Commands may not load until restart

**4. Check editor support:**
- Claude Code: Full support
- Continue: Full support
- Cursor: Limited support
- Others: May not support custom commands

## Pre-commit Hook Issues

### Hooks Not Running

**Problem:** Pre-commit hooks don't execute on commit

**Solutions:**

**1. Check installation:**
```bash
# Install pre-commit
pip install pre-commit

# Install hooks
pre-commit install

# Verify
ls -la .git/hooks/pre-commit
```

**2. Run manually:**
```bash
# Test hooks
pre-commit run --all-files

# See which hooks are configured
pre-commit run --help
```

**3. Check .pre-commit-config.yaml:**
```bash
cat .pre-commit-config.yaml
```

### Hook Failures

**Problem:** Pre-commit hooks fail and block commits

**Solutions:**

**1. See what failed:**
```bash
pre-commit run --all-files
```

**2. Fix validation errors:**
```bash
# Validate config
promptrek validate *.promptrek.yaml

# Fix YAML syntax
```

**3. Update hooks:**
```bash
pre-commit autoupdate
pre-commit install
```

**4. Skip hooks (temporary):**
```bash
git commit --no-verify -m "message"
```

!!! warning
    Only skip hooks if you know what you're doing!

## Performance Issues

### Slow Generation

**Problem:** `promptrek generate` takes a long time

**Solutions:**

**1. Check file size:**
```bash
wc -l config.yaml
# If >1000 lines, consider splitting
```

**2. Use specific editor:**
```bash
# Don't use --all if you only need one
promptrek generate config.yaml --editor cursor
```

**3. Check disk space:**
```bash
df -h .
```

**4. Profile with verbose:**
```bash
promptrek generate config.yaml --editor cursor -v
```

### Large Generated Files

**Problem:** Generated files are excessively large

**Solutions:**

**1. Review content length:**
```yaml
# Keep content focused
content: |
  # Only essential guidelines
  - Key principle 1
  - Key principle 2
  # Not a 100-page manual
```

**2. Use documents for specifics:**
```yaml
# General guidelines in content
content: |
  # General guidelines

# Specific guidelines in documents
documents:
  - name: typescript
    content: "TypeScript specifics..."
    file_globs: "**/*.ts"
```

**3. Remove duplication:**
- Extract common patterns to variables
- Reference external docs instead of copying

## Getting More Help

### Enable Debug Logging

```bash
# Set debug level
export PROMPTREK_LOG_LEVEL=DEBUG

# Run command
promptrek generate config.yaml --editor cursor -v
```

### Collect Diagnostic Info

```bash
# System info
python --version
pip --version
uv --version

# PrompTrek version
promptrek --version

# Validate config
promptrek validate config.yaml --strict

# List editors
promptrek list-editors
```

### Report a Bug

If you can't resolve the issue:

1. **Check existing issues:** [GitHub Issues](https://github.com/flamingquaks/promptrek/issues)

2. **Create new issue** with:
   - PrompTrek version
   - Python version
   - Operating system
   - Steps to reproduce
   - Error messages
   - Configuration file (sanitized)

3. **Include output:**
   ```bash
   promptrek validate config.yaml 2>&1 | tee debug.log
   ```

## Additional Resources

- **[FAQ](faq.md)** - Frequently asked questions
- **[Deprecation Guide](deprecation.md)** - Handling warnings
- **[Examples](../examples/index.md)** - Working configurations
- **[GitHub Issues](https://github.com/flamingquaks/promptrek/issues)** - Report bugs
- **[GitHub Discussions](https://github.com/flamingquaks/promptrek/discussions)** - Ask questions

---

**Still stuck?** Ask for help on [GitHub Discussions](https://github.com/flamingquaks/promptrek/discussions)!
