# Release Scripts

Scripts for managing releases and version tagging.

## release.sh

Creates formal production releases that will be published to PyPI.

### Usage
```bash
./scripts/release.sh
```

### What it does
1. Validates you're on main branch with clean working tree
2. Prompts for new version number (MAJOR.MINOR.PATCH format)
3. Updates version in pyproject.toml
4. Generates/updates CHANGELOG.md using conventional commits
5. Creates a release commit with both changes
6. Creates an annotated git tag (v*.*.*)
7. Provides commands to push to GitHub

### Requirements
- Git repository on main branch
- Clean working tree (no uncommitted changes)
- Node.js (for conventional-changelog-cli)

## release-rc.sh

Creates release candidate tags for testing on Test PyPI without modifying any files.

### Usage
```bash
./scripts/release-rc.sh
```

### What it does
1. Validates you're on main branch with clean working tree
2. Prompts for base version and RC number
3. Creates an annotated git tag (vX.Y.Z-rc.N) on the current commit
4. Provides commands to push the tag to GitHub
5. No files are modified or committed

### Testing RC releases
After pushing an RC tag, the package will be published to Test PyPI. Install with:
```bash
pip install --index-url https://test.pypi.org/simple/ promptrek==X.Y.Z-rc.N
```

## Release Workflow

1. **Development**: Work on features/fixes on feature branches
2. **Release Candidate**: When ready to test:
   - Run `./scripts/release-rc.sh` to create RC
   - Push to GitHub
   - Test from Test PyPI
   - Repeat with new RC numbers as needed
3. **Production Release**: When RC is validated:
   - Run `./scripts/release.sh` to create formal release
   - Push to GitHub
   - Package publishes to PyPI with GitHub release notes

## GitHub Actions Integration

These scripts work with `.github/workflows/release.yml`:
- **RC tags** (vX.Y.Z-rc.N) → Test PyPI only
- **Release tags** (vX.Y.Z) → PyPI + GitHub Release with changelog