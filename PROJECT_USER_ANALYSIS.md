# GPT Automation - Project Purpose, Features & User Perspective

## What is GPT Automation?

**In one sentence**: A CLI tool that automatically extracts and formats your entire codebase into optimized, LLM-friendly text that's ready to paste into ChatGPT or Claude.

**The Problem It Solves**:
- When you want to ask an AI about your code, you normally copy-paste files manually or painstakingly recreate the structure
- Different projects need different file inclusions (some want tests, some don't; some want docs, some don't)
- Keeping track of what to include/exclude is tedious and error-prone

**The Solution**:
- Define once what files to include/exclude
- Run one command to get everything formatted and on your clipboard
- Works offline, no API calls needed

---

## CLI Commands (What Users Do)

### **Command 1: `autogpt init [profile names]`**

**What the user is trying to do**: Set up the tool for a new project

**Syntax**:
```bash
autogpt init                    # First-time setup, creates defaults
autogpt init cli backend api    # Setup with named profiles
```

**What happens behind the scenes**:
1. Creates `.gpt/` directory in project root
2. Creates default filtering configuration files
3. Loads all plugins and validates they're configured
4. Optionally creates profile-specific directories

**Time to value**: ~1 second
**One-time task**: Yes, do this once per project

**Output**: Creates the `.gpt/` directory structure

---

### **Command 2: `autogpt prompt [profiles] [--dir profiles] [--content profiles]`**

**What the user is trying to do**: Generate a formatted code prompt for AI

**Syntax**:
```bash
# Generate everything (default)
autogpt prompt

# Only directory structure, only file contents
autogpt prompt --dir
autogpt prompt --content

# For specific profiles (different filtering rules)
autogpt prompt --dir cli backend        # Dir for cli+backend, content for default
autogpt prompt --content api            # Content for api profile
autogpt prompt --dir backend --content frontend  # Different profiles for each

# Specify what directory to scan
autogpt prompt --root_dir /path/to/project
autogpt prompt --prompt_dir /path/to/subdir
```

**What happens**:
1. Walks through your project directory
2. Applies filtering rules from `.gptignore`, blacklist, whitelist, include-only
3. Formats output into two sections:
   - Directory tree (shows structure)
   - File contents (shows actual code)
4. Copies to clipboard automatically
5. Displays preview in terminal

**Output example**:
```
Directory Structure:
./
  src/
    main.py
    utils.py
  tests/
    test_main.py
  README.md

File Contents:
==========src/main.py:
[actual file content]

==========src/utils.py:
[actual file content]
```

**Time to value**: ~1 second
**Repeated task**: Yes, users run this many times during development

---

## User Workflow

### **Scenario 1: First Time Setting Up GPT Automation**

```
User: I want to use this tool with my Python backend project

Step 1: cd /my/python/project
Step 2: autogpt init
        → Creates .gpt/ directory with defaults
        → User now has .gptignore, filtering rules, etc.

Step 3: (Optional) Edit .gpt/.gptignore
        → Remove unwanted patterns or add specific ones
        → Example: exclude __pycache__, .pyc files, venv/

Step 4: autogpt prompt
        → Gets entire codebase on clipboard
        → Pastes into Claude/ChatGPT with the prompt
```

**Total time**: 1-3 minutes

---

### **Scenario 2: Different Profiles for Different Purposes**

```
User: My project has backend, frontend, and API docs. I want different prompts for each.

Step 1: autogpt init backend frontend api
        → Creates .gpt/backend/, .gpt/frontend/, .gpt/api/ directories

Step 2: Edit filtering rules
        → .gpt/backend/.gptignore - exclude frontend/
        → .gpt/frontend/.gptignore - exclude backend/
        → .gpt/api/.gptignore - include only documentation

Step 3: When talking about backend:
        autogpt prompt --content backend
        → Gets only backend code on clipboard

        When talking about frontend:
        autogpt prompt --content frontend
        → Gets only frontend code on clipboard
```

**Benefit**: Keeps prompts focused and within token limits

---

### **Scenario 3: Repeated Daily Usage**

```
User is developing a feature and frequently needs to ask AI questions

1. Make changes to code
2. Run: autogpt prompt
3. Paste clipboard into Claude
4. Ask question about the code
5. Repeat steps 1-4

This happens 10-20 times during a development session.
Each run takes ~1 second and copies to clipboard.
```

---

## Features & Capabilities

### **1. File Filtering** (Most Important)
**Problem**: How do I include/exclude specific files and directories?

**Solution Options**:
- **`.gptignore`**: Works like `.gitignore` (patterns for exclusion)
- **`.gptincludeonly`**: Explicit whitelist (only include matching files)
- **Blacklist/Whitelist files**: Legacy approach (still supported)

**User benefit**: Control what goes into the prompt without modifying the original project

**Common patterns**:
```
# .gptignore - what to EXCLUDE
node_modules/
.git/
__pycache__/
*.pyc
.env
*.log
build/
dist/

# .gptincludeonly - what to INCLUDE (overrides exclusions)
src/
tests/
README.md
```

---

### **2. Profile-Based Configuration**
**Problem**: Different teams/purposes need different filtering rules

**Solution**: Create named profiles with different rules:
```
.gpt/
  .gptignore              # Global rules
  backend/
    .gptignore            # Backend-specific rules
  frontend/
    .gptignore            # Frontend-specific rules
```

**User benefit**: One command (`autogpt prompt --content backend`) gives only what's relevant

---

### **3. Selective Output Generation**
**Problem**: Sometimes you only want the directory structure OR the file contents, not both

**Solution**: `--dir` and `--content` flags

```bash
autogpt prompt --dir              # Just the tree structure (quick preview)
autogpt prompt --content          # Just the file contents (for code review)
autogpt prompt                    # Both (default)
```

**User benefit**: Faster when you only need structure or don't want huge prompts

---

### **4. Automatic Clipboard Management**
**Problem**: After generating a prompt, you still need to copy-paste it

**Solution**: Automatically copies to clipboard

```bash
autogpt prompt
# Result is on your clipboard, ready to paste into ChatGPT
```

**User benefit**: Zero friction, can immediately paste into AI chat

---

### **5. Directory/File Specification**
**Problem**: Maybe you want to prompt about just one subdirectory, not the whole project

**Solution**: Specify root and scan directories:
```bash
autogpt prompt --root_dir /my/big/project --prompt_dir /my/big/project/src
# Only scans src/, uses project root for reference
```

---

## Value Proposition per Command

| Command | Time | Frequency | User Value | Problem Solved |
|---------|------|-----------|------------|-----------------|
| **init** | ~1s | Once per project | Setup and validate | Don't need to manually configure everything |
| **prompt** | ~1s | 10-50x per dev session | Clipboard-ready code | Faster iteration with AI, no manual copy-paste |

---

## What Dependencies Exist?

**External Libraries Used**:
- `pyperclip` (v1.8.2) - Copy to clipboard (makes paste-ready output possible)
- `gitignore-parser` - Parse .gitignore-style patterns (makes familiar syntax)
- `chardet` - Detect file encodings (handles diverse file types)

**External APIs**: None! (Fully offline)

**External Services**: None! (No cloud dependency)

---

## Configuration & Customization

### **What Can Users Configure?**

1. **What files to include/exclude**:
   - Via `.gptignore` patterns
   - Via `.gptincludeonly` whitelist
   - Via blacklist/whitelist files

2. **Multiple profiles**:
   - Create different filtering rules for different contexts
   - Profile-specific `.gptignore`, `.gptincludeonly`, etc.

3. **What data to output**:
   - Directory structure only (`--dir`)
   - File contents only (`--content`)
   - Both (default)

4. **What directory to scan**:
   - Current directory (default)
   - Specific root directory (`--root_dir`)
   - Specific prompt directory (`--prompt_dir`)

---

## Current Operational Workflow

```
User runs: autogpt prompt [options]
            ↓
1. Find .gpt/ directory (project root)
2. Load settings from .gpt/settings/base_settings.json
3. Initialize plugins (gpt_ignore, gpt_include_only, filter)
4. Walk through directory with visitor pattern
5. Filter files using all three plugins
6. Format output (tree + contents)
7. Copy to clipboard
8. Display preview
```

**What's complex**:
- Initializing plugins for a simple command
- Multiple filtering plugins when most users probably use just one
- Lifecycle management (init, configure, activate)

---

## User Pain Points (Inferred)

1. **Must run init first**: Users can't use the tool without initializing
2. **Configuration files unclear**: What's `.gptignore` vs `.gptincludeonly` vs blacklist?
3. **Profiles confusing**: When to use them, how they work
4. **Init is slow**: Loading plugins, validating, creating directories
5. **Error messages**: What went wrong if init fails?

---

## Hypothetical Simpler Version

What if the tool worked like this instead?

```bash
# No init needed, works immediately
autogpt /path/to/project

# Creates output automatically, copies to clipboard
# Uses sensible defaults (ignore node_modules, .git, __pycache__)

# Want to customize? Create a simple .gptignore file
# Want profiles? Create .gpt/backend/.gptignore

# That's it.
```

**Benefits**:
- Zero-config first usage
- Familiar `.gitignore` syntax
- No plugin system needed
- No init validation
- Faster

**What you'd lose**:
- Plugin extensibility (probably not needed)
- Multiple output formats per command (minor feature)
- Explicit validation step

---

## Questions for Simplification

1. **Do users actually create profiles?** Or do most use the default?
2. **Is init necessary?** Could defaults be embedded and created on-demand?
3. **Do all three filtering methods need to exist?** Could `.gptignore` be the only one?
4. **Is the plugin system needed?** Are users writing custom filtering plugins?
5. **What's the most common use case?** (Probably: run prompt, get clipboard)
6. **What takes the most time?** (Probably: filtering/scanning, not initialization)

---

## Summary: What This Tool Really Does

**For the user**: "I press one button and my code is on my clipboard, formatted for AI"

**For simplification**: The complexity (plugins, init, profiles) might exceed the actual user needs. A simpler approach could be:
- Default behaviors instead of required init
- Single filtering mechanism instead of three
- No plugin system (hardcoded filtering logic)
- Auto-detect whether user wants profiles or not
