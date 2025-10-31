# Release Guide for PrompTrek VSCode Extension

This guide walks through the process of releasing a new version of the PrompTrek VSCode extension.

## Pre-Release Checklist

### 1. Testing

- [ ] **Manual Testing**
  - Test all commands in Command Palette
  - Verify tree views display correctly
  - Test context menus
  - Verify status bar updates
  - Test with various PrompTrek configurations
  - Test variable overrides
  - Test plugin generation

- [ ] **Cross-Platform Testing**
  - Test on Windows (or verify CI passes)
  - Test on macOS (or verify CI passes)
  - Test on Linux (or verify CI passes)

- [ ] **Edge Cases**
  - No configuration file present
  - Invalid YAML configuration
  - Missing PrompTrek CLI
  - Large configuration files
  - Multiple workspace folders

- [ ] **Integration Testing**
  - Test with PrompTrek v0.6.0
  - Verify all schema versions work (v1, v2.x, v3.x)
  - Test with different editors (Copilot, Cursor, Claude, etc.)

### 2. Documentation

- [ ] Update `CHANGELOG.md` with:
  - New features
  - Bug fixes
  - Breaking changes
  - Migration notes (if any)

- [ ] Update `README.md` if needed:
  - New features documented
  - Screenshots updated (if UI changed)
  - Installation instructions accurate
  - Configuration examples current

- [ ] Update `package.json`:
  - Increment version number
  - Update dependencies if needed
  - Verify publisher, repository, and metadata

### 3. Code Quality

- [ ] Run linter: `npm run lint`
- [ ] Fix all linting errors
- [ ] Compile successfully: `npm run compile`
- [ ] No console.log statements in production code
- [ ] Remove unused imports
- [ ] Update comments and JSDoc

### 4. Security

- [ ] Run `npm audit`
- [ ] Fix critical and high vulnerabilities
- [ ] Review dependency changes
- [ ] No secrets or tokens in code

## Release Process

### Step 1: Update Version

Choose the appropriate version bump:
- **Patch (0.1.0 → 0.1.1)**: Bug fixes only
- **Minor (0.1.0 → 0.2.0)**: New features, backward compatible
- **Major (0.1.0 → 1.0.0)**: Breaking changes

```bash
cd vscode-extension

# Update version
npm version patch  # or minor, major

# This will:
# 1. Update package.json version
# 2. Create a git commit
# 3. Create a git tag
```

Or manually:
```bash
# Edit package.json
vim package.json  # Change version field

# Commit
git add package.json
git commit -m "chore(vscode): bump version to 0.1.1"
```

### Step 2: Update Changelog

Edit `CHANGELOG.md`:

```markdown
## [0.1.1] - 2025-01-15

### Added
- Feature X that does Y

### Fixed
- Bug Z that caused issue

### Changed
- Improved performance of feature A
```

### Step 3: Commit and Tag

```bash
# If you used npm version, tag is already created
# Otherwise:
git add CHANGELOG.md
git commit -m "chore(vscode): prepare release 0.1.1"
git tag vscode-v0.1.1
```

### Step 4: Push to GitHub

```bash
# Push commits
git push origin your-branch-name

# Push tags
git push origin vscode-v0.1.1
```

### Step 5: Monitor Release Workflow

1. Go to **Actions** tab in GitHub
2. Wait for "VSCode Extension Release" workflow to complete
3. Check for any failures in:
   - Build jobs
   - GitHub release creation
   - Publishing (if enabled)

### Step 6: Verify Release

1. **GitHub Release:**
   - Go to Releases page
   - Verify version is present
   - Check all platform VSIX files are attached
   - Review release notes

2. **Download and Test:**
   ```bash
   # Download VSIX from release
   code --install-extension promptrek-vscode-0.1.1-ubuntu-latest.vsix

   # Test in VSCode
   # - Open a workspace
   # - Verify extension loads
   # - Test key features
   ```

### Step 7: Publish to Marketplace (Optional)

**First Time Setup:**

1. **Create Azure DevOps Account:**
   - Visit https://dev.azure.com
   - Sign in with Microsoft account

2. **Create Personal Access Token:**
   - Go to User Settings → Personal Access Tokens
   - Create new token with:
     - Name: "VSCode Marketplace Publishing"
     - Organization: All accessible organizations
     - Scopes: Marketplace → Manage
   - Copy token (you won't see it again!)

3. **Add Token to GitHub Secrets:**
   ```bash
   gh secret set VSCE_PAT --body "your-token-here"
   ```

**Publishing:**

1. Go to **Actions** tab
2. Select **VSCode Extension Release** workflow
3. Click **Run workflow**
4. Fill in:
   - Version: `0.1.1`
   - ✅ Publish to VSCode Marketplace
5. Click **Run workflow**

6. Monitor workflow execution

7. Verify on marketplace (5-10 minutes):
   - https://marketplace.visualstudio.com/search?term=promptrek&target=VSCode

### Step 8: Publish to Open VSX (Optional)

**Setup:**

1. Create account at https://open-vsx.org
2. Generate access token: Settings → Access Tokens
3. Add to GitHub secrets:
   ```bash
   gh secret set OPEN_VSX_TOKEN --body "your-token-here"
   ```

The release workflow will automatically publish to Open VSX if the token is configured.

## Post-Release

### Announce Release

1. **GitHub Discussions:**
   - Create announcement post
   - Highlight key features
   - Thank contributors

2. **Social Media:**
   - Twitter/X
   - LinkedIn
   - Reddit (r/vscode, r/PrompTrek if exists)

3. **Update Documentation:**
   - Update main PrompTrek README
   - Update website if applicable

### Monitor Feedback

- Watch GitHub Issues for bug reports
- Monitor marketplace ratings/reviews
- Check for questions in discussions
- Respond to user feedback

## Rollback Procedure

If critical issues are found:

### Option 1: Unpublish (Marketplace)

```bash
# Install vsce
npm install -g @vscode/vsce

# Unpublish version (use sparingly!)
vsce unpublish flamingquaks.promptrek-vscode@0.1.1
```

⚠️ **Warning:** Unpublishing can frustrate users. Consider hotfix instead.

### Option 2: Hotfix Release

1. Fix the critical bug
2. Bump to patch version (0.1.1 → 0.1.2)
3. Follow release process
4. Communicate clearly about the issue and fix

### Option 3: Delete GitHub Release

1. Go to Releases page
2. Click on problematic release
3. Delete release
4. Optionally delete tag:
   ```bash
   git tag -d vscode-v0.1.1
   git push origin :refs/tags/vscode-v0.1.1
   ```

## Version History

Keep track of releases:

| Version | Date       | Highlights                          |
|---------|------------|-------------------------------------|
| 0.1.0   | 2025-01-XX | Initial release                     |
| 0.1.1   | 2025-01-XX | Bug fixes and improvements          |

## Troubleshooting

### Build Fails

**Issue:** Compilation errors
```bash
# Clear and rebuild
rm -rf out node_modules package-lock.json
npm install
npm run compile
```

### Publishing Fails

**Issue:** "Extension publisher is not registered"
- Register publisher at https://marketplace.visualstudio.com/manage
- Update `publisher` field in package.json

**Issue:** "Token expired"
- Regenerate PAT in Azure DevOps
- Update GitHub secret
- Re-run workflow

**Issue:** "Extension already exists at this version"
- Bump version number
- Ensure package.json version is unique

### Size Too Large

**Issue:** Extension exceeds 50MB

1. **Analyze bundle:**
   ```bash
   npm run compile
   du -sh out
   ```

2. **Optimize:**
   - Remove unused dependencies
   - Use `.vscodeignore` to exclude files
   - Minify if needed

3. **Check .vscodeignore:**
   ```
   out/**/*.map
   src/**
   .vscode-test/**
   **/*.ts
   ```

## Emergency Contacts

- **Extension Issues:** GitHub Issues
- **Marketplace Support:** marketplace@microsoft.com
- **Security Issues:** security@flamingquaks.dev (or appropriate contact)

## References

- [VSCode Extension Publishing](https://code.visualstudio.com/api/working-with-extensions/publishing-extension)
- [vsce CLI Documentation](https://github.com/microsoft/vscode-vsce)
- [Open VSX Publishing](https://github.com/eclipse/openvsx/wiki/Publishing-Extensions)
- [Semantic Versioning](https://semver.org/)
- [PrompTrek Documentation](https://flamingquaks.github.io/promptrek)
