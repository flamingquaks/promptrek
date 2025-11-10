"""
Default spec-driven project document commands.

These commands are automatically injected into editor configurations
when using the spec-driven project documents feature.
"""

from typing import List

from promptrek.core.models import Command


def _create_spec_command(
    name: str, description: str, prompt: str, argument_description: str
) -> Command:
    """
    Create a spec command with standard configuration.

    All spec commands share common settings: markdown output format,
    no approval required, and argument support enabled.

    Args:
        name: Command name (e.g., 'promptrek.spec.constitution')
        description: Brief command description
        prompt: Full prompt template with {{ topic }} placeholder
        argument_description: Description of the argument's purpose

    Returns:
        Configured Command object
    """
    output_format = "code" if "implement" in name else "markdown"

    return Command(
        name=name,
        description=description,
        prompt=prompt,
        output_format=output_format,
        requires_approval=False,
        supports_arguments=True,
        argument_description=argument_description,
    )


def get_spec_commands() -> List[Command]:
    """
    Get the default spec-driven project document commands.

    Implements the complete Spec-Kit workflow with 8 commands:
    - constitution: Project-wide values and agreements
    - specify: Structured problem specification
    - plan: Implementation and architecture plan
    - tasks: Task checklist from the plan
    - implement: Code generation scoped to task
    - analyze: Spec consistency review
    - history: Summarize changes across spec files
    - feedback: Structured PR feedback on a diff

    Returns:
        List of Command objects for spec management
    """
    return [
        _create_spec_command(
            name="promptrek.spec.constitution",
            description="Create or update project constitution",
            prompt="""# Arguments:
# - {{ topic }} (optional): context or scope of values/principles

You are drafting a shared constitution for a project.

## Output Instructions

Create a file named `constitution.spec.md` in your editor's appropriate location:
- Claude Code: `.claude/constitution.spec.md`
- Cursor: `.cursor/rules/constitution.spec.md`
- Continue: `.continue/rules/constitution.spec.md`
- Windsurf: `.windsurf/rules/constitution.spec.md`
- Cline: `.clinerules/constitution.spec.md`
- Kiro: `.kiro/steering/constitution.spec.md`
- Amazon Q: `.amazonq/rules/constitution.spec.md`
- JetBrains AI: `.assistant/rules/constitution.spec.md`
- Copilot: `.github/prompts/constitution.spec.md`

Use plain markdown format (do NOT add USF headers - the sync process will add them).

## Content to Include

1. **Mission Statement**: Clear purpose of the project
2. **Core Values**: 4-6 fundamental principles
3. **Anti-Patterns**: Specific practices to avoid
4. **Technical Principles**: Architecture, code quality standards
5. **Working Agreements**: Workflows, testing, code review
6. **Conflict Resolution**: How to resolve competing values

## After Creating

1. Update your editor's core memory file to reference the spec structure
2. Run: `promptrek sync --editor {{{ EDITOR_NAME }}}`

This will sync the constitution to `promptrek/specs/` with proper USF formatting.""",
            argument_description="Optional context or scope",
        ),
        _create_spec_command(
            name="promptrek.spec.specify",
            description="Create a structured software specification",
            prompt="""# Arguments:
# - {{ topic }}: the spec topic (e.g. 'auth-flow')

You are writing a structured software specification for the feature "{{ topic }}".

## Output Instructions

Create a file named `{{ topic }}.spec.md` in your editor's appropriate location:
- Claude Code: `.claude/{{ topic }}.spec.md`
- Cursor: `.cursor/rules/{{ topic }}.spec.md`
- Continue: `.continue/rules/{{ topic }}.spec.md`
- Windsurf: `.windsurf/rules/{{ topic }}.spec.md`
- Cline: `.clinerules/{{ topic }}.spec.md`
- Kiro: `.kiro/steering/{{ topic }}.spec.md`
- Amazon Q: `.amazonq/rules/{{ topic }}.spec.md`
- JetBrains AI: `.assistant/rules/{{ topic }}.spec.md`
- Copilot: `.github/prompts/{{ topic }}.spec.md`

Use plain markdown format (do NOT add USF headers - the sync process will add them).

## Content to Include

1. **Title**: Clear name for the feature
2. **Problem Statement**: What problem does this solve?
3. **Goals**: What should this accomplish?
4. **Non-Goals**: What is explicitly out of scope?
5. **Assumptions**: What are we assuming to be true?
6. **Requirements**: Functional and non-functional requirements
7. **Success Criteria**: How do we know it's done?

## After Creating

1. Update your editor's core memory file to reference this spec
2. Run: `promptrek sync --editor {{{ EDITOR_NAME }}}`

This will sync the spec to `promptrek/specs/` with proper USF formatting.""",
            argument_description="Spec topic or feature name",
        ),
        _create_spec_command(
            name="promptrek.spec.plan",
            description="Generate technical implementation plan from spec",
            prompt="""# Arguments:
# - {{ topic }}: name of the feature or spec this plan supports

You are writing a technical implementation plan for "{{ topic }}".
Reference the related spec ({{ topic }}.spec.md) if it exists in your editor's location.

## Output Instructions

Create a file named `{{ topic }}-plan.spec.md` in your editor's appropriate location:
- Claude Code: `.claude/{{ topic }}-plan.spec.md`
- Cursor: `.cursor/rules/{{ topic }}-plan.spec.md`
- Continue: `.continue/rules/{{ topic }}-plan.spec.md`
- Windsurf: `.windsurf/rules/{{ topic }}-plan.spec.md`
- Cline: `.clinerules/{{ topic }}-plan.spec.md`
- Kiro: `.kiro/steering/{{ topic }}-plan.spec.md`
- Amazon Q: `.amazonq/rules/{{ topic }}-plan.spec.md`
- JetBrains AI: `.assistant/rules/{{ topic }}-plan.spec.md`
- Copilot: `.github/prompts/{{ topic }}-plan.spec.md`

Use plain markdown format (do NOT add USF headers - the sync process will add them).

## Content to Include

1. **Approach**: High-level strategy to implement the spec
2. **Technical Stack**: Languages, frameworks, libraries to use
3. **Architecture**: Key components and their interactions
4. **Data Model**: Database schema or data structures
5. **API Design**: Endpoints, interfaces, or contracts
6. **Milestones**: Major phases of implementation
7. **Dependencies**: What needs to be in place first
8. **Risks**: Potential challenges and mitigation strategies

## After Creating

1. Update your editor's core memory file to link this plan to the original spec
2. Run: `promptrek sync --editor {{{ EDITOR_NAME }}}`

This will sync the plan to `promptrek/specs/` with proper USF formatting and link it to the original spec.""",
            argument_description="Feature or spec name",
        ),
        _create_spec_command(
            name="promptrek.spec.tasks",
            description="Generate implementation tasks from plan",
            prompt="""# Arguments:
# - {{ topic }}: name of the feature or plan to create tasks for

You are converting the plan for "{{ topic }}" into a checklist of development tasks.
Reference the {{ topic }}-plan.spec.md file if it exists in your editor's location.

## Output Instructions

Create a file named `{{ topic }}-tasks.spec.md` in your editor's appropriate location:
- Claude Code: `.claude/{{ topic }}-tasks.spec.md`
- Cursor: `.cursor/rules/{{ topic }}-tasks.spec.md`
- Continue: `.continue/rules/{{ topic }}-tasks.spec.md`
- Windsurf: `.windsurf/rules/{{ topic }}-tasks.spec.md`
- Cline: `.clinerules/{{ topic }}-tasks.spec.md`
- Kiro: `.kiro/steering/{{ topic }}-tasks.spec.md`
- Amazon Q: `.amazonq/rules/{{ topic }}-tasks.spec.md`
- JetBrains AI: `.assistant/rules/{{ topic }}-tasks.spec.md`
- Copilot: `.github/prompts/{{ topic }}-tasks.spec.md`

Use plain markdown format (do NOT add USF headers - the sync process will add them).

## Content Format

Create a markdown checklist with clear, atomic task items:

- [ ] Task 1 (with 1-line description)
- [ ] Task 2 (with 1-line description)
- [ ] Task 3 (with 1-line description)

Guidelines:
- Use clear, atomic task items
- Do not nest subtasks
- Ensure all key plan items are represented
- Include testing and documentation tasks
- Order tasks by logical dependency

## After Creating

1. Update your editor's core memory file to link this task list to the plan
2. Run: `promptrek sync --editor {{{ EDITOR_NAME }}}`

This will sync the tasks to `promptrek/specs/` with proper USF formatting and link them to the plan.""",
            argument_description="Feature or plan name",
        ),
        _create_spec_command(
            name="promptrek.spec.implement",
            description="Implement production code from tasks",
            prompt="""# Arguments:
# - {{ topic }}: the task or module name to implement

You are writing production-ready code for the task: "{{ topic }}".
Reference the {{ topic }}-tasks.spec.md and {{ topic }}-plan.spec.md files for context.

## Output Instructions

Create a file named `{{ topic }}-implementation.spec.md` in your editor's appropriate location:
- Claude Code: `.claude/{{ topic }}-implementation.spec.md`
- Cursor: `.cursor/rules/{{ topic }}-implementation.spec.md`
- Continue: `.continue/rules/{{ topic }}-implementation.spec.md`
- Windsurf: `.windsurf/rules/{{ topic }}-implementation.spec.md`
- Cline: `.clinerules/{{ topic }}-implementation.spec.md`
- Kiro: `.kiro/steering/{{ topic }}-implementation.spec.md`
- Amazon Q: `.amazonq/rules/{{ topic }}-implementation.spec.md`
- JetBrains AI: `.assistant/rules/{{ topic }}-implementation.spec.md`
- Copilot: `.github/prompts/{{ topic }}-implementation.spec.md`

Use plain markdown format (do NOT add USF headers - the sync process will add them).

## Content Guidelines

Document the implementation approach with:

1. **Implementation Summary**: Brief overview of what was implemented
2. **Code Structure**: Key files and components created
3. **Key Decisions**: Important implementation choices and rationale
4. **Testing Approach**: How the implementation is tested
5. **Task Completion**: Check off completed tasks from the task list

Then include actual code implementations as code blocks.

Guidelines:
- Include complete, production-ready code
- Respect file and function boundaries
- Include docstrings and type hints
- Follow project code conventions
- Reference the plan and spec for context

## After Creating

1. Update task checkboxes in {{ topic }}-tasks.spec.md as you complete them
2. Update your editor's core memory file to link this implementation
3. Run: `promptrek sync --editor {{{ EDITOR_NAME }}}`

This will sync the implementation notes to `promptrek/specs/` with proper USF formatting.""",
            argument_description="Task or module name",
        ),
        _create_spec_command(
            name="promptrek.spec.analyze",
            description="Analyze and review consistency of spec artifacts",
            prompt="""# Arguments:
# - {{ topic }} (optional): analyze a specific spec chain if provided

Review the consistency across the spec, plan, and tasks for "{{ topic }}".
Identify issues, omissions, or inconsistencies.

## Output Instructions

Create a file named `{{ topic }}-analysis.spec.md` (or `analysis.spec.md` if no topic) in your editor's appropriate location:
- Claude Code: `.claude/{{ topic }}-analysis.spec.md`
- Cursor: `.cursor/rules/{{ topic }}-analysis.spec.md`
- Continue: `.continue/rules/{{ topic }}-analysis.spec.md`
- Windsurf: `.windsurf/rules/{{ topic }}-analysis.spec.md`
- Cline: `.clinerules/{{ topic }}-analysis.spec.md`
- Kiro: `.kiro/steering/{{ topic }}-analysis.spec.md`
- Amazon Q: `.amazonq/rules/{{ topic }}-analysis.spec.md`
- JetBrains AI: `.assistant/rules/{{ topic }}-analysis.spec.md`
- Copilot: `.github/prompts/{{ topic }}-analysis.spec.md`

Use plain markdown format (do NOT add USF headers - the sync process will add them).

## Content to Include

1. **Issues**: Missing pieces, contradictions, unclear terms
2. **Suggested fixes**: What should be updated where
3. **Consistency check**: Alignment between spec, plan, and tasks

Use markdown bullet lists. Keep tone constructive.

## After Creating

1. Run: `promptrek sync --editor {{{ EDITOR_NAME }}}`

This will sync the analysis to `promptrek/specs/` with proper USF formatting.""",
            argument_description="Optional: specific spec to analyze",
        ),
        _create_spec_command(
            name="promptrek.spec.history",
            description="Summarize changes and progress across specs",
            prompt="""# Arguments:
# - {{ topic }} (optional): limit summary to a specific spec or module

You are summarizing the history and evolution of all specs.
Highlight key changes across `*.spec.md` files in your editor's location.

## Output Instructions

Create a file named `{{ topic }}-history.spec.md` (or `history.spec.md` if no topic) in your editor's appropriate location:
- Claude Code: `.claude/{{ topic }}-history.spec.md`
- Cursor: `.cursor/rules/{{ topic }}-history.spec.md`
- Continue: `.continue/rules/{{ topic }}-history.spec.md`
- Windsurf: `.windsurf/rules/{{ topic }}-history.spec.md`
- Cline: `.clinerules/{{ topic }}-history.spec.md`
- Kiro: `.kiro/steering/{{ topic }}-history.spec.md`
- Amazon Q: `.amazonq/rules/{{ topic }}-history.spec.md`
- JetBrains AI: `.assistant/rules/{{ topic }}-history.spec.md`
- Copilot: `.github/prompts/{{ topic }}-history.spec.md`

Use plain markdown format (do NOT add USF headers - the sync process will add them).

## Content Format

- Date / Change summary
- File(s) affected

Use markdown bullet points.

## After Creating

1. Run: `promptrek sync --editor {{{ EDITOR_NAME }}}`

This will sync the history to `promptrek/specs/` with proper USF formatting.""",
            argument_description="Optional: specific spec or module",
        ),
        _create_spec_command(
            name="promptrek.spec.feedback",
            description="Generate structured PR feedback on a diff",
            prompt="""# Arguments:
# - {{ topic }}: file or diff description (e.g. 'login refactor')

You are reviewing a code or spec diff.
Summarize key issues, risks, and improvements.
Provide PR-style feedback.

## Output Instructions

Create a file named `{{ topic }}-feedback.spec.md` in your editor's appropriate location:
- Claude Code: `.claude/{{ topic }}-feedback.spec.md`
- Cursor: `.cursor/rules/{{ topic }}-feedback.spec.md`
- Continue: `.continue/rules/{{ topic }}-feedback.spec.md`
- Windsurf: `.windsurf/rules/{{ topic }}-feedback.spec.md`
- Cline: `.clinerules/{{ topic }}-feedback.spec.md`
- Kiro: `.kiro/steering/{{ topic }}-feedback.spec.md`
- Amazon Q: `.amazonq/rules/{{ topic }}-feedback.spec.md`
- JetBrains AI: `.assistant/rules/{{ topic }}-feedback.spec.md`
- Copilot: `.github/prompts/{{ topic }}-feedback.spec.md`

Use plain markdown format (do NOT add USF headers - the sync process will add them).

## Content Format

1. **Summary**: High-level assessment
2. **Suggestions**: Bullet list of improvements
3. **Priority ranking**: High / Medium / Low for each suggestion

Avoid repeating implementation; focus on judgment and clarity.

## After Creating

1. Run: `promptrek sync --editor {{{ EDITOR_NAME }}}`

This will sync the feedback to `promptrek/specs/` with proper USF formatting.""",
            argument_description="File or diff description",
        ),
    ]
