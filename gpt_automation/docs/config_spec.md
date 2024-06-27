# Main Configuration System Specifications Document

## Overview

This document outlines how users can configure plugins within a larger
application using JSON files. The configuration system allows for flexibility
and modularity, enabling users to enable or disable specific plugins based on
their preferences.

## Configuration File Structure

### Main Config

The main configuration file allows users to specify which plugins they wish to
enable. This configuration references plugins by their names as defined in a
central plugin list, without needing to specify the detailed settings or paths
of the plugins, which are handled separately by the plugin developers.

    
    
    json
    
    Copy code
    
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
    

## Configuration Keys

  * **extends** : Specifies which configuration, if any, this file extends. It can be set to "none" if there is no parent configuration.
  * **override** : A boolean that indicates whether the values in this configuration should override those in the extended configuration.
  * **plugins** : An array of plugin configurations that the user wants to enable. Each plugin configuration specifies:
    * **plugin_name** : The name of the plugin as recognized by the system.
    * **package_name** : The Python package name associated with the plugin.
    * **enable** : A boolean that indicates whether the plugin should be enabled.

## Usage

The main configuration file is intended for end users who need to manage their
plugin settings easily. This system supports dynamic modifications, allowing
users to enable or disable plugins as required by their specific use cases.

This configuration approach promotes a clean separation between the user-
facing settings and the backend plugin management system, enhancing
maintainability and scalability of the application.

### Practical Steps for Users

  1. **Identify the Plugin** : Determine which plugins are necessary for your workflow and note their names as listed in the central plugin directory.
  2. **Set Configuration** : Modify the main configuration JSON to include the plugins you need, setting the "enable" flag as appropriate.
  3. **Apply Changes** : Save the configuration file and restart the application if necessary to apply the changes.

This system ensures that users can customize their application experience
without delving into the complexities of plugin internals, focusing instead on
what each plugin offers to enhance their productivity or functionality within
the application.