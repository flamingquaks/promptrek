"""
Data models for Universal Prompt Format (UPF).

These models represent the structure of a UPF file and provide
validation and serialization capabilities.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class PromptMetadata(BaseModel):
    """Metadata about the prompt file."""

    title: str = Field(..., description="Human-readable title")
    description: str = Field(..., description="Brief description of purpose")
    version: Optional[str] = Field(
        default=None, description="Semantic version of this prompt"
    )
    author: Optional[str] = Field(default=None, description="Author name or email")
    created: Optional[str] = Field(
        default=None, description="ISO 8601 date (YYYY-MM-DD)"
    )
    updated: Optional[str] = Field(
        default=None, description="ISO 8601 date (YYYY-MM-DD)"
    )
    tags: Optional[List[str]] = Field(
        default=None, description="Optional tags for categorization"
    )

    @field_validator("created", "updated")
    @classmethod
    def validate_dates(cls, v: Optional[str]) -> Optional[str]:
        """Validate date format when provided."""
        if v is None:
            return v
        try:
            datetime.fromisoformat(v)
        except ValueError:
            raise ValueError("Date must be in YYYY-MM-DD format")
        return v


class ProjectContext(BaseModel):
    """Project context information."""

    project_type: Optional[str] = Field(
        default=None, description="e.g., 'web_application', 'api', 'library'"
    )
    technologies: Optional[List[str]] = Field(
        default=None, description="List of technologies used"
    )
    description: Optional[str] = Field(
        default=None, description="Detailed project description"
    )
    repository_url: Optional[str] = Field(
        default=None, description="Optional repository URL"
    )
    documentation_url: Optional[str] = Field(
        default=None, description="Optional documentation URL"
    )


class Instructions(BaseModel):
    """Instructions organized by category."""

    general: Optional[List[str]] = Field(
        default=None, description="General instructions"
    )
    code_style: Optional[List[str]] = Field(
        default=None, description="Code style guidelines"
    )
    architecture: Optional[List[str]] = Field(
        default=None, description="Architecture patterns"
    )
    testing: Optional[List[str]] = Field(default=None, description="Testing guidelines")
    security: Optional[List[str]] = Field(
        default=None, description="Security guidelines"
    )
    performance: Optional[List[str]] = Field(
        default=None, description="Performance guidelines"
    )

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
    then: Optional[Dict[str, Any]] = Field(
        default=None, description="Instructions if true"
    )
    else_clause: Optional[Dict[str, Any]] = Field(
        default=None, alias="else", description="Instructions if false"
    )


class ImportConfig(BaseModel):
    """Import configuration from other UPF files."""

    path: str = Field(..., description="Relative path to another .promptrek.yaml file")
    prefix: Optional[str] = Field(default=None, description="Optional namespace prefix")


# V2 Models - Simplified schema for v2.0.0+


class DocumentConfig(BaseModel):
    """A single document for multi-file editors (v2 schema)."""

    name: str = Field(..., description="Document name (used for filename)")
    content: str = Field(..., description="Raw markdown content")

    # Metadata fields (reusable across editors)
    description: Optional[str] = Field(
        default=None, description="Human-readable description (used by Cursor, etc.)"
    )
    file_globs: Optional[str] = Field(
        default=None,
        description="File patterns where this applies (e.g., '**/*.{ts,tsx}'). Used by Cursor, Copilot path-specific rules.",
    )
    always_apply: Optional[bool] = Field(
        default=None,
        description="Whether to always apply this rule (Cursor alwaysApply). If false with file_globs, auto-attaches to matching files.",
    )


# V2.1 Models - Plugin support (v2.1.0+)


class TrustMetadata(BaseModel):
    """Security and trust metadata for plugins."""

    trusted: bool = Field(
        default=False, description="Whether this plugin/config is trusted"
    )
    trust_level: Optional[str] = Field(
        default=None, description="Trust level: 'full', 'partial', 'untrusted'"
    )
    requires_approval: bool = Field(
        default=True, description="Whether actions require explicit approval"
    )
    source: Optional[str] = Field(
        default=None,
        description="Source of the plugin (e.g., 'official', 'community', 'local')",
    )
    verified_by: Optional[str] = Field(
        default=None, description="Who verified this plugin"
    )
    verified_date: Optional[str] = Field(
        default=None, description="When this plugin was verified (ISO 8601)"
    )

    @field_validator("trust_level")
    @classmethod
    def validate_trust_level(cls, v: Optional[str]) -> Optional[str]:
        """Validate trust level is one of allowed values."""
        if v is not None and v not in ["full", "partial", "untrusted"]:
            raise ValueError("Trust level must be 'full', 'partial', or 'untrusted'")
        return v


class MCPServer(BaseModel):
    """Model Context Protocol (MCP) server configuration."""

    name: str = Field(..., description="Server name/identifier")
    command: str = Field(..., description="Command to start the server")
    args: Optional[List[str]] = Field(
        default=None, description="Command line arguments"
    )
    env: Optional[Dict[str, str]] = Field(
        default=None, description="Environment variables"
    )
    description: Optional[str] = Field(
        default=None, description="Human-readable description"
    )
    trust_metadata: Optional[TrustMetadata] = Field(
        default=None, description="Trust and security metadata"
    )


class WorkflowStep(BaseModel):
    """Single step in a multi-step workflow."""

    name: str = Field(..., description="Step name/identifier")
    action: str = Field(
        ..., description="Action to perform (e.g., 'read_file', 'execute_command')"
    )
    description: Optional[str] = Field(
        default=None, description="Human-readable step description"
    )
    params: Optional[Dict[str, Any]] = Field(
        default=None, description="Parameters for the action"
    )
    conditions: Optional[Dict[str, Any]] = Field(
        default=None, description="Conditions for step execution"
    )


class Command(BaseModel):
    """
    Slash command or workflow configuration for AI editors.

    Supports both simple commands (single prompt) and complex workflows
    (multi-step procedures with tool calls). Use multi_step=True for workflows.
    """

    name: str = Field(..., description="Command name (e.g., 'review-code')")
    description: str = Field(..., description="Command description")
    prompt: str = Field(..., description="Prompt template for the command")
    output_format: Optional[str] = Field(
        default=None, description="Expected output format (e.g., 'markdown', 'json')"
    )
    requires_approval: bool = Field(
        default=False, description="Whether command execution requires approval"
    )
    examples: Optional[List[str]] = Field(
        default=None, description="Example usage of the command"
    )
    trust_metadata: Optional[TrustMetadata] = Field(
        default=None, description="Trust and security metadata"
    )

    # Workflow-specific fields (v3.1.0+)
    multi_step: bool = Field(
        default=False,
        description="Whether this is a multi-step workflow (vs simple command)",
    )
    steps: Optional[List["WorkflowStep"]] = Field(
        default=None, description="Structured workflow steps (optional)"
    )
    tool_calls: Optional[List[str]] = Field(
        default=None,
        description="Tools/commands this workflow uses (e.g., ['gh', 'read_file'])",
    )


class Agent(BaseModel):
    """Autonomous agent configuration."""

    name: str = Field(..., description="Agent name/identifier")
    prompt: str = Field(
        ...,
        description="Full markdown prompt/instructions for the agent",
        alias="system_prompt",  # Backward compatibility with v2.x
    )
    description: Optional[str] = Field(
        default=None,
        description="Optional high-level summary of agent purpose (for documentation)",
    )
    tools: Optional[List[str]] = Field(
        default=None, description="Available tools for the agent"
    )
    trust_level: str = Field(
        default="untrusted", description="Trust level for agent actions"
    )
    requires_approval: bool = Field(
        default=True, description="Whether agent actions require approval"
    )
    context: Optional[Dict[str, Any]] = Field(
        default=None, description="Additional context for the agent"
    )
    trust_metadata: Optional[TrustMetadata] = Field(
        default=None, description="Trust and security metadata"
    )

    model_config = ConfigDict(populate_by_name=True)

    @field_validator("trust_level")
    @classmethod
    def validate_trust_level(cls, v: str) -> str:
        """Validate trust level is one of allowed values."""
        if v not in ["full", "partial", "untrusted"]:
            raise ValueError("Trust level must be 'full', 'partial', or 'untrusted'")
        return v

    @model_validator(mode="before")
    @classmethod
    def handle_system_prompt_compatibility(cls, values: Any) -> Any:
        """Handle backward compatibility for system_prompt field (v3.0.0)."""
        if isinstance(values, dict):
            # If system_prompt is provided but prompt is not, use system_prompt for prompt
            if "system_prompt" in values and "prompt" not in values:
                values["prompt"] = values.pop("system_prompt")
            # If both are provided, prefer prompt and ignore system_prompt
            elif "system_prompt" in values and "prompt" in values:
                values.pop("system_prompt")
        return values


class Hook(BaseModel):
    """Event-driven automation hook configuration."""

    name: str = Field(..., description="Hook name/identifier")
    event: str = Field(
        ...,
        description="Event that triggers the hook (e.g., 'pre-commit', 'post-save', 'prompt-submit', 'agent-spawn')",
    )
    command: str = Field(..., description="Command to execute")
    conditions: Optional[Dict[str, Any]] = Field(
        default=None, description="Conditions for hook execution"
    )
    requires_reapproval: bool = Field(
        default=True, description="Whether hook requires reapproval after changes"
    )
    description: Optional[str] = Field(default=None, description="Hook description")
    agent: Optional[str] = Field(
        default=None,
        description="Agent name to associate hook with (for editors that support agent-scoped hooks like Amazon Q). If not specified, hook applies to all agents or is project-level.",
    )
    trust_metadata: Optional[TrustMetadata] = Field(
        default=None, description="Trust and security metadata"
    )


class PluginConfig(BaseModel):
    """Container for all plugin configurations (v2.1.0+)."""

    mcp_servers: Optional[List[MCPServer]] = Field(
        default=None, description="MCP server configurations"
    )
    commands: Optional[List[Command]] = Field(
        default=None, description="Slash command configurations"
    )
    agents: Optional[List[Agent]] = Field(
        default=None, description="Agent configurations"
    )
    hooks: Optional[List[Hook]] = Field(default=None, description="Hook configurations")

    model_config = ConfigDict(extra="forbid")


class UniversalPromptV2(BaseModel):
    """
    Simplified UPF v2 schema - markdown-first approach.

    DEPRECATED: Use UniversalPromptV3 for new projects.
    v2.1 nested plugin structure (plugins.mcp_servers, etc.) is deprecated.
    v3.0+ uses top-level mcp_servers, commands, agents, hooks fields.
    """

    schema_version: str = Field(..., description="UPF schema version (2.x.x)")
    metadata: PromptMetadata = Field(..., description="Prompt metadata")
    content: str = Field(..., description="Main markdown content")
    content_description: Optional[str] = Field(
        default=None,
        description="Description for main content (used in editor frontmatter)",
    )
    content_always_apply: Optional[bool] = Field(
        default=None, description="Whether main content always applies (default: True)"
    )
    documents: Optional[List[DocumentConfig]] = Field(
        default=None, description="Additional documents for multi-file editors"
    )
    variables: Optional[Dict[str, str]] = Field(
        default=None, description="Template variables"
    )
    plugins: Optional[PluginConfig] = Field(
        default=None, description="Plugin configurations (v2.1.0+ - deprecated in v3.0)"
    )
    ignore_editor_files: Optional[bool] = Field(
        default=None,
        description="Automatically add editor-specific files to .gitignore (default: True)",
    )

    @field_validator("schema_version")
    @classmethod
    def validate_schema_version(cls, v: str) -> str:
        """Validate schema version format and ensure it's 2.x.x."""
        if not v.count(".") == 2:
            raise ValueError("Schema version must be in format 'x.y.z'")
        major = v.split(".")[0]
        if major != "2":
            raise ValueError("UniversalPromptV2 requires schema version 2.x.x")
        return v

    @field_validator("content")
    @classmethod
    def validate_content(cls, v: str) -> str:
        """Ensure content is not empty."""
        if not v or not v.strip():
            raise ValueError("Content cannot be empty")
        return v

    model_config = ConfigDict(validate_assignment=True, extra="forbid")


class UniversalPromptV3(BaseModel):
    """
    UPF v3 schema - markdown-first with top-level plugin fields.

    Major changes from v2:
    - mcp_servers, commands, agents, hooks are now top-level fields
    - Full backward compatibility with v2.1 (parser auto-promotes nested fields)
    """

    schema_version: str = Field(..., description="UPF schema version (3.x.x)")
    metadata: PromptMetadata = Field(..., description="Prompt metadata")
    content: str = Field(..., description="Main markdown content")
    content_description: Optional[str] = Field(
        default=None,
        description="Description for main content (used in editor frontmatter)",
    )
    content_always_apply: Optional[bool] = Field(
        default=None, description="Whether main content always applies (default: True)"
    )
    documents: Optional[List[DocumentConfig]] = Field(
        default=None, description="Additional documents for multi-file editors"
    )
    variables: Optional[Dict[str, str]] = Field(
        default=None, description="Template variables"
    )

    # Top-level plugin fields (promoted from v2.1 plugins.* structure)
    mcp_servers: Optional[List[MCPServer]] = Field(
        default=None, description="MCP server configurations (top-level in v3.0+)"
    )
    commands: Optional[List[Command]] = Field(
        default=None, description="Slash command configurations (top-level in v3.0+)"
    )
    agents: Optional[List[Agent]] = Field(
        default=None, description="Agent configurations (top-level in v3.0+)"
    )
    hooks: Optional[List[Hook]] = Field(
        default=None, description="Hook configurations (top-level in v3.0+)"
    )

    ignore_editor_files: Optional[bool] = Field(
        default=None,
        description="Automatically add editor-specific files to .gitignore (default: True)",
    )

    allow_commands: Optional[bool] = Field(
        default=False,
        description="Allow dynamic variables to execute shell commands (security control)",
    )

    @field_validator("schema_version")
    @classmethod
    def validate_schema_version(cls, v: str) -> str:
        """Validate schema version format and ensure it's 3.x.x."""
        if not v.count(".") == 2:
            raise ValueError("Schema version must be in format 'x.y.z'")
        major = v.split(".")[0]
        if major != "3":
            raise ValueError("UniversalPromptV3 requires schema version 3.x.x")
        return v

    @field_validator("content")
    @classmethod
    def validate_content(cls, v: str) -> str:
        """Ensure content is not empty."""
        if not v or not v.strip():
            raise ValueError("Content cannot be empty")
        return v

    model_config = ConfigDict(validate_assignment=True, extra="forbid")


# V1 Models - Legacy schema for v1.x.x (backwards compatibility)


class UniversalPrompt(BaseModel):
    """Main UPF model representing a complete prompt configuration (v1 schema)."""

    schema_version: str = Field(..., description="UPF schema version")
    metadata: PromptMetadata = Field(..., description="Prompt metadata")
    targets: Optional[List[str]] = Field(
        default=None, description="Target editors this prompt supports"
    )
    context: Optional[ProjectContext] = Field(
        default=None, description="Project context information"
    )
    instructions: Optional[Instructions] = Field(
        default=None, description="Categorized instructions"
    )
    examples: Optional[Dict[str, str]] = Field(
        default=None, description="Code examples by category"
    )
    variables: Optional[Dict[str, str]] = Field(
        default=None, description="Template variables"
    )
    editor_specific: Optional[Dict[str, EditorSpecificConfig]] = Field(
        default=None, description="Editor-specific configurations"
    )
    conditions: Optional[List[Condition]] = Field(
        default=None, description="Conditional instructions"
    )
    imports: Optional[List[ImportConfig]] = Field(
        default=None, description="Import other prompt files"
    )
    ignore_editor_files: Optional[bool] = Field(
        default=None,
        description="Automatically add editor-specific files to .gitignore (default: True)",
    )

    @field_validator("schema_version")
    @classmethod
    def validate_schema_version(cls, v: str) -> str:
        """Validate schema version format."""
        if not v.count(".") == 2:
            raise ValueError("Schema version must be in format 'x.y.z'")
        return v

    @field_validator("targets")
    @classmethod
    def validate_targets(cls, v: Optional[List[str]]) -> Optional[List[str]]:
        """Validate target editors."""
        if v is not None and not v:
            raise ValueError(
                "If targets are specified, at least one target editor must be provided"
            )
        return v

    model_config = ConfigDict(
        validate_assignment=True, extra="forbid"  # Strict validation for the main model
    )


# User-specific configuration (not committed to repository)


class UserConfig(BaseModel):
    """
    User-specific configuration stored in user-config.promptrek.yaml.

    This file contains user-specific settings that should NOT be committed
    to version control. It is automatically added to .gitignore.
    """

    schema_version: str = Field(
        default="1.0.0", description="User config schema version"
    )
    editor_paths: Optional[Dict[str, str]] = Field(
        default=None,
        description="Editor-specific file paths (e.g., cline_mcp_path)",
    )

    @field_validator("schema_version")
    @classmethod
    def validate_schema_version(cls, v: str) -> str:
        """Validate schema version format."""
        if not v.count(".") == 2:
            raise ValueError("Schema version must be in format 'x.y.z'")
        return v

    model_config = ConfigDict(validate_assignment=True, extra="allow")


# Dynamic Variables Configuration


class DynamicVariableConfig(BaseModel):
    """
    Configuration for a dynamic variable that evaluates at generation time.

    Used in .promptrek/variables.promptrek.yaml for command-based variables.
    """

    type: str = Field(..., description="Variable type (must be 'command')")
    value: str = Field(..., description="Shell command to execute")
    cache: bool = Field(
        default=False,
        description="Whether to cache the result (evaluate once per session)",
    )

    @field_validator("type")
    @classmethod
    def validate_type(cls, v: str) -> str:
        """Validate variable type."""
        if v != "command":
            raise ValueError("Only 'command' type is currently supported")
        return v

    model_config = ConfigDict(validate_assignment=True, extra="forbid")


# Generation Metadata (for refresh command)


class GenerationMetadata(BaseModel):
    """
    Metadata about a generation run, saved to .promptrek/last-generation.yaml.

    Used by the 'promptrek refresh' command to regenerate files with updated variables.
    """

    timestamp: str = Field(..., description="ISO 8601 timestamp of generation")
    source_file: str = Field(..., description="Source UPF file path")
    editors: List[str] = Field(..., description="Editors that were generated for")
    output_dir: str = Field(..., description="Output directory path")
    variables: Dict[str, str] = Field(
        default_factory=dict, description="Static variables used"
    )
    dynamic_variables: Dict[str, DynamicVariableConfig] = Field(
        default_factory=dict, description="Dynamic variable configurations"
    )
    builtin_variables_enabled: bool = Field(
        default=True, description="Whether built-in variables were enabled"
    )
    allow_commands: bool = Field(
        default=False, description="Whether command execution was allowed"
    )

    @field_validator("timestamp")
    @classmethod
    def validate_timestamp(cls, v: str) -> str:
        """Validate timestamp format."""
        try:
            datetime.fromisoformat(v)
        except ValueError:
            raise ValueError(
                f"Timestamp must be in ISO 8601 format (e.g., '2025-10-26T14:30:45'), got: {v}"
            )
        return v

    model_config = ConfigDict(validate_assignment=True, extra="allow")


# Universal Spec Format (USF) - Spec-driven project documents


class SpecMetadata(BaseModel):
    """
    Metadata for a single spec file in the Universal Spec Format.

    Stored in promptrek/specs.yaml as part of the spec registry.
    """

    id: str = Field(..., description="Unique identifier for the spec")
    title: str = Field(..., description="Human-readable title")
    path: str = Field(..., description="Relative path to spec file in promptrek/specs/")
    source_command: str = Field(
        ...,
        description="Command that created this spec (e.g., '/promptrek.spec.create')",
    )
    created: str = Field(..., description="ISO 8601 timestamp of creation")
    updated: Optional[str] = Field(
        default=None, description="ISO 8601 timestamp of last update"
    )
    summary: Optional[str] = Field(
        default=None, description="Brief summary of spec content"
    )
    linked_specs: Optional[List[str]] = Field(
        default=None, description="IDs of related/linked specs"
    )
    tags: Optional[List[str]] = Field(
        default=None, description="Tags for categorization"
    )

    @field_validator("created", "updated")
    @classmethod
    def validate_timestamps(cls, v: Optional[str]) -> Optional[str]:
        """Validate timestamp format."""
        if v is None:
            return v
        try:
            datetime.fromisoformat(v)
        except ValueError:
            raise ValueError(f"Timestamp must be in ISO 8601 format, got: {v}")
        return v

    model_config = ConfigDict(validate_assignment=True, extra="forbid")


class UniversalSpecFormat(BaseModel):
    """
    Universal Spec Format (USF) - Registry of spec-driven project documents.

    Stored in promptrek/specs.yaml as the canonical source of spec metadata.
    Actual spec content files are stored in promptrek/specs/ directory (COMMITTED).
    """

    schema_version: str = Field(default="1.0.0", description="USF schema version")
    specs: List[SpecMetadata] = Field(
        default_factory=list, description="List of registered specs"
    )

    @field_validator("schema_version")
    @classmethod
    def validate_schema_version(cls, v: str) -> str:
        """Validate schema version format."""
        if not v.count(".") == 2:
            raise ValueError("Schema version must be in format 'x.y.z'")
        return v

    model_config = ConfigDict(validate_assignment=True, extra="forbid")
