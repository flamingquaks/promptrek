# Support

Need help with PrompTrek? Here's how to get support.

## Community Support

### GitHub Discussions

The best place for general questions, discussions, and sharing ideas:

- **[GitHub Discussions](https://github.com/flamingquaks/promptrek/discussions)**
  - Ask questions
  - Share configurations
  - Request features
  - Help others

### GitHub Issues

For bug reports and feature requests:

- **[Bug Reports](https://github.com/flamingquaks/promptrek/issues/new?template=bug_report.md)**
  - Include reproduction steps
  - Provide your configuration
  - Share error messages and logs

- **[Feature Requests](https://github.com/flamingquaks/promptrek/issues/new?template=feature_request.md)**
  - Describe the feature
  - Explain the use case
  - Suggest implementation approaches

## Documentation

### Quick Links

- [Quick Start Guide](../getting-started/quick-start.md)
- [FAQ](../reference/faq.md)
- [Troubleshooting](../reference/troubleshooting.md)
- [Examples](../examples/index.md)

### Search

Use the search bar at the top of this page to find specific topics in the documentation.

## Getting Help

### Before Asking for Help

1. **Search the documentation** - Use the search feature
2. **Check the FAQ** - Common questions are answered in the [FAQ](../reference/faq.md)
3. **Review troubleshooting** - See the [Troubleshooting Guide](../reference/troubleshooting.md)
4. **Check existing issues** - Someone may have already reported your issue

### When Asking for Help

Please include:

1. **PrompTrek version**
   ```bash
   promptrek --version
   ```

2. **Your configuration**
   - Share your `.promptrek.yaml` file (remove sensitive data)
   - Specify which schema version you're using

3. **Steps to reproduce**
   - Exact commands you ran
   - What you expected to happen
   - What actually happened

4. **Error messages**
   - Full error output
   - Use `--verbose` flag for detailed logs

5. **Environment details**
   - Operating system and version
   - Python version
   - Editor you're targeting

### Example Support Request

```markdown
**PrompTrek Version:** 0.6.0
**Python Version:** 3.11.5
**OS:** macOS 14.1

**Configuration:**
```yaml
schema_version: "3.1.0"
metadata:
  title: "My Project"
...
```

**Steps to Reproduce:**
1. Run `promptrek generate .promptrek.yaml --editor cursor`
2. Error occurs

**Error Message:**
```
ValidationError: Invalid schema version
```

**Expected:** Should generate Cursor configuration
**Actual:** Validation error
```

## Response Time

- **Community questions**: Usually answered within 24-48 hours
- **Bug reports**: Triaged within 1-3 days
- **Feature requests**: Reviewed during sprint planning
- **Pull requests**: Reviewed within 1 week

## Contributing

The best way to get help is to help others! Consider:

- Answering questions in discussions
- Improving documentation
- Submitting bug fixes
- Adding new features

See the [Contributing Guide](contributing.md) for more information.

## Social Media

Stay updated on PrompTrek developments:

- **GitHub**: [@flamingquaks/promptrek](https://github.com/flamingquaks/promptrek)
- **Issues**: [Report bugs](https://github.com/flamingquaks/promptrek/issues)
- **Discussions**: [Join the conversation](https://github.com/flamingquaks/promptrek/discussions)

## Code of Conduct

All support channels are governed by our [Code of Conduct](code-of-conduct.md). Please be respectful and constructive.

## Professional Support

For professional support, training, or custom development:

- Open a discussion with the tag `professional-support`
- Contact the maintainers through GitHub

## Additional Resources

### External Resources

- [MkDocs Documentation](https://www.mkdocs.org/)
- [Python Documentation](https://docs.python.org/)
- [YAML Specification](https://yaml.org/spec/)

### Related Projects

- [Model Context Protocol](https://modelcontextprotocol.io/)
- [GitHub Copilot Documentation](https://docs.github.com/en/copilot)
- [Cursor Documentation](https://docs.cursor.com/)
- [Claude Code Documentation](https://docs.anthropic.com/)

## Emergency Contact

For security vulnerabilities, please **do not** open a public issue. Instead:

1. Email security concerns to the maintainers (check repository for contact)
2. Use GitHub's private vulnerability reporting
3. Allow time for a fix before public disclosure

Thank you for using PrompTrek!
