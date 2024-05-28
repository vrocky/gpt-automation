# .gptignore File Specification

The `.gptignore` file is a custom file format similar to `.gitignore` but with the ability to include headers like an INI file.

## Format

- Lines starting with `#` are considered comments.
- Lines within `[...]` brackets are considered headers.
- Patterns listed under each header are similar to those in a `.gptignore` file.
- headers are not compulsory 
- Headers are considered as profile name

## Example

```ignore
# This is a header
pattern1
pattern2

[Header_1]
pattern2
pattern3

# Another header
[Header_2]
pattern3
pattern4
```

In this example:

`pattern1` and `pattern2` are listed under global pattern

`pattern3` and `pattern4` are listed under the header [Header 1].

`pattern5` and `pattern6` are listed under the header [Header 1].

