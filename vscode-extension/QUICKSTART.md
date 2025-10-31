# Quick Start - Running the Extension

## 🚀 Fastest Way to Run

```bash
cd vscode-extension
./dev.sh
# Press F5 when VSCode opens
```

## 📋 Manual Steps

### 1. Open the Extension Folder

**IMPORTANT:** You must open `vscode-extension/` as your workspace root, not the parent `promptrek/` folder.

```bash
cd vscode-extension
code .
```

### 2. Install & Compile

```bash
npm install
npm run compile
```

### 3. Launch Extension

- Press **F5** in VSCode
- Or click Run → Start Debugging
- Or press the green play button in the debug panel

### 4. Test in the New Window

A new window will open titled **[Extension Development Host]**

In that window:
- Open any folder
- Look for the PrompTrek icon in the sidebar
- Press Ctrl+Shift+P and type "PrompTrek"

## ❌ Common Mistake

**Wrong:** Opening `promptrek/` folder (parent directory)
```bash
cd promptrek  # ❌ Don't do this
code .        # ❌ This won't work
```

**Right:** Opening `vscode-extension/` folder
```bash
cd vscode-extension  # ✅ Do this
code .               # ✅ This works
```

## 🔄 Development Workflow

```bash
# Terminal 1: Run watch mode (auto-compile)
npm run watch

# In VSCode: Press F5 to launch

# After making changes:
# - Reload Extension Development Host: Ctrl+R (Cmd+R on Mac)
```

## 🆘 Troubleshooting

### F5 doesn't work?
→ Make sure you opened `vscode-extension/` folder, not `promptrek/`

### "Cannot find module" error?
→ Run `npm install && npm run compile`

### Changes not appearing?
→ Run `npm run compile` or use `npm run watch`, then reload (Ctrl+R)

### Still stuck?
→ See [DEVELOPMENT.md](DEVELOPMENT.md) for detailed troubleshooting

## ✅ Success Checklist

When it's working correctly, you'll see:

- [ ] New window opens with "[Extension Development Host]" in title
- [ ] PrompTrek icon appears in Activity Bar (left sidebar)
- [ ] Commands appear in Command Palette (Ctrl+Shift+P → "PrompTrek")
- [ ] Output panel shows "PrompTrek extension is now active"

That's it! 🎉
