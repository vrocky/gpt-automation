# GPT Automation
This Python-based project provides a way to automatically generate a project structure, including all directories and files, while ignoring certain unwanted files or directories (as specified in a blacklist). It also provides the ability to generate file contents, and can copy either the entire project structure or just the directory structure to the clipboard.

## Getting Started
Installation
To install the project, run the following command from the project's root directory:

```
python setup.py install
```

This will install the project as a package, making the `main` module accessible from the command line.

## Initialization


To initialize the .gpt directory with sample blacklist and whitelist files, run:
```
autogpt init
```

This will create a .gpt directory if it doesn't already exist, and will copy sample_config/black_list.txt and sample_config/white_list.txt to the .gpt directory.


## Prompt Generation

GPT Automation provides two types of prompts:

1. **Full Prompt:** This includes both the directory structure and the contents of all files. To generate a full prompt, use:

```bat
autogpt prompt-all --black-list-file [BLACKLIST_PATH] --white-list-file [WHITELIST_PATH] --project-path [PROJECT_PATH]
```

2. **Directory-Only Prompt:** As the name suggests, this only includes the directory structure. To generate a directory-only prompt, use:

```bat
autogpt prompt-dir --black-list-file [BLACKLIST_PATH] --white-list-file [WHITELIST_PATH] --project-path [PROJECT_PATH]
```

In both cases, the generated prompt is automatically copied to the clipboard.

## Blacklists and Whitelists

The blacklist file is a list of patterns that will be ignored when generating the prompt. The whitelist file, on the other hand, is a list of patterns that will be included in the prompt. If a file matches a pattern in both the blacklist and the whitelist, it will be included.

Sample contents for black_list.txt:



Here are some sample contents for the black_list.txt and white_list.txt files to be used with the GPT Automation project:

Sample contents for black_list.txt:

```
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


Sample contents for white_list.txt:

```
*.groovy
*.java
*.py
*.ini
*.txt
```

## Output

The whole code will be coped to clipboard in this format

```python

Directory Structure:
./
    file_1.py
    file_2.py
    dir_1/
        file_1.py


File Contents:
==========file_1.py:
##.... code for file_1.py

==========file_2.py:
##.... code for file_2.py

==========dir_1/file_1.py:
##.... code for dir_1/file_1.py
```
