# Quick Start Guide for GitHub Actions Workflows

This is a quick reference for developers working with the PrompTrek VSCode extension CI/CD workflows.

## 🚀 Common Tasks

### Running CI on Your PR

**Automatic:** CI runs automatically when you:
- Open a PR to `main` or `develop`
- Push commits to an open PR
- Modify files in `vscode-extension/`

**What happens:**
1. Code is linted and compiled
2. Extension is packaged on 3 platforms
3. Security scan runs
4. VSIX artifact is created
5. Comment is posted on your PR

**Check status:**
- Look for green checkmark on your PR
- Click "Details" to see logs
- Download VSIX from "Artifacts" section

### Creating a Release

#### Quick Method (Recommended)

```bash
# 1. Update version in package.json
cd vscode-extension
vim package.json  # Change "version" field

# 2. Update CHANGELOG.md
vim CHANGELOG.md  # Add your changes under new version

# 3. Commit and tag
git add package.json CHANGELOG.md
git commit -m "chore(vscode): prepare release v0.1.1"
git tag vscode-v0.1.1

# 4. Push
git push origin your-branch-name
git push origin vscode-v0.1.1
```

#### What Happens Next

1. GitHub Actions detects the tag
2. Builds VSIX for all platforms (5-10 min)
3. Creates GitHub release automatically
4. Attaches VSIX files to release
5. Generates release notes from CHANGELOG

### Publishing to Marketplace

**First time setup:**

```bash
# Add your VSCode Marketplace token
gh secret set VSCE_PAT --body "your-azure-devops-pat"

# Add your Open VSX token (optional)
gh secret set OPEN_VSX_TOKEN --body "your-openvsx-token"
```

**To publish:**

1. Go to GitHub Actions tab
2. Select "VSCode Extension Release"
3. Click "Run workflow"
4. Enter version (e.g., `0.1.1`)
5. Check "Publish to VSCode Marketplace"
6. Click "Run workflow"

**Wait 5-10 minutes** for marketplace review and publication.

### Testing a PR Package Locally

```bash
# 1. Go to PR → Checks → Artifacts
# 2. Download "extension-package-pr{number}.zip"
# 3. Extract and install:
unzip extension-package-pr123.zip
code --install-extension promptrek-vscode-*.vsix
```

## 📋 Workflow Summary

| Workflow | Trigger | Purpose | Duration |
|----------|---------|---------|----------|
| **CI** | Push/PR | Validate code | 5-8 min |
| **Package** | PR | Create reviewable VSIX | 3-5 min |
| **Release** | Tag `vscode-v*` | Create GitHub release | 8-12 min |

## 🔍 Checking Workflow Status

### On Pull Request
```
✅ VSCode Extension CI (Required)
✅ VSCode Extension Package
```

### On Tag Push
```
✅ VSCode Extension Release
  ├── ✅ Build (Ubuntu)
  ├── ✅ Build (Windows)
  ├── ✅ Build (macOS)
  ├── ✅ Create GitHub Release
  └── ⏩ Publish Marketplace (if enabled)
```

## 🛠️ Troubleshooting

### Build Fails

**Compilation error:**
```bash
cd vscode-extension
npm run compile
# Fix errors, then push again
```

**Linting error:**
```bash
npm run lint
# Fix warnings/errors
```

### Release Fails

**Version mismatch:**
- Ensure `package.json` version matches git tag
- Tag format: `vscode-v0.1.0` (note the `v`)

**Publishing fails:**
- Check if secrets are set correctly
- Verify tokens haven't expired
- Check marketplace for existing version

### Can't Find Artifact

- Wait for workflow to complete (green checkmark)
- Scroll down to "Artifacts" section in workflow run
- Artifacts expire after 7-30 days depending on workflow

## 📚 More Information

- **Full Documentation:** [WORKFLOWS.md](WORKFLOWS.md)
- **Release Guide:** [../RELEASE.md](../RELEASE.md)
- **Contributing:** [../CONTRIBUTING.md](../CONTRIBUTING.md)

## 💡 Pro Tips

1. **Test locally first:**
   ```bash
   npm run compile && npm run lint
   ```

2. **Check package size before releasing:**
   ```bash
   vsce package
   ls -lh *.vsix
   ```

3. **Use draft releases for testing:**
   - Create release manually on GitHub
   - Mark as "Draft"
   - Test thoroughly before publishing

4. **Version numbering:**
   - Patch (0.1.0 → 0.1.1): Bug fixes
   - Minor (0.1.0 → 0.2.0): New features
   - Major (0.1.0 → 1.0.0): Breaking changes

5. **Always update CHANGELOG:**
   - Users appreciate knowing what changed
   - Makes release notes automatic
   - Good practice for transparency

## 🔐 Security Notes

- **Never commit secrets** to the repository
- **Use GitHub Secrets** for all tokens
- **Rotate tokens** regularly (every 6 months)
- **Limit token permissions** to minimum required

## 🎯 Workflow Triggers

### What triggers CI?
- Any push to branch with vscode-extension changes
- Opening a PR
- Pushing to a PR branch

### What triggers Release?
- Pushing a tag: `vscode-v*.*.*`
- Manual trigger from Actions tab

### What triggers Package?
- Opening/updating a PR to main/develop
- Manual trigger from Actions tab

## 📦 Artifacts Retention

| Artifact | Retention | When Available |
|----------|-----------|----------------|
| CI VSIX | 7 days | Every CI run |
| PR Package | 30 days | Every PR |
| Release VSIX | 90 days | Version releases |

## ✅ Checklist for Contributors

Before pushing:
- [ ] Code compiles without errors
- [ ] Linter passes
- [ ] Manual testing done
- [ ] CHANGELOG updated (if applicable)

Before releasing:
- [ ] Version bumped in package.json
- [ ] CHANGELOG updated with changes
- [ ] All CI checks pass
- [ ] Manual testing completed
- [ ] Documentation updated (if needed)

## 🆘 Need Help?

- **Workflow issues:** Check [WORKFLOWS.md](WORKFLOWS.md)
- **General questions:** Open a GitHub Discussion
- **Bugs:** Open a GitHub Issue
- **Quick questions:** Check existing documentation first

---

**Remember:** The workflows are designed to help you, not hinder you. If something is confusing or broken, please open an issue so we can improve the automation!
