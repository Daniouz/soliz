# Soliz - A lexer creation tool

## Features

- Provides basic implementations for: strings, integers, floats, operators, symbols
- Soliz's abstract design allows quick and easily understandable development
- Pretty error printing

### Errors look like:

```
Error: Unexpected character
{"key": qas}
        ^
Occurs at: 1:9-9
```

<sub>WARNING: Order of the rules may matter depending on the implementation.</sub>

## Examples

### JSON

```python
from typing import Tuple

from soliz.error import Error
from soliz.impls import StringRule, NumberRule
from soliz.lex import Lexer, Rule, Context
from soliz.tokens import Token


class TokenType:
    TT_LBRACKET = "LBRACKET"
    TT_RBRACKET = "RBRACKET"
    TT_COLON = "COLON"


class JSONRules(Rule):
    def check(self, ctx: Context) -> Tuple[Token, bool] | None:
        match ctx.char:
            case '{':
                return Token(TokenType.TT_LBRACKET, ctx.span()), True
            case '}':
                return Token(TokenType.TT_RBRACKET, ctx.span()), True
            case ':':
                return Token(TokenType.TT_COLON, ctx.span()), True


def main() -> None:
    lexer = Lexer([JSONRules(), StringRule(), NumberRule()])
    text = input("Enter JSON: ")

    try:
        tokens = lexer.lex(text)
        print(tokens)
    except Error as err:
        err.pretty_print(text)
```

## Builtins

Builtin rules can be located in `soliz/impls.py`

### StringRule

This rule allows escape sequences and parses quoted strings.<br>
Errors on invalid escape sequences.

<sub>NOTE: This rule allows newlines inside the string.</sub>

### NumberRule

This rule parses integers and floats, positive or negative.

### OperatorRule

Parses the following operators: `+`, `-`, `*`, `/`, `==`, `^`, `**`

### SymbolRule

Parses the following symbols: `(`, `)`, `=`, `.` as individual token types without value.

### IdentifierRule

Parses identifiers that start with `_` or alphabetic characters, and continue with alphanumeric or `_` characters.
