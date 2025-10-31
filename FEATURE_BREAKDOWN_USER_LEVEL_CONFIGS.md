# Feature Breakdown: User-Level Configuration Support for PrompTrek

## Executive Summary

This document provides a detailed breakdown of work required to implement comprehensive user-level configuration support in PrompTrek, particularly for the sync command. Currently, PrompTrek's sync command only works with project-level configurations, causing many user-level configurations to be skipped. This feature will enable PrompTrek to work with user-level configurations, optionally bring them into project files with proper confirmation workflows, and scale this functionality across all supported editors.

## Problem Statement

### Current State

PrompTrek has two types of configurations:

1. **Project-Level Configurations** (✅ Currently Synced)
   - Located in project directories (e.g., `.cursor/rules/`, `.continue/rules/`)
   - Intended to be committed to version control
   - Shared across team members
   - **Currently supported by sync command**

2. **User-Level/System-Wide Configurations** (❌ NOT Currently Synced)
   - Located in user home directories or VSCode global storage
   - Machine-specific or user-specific settings
   - NOT intended for version control
   - **Currently NOT supported by sync command**

### Specific Issues

#### 1. **Sync Command Limitations**
   - The sync command (`promptrek sync`) only reads from project-level directories
   - User-level editor configurations are completely ignored
   - No way to capture MCP servers, commands, or other plugins defined at user-level
   - Team-reusable configurations in user-level files are lost

#### 2. **Examples of Missed Configurations**

   **Cline (VSCode Extension)**:
   - Project-level: `.clinerules/*.md` (✅ synced)
   - User-level: `~/.config/Code/User/globalStorage/saoudrizwan.claude-dev/settings/cline_mcp_settings.json` (❌ NOT synced)

   **Windsurf**:
   - Project-level: `.windsurf/rules/*.md` (✅ synced)
   - User-level: `~/.codeium/windsurf/mcp_config.json` (❌ NOT synced)

   **Continue**:
   - Project-level: `.continue/rules/*.md` (✅ synced)
   - User-level: `~/.continue/config.json` with MCP servers (❌ NOT synced)

   **Amazon Q**:
   - User-level only: Global configuration (❌ NOT synced)

#### 3. **No User Confirmation Workflow**
   - No way to review user-level configs before bringing them into project
   - Risk of accidentally sharing machine-specific paths
   - No distinction between truly user-specific vs team-reusable configs

#### 4. **Lack of Metadata Tracking**
   - No way to mark a configuration as "user-level" vs "project-level"
   - No tracking of which configurations originated from user-level sources
   - No warnings when user-level configs might contain sensitive data

## Solution Requirements

### Core Functionality

1. **User-Level Configuration Discovery**
   - Detect and read user-level configuration files for all editors
   - Support multiple search paths per editor (VSCode, VSCode Insiders, Cursor, etc.)
   - Handle missing or inaccessible user-level configs gracefully

2. **Sync Enhancement**
   - Extend sync command to read both project-level AND user-level configurations
   - Add `--include-user-level` flag to opt into user-level sync
   - Add `--user-level-only` flag to sync only user-level configs
   - Preserve existing project-level sync behavior by default

3. **Configuration Classification**
   - Add metadata to track configuration origin (user-level vs project-level)
   - Add `config_source` field to UniversalPrompt schemas
   - Support filtering and querying by configuration source

4. **User Confirmation Workflow**
   - Interactive prompts when user-level configs are detected
   - Show preview of what will be synced from user-level
   - Allow selective sync (choose which user-level items to include)
   - Warn about potentially sensitive data (paths, environment variables)

5. **Editor Mapping System**
   - Define which configurations are reusable vs user-specific
   - Create a mapping for each editor showing:
     - What can safely be shared (e.g., MCP server definitions)
     - What should stay user-specific (e.g., file paths, API keys)
   - Implement automatic sanitization of user-specific data

6. **Schema Extensions**
   - Add `user_level` boolean field to plugin items (MCP servers, commands, agents, hooks)
   - Add `sanitized_from` field to track when user-level configs were sanitized
   - Add `user_config_source` metadata to track origin paths

## Detailed Work Breakdown

### Phase 1: Foundation & Data Model Updates

#### Task 1.1: Schema Extensions for User-Level Tracking
**Files to modify:**
- `src/promptrek/core/models.py`

**Changes:**
1. Add `ConfigSource` enum:
   ```python
   class ConfigSource(str, Enum):
       PROJECT = "project"
       USER_LEVEL = "user-level"
       SYSTEM_WIDE = "system-wide"
       MIXED = "mixed"
   ```

2. Extend plugin models (MCPServer, Command, Agent, Hook):
   ```python
   class MCPServer(BaseModel):
       # ... existing fields ...
       user_level: Optional[bool] = Field(False, description="Whether this was sourced from user-level config")
       config_source: Optional[ConfigSource] = Field(ConfigSource.PROJECT, description="Origin of this configuration")
       sanitized: Optional[bool] = Field(False, description="Whether paths/secrets were sanitized")
       original_source_path: Optional[str] = Field(None, description="Original file path if from user-level")
   ```

3. Add metadata to UniversalPromptV3:
   ```python
   class UniversalPromptV3(BaseModel):
       # ... existing fields ...
       config_sources: Optional[List[ConfigSource]] = Field(None, description="Sources of configurations in this file")
       user_level_items_count: Optional[int] = Field(None, description="Count of user-level items")
   ```

**Estimated Effort:** 4-6 hours

#### Task 1.2: User Configuration Model Enhancement
**Files to modify:**
- `src/promptrek/core/models.py`

**Changes:**
1. Extend `UserConfig` model:
   ```python
   class UserConfig(BaseModel):
       schema_version: str = "1.0.0"
       editor_paths: Optional[Dict[str, str]] = None

       # NEW: Track which user-level configs to sync
       sync_preferences: Optional[Dict[str, Any]] = Field(
           None,
           description="User preferences for syncing user-level configs"
       )

       # NEW: Track last sync metadata
       last_user_level_sync: Optional[Dict[str, Any]] = Field(
           None,
           description="Metadata about last user-level sync operation"
       )
   ```

**Estimated Effort:** 2-3 hours

---

### Phase 2: Adapter-Level User Config Support

#### Task 2.1: Create User-Level Config Mixin
**New file:** `src/promptrek/adapters/user_level_mixin.py`

**Purpose:** Provide shared functionality for discovering and parsing user-level configurations

**Key methods:**
```python
class UserLevelConfigMixin:
    """Mixin for adapters to support user-level configuration discovery and parsing."""

    def get_user_level_config_paths(self) -> List[Path]:
        """Return list of possible user-level config paths for this editor."""
        raise NotImplementedError

    def find_user_level_config(self) -> Optional[Path]:
        """Search for and find user-level config file."""
        pass

    def parse_user_level_config(self, config_path: Path) -> Dict[str, Any]:
        """Parse user-level configuration file."""
        raise NotImplementedError

    def sanitize_user_level_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Remove or sanitize user-specific data from config."""
        pass

    def merge_user_and_project_configs(
        self,
        project_config: UniversalPromptV3,
        user_config: Dict[str, Any],
        include_user_level: bool = False
    ) -> UniversalPromptV3:
        """Merge user-level and project-level configs intelligently."""
        pass
```

**Estimated Effort:** 8-10 hours

#### Task 2.2: Update All Adapters with User-Level Support

For each adapter, implement:

1. **Inherit from UserLevelConfigMixin**
2. **Define user-level config paths**
3. **Implement user-level parsing**
4. **Define what's reusable vs user-specific**

**Adapters to update:**

**2.2.1: Continue Adapter**
- User-level path: `~/.continue/config.json`
- Reusable: MCP servers, slash commands (prompts)
- User-specific: File paths in env vars, API keys

**Estimated Effort:** 4-5 hours

**2.2.2: Cline Adapter** (Already has some support)
- User-level path: VSCode globalStorage `cline_mcp_settings.json`
- Reusable: MCP server definitions
- User-specific: All file paths

**Estimated Effort:** 3-4 hours

**2.2.3: Windsurf Adapter**
- User-level path: `~/.codeium/windsurf/mcp_config.json`
- Reusable: MCP server definitions
- User-specific: File paths in commands/env vars

**Estimated Effort:** 3-4 hours

**2.2.4: Amazon Q Adapter**
- User-level path: `~/.aws/amazonq/` (config files)
- Reusable: CLI agents, rules
- User-specific: AWS credentials, region settings

**Estimated Effort:** 4-5 hours

**2.2.5: Claude Code Adapter**
- User-level path: `~/.claude/` (if exists)
- Reusable: Commands, agents
- User-specific: File paths

**Estimated Effort:** 3-4 hours

**2.2.6: Cursor Adapter**
- User-level path: `~/.cursor/` (if exists)
- Reusable: Rules, MCP servers
- User-specific: File paths

**Estimated Effort:** 3-4 hours

**2.2.7: Other Adapters** (Copilot, JetBrains, Kiro)
- Limited user-level config support
- Document which have user-level configs

**Estimated Effort:** 2-3 hours each = 6-9 hours total

---

### Phase 3: Sync Command Enhancement

#### Task 3.1: Add User-Level Flags to Sync Command
**File to modify:** `src/promptrek/cli/commands/sync.py`

**Changes:**
1. Add new CLI flags:
   ```python
   @click.option(
       "--include-user-level",
       is_flag=True,
       help="Include user-level configurations in sync (requires confirmation)"
   )
   @click.option(
       "--user-level-only",
       is_flag=True,
       help="Sync only user-level configurations"
   )
   @click.option(
       "--auto-sanitize",
       is_flag=True,
       default=True,
       help="Automatically sanitize sensitive data from user-level configs"
   )
   @click.option(
       "--no-confirm",
       is_flag=True,
       help="Skip confirmation prompts (use with caution)"
   )
   ```

**Estimated Effort:** 2-3 hours

#### Task 3.2: Implement User-Level Sync Logic
**File to modify:** `src/promptrek/cli/commands/sync.py`

**New functions needed:**
1. `discover_user_level_configs()` - Find user-level configs
2. `preview_user_level_configs()` - Show user what will be synced
3. `confirm_user_level_sync()` - Interactive confirmation
4. `sanitize_user_level_data()` - Remove sensitive data
5. `merge_with_user_level()` - Merge user and project configs

**Workflow:**
```python
def sync_command_enhanced(
    source_dir: Path,
    editor: str,
    include_user_level: bool,
    user_level_only: bool,
    auto_sanitize: bool,
    no_confirm: bool,
    ...
):
    adapter = registry.get(editor)

    # Parse project-level (existing functionality)
    if not user_level_only:
        project_prompt = adapter.parse_files(source_dir)
    else:
        project_prompt = None

    # Parse user-level (NEW)
    user_level_prompt = None
    if include_user_level or user_level_only:
        user_level_config_path = adapter.find_user_level_config()

        if user_level_config_path:
            click.echo(f"🔍 Found user-level config: {user_level_config_path}")

            # Parse user-level config
            user_level_data = adapter.parse_user_level_config(user_level_config_path)

            # Preview what will be synced
            preview_user_level_configs(user_level_data, adapter.name)

            # Confirm with user (unless no-confirm)
            if not no_confirm:
                if not confirm_user_level_sync(user_level_data, editor):
                    click.echo("⏭️  Skipping user-level configs")
                    include_user_level = False

            # Sanitize if enabled
            if auto_sanitize and include_user_level:
                user_level_data = adapter.sanitize_user_level_config(user_level_data)
                click.echo("🧹 Sanitized user-level configurations")

            # Convert to UniversalPrompt format
            user_level_prompt = adapter.convert_user_level_to_prompt(user_level_data)

    # Merge configurations
    if project_prompt and user_level_prompt:
        merged_prompt = adapter.merge_user_and_project_configs(
            project_prompt,
            user_level_prompt
        )
    elif user_level_prompt:
        merged_prompt = user_level_prompt
    else:
        merged_prompt = project_prompt

    # Continue with existing merge and write logic...
```

**Estimated Effort:** 12-16 hours

#### Task 3.3: Add User-Level Sync to Interactive Mode
**File to modify:** `src/promptrek/cli/interactive.py`

**Changes:**
1. Add "Sync with user-level configs" workflow
2. Add guided prompts for user-level sync options
3. Show preview and confirmation in interactive UI

**Estimated Effort:** 4-6 hours

---

### Phase 4: Configuration Mapping & Sanitization

#### Task 4.1: Create Editor Configuration Mapping Registry
**New file:** `src/promptrek/core/editor_config_mapping.py`

**Purpose:** Define what's reusable vs user-specific for each editor

**Structure:**
```python
@dataclass
class ConfigItemMapping:
    """Mapping for a configuration item."""

    item_type: str  # "mcp_server", "command", "agent", "hook"
    field_name: str  # "name", "command", "env"
    reusability: str  # "reusable", "user-specific", "conditional"
    sanitize_rules: Optional[List[str]] = None  # ["remove_paths", "mask_secrets"]

@dataclass
class EditorConfigMapping:
    """Configuration mapping for an editor."""

    editor_name: str
    project_level_paths: List[str]
    user_level_paths: List[str]

    # Define what's reusable
    reusable_items: List[ConfigItemMapping]
    user_specific_items: List[ConfigItemMapping]
    conditional_items: List[ConfigItemMapping]  # Depends on content

    # Sanitization rules
    sanitize_patterns: Dict[str, str]  # regex patterns for sanitization


# Registry of all editor mappings
EDITOR_CONFIG_MAPPINGS: Dict[str, EditorConfigMapping] = {
    "continue": EditorConfigMapping(
        editor_name="continue",
        project_level_paths=[".continue/rules/*.md"],
        user_level_paths=["~/.continue/config.json"],
        reusable_items=[
            ConfigItemMapping("mcp_server", "name", "reusable"),
            ConfigItemMapping("mcp_server", "command", "conditional", ["check_for_paths"]),
            ConfigItemMapping("command", "prompt", "reusable"),
        ],
        user_specific_items=[
            ConfigItemMapping("mcp_server", "env", "user-specific", ["mask_secrets"]),
        ],
        sanitize_patterns={
            "file_paths": r"(/Users/[^/]+|/home/[^/]+|C:\\Users\\[^\\]+)",
            "api_keys": r"(sk-[a-zA-Z0-9]+|key_[a-zA-Z0-9]+)",
        }
    ),
    # ... mappings for other editors ...
}
```

**Estimated Effort:** 10-12 hours

#### Task 4.2: Implement Sanitization Engine
**New file:** `src/promptrek/utils/sanitizer.py`

**Purpose:** Automatically sanitize user-specific data

**Key functions:**
```python
class ConfigSanitizer:
    """Sanitize user-specific data from configurations."""

    def sanitize_paths(self, text: str) -> str:
        """Replace absolute paths with placeholders."""
        pass

    def sanitize_secrets(self, text: str) -> str:
        """Mask API keys, tokens, passwords."""
        pass

    def sanitize_mcp_server(self, server: MCPServer) -> MCPServer:
        """Sanitize MCP server configuration."""
        pass

    def sanitize_env_vars(self, env: Dict[str, str]) -> Dict[str, str]:
        """Sanitize environment variables."""
        pass

    def generate_sanitization_report(self) -> str:
        """Generate report of what was sanitized."""
        pass
```

**Estimated Effort:** 8-10 hours

---

### Phase 5: User Experience Enhancements

#### Task 5.1: Add Preview and Diff UI
**New file:** `src/promptrek/cli/preview.py`

**Purpose:** Show users what will change when syncing user-level configs

**Features:**
1. Tabular display of found configs
2. Diff view showing what will be added to project file
3. Highlight potentially sensitive data
4. Color-coded output for user-level vs project-level

**Estimated Effort:** 6-8 hours

#### Task 5.2: Add Confirmation Workflow
**File to modify:** `src/promptrek/cli/commands/sync.py`

**Interactive prompts:**
1. "Found X user-level configurations. Review them?"
2. Show preview with ability to:
   - View details for each item
   - Select/deselect items to include
   - Choose sanitization level
3. Final confirmation before writing

**Estimated Effort:** 6-8 hours

#### Task 5.3: Add Warning System
**New file:** `src/promptrek/utils/warnings.py`

**Warning types:**
1. Sensitive data detected (paths, secrets)
2. User-specific environment variables
3. Absolute file paths
4. Platform-specific commands

**Estimated Effort:** 4-5 hours

---

### Phase 6: Documentation & Examples

#### Task 6.1: Update Sync Documentation
**File to update:** `gh-pages/user-guide/sync.md`

**Add sections:**
1. "User-Level Configuration Sync"
2. "What Gets Synced vs Skipped"
3. "Sanitization and Security"
4. "Editor-Specific User-Level Paths"
5. Examples for each editor

**Estimated Effort:** 4-6 hours

#### Task 6.2: Create User-Level Config Guide
**New file:** `gh-pages/user-guide/user-level-configs.md`

**Content:**
1. Understanding user-level vs project-level
2. When to sync user-level configs
3. Security considerations
4. Best practices
5. Troubleshooting

**Estimated Effort:** 4-6 hours

#### Task 6.3: Update Schema Documentation
**File to update:** `gh-pages/user-guide/upf-specification.md`

**Add documentation for:**
1. New `user_level` field
2. New `config_source` field
3. New metadata fields
4. Examples of user-level configurations

**Estimated Effort:** 2-3 hours

#### Task 6.4: Create Example Configurations
**New directory:** `examples/user-level-sync/`

**Examples:**
1. Syncing Continue user-level MCP servers
2. Syncing Cline user-level configs
3. Sanitized vs non-sanitized examples
4. Mixed project and user-level configs

**Estimated Effort:** 3-4 hours

---

### Phase 7: Testing

#### Task 7.1: Unit Tests for New Models
**New tests:**
- Test ConfigSource enum
- Test extended MCPServer model with user_level fields
- Test UserConfig extensions
- Test sanitization logic

**Estimated Effort:** 6-8 hours

#### Task 7.2: Unit Tests for User-Level Mixin
**New file:** `tests/unit/adapters/test_user_level_mixin.py`

**Test coverage:**
- User-level config discovery
- Parsing user-level configs
- Sanitization
- Merging logic

**Estimated Effort:** 6-8 hours

#### Task 7.3: Integration Tests for Sync Command
**File to update:** `tests/integration/test_sync_integration.py`

**New test scenarios:**
1. Sync with `--include-user-level` flag
2. Sync with `--user-level-only` flag
3. Sanitization applied correctly
4. User confirmation workflow
5. Merge project and user-level configs

**Estimated Effort:** 8-10 hours

#### Task 7.4: Adapter-Specific Tests
For each adapter, test:
- User-level config discovery
- User-level config parsing
- Sanitization rules
- Merge logic

**Estimated Effort:** 2-3 hours per adapter = 12-18 hours total

#### Task 7.5: End-to-End Workflow Tests
**New file:** `tests/e2e/test_user_level_workflow.py`

**Scenarios:**
1. Full workflow: project setup → generate → manual user edit → sync with user-level
2. Sanitization workflow
3. Selective sync workflow
4. Cross-editor user-level sync

**Estimated Effort:** 8-10 hours

---

### Phase 8: Migration & Backward Compatibility

#### Task 8.1: Ensure Backward Compatibility
**Changes:**
- Default behavior: user-level configs are NOT synced (opt-in with flag)
- Existing sync commands work exactly as before
- No breaking changes to schemas (all new fields are optional)

**Estimated Effort:** 4-5 hours

#### Task 8.2: Add Migration Guide
**New file:** `docs/USER_LEVEL_MIGRATION_GUIDE.md`

**Content:**
1. How to start using user-level sync
2. Migrating existing setups
3. When to use vs not use user-level sync
4. Team workflow recommendations

**Estimated Effort:** 3-4 hours

---

## Implementation Priority

### Priority 1: Core Infrastructure (Must Have)
- Task 1.1: Schema Extensions ⭐
- Task 1.2: User Configuration Model Enhancement ⭐
- Task 2.1: Create User-Level Config Mixin ⭐
- Task 3.1: Add User-Level Flags to Sync Command ⭐
- Task 3.2: Implement User-Level Sync Logic ⭐

**Total Estimated Effort:** 30-40 hours

### Priority 2: Adapter Implementation (Should Have)
- Task 2.2.1: Continue Adapter ⭐
- Task 2.2.2: Cline Adapter ⭐
- Task 2.2.3: Windsurf Adapter ⭐
- Task 4.1: Create Editor Configuration Mapping Registry
- Task 4.2: Implement Sanitization Engine

**Total Estimated Effort:** 35-45 hours

### Priority 3: User Experience (Should Have)
- Task 5.1: Add Preview and Diff UI
- Task 5.2: Add Confirmation Workflow
- Task 5.3: Add Warning System
- Task 3.3: Add User-Level Sync to Interactive Mode

**Total Estimated Effort:** 20-27 hours

### Priority 4: Additional Adapters (Nice to Have)
- Task 2.2.4: Amazon Q Adapter
- Task 2.2.5: Claude Code Adapter
- Task 2.2.6: Cursor Adapter
- Task 2.2.7: Other Adapters

**Total Estimated Effort:** 18-25 hours

### Priority 5: Documentation & Testing (Must Have)
- Task 7.1-7.5: All Testing Tasks
- Task 6.1-6.4: All Documentation Tasks
- Task 8.1-8.2: Migration Tasks

**Total Estimated Effort:** 60-80 hours

---

## Total Estimated Effort

**Minimum Viable Product (Priority 1-2):**
- **65-85 hours** (~2-3 weeks for 1 developer)

**Full Implementation (Priority 1-4):**
- **103-137 hours** (~3-4 weeks for 1 developer)

**Complete with Testing & Docs (All Priorities):**
- **163-217 hours** (~4-6 weeks for 1 developer)

---

## Success Criteria

### Functional Requirements Met
✅ Sync command can discover user-level configurations
✅ User-level configs can be synced with confirmation
✅ Sensitive data is automatically sanitized
✅ Users can selectively choose what to sync
✅ Works with at least 3 major editors (Continue, Cline, Windsurf)
✅ Clear distinction between user-level and project-level configs
✅ No breaking changes to existing functionality

### Quality Requirements Met
✅ 80%+ test coverage for new code
✅ Comprehensive documentation
✅ Clear error messages and warnings
✅ Interactive mode support
✅ Migration guide provided

### User Experience Requirements Met
✅ Clear preview of what will be synced
✅ Easy-to-understand confirmation prompts
✅ Helpful warnings for sensitive data
✅ Works with existing workflows
✅ Good performance (no slowdowns)

---

## Risk Assessment

### Technical Risks

**High Risk:**
1. **Path Discovery Complexity**: Finding user-level configs across different OS and editor versions
   - *Mitigation*: Extensive testing on all platforms, clear documentation for manual path entry

2. **Sanitization Accuracy**: Detecting and sanitizing all sensitive data
   - *Mitigation*: Conservative sanitization rules, user preview before write, warning system

**Medium Risk:**
3. **Breaking Changes**: Accidentally breaking existing sync functionality
   - *Mitigation*: Opt-in flags, comprehensive regression testing, backward compatibility tests

4. **Editor API Changes**: User-level config formats changing in editor updates
   - *Mitigation*: Version detection, graceful degradation, clear error messages

**Low Risk:**
5. **Performance**: Scanning multiple user-level paths
   - *Mitigation*: Caching, lazy loading, only scan when flag is used

### User Experience Risks

**Medium Risk:**
1. **Confusion**: Users not understanding user-level vs project-level
   - *Mitigation*: Clear documentation, interactive mode guidance, warning messages

2. **Accidental Secret Exposure**: User commits sensitive data
   - *Mitigation*: Auto-sanitization by default, warnings, clear preview

---

## Dependencies

### Internal Dependencies
- Existing sync command infrastructure ✅
- Adapter registry system ✅
- Pydantic models ✅
- Interactive CLI framework ✅

### External Dependencies
- No new external dependencies required
- All current dependencies sufficient

---

## Future Enhancements (Out of Scope)

These are intentionally excluded from this feature but could be future additions:

1. **Automatic User-Level Sync**: Automatically sync user-level on every generate
2. **Cloud Sync**: Sync user-level configs across machines via cloud
3. **Team Templates**: Share sanitized user-level configs as team templates
4. **Config Recommendations**: AI-powered suggestions for user-level configs
5. **Editor Extensions**: Browser extensions to export user-level configs
6. **Conflict Resolution**: Advanced merge conflict resolution for user-level configs

---

## Open Questions

1. **Default Behavior**: Should user-level sync be opt-in (safer) or opt-out (convenient)?
   - **Recommendation**: Opt-in with `--include-user-level` flag

2. **Sanitization Level**: How aggressive should auto-sanitization be?
   - **Recommendation**: Conservative by default, with `--no-sanitize` flag to disable

3. **Storage Location**: Where to store metadata about user-level origins?
   - **Recommendation**: In .promptrek/user-config.promptrek.yaml (not committed)

4. **Team Workflow**: How should teams handle user-level configs that ARE team-wide?
   - **Recommendation**: Document best practice: sanitize → review → manually add to project file

---

## Conclusion

This feature will significantly enhance PrompTrek's sync capabilities by enabling it to work with user-level configurations across all supported editors. The implementation is structured in clear phases with well-defined priorities, allowing for incremental delivery and testing.

The key to success will be:
1. **Conservative defaults** (opt-in, auto-sanitize)
2. **Clear user communication** (previews, warnings, confirmations)
3. **Thorough testing** (especially sanitization and path discovery)
4. **Comprehensive documentation** (guide users through the new workflows)

With estimated 4-6 weeks of focused development effort, this feature can be delivered with high quality and minimal risk to existing functionality.
