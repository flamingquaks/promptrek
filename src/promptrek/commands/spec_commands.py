"""
Default spec-driven project document commands.

These commands are automatically injected into editor configurations
when using the spec-driven project documents feature.
"""

from promptrek.core.models import Command


def get_spec_commands():
    """
    Get the default spec-driven project document commands.

    Returns:
        List of Command objects for spec management
    """
    return [
        Command(
            name="promptrek.spec.create",
            description="Create a new spec-driven project document",
            prompt="""Create a new spec-driven project document with AI-driven naming.

## Instructions

1. **Gather Requirements**: Ask the user for the purpose and key details of the spec
2. **Generate Title**: Create a contextual, descriptive title based on the purpose
3. **Create Content**: Write comprehensive markdown content including:
   - Overview and purpose
   - Requirements or specifications
   - Technical details
   - Examples or use cases (if applicable)
4. **Save to Registry**: Save the spec to `promptrek/specs/` and register it in `promptrek/specs.yaml`

## Output Format

The spec should be saved as a markdown file in `promptrek/specs/` with:
- Auto-generated filename based on title and unique ID
- Metadata header (ID, created date, source command, summary, tags)
- Separator (`---`)
- Main content in clean markdown

## Example

```markdown
# API Authentication Specification

**ID:** a1b2c3d4
**Created:** 2025-11-06T10:30:00
**Source:** /promptrek.spec.create
**Summary:** OAuth 2.0 implementation for API endpoints
**Tags:** api, auth, oauth

---

## Overview

This specification defines the OAuth 2.0 authentication flow for our API...

## Requirements

1. Support authorization code flow
2. Implement token refresh mechanism
3. ...
```

After creating the spec, inform the user of:
- Spec ID
- Title
- File path
- How to view it with `/promptrek.spec.analyze`
""",
            output_format="markdown",
            requires_approval=False,
        ),
        Command(
            name="promptrek.spec.plan",
            description="Generate a technical implementation plan from a spec",
            prompt="""Generate a detailed technical implementation plan from a spec.

## Instructions

1. **Select Spec**: Ask the user which spec to create a plan for (or use context)
2. **Analyze Spec**: Read and understand the spec requirements
3. **Create Plan**: Generate a structured technical plan including:
   - Architecture overview
   - Component breakdown
   - Implementation phases
   - Dependencies and prerequisites
   - Risk assessment
   - Timeline estimates (if applicable)
4. **Save as New Spec**: Create a new spec document with the plan (linked to original)

## Output Format

Create a new spec with:
- Title: "[Original Spec Title] - Implementation Plan"
- Link to original spec ID in metadata
- Structured markdown plan with sections for architecture, phases, dependencies, etc.
- Tag with "plan" and original spec tags

## Example Structure

```markdown
# API Authentication Specification - Implementation Plan

**ID:** e5f6g7h8
**Created:** 2025-11-06T11:00:00
**Source:** /promptrek.spec.plan
**Summary:** Implementation plan for OAuth 2.0 authentication
**Tags:** plan, api, auth, oauth
**Linked Specs:** a1b2c3d4

---

## Architecture Overview

[Architecture details...]

## Implementation Phases

### Phase 1: Setup & Configuration
- Set up OAuth 2.0 library
- Configure environment variables
- ...

### Phase 2: Core Authentication Flow
...

## Dependencies

- Library: oauth2-server v4.x
- Database: PostgreSQL 14+
...
```

Inform the user of the new plan spec ID and how to proceed with `/promptrek.spec.tasks`
""",
            output_format="markdown",
            requires_approval=False,
        ),
        Command(
            name="promptrek.spec.tasks",
            description="Break down a plan into actionable tasks",
            prompt="""Break down an implementation plan into concrete, actionable tasks.

## Instructions

1. **Select Plan**: Ask which plan spec to break down (or use context)
2. **Analyze Plan**: Read the plan and identify all work items
3. **Create Task List**: Generate a detailed task breakdown including:
   - Task groups by phase or component
   - Individual actionable tasks
   - Dependencies between tasks
   - Priority/order
   - Acceptance criteria for each task
4. **Save as New Spec**: Create a task breakdown spec (linked to plan)

## Output Format

Create a new spec with:
- Title: "[Plan Title] - Task Breakdown"
- Link to plan spec ID in metadata
- Structured task list with checkboxes, dependencies, and acceptance criteria
- Tag with "tasks" and related tags

## Example Structure

```markdown
# API Authentication Implementation Plan - Task Breakdown

**ID:** i9j0k1l2
**Created:** 2025-11-06T11:30:00
**Source:** /promptrek.spec.tasks
**Summary:** Actionable tasks for OAuth 2.0 implementation
**Tags:** tasks, api, auth, oauth
**Linked Specs:** e5f6g7h8, a1b2c3d4

---

## Phase 1: Setup & Configuration

### Task 1.1: Install OAuth Library
- [ ] Add oauth2-server to package.json
- [ ] Run npm install
- [ ] Verify installation

**Dependencies:** None
**Acceptance Criteria:** Library imported successfully in code

### Task 1.2: Configure Environment
- [ ] Add OAuth credentials to .env
- [ ] Set up callback URLs
- [ ] Configure token expiration times

**Dependencies:** 1.1
**Acceptance Criteria:** Environment variables loaded and validated

...
```

Inform the user they can now use `/promptrek.spec.implement` to start coding
""",
            output_format="markdown",
            requires_approval=False,
        ),
        Command(
            name="promptrek.spec.implement",
            description="Implement code based on tasks and specs",
            prompt="""Implement code based on spec documents, plans, and tasks.

## Instructions

1. **Review Context**: Ask which spec/plan/tasks to implement (or use context)
2. **Read Specs**: Load and review:
   - Original specification
   - Implementation plan (if available)
   - Task breakdown (if available)
3. **Generate Code**: Write production-quality code that:
   - Follows the spec requirements
   - Implements tasks in order
   - Adheres to project coding standards
   - Includes proper error handling
   - Has comprehensive tests
4. **Update Tasks**: Mark completed tasks in the task spec
5. **Document Changes**: Create or update an implementation notes section

## Workflow

1. Confirm which task(s) to implement
2. Show relevant spec sections
3. Implement the code
4. Run tests
5. Update task spec with completion status
6. Provide summary of changes

## Example

When implementing Task 1.1 (Install OAuth Library):

```bash
# Add dependency
npm install oauth2-server

# Verify import
node -e "require('oauth2-server')"
```

Then update the task spec to mark Task 1.1 as complete:

```markdown
### Task 1.1: Install OAuth Library
- [x] Add oauth2-server to package.json
- [x] Run npm install
- [x] Verified installation

**Status:** ✅ Complete
**Completed:** 2025-11-06T12:00:00
```

Continue with the next task or ask user for guidance.
""",
            output_format="code",
            requires_approval=False,
        ),
        Command(
            name="promptrek.spec.analyze",
            description="Analyze specs for consistency and completeness",
            prompt="""Analyze spec documents for consistency, completeness, and quality.

## Instructions

1. **Select Specs**: Ask which spec(s) to analyze (or analyze all linked specs)
2. **Load Specs**: Read spec content and metadata
3. **Perform Analysis**:
   - Check for completeness (all required sections present)
   - Verify consistency across linked specs
   - Identify gaps or ambiguities
   - Check for conflicting requirements
   - Validate links between specs
   - Assess clarity and detail level
4. **Generate Report**: Create analysis report with:
   - Summary of findings
   - Issues by severity (critical, warning, info)
   - Recommendations for improvements
   - Checklist of standards compliance

## Analysis Checklist

- [ ] All required sections present?
- [ ] Clearly defined requirements?
- [ ] No conflicting specifications?
- [ ] Linked specs are consistent?
- [ ] Technical details sufficient?
- [ ] Examples provided where needed?
- [ ] Acceptance criteria clear?
- [ ] Tags appropriate and helpful?

## Output Format

Generate a markdown report:

```markdown
# Spec Analysis Report

**Date:** 2025-11-06T13:00:00
**Analyzed Specs:** a1b2c3d4, e5f6g7h8, i9j0k1l2

## Summary

✅ 2 specs fully compliant
⚠️  1 spec has warnings
❌ 0 critical issues

## Detailed Findings

### Spec a1b2c3d4: API Authentication Specification

**Status:** ✅ Compliant

**Strengths:**
- Clear requirements
- Good examples
- Well-structured

**Suggestions:**
- Add security considerations section
- Include error handling scenarios

### Spec e5f6g7h8: Implementation Plan

**Status:** ⚠️ Has Warnings

**Issues:**
- Missing timeline estimates (Warning)
- Dependency on external library version not pinned (Warning)

**Recommendations:**
- Add estimated timelines for each phase
- Specify exact library versions

...

## Overall Recommendations

1. Add security review section to main spec
2. Pin dependency versions in plan
3. Consider adding API usage examples
```

Offer to create updated versions of specs with improvements if user wants.
""",
            output_format="markdown",
            requires_approval=False,
        ),
    ]
