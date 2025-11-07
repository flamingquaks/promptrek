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

You are drafting a shared constitution for a project. Include:

## Values
What core values guide the team?

## Anti-Patterns
What behaviors or pitfalls should be avoided?

## Working Agreements
What are default collaboration expectations?

Use structured markdown headings and emphasize brevity and clarity.""",
            argument_description="Optional context or scope",
        ),
        _create_spec_command(
            name="promptrek.spec.specify",
            description="Create a structured software specification",
            prompt="""# Arguments:
# - {{ topic }}: the spec topic (e.g. 'auth-flow')

You are writing a structured software specification for the feature "{{ topic }}".
Create a new module spec including the following:

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

Format as clean markdown. Keep each section concise.""",
            argument_description="Spec topic or feature name",
        ),
        _create_spec_command(
            name="promptrek.spec.plan",
            description="Generate technical implementation plan from spec",
            prompt="""# Arguments:
# - {{ topic }}: name of the feature or spec this plan supports

You are writing a technical implementation plan for "{{ topic }}".
Reference the related spec in `promptrek/specs/` if it exists.

## Approach
Describe the strategy and system design.

## Stack
What technologies, frameworks, or tools will be used?

## Milestones
Break down implementation into 2–4 phases.

Use markdown headings. Include bullet lists where helpful.""",
            argument_description="Feature or spec name",
        ),
        _create_spec_command(
            name="promptrek.spec.tasks",
            description="Generate implementation tasks from plan",
            prompt="""# Arguments:
# - {{ topic }}: name of the feature or plan to create tasks for

You are converting the plan for "{{ topic }}" into a checklist of development tasks.
Use the corresponding `.plan.md` file if available.

Output format:
- [ ] Task 1 (with 1-line description)
- [ ] Task 2

Use clear, atomic task items. Do not nest subtasks.
Ensure all key plan items are represented.""",
            argument_description="Feature or plan name",
        ),
        _create_spec_command(
            name="promptrek.spec.implement",
            description="Implement production code from tasks",
            prompt="""# Arguments:
# - {{ topic }}: the task or module name to implement

You are writing production-ready code for the task: "{{ topic }}".
Use the task list and plan as context.

Output only the code block.
Respect file and function boundaries. Include docstrings.
Assume the reader has seen the plan and spec.""",
            argument_description="Task or module name",
        ),
        _create_spec_command(
            name="promptrek.spec.analyze",
            description="Analyze and review consistency of spec artifacts",
            prompt="""# Arguments:
# - {{ topic }} (optional): analyze a specific spec chain if provided

Review the consistency across the spec, plan, and tasks for "{{ topic }}".
Identify issues, omissions, or inconsistencies.

Output:
- Issues (missing pieces, contradictions, unclear terms)
- Suggested fixes (what should be updated where)

Use markdown bullet lists. Keep tone constructive.""",
            argument_description="Optional: specific spec to analyze",
        ),
        _create_spec_command(
            name="promptrek.spec.history",
            description="Summarize changes and progress across specs",
            prompt="""# Arguments:
# - {{ topic }} (optional): limit summary to a specific spec or module

You are summarizing the history and evolution of all specs.
Highlight key changes across `*.spec.md`, `*.plan.md`, and `*.tasks.md`.

Output format:
- Date / Change summary
- File(s) affected

Use markdown bullet points.""",
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

Output format:
- Summary
- Suggestions (bullet list)
- Priority ranking (e.g. High / Medium / Low)

Avoid repeating implementation; focus on judgment and clarity.""",
            argument_description="File or diff description",
        ),
    ]
