"""
Kiro (AI-powered assistance) adapter implementation.
"""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import click

from ..core.exceptions import ValidationError
from ..core.models import UniversalPrompt
from .base import EditorAdapter


class KiroAdapter(EditorAdapter):
    """Adapter for Kiro AI-powered assistance."""

    _description = "Kiro (.kiro/steering/, .kiro/specs/, custom steering files)"
    _file_patterns = [
        ".kiro/steering/*.md",
        ".kiro/specs/*/requirements.md",
        ".kiro/specs/*/design.md",
        ".kiro/specs/*/tasks.md",
        ".kiro/hooks/*.md",
        ".prompts/*.md",
    ]

    def __init__(self):
        super().__init__(
            name="kiro",
            description=self._description,
            file_patterns=self._file_patterns,
        )

    def generate(
        self,
        prompt: UniversalPrompt,
        output_dir: Path,
        dry_run: bool = False,
        verbose: bool = False,
        variables: Optional[Dict[str, Any]] = None,
    ) -> List[Path]:
        """Generate Kiro configuration files."""

        # Apply variable substitution if supported
        processed_prompt = self.substitute_variables(prompt, variables)

        # Process conditionals if supported (content used by generate method)
        self.process_conditionals(processed_prompt, variables)

        created_files = []

        # Generate steering system
        steering_files = self._generate_steering_system(
            processed_prompt, output_dir, dry_run, verbose
        )
        created_files.extend(steering_files)

        # Generate specifications system
        specs_files = self._generate_specs_system(
            processed_prompt, output_dir, dry_run, verbose
        )
        created_files.extend(specs_files)

        # Generate custom steering files
        custom_files = self._generate_custom_steering(
            processed_prompt, output_dir, dry_run, verbose
        )
        created_files.extend(custom_files)

        # Generate hooks system
        hooks_files = self._generate_hooks_system(
            processed_prompt, output_dir, dry_run, verbose
        )
        created_files.extend(hooks_files)

        # Generate prompts system
        prompts_files = self._generate_prompts_system(
            processed_prompt, output_dir, dry_run, verbose
        )
        created_files.extend(prompts_files)

        return created_files

    def _generate_steering_system(
        self,
        prompt: UniversalPrompt,
        output_dir: Path,
        dry_run: bool,
        verbose: bool,
    ) -> List[Path]:
        """Generate .kiro/steering/ system with core steering files."""
        steering_dir = output_dir / ".kiro" / "steering"
        created_files = []

        # Generate product overview
        product_file = steering_dir / "product.md"
        product_content = self._build_product_steering(prompt)

        if dry_run:
            click.echo(f"  📁 Would create: {product_file}")
            if verbose:
                preview = (
                    product_content[:200] + "..."
                    if len(product_content) > 200
                    else product_content
                )
                click.echo(f"    {preview}")
        else:
            steering_dir.mkdir(parents=True, exist_ok=True)
            with open(product_file, "w", encoding="utf-8") as f:
                f.write(product_content)
            click.echo(f"✅ Generated: {product_file}")
            created_files.append(product_file)

        # Generate technology stack steering
        if prompt.context and prompt.context.technologies:
            tech_file = steering_dir / "tech.md"
            tech_content = self._build_tech_steering(prompt)

            if dry_run:
                click.echo(f"  📁 Would create: {tech_file}")
                if verbose:
                    preview = (
                        tech_content[:200] + "..."
                        if len(tech_content) > 200
                        else tech_content
                    )
                    click.echo(f"    {preview}")
            else:
                steering_dir.mkdir(parents=True, exist_ok=True)
                with open(tech_file, "w", encoding="utf-8") as f:
                    f.write(tech_content)
                click.echo(f"✅ Generated: {tech_file}")
                created_files.append(tech_file)

        # Generate project structure steering
        structure_file = steering_dir / "structure.md"
        structure_content = self._build_structure_steering(prompt)

        if dry_run:
            click.echo(f"  📁 Would create: {structure_file}")
            if verbose:
                preview = (
                    structure_content[:200] + "..."
                    if len(structure_content) > 200
                    else structure_content
                )
                click.echo(f"    {preview}")
        else:
            steering_dir.mkdir(parents=True, exist_ok=True)
            with open(structure_file, "w", encoding="utf-8") as f:
                f.write(structure_content)
            click.echo(f"✅ Generated: {structure_file}")
            created_files.append(structure_file)

        return created_files

    def _generate_specs_system(
        self,
        prompt: UniversalPrompt,
        output_dir: Path,
        dry_run: bool,
        verbose: bool,
    ) -> List[Path]:
        """Generate .kiro/specs/ system with project specifications."""
        specs_dir = output_dir / ".kiro" / "specs"
        created_files = []

        # Create a main spec based on the project
        spec_name = prompt.metadata.title.lower().replace(" ", "-")
        spec_dir = specs_dir / spec_name

        # Generate requirements.md
        requirements_file = spec_dir / "requirements.md"
        requirements_content = self._build_requirements_spec(prompt)

        if dry_run:
            click.echo(f"  📁 Would create: {requirements_file}")
            if verbose:
                preview = (
                    requirements_content[:200] + "..."
                    if len(requirements_content) > 200
                    else requirements_content
                )
                click.echo(f"    {preview}")
        else:
            spec_dir.mkdir(parents=True, exist_ok=True)
            with open(requirements_file, "w", encoding="utf-8") as f:
                f.write(requirements_content)
            click.echo(f"✅ Generated: {requirements_file}")
            created_files.append(requirements_file)

        # Generate design.md
        design_file = spec_dir / "design.md"
        design_content = self._build_design_spec(prompt)

        if dry_run:
            click.echo(f"  📁 Would create: {design_file}")
            if verbose:
                preview = (
                    design_content[:200] + "..."
                    if len(design_content) > 200
                    else design_content
                )
                click.echo(f"    {preview}")
        else:
            spec_dir.mkdir(parents=True, exist_ok=True)
            with open(design_file, "w", encoding="utf-8") as f:
                f.write(design_content)
            click.echo(f"✅ Generated: {design_file}")
            created_files.append(design_file)

        # Generate tasks.md
        tasks_file = spec_dir / "tasks.md"
        tasks_content = self._build_tasks_spec(prompt)

        if dry_run:
            click.echo(f"  📁 Would create: {tasks_file}")
            if verbose:
                preview = (
                    tasks_content[:200] + "..."
                    if len(tasks_content) > 200
                    else tasks_content
                )
                click.echo(f"    {preview}")
        else:
            spec_dir.mkdir(parents=True, exist_ok=True)
            with open(tasks_file, "w", encoding="utf-8") as f:
                f.write(tasks_content)
            click.echo(f"✅ Generated: {tasks_file}")
            created_files.append(tasks_file)

        return created_files

    def _generate_custom_steering(
        self,
        prompt: UniversalPrompt,
        output_dir: Path,
        dry_run: bool,
        verbose: bool,
    ) -> List[Path]:
        """Generate custom steering files with specific targeting."""
        steering_dir = output_dir / ".kiro" / "steering"
        created_files = []

        # Generate API standards steering (if applicable)
        if (
            prompt.context
            and prompt.context.technologies
            and any(
                tech.lower() in ["api", "rest", "graphql", "node", "express", "fastapi"]
                for tech in prompt.context.technologies
            )
        ):
            api_file = steering_dir / "api-rest-conventions.md"
            api_content = self._build_api_standards_steering(prompt)

            if dry_run:
                click.echo(f"  📁 Would create: {api_file}")
                if verbose:
                    preview = (
                        api_content[:200] + "..."
                        if len(api_content) > 200
                        else api_content
                    )
                    click.echo(f"    {preview}")
            else:
                steering_dir.mkdir(parents=True, exist_ok=True)
                with open(api_file, "w", encoding="utf-8") as f:
                    f.write(api_content)
                click.echo(f"✅ Generated: {api_file}")
                created_files.append(api_file)

        # Generate frontend standards (if applicable)
        if (
            prompt.context
            and prompt.context.technologies
            and any(
                tech.lower()
                in ["react", "vue", "angular", "svelte", "typescript", "javascript"]
                for tech in prompt.context.technologies
            )
        ):
            frontend_file = steering_dir / "component-development-patterns.md"
            frontend_content = self._build_component_patterns_steering(prompt)

            if dry_run:
                click.echo(f"  📁 Would create: {frontend_file}")
                if verbose:
                    preview = (
                        frontend_content[:200] + "..."
                        if len(frontend_content) > 200
                        else frontend_content
                    )
                    click.echo(f"    {preview}")
            else:
                steering_dir.mkdir(parents=True, exist_ok=True)
                with open(frontend_file, "w", encoding="utf-8") as f:
                    f.write(frontend_content)
                click.echo(f"✅ Generated: {frontend_file}")
                created_files.append(frontend_file)

        return created_files

    def _generate_legacy_config(
        self,
        prompt: UniversalPrompt,
        conditional_content: Optional[Dict[str, Any]],
        output_dir: Path,
        dry_run: bool,
        verbose: bool,
    ) -> List[Path]:
        """Generate legacy configuration for backward compatibility."""
        kiro_dir = output_dir / ".kiro"
        created_files = []

        # Create configuration content
        config_content = self._build_config(prompt)
        prompts_content = self._build_prompts(prompt, conditional_content)

        config_file = kiro_dir / "config.json"
        prompts_file = kiro_dir / "prompts.md"

        if dry_run:
            click.echo(f"  📁 Would create: {config_file} (legacy compatibility)")
            click.echo(f"  📁 Would create: {prompts_file} (legacy compatibility)")
            if verbose:
                preview = (
                    config_content[:200] + "..."
                    if len(config_content) > 200
                    else config_content
                )
                click.echo(f"    {preview}")
        else:
            kiro_dir.mkdir(exist_ok=True)

            with open(config_file, "w", encoding="utf-8") as f:
                f.write(config_content)
            created_files.append(config_file)
            click.echo(f"✅ Generated: {config_file} (legacy compatibility)")

            with open(prompts_file, "w", encoding="utf-8") as f:
                f.write(prompts_content)
            created_files.append(prompts_file)
            click.echo(f"✅ Generated: {prompts_file} (legacy compatibility)")

        return created_files

    def validate(self, prompt: UniversalPrompt) -> List[ValidationError]:
        """Validate prompt for Kiro."""
        errors = []

        # Kiro works well with structured instructions
        if not prompt.instructions:
            errors.append(
                ValidationError(
                    field="instructions",
                    message="Kiro benefits from detailed instructions for AI assistance",
                    severity="warning",
                )
            )

        return errors

    def supports_variables(self) -> bool:
        """Kiro supports variable substitution."""
        return True

    def supports_conditionals(self) -> bool:
        """Kiro supports conditional configuration."""
        return True

    def supports_hooks(self) -> bool:
        """Kiro supports hooks system."""
        return True

    def _build_config(self, prompt: UniversalPrompt) -> str:
        """Build Kiro configuration content."""
        config = {
            "name": prompt.metadata.title,
            "description": prompt.metadata.description,
            "version": prompt.metadata.version,
            "settings": {
                "auto_suggest": True,
                "context_aware": True,
                "smart_completions": True,
                "learning_mode": True,
            },
            "prompts_file": "prompts.md",
        }

        # Add project context
        if prompt.context:
            config["project"] = {}
            if prompt.context.project_type:
                config["project"]["type"] = prompt.context.project_type
            if prompt.context.technologies:
                config["project"]["technologies"] = prompt.context.technologies
                config["settings"]["language_specific"] = True

        # Add editor-specific configuration
        if prompt.editor_specific and "kiro" in prompt.editor_specific:
            kiro_config = prompt.editor_specific["kiro"]
            if hasattr(kiro_config, "settings"):
                config["settings"].update(kiro_config.settings)

        return json.dumps(config, indent=2)

    def _build_prompts(
        self,
        prompt: UniversalPrompt,
        conditional_content: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Build Kiro prompts markdown content."""
        lines = []

        # Header
        lines.append(f"# {prompt.metadata.title} - Kiro AI Prompts")
        lines.append("")
        lines.append("## Project Overview")
        lines.append(prompt.metadata.description)
        lines.append("")

        # Context section
        if prompt.context:
            lines.append("## Project Context")
            if prompt.context.project_type:
                lines.append(f"**Type:** {prompt.context.project_type}")
            if prompt.context.technologies:
                lines.append(
                    f"**Technologies:** {', '.join(prompt.context.technologies)}"
                )
            if prompt.context.description:
                lines.append("")
                lines.append("**Description:**")
                lines.append(prompt.context.description)
            lines.append("")

        # AI Assistant Instructions
        lines.append("## AI Assistant Instructions")
        lines.append("")

        if prompt.instructions:
            if prompt.instructions.general:
                lines.append("### General Guidelines")
                for instruction in prompt.instructions.general:
                    lines.append(f"- {instruction}")
                lines.append("")

            if prompt.instructions.code_style:
                lines.append("### Code Style Guidelines")
                for guideline in prompt.instructions.code_style:
                    lines.append(f"- {guideline}")
                lines.append("")

            if prompt.instructions.testing:
                lines.append("### Testing Guidelines")
                for guideline in prompt.instructions.testing:
                    lines.append(f"- {guideline}")
                lines.append("")

        # Smart Suggestions
        lines.append("## Smart Suggestions")
        lines.append("")
        lines.append("Kiro should provide intelligent suggestions for:")
        lines.append("- Code completion based on project patterns")
        lines.append("- Refactoring opportunities")
        lines.append("- Best practice recommendations")
        lines.append("- Performance optimizations")
        if prompt.context and prompt.context.technologies:
            tech_list = ", ".join(prompt.context.technologies)
            lines.append(f"- {tech_list}-specific improvements")
        lines.append("")

        # Examples if available
        if prompt.examples:
            lines.append("## Code Examples")
            lines.append("")
            lines.append("Use these examples as reference patterns:")
            lines.append("")

            for name, example in prompt.examples.items():
                lines.append(f"### {name.replace('_', ' ').title()}")
                lines.append(example)
                lines.append("")

        return "\n".join(lines)

    def _build_product_steering(self, prompt: UniversalPrompt) -> str:
        """Build product overview steering content."""
        lines = []

        lines.append("---")
        lines.append("inclusion: always")
        lines.append("---")
        lines.append("")
        lines.append(f"# {prompt.metadata.title} - Product Overview")
        lines.append("")
        lines.append("## Product Description")
        lines.append(prompt.metadata.description)
        lines.append("")

        if prompt.context:
            if prompt.context.project_type:
                lines.append("## Project Type")
                lines.append(f"{prompt.context.project_type}")
                lines.append("")

            if prompt.context.description:
                lines.append("## Detailed Description")
                lines.append(prompt.context.description)
                lines.append("")

        lines.append("## Product Goals")
        if prompt.instructions and prompt.instructions.general:
            for instruction in prompt.instructions.general[:3]:  # Take first 3 as goals
                lines.append(f"- {instruction}")
        else:
            lines.append("- Deliver high-quality, maintainable code")
            lines.append("- Follow industry best practices")
            lines.append("- Ensure scalable architecture")

        return "\n".join(lines)

    def _build_tech_steering(self, prompt: UniversalPrompt) -> str:
        """Build technology stack steering content."""
        lines = []

        lines.append("---")
        lines.append("inclusion: always")
        lines.append("---")
        lines.append("")
        lines.append("# Technology Stack")
        lines.append("")

        if prompt.context and prompt.context.technologies:
            lines.append("## Core Technologies")
            for tech in prompt.context.technologies:
                lines.append(f"- **{tech}**: Primary technology for implementation")
            lines.append("")

            lines.append("## Technology Guidelines")
            for tech in prompt.context.technologies:
                lines.append(f"### {tech}")
                tech_guidelines = self._get_tech_guidelines(tech.lower())
                for guideline in tech_guidelines:
                    lines.append(f"- {guideline}")
                lines.append("")

        if prompt.instructions and prompt.instructions.code_style:
            lines.append("## Code Style Requirements")
            for guideline in prompt.instructions.code_style:
                lines.append(f"- {guideline}")

        return "\n".join(lines)

    def _build_structure_steering(self, prompt: UniversalPrompt) -> str:
        """Build project structure steering content."""
        lines = []

        lines.append("---")
        lines.append("inclusion: always")
        lines.append("---")
        lines.append("")
        lines.append("# Project Structure")
        lines.append("")
        lines.append("## Architecture Overview")

        if prompt.context and prompt.context.project_type:
            project_structure = self._get_project_structure(
                prompt.context.project_type.lower()
            )
            lines.append(
                f"This is a {prompt.context.project_type} project with the following structure:"
            )
            lines.append("")
            for item in project_structure:
                lines.append(f"- {item}")
        else:
            lines.append("- Organized modular architecture")
            lines.append("- Clear separation of concerns")
            lines.append("- Scalable file organization")

        lines.append("")
        lines.append("## Organization Principles")
        lines.append("- Follow established project conventions")
        lines.append("- Maintain clear directory structure")
        lines.append("- Use consistent naming patterns")
        lines.append("- Keep related files grouped together")

        return "\n".join(lines)

    def _build_api_standards_steering(self, prompt: UniversalPrompt) -> str:
        """Build API standards steering content with file matching."""
        lines = []

        lines.append("---")
        lines.append("inclusion: fileMatch")
        lines.append('fileMatchPattern: "**/api/**/*.{ts,js,py,go,java}"')
        lines.append("---")
        lines.append("")
        lines.append("# API REST Conventions")
        lines.append("")
        lines.append("This steering file provides comprehensive guidelines for REST API development, ensuring consistency, security, and maintainability across all API endpoints.")
        lines.append("")
        lines.append("## Why These Conventions Matter")
        lines.append("- **Consistency**: Predictable API behavior improves developer experience")
        lines.append("- **Security**: Proper implementation prevents common vulnerabilities")
        lines.append("- **Maintainability**: Clear patterns reduce cognitive load for future changes")
        lines.append("- **Scalability**: Well-designed APIs handle growth gracefully")
        lines.append("")
        lines.append("## REST Conventions")
        lines.append("")
        lines.append("### HTTP Status Codes")
        lines.append("```")
        lines.append("200 OK - Successful GET, PUT, PATCH")
        lines.append("201 Created - Successful POST that creates a resource")
        lines.append("204 No Content - Successful DELETE or PUT with no return value")
        lines.append("400 Bad Request - Invalid request syntax or validation error")
        lines.append("401 Unauthorized - Authentication required")
        lines.append("403 Forbidden - Authentication valid but insufficient permissions")
        lines.append("404 Not Found - Resource does not exist")
        lines.append("422 Unprocessable Entity - Valid syntax but semantic errors")
        lines.append("500 Internal Server Error - Unexpected server error")
        lines.append("```")
        lines.append("")
        lines.append("### URL Patterns")
        lines.append("- Use nouns for resources: `/users`, `/orders`, `/products`")
        lines.append("- Use HTTP verbs for actions: `GET /users/123`, `POST /users`")
        lines.append("- Nested resources: `/users/123/orders` for related data")
        lines.append("- Query parameters for filtering: `/users?role=admin&active=true`")
        lines.append("")
        lines.append("### Response Format Standards")
        lines.append("```json")
        lines.append("{")
        lines.append('  "data": {...},')
        lines.append('  "meta": {')
        lines.append('    "timestamp": "2023-01-01T00:00:00Z",')
        lines.append('    "version": "1.0"')
        lines.append("  }")
        lines.append("}")
        lines.append("```")
        lines.append("")
        lines.append("## Security Implementation")
        lines.append("")
        lines.append("### Authentication Requirements")
        lines.append("- Always validate authentication tokens")
        lines.append("- Implement proper session management")
        lines.append("- Use secure token storage (HttpOnly cookies or secure storage)")
        lines.append("")
        lines.append("### Input Validation")
        lines.append("- Validate all inputs at the API boundary")
        lines.append("- Sanitize data before processing")
        lines.append("- Use schema validation for request bodies")
        lines.append("- Implement rate limiting to prevent abuse")
        lines.append("")

        if prompt.instructions and prompt.instructions.general:
            lines.append("## Additional API Guidelines")
            for instruction in prompt.instructions.general:
                if any(
                    keyword in instruction.lower()
                    for keyword in ["api", "endpoint", "request", "response"]
                ):
                    lines.append(f"- {instruction}")

        return "\n".join(lines)

    def _build_component_patterns_steering(self, prompt: UniversalPrompt) -> str:
        """Build component development patterns steering content."""
        lines = []

        lines.append("---")
        lines.append("inclusion: fileMatch")
        lines.append('fileMatchPattern: "**/components/**/*.{tsx,jsx,vue,svelte}"')
        lines.append("---")
        lines.append("")
        lines.append("# Component Development Patterns")
        lines.append("")
        lines.append("This steering file establishes patterns for building maintainable, reusable, and testable UI components. These patterns ensure consistency across the codebase and improve developer productivity.")
        lines.append("")
        lines.append("## Core Principles")
        lines.append("- **Single Responsibility**: Each component should have one clear purpose")
        lines.append("- **Composition over Inheritance**: Build complex UIs by combining simple components")
        lines.append("- **Predictable State**: Component behavior should be easy to understand and debug")
        lines.append("- **Accessibility First**: Every component should be usable by everyone")
        lines.append("")

        # Determine frontend framework
        if prompt.context and prompt.context.technologies:
            frameworks = [
                tech
                for tech in prompt.context.technologies
                if tech.lower() in ["react", "vue", "angular", "svelte"]
            ]
            if frameworks:
                framework = frameworks[0]
                lines.append(f"## {framework} Guidelines")
                framework_guidelines = self._get_frontend_guidelines(framework.lower())
                for guideline in framework_guidelines:
                    lines.append(f"- {guideline}")
                lines.append("")

        lines.append("## Component Structure")
        lines.append("")
        lines.append("### File Organization")
        lines.append("```")
        lines.append("components/")
        lines.append("  ├── ui/              # Basic UI components (Button, Input, etc.)")
        lines.append("  ├── layout/          # Layout components (Header, Sidebar, etc.)")
        lines.append("  ├── features/        # Feature-specific components")
        lines.append("  └── common/          # Shared business logic components")
        lines.append("```")
        lines.append("")
        lines.append("### Naming Conventions")
        lines.append("- PascalCase for component names: `UserProfile`, `NavigationMenu`")
        lines.append("- camelCase for props and methods: `onItemClick`, `isLoading`")
        lines.append("- kebab-case for CSS classes: `user-profile`, `navigation-menu`")
        lines.append("")
        lines.append("## Development Best Practices")
        lines.append("")
        lines.append("### Prop Validation")
        lines.append("- Always define prop types or interfaces")
        lines.append("- Provide default values where appropriate")
        lines.append("- Document complex prop structures")
        lines.append("")
        lines.append("### State Management")
        lines.append("- Keep component state minimal and focused")
        lines.append("- Lift state up when multiple components need it")
        lines.append("- Use global state management for app-wide data")
        lines.append("")
        lines.append("### Performance Optimization")
        lines.append("- Memoize expensive calculations")
        lines.append("- Implement proper component splitting")
        lines.append("- Use lazy loading for route-level components")
        lines.append("- Optimize re-renders with proper dependency arrays")
        lines.append("")
        lines.append("## Accessibility Standards")
        lines.append("- Include proper ARIA labels and roles")
        lines.append("- Ensure keyboard navigation support")
        lines.append("- Maintain sufficient color contrast ratios")
        lines.append("- Test with screen readers during development")

        return "\n".join(lines)

    def _build_requirements_spec(self, prompt: UniversalPrompt) -> str:
        """Build requirements specification content."""
        lines = []

        lines.append(f"# {prompt.metadata.title} - Requirements")
        lines.append("")
        lines.append("## Project Overview")
        lines.append(prompt.metadata.description)
        lines.append("")

        if prompt.context:
            lines.append("## Functional Requirements")
            if prompt.instructions and prompt.instructions.general:
                for i, instruction in enumerate(prompt.instructions.general, 1):
                    lines.append(f"### FR{i:02d}: {instruction}")
                    lines.append("**Description:** Detailed implementation requirement")
                    lines.append("**Priority:** High")
                    lines.append("**Acceptance Criteria:**")
                    lines.append("- [ ] Implementation meets specified requirements")
                    lines.append("- [ ] Code follows project standards")
                    lines.append("- [ ] Testing coverage is adequate")
                    lines.append("")

            lines.append("## Non-Functional Requirements")
            lines.append("### Performance")
            lines.append("- System should respond within acceptable time limits")
            lines.append("- Code should be optimized for efficiency")
            lines.append("")
            lines.append("### Quality")
            lines.append("- Code should be maintainable and readable")
            lines.append("- Proper error handling should be implemented")
            lines.append("- Documentation should be comprehensive")

        return "\n".join(lines)

    def _build_design_spec(self, prompt: UniversalPrompt) -> str:
        """Build design specification content."""
        lines = []

        lines.append(f"# {prompt.metadata.title} - Technical Design")
        lines.append("")
        lines.append("## Architecture Overview")
        lines.append(prompt.metadata.description)
        lines.append("")

        if prompt.context:
            if prompt.context.technologies:
                lines.append("## Technology Stack")
                for tech in prompt.context.technologies:
                    lines.append(f"- **{tech}**: {self._get_tech_role(tech.lower())}")
                lines.append("")

            lines.append("## System Architecture")
            lines.append("### Component Design")
            lines.append("- Modular architecture with clear separation of concerns")
            lines.append("- Reusable components following established patterns")
            lines.append("- Scalable and maintainable code structure")
            lines.append("")

            if prompt.instructions and prompt.instructions.code_style:
                lines.append("### Design Principles")
                for principle in prompt.instructions.code_style:
                    lines.append(f"- {principle}")
                lines.append("")

        lines.append("## Implementation Guidelines")
        lines.append("- Follow established coding standards")
        lines.append("- Implement proper error handling")
        lines.append("- Include comprehensive logging")
        lines.append("- Ensure testability and modularity")

        return "\n".join(lines)

    def _build_tasks_spec(self, prompt: UniversalPrompt) -> str:
        """Build tasks specification content."""
        lines = []

        lines.append(f"# {prompt.metadata.title} - Implementation Tasks")
        lines.append("")
        lines.append("## Task Breakdown")
        lines.append("")

        if prompt.instructions:
            task_num = 1

            if prompt.instructions.general:
                lines.append("### Core Implementation Tasks")
                for instruction in prompt.instructions.general:
                    lines.append(f"#### Task {task_num}: {instruction}")
                    lines.append("**Status:** Not Started")
                    lines.append("**Estimated Effort:** TBD")
                    lines.append("**Dependencies:** None")
                    lines.append("**Acceptance Criteria:**")
                    lines.append(f"- [ ] {instruction}")
                    lines.append("- [ ] Code reviewed and approved")
                    lines.append("- [ ] Tests implemented and passing")
                    lines.append("")
                    task_num += 1

            if prompt.instructions.testing:
                lines.append("### Testing Tasks")
                for test_instruction in prompt.instructions.testing:
                    lines.append(f"#### Task {task_num}: {test_instruction}")
                    lines.append("**Status:** Not Started")
                    lines.append("**Type:** Testing")
                    lines.append("**Acceptance Criteria:**")
                    lines.append(f"- [ ] {test_instruction}")
                    lines.append("- [ ] Test coverage meets requirements")
                    lines.append("")
                    task_num += 1

        lines.append("## Progress Tracking")
        lines.append("- **Total Tasks:** TBD")
        lines.append("- **Completed:** 0")
        lines.append("- **In Progress:** 0")
        lines.append("- **Not Started:** TBD")

        return "\n".join(lines)

    def _get_tech_guidelines(self, tech: str) -> List[str]:
        """Get technology-specific guidelines."""
        guidelines = {
            "typescript": [
                "Use strict TypeScript configuration",
                "Prefer interfaces over types for object shapes",
                "Include proper type annotations",
            ],
            "react": [
                "Use functional components with hooks",
                "Implement proper prop validation",
                "Follow React best practices",
            ],
            "python": [
                "Follow PEP 8 style guidelines",
                "Use type hints for function signatures",
                "Implement proper error handling",
            ],
            "node": [
                "Use async/await for asynchronous operations",
                "Implement proper error handling middleware",
                "Follow Node.js best practices",
            ],
        }
        return guidelines.get(
            tech, ["Follow established best practices", "Maintain code consistency"]
        )

    def _get_project_structure(self, project_type: str) -> List[str]:
        """Get project structure based on type."""
        structures = {
            "web application": [
                "src/ - Source code directory",
                "public/ - Static assets",
                "tests/ - Test files",
                "docs/ - Documentation",
            ],
            "api": [
                "src/ - Source code",
                "routes/ - API route definitions",
                "middleware/ - Custom middleware",
                "tests/ - API tests",
            ],
            "library": [
                "src/ - Library source code",
                "lib/ - Compiled output",
                "examples/ - Usage examples",
                "docs/ - API documentation",
            ],
        }
        return structures.get(
            project_type,
            ["src/ - Source code", "tests/ - Test files", "docs/ - Documentation"],
        )

    def _get_frontend_guidelines(self, framework: str) -> List[str]:
        """Get frontend framework guidelines."""
        guidelines = {
            "react": [
                "Use functional components with hooks",
                "Implement proper state management",
                "Use React.memo for optimization when needed",
            ],
            "vue": [
                "Use Vue 3 Composition API",
                "Implement proper reactive data patterns",
                "Follow Vue style guide conventions",
            ],
            "angular": [
                "Use Angular CLI for project structure",
                "Implement proper dependency injection",
                "Follow Angular style guide",
            ],
        }
        return guidelines.get(
            framework,
            ["Follow framework best practices", "Implement proper component patterns"],
        )

    def _get_tech_role(self, tech: str) -> str:
        """Get the role description for a technology."""
        roles = {
            "typescript": "Primary language for type-safe development",
            "javascript": "Core scripting language",
            "react": "Frontend framework for UI components",
            "node": "Backend runtime environment",
            "python": "Backend development and scripting",
            "go": "High-performance backend services",
            "rust": "Systems programming and performance-critical code",
        }
        return roles.get(tech, "Development technology")

    def _generate_hooks_system(
        self,
        prompt: UniversalPrompt,
        output_dir: Path,
        dry_run: bool,
        verbose: bool,
    ) -> List[Path]:
        """Generate .kiro/hooks/ system for reusable hooks."""
        hooks_dir = output_dir / ".kiro" / "hooks"
        created_files = []

        # Generate code quality hook
        quality_hook = hooks_dir / "code-quality.md"
        quality_content = self._build_code_quality_hook(prompt)

        if dry_run:
            click.echo(f"  📁 Would create: {quality_hook}")
            if verbose:
                preview = (
                    quality_content[:200] + "..."
                    if len(quality_content) > 200
                    else quality_content
                )
                click.echo(f"    {preview}")
        else:
            hooks_dir.mkdir(parents=True, exist_ok=True)
            with open(quality_hook, "w", encoding="utf-8") as f:
                f.write(quality_content)
            click.echo(f"✅ Generated: {quality_hook}")
            created_files.append(quality_hook)

        # Generate pre-commit hook if applicable
        if prompt.instructions and prompt.instructions.testing:
            precommit_hook = hooks_dir / "pre-commit.md"
            precommit_content = self._build_precommit_hook(prompt)

            if dry_run:
                click.echo(f"  📁 Would create: {precommit_hook}")
                if verbose:
                    preview = (
                        precommit_content[:200] + "..."
                        if len(precommit_content) > 200
                        else precommit_content
                    )
                    click.echo(f"    {preview}")
            else:
                hooks_dir.mkdir(parents=True, exist_ok=True)
                with open(precommit_hook, "w", encoding="utf-8") as f:
                    f.write(precommit_content)
                click.echo(f"✅ Generated: {precommit_hook}")
                created_files.append(precommit_hook)

        return created_files

    def _generate_prompts_system(
        self,
        prompt: UniversalPrompt,
        output_dir: Path,
        dry_run: bool,
        verbose: bool,
    ) -> List[Path]:
        """Generate .prompts/ system for reusable prompts."""
        prompts_dir = output_dir / ".prompts"
        created_files = []

        # Generate development prompts
        dev_prompt = prompts_dir / "development.md"
        dev_content = self._build_development_prompts(prompt)

        if dry_run:
            click.echo(f"  📁 Would create: {dev_prompt}")
            if verbose:
                preview = (
                    dev_content[:200] + "..."
                    if len(dev_content) > 200
                    else dev_content
                )
                click.echo(f"    {preview}")
        else:
            prompts_dir.mkdir(parents=True, exist_ok=True)
            with open(dev_prompt, "w", encoding="utf-8") as f:
                f.write(dev_content)
            click.echo(f"✅ Generated: {dev_prompt}")
            created_files.append(dev_prompt)

        # Generate refactoring prompts if applicable
        if prompt.instructions and prompt.instructions.code_style:
            refactor_prompt = prompts_dir / "refactoring.md"
            refactor_content = self._build_refactoring_prompts(prompt)

            if dry_run:
                click.echo(f"  📁 Would create: {refactor_prompt}")
                if verbose:
                    preview = (
                        refactor_content[:200] + "..."
                        if len(refactor_content) > 200
                        else refactor_content
                    )
                    click.echo(f"    {preview}")
            else:
                prompts_dir.mkdir(parents=True, exist_ok=True)
                with open(refactor_prompt, "w", encoding="utf-8") as f:
                    f.write(refactor_content)
                click.echo(f"✅ Generated: {refactor_prompt}")
                created_files.append(refactor_prompt)

        return created_files

    def _build_code_quality_hook(self, prompt: UniversalPrompt) -> str:
        """Build code quality hook content."""
        lines = []

        lines.append("# Code Quality Hook")
        lines.append("")
        lines.append("Automatically triggered on file save and before commits.")
        lines.append("")
        lines.append("## Quality Checks")
        lines.append("")

        if prompt.instructions and prompt.instructions.code_style:
            lines.append("### Code Style Validation")
            for style_rule in prompt.instructions.code_style:
                lines.append(f"- {style_rule}")
            lines.append("")

        if prompt.context and prompt.context.technologies:
            lines.append("### Technology-Specific Checks")
            for tech in prompt.context.technologies:
                tech_checks = self._get_tech_quality_checks(tech.lower())
                if tech_checks:
                    lines.append(f"#### {tech}")
                    for check in tech_checks:
                        lines.append(f"- {check}")
                    lines.append("")

        lines.append("## Execution Triggers")
        lines.append("- On file save")
        lines.append("- Before git commit")
        lines.append("- Before merge requests")

        return "\n".join(lines)

    def _build_precommit_hook(self, prompt: UniversalPrompt) -> str:
        """Build pre-commit hook content."""
        lines = []

        lines.append("# Pre-Commit Hook")
        lines.append("")
        lines.append("Validates code quality before allowing commits.")
        lines.append("")
        lines.append("## Test Requirements")

        if prompt.instructions and prompt.instructions.testing:
            for test_rule in prompt.instructions.testing:
                lines.append(f"- {test_rule}")
        else:
            lines.append("- All tests must pass")
            lines.append("- Code coverage must meet minimum threshold")

        lines.append("")
        lines.append("## Quality Gates")
        lines.append("- Lint checks must pass")
        lines.append("- Type checking must pass")
        lines.append("- Security scan must pass")
        lines.append("")
        lines.append("## Bypass Options")
        lines.append("Use `--no-verify` flag to bypass (not recommended)")

        return "\n".join(lines)

    def _build_development_prompts(self, prompt: UniversalPrompt) -> str:
        """Build development prompts content."""
        lines = []

        lines.append(f"# {prompt.metadata.title} - Development Prompts")
        lines.append("")
        lines.append("## Feature Development")
        lines.append("")
        lines.append("### New Feature Prompt")
        lines.append("```")
        lines.append(f"I'm working on {prompt.metadata.title}.")
        if prompt.context and prompt.context.technologies:
            tech_list = ", ".join(prompt.context.technologies)
            lines.append(f"This project uses: {tech_list}")
        lines.append("")
        lines.append("Please help me implement [feature description]:")
        lines.append("- Follow the project's established patterns")
        lines.append("- Include appropriate tests")
        lines.append("- Ensure code quality standards")
        lines.append("```")
        lines.append("")

        lines.append("### Bug Fix Prompt")
        lines.append("```")
        lines.append(f"I'm debugging an issue in {prompt.metadata.title}.")
        lines.append("")
        lines.append("Problem: [describe the bug]")
        lines.append("Expected: [what should happen]")
        lines.append("Actual: [what actually happens]")
        lines.append("")
        lines.append("Please help me:")
        lines.append("1. Identify the root cause")
        lines.append("2. Implement a fix")
        lines.append("3. Add tests to prevent regression")
        lines.append("```")

        return "\n".join(lines)

    def _build_refactoring_prompts(self, prompt: UniversalPrompt) -> str:
        """Build refactoring prompts content."""
        lines = []

        lines.append(f"# {prompt.metadata.title} - Refactoring Prompts")
        lines.append("")
        lines.append("## Code Improvement")
        lines.append("")
        lines.append("### Refactoring Prompt")
        lines.append("```")
        lines.append(f"I want to refactor code in {prompt.metadata.title}.")
        lines.append("")
        lines.append("Code to refactor:")
        lines.append("[paste code here]")
        lines.append("")
        lines.append("Please help me improve this code by:")

        if prompt.instructions and prompt.instructions.code_style:
            for style_rule in prompt.instructions.code_style[:3]:  # Take first 3
                lines.append(f"- {style_rule}")
        else:
            lines.append("- Improving readability")
            lines.append("- Reducing complexity")
            lines.append("- Following best practices")

        lines.append("```")
        lines.append("")

        lines.append("### Performance Optimization")
        lines.append("```")
        lines.append("I need to optimize performance in this code:")
        lines.append("[paste code here]")
        lines.append("")
        lines.append("Please suggest optimizations while maintaining:")
        lines.append("- Code readability")
        lines.append("- Test coverage")
        lines.append("- Existing functionality")
        lines.append("```")

        return "\n".join(lines)

    def _get_tech_quality_checks(self, tech: str) -> List[str]:
        """Get technology-specific quality checks."""
        checks = {
            "typescript": [
                "TypeScript strict mode compliance",
                "Proper type annotations",
                "No 'any' types without justification",
            ],
            "react": [
                "Component prop validation",
                "Proper hook usage",
                "No unused components or props",
            ],
            "python": [
                "PEP 8 compliance",
                "Type hints for function signatures",
                "Docstring coverage",
            ],
            "node": [
                "Async/await error handling",
                "Security best practices",
                "Performance optimizations",
            ],
        }
        return checks.get(tech, [])

    def generate_merged(
        self,
        prompt_files: List[Tuple[UniversalPrompt, Path]],
        output_dir: Path,
        dry_run: bool = False,
        verbose: bool = False,
        variables: Optional[Dict[str, Any]] = None,
    ) -> List[Path]:
        """
        Generate Kiro configuration files from multiple merged promptrek files.

        Args:
            prompt_files: List of (prompt, source_file) tuples
            output_dir: Directory to generate files in
            dry_run: If True, don't create files, just show what would be created
            verbose: Enable verbose output
            variables: Additional variables for substitution

        Returns:
            List of file paths that were created (or would be created in dry run)
        """
        if verbose:
            source_files = [str(pf[1]) for pf in prompt_files]
            click.echo(f"Merging {len(prompt_files)} promptrek files: {', '.join(source_files)}")

        # Merge all prompts into one
        merged_prompt = prompt_files[0][0]  # Start with the first prompt
        for prompt, source_file in prompt_files[1:]:
            merged_prompt = self._merge_prompts_for_generation(merged_prompt, prompt)
            if verbose:
                click.echo(f"  Merged content from {source_file}")

        # Use the regular generate method with the merged prompt
        return self.generate(merged_prompt, output_dir, dry_run, verbose, variables)

    def _merge_prompts_for_generation(
        self, base: UniversalPrompt, additional: UniversalPrompt
    ) -> UniversalPrompt:
        """
        Merge two prompts specifically for Kiro generation.
        This is a simpler version focused on what Kiro needs.
        """
        # Import the parser's merge method
        from ..core.parser import UPFParser

        parser = UPFParser()
        return parser._merge_prompts(base, additional)
