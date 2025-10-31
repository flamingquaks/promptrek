#!/bin/bash
#
# VSCode Extension Development Helper Script
#
# This script helps you set up and launch the extension for development
#

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}PrompTrek VSCode Extension Dev Helper${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

echo -e "${YELLOW}Current directory:${NC} $SCRIPT_DIR"
echo ""

# Step 1: Check if we're in the right directory
echo -e "${BLUE}[1/5] Checking directory structure...${NC}"
if [ ! -f "package.json" ]; then
    echo -e "${RED}❌ Error: package.json not found!${NC}"
    echo -e "${RED}   Make sure you're running this from the vscode-extension directory${NC}"
    exit 1
fi

if [ ! -f "tsconfig.json" ]; then
    echo -e "${RED}❌ Error: tsconfig.json not found!${NC}"
    exit 1
fi

if [ ! -d "src" ]; then
    echo -e "${RED}❌ Error: src/ directory not found!${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Directory structure looks good${NC}"
echo ""

# Step 2: Check if node_modules exists
echo -e "${BLUE}[2/5] Checking dependencies...${NC}"
if [ ! -d "node_modules" ]; then
    echo -e "${YELLOW}⚠️  node_modules not found. Installing dependencies...${NC}"
    npm install
    echo -e "${GREEN}✅ Dependencies installed${NC}"
else
    echo -e "${GREEN}✅ Dependencies already installed${NC}"
fi
echo ""

# Step 3: Compile TypeScript
echo -e "${BLUE}[3/5] Compiling TypeScript...${NC}"
if npm run compile; then
    echo -e "${GREEN}✅ Compilation successful${NC}"
else
    echo -e "${RED}❌ Compilation failed!${NC}"
    echo -e "${RED}   Fix the TypeScript errors before continuing${NC}"
    exit 1
fi
echo ""

# Step 4: Check compiled output
echo -e "${BLUE}[4/5] Verifying compiled output...${NC}"
if [ ! -d "out" ]; then
    echo -e "${RED}❌ Error: out/ directory not created!${NC}"
    exit 1
fi

if [ ! -f "out/extension.js" ]; then
    echo -e "${RED}❌ Error: out/extension.js not found!${NC}"
    exit 1
fi

FILE_COUNT=$(find out -name "*.js" | wc -l)
echo -e "${GREEN}✅ Found $FILE_COUNT compiled JavaScript files${NC}"
echo ""

# Step 5: Launch VSCode
echo -e "${BLUE}[5/5] Launching VSCode...${NC}"
echo -e "${YELLOW}Opening VSCode in extension directory...${NC}"
echo ""
echo -e "${GREEN}📝 Next steps:${NC}"
echo -e "   1. VSCode will open in a moment"
echo -e "   2. Press ${GREEN}F5${NC} to launch the Extension Development Host"
echo -e "   3. A new VSCode window will open with your extension active"
echo -e "   4. Test your extension in that window"
echo ""
echo -e "${YELLOW}💡 Tips:${NC}"
echo -e "   - Run ${GREEN}npm run watch${NC} in a terminal for auto-recompilation"
echo -e "   - Press ${GREEN}Ctrl+R${NC} in the Extension Development Host to reload changes"
echo -e "   - Check Output → 'PrompTrek' for logs"
echo -e "   - See DEVELOPMENT.md for full troubleshooting guide"
echo ""

# Open VSCode in this directory
code .

echo -e "${GREEN}✅ Setup complete! VSCode should be opening now.${NC}"
echo -e "${BLUE}========================================${NC}"
