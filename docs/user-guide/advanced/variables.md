# Advanced Variable Usage

Learn advanced techniques for using PrompTrek's variable system to create dynamic, flexible configurations.

## Overview

Beyond basic variable substitution, PrompTrek supports advanced patterns including nested variables, conditional content, environment-specific configurations, and secure secret management.

## Nested Variables

Variables can reference other variables:

```yaml
variables:
  PROJECT_NAME: "E-Commerce"
  PROJECT_VERSION: "2.1.0"
  FULL_TITLE: "{{{ PROJECT_NAME }}} v{{{ PROJECT_VERSION }}}"
  PROJECT_SLUG: "ecommerce-v2"

content: |
  # {{{ FULL_TITLE }}}

  Welcome to {{{ FULL_TITLE }}}!
```

**Result**:
```markdown
# E-Commerce v2.1.0

Welcome to E-Commerce v2.1.0!
```

## Environment-Specific Variables

### Using CLI Overrides

```yaml
# project.promptrek.yaml
variables:
  ENVIRONMENT: "development"
  API_URL: "http://localhost:3000"
  LOG_LEVEL: "debug"
  FEATURES_BETA: "true"

content: |
  Environment: {{{ ENVIRONMENT }}}
  API: {{{ API_URL }}}
  Logging: {{{ LOG_LEVEL }}}
  Beta Features: {{{ FEATURES_BETA }}}
```

**Development**:
```bash
promptrek generate --editor claude
# Uses defaults
```

**Staging**:
```bash
promptrek generate --editor claude \
  -V ENVIRONMENT=staging \
  -V API_URL=https://staging-api.example.com \
  -V LOG_LEVEL=info \
  -V FEATURES_BETA=true
```

**Production**:
```bash
promptrek generate --editor claude \
  -V ENVIRONMENT=production \
  -V API_URL=https://api.example.com \
  -V LOG_LEVEL=error \
  -V FEATURES_BETA=false
```

### Environment Files

Create separate variable files:

```bash
# variables.dev.yaml
ENVIRONMENT: "development"
API_URL: "http://localhost:3000"

# variables.staging.yaml
ENVIRONMENT: "staging"
API_URL: "https://staging.example.com"

# variables.prod.yaml
ENVIRONMENT: "production"
API_URL: "https://api.example.com"
```

Load with scripts:

```bash
#!/bin/bash
# generate-for-env.sh

ENV=${1:-development}
source "variables.${ENV}.yaml"

promptrek generate --editor claude \
  -V ENVIRONMENT="$ENVIRONMENT" \
  -V API_URL="$API_URL"
```

## Secure Secret Management

### Local Variables File

Store secrets separately:

```yaml
# .promptrek/variables.promptrek.yaml (gitignored)
GITHUB_TOKEN: "ghp_real_token_here"
OPENAI_API_KEY: "sk-real_key_here"
DATABASE_PASSWORD: "real_password_here"
AWS_ACCESS_KEY: "AKIA..."
AWS_SECRET_KEY: "secret..."
```

### Environment Variables Integration

Load from system environment:

```bash
# .env file
GITHUB_TOKEN=ghp_token
OPENAI_API_KEY=sk_key

# Load and pass to PrompTrek
source .env
promptrek generate --editor claude \
  -V GITHUB_TOKEN="$GITHUB_TOKEN" \
  -V OPENAI_API_KEY="$OPENAI_API_KEY"
```

### CI/CD Secrets

Use CI/CD secret management:

```yaml
# .github/workflows/generate.yml
- name: Generate prompts
  env:
    GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
    OPENAI_KEY: ${{ secrets.OPENAI_API_KEY }}
  run: |
    promptrek generate --editor claude \
      -V GITHUB_TOKEN="$GITHUB_TOKEN" \
      -V OPENAI_API_KEY="$OPENAI_KEY"
```

## Computed Variables

### Date and Time

Use built-in variables with computation:

```yaml
variables:
  BUILD_DATE: "{{{ CURRENT_DATE }}}"
  BUILD_YEAR: "{{{ CURRENT_YEAR }}}"
  COPYRIGHT: "Copyright {{{ CURRENT_YEAR }}} Company Name"

content: |
  Built on: {{{ BUILD_DATE }}}
  {{{ COPYRIGHT }}}
```

### Version Management

```yaml
variables:
  MAJOR: "2"
  MINOR: "1"
  PATCH: "0"
  VERSION: "{{{ MAJOR }}}.{{{ MINOR }}}.{{{ PATCH }}}"
  VERSION_TAG: "v{{{ VERSION }}}"

metadata:
  version: "{{{ VERSION }}}"

content: |
  # Release {{{ VERSION_TAG }}}
```

## Conditional Content

### Boolean Flags

```yaml
variables:
  INCLUDE_EXAMPLES: "true"
  INCLUDE_ADVANCED: "false"
  DEBUG_MODE: "false"

content: |
  # Documentation

  ## Basic Usage
  ...

  {% if INCLUDE_EXAMPLES == "true" %}
  ## Examples
  Here are some examples...
  {% endif %}

  {% if INCLUDE_ADVANCED == "true" %}
  ## Advanced Topics
  Advanced content...
  {% endif %}

  {% if DEBUG_MODE == "true" %}
  **DEBUG MODE ENABLED**
  {% endif %}
```

!!! note "Editor Support"
    Conditional syntax support varies by editor. Some editors may not process conditionals.

### Feature Flags

```yaml
variables:
  FEATURE_NEW_UI: "true"
  FEATURE_BETA_API: "false"
  FEATURE_EXPERIMENTAL: "false"

content: |
  ## Available Features

  {% if FEATURE_NEW_UI == "true" %}
  - New UI (enabled)
  {% endif %}

  {% if FEATURE_BETA_API == "true" %}
  - Beta API (enabled)
  {% endif %}
```

## Template Patterns

### Project Templates

```yaml
# templates/web-app.promptrek.yaml
variables:
  PROJECT_TYPE: "web-application"
  FRAMEWORK: "react"
  BACKEND: "node"
  DATABASE: "postgresql"

content: |
  # {{{ FRAMEWORK }}} {{{ PROJECT_TYPE }}}

  ## Stack
  - Frontend: {{{ FRAMEWORK }}}
  - Backend: {{{ BACKEND }}}
  - Database: {{{ DATABASE }}}
```

Instantiate with overrides:

```bash
# Create Vue app
promptrek generate templates/web-app.promptrek.yaml \
  -V FRAMEWORK=vue \
  --editor claude

# Create Django app
promptrek generate templates/web-app.promptrek.yaml \
  -V FRAMEWORK=vue \
  -V BACKEND=django \
  -V DATABASE=postgresql \
  --editor claude
```

### Team Member Templates

```yaml
# .promptrek/variables.promptrek.yaml (each team member)
DEVELOPER_NAME: "Alice Johnson"
GITHUB_USERNAME: "alice"
PREFERRED_EDITOR: "vscode"
CODING_STYLE: "functional"
```

```yaml
# project.promptrek.yaml (shared)
content: |
  ## Developer: {{{ DEVELOPER_NAME }}}
  GitHub: @{{{ GITHUB_USERNAME }}}
  Preferred Style: {{{ CODING_STYLE }}}
```

## Variable Validation

### Required Variables

Check for required variables:

```yaml
# project.promptrek.yaml
variables:
  # Required (provide defaults or enforce via docs)
  PROJECT_NAME: "MyApp"    # Must be overridden
  GITHUB_TOKEN: ""         # Must be in local file (empty to show requirement)

mcp_servers:
  - name: github
    env:
      GITHUB_TOKEN: "{{{ GITHUB_TOKEN }}}"
```

### Validation Script

```bash
#!/bin/bash
# validate-variables.sh

REQUIRED_VARS="GITHUB_TOKEN OPENAI_API_KEY DATABASE_URL"

for var in $REQUIRED_VARS; do
  if [ -z "${!var}" ]; then
    echo "Error: Required variable $var is not set"
    exit 1
  fi
done

echo "All required variables are set"
promptrek generate --editor claude
```

## Variable Precedence Strategies

### Override Chain

```
CLI > Local File > Prompt File > Built-in
 4       3            2             1
```

**Example**:

```yaml
# 2. Prompt file (project.promptrek.yaml)
variables:
  ENVIRONMENT: "development"
  VERSION: "1.0.0"
```

```yaml
# 3. Local file (.promptrek/variables.promptrek.yaml)
ENVIRONMENT: "staging"  # Overrides prompt file
```

```bash
# 4. CLI (highest priority)
promptrek generate \
  -V ENVIRONMENT=production  # Overrides everything
```

**Final values**:
- `ENVIRONMENT`: "production" (from CLI)
- `VERSION`: "1.0.0" (from prompt file)

## Best Practices

!!! tip "Use Descriptive Names"
    ```yaml
    # Good
    API_BASE_URL: "https://api.example.com"
    DB_CONNECTION_POOL_SIZE: "10"

    # Avoid
    url: "https://api.example.com"
    size: "10"
    ```

!!! tip "Group Related Variables"
    ```yaml
    variables:
      # API Configuration
      API_BASE_URL: "..."
      API_TIMEOUT: "30000"
      API_RETRY_COUNT: "3"

      # Database Configuration
      DB_HOST: "localhost"
      DB_PORT: "5432"
      DB_NAME: "myapp"
    ```

!!! warning "Never Commit Secrets"
    ```yaml
    # ❌ Don't do this
    variables:
      GITHUB_TOKEN: "ghp_actual_token"  # Committed!

    # ✅ Do this instead
    # .promptrek/variables.promptrek.yaml (gitignored)
    GITHUB_TOKEN: "ghp_actual_token"
    ```

!!! note "Document Required Variables"
    ```yaml
    # project.promptrek.yaml
    # Required variables (set in .promptrek/variables.promptrek.yaml):
    # - GITHUB_TOKEN: GitHub personal access token
    # - OPENAI_API_KEY: OpenAI API key

    content: |
      Uses GitHub Token: {{{ GITHUB_TOKEN }}}
    ```

## See Also

- [Variables Configuration](../configuration/variables.md)
- [Templates](templates.md)
- [Conditionals](conditionals.md)
- [CI/CD Integration](../workflows/cicd.md)
