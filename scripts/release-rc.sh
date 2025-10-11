#!/bin/bash

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_error() { echo -e "${RED}ERROR: $1${NC}" >&2; }
print_success() { echo -e "${GREEN}✓ $1${NC}"; }
print_info() { echo -e "${YELLOW}→ $1${NC}"; }
print_rc() { echo -e "${BLUE}RC: $1${NC}"; }

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

# Get current version from pyproject.toml for reference
CURRENT_VERSION=$(grep '^version = ' pyproject.toml | cut -d '"' -f 2)
print_info "Current pyproject.toml version: $CURRENT_VERSION"

# Prompt for RC version
echo ""
echo "Creating Release Candidate (RC)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Enter version for RC (without 'v' prefix or rc suffix):"
echo "Format: MAJOR.MINOR.PATCH (e.g., 1.0.0)"
read -p "Base version: " NEW_BASE_VERSION

# Validate version format
if ! echo "$NEW_BASE_VERSION" | grep -qE '^[0-9]+\.[0-9]+\.[0-9]+$'; then
    print_error "Invalid version format. Please use MAJOR.MINOR.PATCH format (e.g., 1.0.0)"
    exit 1
fi

# Prompt for RC number
echo ""
echo "Enter RC number (e.g., 1 for rc.1, 2 for rc.2):"
read -p "RC number: " RC_NUMBER

# Validate RC number
if ! echo "$RC_NUMBER" | grep -qE '^[0-9]+$'; then
    print_error "Invalid RC number. Please use a number (e.g., 1, 2, 3)"
    exit 1
fi

# Construct full version
NEW_VERSION="${NEW_BASE_VERSION}-rc.${RC_NUMBER}"
TAG_VERSION="v${NEW_VERSION}"

# Confirm release
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Release Candidate Summary:"
echo "  Git tag:         $TAG_VERSION"
echo "  PyPI target:     Test PyPI"
echo "  Note:            No version changes will be committed"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
read -p "Do you want to proceed with this RC tag? (y/N) " -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    print_info "RC release cancelled"
    exit 0
fi

# Get current commit hash for reference
CURRENT_COMMIT=$(git rev-parse --short HEAD)
print_info "Current commit: $CURRENT_COMMIT"

# Create git tag on current commit
print_info "Creating git tag $TAG_VERSION on latest main..."
git tag -a "$TAG_VERSION" -m "Release candidate $RC_NUMBER for version $NEW_BASE_VERSION

Tagged commit: $CURRENT_COMMIT
Target: Test PyPI for validation"
print_success "Created tag $TAG_VERSION"

# Show summary
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
print_rc "Release Candidate $TAG_VERSION prepared!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Next steps:"
echo "  1. Review the tag:"
echo "     $ git show $TAG_VERSION"
echo ""
echo "  2. Push the tag to GitHub (this will trigger Test PyPI release):"
echo "     $ git push origin $TAG_VERSION"
echo ""
echo "  3. After testing on Test PyPI, install with:"
echo "     $ pip install --index-url https://test.pypi.org/simple/ promptrek"
echo ""
echo "To undo this RC tag (if not pushed yet):"
echo "  $ git tag -d $TAG_VERSION"
echo ""
