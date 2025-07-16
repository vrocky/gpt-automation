# Configuration

## Ignore/Include Files
- `.gptignore`: Like `.gitignore`, specifies files/dirs to exclude
- `.gptincludeonly`: Specifies files/dirs to include exclusively
- `black_list.txt`/`white_list.txt`: Legacy support

## Profiles
- Rules can be global or profile-specific (with `[profile]` headers)
- Example:
  ```
  [cli]
  *.md
  src/main/
  *.yml
  ```
- Specify profiles in CLI to apply their rules
