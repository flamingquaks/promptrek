# Variables System Documentation

PrompTrek's variable system enables dynamic, reusable prompts through template substitution. Variables make your prompt files flexible and environment-agnostic.

## Overview

Variables in PrompTrek:

- **Define once, use anywhere**: Set variables and reference them throughout your configuration
- **Multiple sources**: Built-in, file-based, prompt-defined, and CLI override variables
- **Secure secrets**: Separate sensitive data from committed configuration
- **Environment flexibility**: Different values for dev, staging, production
- **Triple-brace syntax**: Use `{{{ VARIABLE_NAME }}}` for substitution

## Variable Syntax

### Basic Syntax

```yaml
variables:
  PROJECT_NAME: "My Application"
  VERSION: "1.0.0"

content: |
  # {{{ PROJECT_NAME }}} v{{{ VERSION }}}
```

**Result**:
```markdown
# My Application v1.0.0
```

### Triple Braces

PrompTrek uses **triple braces** `{{{ }}}` to distinguish from editor-specific templating:

```yaml
variables:
  API_KEY: "secret-key-123"

mcp_servers:
  - name: api-server
    env:
      API_KEY: "{{{ API_KEY }}}"        # PrompTrek variable
```

!!! warning "Syntax Required"
    Always use `{{{ VARIABLE_NAME }}}` with **three braces**. Single `{VAR}` or double `{{VAR}}` won't work.

## Variable Sources

Variables are evaluated in order of precedence (lowest to highest):

### 1. Built-in Variables (Lowest Priority)

Always available without configuration:

```yaml
content: |
  Generated on: {{{ CURRENT_DATE }}}
  Year: {{{ CURRENT_YEAR }}}
  Month: {{{ CURRENT_MONTH }}}
  Time: {{{ CURRENT_TIME }}}
```

**Built-in variables**:

- `CURRENT_DATE`: Current date (`YYYY-MM-DD`)
- `CURRENT_YEAR`: Current year (`YYYY`)
- `CURRENT_MONTH`: Current month name (`January`, etc.)
- `CURRENT_TIME`: Current time (`HH:MM:SS`)
- `CURRENT_DATETIME`: Date and time combined

### 2. Local Variables File

Stored in `.promptrek/variables.promptrek.yaml` (gitignored by default):

```yaml
# .promptrek/variables.promptrek.yaml
GITHUB_TOKEN: "ghp_YourPersonalToken123"
OPENAI_API_KEY: "sk-YourOpenAIKey456"
DATABASE_PASSWORD: "dev-password-789"
```

**Purpose**: Store user-specific or sensitive values that shouldn't be committed.

### 3. Prompt File Variables

Defined in your `.promptrek.yaml` file:

```yaml
# project.promptrek.yaml
variables:
  PROJECT_NAME: "E-Commerce Platform"
  NODE_VERSION: "20"
  ENVIRONMENT: "development"
```

**Purpose**: Project-wide defaults that can be committed safely.

### 4. CLI Override Variables (Highest Priority)

Passed via command-line with `-V` or `--var`:

```bash
promptrek generate --editor claude \
  -V ENVIRONMENT=production \
  -V VERSION=2.0.0
```

**Purpose**: Runtime overrides for different environments or deployments.

## Variable Precedence Example

```yaml
# project.promptrek.yaml
variables:
  ENVIRONMENT: "development"      # Priority 3: Prompt file
  VERSION: "1.0.0"

content: |
  Environment: {{{ ENVIRONMENT }}}
  Version: {{{ VERSION }}}
  Date: {{{ CURRENT_DATE }}}      # Priority 1: Built-in
```

```yaml
# .promptrek/variables.promptrek.yaml
ENVIRONMENT: "staging"            # Priority 2: Local file (overrides prompt file)
```

```bash
# CLI override (Priority 4: Highest)
promptrek generate --editor claude \
  -V ENVIRONMENT=production       # Overrides all other sources
```

**Final result**:
```markdown
Environment: production           # CLI override wins
Version: 1.0.0                   # From prompt file
Date: 2024-01-15                 # Built-in variable
```

## Common Use Cases

### Secrets Management

Keep secrets out of version control:

```yaml
# project.promptrek.yaml (committed)
variables:
  PROJECT_NAME: "My App"
  # Don't put secrets here!

mcp_servers:
  - name: github
    env:
      GITHUB_TOKEN: "{{{ GITHUB_TOKEN }}}"  # References local variable
```

```yaml
# .promptrek/variables.promptrek.yaml (gitignored)
GITHUB_TOKEN: "ghp_ActualTokenHere123"
OPENAI_API_KEY: "sk-ActualKeyHere456"
DATABASE_URL: "postgresql://user:pass@localhost/db"
```

### Environment-Specific Configuration

```yaml
# project.promptrek.yaml
variables:
  ENVIRONMENT: "development"
  API_URL: "http://localhost:3000"
  LOG_LEVEL: "debug"

content: |
  # Configuration for {{{ ENVIRONMENT }}}

  API Endpoint: {{{ API_URL }}}
  Log Level: {{{ LOG_LEVEL }}}
```

**Development**:
```bash
promptrek generate --editor claude
# Uses defaults: development, localhost, debug
```

**Production**:
```bash
promptrek generate --editor claude \
  -V ENVIRONMENT=production \
  -V API_URL=https://api.example.com \
  -V LOG_LEVEL=error
```

### Version Management

```yaml
# project.promptrek.yaml
variables:
  VERSION: "1.0.0"
  BUILD_DATE: "{{{ CURRENT_DATE }}}"

metadata:
  version: "{{{ VERSION }}}"

content: |
  # Project v{{{ VERSION }}}

  Built on: {{{ BUILD_DATE }}}

  ## Version Information
  - Release: {{{ VERSION }}}
  - Build Date: {{{ BUILD_DATE }}}
```

### Team Member Customization

Each team member maintains their own local variables:

```yaml
# .promptrek/variables.promptrek.yaml (Alice's machine)
AUTHOR_NAME: "Alice Johnson"
AUTHOR_EMAIL: "alice@example.com"
GITHUB_USERNAME: "alice-dev"
```

```yaml
# .promptrek/variables.promptrek.yaml (Bob's machine)
AUTHOR_NAME: "Bob Smith"
AUTHOR_EMAIL: "bob@example.com"
GITHUB_USERNAME: "bob-codes"
```

```yaml
# project.promptrek.yaml (shared/committed)
content: |
  Author: {{{ AUTHOR_NAME }}} <{{{ AUTHOR_EMAIL }}}>
  GitHub: https://github.com/{{{ GITHUB_USERNAME }}}
```

## Variable Best Practices

### Naming Conventions

!!! tip "Variable Naming"
    - Use UPPER_CASE_SNAKE_CASE
    - Be descriptive but concise
    - Use prefixes for grouping (e.g., `DB_*`, `API_*`)

```yaml
# Good naming
variables:
  PROJECT_NAME: "My App"
  API_BASE_URL: "https://api.example.com"
  DB_HOST: "localhost"
  DB_PORT: "5432"
  LOG_LEVEL: "info"

# Avoid
variables:
  name: "My App"              # Not uppercase
  url: "https://api.com"      # Too vague
  apiBaseURL: "https://..."   # Not snake_case
```

### Grouped Variables

Organize related variables with prefixes:

```yaml
variables:
  # Project
  PROJECT_NAME: "E-Commerce Platform"
  PROJECT_VERSION: "2.1.0"

  # API
  API_BASE_URL: "https://api.example.com"
  API_TIMEOUT: "30000"
  API_RETRY_COUNT: "3"

  # Database
  DB_HOST: "localhost"
  DB_PORT: "5432"
  DB_NAME: "ecommerce"

  # Feature Flags
  FEATURE_BETA_UI: "false"
  FEATURE_NEW_CHECKOUT: "true"
```

### Default Values

Provide sensible defaults in prompt file:

```yaml
# project.promptrek.yaml
variables:
  ENVIRONMENT: "development"     # Safe default
  LOG_LEVEL: "info"             # Safe default
  DEBUG_MODE: "false"           # Safe default

  # Secrets - no defaults (must be in local file)
  # GITHUB_TOKEN: ""             # Don't do this
  # API_KEY: ""                  # Don't do this
```

### Secret Variables

Keep secrets in local file only:

```yaml
# .promptrek/variables.promptrek.yaml (NEVER commit)
GITHUB_TOKEN: "ghp_..."
OPENAI_API_KEY: "sk-..."
DATABASE_PASSWORD: "..."
AWS_ACCESS_KEY: "..."
```

Ensure `.gitignore` includes:

```gitignore
# Secrets
.promptrek/variables.promptrek.yaml
variables.promptrek.yaml
```

## Variable Validation

### Check Variable Usage

Validate variables are defined:

```bash
promptrek validate project.promptrek.yaml
```

If you reference undefined variables, you'll see warnings:

```
⚠️  Warning: Variable 'UNDEFINED_VAR' is used but not defined
```

### List Variables

View all variables that will be used:

```bash
# Preview shows variable substitution
promptrek preview project.promptrek.yaml --editor claude

# Verbose mode shows variable resolution
promptrek --verbose generate --editor claude
```

## Advanced Variable Features

### Nested Variables

Variables can reference other variables:

```yaml
variables:
  PROJECT_NAME: "My App"
  PROJECT_VERSION: "1.0.0"
  FULL_NAME: "{{{ PROJECT_NAME }}} v{{{ PROJECT_VERSION }}}"

content: |
  Welcome to {{{ FULL_NAME }}}
```

### Conditional Content

Use variables for conditional sections:

```yaml
variables:
  INCLUDE_TESTING: "true"
  INCLUDE_DOCKER: "false"

content: |
  # Project Guidelines

  ## Development
  Follow best practices...

  {{% if INCLUDE_TESTING == "true" %}}
  ## Testing
  Run tests with: npm test
  {{% endif %}}

  {{% if INCLUDE_DOCKER == "true" %}}
  ## Docker
  Build with: docker build .
  {{% endif %}}
```

!!! note "Template Syntax"
    Advanced conditional syntax may vary by editor adapter. Check adapter-specific documentation.

### Environment Files

Load variables from environment files:

```bash
# .env file
export GITHUB_TOKEN="ghp_..."
export API_KEY="sk-..."

# Load and generate
source .env
promptrek generate --editor claude \
  -V GITHUB_TOKEN="$GITHUB_TOKEN" \
  -V API_KEY="$API_KEY"
```

## Troubleshooting

### Variable Not Substituted

**Problem**: Variable appears as `{{{ VAR_NAME }}}` in output

**Solutions**:

1. Check syntax - must be triple braces
2. Verify variable is defined
3. Check variable name spelling (case-sensitive)
4. Run validation: `promptrek validate`

```yaml
# Wrong
content: "Version: {{ VERSION }}"     # Double braces
content: "Version: {VERSION}"         # Single braces
content: "Version: ${VERSION}"        # Dollar sign

# Correct
content: "Version: {{{ VERSION }}}"   # Triple braces
```

### Undefined Variable

**Problem**: Warning about undefined variable

**Solution**: Define in one of the variable sources

```yaml
# Option 1: Add to prompt file
variables:
  MISSING_VAR: "value"

# Option 2: Add to local file
# .promptrek/variables.promptrek.yaml
MISSING_VAR: "value"

# Option 3: Pass via CLI
promptrek generate -V MISSING_VAR=value --editor claude
```

### Secret Accidentally Committed

**Problem**: Committed secrets to git

**Solution**: Remove from history and use local file

```bash
# 1. Remove from current version
git rm --cached .promptrek/variables.promptrek.yaml

# 2. Add to .gitignore
echo ".promptrek/variables.promptrek.yaml" >> .gitignore

# 3. Rewrite history (if recently committed)
git filter-branch --force --index-filter \
  "git rm --cached --ignore-unmatch .promptrek/variables.promptrek.yaml" \
  --prune-empty --tag-name-filter cat -- --all

# 4. Rotate compromised secrets!
```

## Examples

### Complete Variable Setup

```yaml
# project.promptrek.yaml (committed)
schema_version: "3.1.0"

metadata:
  title: "{{{ PROJECT_NAME }}}"
  version: "{{{ VERSION }}}"

variables:
  # Project info (safe to commit)
  PROJECT_NAME: "E-Commerce API"
  VERSION: "2.1.0"
  ENVIRONMENT: "development"

  # Build info
  BUILD_DATE: "{{{ CURRENT_DATE }}}"
  BUILD_YEAR: "{{{ CURRENT_YEAR }}}"

content: |
  # {{{ PROJECT_NAME }}} v{{{ VERSION }}}

  Environment: {{{ ENVIRONMENT }}}
  Built: {{{ BUILD_DATE }}}

mcp_servers:
  - name: github
    env:
      GITHUB_TOKEN: "{{{ GITHUB_TOKEN }}}"  # From local file

  - name: openai
    env:
      OPENAI_API_KEY: "{{{ OPENAI_API_KEY }}}"  # From local file
```

```yaml
# .promptrek/variables.promptrek.yaml (gitignored)
GITHUB_TOKEN: "ghp_YourActualTokenHere123"
OPENAI_API_KEY: "sk-YourActualKeyHere456"
```

```bash
# Generate for production
promptrek generate --editor claude \
  -V ENVIRONMENT=production \
  -V VERSION=2.1.0
```

## See Also

- [Advanced Variables](../advanced/variables.md) - Advanced variable techniques
- [Schema v3.1.0](schema-v3.1.md) - Variable support in schema
- [Templates](../advanced/templates.md) - Template patterns and best practices
- [CLI Generate Command](../../cli/commands/generate.md) - Variable overrides
