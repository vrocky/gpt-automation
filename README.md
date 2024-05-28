
# GPT Automation

This Python-based project provides a way to automatically generate a project structure, including all directories and files, while ignoring certain unwanted files or directories as specified in a blacklist or a `.gptignore` file. It also offers the capability to generate file contents, allowing users to copy either the entire project structure or just the directory structure to the clipboard.

## Installation

### Pipx Installation

We recommend installing GPT Automation through pipx, a package manager for running applications written in Python. If you haven't installed pipx, first install it by running:

```bash
python3 -m pip install --user pipx
python3 -m pipx ensurepath
```

Next, install the GPT Automation package with:

```bash
pipx install gpt-automation
```

<h3>Manual Installation</h3>

To manually install the project, run the following command from the project's root directory:

```bash
python setup.py install
```

This will install the project as a package, making the main module accessible from the command line.

<h2>Initialization</h2>

To initialize the .gpt directory with sample blacklist, whitelist, and .gptignore files, run:

```bash
autogpt init [profile names]
```

This creates a .gpt directory (or profile-specific directories under .gpt/other_profiles/ if profile names are specified) if it doesn't already exist, copying sample_config/black_list.txt, sample_config/white_list.txt, and a sample .gptignore file into this directory.

<h2>Prompt Generation</h2>

GPT Automation provides two types of prompts:

- Full Prompt: Includes both the directory structure and the contents of all files. To generate a full prompt, use:

```bash
autogpt prompt --dir [profile names] --content [profile names]
```

- Directory-Only Prompt: Only includes the directory structure. To generate a directory-only prompt, use:

```bash
autogpt prompt --dir [profile names]
```

- Content-Only Prompt: Only includes the file contents. To generate a content-only prompt, use:

```bash
autogpt prompt --content [profile names]
```

In all cases, the generated prompt is automatically copied to the clipboard.

<h2>Options</h2>

- --dir: Generates prompts only for directory structures for specified profiles.
- --content: Generates prompts only for file contents for specified profiles.
- The default profile used is "default" if no profiles are specified.

<h2>Blacklists, Whitelists, .gptignore, and .gptincludeonly</h2>

The blacklist file contains patterns of files and directories to ignore during prompt generation, whereas the whitelist file contains patterns of files and directories to include. The .gptignore file functions similarly to a blacklist, offering a more flexible and familiar way to specify files and directories to ignore. The .gptincludeonly file is a new addition that allows users to specify files and directories that should exclusively be included in the prompt, regardless of other rules. If a file matches patterns in both the include and exclude lists, it will be included in the prompt.

```plaintext
# Sample Blacklist (black_list.txt)
*/.gpt/*
*/.git/*
*.gitignore
*.gptignore
*/__pycache__/*
*/gen_scripts/old/*
*/resources/*
*tests*

# Sample Whitelist (white_list.txt)
*.groovy
*.java
*.py
*.ini
*.txt

# Sample `.gptignore`
# Ignore all markdown files
*.md

# Ignore specific directories
node_modules/
build/

# Sample `.gptincludeonly`
# Explicitly include only these files or directories
src/main/
*.yml
```

<h2>Output</h2>

The generated code, including the directory structure and file contents, will be copied to the clipboard in the following format:

```dir
Directory Structure:
./
    file_1.py
    file_2.py
    dir_1/
        file_1.py

File Contents:
==========file_1.py:
# Code for file_1.py

==========file_2.py:
# Code for file_2.py

==========dir_1/file_1.py:
# Code for dir_1/file_1.py
```







<h2>Profile-Based Configuration in .gptignore and .gptincludeonly</h2>

Profiles in .gptignore and .gptincludeonly files allow users to define different exclusion and inclusion rules for various project environments or scenarios. This section provides examples of how to structure these files with profile headers and without (global), along with comments to explain their usage.

<h3>Example with Profile Headers</h3>

```plaintext
# Global Rules (Applies to all profiles)
# Ignore all .git directories
.git/

# Profile: cli
# Rules specific to the "cli" profile
[cli]
# Ignore all markdown files
*.md

# Explicitly include only these files or directories
src/main/
*.yml

# Profile: ignore_walk
# Rules specific to the "ignore_walk" profile
[ignore_walk]
# Ignore specific directories
node_modules/
build/

# Profile: ignore_walk_tests
# Rules specific to the "ignore_walk_tests" profile
[ignore_walk_tests]
# Ignore test files with "ignore_walk" in their path
tests/*/ignore_walk*

# Profile: setup
# Rules specific to the "setup" profile
[setup]
# Ignore setup-related files
setup.py
setup.cfg
pyproject.toml
```

<h3>Example without Profile Headers (Global Rules Only)</h3>

```plaintext
# Global Rules (Applies to all profiles)
# Ignore all .git directories
.git/

# Ignore all markdown files
*.md

# Explicitly include only these files or directories
src/main/
*.yml

# Ignore specific directories
node_modules/
build/

# Ignore test files with "ignore_walk" in their path
tests/*/ignore_walk*

# Ignore setup-related files
setup.py
setup.cfg
pyproject.toml
```

<h3>Example Usage</h3>

Suppose you have defined the following profiles:

- cli
- ignore_walk
- ignore_walk_tests
- setup

You can then apply the rules defined within these profiles during project initialization and prompt generation by specifying the corresponding profile names. For example:

```bash
autogpt init cli ignore_walk
autogpt prompt --dir ignore_walk_tests --content setup
```

This will apply the rules defined in the specified profiles to the initialization and prompt generation processes, ensuring that the directory structure and file contents meet the requirements of each specific profile.




This README provides detailed instructions for installing and using the GPT Automation tool, including how to use the init, prompt commands with their respective options. It also explains the purpose of the blacklist, whitelist, and .gptignore files, and how the output will be formatted and copied to the clipboard.




