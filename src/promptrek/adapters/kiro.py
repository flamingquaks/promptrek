"""
Kiro (AI-powered assistance) adapter implementation.
"""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

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
            api_file = steering_dir / "api-standards.md"
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
            frontend_file = steering_dir / "frontend-standards.md"
            frontend_content = self._build_frontend_standards_steering(prompt)

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
        lines.append('fileMatchPattern: "app/api/**/*"')
        lines.append("---")
        lines.append("")
        lines.append("# API Standards")
        lines.append("")
        lines.append("## REST Conventions")
        lines.append("- Use HTTP status codes properly")
        lines.append("- Follow RESTful naming patterns")
        lines.append("- Include proper error responses")
        lines.append("- Implement consistent response formats")
        lines.append("")
        lines.append("## Authentication & Security")
        lines.append("- Implement proper authentication mechanisms")
        lines.append("- Validate all inputs")
        lines.append("- Use HTTPS for all communications")
        lines.append("- Follow OWASP security guidelines")
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

    def _build_frontend_standards_steering(self, prompt: UniversalPrompt) -> str:
        """Build frontend standards steering content."""
        lines = []

        lines.append("---")
        lines.append("inclusion: fileMatch")
        lines.append('fileMatchPattern: "src/**/*.{tsx,jsx,ts,js,vue,svelte}"')
        lines.append("---")
        lines.append("")
        lines.append("# Frontend Standards")
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

        lines.append("## Component Development")
        lines.append("- Create reusable, modular components")
        lines.append("- Follow single responsibility principle")
        lines.append("- Implement proper prop validation")
        lines.append("- Use consistent naming conventions")
        lines.append("")
        lines.append("## Performance Guidelines")
        lines.append("- Optimize bundle size and loading times")
        lines.append("- Implement code splitting where appropriate")
        lines.append("- Use lazy loading for non-critical components")
        lines.append("- Follow accessibility best practices")

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
