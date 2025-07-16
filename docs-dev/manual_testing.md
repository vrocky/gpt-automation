# Manual Testing Guide: Using `test_data` Directory

This guide explains how to manually test GPT Automation's directory and content prompt generation using the provided `test_data` directory.

## Prerequisites
- Ensure you have installed GPT Automation (see `cli.md` for installation instructions).
- Run `autogpt init` if you haven't already, to set up configuration files.

## Steps for Manual Testing

### 1. Explore Directory Structure
Run the following command to generate and preview the directory structure:

```
autogpt prompt --dir
```
- This will output the directory tree, including `test_data` and its subfolders.
- The structure is also copied to your clipboard for easy use.

### 2. Explore File Contents
To preview file contents in `test_data`, run:

```
autogpt prompt --content
```
- This will output the contents of all files (subject to ignore/include rules).

### 3. Combine Directory and Content Prompts
To generate both directory and file content prompts:

```
autogpt prompt --dir --content
```

### 4. Test Ignore/Include Rules
- Edit `.gptignore` or `.gptincludeonly` to add or remove patterns.
- Re-run the above commands to see how the output changes.
- Example: Add `*.txt` to `.gptignore` and verify `.txt` files in `test_data` are excluded.

### 5. Test Profiles
- Add profile-specific rules in `.gptignore` or `.gptincludeonly` (see `config.md`).
- Run with a profile:
  ```
  autogpt prompt --dir myprofile
  ```
- Confirm only files/dirs matching the profile's rules are included.

### 6. Validate Output
- Check that the output matches the expected structure and content for your ignore/include settings.
- Use the clipboard output to paste into an LLM or other tool for further testing.

## Notes
- The `test_data` directory is designed to cover various edge cases (nested dirs, ignore files, etc.).
- For automated tests, see the `tests/` directory.

---

This guide helps you manually verify GPT Automation's core features using the sample data provided in `test_data/`.
