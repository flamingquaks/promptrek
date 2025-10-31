# Running the VSCode Extension in Development Mode

## The Issue

When you press F5, VSCode needs to know where your extension is. The problem is likely that you're opening the wrong folder in VSCode.

## ✅ Correct Setup (Step-by-Step)

### Option 1: Open Extension Folder Directly (Recommended)

1. **Close all VSCode windows**

2. **Open the extension folder as the workspace:**
   ```bash
   cd vscode-extension
   code .
   ```

   Or from VSCode:
   - File → Open Folder...
   - Navigate to `promptrek/vscode-extension/`
   - Click "Open"

3. **Verify you're in the right place:**
   - Check the bottom-left of VSCode
   - Should show: `VSCODE-EXTENSION` or similar
   - In Explorer, you should see `package.json`, `src/`, `tsconfig.json` at the root

4. **Make sure it's compiled:**
   ```bash
   npm install
   npm run compile
   ```

   You should see an `out/` folder appear

5. **Press F5 to launch:**
   - Select "Run Extension" from the debug dropdown (if prompted)
   - A new VSCode window will open with "[Extension Development Host]" in the title
   - Your extension will be active in this window

### Option 2: Use Workspace File (Alternative)

If you want to develop the extension while keeping the main PrompTrek project open:

1. **Create a VSCode workspace file:**
   ```bash
   cd promptrek
   cat > promptrek-dev.code-workspace << 'EOF'
   {
     "folders": [
       {
         "name": "PrompTrek",
         "path": "."
       },
       {
         "name": "VSCode Extension",
         "path": "vscode-extension"
       }
     ],
     "settings": {}
   }
   EOF
   ```

2. **Open the workspace:**
   ```bash
   code promptrek-dev.code-workspace
   ```

3. **When pressing F5:**
   - Make sure "VSCode Extension" folder is selected in the Explorer
   - Or switch to a file inside vscode-extension/ before pressing F5

## 🔍 Troubleshooting

### "Cannot find module" or "Extension not found"

**Problem:** Wrong workspace folder is open

**Solution:**
```bash
# Close all VSCode windows, then:
cd vscode-extension
code .
```

### "Command not found" when pressing F5

**Problem:** Extension not compiled

**Solution:**
```bash
cd vscode-extension
npm install
npm run compile
ls out/  # Should show compiled .js files
```

### "preLaunchTask 'npm: watch' not found"

**Problem:** Tasks not properly configured or wrong folder open

**Solution:**
```bash
# Make sure you're in vscode-extension folder
cd vscode-extension
code .
# Then press F5
```

### Changes not appearing in Extension Development Host

**Problem:** Extension not recompiled

**Solution:**
```bash
# Option 1: Run watch mode (auto-recompile)
npm run watch

# Option 2: Recompile manually after each change
npm run compile

# Then restart the Extension Development Host (Ctrl+R or Cmd+R in the dev host window)
```

## 📋 Quick Checklist

Before pressing F5, verify:

- [ ] You opened `vscode-extension/` folder (not `promptrek/`)
- [ ] You ran `npm install` in vscode-extension/
- [ ] You ran `npm run compile` successfully
- [ ] The `out/` directory exists and has .js files
- [ ] You see `package.json` at the root in VSCode Explorer
- [ ] The status bar shows the correct folder name

## 🎯 What Should Happen

When F5 works correctly:

1. **Build Task Runs:** You'll see "Starting compilation in watch mode..."
2. **New Window Opens:** Title bar shows "[Extension Development Host]"
3. **Extension Activates:** Check Output → "PrompTrek" channel for activation logs
4. **Sidebar Available:** You should see the PrompTrek icon in the Activity Bar
5. **Commands Work:** Open Command Palette (Ctrl+Shift+P) and type "PrompTrek"

## 🧪 Testing Your Extension

Once the Extension Development Host window opens:

1. **Open a test workspace:**
   - File → Open Folder
   - Open any folder (preferably one with a .promptrek.yaml file)

2. **Check the PrompTrek sidebar:**
   - Click the PrompTrek icon in the Activity Bar (left side)
   - You should see "Configuration" and "Supported Editors" views

3. **Try a command:**
   - Press Ctrl+Shift+P (Cmd+Shift+P on Mac)
   - Type "PrompTrek: Initialize Configuration"
   - Follow the prompts

4. **Check for errors:**
   - View → Output → Select "PrompTrek"
   - View → Developer → Developer Tools (Console tab)

## 🔄 Development Workflow

### Normal Development:

```bash
# 1. Open extension folder
cd vscode-extension
code .

# 2. Start watch mode (optional but recommended)
npm run watch

# 3. Press F5 to launch Extension Development Host

# 4. Make changes to TypeScript files in src/

# 5. Reload the Extension Development Host:
#    - Press Ctrl+R (Cmd+R on Mac) in the Extension Development Host window
#    - Or click the green circular arrow in the debug toolbar
```

### After Making Changes:

- **If watch mode is running:** Just reload the Extension Development Host (Ctrl+R)
- **If not using watch mode:** Run `npm run compile`, then reload

## 📝 Common Development Commands

```bash
# Install dependencies
npm install

# Compile once
npm run compile

# Compile and watch for changes (recommended during dev)
npm run watch

# Lint code
npm run lint

# Package extension
npm install -g @vscode/vsce
vsce package
```

## 🆘 Still Not Working?

### Check the Debug Console

1. In the Extension Development Host window
2. View → Output
3. Select "Extension Host" from the dropdown
4. Look for error messages

### Check the Developer Tools

1. In the Extension Development Host window
2. Help → Toggle Developer Tools
3. Check Console tab for errors

### Verify Extension Package

```bash
cd vscode-extension
node -e "console.log(require('./package.json').main)"
# Should output: ./out/extension.js

ls -la out/extension.js
# Should exist and be recent
```

### Nuclear Option (Clean Rebuild)

```bash
cd vscode-extension
rm -rf node_modules out
npm install
npm run compile
code .
# Now press F5
```

## 📚 Additional Resources

- [VSCode Extension Development](https://code.visualstudio.com/api/get-started/your-first-extension)
- [Debug Extension](https://code.visualstudio.com/api/working-with-extensions/testing-extension)
- [Extension Manifest](https://code.visualstudio.com/api/references/extension-manifest)

## ✅ Success Indicators

You'll know it's working when:

1. ✅ F5 launches without errors
2. ✅ New window opens with "[Extension Development Host]" in title
3. ✅ PrompTrek icon appears in the Activity Bar
4. ✅ PrompTrek commands appear in Command Palette
5. ✅ No errors in Output → "PrompTrek" channel
6. ✅ Console (Developer Tools) shows "PrompTrek extension is now active"

---

**Most Common Fix:** Just open the `vscode-extension` folder directly in VSCode, not the parent `promptrek` folder!
