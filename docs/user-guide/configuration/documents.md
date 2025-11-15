# Multi-Document Support

PrompTrek's multi-document feature allows you to organize complex prompts into separate, focused documents that work together. This is especially powerful for editors that support multiple prompt files or context-specific rules.

## Overview

Multi-document support enables:

- **Logical separation**: Split large prompts into focused, manageable pieces
- **Path-specific rules**: Apply different guidelines to different file types
- **Context organization**: Separate frontend, backend, testing, etc. concerns
- **Editor features**: Leverage advanced editor capabilities (Cursor rules, Copilot instructions)
- **Maintainability**: Easier to update and version individual documents

## Document Structure

### Basic Syntax

```yaml
schema_version: "3.1.0"

metadata:
  title: "My Project"
  description: "Project configuration"

content: |
  # Main Project Guidelines
  These apply to all files...

documents:
  - name: "testing-guidelines"
    content: |
      # Testing Guidelines
      Test-specific instructions...

  - name: "frontend-rules"
    content: |
      # Frontend Development
      React/TypeScript guidelines...
```

### Document Fields

Each document in the `documents` array has:

#### name (required)

**Type**: `string`

Identifier for the document, used in generated filenames.

```yaml
documents:
  - name: "testing-guidelines"    # Becomes testing-guidelines.md
  - name: "api-patterns"          # Becomes api-patterns.md
```

**Best practices**:
- Use kebab-case
- Be descriptive
- Keep concise (2-4 words)
- Indicate purpose or domain

#### content (required)

**Type**: `string` (markdown)

The actual markdown content of the document.

```yaml
documents:
  - name: "security"
    content: |
      # Security Guidelines

      ## Authentication
      - Use OAuth 2.0
      - Implement CSRF protection

      ## Data Validation
      - Sanitize all inputs
      - Use parameterized queries
```

#### description (optional)

**Type**: `string`

Human-readable description of the document's purpose.

```yaml
documents:
  - name: "database"
    description: "Database schema design and query optimization guidelines"
    content: |
      # Database Guidelines
      ...
```

**Used by**: Cursor (displayed in UI), Continue (metadata)

#### file_globs (optional)

**Type**: `string`

File patterns where this document should apply (glob syntax).

```yaml
documents:
  - name: "typescript-patterns"
    file_globs: "**/*.{ts,tsx}"
    content: |
      # TypeScript Best Practices
      ...

  - name: "python-style"
    file_globs: "**/*.py"
    content: |
      # Python Style Guide
      ...
```

**Supported patterns**:
- `**/*.ts` - All TypeScript files
- `**/*.{ts,tsx}` - TypeScript and TSX files
- `src/**/*.py` - Python files in src directory
- `tests/**/*` - All files in tests directory

**Editor support**:
- **Cursor**: Auto-attaches rules to matching files
- **Copilot**: Path-specific instructions
- **Others**: Informational only

#### always_apply (optional)

**Type**: `boolean`

Whether to always apply this document regardless of file context.

```yaml
documents:
  - name: "core-principles"
    always_apply: true            # Always applied
    content: |
      # Core Development Principles
      ...

  - name: "react-components"
    file_globs: "**/*.tsx"
    always_apply: false           # Only for .tsx files
    content: |
      # React Component Guidelines
      ...
```

**Default**: `true` if no `file_globs` specified, `false` otherwise

**Cursor behavior**:
- `always_apply: true` → Cursor's "alwaysApply" rule
- `always_apply: false` with `file_globs` → Auto-attach to matching files

## Use Cases

### Organizing by Technology Stack

Separate guidelines by technology:

```yaml
content: |
  # General Project Guidelines
  Team standards and workflows...

documents:
  - name: "frontend-react"
    description: "React and TypeScript frontend guidelines"
    file_globs: "src/frontend/**/*.{ts,tsx}"
    content: |
      # Frontend Development

      ## React Patterns
      - Functional components only
      - Use hooks for state management
      - Props destructuring

      ## TypeScript
      - Strict mode enabled
      - No implicit any
      - Interface over type

  - name: "backend-node"
    description: "Node.js backend guidelines"
    file_globs: "src/backend/**/*.ts"
    content: |
      # Backend Development

      ## API Design
      - RESTful principles
      - Versioned endpoints
      - Proper HTTP status codes

      ## Database
      - Use TypeORM
      - Migrations for schema changes

  - name: "testing"
    description: "Testing standards"
    file_globs: "**/*.test.{ts,tsx}"
    content: |
      # Testing Guidelines

      ## Unit Tests
      - Jest + React Testing Library
      - AAA pattern (Arrange, Act, Assert)
      - Mock external dependencies
```

### Separation by Concern

Organize by development concern:

```yaml
documents:
  - name: "architecture"
    always_apply: true
    content: |
      # Architecture Principles
      Clean architecture, SOLID, DDD...

  - name: "security"
    always_apply: true
    content: |
      # Security Requirements
      Authentication, authorization, data protection...

  - name: "performance"
    description: "Performance optimization guidelines"
    content: |
      # Performance Guidelines
      Caching, lazy loading, bundle optimization...

  - name: "accessibility"
    file_globs: "src/components/**/*.tsx"
    content: |
      # Accessibility Standards
      WCAG 2.1 AA compliance, ARIA labels...
```

### Monorepo Structure

Organize by package or workspace:

```yaml
documents:
  - name: "shared-library"
    description: "Shared library guidelines"
    file_globs: "packages/shared/**/*"
    content: |
      # Shared Library
      Reusable utilities and components...

  - name: "web-app"
    description: "Web application specific rules"
    file_globs: "apps/web/**/*"
    content: |
      # Web Application
      Next.js app-specific guidelines...

  - name: "mobile-app"
    description: "Mobile app specific rules"
    file_globs: "apps/mobile/**/*"
    content: |
      # Mobile Application
      React Native specific guidelines...

  - name: "api-service"
    description: "API service guidelines"
    file_globs: "apps/api/**/*"
    content: |
      # API Service
      Backend service patterns...
```

### Domain-Driven Design

Organize by business domain:

```yaml
documents:
  - name: "user-management"
    description: "User management domain"
    file_globs: "src/domains/users/**/*"
    content: |
      # User Management Domain
      Authentication, profiles, preferences...

  - name: "order-processing"
    description: "Order processing domain"
    file_globs: "src/domains/orders/**/*"
    content: |
      # Order Processing Domain
      Cart, checkout, fulfillment...

  - name: "inventory"
    description: "Inventory management domain"
    file_globs: "src/domains/inventory/**/*"
    content: |
      # Inventory Domain
      Stock tracking, warehouse management...
```

## Generated Files by Editor

### Claude Code

Generates separate files in `.claude/prompts/`:

```
.claude/
└── prompts/
    ├── project.md                 # Main content
    ├── testing-guidelines.md
    ├── frontend-react.md
    └── backend-node.md
```

### Cursor

Generates `.cursor/rules/` files:

```
.cursor/
└── rules/
    ├── project.mdc               # Main content
    ├── testing-guidelines.mdc
    ├── frontend-react.mdc        # With file_globs metadata
    └── backend-node.mdc
```

**With frontmatter**:

```markdown
---
description: "React and TypeScript frontend guidelines"
globs: ["src/frontend/**/*.{ts,tsx}"]
alwaysApply: false
---

# Frontend Development
...
```

### Continue

Merges into `.continue/config.json`:

```json
{
  "rules": [
    {
      "name": "project",
      "content": "Main project guidelines..."
    },
    {
      "name": "testing-guidelines",
      "content": "Testing standards..."
    }
  ]
}
```

### GitHub Copilot

Generates instruction files:

```
.github/
└── instructions/
    ├── project.instructions.md
    ├── testing-guidelines.instructions.md
    └── frontend-react.instructions.md
```

## Best Practices

### Document Organization

!!! tip "Logical Separation"
    Split documents by:
    - **Technology**: React, Node.js, Python
    - **Layer**: Frontend, Backend, Database
    - **Concern**: Security, Testing, Performance
    - **Domain**: User management, Orders, Inventory

!!! warning "Don't Over-Split"
    Too many small documents can be harder to manage than one comprehensive document. Aim for 3-7 documents maximum.

### File Glob Patterns

!!! tip "Specific Patterns"
    Be specific with file globs to avoid conflicts:
    ```yaml
    # Good - specific
    file_globs: "src/components/**/*.tsx"

    # Too broad - may overlap
    file_globs: "**/*"
    ```

!!! tip "Test Your Patterns"
    Verify glob patterns match intended files:
    ```bash
    # Use glob to test patterns (requires glob command)
    ls src/components/**/*.tsx
    ```

### Content Strategy

!!! tip "Main Content First"
    Put general guidelines in `content`, specific rules in `documents`:
    ```yaml
    content: |
      # General team standards that apply everywhere

    documents:
      - name: "specific-tech"
        content: |
          # Technology-specific guidelines
    ```

!!! note "Avoid Duplication"
    Don't repeat content between main `content` and `documents`. Reference instead:
    ```yaml
    content: |
      # Code Quality
      See testing-guidelines document for testing standards.

    documents:
      - name: "testing-guidelines"
        content: |
          # Detailed testing standards...
    ```

### Naming Conventions

!!! tip "Clear Names"
    Use descriptive, consistent naming:
    ```yaml
    # Good
    - name: "react-components"
    - name: "api-design"
    - name: "database-patterns"

    # Avoid
    - name: "doc1"              # Not descriptive
    - name: "ReactComponents"   # Not kebab-case
    - name: "stuff"             # Too vague
    ```

## Complete Example

```yaml
schema_version: "3.1.0"

metadata:
  title: "Full-Stack E-Commerce Platform"
  description: "Microservices-based e-commerce system"

# Main general guidelines
content: |
  # E-Commerce Platform

  ## Project Overview
  Microservices architecture with React frontend and Node.js services.

  ## General Principles
  - Clean code practices
  - Test-driven development
  - Documentation as code
  - Continuous integration

# Specific domain documents
documents:
  # Frontend
  - name: "frontend-guidelines"
    description: "React and TypeScript frontend development"
    file_globs: "apps/web/src/**/*.{ts,tsx}"
    always_apply: false
    content: |
      # Frontend Development Guidelines

      ## Component Structure
      - Functional components with hooks
      - Props interface always defined
      - Component file naming: PascalCase.tsx

      ## State Management
      - Redux Toolkit for global state
      - React Query for server state
      - Local state with useState/useReducer

      ## Styling
      - Styled-components for component styles
      - Theme-based design system
      - Mobile-first responsive design

  # Backend
  - name: "backend-guidelines"
    description: "Node.js microservices backend"
    file_globs: "services/**/*.ts"
    always_apply: false
    content: |
      # Backend Development Guidelines

      ## Service Structure
      - Clean architecture layers
      - Dependency injection
      - Domain-driven design

      ## API Design
      - RESTful endpoints
      - OpenAPI/Swagger documentation
      - Versioned APIs (/v1/, /v2/)

      ## Database
      - PostgreSQL with TypeORM
      - Migrations for schema changes
      - Connection pooling

  # Testing
  - name: "testing-standards"
    description: "Testing requirements and patterns"
    file_globs: "**/*.{test,spec}.{ts,tsx}"
    content: |
      # Testing Standards

      ## Coverage Requirements
      - Unit tests: 80% minimum
      - Integration tests for APIs
      - E2E tests for critical flows

      ## Testing Patterns
      - Jest for unit tests
      - React Testing Library for components
      - Supertest for API tests

      ## Best Practices
      - AAA pattern (Arrange, Act, Assert)
      - One assertion per test
      - Descriptive test names

  # Security
  - name: "security-requirements"
    description: "Security and compliance standards"
    always_apply: true            # Apply everywhere
    content: |
      # Security Requirements

      ## Authentication
      - JWT tokens with refresh mechanism
      - OAuth 2.0 for third-party login
      - MFA for sensitive operations

      ## Data Protection
      - Encrypt sensitive data at rest
      - TLS 1.3 for data in transit
      - GDPR compliance for user data

      ## Input Validation
      - Validate all user inputs
      - Sanitize before database operations
      - Rate limiting on APIs

  # DevOps
  - name: "devops-practices"
    description: "CI/CD and infrastructure"
    file_globs: "{.github/**/*,infrastructure/**/*,docker/**/*}"
    content: |
      # DevOps Practices

      ## CI/CD Pipeline
      - GitHub Actions for CI
      - Automated testing on PR
      - Staging deployment on merge

      ## Infrastructure
      - Kubernetes for orchestration
      - Terraform for IaC
      - AWS as cloud provider

      ## Monitoring
      - Application metrics with Prometheus
      - Logging with ELK stack
      - Error tracking with Sentry
```

## See Also

- [Advanced Multi-Document Patterns](../advanced/multi-document.md)
- [Schema v3.1.0 Guide](schema-v3.1.md)
- [Adapter Capabilities](../adapters/capabilities.md)
- [Variables in Documents](variables.md)
