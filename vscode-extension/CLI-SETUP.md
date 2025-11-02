# Installing PrompTrek CLI - Required for Extension

## ⚠️ Important

The VSCode extension is a **graphical wrapper** around the PrompTrek CLI. You need to install the CLI for the extension to work!

## Error You're Seeing

```
Failed to initialize configuration: /bin/sh: promptrek: command not found
```

This means the `promptrek` command is not installed or not in your PATH.

## 🚀 Quick Install (Choose One)

### Option 1: Using uv (Recommended)

```bash
# Install uv if you don't have it
curl -LsSf https://astral.sh/uv/install.sh | sh

# Navigate to the PrompTrek repository
cd promptrek

# Install PrompTrek
uv sync

# The promptrek command is now available via: uv run promptrek
# Or activate the virtual environment:
source .venv/bin/activate  # Unix/Mac
# OR
.venv\Scripts\activate     # Windows

# Verify it works
promptrek --version
```

### Option 2: Using pip (Traditional)

```bash
# Navigate to the PrompTrek repository
cd promptrek

# Install in development mode
pip install -e .

# Verify it works
promptrek --version
```

### Option 3: Using uv with Global Install

```bash
cd promptrek
uv tool install -e .

# Verify it works
promptrek --version
```

## ✅ Verify Installation

After installing, run:

```bash
promptrek --version
# Should output: PrompTrek version 0.6.0 (or similar)

which promptrek
# Should show the path to the command
```

## 🔧 Configure VSCode Extension (If Needed)

If you installed with uv and want to use `uv run promptrek`:

1. In VSCode, open Settings (`Ctrl+,` or `Cmd+,`)
2. Search for "PrompTrek"
3. Find "PrompTrek: Cli Path"
4. Change it to:
   - If using uv: Leave as `promptrek` and activate the venv first
   - If custom location: Enter full path like `/path/to/.venv/bin/promptrek`

## 🎯 After Installation

Once the CLI is installed:

1. **Restart VSCode** (or just reload the Extension Development Host with `Ctrl+R`)
2. Try the command again:
   - Press `Ctrl+Shift+P`
   - Type "PrompTrek: Initialize Configuration"
   - It should work now!

## 🧪 Test the CLI Directly

Before using the extension, verify the CLI works:

```bash
# Test with version
promptrek --version

# Try initializing a config
cd /tmp/test
promptrek init --output test.promptrek.yaml

# If that works, the extension will work too!
```

## 💡 Where to Install From

The PrompTrek CLI is in the parent directory of this extension:

```bash
# If you're in vscode-extension/
cd ..              # Go back to promptrek/
uv sync           # Install PrompTrek
source .venv/bin/activate  # Activate environment (Unix/Mac)
```

## 🆘 Troubleshooting

### "Command not found" even after installing

**Problem:** PrompTrek is installed but not in PATH

**Solution 1 - Activate the virtual environment:**
```bash
cd promptrek
source .venv/bin/activate  # Unix/Mac
.venv\Scripts\activate     # Windows
```

**Solution 2 - Configure extension to use full path:**
1. Find where PrompTrek is installed:
   ```bash
   which promptrek
   # Or if using uv:
   ls .venv/bin/promptrek
   ```
2. Update VSCode settings:
   - Settings → "PrompTrek: Cli Path"
   - Enter the full path: `/full/path/to/.venv/bin/promptrek`

### "Permission denied"

```bash
# Make sure it's executable
chmod +x ~/.local/bin/promptrek
# Or wherever it's installed
```

### Using uv but don't want to activate venv

Configure the extension to use `uv run`:

1. VSCode Settings → "PrompTrek: Cli Path"
2. Change to: `uv run --directory /path/to/promptrek promptrek`

Or create a wrapper script:

```bash
#!/bin/bash
cd /path/to/promptrek
uv run promptrek "$@"
```

Save as `~/bin/promptrek`, make executable, and use that path.

## 📋 Quick Reference

| Installation Method | Command to Use | Path to Configure |
|---------------------|----------------|-------------------|
| `uv sync` + activate venv | `promptrek` | `promptrek` (default) |
| `pip install -e .` | `promptrek` | `promptrek` (default) |
| `uv tool install` | `promptrek` | `promptrek` (default) |
| Custom location | Full path | `/full/path/to/promptrek` |

## ✅ Success!

Once installed, you'll be able to:
- ✅ Initialize new configurations
- ✅ Generate for editors
- ✅ Validate configurations
- ✅ Use all VSCode extension features

The extension just calls the CLI behind the scenes, so if the CLI works in your terminal, it will work in the extension!

---

**Next Steps:**
1. Install PrompTrek CLI (see above)
2. Verify with `promptrek --version`
3. Restart VSCode or reload Extension Development Host (`Ctrl+R`)
4. Try the commands again!
