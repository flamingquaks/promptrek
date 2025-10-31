#!/bin/bash
#
# Extension Setup Test Script
# Run this to diagnose F5 issues
#

set +e  # Don't exit on errors, we want to see all checks

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}======================================${NC}"
echo -e "${BLUE}VSCode Extension Setup Diagnostic${NC}"
echo -e "${BLUE}======================================${NC}"
echo ""

# Track if we have any failures
FAILURES=0

# Check 1: Directory
echo -e "${BLUE}[1] Checking directory...${NC}"
if [ -f "package.json" ] && [ -f "tsconfig.json" ]; then
    echo -e "${GREEN}✅ Correct directory${NC}"
    echo "   $(pwd)"
else
    echo -e "${RED}❌ Wrong directory!${NC}"
    echo "   You must run this from vscode-extension/ directory"
    FAILURES=$((FAILURES + 1))
fi
echo ""

# Check 2: Package.json
echo -e "${BLUE}[2] Checking package.json...${NC}"
if [ -f "package.json" ]; then
    MAIN=$(node -e "console.log(require('./package.json').main)" 2>&1)
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ package.json valid${NC}"
        echo "   Main entry: $MAIN"
    else
        echo -e "${RED}❌ package.json has errors${NC}"
        FAILURES=$((FAILURES + 1))
    fi
else
    echo -e "${RED}❌ package.json not found${NC}"
    FAILURES=$((FAILURES + 1))
fi
echo ""

# Check 3: node_modules
echo -e "${BLUE}[3] Checking dependencies...${NC}"
if [ -d "node_modules" ]; then
    echo -e "${GREEN}✅ node_modules exists${NC}"
    COUNT=$(ls node_modules | wc -l)
    echo "   $COUNT packages installed"
else
    echo -e "${RED}❌ node_modules missing${NC}"
    echo "   Run: npm install"
    FAILURES=$((FAILURES + 1))
fi
echo ""

# Check 4: Compilation
echo -e "${BLUE}[4] Checking compiled output...${NC}"
if [ -f "out/extension.js" ]; then
    SIZE=$(ls -lh out/extension.js | awk '{print $5}')
    echo -e "${GREEN}✅ Extension compiled${NC}"
    echo "   out/extension.js ($SIZE)"

    # Count compiled files
    JS_COUNT=$(find out -name "*.js" 2>/dev/null | wc -l)
    echo "   Total JS files: $JS_COUNT"
else
    echo -e "${RED}❌ Extension not compiled${NC}"
    echo "   Run: npm run compile"
    FAILURES=$((FAILURES + 1))
fi
echo ""

# Check 5: VSCode configs
echo -e "${BLUE}[5] Checking VSCode configuration...${NC}"
if [ -f ".vscode/launch.json" ]; then
    echo -e "${GREEN}✅ launch.json exists${NC}"
else
    echo -e "${RED}❌ .vscode/launch.json missing${NC}"
    FAILURES=$((FAILURES + 1))
fi

if [ -f ".vscode/tasks.json" ]; then
    echo -e "${GREEN}✅ tasks.json exists${NC}"
else
    echo -e "${RED}❌ .vscode/tasks.json missing${NC}"
    FAILURES=$((FAILURES + 1))
fi
echo ""

# Check 6: Icons
echo -e "${BLUE}[6] Checking media files...${NC}"
if [ -f "media/logo.png" ]; then
    echo -e "${GREEN}✅ logo.png exists${NC}"
else
    echo -e "${YELLOW}⚠️  logo.png missing${NC}"
fi

if [ -f "media/icons/logo.svg" ]; then
    echo -e "${GREEN}✅ media/icons/logo.svg exists${NC}"
else
    echo -e "${YELLOW}⚠️  media/icons/logo.svg missing (may cause sidebar icon issues)${NC}"
fi
echo ""

# Check 7: TypeScript config
echo -e "${BLUE}[7] Checking TypeScript configuration...${NC}"
if [ -f "tsconfig.json" ]; then
    echo -e "${GREEN}✅ tsconfig.json exists${NC}"
else
    echo -e "${RED}❌ tsconfig.json missing${NC}"
    FAILURES=$((FAILURES + 1))
fi
echo ""

# Summary
echo -e "${BLUE}======================================${NC}"
if [ $FAILURES -eq 0 ]; then
    echo -e "${GREEN}✅ All checks passed!${NC}"
    echo ""
    echo -e "${GREEN}Ready to run the extension:${NC}"
    echo "1. Open this folder in VSCode: code ."
    echo "2. Press F5 to launch Extension Development Host"
    echo ""
    echo -e "${YELLOW}If F5 still doesn't work:${NC}"
    echo "- Close all VSCode windows"
    echo "- Run: code ."
    echo "- Wait for VSCode to fully load"
    echo "- Press F5"
    echo "- Check the Debug Console for errors"
else
    echo -e "${RED}❌ Found $FAILURES issue(s)${NC}"
    echo ""
    echo -e "${YELLOW}To fix:${NC}"
    if [ ! -d "node_modules" ]; then
        echo "  npm install"
    fi
    if [ ! -f "out/extension.js" ]; then
        echo "  npm run compile"
    fi
    echo ""
    echo "Then run this script again to verify"
fi
echo -e "${BLUE}======================================${NC}"

exit $FAILURES
