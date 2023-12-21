# Soliz - A lexer creation tool

## Features

- Provides basic implementations for: strings, integers, floats, operators, symbols
- Soliz's abstract design allows quick and easily understandable development
- Pretty error printing

### Errors look like:

```
Error: Unexpected character
{"key": 4.4.}
           ^
Expected: 'digit', found '.'
Occurs at: 1:12-12
```

<sub>WARNING: Order of the rules may matter depending on the implementation.</sub>

## Builtins

Builtin rules can be located in `soliz/impls.py`

### StringRule

This rule allows escape sequences and parses quoted strings.<br>
Errors on invalid escape sequences.

<sub>NOTE: This rule allows newlines inside the string.</sub>

### NumberRule

This rule parses integers and floats, positive or negative.

### OperatorRule

Parses the following operators: `+`, `-`, `*`, `/`, `==`, `^`, `**`, `%`

### SymbolRule

Parses the following symbols: `(`, `)`, `=`, `.` as individual token types without value.

### IdentifierRule

Parses identifiers that start with `_` or alphabetic characters, and continue with alphanumeric or `_` characters.
