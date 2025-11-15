# Custom Commands Example

This example demonstrates how to configure custom slash commands for AI editors using PrompTrek.

## Overview

**Use Case:** Create reusable slash commands for common development tasks

**What You'll Learn:**
- Defining custom commands in PrompTrek
- Command structure and options
- Using commands in AI editors
- Best practices for command design

## What are Custom Commands?

Custom commands (slash commands) are predefined prompts that can be invoked with a simple `/command-name` syntax in AI editors.

**Benefits:**
- **Consistency** - Same prompt every time
- **Efficiency** - No need to retype complex prompts
- **Shareability** - Distribute commands across team
- **Discoverability** - Commands appear in editor autocomplete

**Supported Editors:**
- Claude Code (full support with `.claude/commands/*.md`)
- Cursor (partial support)
- Continue (custom slash commands)

## Complete Configuration

```yaml
# yaml-language-server: $schema=https://promptrek.ai/schema/v3.1.0.json
schema_version: "3.1.0"
metadata:
  title: Custom Commands Example
  description: Reusable slash commands for development workflow
  version: 1.0.0
  author: PrompTrek Team
  tags: [commands, workflow, automation]

content: |
  # Development Workflow Commands

  This project includes custom commands for common tasks:
  - `/review-pr` - Code review
  - `/generate-tests` - Test generation
  - `/write-docs` - Documentation
  - `/security-audit` - Security scan

  Use these commands in your AI editor by typing `/command-name`.

# Custom slash commands
commands:
  # Code review command
  - name: review-pr
    description: Perform comprehensive code review
    prompt: |
      Review the pull request with the following criteria:

      **Code Quality:**
      - Adherence to coding standards and best practices
      - Code readability and maintainability
      - Proper error handling
      - Appropriate use of design patterns

      **Testing:**
      - Adequate test coverage
      - Edge cases handled
      - Tests are meaningful and not trivial

      **Documentation:**
      - Code is well-documented
      - README updated if needed
      - API changes documented

      **Security:**
      - No security vulnerabilities
      - Input validation present
      - Authentication/authorization correct

      **Performance:**
      - No obvious performance issues
      - Efficient algorithms used
      - Database queries optimized

      Provide a structured review with sections for each criterion.
    output_format: markdown
    requires_approval: false
    examples:
      - "/review-pr #123"
      - "/review-pr https://github.com/org/repo/pull/456"
    trust_metadata:
      trusted: true
      trust_level: full
      source: local

  # Test generation command
  - name: generate-tests
    description: Generate comprehensive unit tests
    prompt: |
      Generate unit tests for the provided code with:
      - Test cases for normal operation
      - Edge case testing
      - Error condition handling
      - Mocking external dependencies
      - Clear test descriptions
      - Good code coverage

      Use the project's testing framework and follow existing test patterns.
    output_format: code
    requires_approval: false
    examples:
      - "/generate-tests src/utils/parser.ts"
      - "/generate-tests --coverage=90 src/api/handler.py"

  # Documentation generation command
  - name: write-docs
    description: Generate comprehensive documentation
    prompt: |
      Generate documentation including:
      - Overview and purpose
      - API reference
      - Usage examples
      - Configuration options
      - Common pitfalls
      - Links to related documentation

      Use the project's documentation format (JSDoc, Python docstrings, etc.).
    output_format: markdown
    requires_approval: false

  # Security audit command
  - name: security-audit
    description: Perform security vulnerability scan
    prompt: |
      Analyze the code for security vulnerabilities:
      - SQL injection risks
      - XSS vulnerabilities
      - CSRF protection
      - Authentication/authorization issues
      - Sensitive data exposure
      - Dependency vulnerabilities
      - Secure configuration

      Provide severity ratings and remediation steps.
    requires_approval: true
    trust_metadata:
      trusted: true
      requires_approval: true

  # Refactoring command
  - name: refactor
    description: Suggest refactoring improvements
    prompt: |
      Analyze the code and suggest refactoring improvements:

      **Code Structure:**
      - Extract complex functions into smaller ones
      - Identify repeated code for extraction
      - Suggest better naming

      **Design Patterns:**
      - Identify applicable design patterns
      - Suggest architectural improvements

      **Performance:**
      - Identify performance bottlenecks
      - Suggest optimizations

      Provide specific, actionable recommendations.

  # API endpoint generator
  - name: create-endpoint
    description: Generate REST API endpoint
    prompt: |
      Create a new REST API endpoint with:

      **Files to Generate:**
      - Route handler
      - Controller with business logic
      - Service layer for data access
      - Request/response DTOs
      - Validation schema (Zod/class-validator)
      - Unit tests
      - Integration tests

      **Include:**
      - Proper error handling
      - TypeScript types
      - OpenAPI/Swagger documentation
      - Authentication middleware
```

## Configuration Breakdown

### Command Structure

Each command includes:

```yaml
- name: command-name           # Used as /command-name
  description: "What it does"  # Shown in autocomplete
  prompt: |                    # The actual prompt
    Detailed instructions...
  output_format: markdown      # Expected output format
  requires_approval: false     # Security setting
  examples: [...]              # Usage examples
  trust_metadata: {...}        # Trust configuration
```

### Command Fields

**name** (required)
- Used to invoke: `/command-name`
- Must be unique
- Use kebab-case

**description** (required)
- Short description for autocomplete
- Keep under 80 characters

**prompt** (required)
- The actual prompt sent to AI
- Can be multi-line with markdown
- Include clear, specific instructions

**output_format** (optional)
- `markdown` - Formatted documentation
- `code` - Code output
- `json` - Structured data
- `text` - Plain text

**requires_approval** (optional)
- `true` - User must approve before execution
- `false` - Runs immediately (default)

**examples** (optional)
- Show usage examples
- Helpful for autocomplete

## Usage Instructions

### Step 1: Save Configuration

Save to `commands.promptrek.yaml`.

### Step 2: Generate Command Files

```bash
# For Claude Code
promptrek plugins generate commands.promptrek.yaml --editor claude

# For all supported editors
promptrek plugins generate commands.promptrek.yaml --all
```

### Step 3: Use in Editor

**Claude Code:**
```
/review-pr #123
/generate-tests src/utils/parser.ts
/write-docs
```

**Continue:**
```
/review-pr
/security-audit src/auth/
```

### Step 4: Verify Generated Files

**Claude Code:** `.claude/commands/*.md`

```
.claude/
  commands/
    review-pr.md
    generate-tests.md
    write-docs.md
    security-audit.md
```

Each file contains:
```markdown
# review-pr

Perform comprehensive code review

## Prompt

Review the pull request with the following criteria:
...
```

## Command Categories

### Code Review Commands

```yaml
commands:
  - name: review-pr
    description: Full PR review
    prompt: |
      Review focusing on code quality, testing, security, and performance.

  - name: review-security
    description: Security-focused review
    prompt: |
      Security review focusing on:
      - Authentication/authorization
      - Input validation
      - Data exposure
      - Dependency vulnerabilities

  - name: review-performance
    description: Performance review
    prompt: |
      Performance review focusing on:
      - Algorithm efficiency
      - Database queries
      - Memory usage
      - Network requests
```

### Code Generation Commands

```yaml
commands:
  - name: generate-component
    description: Generate React component
    prompt: |
      Generate a React component with:
      - TypeScript types
      - Props interface
      - JSDoc comments
      - Unit tests
      - Storybook story

  - name: generate-api
    description: Generate API endpoint
    prompt: |
      Generate REST API endpoint with:
      - Route handler
      - Controller
      - Service layer
      - DTOs
      - Tests

  - name: generate-tests
    description: Generate unit tests
    prompt: |
      Generate comprehensive unit tests with:
      - Normal cases
      - Edge cases
      - Error conditions
      - Mocking
```

### Documentation Commands

```yaml
commands:
  - name: write-docs
    description: Generate documentation
    prompt: |
      Generate comprehensive documentation.

  - name: write-readme
    description: Generate README
    prompt: |
      Generate README.md with:
      - Project overview
      - Installation instructions
      - Usage examples
      - API reference
      - Contributing guidelines

  - name: write-changelog
    description: Generate changelog entry
    prompt: |
      Generate changelog entry following Keep a Changelog format.
```

### Refactoring Commands

```yaml
commands:
  - name: refactor
    description: Suggest refactoring
    prompt: |
      Analyze and suggest refactoring improvements.

  - name: extract-function
    description: Extract function
    prompt: |
      Extract the selected code into a well-named function.

  - name: simplify
    description: Simplify code
    prompt: |
      Simplify the code while maintaining functionality.
```

## Advanced Examples

### Project-Specific Commands

```yaml
# E-commerce project commands
commands:
  - name: create-product
    description: Generate product model
    prompt: |
      Create a product model for our e-commerce platform:

      **Required Fields:**
      - id: UUID
      - name: string (2-200 chars)
      - description: text
      - price: decimal (2 places)
      - currency: ISO 4217 code
      - inventory: integer
      - category: reference to Category
      - images: array of URLs
      - createdAt: timestamp
      - updatedAt: timestamp

      **Include:**
      - TypeScript interfaces
      - Prisma schema
      - Validation schema (Zod)
      - Factory for tests

  - name: payment-integration
    description: Add payment processing
    prompt: |
      Implement Stripe payment processing:

      **Requirements:**
      - Create payment intent
      - Handle webhooks
      - Update order status
      - Handle failures gracefully
      - Log all transactions
      - PCI compliance

      **Files:**
      - Payment service
      - Webhook handler
      - Types/interfaces
      - Tests
```

### Framework-Specific Commands

```yaml
# React/Next.js commands
commands:
  - name: create-page
    description: Generate Next.js page
    prompt: |
      Create a Next.js page with:
      - Server component (default)
      - TypeScript
      - SEO metadata
      - Error boundary
      - Loading state

  - name: create-api-route
    description: Generate API route
    prompt: |
      Create Next.js API route with:
      - Route handler
      - Request validation
      - Error handling
      - TypeScript types
      - Rate limiting

# NestJS commands
commands:
  - name: create-module
    description: Generate NestJS module
    prompt: |
      Create NestJS module with:
      - Module definition
      - Controller
      - Service
      - DTOs
      - Tests for each
```

### Workflow Commands

```yaml
commands:
  - name: prepare-release
    description: Prepare release checklist
    prompt: |
      Generate release preparation checklist:

      - [ ] All tests passing
      - [ ] Documentation updated
      - [ ] CHANGELOG.md updated
      - [ ] Version bumped
      - [ ] Dependencies updated
      - [ ] Security scan clean
      - [ ] Performance benchmarks
      - [ ] Migration scripts (if needed)

  - name: onboard
    description: Onboarding checklist
    prompt: |
      Generate onboarding checklist for new developers:

      - [ ] Clone repository
      - [ ] Install dependencies
      - [ ] Configure environment
      - [ ] Run tests
      - [ ] Start development server
      - [ ] Review architecture docs
      - [ ] Understand Git workflow
```

## Best Practices

### Writing Effective Commands

!!! tip "Be Specific"
    Provide clear, detailed instructions:

    **Good:**
    ```yaml
    prompt: |
      Generate unit tests with:
      - Arrange, Act, Assert pattern
      - Mock external dependencies
      - Test normal and error cases
      - Use descriptive test names
    ```

    **Bad:**
    ```yaml
    prompt: "Write some tests"
    ```

### Command Naming

!!! tip "Clear Names"
    Use descriptive, action-oriented names:

    - `review-pr` ✅ not `review` ❌
    - `generate-tests` ✅ not `tests` ❌
    - `security-audit` ✅ not `audit` ❌

### Security

!!! warning "Approval for Dangerous Operations"
    Require approval for commands that:
    - Modify files
    - Make API calls
    - Access sensitive data

    ```yaml
    - name: delete-files
      requires_approval: true
      trust_metadata:
        requires_approval: true
    ```

## Troubleshooting

### Commands Not Appearing

**Problem:** Commands don't show in autocomplete

**Solutions:**
1. Verify files generated: `ls .claude/commands/`
2. Restart editor
3. Check command name format (kebab-case)

### Command Not Working as Expected

**Problem:** Command gives poor results

**Solutions:**
1. Review prompt clarity
2. Add more specific instructions
3. Include examples in prompt
4. Test with different inputs

## Real-World Example: Full Development Workflow

```yaml
schema_version: "3.1.0"
metadata:
  title: Complete Development Workflow

commands:
  # Planning
  - name: break-down-task
    description: Break feature into tasks
    prompt: |
      Break down this feature into implementation tasks:
      - List all components/files needed
      - Identify dependencies
      - Estimate complexity
      - Suggest implementation order

  # Implementation
  - name: implement-feature
    description: Implement feature
    prompt: |
      Implement the feature following our guidelines:
      - TypeScript with strict mode
      - Comprehensive error handling
      - Unit tests (>80% coverage)
      - Documentation

  # Testing
  - name: generate-tests
    description: Generate tests
    prompt: |
      Generate tests covering:
      - Happy path
      - Edge cases
      - Error conditions
      - Integration scenarios

  # Review
  - name: self-review
    description: Self-review checklist
    prompt: |
      Self-review checklist:
      - [ ] Tests passing
      - [ ] No console.logs
      - [ ] Types complete
      - [ ] Documentation updated
      - [ ] No TODOs
      - [ ] Performance acceptable

  # Documentation
  - name: update-docs
    description: Update documentation
    prompt: |
      Update documentation for this change:
      - API reference
      - Usage examples
      - Migration guide (if breaking)
      - Changelog entry
```

## Related Examples

- **[MCP Servers](mcp-servers.md)** - External tool integration
- **[React TypeScript](../basic/react-typescript.md)** - Frontend commands
- **[Node.js API](../basic/node-api.md)** - Backend commands

## Additional Resources

- [Claude Code Commands](https://docs.anthropic.com/claude/docs/custom-commands)
- [Continue Custom Commands](https://docs.continue.dev/customization/slash-commands)
- [Effective Prompt Engineering](https://docs.anthropic.com/claude/docs/prompt-engineering)

---

**Next Steps:**
1. Identify common workflows in your project
2. Create commands for repetitive tasks
3. Test commands with real scenarios
4. Share with team and iterate
5. Build a library of reusable commands
