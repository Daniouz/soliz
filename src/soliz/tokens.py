from typing import Any


class Span:
    """Object used for human-friendly debugging regarding Token outputs and lexer errors."""

    def __init__(self, ln: int, cs: int, ce: int) -> None:
        """
        Instantiates a Span.

        :param ln: the line number
        :param cs: the start column
        :param ce: the end column
        """
        self.ln = ln
        self.cs = cs
        self.ce = ce

    def __repr__(self) -> str:
        return f"{self.ln}:{self.cs}-{self.ce}"


class TokenType:
    """Builtin token type constants."""
    TT_SPACE = "space"
    TT_STRING = "string"
    TT_INT = "int"
    TT_FLOAT = "float"
    TT_OP = "operator"
    TT_ID = "identifier"
    TT_LPAREN = '('
    TT_RPAREN = ')'
    TT_EQUALS = '='
    TT_PERIOD = '.'
    TT_COMMA = ','
    TT_COLON = ':'
    TT_SEMICOLON = ';'
    TT_AND = '&'
    TT_AT = '@'
    TT_TILDA = '~'
    TT_QUESTION = '?'
    TT_EXCLAMATION = '!'
    TT_HASHTAG = '#'
    TT_CARET = '^'
    TT_LBRACE = '{'
    TT_RBRACE = '}'
    TT_LBRACKET = '['
    TT_RBRACKET = ']'
    TT_EOL = "<eol>"
    TT_EOI = "<eoi>"


class Token:
    """A piece of data parsed from the source."""

    def __init__(self, ty: str, span: Span, value: Any | None = None) -> None:
        """
        Instantiates a Token.

        :param ty: the type of token
        :param value: the token's value
        :param span: the span in which the token was defined
        """
        if ty is None or span is None:
            raise ValueError("Arguments cannot be None")

        self.ty = ty
        self.value = value
        self.location = span

    def __repr__(self) -> str:
        return f"<{self.ty} [{self.value}] {self.location}>"
