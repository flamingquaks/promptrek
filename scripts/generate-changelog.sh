#!/bin/bash
# Generate changelog locally for testing
# Usage: ./scripts/generate-changelog.sh [tag]

set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}PrompTrek Changelog Generator${NC}"
echo "==============================="

# Check if conventional-changelog is installed
if ! command -v conventional-changelog &> /dev/null; then
    echo -e "${BLUE}Installing conventional-changelog...${NC}"
    npm install -g conventional-changelog-cli conventional-commits-parser
fi

# Generate changelog
echo -e "${BLUE}Generating changelog...${NC}"
if [ -n "$1" ]; then
    echo "Generating changelog up to tag: $1"
    conventional-changelog -p angular -i CHANGELOG.md -s --tag-prefix "v" --release-count 0
else
    echo "Generating full changelog from git history"
    conventional-changelog -p angular -i CHANGELOG.md -s -r 0
fi

echo -e "${GREEN}Changelog generated successfully!${NC}"
echo "Check CHANGELOG.md for the updated content."

# Show a preview of recent changes
echo ""
echo -e "${BLUE}Recent changelog entries:${NC}"
head -30 CHANGELOG.md
