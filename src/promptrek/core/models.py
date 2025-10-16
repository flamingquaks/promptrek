"""
Data models for Universal Prompt Format (UPF).

These models represent the structure of a UPF file and provide
validation and serialization capabilities.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, ConfigDict, Field, field_validator


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
    frontmatter: Optional[Dict[str, Any]] = Field(
        default=None, description="Optional YAML frontmatter for the document"
    )
    content: str = Field(..., description="Raw markdown content")


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


class Command(BaseModel):
    """Slash command configuration for AI editors."""

    name: str = Field(..., description="Command name (e.g., 'review-code')")
    description: str = Field(..., description="Command description")
    prompt: str = Field(..., description="Prompt template for the command")
    output_format: Optional[str] = Field(
        default=None, description="Expected output format (e.g., 'markdown', 'json')"
    )
    requires_approval: bool = Field(
        default=False, description="Whether command execution requires approval"
    )
    system_message: Optional[str] = Field(
        default=None, description="Optional system message for the command"
    )
    examples: Optional[List[str]] = Field(
        default=None, description="Example usage of the command"
    )
    trust_metadata: Optional[TrustMetadata] = Field(
        default=None, description="Trust and security metadata"
    )


class Agent(BaseModel):
    """Autonomous agent configuration."""

    name: str = Field(..., description="Agent name/identifier")
    description: str = Field(..., description="Agent description and purpose")
    system_prompt: str = Field(..., description="System prompt for the agent")
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

    @field_validator("trust_level")
    @classmethod
    def validate_trust_level(cls, v: str) -> str:
        """Validate trust level is one of allowed values."""
        if v not in ["full", "partial", "untrusted"]:
            raise ValueError("Trust level must be 'full', 'partial', or 'untrusted'")
        return v


class Hook(BaseModel):
    """Event-driven automation hook configuration."""

    name: str = Field(..., description="Hook name/identifier")
    event: str = Field(
        ...,
        description="Event that triggers the hook (e.g., 'pre-commit', 'post-save')",
    )
    command: str = Field(..., description="Command to execute")
    conditions: Optional[Dict[str, Any]] = Field(
        default=None, description="Conditions for hook execution"
    )
    requires_reapproval: bool = Field(
        default=True, description="Whether hook requires reapproval after changes"
    )
    description: Optional[str] = Field(default=None, description="Hook description")
    trust_metadata: Optional[TrustMetadata] = Field(
        default=None, description="Trust and security metadata"
    )


class MarketplaceMetadata(BaseModel):
    """Metadata for plugin marketplace listings (v2.1 - deprecated in v3.0)."""

    plugin_id: Optional[str] = Field(
        default=None, description="Unique plugin identifier"
    )
    marketplace_url: Optional[str] = Field(
        default=None, description="URL to marketplace listing"
    )
    rating: Optional[float] = Field(default=None, description="User rating (0-5)")
    downloads: Optional[int] = Field(default=None, description="Number of downloads")
    last_updated: Optional[str] = Field(
        default=None, description="Last update date (ISO 8601)"
    )


# V3 Models - Plugin Marketplace/Discovery (v3.0.0+)


class PluginSourceGitHub(BaseModel):
    """GitHub repository source for plugins."""

    source: str = Field(default="github", description="Source type (must be 'github')")
    repo: str = Field(..., description="GitHub repository in format 'owner/repo'")
    ref: Optional[str] = Field(
        default=None, description="Git ref (branch, tag, or commit SHA)"
    )

    @field_validator("source")
    @classmethod
    def validate_source(cls, v: str) -> str:
        """Validate source is 'github'."""
        if v != "github":
            raise ValueError("GitHub source must have source='github'")
        return v


class PluginSourceURL(BaseModel):
    """Git URL source for plugins."""

    source: str = Field(default="url", description="Source type (must be 'url')")
    url: str = Field(..., description="Git repository URL")
    ref: Optional[str] = Field(
        default=None, description="Git ref (branch, tag, or commit SHA)"
    )

    @field_validator("source")
    @classmethod
    def validate_source(cls, v: str) -> str:
        """Validate source is 'url'."""
        if v != "url":
            raise ValueError("URL source must have source='url'")
        return v


class PluginAuthor(BaseModel):
    """Author information for plugins."""

    name: str = Field(..., description="Author name")
    email: Optional[str] = Field(default=None, description="Author email")
    url: Optional[str] = Field(default=None, description="Author website/profile URL")


class PluginEntry(BaseModel):
    """Plugin entry for marketplace configuration (v3.0+)."""

    name: str = Field(..., description="Plugin identifier (kebab-case)")
    source: Union[str, PluginSourceGitHub, PluginSourceURL] = Field(
        ..., description="Plugin source (relative path, GitHub repo, or Git URL)"
    )
    description: Optional[str] = Field(default=None, description="Plugin description")
    version: Optional[str] = Field(default=None, description="Plugin version")
    author: Optional[Union[str, PluginAuthor]] = Field(
        default=None, description="Plugin author"
    )
    homepage: Optional[str] = Field(
        default=None, description="Plugin homepage/documentation URL"
    )
    repository: Optional[str] = Field(
        default=None, description="Plugin source repository URL"
    )
    license: Optional[str] = Field(
        default=None, description="SPDX license identifier (e.g., MIT, Apache-2.0)"
    )
    keywords: Optional[List[str]] = Field(
        default=None, description="Keywords for plugin discovery"
    )
    tags: Optional[List[str]] = Field(
        default=None, description="Tags for categorization (alias for keywords)"
    )
    strict: bool = Field(default=True, description="Require plugin.json manifest file")
    commands: Optional[List[str]] = Field(
        default=None, description="Custom command file paths"
    )
    agents: Optional[List[str]] = Field(
        default=None, description="Custom agent file paths"
    )
    hooks: Optional[Dict[str, Any]] = Field(
        default=None, description="Hook configuration"
    )
    mcp_servers: Optional[Dict[str, Any]] = Field(
        default=None, description="MCP server configurations"
    )

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Validate plugin name is kebab-case."""
        if not v or not all(c.islower() or c.isdigit() or c == "-" for c in v):
            raise ValueError("Plugin name must be kebab-case (lowercase with hyphens)")
        return v


class MarketplaceOwner(BaseModel):
    """Owner/maintainer information for marketplace."""

    name: str = Field(..., description="Owner/maintainer name")
    email: Optional[str] = Field(default=None, description="Contact email")
    url: Optional[str] = Field(default=None, description="Website or profile URL")


class MarketplaceConfig(BaseModel):
    """Marketplace configuration for .claude-plugin/marketplace.json (v3.0+)."""

    name: str = Field(..., description="Marketplace identifier (kebab-case)")
    owner: MarketplaceOwner = Field(..., description="Marketplace owner information")
    plugins: List[PluginEntry] = Field(
        default_factory=list, description="Available plugins"
    )
    metadata: Optional[Dict[str, Any]] = Field(
        default=None, description="Additional marketplace metadata"
    )
    plugin_root: Optional[str] = Field(
        default=None, description="Base path for relative plugin sources"
    )

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Validate marketplace name is kebab-case."""
        if not v or not all(c.islower() or c.isdigit() or c == "-" for c in v):
            raise ValueError("Marketplace name must be kebab-case")
        return v


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
    marketplace_metadata: Optional[MarketplaceMetadata] = Field(
        default=None, description="Plugin marketplace metadata"
    )

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
    - plugins field repurposed for marketplace/plugin discovery (List[PluginEntry])
    - Full backward compatibility with v2.1 (parser auto-promotes nested fields)
    """

    schema_version: str = Field(..., description="UPF schema version (3.x.x)")
    metadata: PromptMetadata = Field(..., description="Prompt metadata")
    content: str = Field(..., description="Main markdown content")
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

    # Repurposed plugins field for marketplace/discovery
    plugins: Optional[List[PluginEntry]] = Field(
        default=None, description="Plugin marketplace entries (v3.0+)"
    )
    ignore_editor_files: Optional[bool] = Field(
        default=None,
        description="Automatically add editor-specific files to .gitignore (default: True)",
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
