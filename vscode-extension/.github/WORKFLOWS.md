# GitHub Actions Workflows for VSCode Extension

This document describes the GitHub Actions workflows configured for the PrompTrek VSCode extension.

## Workflows Overview

### 1. VSCode Extension CI (`vscode-extension-ci.yml`)

**Triggers:**
- Push to `main`, `develop`, or `claude/**` branches
- Pull requests to `main` or `develop`
- Only when files in `vscode-extension/` are modified

**Purpose:** Continuous Integration to validate extension quality

**Jobs:**

#### `build-and-test`
- **Platforms:** Ubuntu, Windows, macOS
- **Node versions:** 18.x, 20.x
- **Steps:**
  1. Install dependencies with `npm ci`
  2. Lint code with `npm run lint`
  3. Compile TypeScript
  4. Package extension with `vsce`
  5. Upload VSIX artifacts

#### `validate-extension`
- Validates `package.json` structure
- Checks for required files (README, CHANGELOG, etc.)
- Validates TypeScript configuration
- Analyzes extension size
- Ensures it's under 50MB

#### `security-scan`
- Runs `npm audit` for vulnerabilities
- Uses TruffleHog to check for secrets
- Reports security issues

#### `summary`
- Generates comprehensive build summary
- Shows status of all jobs
- Lists tested platforms and Node versions

**Matrix Strategy:** Tests on 6 combinations (3 OS × 2 Node versions)

---

### 2. VSCode Extension Release (`vscode-extension-release.yml`)

**Triggers:**
- Push tags matching `vscode-v*.*.*` (e.g., `vscode-v0.1.0`)
- Manual workflow dispatch with version input

**Purpose:** Create releases and publish to marketplaces

**Jobs:**

#### `validate-version`
- Extracts version from tag or input
- Validates version format (X.Y.Z)
- Checks package.json version matches

#### `build-release`
- **Platforms:** Ubuntu, Windows, macOS
- Builds release artifacts for each platform
- Creates platform-specific VSIX files
- Uploads artifacts with 90-day retention

#### `create-github-release`
- Downloads all platform artifacts
- Generates release notes from CHANGELOG
- Creates GitHub release with:
  - Version tag
  - Release notes
  - Platform-specific VSIX files
  - Installation instructions

#### `publish-marketplace`
- **Condition:** Manual dispatch with `publish_marketplace=true` and `VSCE_PAT` secret set
- Publishes to VSCode Marketplace
- Uses vsce CLI with Personal Access Token
- Provides success notification with marketplace link

#### `publish-open-vsx`
- **Condition:** Manual dispatch with `publish_marketplace=true` and `OPEN_VSX_TOKEN` secret set
- Publishes to Open VSX Registry
- Alternative marketplace for VSCodium and other editors

#### `release-summary`
- Generates comprehensive release summary
- Shows status of all publishing steps
- Provides links to release and documentation

---

### 3. VSCode Extension Package (`vscode-extension-package.yml`)

**Triggers:**
- Pull requests to `main` or `develop`
- Manual workflow dispatch

**Purpose:** Package extension for PR review

**Jobs:**

#### `package-extension`
- Creates VSIX package for the PR
- Uploads as artifact (30-day retention)
- Comments on PR with:
  - Package details (size, version)
  - Installation instructions
  - Testing guidelines
- Names artifact with PR number for easy identification

#### `analyze-bundle`
- Analyzes production dependencies
- Checks for security vulnerabilities
- Reports bundle size and file counts
- Lists largest compiled files
- Provides insights for optimization

---

## Setup Instructions

### Prerequisites

1. **Node.js and npm:** Installed in CI environment (handled by workflow)
2. **GitHub Secrets:** Configure for publishing

### Required GitHub Secrets

#### For VSCode Marketplace Publishing

1. **Create Personal Access Token:**
   ```bash
   # Visit: https://dev.azure.com/
   # Create token with Marketplace > Manage permission
   ```

2. **Add to GitHub Secrets:**
   - Name: `VSCE_PAT`
   - Value: Your Azure DevOps PAT

#### For Open VSX Publishing

1. **Create Access Token:**
   ```bash
   # Visit: https://open-vsx.org/user-settings/tokens
   # Create new token
   ```

2. **Add to GitHub Secrets:**
   - Name: `OPEN_VSX_TOKEN`
   - Value: Your Open VSX token

### Configuring Secrets

```bash
# Using GitHub CLI
gh secret set VSCE_PAT --body "your-azure-pat"
gh secret set OPEN_VSX_TOKEN --body "your-openvsx-token"

# Or through GitHub UI:
# Settings → Secrets and variables → Actions → New repository secret
```

---

## Usage Guide

### Running CI on Pull Requests

CI runs automatically when:
1. You open a PR that modifies `vscode-extension/`
2. You push commits to an open PR

**What to check:**
- Build status badge on PR
- Compilation errors in logs
- Security scan results
- Package artifact in workflow run

### Creating a Release

#### Method 1: Using Git Tags

```bash
# Update version in package.json first
cd vscode-extension
npm version patch  # or minor, major

# Push tag to trigger release
git push origin vscode-v0.1.0
```

#### Method 2: Manual Workflow Dispatch

1. Go to **Actions** tab in GitHub
2. Select **VSCode Extension Release** workflow
3. Click **Run workflow**
4. Fill in:
   - Version number (e.g., `0.1.0`)
   - Check "Publish to marketplace" if ready
5. Click **Run workflow**

### Publishing to Marketplaces

**Important:** Only publish stable, tested versions!

1. Ensure version in `package.json` is correct
2. Update `CHANGELOG.md` with changes
3. Run release workflow with `publish_marketplace=true`
4. Verify secrets are configured
5. Monitor workflow for success

**Timeline:**
- GitHub Release: Immediate
- VSCode Marketplace: 5-10 minutes review
- Open VSX: Usually immediate

### Downloading Build Artifacts

**From Pull Request:**
1. Go to PR → Checks tab
2. Find "VSCode Extension Package" workflow
3. Scroll to "Artifacts" section
4. Download `extension-package-pr{number}`

**From Release:**
1. Go to Releases page
2. Find your version
3. Download platform-specific VSIX

---

## Workflow Customization

### Modifying Build Matrix

Edit `vscode-extension-ci.yml`:

```yaml
strategy:
  matrix:
    os: [ubuntu-latest, windows-latest, macos-latest]
    node-version: [18.x, 20.x]
    # Add more combinations as needed
```

### Adding Tests

When you add tests to the extension:

```yaml
- name: Run tests
  working-directory: vscode-extension
  run: npm test
```

### Changing Retention Periods

Adjust artifact retention in workflow files:

```yaml
- uses: actions/upload-artifact@v4
  with:
    retention-days: 30  # Change as needed
```

---

## Troubleshooting

### Build Failures

**Compilation errors:**
```bash
# Test locally first
cd vscode-extension
npm run compile
```

**Dependency issues:**
```bash
# Clear and reinstall
rm -rf node_modules package-lock.json
npm install
```

### Publishing Failures

**Marketplace rejection:**
- Check extension size (must be < 50MB)
- Validate `package.json` completeness
- Ensure README has screenshots
- Verify publisher name is registered

**Token expiration:**
- Regenerate tokens in respective portals
- Update GitHub secrets
- Re-run workflow

### Artifact Access

**Can't download artifact:**
- Check if you're signed into GitHub
- Verify workflow completed successfully
- Ensure artifact hasn't expired

---

## Best Practices

### Version Management

1. **Semantic Versioning:**
   - MAJOR: Breaking changes
   - MINOR: New features
   - PATCH: Bug fixes

2. **Update Checklist:**
   - [ ] Update `package.json` version
   - [ ] Update `CHANGELOG.md`
   - [ ] Commit changes
   - [ ] Create git tag
   - [ ] Push tag to trigger release

### Before Publishing

- [ ] Test extension manually
- [ ] Review CHANGELOG
- [ ] Check artifact size
- [ ] Verify all platforms build successfully
- [ ] Test on different VS Code versions
- [ ] Review security scan results

### Release Notes

Write clear, user-focused release notes:
- What changed (user perspective)
- New features with examples
- Bug fixes with context
- Breaking changes clearly marked
- Migration instructions if needed

---

## Workflow Status Badges

Add to your README:

```markdown
[![VSCode Extension CI](https://github.com/flamingquaks/promptrek/actions/workflows/vscode-extension-ci.yml/badge.svg)](https://github.com/flamingquaks/promptrek/actions/workflows/vscode-extension-ci.yml)
```

---

## Support

**Issues with workflows:**
- Check workflow logs in Actions tab
- Review this documentation
- Open issue in repository

**Publishing questions:**
- VSCode Marketplace: https://code.visualstudio.com/api/working-with-extensions/publishing-extension
- Open VSX: https://github.com/eclipse/openvsx/wiki/Publishing-Extensions

---

## Future Enhancements

Planned improvements to workflows:

- [ ] Automated E2E testing
- [ ] Performance benchmarking
- [ ] Screenshot generation for marketplace
- [ ] Automated changelog generation
- [ ] Integration with semantic-release
- [ ] Automated dependency updates (Dependabot)
- [ ] Beta/pre-release channels
- [ ] Telemetry and usage analytics setup
