# Dynamic Variables Example

This example demonstrates PrompTrek's dynamic variables feature, which allows you to use:
- **Built-in dynamic variables** (date/time, project context, git info)
- **User-defined command-based variables** that execute shell commands

## Features Demonstrated

### 1. Built-in Dynamic Variables
These are always available and require no configuration:

| Variable | Description | Example Value |
|----------|-------------|---------------|
| `{{{ CURRENT_DATE }}}` | Current date (YYYY-MM-DD) | `2025-10-26` |
| `{{{ CURRENT_TIME }}}` | Current time (HH:MM:SS) | `14:30:45` |
| `{{{ CURRENT_DATETIME }}}` | ISO 8601 datetime | `2025-10-26T14:30:45Z` |
| `{{{ CURRENT_YEAR }}}` | Current year | `2025` |
| `{{{ CURRENT_MONTH }}}` | Current month (01-12) | `10` |
| `{{{ CURRENT_DAY }}}` | Current day (01-31) | `26` |
| `{{{ PROJECT_NAME }}}` | Current directory name | `promptrek` |
| `{{{ PROJECT_ROOT }}}` | Absolute path to project | `/home/user/promptrek` |
| `{{{ GIT_BRANCH }}}` | Git branch name | `main` |
| `{{{ GIT_COMMIT_SHORT }}}` | Short commit hash | `abc1234` |

### 2. User-Defined Dynamic Variables
Defined in `.promptrek/variables.promptrek.yaml` with shell commands:

```yaml
BUILD_ID:
  type: command
  value: uuidgen
  cache: true  # Evaluate once and cache

PYTHON_LOC:
  type: command
  value: find . -name "*.py" -type f -exec wc -l {} + | tail -1 | awk '{print $1}'
  cache: false  # Re-evaluate each time
```

## Usage

### Initial Generation
1. Enable command execution in `project.promptrek.yaml`:
   ```yaml
   allow_commands: true
   ```

2. Generate editor files:
   ```bash
   promptrek generate project.promptrek.yaml --editor claude --all
   ```

3. Variables will be evaluated and substituted in the generated files.

### Refresh with Updated Variables
When you want to update dynamic variables (e.g., to get today's date):

```bash
promptrek refresh
```

This regenerates the editor files using the same settings but with fresh variable values.

### Refresh Options
```bash
# Refresh all editors from last generation
promptrek refresh

# Refresh specific editor
promptrek refresh --editor claude

# Clear cached variables before refreshing
promptrek refresh --clear-cache

# Preview changes without writing files
promptrek refresh --dry-run
```

## Security Considerations

⚠️ **Important**: Command-based variables execute shell commands on your system.

- Only enable `allow_commands: true` if you trust the commands
- Review all commands in `.promptrek/variables.promptrek.yaml`
- PrompTrek will show a security warning on first use
- Commands have a 5-second timeout limit
- Failed commands are logged but don't stop generation

## File Structure

```
examples/dynamic-variables/
├── project.promptrek.yaml          # Main UPF file with allow_commands
├── .promptrek/
│   └── variables.promptrek.yaml    # User-defined variables
└── README.md                        # This file
```

## Tips

1. **Use built-in variables when possible** - They're faster and safer
2. **Cache expensive operations** - Set `cache: true` for commands that don't change
3. **Keep commands simple** - Complex logic should be in scripts
4. **Test commands first** - Run them in your shell to verify output
5. **Use for automation** - Great for build IDs, timestamps, CI/CD info

## Use Cases

- **Date-stamped documentation**: Automatically update "Last modified" dates
- **Build identifiers**: Generate unique IDs for each build
- **Git context**: Include branch and commit info in prompts
- **Environment info**: Show current user, hostname, etc.
- **Dynamic metrics**: Include project stats (LOC, file counts, etc.)

## Learn More

- [Dynamic Variables Documentation](../../docs/variables.md)
- [Security Best Practices](../../docs/security.md)
- [PrompTrek CLI Reference](../../docs/cli.md)
