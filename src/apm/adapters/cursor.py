"""
Cursor editor adapter implementation.
"""

import click
from pathlib import Path
from typing import List

from .base import EditorAdapter
from ..core.models import UniversalPrompt
from ..core.exceptions import ValidationError


class CursorAdapter(EditorAdapter):
    """Adapter for Cursor editor."""
    
    _description = "Cursor (.cursorrules)"
    _file_patterns = [".cursorrules"]
    
    def __init__(self):
        super().__init__(
            name="cursor",
            description=self._description,
            file_patterns=self._file_patterns
        )
    
    def generate(self, prompt: UniversalPrompt, output_dir: Path, dry_run: bool = False, verbose: bool = False) -> List[Path]:
        """Generate Cursor rules."""
        
        # Create content
        content = self._build_content(prompt)
        
        # Determine output path
        output_file = output_dir / '.cursorrules'
        
        if dry_run:
            click.echo(f"  📁 Would create: {output_file}")
            if verbose:
                click.echo("  📄 Content preview:")
                preview = content[:200] + "..." if len(content) > 200 else content
                click.echo(f"    {preview}")
        else:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(content)
            click.echo(f"✅ Generated: {output_file}")
        
        return [output_file]
    
    def validate(self, prompt: UniversalPrompt) -> List[ValidationError]:
        """Validate prompt for Cursor."""
        errors = []
        
        # Cursor works well with structured instructions
        if not prompt.instructions:
            errors.append(ValidationError(
                field="instructions",
                message="Cursor works best with structured instructions"
            ))
        
        return errors
    
    def supports_variables(self) -> bool:
        """Cursor supports variable substitution."""
        return True
    
    def supports_conditionals(self) -> bool:
        """Cursor supports conditional instructions."""
        return True
    
    def _build_content(self, prompt: UniversalPrompt) -> str:
        """Build Cursor rules content."""
        lines = []
        
        lines.append(f"# {prompt.metadata.title}")
        lines.append("")
        lines.append(prompt.metadata.description)
        lines.append("")
        
        # Instructions
        if prompt.instructions:
            lines.append("## Instructions")
            
            for category, instructions in [
                ("General", prompt.instructions.general),
                ("Code Style", prompt.instructions.code_style),
                ("Testing", prompt.instructions.testing),
            ]:
                if instructions:
                    lines.append(f"### {category}")
                    for instruction in instructions:
                        lines.append(f"- {instruction}")
                    lines.append("")
        
        return "\n".join(lines)