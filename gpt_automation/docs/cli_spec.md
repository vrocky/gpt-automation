# Enhanced CLI Specification for GPT Automation

## Overview

GPT Automation facilitates the automatic generation of project structures. It
allows users to define profiles that can customize the inclusion or exclusion
of specific files and directories. The CLI provides commands for initializing
configuration profiles and generating prompts for directory structures and
file contents.

## Commands

### `init`

Initializes the GPT Automation configuration, creating necessary configuration
files and directories based on the provided profiles.

**Usage:**

    
    
     bash
    
    Copy code
    
    autogpt init [profile names]
    

  * **Parameters:**
    * `[profile names]` (optional): Space-separated list of profile names to initialize. If no profile is specified, it initializes a default profile.
  * **Description:**
    * Initializes directories and configuration files within a `.gpt` directory in the current working directory. If profiles are specified, creates profile-specific configurations.

**Examples:**

  * Initialize with no specific profiles:
    
        bash
    
    Copy code
    
    autogpt init
    

  * Initialize with specific profiles:
    
        bash
    
    Copy code
    
    autogpt init cli backend
    

### `prompt`

Generates prompts for directory structures and/or file contents based on the
specified profiles. Results are automatically copied to the clipboard.

**Usage:**

    
    
     bash
    
    Copy code
    
    autogpt prompt --dir [profile names] --content [profile names]
    

  * **Options:**
    * `--dir [profile names]`: Generates prompts for directory structures for specified profiles. If no profile is specified under this option, it defaults to using profiles specified in the general `[profile names]`.
    * `--content [profile names]`: Generates prompts for file contents for specified profiles. Similar to `--dir`, it defaults to general profiles if none are specified here.
  * **Behavior:**
    * If neither `--dir` nor `--content` is specified, the command defaults to generating both directory and content prompts for the specified profiles.
    * Outputs are structured to show the directory preview when generating content and are printed to the console and copied to the clipboard.

**Examples:**

  * Generate directory structure for specific profiles:
    
        bash
    
    Copy code
    
    autogpt prompt --dir cli backend
    

  * Generate file contents for specific profiles:
    
        bash
    
    Copy code
    
    autogpt prompt --content cli backend
    

  * Generate both for multiple profiles:
    
        bash
    
    Copy code
    
    autogpt prompt --dir cli backend --content cli backend
    

## Configuration Files

### `.gptignore`

Specifies exclusion patterns for files and directories during prompt
generation.

**Features:**

  * Supports wildcard characters for broad matching.
  * Path-specific exclusions can be specified by ending patterns with a slash `/`.

### `.gptincludeonly`

Lists files and directories that should be exclusively included, overriding
exclusion rules.

**Features:**

  * Provides an exact specification of which files or directories to include, irrespective of other exclusion patterns.

## Profiles

Enable tailored configurations for different development environments or
project setups.

**Profiles Example:**

  * `cli`: Specific to command-line interface tools.
  * `backend`: Geared towards backend services configurations.

## Output

Results include a structured preview of directory structures and file
contents, formatted for clarity, and copied to the clipboard.