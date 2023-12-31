from abc import ABC, abstractmethod
from typing import Tuple

from .error import BuiltinErrors, Error, ErrorContext
from .tokens import Span, Token, TokenType


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
        self.col += 1
        self.char = self.text[self.index]

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


class LexResult:
    def __init__(self, tokens: list[Token]) -> None:
        self.tokens = tokens

    def discard_type(self, ty: str) -> None:
        self.tokens = [token for token in self.tokens if token.ty != ty]

    def discard_types(self, *tys: str) -> None:
        self.tokens = [token for token in self.tokens if token.ty not in tys]


class Lexer:
    """Analyzes text and converts pieces of syntax into tokens for later parsing."""

    def __init__(self, rules: list[Rule], append_eoi_token: bool = True) -> None:
        """
        Instantiates a Lexer.

        :param rules: the lexer rules
        :param append_eoi_token: if an EOI token should be appended to this lexer's parse results
        """
        if rules is None:
            raise ValueError("`rules` cannot be None")

        self._rules = rules
        self.append_eoi_token = append_eoi_token

    def lex(self, text: str) -> LexResult:
        """
        Analyzes the text for tokens and returns them in a LexResult.

        :param text: the text to lex
        :raises: Error: if an error occurs while analyzing the text
        :return: the result
        """
        if text is None:
            raise ValueError("`text` cannot be None")

        ctx = Context(text)
        token_list = []

        while not ctx.is_eoi():
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

        if self.append_eoi_token:
            token_list.append(Token(TokenType.TT_EOI, ctx.span()))

        return LexResult(token_list)
