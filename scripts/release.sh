#!/bin/bash

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_error() { echo -e "${RED}ERROR: $1${NC}" >&2; }
print_success() { echo -e "${GREEN}✓ $1${NC}"; }
print_info() { echo -e "${YELLOW}→ $1${NC}"; }

# Check if we're on main branch
CURRENT_BRANCH=$(git branch --show-current)
if [ "$CURRENT_BRANCH" != "main" ]; then
    print_error "You must be on the main branch to create a release"
    print_info "Current branch: $CURRENT_BRANCH"
    exit 1
fi

# Check for uncommitted changes
if ! git diff --quiet || ! git diff --cached --quiet; then
    print_error "You have uncommitted changes. Please commit or stash them first."
    git status --short
    exit 1
fi

# Pull latest changes
print_info "Pulling latest changes from origin/main..."
git pull origin main

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    print_error "uv is required but not installed. Please install it first."
    print_info "Visit: https://github.com/astral-sh/uv"
    exit 1
fi

# Get current version from pyproject.toml
CURRENT_VERSION=$(grep '^version = ' pyproject.toml | cut -d '"' -f 2)
print_info "Current version: $CURRENT_VERSION"

# Prompt for new version
echo ""
echo "Enter new version number (without 'v' prefix):"
echo "Format: MAJOR.MINOR.PATCH (e.g., 1.0.0)"
read -p "New version: " NEW_VERSION

# Validate version format
if ! echo "$NEW_VERSION" | grep -qE '^[0-9]+\.[0-9]+\.[0-9]+$'; then
    print_error "Invalid version format. Please use MAJOR.MINOR.PATCH format (e.g., 1.0.0)"
    exit 1
fi

# Check if this is a downgrade
if [ "$NEW_VERSION" = "$CURRENT_VERSION" ]; then
    print_error "New version is the same as current version"
    exit 1
fi

# Confirm release
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Release Summary:"
echo "  Current version: $CURRENT_VERSION"
echo "  New version:     $NEW_VERSION"
echo "  Git tag:         v$NEW_VERSION"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
read -p "Do you want to proceed with this release? (y/N) " -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    print_info "Release cancelled"
    exit 0
fi

# Update version in pyproject.toml
print_info "Updating version in pyproject.toml..."
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    sed -i '' "s/^version = \".*\"/version = \"$NEW_VERSION\"/" pyproject.toml
else
    # Linux
    sed -i "s/^version = \".*\"/version = \"$NEW_VERSION\"/" pyproject.toml
fi
print_success "Updated pyproject.toml"

# Update lock file with new version
print_info "Updating uv.lock with new version..."
if ! uv lock; then
    print_error "Failed to update uv.lock"
    exit 1
fi
print_success "Updated uv.lock"

# Check if conventional-changelog is installed
if ! command -v conventional-changelog &> /dev/null; then
    print_info "Installing conventional-changelog-cli..."
    npm install -g conventional-changelog-cli
fi

# Find the last stable version tag (excluding RC tags)
print_info "Finding last stable version tag..."
LAST_STABLE_TAG=$(git tag -l --sort=-version:refname | grep -E '^v[0-9]+\.[0-9]+\.[0-9]+$' | head -n 1)
if [ -z "$LAST_STABLE_TAG" ]; then
    print_info "No previous stable version found, generating full changelog"
    LAST_STABLE_TAG=""
else
    print_info "Last stable version: $LAST_STABLE_TAG"
fi

# Temporarily hide RC tags so conventional-changelog only sees stable versions
RC_TAGS=$(git tag -l | grep -E '^v[0-9]+\.[0-9]+\.[0-9]+-rc\.[0-9]+$')
if [ -n "$RC_TAGS" ]; then
    print_info "Temporarily hiding RC tags for changelog generation..."
    while IFS= read -r tag; do
        git tag "_backup_$tag" "$tag" 2>/dev/null || true
        git tag -d "$tag" 2>/dev/null || true
    done <<< "$RC_TAGS"
fi

# Generate changelog with the new version
print_info "Generating changelog for version $NEW_VERSION..."
if [ -f CHANGELOG.md ]; then
    # Update existing changelog with new version
    conventional-changelog -p angular -i CHANGELOG.md -s -r 2 --pkg "{\"version\":\"$NEW_VERSION\"}"
else
    # Create new changelog
    conventional-changelog -p angular -o CHANGELOG.md --pkg "{\"version\":\"$NEW_VERSION\"}"
fi

# Restore RC tags
if [ -n "$RC_TAGS" ]; then
    print_info "Restoring RC tags..."
    while IFS= read -r tag; do
        git tag "$tag" "_backup_$tag" 2>/dev/null || true
        git tag -d "_backup_$tag" 2>/dev/null || true
    done <<< "$RC_TAGS"
fi
print_success "Generated changelog"

# Stage changes
print_info "Staging changes..."
git add pyproject.toml uv.lock CHANGELOG.md

# Show what will be committed
echo ""
print_info "Changes to be committed:"
git diff --cached --stat
echo ""

# Create release commit
print_info "Creating release commit..."
git commit -m "release: v$NEW_VERSION

- Update version in pyproject.toml to $NEW_VERSION
- Update uv.lock with new version
- Update CHANGELOG.md with latest changes"
print_success "Created release commit"

# Create git tag
print_info "Creating git tag v$NEW_VERSION..."
git tag -a "v$NEW_VERSION" -m "Release version $NEW_VERSION"
print_success "Created tag v$NEW_VERSION"

# Show summary
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🎉 Release v$NEW_VERSION prepared successfully!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Next steps:"
echo "  1. Review the changes:"
echo "     $ git show HEAD"
echo "     $ git show v$NEW_VERSION"
echo ""
echo "  2. Push to GitHub (this will trigger the release workflow):"
echo "     $ git push origin main"
echo "     $ git push origin v$NEW_VERSION"
echo ""
echo "  3. Or push both at once:"
echo "     $ git push origin main --tags"
echo ""
echo "To undo this release (if not pushed yet):"
echo "  $ git tag -d v$NEW_VERSION"
echo "  $ git reset --hard HEAD~1"
echo ""
