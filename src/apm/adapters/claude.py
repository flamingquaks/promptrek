"""
Claude Code adapter implementation.
"""

import click
from pathlib import Path
from typing import List, Optional, Dict, Any

from .base import EditorAdapter
from ..core.models import UniversalPrompt
from ..core.exceptions import ValidationError


class ClaudeAdapter(EditorAdapter):
    """Adapter for Claude Code."""
    
    _description = "Claude Code (context-based)"
    _file_patterns = [".claude/context.md", ".claude-context.md"]
    
    def __init__(self):
        super().__init__(
            name="claude",
            description=self._description,
            file_patterns=self._file_patterns
        )
    
    def generate(self, prompt: UniversalPrompt, output_dir: Path, dry_run: bool = False, 
                verbose: bool = False, variables: Optional[Dict[str, Any]] = None) -> List[Path]:
        """Generate Claude Code context files."""
        
        # Apply variable substitution if supported
        processed_prompt = self.substitute_variables(prompt, variables)
        
        # Create content
        content = self._build_content(processed_prompt)
        
        # Determine output path - Claude works well with context files in .claude directory
        claude_dir = output_dir / '.claude'
        output_file = claude_dir / 'context.md'
        
        if dry_run:
            click.echo(f"  📁 Would create: {output_file}")
            if verbose:
                click.echo("  📄 Content preview:")
                preview = content[:200] + "..." if len(content) > 200 else content
                click.echo(f"    {preview}")
        else:
            # Create directory and file
            claude_dir.mkdir(exist_ok=True)
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(content)
            click.echo(f"✅ Generated: {output_file}")
        
        return [output_file]
    
    def validate(self, prompt: UniversalPrompt) -> List[ValidationError]:
        """Validate prompt for Claude."""
        errors = []
        
        # Claude works well with detailed context and examples
        if not prompt.context:
            errors.append(ValidationError(
                field="context",
                message="Claude works best with detailed project context information",
                severity="warning"
            ))
        
        if not prompt.examples:
            errors.append(ValidationError(
                field="examples",
                message="Claude benefits from code examples for better understanding",
                severity="warning"
            ))
        
        return errors
    
    def supports_variables(self) -> bool:
        """Claude supports variable substitution."""
        return True
    
    def supports_conditionals(self) -> bool:
        """Claude supports conditional instructions."""
        return True
    
    def _build_content(self, prompt: UniversalPrompt) -> str:
        """Build Claude Code context content."""
        lines = []
        
        # Header with clear context
        lines.append(f"# {prompt.metadata.title}")
        lines.append("")
        lines.append("## Project Overview")
        lines.append(prompt.metadata.description)
        lines.append("")
        
        # Project context is crucial for Claude
        if prompt.context:
            lines.append("## Project Details")
            if prompt.context.project_type:
                lines.append(f"**Project Type:** {prompt.context.project_type}")
            if prompt.context.technologies:
                lines.append(f"**Technologies:** {', '.join(prompt.context.technologies)}")
            if prompt.context.description:
                lines.append("")
                lines.append("**Description:**")
                lines.append(prompt.context.description)
            lines.append("")
        
        # Instructions organized for Claude's understanding
        if prompt.instructions:
            lines.append("## Development Guidelines")
            
            if prompt.instructions.general:
                lines.append("### General Principles")
                for instruction in prompt.instructions.general:
                    lines.append(f"- {instruction}")
                lines.append("")
            
            if prompt.instructions.code_style:
                lines.append("### Code Style Requirements")
                for guideline in prompt.instructions.code_style:
                    lines.append(f"- {guideline}")
                lines.append("")
            
            if prompt.instructions.testing:
                lines.append("### Testing Standards")
                for guideline in prompt.instructions.testing:
                    lines.append(f"- {guideline}")
                lines.append("")
            
            # Add architecture guidelines if present
            if hasattr(prompt.instructions, 'architecture') and prompt.instructions.architecture:
                lines.append("### Architecture Guidelines")
                for guideline in prompt.instructions.architecture:
                    lines.append(f"- {guideline}")
                lines.append("")
        
        # Examples are very useful for Claude
        if prompt.examples:
            lines.append("## Code Examples")
            lines.append("")
            lines.append("The following examples demonstrate the expected code patterns and style:")
            lines.append("")
            
            for name, example in prompt.examples.items():
                lines.append(f"### {name.replace('_', ' ').title()}")
                lines.append(example)
                lines.append("")
        
        # Claude-specific instructions
        lines.append("## AI Assistant Instructions")
        lines.append("")
        lines.append("When working on this project:")
        lines.append("- Follow the established patterns and conventions shown above")
        lines.append("- Maintain consistency with the existing codebase")
        lines.append("- Consider the project context and requirements in all suggestions")
        lines.append("- Prioritize code quality, maintainability, and best practices")
        if prompt.context and prompt.context.technologies:
            tech_list = ", ".join(prompt.context.technologies)
            lines.append(f"- Leverage {tech_list} best practices and idioms")
        
        return "\n".join(lines)