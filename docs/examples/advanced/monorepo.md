# NX Monorepo Example

This example demonstrates how to configure PrompTrek for a large-scale NX monorepo with multiple applications and shared libraries.

## Overview

**Use Case:** Enterprise-scale monorepo with multiple React apps, NestJS backends, and shared libraries

**What You'll Learn:**
- Configuring PrompTrek for monorepo architecture
- Managing multiple applications and libraries
- Enforcing module boundaries
- Code generation and workspace organization
- Multi-document configurations for different project types

## Complete Configuration

```yaml
# yaml-language-server: $schema=https://promptrek.ai/schema/v3.1.0.json
schema_version: "3.1.0"
metadata:
  title: Nx Monorepo
  description: Large-scale monorepo development with Nx
  version: 1.0.0
  author: PrompTrek
  tags:
    - nx
    - monorepo
    - typescript
    - react

content: |
  # Nx Monorepo Development Guide

  ## Monorepo Architecture

  **Tech Stack:**
  - Nx 18+
  - TypeScript
  - React for frontend apps
  - NestJS for backend apps
  - Shared libraries
  - Jest for testing
  - ESLint + Prettier

  **Workspace Structure:**
  ```
  apps/
    web/             # React web application
    mobile/          # React Native app
    api/             # NestJS API
  libs/
    shared/
      ui/            # Shared UI components
      utils/         # Shared utilities
      types/         # Shared TypeScript types
    feature/
      auth/          # Authentication feature
      users/         # Users feature
  tools/             # Custom scripts and tools
  ```

  ## Nx Commands

  ```bash
  # Generate new application
  nx g @nx/react:app web
  nx g @nx/nest:app api

  # Generate library
  nx g @nx/react:lib ui --directory=shared
  nx g @nx/js:lib utils --directory=shared

  # Run application
  nx serve web
  nx serve api

  # Build application
  nx build web --prod
  nx build api --prod

  # Test
  nx test web
  nx test shared-ui
  nx affected:test  # Test only affected projects

  # Lint
  nx lint web
  nx affected:lint

  # Run all targets for affected projects
  nx affected --target=build
  ```

  ## Shared Library Example

  ```typescript
  // libs/shared/ui/src/lib/Button/Button.tsx
  export interface ButtonProps {
    variant?: 'primary' | 'secondary';
    size?: 'sm' | 'md' | 'lg';
    children: React.ReactNode;
    onClick?: () => void;
  }

  export function Button({
    variant = 'primary',
    size = 'md',
    children,
    onClick,
  }: ButtonProps) {
    return (
      <button
        className={`btn btn-${variant} btn-${size}`}
        onClick={onClick}
      >
        {children}
      </button>
    );
  }
  ```

  ## Dependency Graph Management

  ### Enforce Module Boundaries
  ```json
  // .eslintrc.json
  {
    "overrides": [
      {
        "files": ["*.ts", "*.tsx"],
        "rules": {
          "@nx/enforce-module-boundaries": [
            "error",
            {
              "depConstraints": [
                {
                  "sourceTag": "type:app",
                  "onlyDependOnLibsWithTags": ["type:feature", "type:ui", "type:util"]
                },
                {
                  "sourceTag": "type:feature",
                  "onlyDependOnLibsWithTags": ["type:ui", "type:util"]
                },
                {
                  "sourceTag": "type:ui",
                  "onlyDependOnLibsWithTags": ["type:util"]
                }
              ]
            }
          ]
        }
      }
    ]
  }
  ```

  ## Best Practices

  ### Library Organization
  - Keep libraries small and focused
  - Use tags to enforce boundaries
  - Create buildable libraries for faster builds
  - Use path mappings in tsconfig.json

  ### Performance
  - Enable Nx Cloud for distributed caching
  - Use `affected` commands in CI
  - Configure task dependencies properly
  - Enable parallel execution

  ### Code Sharing
  - Share types through dedicated library
  - Extract common utilities early
  - Create feature libraries for domains
  - Use generator for consistency

variables:
  NX_CLOUD_TOKEN: your-cloud-token
  ORG_NAME: myorg
```

## Configuration Breakdown

### Monorepo-Specific Guidelines

The configuration includes:

1. **Workspace Structure** - Clear organization of apps and libs
2. **Nx Commands** - Common commands for different tasks
3. **Module Boundaries** - Enforcing dependency constraints
4. **Code Sharing** - Patterns for shared code
5. **Performance** - Optimization strategies

### Multi-Document Configuration

For a monorepo, use separate documents for different project types:

```yaml
schema_version: "3.1.0"
metadata:
  title: Nx Monorepo

content: |
  # General Monorepo Guidelines
  - Follow Nx conventions
  - Use affected commands in CI
  - Keep libraries focused and small

# React app-specific rules
documents:
  - name: react-apps
    content: |
      # React Application Guidelines

      ## Component Structure
      - Use functional components with hooks
      - Keep components under 200 lines
      - Extract complex logic to custom hooks

      ## State Management
      - Use React Query for server state
      - Use Zustand for global client state
      - Keep state close to where it's used

      ## File Organization
      ```
      apps/web/src/
        app/
          components/   # App-specific components
          pages/        # Route components
          hooks/        # App-specific hooks
      ```
    file_globs: "apps/*/src/**/*.{tsx,jsx}"
    always_apply: false

  # NestJS backend rules
  - name: nestjs-backends
    content: |
      # NestJS Backend Guidelines

      ## Module Structure
      - One feature per module
      - Use dependency injection
      - Keep controllers thin

      ## API Design
      - Use DTOs for request/response
      - Implement validation with class-validator
      - Use Swagger decorators for docs

      ## Example Controller
      ```typescript
      @Controller('users')
      @ApiTags('users')
      export class UsersController {
        constructor(private readonly usersService: UsersService) {}

        @Get()
        @ApiResponse({ type: [UserDto] })
        findAll(): Promise<UserDto[]> {
          return this.usersService.findAll();
        }
      }
      ```
    file_globs: "apps/api/src/**/*.{ts,controller.ts}"
    always_apply: false

  # Shared library rules
  - name: shared-libraries
    content: |
      # Shared Library Guidelines

      ## Library Types
      - **UI Libraries**: Reusable components only
      - **Util Libraries**: Pure functions, no side effects
      - **Feature Libraries**: Domain logic and state

      ## Exports
      - Export through barrel files (index.ts)
      - Only export public API
      - Document all exported functions

      ## Dependencies
      - Minimize external dependencies
      - No circular dependencies
      - Follow dependency constraints
    file_globs: "libs/**/*.{ts,tsx}"
    always_apply: false

  # Testing rules
  - name: testing
    content: |
      # Monorepo Testing Guidelines

      ## Test Organization
      - Co-locate tests with source files
      - Use .spec.ts for unit tests
      - Use .e2e-spec.ts for e2e tests

      ## Shared Test Utilities
      ```typescript
      // libs/shared/testing/src/lib/test-utils.tsx
      import { render } from '@testing-library/react';

      export function renderWithProviders(ui: React.ReactElement) {
        return render(ui, {
          wrapper: ({ children }) => (
            <QueryClientProvider client={queryClient}>
              {children}
            </QueryClientProvider>
          ),
        });
      }
      ```

      ## Running Tests
      ```bash
      # Test specific project
      nx test web

      # Test affected projects
      nx affected:test

      # Test all
      nx run-many --target=test --all
      ```
    file_globs: "**/*.spec.{ts,tsx}"
    always_apply: false

variables:
  NX_CLOUD_TOKEN: your-cloud-token
  ORG_NAME: myorg
```

## Usage Instructions

### Step 1: Save Configuration

Save to `nx-monorepo.promptrek.yaml` in your workspace root.

### Step 2: Validate

```bash
promptrek validate nx-monorepo.promptrek.yaml
```

### Step 3: Generate

```bash
# Generate for all editors
promptrek generate nx-monorepo.promptrek.yaml --all

# For specific editor with context-aware rules
promptrek generate nx-monorepo.promptrek.yaml --editor cursor
```

### Step 4: Customize for Your Workspace

```yaml
variables:
  NX_CLOUD_TOKEN: "your-actual-token"
  ORG_NAME: "acme"
  PRIMARY_APP: "web"
  API_URL: "https://api.acme.com"
```

## Advanced: With Code Generators

Add custom commands for Nx operations:

```yaml
commands:
  - name: generate-feature
    description: Generate a new feature library
    prompt: |
      Generate an Nx feature library with:
      - Library scaffold using `nx g @nx/js:lib`
      - Barrel export (index.ts)
      - Basic tests
      - README.md with usage
      - Appropriate tags in project.json

      Include:
      - State management setup (if needed)
      - API service layer
      - Types/interfaces
      - Unit tests

  - name: generate-component
    description: Generate a UI component in shared library
    prompt: |
      Generate a reusable component in libs/shared/ui:
      - Component file with TypeScript
      - Props interface
      - Storybook story
      - Unit tests
      - Export from index.ts

      Follow shared component guidelines:
      - No business logic
      - Fully typed props
      - Accessible markup

  - name: affected-analysis
    description: Analyze affected projects
    prompt: |
      Analyze the affected projects and suggest:
      - Which tests need to run
      - Which builds are required
      - Potential breaking changes
      - Migration strategy if needed

      Run: `nx affected:graph` to visualize
```

## Generated Files Structure

### For Cursor

```
.cursor/
  rules/
    index.mdc           # General monorepo guidelines
    react-apps.mdc      # React-specific rules
    nestjs-backends.mdc # Backend-specific rules
    shared-libraries.mdc # Library guidelines
    testing.mdc         # Test guidelines
AGENTS.md               # Project overview
```

Each `.mdc` file includes frontmatter:

```yaml
---
alwaysApply: false
fileGlobs:
  - "apps/*/src/**/*.tsx"
tags:
  - react
  - frontend
---
```

### For GitHub Copilot

```
.github/
  copilot-instructions.md      # General guidelines
  instructions/
    apps-web.instructions.md   # Web app specific
    apps-api.instructions.md   # API specific
    libs-shared.instructions.md # Library specific
```

## Real-World Monorepo Example

### E-Commerce Platform

```yaml
schema_version: "3.1.0"
metadata:
  title: E-Commerce Platform Monorepo
  description: Full-stack e-commerce with multiple storefronts

content: |
  # E-Commerce Platform

  ## Architecture Overview
  - Customer-facing web app (React)
  - Admin dashboard (React)
  - Mobile app (React Native)
  - GraphQL API (NestJS)
  - Microservices (NestJS)

  ## Workspace Apps
  - `apps/storefront` - Customer web app
  - `apps/admin` - Admin dashboard
  - `apps/mobile` - React Native app
  - `apps/api-gateway` - GraphQL gateway
  - `apps/services/products` - Product service
  - `apps/services/orders` - Order service
  - `apps/services/payments` - Payment service

  ## Shared Libraries
  - `libs/shared/ui` - Design system
  - `libs/shared/data-access` - API clients
  - `libs/shared/utils` - Utilities
  - `libs/domain/products` - Product domain
  - `libs/domain/orders` - Order domain
  - `libs/domain/auth` - Authentication

variables:
  ORG_NAME: acme-ecommerce
  API_GATEWAY_URL: https://api.acme.com/graphql
  STRIPE_PUBLIC_KEY: pk_test_xxx
```

## Best Practices

### Workspace Organization

!!! tip "Clear Boundaries"
    - Apps should not import from other apps
    - Libraries should follow the dependency graph
    - Use tags to enforce architectural boundaries

### Code Generation

!!! tip "Consistent Patterns"
    Use Nx generators for consistency:
    ```bash
    nx g @nx/react:component Button --project=shared-ui
    nx g @nx/nest:resource products --project=api
    ```

### CI/CD Optimization

!!! tip "Affected Commands"
    Only test and build what changed:
    ```yaml
    # .github/workflows/ci.yml
    - run: nx affected --target=test --base=origin/main
    - run: nx affected --target=build --base=origin/main
    ```

## Troubleshooting

### Module Boundary Violations

**Problem:** ESLint errors about module boundaries

**Solution:** Check project tags and dependency constraints:

```json
// libs/feature/auth/project.json
{
  "tags": ["type:feature", "scope:auth"]
}
```

### Circular Dependencies

**Problem:** Circular dependency detected

**Solution:**
1. Visualize with `nx graph`
2. Extract shared code to separate library
3. Use dependency injection

### Slow Build Times

**Problem:** Builds take too long

**Solution:**
- Enable Nx Cloud caching
- Use buildable libraries
- Configure task pipelines properly

## Related Examples

- **[React TypeScript](../basic/react-typescript.md)** - For individual React apps
- **[Node.js API](../basic/node-api.md)** - For backend services
- **[Custom Commands](../plugins/custom-commands.md)** - Nx-specific commands

## Additional Resources

- [Nx Documentation](https://nx.dev/)
- [Nx Cloud](https://nx.app/)
- [Monorepo Best Practices](https://nx.dev/concepts/more-concepts/monorepo-nx-enterprise)
- [Module Boundaries](https://nx.dev/core-features/enforce-module-boundaries)

---

**Next Steps:**
1. Adapt workspace structure to your needs
2. Set up multi-document configuration
3. Configure module boundary rules
4. Enable Nx Cloud for caching
5. Add custom generators for your patterns
