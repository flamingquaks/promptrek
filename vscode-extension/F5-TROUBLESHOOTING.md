# F5 Troubleshooting Guide

## ✅ Setup is Correct

If you ran `./test-setup.sh` and all checks passed, your setup is correct!

## 📋 Exact Steps to Run Extension

### Step 1: Close ALL VSCode Windows
```bash
# Close every VSCode window completely
# Make sure no VSCode instances are running
```

### Step 2: Open ONLY the Extension Folder
```bash
cd /path/to/promptrek/vscode-extension  # Full path to vscode-extension folder
code .
```

**CRITICAL:** You must open `vscode-extension/` folder, NOT the parent `promptrek/` folder!

### Step 3: Wait for VSCode to Load
- Wait until VSCode fully loads
- Check bottom status bar says "Extension Host"
- TypeScript and ESLint should finish initializing

### Step 4: Open Run & Debug Panel
- Click the Run icon in the left sidebar (bug icon)
- OR press `Ctrl+Shift+D` (Cmd+Shift+D on Mac)
- You should see "Run Extension" in the dropdown

### Step 5: Press F5 (or click the green play button)

## ✅ What SHOULD Happen

When F5 works correctly, you'll see:

1. **Terminal shows task output:**
   ```
   > Executing task: npm run watch <

   > promptrek-vscode@0.1.0 watch
   > tsc -watch -p ./

   Starting compilation in watch mode...
   ```

2. **New window opens:**
   - Title bar shows: **[Extension Development Host]**
   - This is a separate VSCode window for testing

3. **In the Extension Development Host window:**
   - Status bar says "Extension Host"
   - Your extension is now active

4. **To verify it's working:**
   - Press `Ctrl+Shift+P` in the Extension Development Host
   - Type "PrompTrek"
   - You should see PrompTrek commands listed

## ❌ What If Nothing Happens?

### Scenario 1: F5 Does Nothing At All

**Cause:** Wrong folder open, or no debug configuration found

**Fix:**
```bash
# Close VSCode completely
cd vscode-extension
code .
# Wait for full load, then press F5
```

### Scenario 2: Task Error Appears

**Error message:** `"preLaunchTask 'npm: watch' terminated with exit code 1"`

**Fix:**
```bash
npm run compile
# If errors appear, fix TypeScript errors first
# Then press F5 again
```

### Scenario 3: "Extension not found" or "Cannot activate"

**Cause:** Extension compiled incorrectly or main entry point wrong

**Fix:**
```bash
# Clean rebuild
rm -rf out node_modules
npm install
npm run compile
# Restart VSCode, then press F5
```

### Scenario 4: Window Opens But Extension Not Active

**Symptoms:** Extension Development Host opens, but no PrompTrek icon/commands

**Debugging:**
1. In Extension Development Host, press `Ctrl+Shift+I` (open DevTools)
2. Check Console tab for errors
3. Look for activation errors

**Common issues:**
- Icon file missing → Check `media/icons/logo.svg` exists
- Extension crashed on activation → Check console for stack trace

## 🔍 Checking Debug Output

### Debug Console (Original VSCode Window)
- View → Debug Console
- Shows extension host output
- Look for activation messages or errors

### Output Panel (Extension Development Host)
- View → Output
- Select "Extension Host" from dropdown
- Shows runtime errors

### Developer Tools (Extension Development Host)
- Help → Toggle Developer Tools
- Console tab shows JavaScript errors
- Look for red error messages

## 📊 Expected Console Output

When working correctly, you should see:
```
PrompTrek extension is now active
```

In the Debug Console of the original window.

## 🧪 Test If Extension Is Active

Run this in Extension Development Host:

1. Open Command Palette: `Ctrl+Shift+P`
2. Type: `PrompTrek`
3. You should see commands like:
   - PrompTrek: Initialize Configuration
   - PrompTrek: Generate for Editor...
   - PrompTrek: Validate Configuration
   - etc.

If you see these, the extension IS working!

## 🎯 Common User Mistakes

### Mistake #1: Wrong Workspace
```bash
# ❌ WRONG - Opens parent folder
cd promptrek
code .

# ✅ RIGHT - Opens extension folder
cd promptrek/vscode-extension
code .
```

### Mistake #2: Multiple Folders Open
If you have a multi-folder workspace open, VSCode might be confused about which folder to use.

**Fix:** Close workspace, open ONLY vscode-extension folder

### Mistake #3: Not Waiting for TypeScript
If you press F5 immediately after opening VSCode, TypeScript might still be initializing.

**Fix:** Wait 5-10 seconds after opening, until status bar shows TypeScript is ready

### Mistake #4: Old VSCode Version
Extension requires VSCode 1.85.0 or higher.

**Check version:** Help → About

## 🆘 Last Resort: Complete Reset

If nothing works:

```bash
# 1. Close ALL VSCode windows

# 2. Clean everything
cd vscode-extension
rm -rf node_modules out .vscode-test

# 3. Reinstall
npm install

# 4. Recompile
npm run compile

# 5. Verify setup
./test-setup.sh

# 6. Open fresh
code .

# 7. Wait 10 seconds

# 8. Press F5
```

## 📸 What I Need to Help You

If it's still not working, tell me:

1. **What happens when you press F5?**
   - Nothing?
   - Error message? (exact text)
   - Window opens but extension not active?

2. **Check Terminal output:**
   - What appears in the Terminal panel?
   - Any red error messages?

3. **Check Debug Console:**
   - View → Debug Console
   - What messages appear?
   - Any errors in red?

4. **Which folder did you open?**
   ```bash
   pwd  # Run this in VSCode terminal
   ```
   Should show: `.../promptrek/vscode-extension`

5. **Run diagnostics:**
   ```bash
   ./test-setup.sh
   ```
   Share the output

## 💡 Pro Tips

### Tip 1: Use Watch Mode
Instead of F5, you can:
```bash
# Terminal 1: Run watch mode
npm run watch

# Then press F5 to launch
# Changes auto-compile as you edit
```

### Tip 2: Faster Reload
After making changes:
- In Extension Development Host, press `Ctrl+R` (Cmd+R on Mac)
- Faster than stopping and restarting with F5

### Tip 3: Check Extension Host Log
- In Extension Development Host
- Help → Toggle Developer Tools
- Network tab can show if files are loading

### Tip 4: Verbose Logging
Add to your launch.json args:
```json
"args": [
  "--extensionDevelopmentPath=${workspaceFolder}",
  "--log=debug"
]
```

## ✅ Success Checklist

Extension is working if you can:

- [ ] See "Extension Development Host" in title bar
- [ ] Find PrompTrek icon in Activity Bar (left sidebar)
- [ ] Run PrompTrek commands from Command Palette
- [ ] See "PrompTrek extension is now active" in Debug Console
- [ ] View → Output → "PrompTrek" channel exists
- [ ] No errors in JavaScript console (DevTools)

If you can check all these boxes, it's working!
