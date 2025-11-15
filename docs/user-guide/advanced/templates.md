# Template System

Create reusable PrompTrek templates for common project types and patterns.

## Overview

PrompTrek templates are reusable `.promptrek.yaml` files that can be customized through variables and CLI overrides. Templates help standardize configurations across projects.

## Creating Templates

### Basic Template

```yaml
# templates/web-app.promptrek.yaml
schema_version: "3.1.0"

metadata:
  title: "{{{ PROJECT_NAME }}} Web Application"
  description: "{{{ FRAMEWORK }}} web application"
  tags: [web, "{{{ FRAMEWORK }}}"]

variables:
  PROJECT_NAME: "MyApp"           # Override at generation
  FRAMEWORK: "react"              # Override at generation
  NODE_VERSION: "20"

content: |
  # {{{ PROJECT_NAME }}}

  ## Stack
  - Framework: {{{ FRAMEWORK }}}
  - Node Version: {{{ NODE_VERSION }}}

  ## Guidelines
  Write clean, maintainable code following {{{ FRAMEWORK }}} best practices.
```

Use the template:

```bash
promptrek generate templates/web-app.promptrek.yaml \
  -V PROJECT_NAME="E-Commerce" \
  -V FRAMEWORK=vue \
  --editor claude
```

### Full-Stack Template

```yaml
# templates/fullstack.promptrek.yaml
variables:
  PROJECT_NAME: "MyApp"
  FRONTEND_FRAMEWORK: "react"
  BACKEND_FRAMEWORK: "express"
  DATABASE: "postgresql"

content: |
  # {{{ PROJECT_NAME }}} - Full Stack Application

documents:
  - name: "frontend"
    file_globs: "src/frontend/**/*"
    content: |
      # Frontend: {{{ FRONTEND_FRAMEWORK }}}

  - name: "backend"
    file_globs: "src/backend/**/*"
    content: |
      # Backend: {{{ BACKEND_FRAMEWORK }}}

  - name: "database"
    content: |
      # Database: {{{ DATABASE }}}
```

## Template Categories

### By Project Type

```
templates/
├── web-app.promptrek.yaml        # Web applications
├── api-service.promptrek.yaml    # API services
├── cli-tool.promptrek.yaml       # CLI tools
├── library.promptrek.yaml        # Libraries
└── monorepo.promptrek.yaml       # Monorepos
```

### By Technology

```
templates/
├── react-app.promptrek.yaml
├── vue-app.promptrek.yaml
├── python-fastapi.promptrek.yaml
├── golang-service.promptrek.yaml
└── rust-cli.promptrek.yaml
```

## Template Distribution

### Git Repository

```bash
# Template repository structure
promptrek-templates/
├── README.md
├── templates/
│   ├── web/
│   │   ├── react.promptrek.yaml
│   │   └── vue.promptrek.yaml
│   ├── api/
│   │   ├── rest.promptrek.yaml
│   │   └── graphql.promptrek.yaml
│   └── examples/
```

Use templates:

```bash
# Clone templates
git clone https://github.com/org/promptrek-templates

# Use a template
promptrek generate promptrek-templates/templates/web/react.promptrek.yaml \
  -V PROJECT_NAME="MyApp" \
  --editor claude
```

## Best Practices

!!! tip "Document Variables"
    ```yaml
    # Required variables:
    # - PROJECT_NAME: Name of the project
    # - FRAMEWORK: Frontend framework (react/vue/angular)
    # - NODE_VERSION: Node.js version

    variables:
      PROJECT_NAME: "MyApp"
      FRAMEWORK: "react"
      NODE_VERSION: "20"
    ```

!!! tip "Provide Sensible Defaults"
    ```yaml
    variables:
      # Good defaults
      NODE_VERSION: "20"          # LTS version
      TEST_FRAMEWORK: "jest"      # Popular choice
      ENVIRONMENT: "development"  # Safe default
    ```

## See Also

- [Variables](../configuration/variables.md)
- [Advanced Variables](variables.md)
- [Examples](/examples/)
