# PrompTrek: Slash Command Spec Integration (Product Definition)

## Overview

PrompTrek aims to mirror the structured spec-driven development workflow pioneered by GitHub’s Spec-Kit. By integrating a suite of editor-injected slash commands (e.g. `/promptrek.spec.specify`), PrompTrek enables multi-step artifact generation with consistent quality, traceability, and AI scaffolding. These commands output structured spec documents and planning artifacts managed through the Universal Spec Format (USF).

## Inspiration from Spec-Kit Slash Commands

Spec-Kit defines a lifecycle of spec generation via dedicated commands:

- `/speckit.constitution` – project-wide constitution of values and agreements
- `/speckit.specify` – creates a structured problem spec
- `/speckit.plan` – builds a technical implementation plan
- `/speckit.tasks` – generates a development checklist
- `/speckit.implement` – turns tasks into code
- `/speckit.analyze` – reviews internal consistency and gaps
- `/speckit.history` – summarizes changes and progress across specs
- `/speckit.feedback` – prepares pull request feedback for a diff

Each command in Spec-Kit:

- Is backed by a markdown prompt template (e.g. `plan.prompt.md`)
- Includes explicit instructions, references to prior artifacts, and structured output expectations
- May reference or rely on a `constitution.md` or memory context for consistency
- Is structured to produce formatted markdown, checklists, or code blocks

## PrompTrek Implementation Goals

### Slash Command Prompt Templates

Each command supports **arguments** passed after the command name. These are interpreted by the editor or AI engine and injected as context into the prompt templates.

- **Positional argument**: becomes the topic or module name (e.g. `/promptrek.spec.create auth-flow`)
- **Named flags**: may be parsed by future adapters (e.g. `/promptrek.spec.plan auth-flow --format=table`)

Arguments will be interpolated into prompt templates using variables like `{{ topic }}` or `{{ args }}` where applicable.


Below are the proposed default prompt instructions for each slash command. These will be rendered as `.md` prompt files in supported editors.

#### `/promptrek.spec.specify`

```
# Arguments:
# - {{ topic }}: the spec topic (e.g. 'auth-flow')

You are writing a structured software specification for the feature "{{ topic }}".
Create a new module spec including the following:
You are writing a structured software specification.
Create a new feature or module spec including the following:

## Title
Give a short, descriptive title.

## Problem
What problem does this spec solve?

## Goals
List key outcomes or success criteria.

## Non-Goals
Clarify what's explicitly out of scope.

## Assumptions
Any preconditions or requirements that must be met.

Format as clean markdown. Keep each section concise.
```

#### `/promptrek.spec.plan`

```
# Arguments:
# - {{ topic }}: name of the feature or spec this plan supports

You are writing a technical implementation plan for "{{ topic }}".
Reference the related spec in `promptrek/specs/` if it exists.
You are writing a technical implementation plan based on an existing spec.
Reference the most recent spec document in `promptrek/specs/`.

## Approach
Describe the strategy and system design.

## Stack
What technologies, frameworks, or tools will be used?

## Milestones
Break down implementation into 2–4 phases.

Use markdown headings. Include bullet lists where helpful.
```

#### `/promptrek.spec.tasks`

```
# Arguments:
# - {{ topic }}: name of the feature or plan to create tasks for

You are converting the plan for "{{ topic }}" into a checklist of development tasks.
Use the corresponding `.plan.md` file if available.
You are turning a technical plan into an implementation checklist.
Scan the latest `.promptrek/specs/*plan.md` file if available.

Output format:
- [ ] Task 1 (with 1-line description)
- [ ] Task 2

Use clear, atomic task items. Do not nest subtasks.
Ensure all key plan items are represented.
```

#### `/promptrek.spec.implement`

```
# Arguments:
# - {{ topic }}: the task or module name to implement

You are writing production-ready code for the task: "{{ topic }}".
Use the task list and plan as context.
You are writing production-quality code for a specific task.
Use the linked `.promptrek/specs/*tasks.md` file as input.

Output only the code block.
Respect file and function boundaries. Include docstrings.
Assume the reader has seen the plan and spec.
```

#### `/promptrek.spec.analyze`

```
# Arguments:
# - {{ topic }} (optional): analyze a specific spec chain if provided

Review the consistency across the spec, plan, and tasks for "{{ topic }}".
Identify issues, omissions, or inconsistencies.
You are reviewing the consistency of linked spec artifacts.
Compare the `.spec.md`, `.plan.md`, and `.tasks.md` files.

Output:
- Issues (missing pieces, contradictions, unclear terms)
- Suggested fixes (what should be updated where)

Use markdown bullet lists. Keep tone constructive.
```

PrompTrek adopts these principles using the following slash command suite:

### Slash Commands (Editor Injected)

PrompTrek adopts the full Spec-Kit agent command suite, prepended with `/promptrek.spec.`:

- `/promptrek.spec.constitution` → project-wide values and agreements
- `/promptrek.spec.specify` → structured problem specification
- `/promptrek.spec.plan` → implementation and architecture plan
- `/promptrek.spec.tasks` → task checklist from the plan
- `/promptrek.spec.implement` → code generation scoped to task
- `/promptrek.spec.analyze` → spec consistency review
- `/promptrek.spec.history` → summarize changes across spec files
- `/promptrek.spec.feedback` → structured PR feedback on a diff

These commands are injected into `.claude/`, `.continue/`, etc., and mirror the purpose and structure of Spec-Kit’s markdown prompts.

Each command prompt follows a high-quality instruction pattern inspired by Spec-Kit:

- Preamble: framing of task with tone and expectations
- Context: references to other files (e.g. "Use the current `constitution.md`")
- Format: sectioned markdown or checklists (e.g. headings, bullet goals)
- Output intent: instruct AI to generate draft content, not commit-ready files

## Spec Storage & Metadata

- Outputs stored in `promptrek/specs/` (COMMITTED to git)
- Indexed via `promptrek/specs.yaml` (Universal Spec Format / USF)
- AI-generated names and summaries tracked centrally

### Universal Spec Format (USF) Example

```yaml
specs:
  - id: auth-flow
    title: User Authentication
    path: promptrek/specs/auth-flow.md
    source_command: /promptrek.spec.specify
    summary: Handles login and recovery flows
```

#### `/promptrek.spec.constitution`

```
# Arguments:
# - {{ topic }} (optional): context or scope of values/principles

You are drafting a shared constitution for a project. Include:

## Values
What core values guide the team?

## Anti-Patterns
What behaviors or pitfalls should be avoided?

## Working Agreements
What are default collaboration expectations?

Use structured markdown headings and emphasize brevity and clarity.
```

#### `/promptrek.spec.history`

```
# Arguments:
# - {{ topic }} (optional): limit summary to a specific spec or module

You are summarizing the history and evolution of all specs.
Highlight key changes across `*.spec.md`, `*.plan.md`, and `*.tasks.md`.

Output format:
- Date / Change summary
- File(s) affected

Use markdown bullet points.
```

#### `/promptrek.spec.feedback`

```
# Arguments:
# - {{ topic }}: file or diff description (e.g. 'login refactor')

You are reviewing a code or spec diff.
Summarize key issues, risks, and improvements.
Provide PR-style feedback.

Output format:
- Summary
- Suggestions (bullet list)
- Priority ranking (e.g. High / Medium / Low)

Avoid repeating implementation; focus on judgment and clarity.
```

### CLI

- `promptrek generate` → injects slash prompts
- `promptrek sync` → pulls .specs/\* into USF
- `promptrek list-specs` → inspect registry
- `promptrek spec export` → renders markdown for sharing

## Benefits

- Inherits proven multi-step spec methodology from Spec-Kit
- Standardized slash prompts across Claude, Continue, etc.
- Central control of all AI-generated specs via USF

## Next Steps

- Finalize `specs.yaml` (USF) schema
- Write `/promptrek.spec.*` prompts using Spec-Kit’s quality guidelines
- Build editor adapters with injected prompts and sync hooks

