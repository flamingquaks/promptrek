# Feedback and Support

We value your feedback and want to hear from you! PrompTrek is actively developed and we're always looking to improve based on community input.

## Quick Links

<div class="grid cards" markdown>

-   :material-bug:{ .lg .middle } **Report a Bug**

    ---

    Found a bug? Help us fix it with a detailed report.

    [:octicons-arrow-right-24: Report Bug](https://github.com/flamingquaks/promptrek/issues/new?template=bug_report.yml)

-   :material-lightbulb:{ .lg .middle } **Request a Feature**

    ---

    Have an idea? Share your feature request with us.

    [:octicons-arrow-right-24: Request Feature](https://github.com/flamingquaks/promptrek/issues/new?template=feature_request.yml)

-   :material-chat:{ .lg .middle } **Ask a Question**

    ---

    Need help or want to discuss ideas?

    [:octicons-arrow-right-24: Join Discussion](https://github.com/flamingquaks/promptrek/discussions)

-   :material-magnify:{ .lg .middle } **Browse Issues**

    ---

    Search existing issues and discussions.

    [:octicons-arrow-right-24: Browse Issues](https://github.com/flamingquaks/promptrek/issues)

</div>

## Report a Bug

Found a bug? Help us fix it by creating a detailed bug report.

### Before Reporting

1. **Search existing issues** to avoid duplicates: [Search Issues](https://github.com/flamingquaks/promptrek/issues)
2. **Check the latest version** - is the bug still present in the latest release?
3. **Review troubleshooting** - might have a quick fix: [Troubleshooting Guide](../reference/troubleshooting.md)

### Submit a Bug Report

[**Create Bug Report →**](https://github.com/flamingquaks/promptrek/issues/new?template=bug_report.yml)

**Please include:**

- **PrompTrek version** - Run `promptrek --version`
- **Python version** - Run `python --version`
- **Operating system** - Windows, macOS, Linux (which distro?)
- **Steps to reproduce** - Clear, numbered steps
- **Expected behavior** - What should happen
- **Actual behavior** - What actually happens
- **Error messages** - Full stack trace if available
- **Configuration file** - Minimal example (sanitize secrets!)

**Example:**

```markdown
## Environment
- PrompTrek: v0.5.0
- Python: 3.11.5
- OS: Ubuntu 22.04

## Steps to Reproduce
1. Create config.yaml with nested plugins
2. Run `promptrek generate config.yaml --editor cursor`
3. Check .cursor/rules/index.mdc

## Expected Behavior
File should contain MCP server configuration

## Actual Behavior
File is empty

## Error Message
```
ValueError: mcp_servers not found in configuration
```

## Configuration
```yaml
schema_version: "2.1.0"
plugins:
  mcp_servers:
    - name: github
      command: npx
```
```

## Request a Feature

Have an idea for a new feature or improvement?

### Before Requesting

1. **Search existing requests** - someone might have already suggested it
2. **Consider the scope** - does it fit PrompTrek's purpose?
3. **Think about users** - how would this benefit others?

### Submit a Feature Request

[**Create Feature Request →**](https://github.com/flamingquaks/promptrek/issues/new?template=feature_request.yml)

**Tell us about:**

- **The problem** you're trying to solve
- **Your proposed solution** - how should it work?
- **Benefits** - who would this help and how?
- **Alternatives** - other solutions you've considered
- **Example usage** - what would the code/config look like?

**Example:**

```markdown
## Problem
Currently, PrompTrek can't generate configurations for multiple environments (dev, staging, prod) from a single config file.

## Proposed Solution
Add support for environment-specific variable files:

```yaml
# config.yaml
content: |
  API: {{{ API_URL }}}

# .promptrek/variables.dev.yaml
API_URL: "http://localhost:3000"

# .promptrek/variables.prod.yaml
API_URL: "https://api.production.com"
```

Then generate with: `promptrek generate config.yaml --env prod`

## Benefits
- Manage multiple environments easily
- No need for multiple config files
- Team members can have local overrides

## Alternatives
- Use `-V` flag for each variable (tedious for many vars)
- Maintain separate config files (duplication)

## Example Usage
```bash
# Development
promptrek generate config.yaml --env dev --editor cursor

# Production
promptrek generate config.yaml --env prod --editor cursor
```
```

## Ask a Question

For questions, ideas, or general discussion, use GitHub Discussions.

[**Join the Discussion →**](https://github.com/flamingquaks/promptrek/discussions)

### Discussion Categories

**Q&A** - Ask questions and get help
- How do I...?
- What's the best way to...?
- Is it possible to...?

**Ideas** - Share suggestions and brainstorm
- Feature ideas
- Workflow improvements
- Integration suggestions

**Show and Tell** - Share your configurations
- Example projects
- Tips and tricks
- Success stories

**General** - Everything else
- Community chat
- Announcements
- Off-topic (related to AI/development)

## Browse Existing Issues

Before creating a new issue, please check if it already exists:

[**Browse All Issues →**](https://github.com/flamingquaks/promptrek/issues)

**Filter by labels:**
- `bug` - Something isn't working
- `enhancement` - New feature or request
- `documentation` - Documentation improvements
- `good first issue` - Good for newcomers
- `help wanted` - Extra attention needed
- `question` - Further information requested

## Response Time

We aim to respond to:

| Type | Response Time | Resolution Time |
|------|---------------|-----------------|
| **Bug reports** | Within 2-3 business days | Varies by severity |
| **Feature requests** | Within 1 week | Varies by complexity |
| **Questions (Discussions)** | Within 1-2 business days | As needed |
| **Pull requests** | Within 3-5 business days | Varies by size |

!!! note "Community Effort"
    PrompTrek is maintained by a small team. Response times may vary. Community members often help each other - your contributions are appreciated!

## How You Can Help

### Beyond Reporting

**Help Others:**
- Answer questions in Discussions
- Review pull requests
- Test pre-release versions
- Share your configurations

**Improve Documentation:**
- Fix typos
- Add examples
- Clarify unclear sections
- Create tutorials

**Spread the Word:**
- Star the repository
- Share on social media
- Write blog posts
- Give talks/presentations

## Community Guidelines

When providing feedback:

**Do:**
- Be specific and detailed
- Provide examples
- Be respectful and constructive
- Search before posting
- Use appropriate labels/categories

**Don't:**
- Report multiple issues in one
- Post duplicate issues
- Include sensitive information
- Use aggressive language
- Post off-topic content

See our [Code of Conduct](code-of-conduct.md) for full guidelines.

## Contact Information

### Project Links

- **GitHub Repository:** [https://github.com/flamingquaks/promptrek](https://github.com/flamingquaks/promptrek)
- **Documentation:** [https://flamingquaks.github.io/promptrek](https://flamingquaks.github.io/promptrek)
- **Issues:** [https://github.com/flamingquaks/promptrek/issues](https://github.com/flamingquaks/promptrek/issues)
- **Discussions:** [https://github.com/flamingquaks/promptrek/discussions](https://github.com/flamingquaks/promptrek/discussions)

### Social Media

Stay updated on PrompTrek news and updates:

- **GitHub:** Watch releases and discussions
- **Twitter/X:** Follow development updates (coming soon)
- **Blog:** Technical deep-dives (coming soon)

### For Private Matters

For security vulnerabilities or sensitive issues:

- **Email:** developer@flamingquaks.dev
- **Subject:** Include "PrompTrek" in subject line

!!! warning "Security Issues"
    Please do **not** create public issues for security vulnerabilities. Email us directly at developer@flamingquaks.dev.

## Additional Resources

### Documentation

- **[User Guide](../user-guide/index.md)** - Complete documentation
- **[Examples](../examples/index.md)** - Real-world configurations
- **[FAQ](../reference/faq.md)** - Frequently asked questions
- **[Troubleshooting](../reference/troubleshooting.md)** - Common issues

### Contributing

Want to contribute code or documentation?

- **[Contributing Guide](contributing.md)** - How to contribute
- **[Code of Conduct](code-of-conduct.md)** - Community guidelines
- **[Development Setup](contributing.md#development-setup)** - Get started

## Thank You

Thank you for taking the time to provide feedback! Your input helps make PrompTrek better for everyone.

Every bug report, feature request, question, and contribution makes a difference. We appreciate your support and involvement in the PrompTrek community.

---

**Questions?** Check the [FAQ](../reference/faq.md) or [join the discussion](https://github.com/flamingquaks/promptrek/discussions)!

**Want to contribute?** See the [Contributing Guide](contributing.md)!
