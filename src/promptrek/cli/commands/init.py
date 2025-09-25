"""
Init command implementation.

Handles initialization of new universal prompt files.
"""

from pathlib import Path
from typing import Optional

import click
import yaml

from ...core.exceptions import CLIError


def init_command(ctx: click.Context, template: Optional[str], output: str) -> None:
    """
    Initialize a new universal prompt file.

    Args:
        ctx: Click context
        template: Optional template name to use
        output: Output file path
    """
    output_path = Path(output)

    # Check if file already exists
    if output_path.exists():
        if not click.confirm(f"File {output_path} already exists. Overwrite?"):
            raise CLIError("Initialization cancelled")

    # Ensure output path has correct extension
    if not output_path.name.endswith((".promptrek.yaml")):
        output_path = output_path.with_suffix(".promptrek.yaml")

    # Create basic template
    if template:
        upf_data = _get_template(template)
    else:
        upf_data = _get_basic_template()

    # Create output directory if needed
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Write the file
    try:
        with open(output_path, "w", encoding="utf-8") as f:
            yaml.dump(
                upf_data,
                f,
                default_flow_style=False,
                allow_unicode=True,
                sort_keys=False,
            )
    except Exception as e:
        raise CLIError(f"Failed to write file {output_path}: {e}")

    click.echo(f"✅ Initialized universal prompt file: {output_path}")
    click.echo("📝 Edit the file to customize your prompt configuration")
    click.echo(f"🔍 Run 'promptrek validate {output_path}' to check your configuration")


def _get_basic_template() -> dict:
    """Get the basic template structure."""
    return {
        "schema_version": "1.0.0",
        "metadata": {
            "title": "My Project Assistant",
            "description": "AI assistant configuration for my project",
            "version": "1.0.0",
            "author": "Your Name <your.email@example.com>",
            "created": "2024-01-01",
            "updated": "2024-01-01",
            "tags": ["project", "ai-assistant"],
        },
        "targets": ["copilot", "cursor", "continue"],
        "context": {
            "project_type": "web_application",
            "technologies": ["python", "javascript", "react"],
            "description": "A sample project using modern web technologies",
        },
        "instructions": {
            "general": [
                "Write clean, readable, and maintainable code",
                "Follow existing code patterns and conventions",
                "Add appropriate comments for complex logic",
            ],
            "code_style": [
                "Use meaningful and descriptive variable names",
                "Follow the existing linting and formatting rules",
                "Prefer explicit over implicit code",
            ],
            "testing": [
                "Write unit tests for new functions",
                "Ensure tests are clear and well-documented",
                "Aim for good test coverage",
            ],
        },
        "examples": {
            "function": '''```python
def calculate_total(items: list[float]) -> float:
    """Calculate the total sum of items.

    Args:
        items: List of numeric values to sum

    Returns:
        Total sum of all items
    """
    return sum(items)
```'''
        },
        "variables": {
            "PROJECT_NAME": "My Project",
            "AUTHOR_EMAIL": "your.email@example.com",
        },
    }


def _get_template(template_name: str) -> dict:
    """
    Get a specific template by name.

    Args:
        template_name: Name of the template to use

    Returns:
        Template data dictionary

    Raises:
        CLIError: If template is not found
    """
    templates = {
        "basic": _get_basic_template(),
        "react": _get_react_template(),
        "api": _get_api_template(),
    }

    if template_name not in templates:
        available = ", ".join(templates.keys())
        raise CLIError(
            f"Unknown template '{template_name}'. Available templates: {available}"
        )

    return templates[template_name]


def _get_react_template() -> dict:
    """Get React/TypeScript project template."""
    template = _get_basic_template()
    template["metadata"]["title"] = "React TypeScript Project Assistant"
    template["metadata"][
        "description"
    ] = "AI assistant for React TypeScript development"
    template["context"]["project_type"] = "web_application"
    template["context"]["technologies"] = ["typescript", "react", "vite", "tailwindcss"]
    template["instructions"]["general"].extend(
        [
            "Use TypeScript for all new files",
            "Follow React functional component patterns",
            "Implement proper error boundaries",
        ]
    )
    template["instructions"]["code_style"].extend(
        [
            "Use functional components with hooks",
            "Prefer arrow functions for components",
            "Use TypeScript interfaces for props",
        ]
    )
    template["examples"][
        "component"
    ] = """```typescript
interface ButtonProps {
  title: string;
  onClick: () => void;
  variant?: 'primary' | 'secondary';
}

export const Button: React.FC<ButtonProps> = ({
  title,
  onClick,
  variant = 'primary'
}) => {
  return (
    <button
      className={`btn btn-${variant}`}
      onClick={onClick}
    >
      {title}
    </button>
  );
};
```"""
    return template


def _get_api_template() -> dict:
    """Get API project template."""
    template = _get_basic_template()
    template["metadata"]["title"] = "API Service Assistant"
    template["metadata"]["description"] = "AI assistant for API development"
    template["context"]["project_type"] = "api_service"
    template["context"]["technologies"] = [
        "python",
        "fastapi",
        "postgresql",
        "sqlalchemy",
    ]
    template["instructions"]["general"].extend(
        [
            "Follow RESTful API design principles",
            "Implement proper error handling",
            "Use async/await for database operations",
        ]
    )
    template["instructions"]["security"] = [
        "Validate all user inputs",
        "Use parameterized queries",
        "Implement proper authentication",
        "Never log sensitive information",
    ]
    template["examples"][
        "endpoint"
    ] = """```python
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

class UserCreate(BaseModel):
    name: str
    email: str

@router.post("/users")
async def create_user(user: UserCreate):
    try:
        # Create user logic here
        return {"id": 1, "name": user.name, "email": user.email}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```"""
    return template
