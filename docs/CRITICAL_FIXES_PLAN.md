# PrompTrek Critical Fixes Plan - Priority: Existing Functionality

## Focus: Fix Broken Implementations First

**Priority**: Fix existing functionality that currently generates incorrect or useless files before adding any new features.

## Critical Issues Requiring Immediate Fix 🔴

### Issue 1: Wrong File Formats and Locations
**Impact**: Generated files don't work with actual AI tools

**Tools Affected:**
- **Continue**: Uses deprecated `.continue/config.json` instead of `config.yaml`
- **Cline**: Uses non-existent `.cline/config.json` instead of `.clinerules`
- **Cursor**: Missing modern `.cursor/rules/` system

### Issue 2: Generating Files for Tools That Don't Support Them
**Impact**: 40% of generated files are completely useless

**Tools Affected:**
- **Amazon Q**: Generates project files but only uses global settings
- **JetBrains AI**: Generates project files but only uses IDE config
- **Tabnine**: Generates project files but only uses enterprise settings
- **Windsurf**: Still references discontinued "Codeium"

## PHASE 1: Critical Fixes (Week 1) 🔴

### 1.1 Fix Continue Adapter - BROKEN FORMAT
**Current Problem**: Generates `.continue/config.json` (deprecated)  
**Fix**: Generate `config.yaml` (current format)

**File**: `src/promptrek/adapters/continue_adapter.py`
```python
# BEFORE (WRONG):
output_file = output_dir / ".continue" / "config.json"
content = json.dumps(config_data, indent=2)

# AFTER (CORRECT): 
output_file = output_dir / "config.yaml"
content = yaml.dump(config_data, default_flow_style=False)
```

### 1.2 Fix Cline Adapter - COMPLETELY WRONG
**Current Problem**: Generates `.cline/config.json` (doesn't exist)  
**Fix**: Generate `.clinerules` (actual format)

**File**: `src/promptrek/adapters/cline.py`
```python
# BEFORE (WRONG):
output_file = output_dir / ".cline" / "config.json"

# AFTER (CORRECT):
output_file = output_dir / ".clinerules"  
# Use markdown format, not JSON
```

### 1.3 Fix Cursor Adapter - OUTDATED
**Current Problem**: Only generates `.cursorrules` (legacy)  
**Fix**: Generate `.cursor/rules/` (modern format)

**File**: `src/promptrek/adapters/cursor.py`
```python
# BEFORE (INCOMPLETE):
output_file = output_dir / ".cursorrules"

# AFTER (COMPLETE):
# Primary: .cursor/rules/ directory with .mdc files
# Secondary: Keep .cursorrules for backward compatibility
```

### 1.4 Disable Invalid Tool Adapters - USELESS FILES
**Current Problem**: Generates files for tools that don't use them  
**Fix**: Disable or convert to "information only" mode

**Files to modify:**
- `src/promptrek/adapters/amazon_q.py` - Should not generate files
- `src/promptrek/adapters/jetbrains.py` - Should not generate files  
- `src/promptrek/adapters/tabnine.py` - Should not generate files
- `src/promptrek/adapters/codeium.py` - Update to Windsurf, no files

## PHASE 2: Registry and CLI Updates (Week 1-2) 🟡

### 2.1 Update Registry to Mark Invalid Adapters
**File**: `src/promptrek/adapters/registry.py`

```python
# Add capability flags to prevent file generation
class AdapterCapabilities:
    GENERATES_PROJECT_FILES = "generates_project_files"
    GLOBAL_CONFIG_ONLY = "global_config_only"

# Update registry to mark which adapters actually work
ADAPTER_CAPABILITIES = {
    "copilot": [AdapterCapabilities.GENERATES_PROJECT_FILES],
    "cursor": [AdapterCapabilities.GENERATES_PROJECT_FILES], 
    "continue": [AdapterCapabilities.GENERATES_PROJECT_FILES],
    "cline": [AdapterCapabilities.GENERATES_PROJECT_FILES],
    "amazon_q": [AdapterCapabilities.GLOBAL_CONFIG_ONLY],
    "jetbrains": [AdapterCapabilities.GLOBAL_CONFIG_ONLY],
    "tabnine": [AdapterCapabilities.GLOBAL_CONFIG_ONLY],
    "windsurf": [AdapterCapabilities.GLOBAL_CONFIG_ONLY]
}
```

### 2.2 Update CLI to Show Which Tools Actually Work
**File**: `src/promptrek/cli/commands/generate.py`

```python
def generate():
    """Only generate files for tools that actually support them."""
    
    working_adapters = get_project_file_adapters()  # Only 6 tools
    global_only_adapters = get_global_config_adapters()  # 4 tools
    
    click.echo("Generating files for tools that support project configuration:")
    for adapter in working_adapters:
        # Generate files
        
    if global_only_adapters:
        click.echo(f"\nℹ️  Note: {len(global_only_adapters)} tools use global configuration only:")
        for adapter in global_only_adapters:
            click.echo(f"  - {adapter.name}: Configure through {adapter.config_method}")
```

## PHASE 3: Validation and Testing (Week 2) 🟡

### 3.1 Add Validation for Generated Files
```python
def validate_generated_files(adapter_name: str, output_dir: Path) -> List[str]:
    """Validate that generated files are correct for the tool."""
    errors = []
    
    if adapter_name == "continue":
        config_yaml = output_dir / "config.yaml"
        if not config_yaml.exists():
            errors.append("Missing config.yaml for Continue")
        
        # Check for deprecated file
        deprecated = output_dir / ".continue" / "config.json" 
        if deprecated.exists():
            errors.append("Found deprecated .continue/config.json - remove this file")
    
    # Similar validation for other tools
    return errors
```

### 3.2 Test Against Real Tools
```python
# Create integration tests to verify files actually work
def test_continue_config_works():
    """Test that generated config.yaml works with Continue."""
    # Generate config using PrompTrek
    # Validate YAML format  
    # Test that Continue can parse it
    
def test_cline_rules_work():
    """Test that generated .clinerules works with Cline."""
    # Generate rules using PrompTrek
    # Validate markdown format
    # Test that Cline can read it
```

## Immediate Actions (This Week)

### Day 1: Fix Continue
- [ ] Update `continue_adapter.py` to generate `config.yaml`
- [ ] Fix YAML format issues
- [ ] Test with actual Continue tool

### Day 2: Fix Cline  
- [ ] Completely rewrite `cline.py` adapter
- [ ] Generate `.clinerules` in markdown format
- [ ] Test with actual Cline tool

### Day 3: Fix Cursor
- [ ] Update `cursor.py` to generate `.cursor/rules/`
- [ ] Keep `.cursorrules` for backward compatibility  
- [ ] Test with actual Cursor tool

### Day 4: Disable Invalid Adapters
- [ ] Mark Amazon Q, JetBrains AI, Tabnine, Windsurf as global-config-only
- [ ] Update CLI to not generate files for these tools
- [ ] Provide configuration instructions instead

### Day 5: Testing and Validation
- [ ] Test all fixes work with real tools
- [ ] Update documentation
- [ ] Create validation scripts

## Success Criteria

**Week 1 Goals:**
- [ ] Continue generates working `config.yaml` (not broken JSON)
- [ ] Cline generates working `.clinerules` (not non-existent JSON)  
- [ ] Cursor generates modern `.cursor/rules/` (not just legacy)
- [ ] Invalid tools stop generating useless files

**Validation:**
- [ ] All generated files can be parsed by their respective tools
- [ ] No more files generated for global-config-only tools
- [ ] Users get clear messages about which tools support project configs

## What We're NOT Doing Yet

- ❌ Adding new features like path-specific instructions
- ❌ Major architectural changes
- ❌ Advanced configuration options
- ❌ New tool support

**Focus**: Fix what's broken first, enhance later.

## Files to Modify (Priority Order)

1. **`src/promptrek/adapters/continue_adapter.py`** - Fix deprecated JSON format
2. **`src/promptrek/adapters/cline.py`** - Fix completely wrong file location  
3. **`src/promptrek/adapters/cursor.py`** - Add modern file format
4. **`src/promptrek/adapters/amazon_q.py`** - Disable file generation
5. **`src/promptrek/adapters/jetbrains.py`** - Disable file generation
6. **`src/promptrek/adapters/tabnine.py`** - Disable file generation  
7. **`src/promptrek/adapters/codeium.py`** - Update to Windsurf, disable generation
8. **`src/promptrek/adapters/registry.py`** - Add capability flags
9. **`src/promptrek/cli/commands/generate.py`** - Update CLI messaging

This plan focuses exclusively on fixing the broken functionality that currently exists, without adding any new features or complex architectural changes.
