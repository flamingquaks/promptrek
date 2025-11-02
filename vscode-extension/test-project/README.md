# Test Project for PrompTrek VSCode Extension

This folder contains a test `.promptrek.yaml` file for testing the VSCode extension.

## Quick Start

1. In the **Extension Development Host** window (the one that opened when you pressed F5):
   - File → Open Folder...
   - Navigate to this `test-project` folder
   - Click Open

2. You should see:
   - PrompTrek icon in the Activity Bar (left sidebar)
   - Configuration tree view when you click it
   - Supported editors list

3. Try some commands:
   - Press `Ctrl+Shift+P` (or `Cmd+Shift+P`)
   - Type "PrompTrek"
   - Try different commands!

## What to Test

- ✅ View configuration in sidebar
- ✅ Generate for an editor (e.g., Cursor, Copilot)
- ✅ Validate the configuration
- ✅ Preview output
- ✅ Check status bar shows PrompTrek info
- ✅ Right-click on `project.promptrek.yaml` for context menu

## Expected Behavior

After generating for an editor, you'll see new files/folders created:
- `.cursor/` - If you generated for Cursor
- `.github/copilot-instructions.md` - If you generated for GitHub Copilot
- `.claude/CLAUDE.md` - If you generated for Claude Code
- etc.

Have fun testing! 🎉
