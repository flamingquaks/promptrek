---
layout: guide
title: User Guide
---

# User Guide

Welcome to the PrompTrek User Guide! This comprehensive documentation will help you master PrompTrek and effectively manage AI editor prompts across your projects.

## Getting Started

PrompTrek is a universal AI editor prompt storage solution that allows you to write prompts once and deploy them everywhere. Whether you're using GitHub Copilot, Cursor, Continue, or any other AI coding assistant, PrompTrek has you covered.

## Documentation Sections

Explore the following sections to learn everything about PrompTrek:

### 📘 [UPF Specification](user-guide/upf-specification.html)
Learn about the Universal Prompt Format (UPF) - the standardized YAML-based format at the heart of PrompTrek. Understand the schema, structure, and how to create your own universal prompts.

### ⚡ [Advanced Features](user-guide/advanced-features.html)
Discover powerful features like variable substitution, conditional instructions, import systems, and multi-file configurations to create sophisticated prompt setups.

### 🔌 [Editor Adapters](user-guide/adapters.html)
Comprehensive guide to all supported AI editors. Learn how PrompTrek generates editor-specific configurations for GitHub Copilot, Cursor, Continue, Kiro, and more.

### 📊 [Adapter Capabilities](user-guide/adapter-capabilities.html)
Compare features across different editor adapters. See which advanced features are supported by each AI editor integration.

### 🔄 [Sync Feature](user-guide/sync.html)
Learn about bidirectional synchronization between editor-specific configurations and PrompTrek's universal format. Keep your prompts in sync across all tools.

### 🔗 [Pre-commit Integration](user-guide/pre-commit.html)
Set up automated prompt generation and validation with pre-commit hooks. Ensure your prompts are always up-to-date and valid before committing changes.

## Quick Reference

### Installation

```bash
# Install via pip
pip install promptrek

# Or using uv (recommended for development)
git clone https://github.com/flamingquaks/promptrek.git
cd promptrek
uv sync
```

### Basic Usage

```bash
# Initialize a new configuration
promptrek init

# Generate for a specific editor
promptrek generate --editor copilot

# Generate for all configured editors
promptrek generate --all

# Validate your configuration
promptrek validate

# Sync from editor-specific files back to UPF
promptrek sync --from copilot
```

## Need More Help?

- Check the [Quick Start Guide](quick-start.html) for a step-by-step tutorial
- Visit our [GitHub repository]({{ site.github_url }}) for examples and issues
- Review the [Contributing Guide](contributing.html) to help improve PrompTrek

Happy prompting! 🚀
