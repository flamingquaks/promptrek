"""
Data models for Universal Prompt Format (UPF).

These models represent the structure of a UPF file and provide
validation and serialization capabilities.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, field_validator, ConfigDict


class PromptMetadata(BaseModel):
    """Metadata about the prompt file."""
    
    title: str = Field(..., description="Human-readable title")
    description: str = Field(..., description="Brief description of purpose")
    version: str = Field(..., description="Semantic version of this prompt")
    author: str = Field(..., description="Author name or email")
    created: str = Field(..., description="ISO 8601 date (YYYY-MM-DD)")
    updated: str = Field(..., description="ISO 8601 date (YYYY-MM-DD)")
    tags: Optional[List[str]] = Field(default=None, description="Optional tags for categorization")

    @field_validator("created", "updated")
    @classmethod
    def validate_dates(cls, v: str) -> str:
        """Validate date format."""
        try:
            datetime.fromisoformat(v)
        except ValueError:
            raise ValueError("Date must be in YYYY-MM-DD format")
        return v


class ProjectContext(BaseModel):
    """Project context information."""
    
    project_type: Optional[str] = Field(default=None, description="e.g., 'web_application', 'api', 'library'")
    technologies: Optional[List[str]] = Field(default=None, description="List of technologies used")
    description: Optional[str] = Field(default=None, description="Detailed project description")
    repository_url: Optional[str] = Field(default=None, description="Optional repository URL")
    documentation_url: Optional[str] = Field(default=None, description="Optional documentation URL")


class Instructions(BaseModel):
    """Instructions organized by category."""
    
    general: Optional[List[str]] = Field(default=None, description="General instructions")
    code_style: Optional[List[str]] = Field(default=None, description="Code style guidelines")
    architecture: Optional[List[str]] = Field(default=None, description="Architecture patterns")
    testing: Optional[List[str]] = Field(default=None, description="Testing guidelines")
    security: Optional[List[str]] = Field(default=None, description="Security guidelines")
    performance: Optional[List[str]] = Field(default=None, description="Performance guidelines")
    
    # Allow additional custom categories
    model_config = ConfigDict(extra="allow")


class CustomCommand(BaseModel):
    """Custom command for specific editors."""
    
    name: str = Field(..., description="Command name")
    prompt: str = Field(..., description="Command prompt template")
    description: str = Field(..., description="Command description")


class EditorSpecificConfig(BaseModel):
    """Editor-specific configuration."""
    
    additional_instructions: Optional[List[str]] = Field(default=None)
    custom_commands: Optional[List[CustomCommand]] = Field(default=None)
    templates: Optional[Dict[str, str]] = Field(default=None)
    
    # Allow additional editor-specific fields
    model_config = ConfigDict(extra="allow")


class Condition(BaseModel):
    """Conditional instruction."""
    
    if_condition: str = Field(..., alias="if", description="Condition expression")
    then: Optional[Dict[str, Any]] = Field(default=None, description="Instructions if true")
    else_clause: Optional[Dict[str, Any]] = Field(default=None, alias="else", description="Instructions if false")


class ImportConfig(BaseModel):
    """Import configuration from other UPF files."""
    
    path: str = Field(..., description="Relative path to another .apm.yaml file")
    prefix: Optional[str] = Field(default=None, description="Optional namespace prefix")


class UniversalPrompt(BaseModel):
    """Main UPF model representing a complete prompt configuration."""
    
    schema_version: str = Field(..., description="UPF schema version")
    metadata: PromptMetadata = Field(..., description="Prompt metadata")
    targets: List[str] = Field(..., description="Target editors this prompt supports")
    context: Optional[ProjectContext] = Field(default=None, description="Project context information")
    instructions: Optional[Instructions] = Field(default=None, description="Categorized instructions")
    examples: Optional[Dict[str, str]] = Field(default=None, description="Code examples by category")
    variables: Optional[Dict[str, str]] = Field(default=None, description="Template variables")
    editor_specific: Optional[Dict[str, EditorSpecificConfig]] = Field(default=None, description="Editor-specific configurations")
    conditions: Optional[List[Condition]] = Field(default=None, description="Conditional instructions")
    imports: Optional[List[ImportConfig]] = Field(default=None, description="Import other prompt files")

    @field_validator("schema_version")
    @classmethod
    def validate_schema_version(cls, v: str) -> str:
        """Validate schema version format."""
        if not v.count(".") == 2:
            raise ValueError("Schema version must be in format 'x.y.z'")
        return v

    @field_validator("targets")
    @classmethod
    def validate_targets(cls, v: List[str]) -> List[str]:
        """Validate target editors."""
        if not v:
            raise ValueError("At least one target editor must be specified")
        return v

    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid"  # Strict validation for the main model
    )