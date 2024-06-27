# Plugin Development Guide

## Overview

This document provides guidelines for developers on how to create and
integrate plugins into the application's modular configuration system. It
covers the structure of plugin directories, the creation of the plugin code,
and the definition of the plugin manifest files.

## Directory Structure

Each plugin should be contained within its own directory. The structure should include the plugin's Python file and

its manifest file, `manifest.json`.

### Example Directory Structure

    
```
 ./plugins/
        plugin_one/
            manifest.json
            plugin_one.py
        plugin_two/
            manifest.json
            plugin_two.py
            
```

Understood! Let's update the plugin development guidelines to reflect these
modifications, including flexibility in plugin location and changes to the
manifest file structure to specify module and class names instead of an entry
point.


## Plugin Manifest File

The `manifest.json` file is crucial as it contains metadata about the plugin,
crucial for the application to correctly load and use the plugin.

### Manifest File Structure

The manifest should now include the following:

  * **name** : The official name of the plugin.
  * **description** : A brief description of what the plugin does.
  * **module_name** : The Python module where the main plugin code is located.
  * **class_name** : The class within the module that should be instantiated or used.
  * **version** : The current version of the plugin.
  * **author** : The name or organization behind the plugin.
  * **package_name** : The Python package name, if applicable.

### Example `manifest.json`

    
    
    json
    
    Copy code
    
    {
        "name": "my_plugin",
        "description": "Provides enhanced data processing capabilities.",
        "module_name": "my_plugin_module",
        "class_name": "DataProcessor",
        "version": "1.0.0",
        "author": "Your Name",
        "package_name": "advanced_data_processing"
    }
    

## Central Plugin Registry (`plugin_registry.json`)

A file named `plugin_registry.json` serves as the central registry for all
plugins. It lists every available plugin and their respective directories to
facilitate discovery and loading by the main application.

### Structure of `plugin_registry.json`

    
    
    json
    
    Copy code
    
    {
        "plugins": [
            {
                "name": "my_plugin",
                "path": "./any_directory/my_plugin/"
            },
            {
                "name": "another_plugin",
                "path": "./some_other_directory/another_plugin/"
            }
        ]
    }
    

This file should be stored in a location that is easily accessible by the main
application, typically at the root or within a specific configuration
directory.


So the new user config will be looking like 

### Main Config

The main configuration file allows users to specify which plugins they wish to
enable. This configuration references plugins by their names as defined in a
central plugin list, without needing to specify the detailed settings or paths
of the plugins, which are handled separately by the plugin developers.

    
```   
    {
        "extends": "none",
        "override": false,
        "plugins": [
            {
                "plugin_name": "plugin_one",
                "package_name": "gpt_automation",
                "enable": true
            },
            {
                "plugin_name": "plugin_two",
                "package_name": "gpt_automation",
                "enable": true
            }
        ]
    }
    
 ```
    