# VSCode Extension Debugging Guide

## What to check when F5 doesn't work

Let me help you debug step by step. Run these commands and tell me what you see:

### 1. Verify you're in the right directory
```bash
pwd
# Should show: .../promptrek/vscode-extension
```

### 2. Check if extension is compiled
```bash
ls out/extension.js
# Should show the file exists
```

### 3. Check VSCode configuration
```bash
ls .vscode/launch.json .vscode/tasks.json
# Both files should exist
```

### 4. Try compiling again
```bash
npm run compile
# Should complete without errors
```

### 5. Check for errors in VSCode

When you press F5, VSCode should show output in several places:

**Terminal Panel:**
- Look for "Starting compilation" or task output
- Check for any red error messages

**Debug Console:**
- View → Debug Console
- Look for error messages

**Output Panel:**
- View → Output
- Select "Tasks" from dropdown
- Look for compilation errors

**Developer Tools:**
- Help → Toggle Developer Tools (in the Extension Development Host window)
- Check Console tab for errors

## What error messages do you see?

Please share:
1. What happens when you press F5?
2. Any error messages in Terminal, Debug Console, or Output?
3. Does a new window open at all?
4. What's in VSCode's bottom status bar when you press F5?

## Try this diagnostic command

```bash
cd vscode-extension

# Check setup
echo "=== Checking setup ==="
echo "Directory: $(pwd)"
echo ""

echo "=== package.json exists? ==="
ls -lh package.json
echo ""

echo "=== Extension entry point ==="
node -e "console.log('Main:', require('./package.json').main)"
echo ""

echo "=== Extension.js exists? ==="
ls -lh out/extension.js 2>&1 || echo "NOT FOUND - Run: npm run compile"
echo ""

echo "=== VSCode configs exist? ==="
ls -lh .vscode/launch.json .vscode/tasks.json 2>&1 || echo "Missing VSCode configs"
echo ""

echo "=== Icon files exist? ==="
ls -lh media/logo.png media/icons/logo.svg 2>&1 || echo "Some icons missing"
echo ""

echo "=== Node modules installed? ==="
ls -ld node_modules 2>&1 || echo "Run: npm install"
```

Run this and paste the output!
