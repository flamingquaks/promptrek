# Multi-Document Patterns

Advanced patterns for organizing complex prompts using PrompTrek's multi-document support.

## Overview

Multi-document support allows you to split large, complex prompts into focused, maintainable pieces. This guide covers advanced patterns and best practices.

## Common Patterns

### Technology Stack Separation

Organize by technology layer:

```yaml
schema_version: "3.1.0"

metadata:
  title: "Full-Stack Application"

content: |
  # General Project Guidelines
  Universal standards that apply to all code...

documents:
  - name: "frontend-react"
    file_globs: "src/frontend/**/*.{ts,tsx,jsx}"
    content: |
      # Frontend Development with React
      React-specific patterns and practices...

  - name: "backend-api"
    file_globs: "src/backend/**/*.ts"
    content: |
      # Backend API Development
      Node.js/Express API guidelines...

  - name: "database-schema"
    file_globs: "src/db/**/*.sql"
    content: |
      # Database Schema Guidelines
      PostgreSQL schema design patterns...

  - name: "infrastructure"
    file_globs: "{terraform/**/*,k8s/**/*}"
    content: |
      # Infrastructure as Code
      Terraform and Kubernetes configurations...
```

### Domain-Driven Design

Organize by business domain:

```yaml
documents:
  - name: "user-domain"
    file_globs: "src/domains/users/**/*"
    content: |
      # User Management Domain
      Authentication, authorization, profiles...

  - name: "order-domain"
    file_globs: "src/domains/orders/**/*"
    content: |
      # Order Processing Domain
      Cart, checkout, fulfillment workflows...

  - name: "inventory-domain"
    file_globs: "src/domains/inventory/**/*"
    content: |
      # Inventory Management Domain
      Stock tracking, warehouse operations...

  - name: "shared-kernel"
    file_globs: "src/shared/**/*"
    always_apply: true
    content: |
      # Shared Kernel
      Cross-domain utilities and types...
```

### Layered Architecture

Separate by architectural layer:

```yaml
documents:
  - name: "presentation-layer"
    file_globs: "src/presentation/**/*"
    content: |
      # Presentation Layer
      UI components, views, presenters...

  - name: "application-layer"
    file_globs: "src/application/**/*"
    content: |
      # Application Layer
      Use cases, application services...

  - name: "domain-layer"
    file_globs: "src/domain/**/*"
    content: |
      # Domain Layer
      Entities, value objects, domain services...

  - name: "infrastructure-layer"
    file_globs: "src/infrastructure/**/*"
    content: |
      # Infrastructure Layer
      Repositories, external services...
```

## Advanced File Glob Patterns

### Multiple Extensions

```yaml
documents:
  - name: "typescript-files"
    file_globs: "**/*.{ts,tsx,mts,cts}"
    content: |
      TypeScript guidelines...

  - name: "config-files"
    file_globs: "**/*.{json,yaml,yml,toml}"
    content: |
      Configuration file guidelines...
```

### Directory-Specific Rules

```yaml
documents:
  - name: "source-code"
    file_globs: "src/**/*.{ts,tsx}"
    content: |
      Source code standards...

  - name: "test-files"
    file_globs: "**/*.{test,spec}.{ts,tsx}"
    content: |
      Testing guidelines...

  - name: "e2e-tests"
    file_globs: "e2e/**/*"
    content: |
      End-to-end test patterns...
```

### Exclusion Patterns

```yaml
documents:
  - name: "app-code"
    file_globs: "src/**/*.ts"
    # Note: PrompTrek doesn't support negation in file_globs
    # Use specific patterns instead
    content: |
      Application code (excluding tests)...

  - name: "tests-only"
    file_globs: "src/**/*.test.ts"
    content: |
      Test-specific guidelines...
```

## Context-Aware Documents

### Always-Apply vs Conditional

```yaml
content: |
  # Base Guidelines (always applied)
  Core principles for all code...

documents:
  # Always applied, regardless of file
  - name: "security-requirements"
    always_apply: true
    content: |
      # Security Requirements
      Must be followed for ALL code...

  # Applied only to matching files
  - name: "react-components"
    file_globs: "**/*.tsx"
    always_apply: false
    content: |
      # React Component Guidelines
      Only applies to .tsx files...
```

### Hierarchical Application

```yaml
documents:
  # Level 1: Universal (always_apply: true)
  - name: "coding-standards"
    always_apply: true
    content: Core standards...

  # Level 2: Language-specific
  - name: "typescript-standards"
    file_globs: "**/*.{ts,tsx}"
    content: TypeScript guidelines...

  # Level 3: Framework-specific
  - name: "react-patterns"
    file_globs: "**/*.tsx"
    content: React-specific patterns...

  # Level 4: Domain-specific
  - name: "auth-components"
    file_globs: "src/components/auth/**/*.tsx"
    content: Auth component patterns...
```

## Monorepo Patterns

### Workspace-Based Organization

```yaml
documents:
  # Shared packages
  - name: "shared-ui"
    file_globs: "packages/ui/**/*"
    content: |
      # Shared UI Library
      Reusable components and styles...

  - name: "shared-utils"
    file_globs: "packages/utils/**/*"
    content: |
      # Shared Utilities
      Common utility functions...

  # Applications
  - name: "web-app"
    file_globs: "apps/web/**/*"
    content: |
      # Web Application
      Next.js web app guidelines...

  - name: "mobile-app"
    file_globs: "apps/mobile/**/*"
    content: |
      # Mobile Application
      React Native app guidelines...

  # Services
  - name: "api-service"
    file_globs: "services/api/**/*"
    content: |
      # API Service
      Backend API guidelines...
```

### Package-Specific Rules

```yaml
documents:
  - name: "package-design-system"
    file_globs: "packages/design-system/**/*"
    description: "Design system component library"
    content: |
      # Design System

      ## Component Structure
      - Atomic design principles
      - Storybook documentation
      - Accessibility first

  - name: "package-shared-types"
    file_globs: "packages/types/**/*"
    description: "Shared TypeScript types"
    content: |
      # Shared Types

      ## Type Definition Guidelines
      - Use interfaces for objects
      - Prefer type aliases for unions
      - Document complex types
```

## Editor-Specific Patterns

### Cursor Multi-Rules

Optimized for Cursor's `.cursor/rules/` system:

```yaml
documents:
  - name: "always-apply-core"
    always_apply: true
    description: "Core rules that always apply"
    content: |
      # Core Development Rules
      These apply to ALL files...

  - name: "typescript-auto"
    file_globs: "**/*.{ts,tsx}"
    always_apply: false  # Auto-attach to .ts/.tsx files
    description: "TypeScript-specific rules"
    content: |
      # TypeScript Rules
      Auto-applies to TypeScript files...
```

### Claude Multi-Prompts

Optimized for Claude's `.claude/prompts/` system:

```yaml
content: |
  # Main Project Context
  Primary project guidelines...

documents:
  - name: "testing-guide"
    content: |
      # Testing Guide
      Comprehensive testing documentation...

  - name: "architecture-guide"
    content: |
      # Architecture Guide
      System architecture and patterns...

  - name: "api-reference"
    content: |
      # API Reference
      API endpoints and usage...
```

## Variable Integration

### Document-Specific Variables

```yaml
variables:
  PROJECT_NAME: "E-Commerce Platform"
  FRONTEND_FRAMEWORK: "React"
  BACKEND_FRAMEWORK: "Node.js"

documents:
  - name: "frontend"
    content: |
      # {{{ PROJECT_NAME }}} - Frontend

      Framework: {{{ FRONTEND_FRAMEWORK }}}

  - name: "backend"
    content: |
      # {{{ PROJECT_NAME }}} - Backend

      Framework: {{{ BACKEND_FRAMEWORK }}}
```

### Conditional Documents

```yaml
variables:
  INCLUDE_MOBILE: "true"
  INCLUDE_DESKTOP: "false"

documents:
  # Always included
  - name: "web-guidelines"
    content: Web development...

  # Conditionally rendered
  {% if INCLUDE_MOBILE == "true" %}
  - name: "mobile-guidelines"
    content: Mobile development...
  {% endif %}

  {% if INCLUDE_DESKTOP == "true" %}
  - name: "desktop-guidelines"
    content: Desktop app development...
  {% endif %}
```

## Performance Considerations

### Document Size

Keep individual documents focused:

```yaml
# Good: Focused documents
documents:
  - name: "react-components"     # ~500 lines
  - name: "react-hooks"          # ~300 lines
  - name: "react-testing"        # ~400 lines

# Avoid: Monolithic documents
documents:
  - name: "everything-react"     # 5000+ lines (too large)
```

### Number of Documents

Optimal range: 3-10 documents per project

```yaml
# Good: 5 focused documents
documents:
  - name: "frontend"
  - name: "backend"
  - name: "database"
  - name: "testing"
  - name: "deployment"

# Avoid: Too many documents
documents:
  # 20+ documents (hard to manage)
```

## Best Practices

!!! tip "Organize by Purpose"
    Group documents by their purpose or domain, not arbitrarily:
    ```yaml
    # Good
    - name: "authentication"
    - name: "authorization"

    # Avoid
    - name: "doc1"
    - name: "misc"
    ```

!!! tip "Use Descriptive File Globs"
    Make file patterns clear and specific:
    ```yaml
    # Good
    file_globs: "src/components/**/*.tsx"

    # Too broad
    file_globs: "**/*"
    ```

!!! warning "Avoid Overlapping Globs"
    Prevent multiple documents matching the same files:
    ```yaml
    # Avoid overlap
    - file_globs: "**/*.ts"           # Matches all TypeScript
    - file_globs: "src/**/*.ts"       # Overlaps with above

    # Better: Be specific
    - file_globs: "src/backend/**/*.ts"
    - file_globs: "src/frontend/**/*.ts"
    ```

!!! note "Test with Dry Run"
    Verify document generation:
    ```bash
    promptrek generate --all --dry-run
    ```

## See Also

- [Documents Configuration](../configuration/documents.md)
- [File Globs](https://en.wikipedia.org/wiki/Glob_(programming))
- [Adapter Capabilities](../adapters/capabilities.md)
- [Schema v3.1.0](../configuration/schema-v3.1.md)
