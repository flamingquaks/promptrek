# Conditional Instructions

Use conditional logic to create dynamic prompts that adapt based on variables and context.

## Overview

Conditional instructions allow you to include or exclude content based on variable values, creating flexible, context-aware prompts.

!!! note "Editor Support"
    Conditional syntax support varies by editor. Some editors process conditionals during generation, others may display them as-is.

## Basic Syntax

### If Statements

```yaml
variables:
  INCLUDE_TESTS: "true"

content: |
  # Project Guidelines

  ## Development
  Write clean, maintainable code.

  {% if INCLUDE_TESTS == "true" %}
  ## Testing
  Write tests for all new features.
  Coverage target: 80%
  {% endif %}
```

### If-Else Statements

```yaml
variables:
  ENVIRONMENT: "production"

content: |
  ## Configuration

  {% if ENVIRONMENT == "production" %}
  Use production database and strict error handling.
  {% else %}
  Use development database and verbose logging.
  {% endif %}
```

### Multiple Conditions

```yaml
variables:
  ENVIRONMENT: "staging"

content: |
  {% if ENVIRONMENT == "development" %}
  Development mode: verbose logging, hot reload enabled
  {% elif ENVIRONMENT == "staging" %}
  Staging mode: normal logging, performance monitoring
  {% elif ENVIRONMENT == "production" %}
  Production mode: error logging only, optimized builds
  {% else %}
  Unknown environment
  {% endif %}
```

## Common Use Cases

### Feature Flags

```yaml
variables:
  FEATURE_BETA_UI: "true"
  FEATURE_NEW_API: "false"

content: |
  ## Available Features

  {% if FEATURE_BETA_UI == "true" %}
  ### Beta UI
  New UI components are enabled.
  Use the design system from `src/components/beta/`
  {% endif %}

  {% if FEATURE_NEW_API == "true" %}
  ### New API
  Use the v2 API endpoints at `/api/v2/`
  {% else %}
  ### Current API
  Use the v1 API endpoints at `/api/v1/`
  {% endif %}
```

### Environment-Specific Guidelines

```yaml
variables:
  ENVIRONMENT: "development"
  DEBUG_MODE: "true"

content: |
  {% if ENVIRONMENT == "development" %}
  ## Development Guidelines
  - Hot reload enabled
  - Source maps enabled
  - Verbose error messages
  {% endif %}

  {% if DEBUG_MODE == "true" %}
  ## Debug Mode
  Additional logging enabled.
  Use `console.debug()` for debug output.
  {% endif %}
```

### Technology Stack Variations

```yaml
variables:
  DATABASE: "postgresql"
  CACHE: "redis"

content: |
  ## Database Configuration

  {% if DATABASE == "postgresql" %}
  Using PostgreSQL:
  - Use parameterized queries: `$1, $2, ...`
  - Enable connection pooling
  - Use JSONB for JSON data
  {% elif DATABASE == "mysql" %}
  Using MySQL:
  - Use prepared statements: `?, ?, ...`
  - Enable query cache
  - Use JSON columns for JSON data
  {% endif %}

  {% if CACHE == "redis" %}
  ## Caching with Redis
  - Use Redis for session storage
  - Cache frequently accessed data
  - Set appropriate TTLs
  {% endif %}
```

## Best Practices

!!! tip "Use Boolean Variables"
    ```yaml
    # Good: Boolean string values
    INCLUDE_TESTS: "true"
    DEBUG_MODE: "false"

    # Check with ==
    {% if INCLUDE_TESTS == "true" %}
    ```

!!! warning "Quote Comparison Values"
    ```yaml
    # Correct
    {% if ENVIRONMENT == "production" %}

    # May not work
    {% if ENVIRONMENT == production %}
    ```

!!! note "Default Values"
    Provide defaults for conditional variables:
    ```yaml
    variables:
      INCLUDE_TESTS: "true"  # Default to including tests
      DEBUG_MODE: "false"     # Default to production mode
    ```

## See Also

- [Advanced Variables](variables.md)
- [Templates](templates.md)
- [Variables Configuration](../configuration/variables.md)
