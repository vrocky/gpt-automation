# Logging & Output Audit for GPT Automation

This document tracks the audit of all print and logging output in the codebase, in preparation for a centralized logging refactor.

## Audit Goals
- Remove all direct print statements (except final summary)
- Use a centralized logger everywhere
- Only warnings/errors go to console; all else to log file
- No ad-hoc logger configs in modules/plugins

## Audit Table

| File/Module | Print Statements | Direct Logging Setup | Notes/Actions Needed |
|-------------|------------------|---------------------|----------------------|
| main.py | No print statements | No direct logging setup | CLI entrypoint. All output is handled by downstream commands. No logging or print in this file. Should use centralized logger for any future CLI errors or summaries. |
| commands/init_command.py | No print, custom logging setup | Yes (custom, needs centralization) | Uses its own logger and handlers. Should use centralized logging utility. Only final summary should go to console. |
| commands/prompt_command.py | No print, custom logging setup | Yes (custom, needs centralization) | Uses its own logger and handlers. Should use centralized logging utility. Only final summary should go to console. |
| impl/setting/setting_utils.py | No print | No | No logging or print. No action needed. |
| impl/setting/settings_resolver.py | No print | No | No logging or print. No action needed. |
| impl/plugin_impl/plugin_init.py | No print | Uses logger, but not centralized | Should use centralized logging utility. |
| impl/plugin_impl/plugin_loader.py | No print | Uses logger, but not centralized | Should use centralized logging utility. |
| impl/plugin_impl/plugin_interfaces.py | No print | No | No logging or print. No action needed. |
| impl/plugin_impl/plugin_context.py | No print | No | No logging or print. No action needed. |
| impl/plugin_impl/plugin_utils.py | No print | No | No logging or print. No action needed. |
| impl/base_plugin.py | No print | No | No logging or print. No action needed. |
| plugins/filter_plugin/plugin.py | No print | No | No logging or print. No action needed. |
| plugins/ignore_plugin/plugin.py | No print | No | No logging or print. No action needed. |
| plugins/include_only_plugin/plugin.py | No print | No | No logging or print. No action needed. |
| plugins/ignore_plugin/ignore_visitor.py | Yes (print in before_traverse_directory) | No | Replace print with logger.debug/info. |
| plugins/include_only_plugin/includeonly_visitor.py | Yes (print in before_traverse_directory) | No | Replace print with logger.debug/info. |

## Next Steps
- Fill in the table by reading each file and noting all output code
- Plan refactor for each file
- Implement centralized logging in phase 2
