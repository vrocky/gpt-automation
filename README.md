
# GPT Automation

This Python-based project provides a way to automatically generate a project structure, including all directories and files, while ignoring certain unwanted files or directories as specified in a blacklist. It also offers the capability to generate file contents, allowing users to copy either the entire project structure or just the directory structure to the clipboard.

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

Manual InstallationTo manually install the project, run the following command from the project's root directory:

```bash
python setup.py install
```

This will install the project as a package, making the main module accessible from the command line.

InitializationTo initialize the .gpt directory with sample blacklist and whitelist files, run:

```bash
autogpt init [--profile PROFILE_NAME]
```

This creates a .gpt directory (or a profile-specific directory under .gpt/other_profiles/ if --profile is specified) if it doesn't already exist, copying sample_config/black_list.txt and sample_config/white_list.txt into this directory.

Prompt GenerationGPT Automation provides two types of prompts:

Full PromptIncludes both the directory structure and the contents of all files. To generate a full prompt, use:

```bash
autogpt prompt-all [--path PROJECT_PATH] [--profile PROFILE_NAME]
```

Directory-Only PromptOnly includes the directory structure. To generate a directory-only prompt, use:

```bash
autogpt prompt-dir [--path PROJECT_PATH] [--profile PROFILE_NAME]
```

In both cases, the generated prompt is automatically copied to the clipboard.

Options- --path: Specifies the path to your project's root directory. Defaults to the current directory.
- --profile: Specifies the name of the profile to use. This allows for different configurations for different projects or use cases.

Blacklists and WhitelistsThe blacklist file contains patterns of files and directories to ignore during prompt generation, whereas the whitelist file contains patterns of files and directories to include. If a file matches patterns in both lists, it will be included in the prompt.

Sample Blacklist (black_list.txt)```plaintext
*prompts*
*.idea*
*__pycache__*
*.xml
*.gitignore*
*.md
*gen_scripts/old*
*/resources*
*.tpl
*bazel-*
*examples*
*tests*
*scripts*
*dse*
*.gpt*
```

Sample Whitelist (white_list.txt)```plaintext
*.groovy
*.java
*.py
*.ini
*.txt
```

OutputThe generated code, including the directory structure and file contents, will be copied to the clipboard in the following format:

```python
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

This README provides detailed instructions for installing and using the GPT Automation tool, including how to use the `init`, `prompt-all`, and `prompt-dir` commands with their respective options. It also explains the purpose of the blacklist and whitelist files, and how the output will be formatted and copied to the clipboard.


