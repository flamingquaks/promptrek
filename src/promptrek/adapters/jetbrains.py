"""
JetBrains AI (IDE-integrated) adapter implementation.
"""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

import click

from ..core.exceptions import ValidationError
from ..core.models import UniversalPrompt
from .base import EditorAdapter


class JetBrainsAdapter(EditorAdapter):
    """Adapter for JetBrains AI IDE-integrated assistance."""

    _description = "JetBrains AI (IDE-integrated)"
    _file_patterns = [".idea/ai-assistant.xml", ".jetbrains/config.json"]

    def __init__(self):
        super().__init__(
            name="jetbrains",
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
        """Generate JetBrains AI configuration files."""

        # Apply variable substitution if supported
        processed_prompt = self.substitute_variables(prompt, variables)

        # Create IDE configuration content
        xml_content = self._build_ide_config(processed_prompt)

        # Create JSON configuration content
        json_content = self._build_json_config(processed_prompt)

        # Determine output paths
        idea_dir = output_dir / ".idea"
        jetbrains_dir = output_dir / ".jetbrains"
        xml_file = idea_dir / "ai-assistant.xml"
        json_file = jetbrains_dir / "config.json"

        created_files = []

        if dry_run:
            click.echo(f"  📁 Would create: {xml_file}")
            click.echo(f"  📁 Would create: {json_file}")
            if verbose:
                click.echo("  📄 XML config preview:")
                preview = (
                    xml_content[:200] + "..." if len(xml_content) > 200 else xml_content
                )
                click.echo(f"    {preview}")
        else:
            # Create directories and files
            idea_dir.mkdir(exist_ok=True)
            with open(xml_file, "w", encoding="utf-8") as f:
                f.write(xml_content)
            created_files.append(xml_file)
            click.echo(f"✅ Generated: {xml_file}")

            jetbrains_dir.mkdir(exist_ok=True)
            with open(json_file, "w", encoding="utf-8") as f:
                f.write(json_content)
            created_files.append(json_file)
            click.echo(f"✅ Generated: {json_file}")

        return created_files or [xml_file, json_file]

    def validate(self, prompt: UniversalPrompt) -> List[ValidationError]:
        """Validate prompt for JetBrains AI."""
        errors = []

        # JetBrains works well with structured development guidelines
        if not prompt.instructions:
            errors.append(
                ValidationError(
                    field="instructions",
                    message="JetBrains AI benefits from structured development guidelines",
                    severity="warning",
                )
            )

        return errors

    def supports_variables(self) -> bool:
        """JetBrains supports variable substitution."""
        return True

    def supports_conditionals(self) -> bool:
        """JetBrains supports conditional configuration."""
        return True

    def _build_ide_config(self, prompt: UniversalPrompt) -> str:
        """Build JetBrains IDE configuration XML content."""
        lines = []

        # XML header
        lines.append('<?xml version="1.0" encoding="UTF-8"?>')
        lines.append("<application>")
        lines.append('  <component name="AIAssistant">')
        lines.append(
            f'    <option name="projectName" value="{prompt.metadata.title}" />'
        )
        lines.append(
            f'    <option name="projectDescription" value="{prompt.metadata.description}" />'
        )
        lines.append('    <option name="aiAssistanceEnabled" value="true" />')
        lines.append('    <option name="smartCompletions" value="true" />')
        lines.append('    <option name="contextAware" value="true" />')
        lines.append("")

        # Project settings
        if prompt.context:
            lines.append("    <projectSettings>")
            if prompt.context.project_type:
                lines.append(
                    f'      <option name="projectType" value="{prompt.context.project_type}" />'
                )
            if prompt.context.technologies:
                lines.append("      <technologies>")
                for tech in prompt.context.technologies:
                    lines.append(f'        <technology name="{tech}" enabled="true" />')
                lines.append("      </technologies>")
            lines.append("    </projectSettings>")
            lines.append("")

        # Code style settings
        if prompt.instructions and prompt.instructions.code_style:
            lines.append("    <codeStyle>")
            for guideline in prompt.instructions.code_style:
                escaped_guideline = (
                    guideline.replace('"', "&quot;")
                    .replace("<", "&lt;")
                    .replace(">", "&gt;")
                )
                lines.append(f'      <rule description="{escaped_guideline}" />')
            lines.append("    </codeStyle>")
            lines.append("")

        # AI behavior settings
        lines.append("    <aiBehavior>")
        lines.append('      <option name="suggestionLevel" value="medium" />')
        lines.append('      <option name="autoImports" value="true" />')
        lines.append('      <option name="refactoringHints" value="true" />')
        lines.append('      <option name="codeGeneration" value="true" />')
        lines.append('      <option name="testGeneration" value="true" />')
        lines.append("    </aiBehavior>")
        lines.append("")

        # Close XML
        lines.append("  </component>")
        lines.append("</application>")

        return "\n".join(lines)

    def _build_json_config(self, prompt: UniversalPrompt) -> str:
        """Build JetBrains JSON configuration content."""
        config = {
            "version": "1.0",
            "project": {
                "name": prompt.metadata.title,
                "description": prompt.metadata.description,
                "version": prompt.metadata.version,
            },
            "ai_assistant": {
                "enabled": True,
                "features": {
                    "code_completion": True,
                    "code_generation": True,
                    "refactoring_suggestions": True,
                    "test_generation": True,
                    "documentation_generation": True,
                    "error_analysis": True,
                },
                "behavior": {
                    "suggestion_frequency": "medium",
                    "context_awareness": "high",
                    "learning_mode": True,
                },
            },
        }

        # Add language-specific settings
        if prompt.context and prompt.context.technologies:
            config["languages"] = {}
            for tech in prompt.context.technologies:
                tech_lower = tech.lower()
                config["languages"][tech_lower] = {
                    "enabled": True,
                    "completion_level": "advanced",
                    "framework_support": True,
                }

        # Add development guidelines
        if prompt.instructions:
            config["guidelines"] = {}

            if prompt.instructions.general:
                config["guidelines"]["general"] = prompt.instructions.general

            if prompt.instructions.code_style:
                config["guidelines"]["code_style"] = prompt.instructions.code_style

            if prompt.instructions.testing:
                config["guidelines"]["testing"] = prompt.instructions.testing

        # Add IDE-specific features
        config["ide_integration"] = {
            "inspection_hints": True,
            "quick_fixes": True,
            "live_templates": True,
            "intention_actions": True,
            "debugging_assistance": True,
        }

        # Add project type specific features
        if prompt.context and prompt.context.project_type:
            project_type = prompt.context.project_type
            if project_type in ["web_application", "api_service"]:
                config["ide_integration"]["web_development"] = {
                    "html_completion": True,
                    "css_assistance": True,
                    "api_testing": True,
                }
            elif project_type in ["mobile_app"]:
                config["ide_integration"]["mobile_development"] = {
                    "ui_generation": True,
                    "platform_specific": True,
                }

        # Add custom templates if examples exist
        if prompt.examples:
            config["templates"] = {}
            for name, example in prompt.examples.items():
                config["templates"][name] = {
                    "description": f"Template for {name.replace('_', ' ')}",
                    "content": example[:500] + "..." if len(example) > 500 else example,
                    "type": "code_snippet",
                }

        return json.dumps(config, indent=2)
