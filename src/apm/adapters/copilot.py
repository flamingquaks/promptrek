"""
GitHub Copilot adapter implementation.
"""

import click
from pathlib import Path
from typing import List, Optional, Dict, Any

from .base import EditorAdapter
from ..core.models import UniversalPrompt
from ..core.exceptions import ValidationError


class CopilotAdapter(EditorAdapter):
    """Adapter for GitHub Copilot."""
    
    _description = "GitHub Copilot (.github/copilot-instructions.md)"
    _file_patterns = [".github/copilot-instructions.md", ".copilot/instructions.md"]
    
    def __init__(self):
        super().__init__(
            name="copilot",
            description=self._description,
            file_patterns=self._file_patterns
        )
    
    def generate(self, prompt: UniversalPrompt, output_dir: Path, dry_run: bool = False, 
                verbose: bool = False, variables: Optional[Dict[str, Any]] = None) -> List[Path]:
        """Generate GitHub Copilot instructions."""
        
        # Apply variable substitution if supported
        processed_prompt = self.substitute_variables(prompt, variables)
        
        # Create content
        content = self._build_content(processed_prompt)
        
        # Determine output path
        github_dir = output_dir / '.github'
        output_file = github_dir / 'copilot-instructions.md'
        
        if dry_run:
            click.echo(f"  📁 Would create: {output_file}")
            if verbose:
                click.echo("  📄 Content preview:")
                preview = content[:200] + "..." if len(content) > 200 else content
                click.echo(f"    {preview}")
        else:
            # Create directory and file
            github_dir.mkdir(exist_ok=True)
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(content)
            click.echo(f"✅ Generated: {output_file}")
        
        return [output_file]
    
    def validate(self, prompt: UniversalPrompt) -> List[ValidationError]:
        """Validate prompt for Copilot."""
        errors = []
        
        # Copilot works best with clear instructions
        if not prompt.instructions or not prompt.instructions.general:
            errors.append(ValidationError(
                field="instructions.general",
                message="GitHub Copilot works best with general instructions"
            ))
        
        return errors
    
    def supports_variables(self) -> bool:
        """Copilot supports variable substitution through templating."""
        return True
    
    def supports_conditionals(self) -> bool:
        """Copilot supports conditional instructions."""
        return True
    
    def _build_content(self, prompt: UniversalPrompt) -> str:
        """Build GitHub Copilot instructions content."""
        lines = []
        
        # Header
        lines.append(f"# {prompt.metadata.title}")
        lines.append("")
        lines.append(prompt.metadata.description)
        lines.append("")
        
        # Project Information
        if prompt.context:
            lines.append("## Project Information")
            if prompt.context.project_type:
                lines.append(f"- Type: {prompt.context.project_type}")
            if prompt.context.technologies:
                lines.append(f"- Technologies: {', '.join(prompt.context.technologies)}")
            if prompt.context.description:
                lines.append(f"- Description: {prompt.context.description}")
            lines.append("")
        
        # Instructions
        if prompt.instructions:
            if prompt.instructions.general:
                lines.append("## General Instructions")
                for instruction in prompt.instructions.general:
                    lines.append(f"- {instruction}")
                lines.append("")
            
            if prompt.instructions.code_style:
                lines.append("## Code Style Guidelines")
                for guideline in prompt.instructions.code_style:
                    lines.append(f"- {guideline}")
                lines.append("")
            
            if prompt.instructions.testing:
                lines.append("## Testing Guidelines")
                for guideline in prompt.instructions.testing:
                    lines.append(f"- {guideline}")
                lines.append("")
        
        # Examples
        if prompt.examples:
            lines.append("## Examples")
            for name, example in prompt.examples.items():
                lines.append(f"### {name.title()}")
                lines.append(example)
                lines.append("")
        
        return "\n".join(lines)