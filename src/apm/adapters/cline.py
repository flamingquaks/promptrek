"""
Cline (terminal-based AI assistant) adapter implementation.
"""

import json
import click
from pathlib import Path
from typing import List, Optional, Dict, Any

from .base import EditorAdapter
from ..core.models import UniversalPrompt
from ..core.exceptions import ValidationError


class ClineAdapter(EditorAdapter):
    """Adapter for Cline terminal-based AI assistant."""
    
    _description = "Cline (terminal-based)"
    _file_patterns = [".cline/config.json", "cline-context.md"]
    
    def __init__(self):
        super().__init__(
            name="cline",
            description=self._description,
            file_patterns=self._file_patterns
        )
    
    def generate(self, prompt: UniversalPrompt, output_dir: Path, dry_run: bool = False, 
                verbose: bool = False, variables: Optional[Dict[str, Any]] = None) -> List[Path]:
        """Generate Cline configuration and context files."""
        
        # Apply variable substitution if supported
        processed_prompt = self.substitute_variables(prompt, variables)
        
        # Create configuration content
        config_content = self._build_config(processed_prompt)
        
        # Create context content  
        context_content = self._build_context(processed_prompt)
        
        # Determine output paths
        cline_dir = output_dir / '.cline'
        config_file = cline_dir / 'config.json'
        context_file = output_dir / 'cline-context.md'
        
        created_files = []
        
        if dry_run:
            click.echo(f"  📁 Would create: {config_file}")
            click.echo(f"  📁 Would create: {context_file}")
            if verbose:
                click.echo("  📄 Config preview:")
                preview = config_content[:200] + "..." if len(config_content) > 200 else config_content
                click.echo(f"    {preview}")
        else:
            # Create directory and config file
            cline_dir.mkdir(exist_ok=True)
            with open(config_file, 'w', encoding='utf-8') as f:
                f.write(config_content)
            created_files.append(config_file)
            click.echo(f"✅ Generated: {config_file}")
            
            # Create context file
            with open(context_file, 'w', encoding='utf-8') as f:
                f.write(context_content)
            created_files.append(context_file)
            click.echo(f"✅ Generated: {context_file}")
        
        return created_files or [config_file, context_file]
    
    def validate(self, prompt: UniversalPrompt) -> List[ValidationError]:
        """Validate prompt for Cline."""
        errors = []
        
        # Cline works well with clear instructions and context
        if not prompt.instructions or not prompt.instructions.general:
            errors.append(ValidationError(
                field="instructions.general",
                message="Cline needs clear general instructions for terminal operations"
            ))
        
        return errors
    
    def supports_variables(self) -> bool:
        """Cline supports variable substitution."""
        return True
    
    def supports_conditionals(self) -> bool:
        """Cline supports conditional configuration."""
        return True
    
    def _build_config(self, prompt: UniversalPrompt) -> str:
        """Build Cline configuration content."""
        config = {
            "name": prompt.metadata.title,
            "description": prompt.metadata.description,
            "version": prompt.metadata.version,
            "contextFile": "cline-context.md",
            "settings": {
                "autoSuggest": True,
                "verboseLogging": False,
                "safeMode": True,
                "maxHistoryLength": 100
            }
        }
        
        # Add project-specific settings
        if prompt.context:
            config["project"] = {}
            if prompt.context.project_type:
                config["project"]["type"] = prompt.context.project_type
            if prompt.context.technologies:
                config["project"]["technologies"] = prompt.context.technologies
        
        # Add custom commands if available from editor_specific config
        if prompt.editor_specific and "cline" in prompt.editor_specific:
            cline_config = prompt.editor_specific["cline"]
            if hasattr(cline_config, 'custom_commands') and cline_config.custom_commands:
                config["customCommands"] = [
                    {
                        "name": cmd.name,
                        "description": cmd.description,
                        "prompt": cmd.prompt
                    }
                    for cmd in cline_config.custom_commands
                ]
        
        return json.dumps(config, indent=2)
    
    def _build_context(self, prompt: UniversalPrompt) -> str:
        """Build Cline context markdown content."""
        lines = []
        
        # Header
        lines.append(f"# {prompt.metadata.title} - Cline Context")
        lines.append("")
        lines.append("## Project Overview")
        lines.append(prompt.metadata.description)
        lines.append("")
        
        # Project Information
        if prompt.context:
            lines.append("## Project Information")
            if prompt.context.project_type:
                lines.append(f"**Type:** {prompt.context.project_type}")
            if prompt.context.technologies:
                lines.append(f"**Technologies:** {', '.join(prompt.context.technologies)}")
            if prompt.context.description:
                lines.append("")
                lines.append("**Details:**")
                lines.append(prompt.context.description)
            lines.append("")
        
        # Terminal and Development Instructions
        if prompt.instructions:
            lines.append("## Development Instructions")
            
            if prompt.instructions.general:
                lines.append("### General Guidelines")
                for instruction in prompt.instructions.general:
                    lines.append(f"- {instruction}")
                lines.append("")
            
            if prompt.instructions.code_style:
                lines.append("### Code Standards")
                for guideline in prompt.instructions.code_style:
                    lines.append(f"- {guideline}")
                lines.append("")
        
        # Terminal-specific guidance
        lines.append("## Terminal Operations")
        lines.append("")
        lines.append("When performing terminal operations:")
        lines.append("- Always confirm destructive operations before executing")
        lines.append("- Use safe commands and check file permissions")
        lines.append("- Provide clear explanations for complex command sequences")
        lines.append("- Respect the project structure and conventions")
        if prompt.context and prompt.context.technologies:
            lines.append(f"- Use appropriate tools for {', '.join(prompt.context.technologies)} development")
        lines.append("")
        
        # Examples if available
        if prompt.examples:
            lines.append("## Code Examples")
            for name, example in prompt.examples.items():
                lines.append(f"### {name.replace('_', ' ').title()}")
                lines.append(example)
                lines.append("")
        
        return "\n".join(lines)