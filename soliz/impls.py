from typing import Tuple

from soliz.lex import Context, Rule
from soliz.error import Error, BuiltinErrors, ErrorContext
from soliz.tokens import Token


class TokenType:
    """Token type constants."""
    TT_STR = "string"
    TT_INT = "int"
    TT_FLOAT = "float"
    TT_OP = "operator"
    TT_ID = "identifier"
    TT_LPAREN = "lparen"
    TT_RPAREN = "rparen"
    TT_EQUALS = "equals"
    TT_PERIOD = "period"


class StringRule(Rule):
    """
    Lexer rule for analyzing basic strings.
    Supports the following escape sequences: '"', '\\', 'n', 'r', 't', 'b', 'f',
    """

    def check(self, ctx: Context) -> Tuple[Token, bool] | None:
        """
        Checks the given context for a string and returns it as a Token, if present.

        :param ctx: the lexer context
        :raises Error: if EOI is reached
        :return: the string Token and True, or None if this rule is inapplicable to the given context
        """
        if ctx.char != '"':
            return None

        chars = []
        col_start = ctx.col
        found_end_quote = False

        while not found_end_quote:
            char = ctx.next_char_else(['"', "any"])

            if char == '"':
                found_end_quote = True
            elif char == '\\':
                if (esc := ctx.next_char()) is None:
                    raise Error(BuiltinErrors.UNEXPECTED_EOI, ctx.span(),
                                ErrorContext(['any', '"', r'\\', r'\n', r'\r', r'\t', r'\b', r'\f'], "EOI"))

                match esc:
                    case '"':
                        chars.append('"')
                    case '\\':
                        chars.append('\\')
                    case 'n':
                        chars.append('\n')
                    case 'r':
                        chars.append('\r')
                    case 't':
                        chars.append('\t')
                    case 'b':
                        chars.append('\b')
                    case 'f':
                        chars.append('\f')
                    case _:
                        raise Error(BuiltinErrors.UNSUPPORTED_ESCAPE, ctx.span(),
                                    ErrorContext(['"', r'\\', r'\n', r'\r', r'\t', r'\b', r'\f'], esc))
            else:
                chars.append(char)

        return Token(TokenType.TT_STR, ctx.span(col_start, -1), ''.join(chars)), True


class NumberRule(Rule):
    """Lexer rule for analyzing floats and integers."""

    def check(self, ctx: Context) -> Tuple[Token, bool] | None:
        if not (ctx.char.isdigit() or ctx.char == '-'):
            return

        seq = []
        cs = ctx.col
        is_float = False

        if ctx.char == '-':
            if ctx.peek().isdigit():
                if ctx.index > 0 and ctx.peek(-1).isdigit():
                    return

                seq.append('-')
                ctx.advance()
            else:
                return

        while not ctx.is_eoi():
            if ctx.char == '.':
                if is_float:
                    raise Error(BuiltinErrors.UNEXPECTED_CHARACTER, ctx.span(),
                                ErrorContext(['digit'], '.'))

                is_float = True
            elif not ctx.char.isdigit():
                break

            seq.append(ctx.char)
            ctx.advance()

        span = ctx.span(cs)
        value = ''.join(seq)

        if is_float:
            return Token(TokenType.TT_FLOAT, span, float(value)), False

        return Token(TokenType.TT_INT, span, int(value)), False


class OperatorRule(Rule):
    def check(self, ctx: Context) -> Tuple[Token, bool] | None:
        match ctx.char:
            case '+':
                return Token(TokenType.TT_OP, ctx.span(), '+'), True
            case '-':
                return Token(TokenType.TT_OP, ctx.span(), '-'), True
            case '*':
                if ctx.peek() == '*':
                    ctx.advance()
                    return Token(TokenType.TT_OP, ctx.span(ctx.col - 1), "**"), True

                return Token(TokenType.TT_OP, ctx.span(), '*'), True
            case '/':
                return Token(TokenType.TT_OP, ctx.span(), '/'), True
            case '^':
                return Token(TokenType.TT_OP, ctx.span(), '^'), True
            case '%':
                return Token(TokenType.TT_OP, ctx.span(), '%'), True
            case '=':
                if ctx.peek() == '=':
                    ctx.advance()
                    return Token(TokenType.TT_OP, ctx.span(ctx.col - 1), "=="), True


class SymbolRule(Rule):
    def check(self, ctx: Context) -> Tuple[Token, bool] | None:
        match ctx.char:
            case '(':
                return Token(TokenType.TT_LPAREN, ctx.span()), True
            case ')':
                return Token(TokenType.TT_RPAREN, ctx.span()), True
            case '.':
                return Token(TokenType.TT_PERIOD, ctx.span()), True
            case '=':
                return Token(TokenType.TT_EQUALS, ctx.span()), True


class IdentifierRule(Rule):
    def check(self, ctx: Context) -> Tuple[Token, bool] | None:
        if not ctx.char.isalpha() or ctx.char == '_':
            return

        start = ctx.col
        chars = []

        while not ctx.is_eoi() and (ctx.char.isalnum() or ctx.char == '_'):
            chars.append(ctx.char)
            ctx.advance()

        return Token(TokenType.TT_ID, ctx.span(start, -1), ''.join(chars)), False
