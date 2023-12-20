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


class Token:
    """A piece of data parsed from the source."""

    def __init__(self, ty: str, span: Span, value: Any | None = None) -> None:
        """
        Instantiates a Token.

        :param ty: the type of token
        :param value: the token's value
        :param span: the span in which the token was defined
        """
        self.ty = ty
        self.value = value
        self.location = span

    def __repr__(self) -> str:
        return f"<{self.ty} [{self.value}] {self.location}>"
