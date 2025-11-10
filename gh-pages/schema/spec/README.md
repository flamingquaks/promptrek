# Universal Spec Format (USF) Schema

This directory contains JSON Schema definitions for PrompTrek spec documents.

## What is USF?

The Universal Spec Format (USF) is a standardized format for specification documents managed by PrompTrek. These are individual markdown files that capture:

- Project requirements and specifications
- Design decisions and architecture
- Implementation plans
- Technical documentation

## Schema Versions

| Version | File | Status | Description |
|---------|------|--------|-------------|
| 1.0.0 | [v1.0.0.json](v1.0.0.json) | Current | Initial USF schema for spec documents |
| 1.0 | [v1.0.json](v1.0.json) | Alias | Alias for latest 1.0.x version |

## Usage

Spec files automatically include a schema directive at the top:

```html
<!-- yaml-language-server: $schema=https://promptrek.ai/schema/spec/v1.0.0.json -->
<!-- Universal Spec Format (USF) - PrompTrek Spec Document -->
<!-- This is a specification document managed by PrompTrek -->
<!-- Learn more about specs: https://promptrek.ai/user-guide/spec-driven-development -->
```

This enables IDE support for:
- Schema validation
- Autocomplete for metadata fields
- Documentation on hover

## Spec File Structure

A USF spec file consists of:

1. **HTML Comments**: Schema directive and documentation links
2. **Title**: Main heading with spec title
3. **Metadata**: Key-value pairs for spec information
   - ID: Unique identifier
   - Created: ISO 8601 timestamp
   - Updated: ISO 8601 timestamp (optional)
   - Source: Command that created the spec
   - Summary: Brief description (optional)
   - Tags: Categorization tags (optional)
4. **Separator**: `---` divider
5. **Content**: Markdown body with spec details

## Related Schemas

- Project configuration schemas: `../v3.0.0.json`, `../v3.1.0.json`
- User configuration schema: `../user-config/v1.0.0.json`

## Learn More

- [PrompTrek Specs Documentation](https://docs.promptrek.com/concepts/specs)
- [Universal Spec Format Guide](https://docs.promptrek.com/reference/usf)
- [Schema Documentation](https://docs.promptrek.com/reference/schemas)
