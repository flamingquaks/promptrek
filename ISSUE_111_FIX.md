# Fix for Issue #111: Amazon Q Agents Configuration Incorrect

## Issue Summary
Amazon Q agents were being generated in the correct location (`.amazonq/cli-agents/*.json`) but were not being picked up by the Amazon Q CLI because the `resources` field was using an incorrect path.

## Root Cause
The `resources` field in generated agent JSON files was using:
```json
"resources": ["file://.amazonq/rules/**/*.md"]
```

However, according to Amazon Q documentation, relative paths in the `resources` field are resolved **relative to the agent configuration file's directory**.

Since agent configs are located at:
- `.amazonq/cli-agents/agent-name.json`

And rules are located at:
- `.amazonq/rules/*.md`

The path `file://.amazonq/rules/**/*.md` would resolve to:
- `.amazonq/cli-agents/.amazonq/rules/**/*.md` ❌ (incorrect)

## Solution
Changed the `resources` path to use a proper relative path:
```json
"resources": ["file://../rules/**/*.md"]
```

This correctly resolves from the agent config location:
- Agent at: `.amazonq/cli-agents/agent-name.json`
- Path: `../rules/**/*.md`
- Resolves to: `.amazonq/rules/**/*.md` ✅ (correct)

## Files Modified

### 1. `src/promptrek/adapters/amazon_q.py`
**Changes:**
- Line ~360: Updated `_generate_agents_v3()` to use `file://../rules/**/*.md`
- Line ~420: Updated `_generate_default_agent_with_hooks()` to use `file://../rules/**/*.md`

**Before:**
```python
agent_config["resources"] = ["file://.amazonq/rules/**/*.md"]
```

**After:**
```python
# Add resources pointing to rules (using relative path from agent config location)
# Agent configs are in .amazonq/cli-agents/, rules are in .amazonq/rules/
# So we need to go up one level: ../rules/**/*.md
agent_config["resources"] = ["file://../rules/**/*.md"]
```

### 2. `tests/unit/adapters/test_amazon_q.py`
**Changes:**
- Line 246: Updated test assertion to expect correct path
- Added new test `test_agent_resources_use_relative_path()` to document and verify the fix

## Verification

### Test Results
All 16 Amazon Q adapter tests pass:
```bash
$ uv run python -m pytest tests/unit/adapters/test_amazon_q.py -v --no-cov
============================== 16 passed in 0.09s ==============================
```

### Generated Agent Example
```json
{
  "name": "test-agent",
  "description": "A test agent",
  "prompt": "You are a helpful test agent",
  "tools": [
    "fs_read",
    "fs_write"
  ],
  "resources": [
    "file://../rules/**/*.md"
  ]
}
```

## References
- **Amazon Q Agent Format Documentation**: https://github.com/aws/amazon-q-developer-cli/blob/main/docs/agent-format.md
- **Amazon Q CLI Source** (agent loading): https://github.com/aws/amazon-q-developer-cli/blob/main/crates/agent/src/agent/agent_config/mod.rs
- **Path Resolution**: Relative paths in `resources` are resolved relative to the agent config file's directory

## Testing Instructions

1. Create a test PrompTrek config with agents:
```yaml
schema_version: "3.1.0"
metadata:
  title: "Test Amazon Q Agent"
  description: "Testing agent generation"
  
content: |
  # Test Project
  This is a test project.

agents:
  - name: test-agent
    description: "A test agent"
    prompt: "You are a helpful test agent"
    tools: ["fs_read", "fs_write"]
```

2. Generate Amazon Q configuration:
```bash
promptrek generate test.promptrek.yaml --editor amazon-q
```

3. Verify the generated agent has correct resources path:
```bash
cat .amazonq/cli-agents/test-agent.json
# Should show: "resources": ["file://../rules/**/*.md"]
```

4. Test with Amazon Q CLI:
```bash
q chat --agent test-agent
# Agent should now be recognized and load rules correctly
```

## Impact
- **Severity**: High - Agents were not functional before this fix
- **Scope**: All Amazon Q agent generation (schema v3.x)
- **Backward Compatibility**: No breaking changes - only fixes incorrect behavior
- **User Action Required**: Regenerate Amazon Q agents using `promptrek generate`
