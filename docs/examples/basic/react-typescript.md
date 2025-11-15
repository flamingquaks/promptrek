# React TypeScript Example

This example demonstrates how to configure PrompTrek for a modern React TypeScript project using best practices and current tooling.

## Overview

**Use Case:** React 18+ application with TypeScript, Vite, React Router, and Tailwind CSS

**What You'll Learn:**
- Configuring PrompTrek for frontend projects
- Setting up TypeScript-specific guidelines
- Using variables for project customization
- Generating configurations for multiple editors

## Complete Configuration

```yaml
# yaml-language-server: $schema=https://promptrek.ai/schema/v3.1.0.json
schema_version: "3.1.0"
metadata:
  title: React TypeScript Project
  description: AI coding assistant configuration for React TypeScript projects
  version: 1.0.0
  author: PrompTrek
  tags:
    - react
    - typescript
    - frontend
    - web

content: |
  # React TypeScript Development Guide

  ## Project Overview
  This is a React TypeScript project using modern best practices and tools.

  **Tech Stack:**
  - React 18+ with TypeScript
  - Vite for build tooling
  - React Router for navigation
  - TanStack Query for data fetching
  - Tailwind CSS for styling

  ## Code Style Guidelines

  ### Component Structure
  - Use functional components with hooks
  - Prefer named exports over default exports
  - Keep components small and focused (< 200 lines)
  - Extract complex logic into custom hooks

  ### TypeScript Best Practices
  - Enable strict mode in tsconfig.json
  - Avoid `any` type - use `unknown` or proper types
  - Use interface for object shapes, type for unions/intersections
  - Leverage type inference where possible

  ### File Organization
  ```
  src/
    components/     # Reusable UI components
    features/       # Feature-specific code
    hooks/          # Custom React hooks
    utils/          # Pure utility functions
    types/          # Shared TypeScript types
  ```

  ## Component Example

  ```tsx
  // components/UserCard.tsx
  interface UserCardProps {
    userId: string;
    onSelect?: (userId: string) => void;
  }

  export function UserCard({ userId, onSelect }: UserCardProps) {
    const { data: user, isLoading } = useUser(userId);

    if (isLoading) return <Skeleton />;
    if (!user) return null;

    return (
      <div className="p-4 border rounded-lg">
        <h3 className="text-lg font-semibold">{user.name}</h3>
        <p className="text-gray-600">{user.email}</p>
        {onSelect && (
          <button onClick={() => onSelect(userId)}>
            Select User
          </button>
        )}
      </div>
    );
  }
  ```

  ## Custom Hook Example

  ```tsx
  // hooks/useUser.ts
  import { useQuery } from '@tanstack/react-query';

  export function useUser(userId: string) {
    return useQuery({
      queryKey: ['user', userId],
      queryFn: () => fetchUser(userId),
      staleTime: 5 * 60 * 1000, // 5 minutes
    });
  }
  ```

  ## Testing
  - Use Vitest for unit tests
  - Use React Testing Library for component tests
  - Test user interactions, not implementation details
  - Aim for meaningful test coverage (focus on critical paths)

  ## Performance
  - Use React.memo() for expensive components
  - Implement code splitting with lazy() and Suspense
  - Optimize images with proper formats and lazy loading
  - Monitor bundle size with Vite's build analyzer

  ## Accessibility
  - Use semantic HTML elements
  - Include ARIA labels for interactive elements
  - Ensure keyboard navigation works
  - Test with screen readers

variables:
  PROJECT_NAME: my-react-app
  API_URL: https://api.example.com
```

## Configuration Breakdown

### Metadata Section

```yaml
metadata:
  title: React TypeScript Project
  description: AI coding assistant configuration for React TypeScript projects
  version: 1.0.0
  author: PrompTrek
  tags:
    - react
    - typescript
    - frontend
    - web
```

**Purpose:** Provides metadata about your configuration for organization and discovery.

- `title`: Clear identifier for the configuration
- `description`: What this configuration is for
- `version`: Track configuration changes over time
- `tags`: Categorize for filtering and search

### Content Section

The `content` field contains the actual guidelines and instructions for your AI assistant.

**Key Sections:**

1. **Project Overview** - Tech stack and architecture overview
2. **Code Style Guidelines** - Conventions and patterns to follow
3. **Code Examples** - Concrete examples of good patterns
4. **Testing** - Testing philosophy and tools
5. **Performance** - Optimization guidelines
6. **Accessibility** - A11y requirements

### Variables Section

```yaml
variables:
  PROJECT_NAME: my-react-app
  API_URL: https://api.example.com
```

**Usage:** Variables allow you to customize the configuration without editing the content.

**Override at generation time:**

```bash
promptrek generate react-config.promptrek.yaml --editor cursor \
  -V PROJECT_NAME=my-awesome-app \
  -V API_URL=https://api.production.com
```

## Usage Instructions

### Step 1: Save the Configuration

Save the complete configuration above to `react-project.promptrek.yaml`.

### Step 2: Validate

```bash
promptrek validate react-project.promptrek.yaml
```

### Step 3: Generate Editor Configurations

```bash
# For GitHub Copilot
promptrek generate react-project.promptrek.yaml --editor copilot

# For Cursor
promptrek generate react-project.promptrek.yaml --editor cursor

# For all configured editors
promptrek generate react-project.promptrek.yaml --all
```

### Step 4: Customize for Your Project

Edit the configuration to match your specific needs:

- Update tech stack in the overview
- Add/remove code style guidelines
- Include project-specific patterns
- Add custom variables

## Generated Files

### GitHub Copilot

**File:** `.github/copilot-instructions.md`

```markdown
# React TypeScript Development Guide

## Project Overview
This is a React TypeScript project using modern best practices and tools.

**Tech Stack:**
- React 18+ with TypeScript
- Vite for build tooling
...
```

### Cursor

**Files:**
- `.cursor/rules/index.mdc` - Main rules file with metadata
- `AGENTS.md` - Project overview

The `.cursor/rules/index.mdc` includes frontmatter:

```yaml
---
alwaysApply: true
tags:
  - react
  - typescript
  - frontend
---

# React TypeScript Development Guide
...
```

### Continue

**File:** `.continue/rules/react-typescript-project.md`

```markdown
# React TypeScript Development Guide

## Project Overview
...
```

## Editor-Specific Tips

### GitHub Copilot

!!! tip "Path-Specific Instructions"
    Create additional instructions for specific directories:

    ```bash
    # Add component-specific rules
    promptrek generate --editor copilot \
      --path components \
      --output .github/instructions/components.instructions.md
    ```

### Cursor

!!! tip "Always Attached Rules"
    Cursor's `alwaysApply: true` metadata ensures rules are always active. Use `always_apply: false` in documents for path-specific rules.

### Continue

!!! tip "Multiple Rule Files"
    Continue supports multiple rule files. Split guidelines by concern:
    - `react-guidelines.md`
    - `typescript-guidelines.md`
    - `testing-guidelines.md`

## Advanced Customization

### Multi-Document Configuration

For path-specific rules, use the `documents` field:

```yaml
schema_version: "3.1.0"
metadata:
  title: React TypeScript Project

content: |
  # General Guidelines
  - Write clean, maintainable code

# TypeScript-specific rules
documents:
  - name: typescript-strict
    content: |
      # Strict TypeScript Rules
      - No `any` types allowed
      - All functions must have return types
      - Enable all strict checks in tsconfig
    file_globs: "**/*.{ts,tsx}"
    always_apply: false

  - name: component-rules
    content: |
      # Component Guidelines
      - Props must be fully typed
      - Use functional components only
      - Extract logic to custom hooks
    file_globs: "src/components/**/*.tsx"
    always_apply: false
```

### With Testing Configuration

Add testing-specific guidelines:

```yaml
documents:
  - name: testing
    content: |
      # Testing Guidelines

      ## Test Structure
      - Arrange, Act, Assert pattern
      - One assertion per test when possible
      - Clear test descriptions

      ## React Testing Library
      ```tsx
      test('displays user information', async () => {
        // Arrange
        const user = { name: 'John', email: 'john@example.com' };

        // Act
        render(<UserCard user={user} />);

        // Assert
        expect(screen.getByText('John')).toBeInTheDocument();
        expect(screen.getByText('john@example.com')).toBeInTheDocument();
      });
      ```
    file_globs: "**/*.{test,spec}.{ts,tsx}"
    always_apply: false
```

## Real-World Customization

### For a Specific Project

```yaml
variables:
  PROJECT_NAME: my-ecommerce-app
  API_URL: https://api.mystore.com
  STRIPE_PUBLIC_KEY: pk_test_xxxxx
  GA_TRACKING_ID: UA-XXXXX-X

content: |
  # E-Commerce App Development Guide

  ## Project-Specific Context
  This is an e-commerce application with:
  - User authentication via Auth0
  - Payment processing with Stripe
  - Analytics via Google Analytics
  - Product catalog from custom API

  ## Special Considerations
  - All payment flows must be PCI compliant
  - User data must be handled per GDPR
  - Track key user events for analytics
```

## Best Practices

### Do's

- Include code examples for complex patterns
- Document the "why" behind guidelines, not just "what"
- Keep guidelines focused and actionable
- Update configuration as project evolves
- Use variables for environment-specific values

### Don'ts

- Don't include overly generic advice
- Don't make rules too strict - allow flexibility
- Don't forget to update examples when patterns change
- Don't include sensitive data in the configuration (use variables)

## Related Examples

- **[Node.js API](node-api.md)** - Backend API example
- **[NX Monorepo](../advanced/monorepo.md)** - Large-scale project structure
- **[Custom Commands](../plugins/custom-commands.md)** - Add testing commands

## Troubleshooting

### Issue: Generated files not updating

**Solution:** Clear editor cache and regenerate:

```bash
# Remove old files
rm -rf .cursor/ .github/copilot-instructions.md

# Regenerate
promptrek generate react-project.promptrek.yaml --all
```

### Issue: Variables not substituting

**Solution:** Ensure you're using the correct syntax `{{{ VARIABLE_NAME }}}` with triple braces.

### Issue: TypeScript guidelines too strict

**Solution:** Adjust the guidelines to match your team's preferences:

```yaml
content: |
  ## TypeScript Best Practices
  - Prefer explicit types for public APIs
  - Type inference is acceptable for internal implementation
  - Use `any` sparingly with a comment explaining why
```

## Additional Resources

- [React Official Docs](https://react.dev/)
- [TypeScript Handbook](https://www.typescriptlang.org/docs/)
- [Vite Guide](https://vitejs.dev/guide/)
- [React Testing Library](https://testing-library.com/react)

---

**Next Steps:**
1. Customize the configuration for your project
2. Generate files for your preferred editor
3. Share with your team
4. Iterate based on feedback
