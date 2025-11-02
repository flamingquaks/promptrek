# Testing the Extension - Quick Guide

## 🎯 You've Launched the Extension Development Host!

Now you need to open a project/folder to test the extension's features.

## Method 1: Test with an Existing PrompTrek Project (Best)

If you have a folder with a `.promptrek.yaml` file:

1. **In the Extension Development Host window** (the new window that opened):
   - File → Open Folder...
   - Navigate to your project with `.promptrek.yaml`
   - Click "Open"

2. **Check if it works:**
   - Look for PrompTrek icon in the Activity Bar (left sidebar)
   - Click it to see your configuration
   - Press `Ctrl+Shift+P` and type "PrompTrek" to see commands

## Method 2: Create a Test Folder (Easiest)

Let's create a quick test project:

### In Your Terminal:

```bash
# Create a test folder
mkdir ~/promptrek-test
cd ~/promptrek-test

# Create a simple test configuration
cat > project.promptrek.yaml << 'EOF'
schema_version: "3.1.0"
metadata:
  title: "Test Project"
  description: "Testing the VSCode extension"
  tags: [test]

content: |
  # Test Project Assistant

  ## Project Details
  This is a test project for the PrompTrek VSCode extension.

  ## Guidelines
  - Write clean code
  - Follow best practices
  - Have fun!

variables:
  PROJECT_NAME: "test-project"
  VERSION: "1.0.0"
EOF

echo "Test project created at ~/promptrek-test"
```

### Then in Extension Development Host:

1. **File → Open Folder...**
2. Navigate to `~/promptrek-test` (or wherever you created it)
3. Click **Open**

## ✅ What You Should See

Once you open a folder with a `.promptrek.yaml` file:

### 1. PrompTrek Sidebar
- Click the PrompTrek icon in Activity Bar (left side)
- You'll see two views:
  - **Configuration** - Shows your config structure
  - **Supported Editors** - Shows which editors are supported

### 2. Explore the Configuration View
Expand the sections to see:
- **Metadata** (title, description, tags)
- **Variables** (PROJECT_NAME, VERSION, etc.)
- **Content** (preview of markdown content)
- **Plugins** (if you have any MCP servers, commands, agents)
- **Documents** (if you have multiple documents)

### 3. Try Some Commands

Press `Ctrl+Shift+P` (or `Cmd+Shift+P` on Mac) and type "PrompTrek":

```
PrompTrek: Initialize Configuration     - Create new config
PrompTrek: Generate for Editor...       - Generate for specific editor
PrompTrek: Generate for All Editors     - Generate for all editors
PrompTrek: Validate Configuration       - Check for errors
PrompTrek: Preview Output...            - Preview what will be generated
PrompTrek: Open Configuration File      - Open .promptrek.yaml
```

### 4. Test the Generate Feature

1. Right-click on `project.promptrek.yaml` in Explorer
2. You should see PrompTrek options in the context menu:
   - **Validate Configuration**
   - **Generate for Editor...**
   - **Generate for All Editors**

3. Try "Generate for Editor..."
   - Select an editor (e.g., "Cursor", "GitHub Copilot", "Claude Code")
   - Watch it generate the editor-specific files!

### 5. Check the Output

After generating:
- Look in your test folder for new files/directories:
  - `.cursor/` folder (if you generated for Cursor)
  - `.github/copilot-instructions.md` (if you generated for Copilot)
  - `.claude/CLAUDE.md` (if you generated for Claude)
  - etc.

## 🎨 What to Test

Here's a checklist of features to try:

### Basic Features
- [ ] PrompTrek icon appears in sidebar
- [ ] Configuration tree view shows your config
- [ ] Editor status view shows all supported editors
- [ ] Commands appear in Command Palette

### Generation Features
- [ ] Generate for a single editor works
- [ ] Generated files appear in correct locations
- [ ] Generate for all editors works
- [ ] Variable overrides during generation

### Validation Features
- [ ] Validate command shows success for valid config
- [ ] Validate shows errors for invalid config (try breaking the YAML)

### Context Menus
- [ ] Right-click on `.promptrek.yaml` shows PrompTrek options
- [ ] Context menu commands work

### Status Bar
- [ ] Status bar shows PrompTrek info (bottom right)
- [ ] Clicking status bar opens config file

## 🧪 Advanced Testing

Want to test more features? Try this advanced config:

```yaml
schema_version: "3.1.0"
metadata:
  title: "Advanced Test"
  description: "Testing all features"
  version: "1.0.0"
  author: "Test User"
  tags: [test, advanced, demo]

content: |
  # Advanced Test Project

  ## Testing Features
  - Multi-document support
  - Plugin configurations
  - Variable substitution

variables:
  PROJECT_NAME: "advanced-test"
  VERSION: "2.0.0"
  API_URL: "https://api.example.com"

# Test with plugins (optional)
mcp_servers:
  - name: test-server
    command: echo
    args: ["Hello from MCP"]
    description: "Test MCP server"

commands:
  - name: test-command
    description: "Test custom command"
    prompt: "This is a test command"

# Test with documents
documents:
  - name: typescript
    content: |
      # TypeScript Guidelines
      - Use strict mode
      - Prefer interfaces
    description: "TypeScript coding standards"
    file_globs: "**/*.ts"
```

Save this as a different file and try opening it!

## 🔍 Debugging the Extension

### Check the Output Panel
- View → Output
- Select "PrompTrek" from dropdown
- You'll see extension logs

### Check the Console
- Help → Toggle Developer Tools
- Console tab shows JavaScript errors
- Network tab shows file loading

### Check Extension Host Output
- View → Output
- Select "Extension Host" from dropdown
- Shows activation messages and errors

## 📸 What Success Looks Like

When everything is working:
1. ✅ PrompTrek icon visible in Activity Bar
2. ✅ Configuration tree shows your config structure
3. ✅ Commands work from Command Palette
4. ✅ Generate creates files in your project
5. ✅ No errors in Output or Console
6. ✅ Context menus show PrompTrek options

## 🎉 You're Testing the Extension!

Now you can:
- Modify the TypeScript code in the original VSCode window
- Press `Ctrl+R` in the Extension Development Host to reload changes
- Test new features immediately
- See errors in Debug Console

## 💡 Tips

1. **Keep both windows visible** - Original VSCode (for coding) + Extension Development Host (for testing)

2. **Use watch mode** - Run `npm run watch` in terminal so changes auto-compile

3. **Quick reload** - Press `Ctrl+R` (Cmd+R on Mac) in Extension Development Host after changes

4. **Check logs** - Always check Output → "PrompTrek" for debug info

5. **Test edge cases** - Try invalid YAML, missing files, etc.

## 🆘 Need Help?

If something doesn't work:
1. Check Output → "PrompTrek" for errors
2. Check Developer Tools Console
3. Check that `.promptrek.yaml` is valid YAML
4. Reload the Extension Development Host (Ctrl+R)

Happy testing! 🚀
