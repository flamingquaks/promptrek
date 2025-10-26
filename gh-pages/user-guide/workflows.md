---
layout: default
title: Workflows
parent: User Guide
nav_order: 6
---

# Multi-Step Workflows

{: .fs-9 }

Define complex, automated multi-step procedures that can be triggered with a single command.
{: .fs-6 .fw-300 }

---

## Overview

Workflows allow you to create complex, multi-step automated procedures in your `project.promptrek.yaml` that work across all supported AI coding editors. Introduced in **schema v3.1.0**, workflows extend the existing `Command` model with optional fields for defining structured, repeatable processes.

## Quick Start

Add a workflow to your `project.promptrek.yaml`:

```yaml
schema_version: "3.1.0"

metadata:
  title: My Project
  description: Project with workflows

content: |
  # Project Guidelines
  Follow best practices...

commands:
  - name: pr-review
    multi_step: true  # This makes it a workflow
    description: Complete pull request review workflow
    prompt: |
      Review the pull request:
      1. Fetch PR details using `gh pr view`
      2. Review changed files
      3. Run tests
      4. Provide feedback
    tool_calls: [gh, read_file, execute_command]
    requires_approval: true
```

Generate for your editor:

```bash
promptrek generate project.promptrek.yaml --editor cline
```

Use the workflow:
- **Cline**: Type `/pr-review` in chat
- **Claude**: Use custom command system
- **Cursor**: Access via agent functions
- **Continue**: Type `/pr-review` in chat

## Workflow vs Command

### Simple Command

Use for single actions or prompts:

```yaml
commands:
  - name: explain-code
    description: Explain selected code
    prompt: "Analyze and explain this code in detail."
```

### Workflow

Use for multi-step procedures:

```yaml
commands:
  - name: deploy-workflow
    multi_step: true
    description: Complete deployment workflow
    prompt: |
      Deploy to production:
      1. Run tests
      2. Build artifacts
      3. Deploy to server
      4. Verify deployment
    tool_calls: [docker, kubectl, execute_command]
    requires_approval: true
```

## Workflow Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | string | ✅ Yes | Workflow identifier |
| `description` | string | ✅ Yes | Human-readable description |
| `prompt` | string | ✅ Yes | Main workflow instructions |
| `multi_step` | boolean | ⚠️ Optional | Set to `true` to mark as workflow (default: `false`) |
| `tool_calls` | list[string] | ⚠️ Optional | List of required tools |
| `requires_approval` | boolean | ⚠️ Optional | Whether to require approval (default: `false`) |
| `steps` | list[WorkflowStep] | ⚠️ Optional | Structured step definitions |
| `examples` | list[string] | ⚠️ Optional | Usage examples |

### WorkflowStep Fields

For workflows that need structured step definitions:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | string | ✅ Yes | Step identifier |
| `action` | string | ✅ Yes | Action type (e.g., `execute_command`) |
| `description` | string | ⚠️ Optional | Human-readable description |
| `params` | object | ⚠️ Optional | Action parameters |
| `conditions` | object | ⚠️ Optional | Execution conditions |

## Examples

### Code Review Workflow

```yaml
commands:
  - name: code-review
    multi_step: true
    description: Comprehensive code review checklist
    prompt: |
      # Code Review Workflow

      1. **Code Quality**
         - Check for code smells
         - Verify naming conventions

      2. **Testing**
         - Ensure tests exist
         - Verify coverage

      3. **Security**
         - Scan for vulnerabilities
         - Check dependencies

      4. **Documentation**
         - Verify docstrings
         - Check README updates

    tool_calls: [read_file, search_files, execute_command]
    requires_approval: false

    examples:
      - "Review recent changes in src/"
      - "Quick review focusing on security"
```

### Deployment Workflow with Steps

```yaml
commands:
  - name: deploy-production
    multi_step: true
    description: Deploy to production environment
    requires_approval: true

    prompt: |
      Deploy application to production:
      1. Verify all tests pass
      2. Build Docker image
      3. Push to registry
      4. Deploy to production
      5. Run smoke tests

    tool_calls: [docker, kubectl, execute_command]

    steps:
      - name: run-tests
        action: execute_command
        description: Run full test suite
        params:
          command: "make test"

      - name: build-image
        action: execute_command
        description: Build Docker image
        params:
          command: "docker build -t myapp:latest ."

      - name: push-image
        action: execute_command
        description: Push to registry
        params:
          command: "docker push myapp:latest"

      - name: deploy
        action: execute_command
        description: Deploy to Kubernetes
        params:
          command: "kubectl apply -f k8s/production/"

      - name: smoke-test
        action: execute_command
        description: Run smoke tests
        params:
          command: "make smoke-test"
```

### Database Migration Workflow

```yaml
commands:
  - name: db-migrate
    multi_step: true
    description: Safe database migration
    requires_approval: true

    prompt: |
      # Database Migration Workflow

      **⚠️ DANGER**: This modifies the database!

      Steps:
      1. Create backup
      2. Run migration in dry-run mode
      3. Review changes
      4. Apply migration
      5. Verify integrity

    tool_calls: [execute_command]

    steps:
      - name: backup
        action: execute_command
        description: Create database backup
        params:
          command: "pg_dump mydb > backup_$(date +%Y%m%d).sql"

      - name: dry-run
        action: execute_command
        description: Test migration
        params:
          command: "alembic upgrade head --sql"

      - name: migrate
        action: execute_command
        description: Apply migration
        params:
          command: "alembic upgrade head"

      - name: verify
        action: execute_command
        description: Verify migration
        params:
          command: "python verify_migration.py"
```

## Editor Support

| Editor | Workflow Location | Format | Trigger |
|--------|------------------|--------|---------|
| **Cline** | `.clinerules/workflows/` | Markdown | `/workflow-name` |
| **Claude** | `.claude/commands/` | Markdown | Custom command |
| **Cursor** | `.cursor/agent-functions/` | JSON | Agent function |
| **Continue** | `.continue/config.json` | JSON | `/workflow-name` |

### Cline

Workflows generate to `.clinerules/workflows/<name>.md`:

```markdown
# pr-review

Complete pull request review workflow

## Required Tools

- `gh`
- `read_file`
- `execute_command`

## Workflow

# PR Review Workflow
...
```

Trigger: `/pr-review`

### Claude

Workflows generate to `.claude/commands/<name>.md`:

```markdown
# pr-review

**Description:** Complete pull request review workflow

**Type:** Multi-step Workflow

## Required Tools

- `gh`
- `read_file`
- `execute_command`

## Prompt

# PR Review Workflow
...
```

### Cursor

Workflows generate to `.cursor/agent-functions/<name>.json`:

```json
{
  "name": "pr-review",
  "description": "Complete pull request review workflow",
  "prompt": "# PR Review Workflow...",
  "multiStep": true,
  "toolCalls": ["gh", "read_file", "execute_command"],
  "requiresApproval": true
}
```

### Continue

Workflows generate to `.continue/config.json`:

```json
{
  "slashCommands": [
    {
      "name": "pr-review",
      "description": "Complete pull request review workflow",
      "prompt": "# PR Review Workflow...",
      "multiStep": true,
      "toolCalls": ["gh", "read_file", "execute_command"],
      "requiresApproval": true
    }
  ]
}
```

## Variable Substitution
{% raw %}
Workflows support variable substitution using `{{{ VAR }}}` syntax:

```yaml
commands:
  - name: deploy-to-env
    multi_step: true
    prompt: |
      Deploy to environment: {{{ ENVIRONMENT }}}
      Branch: {{{ BRANCH }}}
    steps:
      - name: deploy
        action: execute_command
        params:
          command: "deploy.sh {{{ ENVIRONMENT }}} {{{ BRANCH }}}"
```
{% endraw %}

Generate with variables:

```bash
promptrek generate project.promptrek.yaml \
  --editor cline \
  -V ENVIRONMENT=production \
  -V BRANCH=main
```

## Best Practices

### 1. Tool Requirements

Always list required tools:

```yaml
tool_calls:
  - docker
  - kubectl
  - gh
```

This helps users know what to install before running the workflow.

### 2. Approval Gates

Set `requires_approval: true` for:
- Destructive operations (delete, deploy, etc.)
- External API calls
- File modifications
- Git operations (push, merge, etc.)

```yaml
requires_approval: true
```

### 3. Clear Instructions

Write step-by-step instructions in the prompt:

```yaml
prompt: |
  Follow these steps:
  1. First, do X
  2. Then, do Y
  3. Finally, do Z
```

### 4. Naming Conventions

- Simple commands: `verb-noun` (e.g., `explain-code`, `generate-tests`)
- Workflows: `noun-workflow` or describe the process (e.g., `pr-review-workflow`, `release-workflow`)

### 5. Add Examples

Help users understand how to use the workflow:

```yaml
examples:
  - "Review PR #123 with focus on security"
  - "Quick review of PR #456 for style only"
```

## Migration from Schema v3.0

Schema v3.1.0 is **100% backward compatible** with schema v3.0. To add workflow features:

### Before (Schema v3.0)

```yaml
schema_version: "3.0.0"

commands:
  - name: my-command
    description: Do something
    prompt: "Instructions here"
```

### After (Schema v3.1) - Enhanced

```yaml
schema_version: "3.1.0"

commands:
  - name: my-command
    description: Do something
    prompt: "Instructions here"
    multi_step: true  # NEW
    tool_calls: [tool1, tool2]  # NEW
    requires_approval: true  # NEW
```

No migration needed - just update `schema_version` and add new fields!

## See Also

- [Commands Reference]({{ site.baseurl }}/schema/v3.1.json)
- [Quick Start Guide]({{ site.baseurl }}/quick-start)
- [Adapter Documentation]({{ site.baseurl }}/developer/adapters)
- [Variable Substitution]({{ site.baseurl }}/user-guide/variables)

## Questions?

- [GitHub Discussions](https://github.com/flamingquaks/promptrek/discussions)
- [GitHub Issues](https://github.com/flamingquaks/promptrek/issues)
