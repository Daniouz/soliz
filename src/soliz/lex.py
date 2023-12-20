from abc import ABC, abstractmethod

from src.soliz.error import BuiltinErrors, Error, ErrorContext
from src.soliz.tokens import Span, Token

from typing import Tuple


class Context:
    def __init__(self, text: str) -> None:
        """
        Initializes a Context.

        :param text: the text content of the source file
        """
        self.text = text
        self.index = 0
        self.col = 1
        self.ln = 1
        self.char = text[0] if text else None

    def advance(self) -> None:
        """
        Advances to the next character in the text.

        If the character is a newline, the line number will be incremented and the current column will be reset to one.
        """
        if not self.has_next():
            self.char = None
            return

        self.index += 1
        self.char = self.text[self.index]

        if self.char == '\n':
            self.ln += 1
            self.col = 1
        else:
            self.col += 1

    def has_next(self) -> bool:
        """
        Returns whether another character is available in the iteration.

        :return: if EOI has not been reached
        """
        return self.index + 1 < len(self.text)

    def peek(self, n: int = 1) -> str | None:
        """
        Returns the next nth character in the text without advancing, if present.

        :return: the character, or None
        """
        if self.index + n >= len(self.text):
            return None

        return self.text[self.index + n]

    def next_char(self) -> str | None:
        """
        Advances to and returns the next character in the text, if EOI has not been reached.

        :return: the character, or None
        """
        self.advance()
        return self.char

    def is_eoi(self) -> bool:
        """
        Returns if this context has reached the end of the text.

        :return: if EOI has been reached
        """
        return self.char is None

    def next_char_else(self, expect: list[str]) -> str:
        """
        Advances to and returns the next character in the text, or raises the builtin UNEXPECTED_EOI if EOI is reached.

        :raises Error: if EOI is reached
        :return: the character
        """
        if (char := self.next_char()) is None:
            raise Error(BuiltinErrors.UNEXPECTED_EOI, self.span(), ErrorContext(expect, "EOI"))

        return char

    def span(self, start_col: int | None = None, end_offset: int = 0) -> Span:
        """
        Creates and returns a Span according to the context's position.

        :return: the location
        """
        return Span(self.ln, self.col if start_col is None else start_col, self.col + end_offset)


class Rule(ABC):
    """A lexer rule which analyzes text for tokens."""

    @abstractmethod
    def check(self, ctx: Context) -> Tuple[Token, bool] | None:
        """
        Analyzes the given context and returns a Token if present, according to the rule's implementation.

        :param ctx: the lexer context
        :raises Error: if an Error occurs while validating the Token
        :return: the analyzed Token and whether the lexer should advance, or None if this rule is inapplicable to the
                 given context
        """
        pass


class Lexer:
    """Analyzes text and converts pieces of syntax into tokens for later parsing."""

    def __init__(self, rules: list[Rule]) -> None:
        """
        Instantiates a Lexer.

        :param rules: the lexer rules
        """
        self._rules = rules

    def lex(self, text: str) -> list[Token]:
        """
        Analyzes the text for tokens and returns them.

        :param text: the text to lex
        :raises: Error: if an error occurs while analyzing the text
        :return: the tokens
        """
        ctx = Context(text)
        token_list = []

        while not ctx.is_eoi():
            if ctx.char.isspace():
                ctx.advance()
                continue

            applied = False

            for rule in self._rules:
                if res := rule.check(ctx):
                    token, should_advance = res
                    token_list.append(token)

                    if should_advance:
                        ctx.advance()

                    applied = True
                    break

            if not applied:
                raise Error(BuiltinErrors.UNEXPECTED_CHARACTER, ctx.span())

        return token_list
