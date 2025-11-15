# promptrek validate

Validate one or more universal prompt files for correctness.

## Synopsis

```bash
promptrek validate FILES... [OPTIONS]
```

## Description

The `validate` command checks your PrompTrek configuration files (`.promptrek.yaml`) for syntax errors, schema compliance, and logical consistency. It provides detailed error messages and warnings to help you fix issues before generating editor configurations.

Validation is an essential step in the PrompTrek workflow to ensure your configuration will work correctly across all supported editors.

## Options

**`FILES...`** (required)
: One or more `.promptrek.yaml` files to validate

**`--strict`**
: Treat warnings as errors (fail validation if warnings are present)

## Examples

### Basic Validation

Validate a single file:

```bash
promptrek validate project.promptrek.yaml
```

**Success output**:
```
🔍 Validating project.promptrek.yaml...
✅ File parsed successfully
✅ Validation passed
```

### Validate Multiple Files

Check multiple configuration files at once:

```bash
promptrek validate backend.yaml frontend.yaml shared.yaml
```

**Output**:
```
🔍 Validating backend.yaml...
✅ Validation passed

🔍 Validating frontend.yaml...
✅ Validation passed

🔍 Validating shared.yaml...
✅ Validation passed
```

### Strict Mode

Treat warnings as errors:

```bash
promptrek validate project.promptrek.yaml --strict
```

**Example output with warnings in strict mode**:
```
🔍 Validating project.promptrek.yaml...
✅ File parsed successfully
❌ Found 2 error(s):
  • metadata.author: Recommended format is "Name <email@example.com>"
  • variables: Variable 'UNUSED_VAR' is defined but never used in content
```

Exit code: `1` (failure)

### Verbose Validation

Use global `--verbose` flag for detailed information:

```bash
promptrek --verbose validate project.promptrek.yaml
```

**Verbose output includes**:
```
🔍 Validating project.promptrek.yaml...
✅ File parsed successfully

📋 Summary:
  Title: My Project Assistant
  Version: 1.0.0
  Targets: claude, cursor, continue
  Technologies: python, typescript, react
  Instructions: 12 total
  Examples: 3
  Variables: 5

✅ Validation passed
```

## Validation Checks

### Schema Validation

Checks that your file conforms to the PrompTrek schema:

- **Required fields**: `schema_version`, `metadata`, `content` (v2/v3) or structured fields (v1)
- **Field types**: Ensures fields have correct data types
- **Schema version**: Validates against the correct version (v1.0.0, v2.0.0, v2.1.0, or v3.0.0)

**Example error**:
```
❌ Validation failed with 1 error(s):
  • metadata.version: Required field is missing
```

### Metadata Validation

Verifies metadata fields are present and well-formed:

- **title**: Required, non-empty string
- **description**: Required, non-empty string
- **version**: Required, follows semantic versioning
- **author**: Recommended format: "Name <email@example.com>"
- **dates**: Valid date format (YYYY-MM-DD)

**Example warning**:
```
⚠️ Found 1 warning(s):
  • metadata.author: Recommended format is "Name <email@example.com>"
```

### Content Validation

For v2/v3 schemas (markdown-first):

- **content**: Must be non-empty
- **syntax**: Checks for common markdown issues
- **variables**: Validates variable references

For v1 schemas (structured):

- **instructions**: Validates structure and content
- **context**: Checks required context fields
- **examples**: Validates code examples

**Example error**:
```
❌ Validation failed with 1 error(s):
  • content: Content field cannot be empty
```

### Variable Validation

Checks variable definitions and usage:

- **Definition format**: Variables must follow naming conventions
- **Usage**: Variables should be used in content
- **References**: All used variables should be defined

**Example warnings**:
```
⚠️ Found 2 warning(s):
  • Variable 'PROJECT_NAME' is defined but never used in content
  • Variable reference '{{UNKNOWN_VAR}}' in content is not defined
```

### Plugin Validation (v2.1+ / v3)

For configurations with plugins:

- **MCP Servers**: Validates server configuration structure
- **Commands**: Checks slash command definitions
- **Agents**: Validates agent configurations
- **Hooks**: Verifies hook definitions

**Example error**:
```
❌ Validation failed with 1 error(s):
  • mcp_servers[0].command: Command field is required for MCP server 'my-server'
```

## Error Types

### Errors (Critical)

Critical issues that prevent generation:

```
❌ Validation failed with 3 error(s):
  • metadata.title: Required field is missing
  • content: Content field cannot be empty
  • schema_version: Invalid version '4.0.0', must be 1.0.0, 2.0.0, 2.1.0, or 3.0.0
```

**Exit code**: `1`

**Action**: Fix all errors before attempting generation.

### Warnings (Non-Critical)

Issues that don't prevent generation but should be reviewed:

```
⚠️ Found 2 warning(s):
  • metadata.author: Recommended format is "Name <email@example.com>"
  • Variable 'DEBUG_MODE' is defined but never used
```

**Exit code**: `0` (unless `--strict` is used)

**Action**: Review and fix warnings for best practices.

## Validation Output

### Success

```
🔍 Validating project.promptrek.yaml...
✅ File parsed successfully
✅ Validation passed
```

### Success with Warnings

```
🔍 Validating project.promptrek.yaml...
✅ File parsed successfully
⚠️ Found 1 warning(s):
  • metadata.author: Recommended format is "Name <email@example.com>"
✅ Validation passed with warnings
```

### Failure

```
🔍 Validating project.promptrek.yaml...
❌ Parsing failed: Invalid YAML syntax at line 15: mapping values are not allowed here

# or

🔍 Validating project.promptrek.yaml...
✅ File parsed successfully
❌ Validation failed with 2 error(s):
  • metadata.version: Required field is missing
  • content: Content field cannot be empty
```

## Common Validation Issues

### YAML Syntax Errors

**Problem**:
```
❌ Parsing failed: Invalid YAML syntax at line 10: mapping values are not allowed here
```

**Common causes**:
- Incorrect indentation
- Missing colons or quotes
- Invalid characters
- Unclosed strings

**Solution**:
```bash
# Use a YAML validator to find syntax issues
yamllint project.promptrek.yaml

# Check line 10 in your editor
vim +10 project.promptrek.yaml
```

### Missing Required Fields

**Problem**:
```
❌ Validation failed with 1 error(s):
  • metadata.title: Required field is missing
```

**Solution**: Add the required field:
```yaml
metadata:
  title: "My Project Assistant"  # Add this
  description: "AI configuration"
  version: "1.0.0"
```

### Invalid Schema Version

**Problem**:
```
❌ Validation failed with 1 error(s):
  • schema_version: Invalid version '4.0.0', must be 1.0.0, 2.0.0, 2.1.0, or 3.0.0
```

**Solution**: Use a valid schema version:
```yaml
schema_version: "3.0.0"  # Use 3.0.0 for new projects
```

### Variable Issues

**Problem**:
```
⚠️ Found 1 warning(s):
  • Variable 'PROJECT_NAME' is defined but never used in content
```

**Solution**: Either use the variable or remove it:
```yaml
# Option 1: Use it in content
content: |
  # {{PROJECT_NAME}} Documentation
  ...

# Option 2: Remove unused variable
variables:
  # PROJECT_NAME: "My Project"  # Removed
  AUTHOR: "Developer"
```

## Integration with Workflows

### Pre-Generation Validation

Always validate before generating:

```bash
# Validate first, then generate
promptrek validate project.promptrek.yaml && \
  promptrek generate --all
```

### Pre-Commit Hook

Add validation to pre-commit:

```yaml
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: validate-promptrek
        name: Validate PrompTrek files
        entry: promptrek validate
        language: system
        files: '\.promptrek\.yaml$'
```

### CI/CD Integration

```yaml
# .github/workflows/validate.yml
name: Validate PrompTrek
on: [push, pull_request]
jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - run: pip install promptrek
      - run: promptrek validate project.promptrek.yaml --strict
```

## Batch Validation

### Validate All Files in Directory

```bash
# Find and validate all .promptrek.yaml files
find . -name "*.promptrek.yaml" -exec promptrek validate {} \;

# Or using shell glob
promptrek validate **/*.promptrek.yaml
```

### Validate with Error Reporting

```bash
# Count total errors across all files
FAILED=0
for file in *.promptrek.yaml; do
    if ! promptrek validate "$file" --strict; then
        FAILED=$((FAILED + 1))
    fi
done
echo "Failed validations: $FAILED"
```

## Tips and Best Practices

!!! tip "Validate Early and Often"
    Run validation after any changes to your PrompTrek configuration:
    ```bash
    # After editing
    vim project.promptrek.yaml
    promptrek validate project.promptrek.yaml
    ```

!!! tip "Use Strict Mode in CI"
    Enable strict mode in CI/CD to enforce high quality:
    ```bash
    promptrek validate project.promptrek.yaml --strict
    ```

!!! tip "Fix Warnings"
    Even though warnings don't cause failure, addressing them improves configuration quality and prevents future issues.

!!! warning "Don't Skip Validation"
    Always validate before committing or generating. Invalid configurations can cause generation failures or unexpected behavior.

!!! note "Schema Version Matters"
    Different schema versions have different validation rules. Make sure you're using the correct schema version for your needs.

## Troubleshooting

### Validation Passes but Generation Fails

**Problem**: Validation succeeds but generation fails

**Cause**: Some editor-specific validations only happen during generation

**Solution**:
```bash
# Use dry-run to test generation
promptrek generate --editor claude --dry-run

# If that works, try actual generation
promptrek generate --editor claude
```

### False Positives

**Problem**: Validator reports false warnings

**Cause**: Validator may not understand complex variable usage or conditional content

**Solution**:
- Verify the warning is actually false
- If it's a legitimate pattern, consider refactoring
- Report false positives as issues

### Performance Issues

**Problem**: Validation is slow for large files

**Solution**:
```bash
# Split large configurations
# Validate in parallel
promptrek validate file1.yaml &
promptrek validate file2.yaml &
wait
```

## See Also

- [init command](init.md) - Initialize PrompTrek configuration
- [generate command](generate.md) - Generate editor configurations
- [UPF Specification](../../user-guide/upf-specification.md) - Schema documentation
- [Common Issues](../../getting-started/basic-usage.md#troubleshooting) - Troubleshooting guide
