### CLI Configuration for Plugin Management Specification Document

#### Overview

This document details the specifications for configuring plugins via a
command-line interface (CLI). It focuses on CLI modifiers that integrate with
plugin-specific configurations defined in external files, particularly
aligning with settings outlined in each plugin’s `manifest.json`.

#### Logging

All plugin-specific logs are routed to the central log file. Debug output will not clutter the console; only summary and errors are shown on the console.

#### CLI Modifiers and Arguments

  1. **`--plugin-args <key>=<value>`**

     * **Purpose** : Directly passes specific arguments to plugins to facilitate runtime customization.
     * **Format** : Utilizes the format `package-name__plugin-name__variable-name=value`.
     * **Example** :
        
        ```        
        --plugin-args mypackage__pluginA__timeout=30
        ```     

  2. **`--environment <key>=<value>`**

     * **Purpose** : Sets environment variables specific to plugins, modifying their behavior during runtime.
     * **Format** : Configured as `package-name__plugin-name__variable-name=value`.
     * **Example** :
        
        ```bash
        --environment mypackage__pluginA__debug=true
        ```
                

  3. **`--add-config <file_path>`**

     * **Purpose** : Automatically assigns configuration files to plugins based on matching file patterns specified in the plugin’s `manifest.json`.
     * **Explanation** : This option leverages the `configFilePatterns` attribute from the plugin's `manifest.json` to route the right configuration files to the correct plugin.
     * **Example** :
        
        ```
        --add-config /path/to/plugin_config.cfg.json
        ```
                
   
        

#### Configuration File Formats

  1. **.conf Files**

     * **Description** : Simple text-based configuration files containing directives for plugin settings.
     * **Format** : Each directive follows the format `package-name__plugin-name__variable-name=value`.
     * **Example** :
        
        ```      
        mypackage__pluginA__timeout=30
        mypackage__pluginB__debug=true
        ```       

  2. **.json Files**

     * **Description** : Structured JSON files used for complex plugin configurations.
     * **Format** : Nested objects representing plugin hierarchies.
     * **Example** :
        
        ```
                {
                "mypackage": {
                    "pluginA": {
                    "timeout": 30,
                    "feature_enabled": true
                    },
                    "pluginB": {
                    "path": "/usr/local/bin",
                    "debug": true
                    }
                }
                }
        ```
                

#### Explanation of `--add-config`

  * **Functionality** : The `--add-config` modifier is designed to simplify the configuration process by automating the detection and application of appropriate configuration files to their respective plugins. It relies on `configFilePatterns` defined in the `manifest.json` of each plugin, which specify the patterns or extensions of configuration files that are accepted by the plugin.
  * **Process** :
    * The CLI tool scans the provided configuration file path.
    * It then checks against the `configFilePatterns` listed in the plugin's manifest.
    * If a match is found, the configuration file is passed to the respective plugin.
    * This ensures that each plugin receives only the configuration files formatted and named according to its specified requirements.

#### Glimpse into `manifest.json`

While a detailed `manifest.json` specification is maintained in a separate
document, here’s a brief example to illustrate how it interacts with the CLI
configuration:

**Example `manifest.json` for Plugin A**:


    
```json
    {
        "name": "my_plugin",
        "description": "Enhances data processing capabilities.",
        "module_name": "my_plugin_module",
        "class_name": "DataProcessor",
        "version": "1.0.0",
        "author": "Your Name",
        "package_name": "advanced_data_processing",
        "configFilePatterns": [
            ".cfg.json",
            ".setting.json"
            ]
    }
```
    

  * **Key Attribute** : `configFilePatterns` lists the file extensions that this plugin can accept, enabling the CLI tool to match and assign configuration files appropriately.

#### Conclusion

This document provides a comprehensive framework for using a CLI to manage
plugin configurations, emphasizing flexibility and precision in assigning
configuration files based on defined patterns in the plugin's `manifest.json`.
This approach ensures that plugins are configured in a manner that is both
efficient and error-resistant, tailored to the specific needs outlined in
their manifest files.
