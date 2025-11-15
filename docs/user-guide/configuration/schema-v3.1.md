# Schema v3.1.0 Detailed Guide

Schema v3.1.0 is the latest version of the Universal Prompt Format (UPF), introducing multi-step workflow support and enhanced agent capabilities.

## Overview

v3.1.0 builds on v3.0.0 by adding:

- **Multi-step workflows** for complex command orchestration
- **Tool call tracking** to specify which tools workflows use
- **Enhanced agent prompts** with full markdown support
- **Workflow steps** for structured execution flows
- **100% backward compatibility** with v3.0.0

## Schema Declaration

Always start your PrompTrek file with the schema version:

```yaml
schema_version: "3.1.0"
```

## Top-Level Structure

```yaml
schema_version: "3.1.0"          # Required: Schema version
metadata:                         # Required: File metadata
  title: "Project Name"
  description: "Brief description"
  # ... additional metadata fields

content: |                        # Required: Main markdown content
  # Your project guidelines
  ...

# Optional top-level fields
content_description: "Main guidelines description"
content_always_apply: true
variables: {}                     # Template variables
documents: []                     # Additional documents

# Plugin configurations (top-level in v3.x)
mcp_servers: []                   # MCP server configurations
commands: []                      # Slash commands and workflows
agents: []                        # Autonomous agents
hooks: []                         # Event-driven hooks

ignore_editor_files: true         # Auto-manage .gitignore
```

## New in v3.1: Multi-Step Workflows

### Simple Commands vs Workflows

v3.1.0 distinguishes between simple commands and complex workflows:

#### Simple Command (v3.0 style)

```yaml
commands:
  - name: review-code
    description: "Quick code review"
    prompt: |
      Review the selected code for:
      - Code quality
      - Best practices
      - Security issues
```

#### Multi-Step Workflow (v3.1 new)

```yaml
commands:
  - name: comprehensive-review
    description: "Full code review workflow"
    multi_step: true              # Mark as workflow
    tool_calls:                   # Tools this workflow uses
      - read_file
      - run_tests
      - gh
    prompt: |
      Perform a comprehensive code review:

      ## Steps
      1. Read and analyze the code
      2. Run automated tests
      3. Check GitHub PR comments
      4. Generate review summary
    steps:                        # Structured execution steps
      - name: analyze
        action: read_file
        description: "Read and analyze code"
        params:
          pattern: "**/*.py"

      - name: test
        action: execute_command
        description: "Run test suite"
        params:
          command: "pytest tests/"

      - name: check-pr
        action: gh_api_call
        description: "Check PR comments"
        params:
          endpoint: "pulls/{{PR_NUMBER}}/comments"
        conditions:
          env_var: "PR_NUMBER"
```

### Workflow Fields

#### `multi_step` (boolean)

Marks a command as a multi-step workflow:

```yaml
commands:
  - name: deploy-workflow
    multi_step: true              # This is a workflow, not a simple command
    # ...
```

#### `tool_calls` (array of strings)

Specifies which tools/commands the workflow uses:

```yaml
commands:
  - name: release-workflow
    multi_step: true
    tool_calls:
      - git                       # Git operations
      - npm                       # Package management
      - gh                        # GitHub CLI
      - read_file                 # File reading
      - write_file                # File writing
```

This helps AI editors:
- Prepare necessary tools
- Validate tool availability
- Request permissions upfront

#### `steps` (array of WorkflowStep)

Structured workflow execution steps:

```yaml
steps:
  - name: build                   # Step identifier
    action: execute_command       # Action type
    description: "Build project"  # Human-readable description
    params:                       # Action-specific parameters
      command: "npm run build"
    conditions:                   # Optional execution conditions
      file_exists: "package.json"
```

**WorkflowStep fields**:

- `name` (string, required): Step identifier
- `action` (string, required): Action to perform
- `description` (string, optional): Human-readable description
- `params` (object, optional): Parameters for the action
- `conditions` (object, optional): Execution conditions

**Common actions**:

- `read_file`: Read files
- `write_file`: Write files
- `execute_command`: Run shell commands
- `git_operation`: Git operations
- `gh_api_call`: GitHub API calls
- `validate`: Validation steps
- `test`: Test execution

## New in v3.1: Enhanced Agent Prompts

### Agent Prompt Field

v3.1.0 introduces the `prompt` field for agents, providing full markdown instructions:

```yaml
agents:
  - name: test-generator
    description: "Automated test generation"
    prompt: |                     # New in v3.1: Full markdown prompt
      # Test Generation Agent

      You are a specialized test generation agent. Your role is to create
      comprehensive, maintainable test suites.

      ## Guidelines

      - Use Jest and React Testing Library
      - Aim for 100% code coverage
      - Include edge cases and error scenarios
      - Write descriptive test names
      - Follow AAA pattern (Arrange, Act, Assert)

      ## Test Structure

      ```javascript
      describe('ComponentName', () => {
        it('should handle expected behavior', () => {
          // Test implementation
        });
      });
      ```

      ## Context

      - Testing framework: {{{ TESTING_FRAMEWORK }}}
      - Coverage target: {{{ COVERAGE_TARGET }}}%

    tools:
      - file_read
      - file_write
      - run_tests
    trust_level: partial
    requires_approval: true
```

### Deprecated: system_prompt

The old `system_prompt` field (v3.0) still works but is deprecated:

```yaml
# v3.0 style (still supported)
agents:
  - name: old-agent
    description: "Agent description"
    system_prompt: "Brief system instructions"

# v3.1 style (recommended)
agents:
  - name: new-agent
    description: "Agent description"
    prompt: |
      # Full Markdown Instructions
      Detailed guidelines and context...
```

!!! tip "Migration from system_prompt"
    Simply rename `system_prompt` to `prompt` and enhance with markdown formatting for better agent instructions.

## Complete v3.1.0 Example

```yaml
schema_version: "3.1.0"

metadata:
  title: "Full-Stack TypeScript Project"
  description: "Complete v3.1.0 configuration example"
  version: "1.0.0"
  author: "Development Team"
  tags: [typescript, react, node, testing]
  created: "2024-01-15"
  updated: "2024-01-15"

content: |
  # Full-Stack TypeScript Project

  ## Overview
  Modern TypeScript application with React frontend and Node.js backend.

  ## Development Guidelines

  ### Code Quality
  - TypeScript strict mode enabled
  - 90%+ test coverage required
  - ESLint and Prettier enforced
  - No `any` types without justification

  ### Architecture
  - Clean Architecture principles
  - Domain-driven design
  - SOLID principles
  - Dependency injection

variables:
  PROJECT_NAME: "my-fullstack-app"
  NODE_VERSION: "20"
  TESTING_FRAMEWORK: "jest"
  COVERAGE_TARGET: "90"
  GITHUB_TOKEN: "ghp_your_token"

# MCP Servers (top-level)
mcp_servers:
  - name: github
    command: npx
    args: ["-y", "@modelcontextprotocol/server-github"]
    env:
      GITHUB_TOKEN: "{{{ GITHUB_TOKEN }}}"
    description: "GitHub API integration"
    trust_metadata:
      trusted: true
      trust_level: full

  - name: filesystem
    command: npx
    args: ["-y", "@modelcontextprotocol/server-filesystem", "./src", "./tests"]
    description: "Filesystem access"
    trust_metadata:
      trusted: true
      trust_level: partial

# Commands and Workflows (top-level)
commands:
  # Simple command
  - name: review-code
    description: "Quick code review"
    prompt: |
      Review the selected code for:
      - TypeScript best practices
      - Type safety
      - Code duplication
      - Performance issues
    output_format: markdown
    requires_approval: false

  # Multi-step workflow (v3.1 feature)
  - name: release-workflow
    description: "Complete release workflow"
    multi_step: true
    tool_calls:
      - git
      - npm
      - gh
      - run_tests
    prompt: |
      # Release Workflow

      Execute a complete release process:

      ## Steps
      1. Validate working directory is clean
      2. Run full test suite with coverage
      3. Build production artifacts
      4. Update version number
      5. Create git tag
      6. Push to GitHub
      7. Create GitHub release

      ## Requirements
      - All tests must pass
      - Coverage must be ≥ {{{ COVERAGE_TARGET }}}%
      - No uncommitted changes
      - Must be on main branch

    steps:
      - name: validate
        action: git_operation
        description: "Check working directory is clean"
        params:
          operation: status
        conditions:
          clean: true

      - name: test
        action: execute_command
        description: "Run test suite"
        params:
          command: "npm test -- --coverage"
        conditions:
          exit_code: 0

      - name: build
        action: execute_command
        description: "Build production artifacts"
        params:
          command: "npm run build:prod"

      - name: version
        action: execute_command
        description: "Update version"
        params:
          command: "npm version {{{ VERSION_TYPE }}}"

      - name: tag
        action: git_operation
        description: "Create git tag"
        params:
          operation: tag
          message: "Release v{{{ VERSION }}}"

      - name: push
        action: git_operation
        description: "Push to GitHub"
        params:
          operation: push
          tags: true

      - name: release
        action: gh_api_call
        description: "Create GitHub release"
        params:
          endpoint: "repos/{{{ REPO_OWNER }}}/{{{ REPO_NAME }}}/releases"
          method: POST
          body:
            tag_name: "v{{{ VERSION }}}"
            name: "Release v{{{ VERSION }}}"
            draft: false

# Agents (top-level)
agents:
  # Enhanced agent with v3.1 prompt field
  - name: test-generator
    description: "Automated test generation"
    prompt: |
      # Test Generation Agent

      You are a specialized agent for generating comprehensive test suites
      for TypeScript applications.

      ## Your Expertise

      - Jest and React Testing Library
      - Integration and unit testing
      - Mocking and stubbing
      - Test coverage optimization

      ## Guidelines

      ### Test Structure
      ```typescript
      describe('ComponentName', () => {
        describe('method/feature', () => {
          it('should handle expected case', () => {
            // Arrange
            // Act
            // Assert
          });

          it('should handle error case', () => {
            // Test error scenarios
          });
        });
      });
      ```

      ### Coverage Requirements
      - Target: {{{ COVERAGE_TARGET }}}%
      - Test all public methods
      - Cover edge cases and errors
      - Test component lifecycle

      ### Best Practices
      - Descriptive test names
      - Single assertion focus
      - Proper cleanup
      - Avoid test interdependence

    tools:
      - file_read
      - file_write
      - run_tests
    trust_level: partial
    requires_approval: true
    context:
      framework: "jest"
      coverage_target: 90

  - name: refactoring-assistant
    description: "Code refactoring helper"
    prompt: |
      # Refactoring Assistant

      Guide developers through safe, incremental code refactoring.

      ## Approach
      1. Analyze current code structure
      2. Identify refactoring opportunities
      3. Propose incremental changes
      4. Verify tests pass after each step
      5. Document changes

      ## Principles
      - Preserve existing behavior
      - Incremental changes
      - Test-driven refactoring
      - Clear communication

    tools:
      - file_read
      - file_write
      - run_tests
      - git_operation
    trust_level: partial
    requires_approval: true

# Hooks (top-level)
hooks:
  - name: pre-commit
    event: pre-commit
    command: "npm run lint && npm test"
    description: "Lint and test before commit"
    conditions:
      path: "**/*.{ts,tsx}"
    requires_reapproval: false

  - name: pre-push
    event: pre-push
    command: "npm run build && npm test -- --coverage"
    description: "Build and test before push"
    requires_reapproval: false

# Additional documents
documents:
  - name: testing-guidelines
    description: "Testing standards and practices"
    content: |
      # Testing Guidelines

      ## Unit Tests
      - Test individual functions/components
      - Mock external dependencies
      - Fast execution (< 100ms per test)

      ## Integration Tests
      - Test component interactions
      - Use real implementations when possible
      - Database/API mocking

      ## E2E Tests
      - Critical user flows only
      - Slower execution acceptable
      - Realistic test data

  - name: typescript-patterns
    description: "TypeScript patterns and practices"
    file_globs: "**/*.{ts,tsx}"
    always_apply: false
    content: |
      # TypeScript Patterns

      ## Type Safety
      - Avoid `any` - use `unknown` or generics
      - Prefer interfaces for objects
      - Use strict null checks

      ## Advanced Types
      - Conditional types for complex logic
      - Mapped types for transformations
      - Template literal types for strings

ignore_editor_files: true
```

## Workflow Use Cases

### CI/CD Pipeline Workflow

```yaml
commands:
  - name: ci-pipeline
    description: "Complete CI/CD pipeline"
    multi_step: true
    tool_calls: [git, npm, run_tests, gh]
    prompt: |
      Execute full CI/CD pipeline with quality gates.
    steps:
      - name: install
        action: execute_command
        params:
          command: "npm ci"

      - name: lint
        action: execute_command
        params:
          command: "npm run lint"

      - name: test
        action: execute_command
        params:
          command: "npm test -- --coverage"

      - name: build
        action: execute_command
        params:
          command: "npm run build"

      - name: deploy
        action: execute_command
        params:
          command: "npm run deploy"
        conditions:
          branch: "main"
```

### Code Generation Workflow

```yaml
commands:
  - name: generate-crud
    description: "Generate CRUD operations"
    multi_step: true
    tool_calls: [file_read, file_write, run_tests]
    prompt: |
      Generate complete CRUD operations for a new entity.
    steps:
      - name: read-template
        action: read_file
        params:
          path: "templates/crud.template.ts"

      - name: generate-model
        action: write_file
        description: "Create model file"

      - name: generate-service
        action: write_file
        description: "Create service file"

      - name: generate-tests
        action: write_file
        description: "Create test file"

      - name: verify
        action: run_tests
        description: "Verify generated code"
```

## Migration from v3.0 to v3.1

### Minimal Migration

v3.0 files work perfectly in v3.1 without changes:

```yaml
# v3.0 file works as-is in v3.1
schema_version: "3.0.0"  # Can keep v3.0.0
# ... rest of configuration
```

### Adding v3.1 Features

To use v3.1 features, update schema version and add workflow fields:

```yaml
# Update schema version
schema_version: "3.1.0"

commands:
  # Existing simple commands remain unchanged
  - name: review
    description: "Code review"
    prompt: "Review code..."

  # Add new workflow features
  - name: deploy
    description: "Deployment workflow"
    multi_step: true              # Add this
    tool_calls: [git, npm]        # Add this
    prompt: |
      Deploy application...
    steps:                        # Add this
      - name: build
        action: execute_command
        params:
          command: "npm run build"
```

### Upgrading Agents

```yaml
agents:
  # v3.0 style (still works)
  - name: old-agent
    description: "Agent"
    system_prompt: "Brief instructions"

  # v3.1 style (enhanced)
  - name: new-agent
    description: "Agent"
    prompt: |                     # Renamed and enhanced
      # Agent Instructions
      Detailed markdown content...
```

## Validation

Validate v3.1.0 files:

```bash
# Basic validation
promptrek validate project.promptrek.yaml

# Verbose validation with schema details
promptrek --verbose validate project.promptrek.yaml
```

## Best Practices

!!! tip "Use Workflows for Complex Tasks"
    Use `multi_step: true` for any command that:
    - Executes multiple operations
    - Has dependencies between steps
    - Needs conditional execution
    - Requires multiple tools

!!! tip "Document Tool Calls"
    Always specify `tool_calls` for workflows to help AI editors prepare the necessary tools.

!!! tip "Rich Agent Prompts"
    Use the new `prompt` field with full markdown to provide comprehensive agent instructions, including examples and context.

!!! warning "Backward Compatibility"
    While v3.1 is backward compatible with v3.0, v3.0 tools cannot parse v3.1 workflow features.

## See Also

- [Schema Versions Overview](schema-versions.md)
- [Metadata Configuration](metadata.md)
- [Variables System](variables.md)
- [v3.1.0 Schema Reference](../../schema/v3.1.0.md)
- [Migration Guide](../../user-guide/workflows/migration.md)
