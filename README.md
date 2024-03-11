<h1>GPT Automation</h1>

This Python-based project provides a way to automatically generate a project structure, including all directories and files, while ignoring certain unwanted files or directories as specified in a blacklist or a .gptignore file. It also offers the capability to generate file contents, allowing users to copy either the entire project structure or just the directory structure to the clipboard.

<h2>Installation</h2>

<h3>Pipx Installation</h3>

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

<h3>Initialization</h3>

To initialize the .gpt directory with sample blacklist, whitelist, and .gptignore files, run:

```bash
autogpt init [--profile PROFILE_NAME]
```

This creates a .gpt directory (or a profile-specific directory under .gpt/other_profiles/ if --profile is specified) if it doesn't already exist, copying sample_config/black_list.txt, sample_config/white_list.txt, and a sample .gptignore file into this directory.

<h3>Prompt Generation</h3>

GPT Automation provides two types of prompts:

- Full Prompt: Includes both the directory structure and the contents of all files. To generate a full prompt, use:

```bash
autogpt prompt-all [--path PROJECT_PATH] [--profile PROFILE_NAME]
```

- Directory-Only Prompt: Only includes the directory structure. To generate a directory-only prompt, use:

```bash
autogpt prompt-dir [--path PROJECT_PATH] [--profile PROFILE_NAME]
```

In both cases, the generated prompt is automatically copied to the clipboard.

<h3>Options</h3>

- --path: Specifies the path to your project's root directory. Defaults to the current directory.
- --profile: Specifies the name of the profile to use. This allows for different configurations for different projects or use cases.

<h3>Blacklists, Whitelists, .gptignore, and .gptincludeonly</h3>

The blacklist file contains patterns of files and directories to ignore during prompt generation, whereas the whitelist file contains patterns of files and directories to include. The .gptignore file functions similarly to a blacklist, offering a more flexible and familiar way to specify files and directories to ignore. The .gptincludeonly file is a new addition that allows users to specify files and directories that should exclusively be included in the prompt, regardless of other rules. If a file matches patterns in both the include and exclude lists, it will be included in the prompt.
Sample Blacklist (black_list.txt)

```plaintext
*prompts*
*.idea*
*__pycache__*
*.xml
*.gitignore*
*.md
*gen_scripts/old*
*/resources*
*examples*
*tests*
*scripts*
*dse*
*.gpt*
```

Sample Whitelist (white_list.txt)

```plaintext
*.groovy
*.java
*.py
*.ini
*.txt
```

Sample `.gptignore`

```gitignore
# Ignore all markdown files
*.md

# Ignore specific directories
node_modules/
build/
```

Sample `.gptincludeonly`

```gitignore
# Explicitly include only these files or directories
src/main/
*.yml

```


<h3>Output</h3>

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

This README provides detailed instructions for installing and using the GPT Automation tool, including how to use the init, prompt-all, and prompt-dir commands with their respective options. It also explains the purpose of the blacklist, whitelist, and .gptignore files, and how the output will be formatted and copied to the clipboard.


