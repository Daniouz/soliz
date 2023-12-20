from typing import Tuple

from soliz.error import Error, ErrorContext, BuiltinErrors
from soliz.impls import StringRule, NumberRule, TokenType
from soliz.lex import Lexer, Rule, Context
from soliz.tokens import Token, Span


class JsonToken:
    TT_LBRACKET = "{"
    TT_RBRACKET = "}"
    TT_COLON = ":"
    TT_COMMA = ","


class JSONSymbolRule(Rule):
    def check(self, ctx: Context) -> Tuple[Token, bool] | None:
        match ctx.char:
            case '{':
                return Token(JsonToken.TT_LBRACKET, ctx.span()), True
            case '}':
                return Token(JsonToken.TT_RBRACKET, ctx.span()), True
            case ':':
                return Token(JsonToken.TT_COLON, ctx.span()), True
            case ',':
                return Token(JsonToken.TT_COMMA, ctx.span()), True


class TokenIterator:
    def __init__(self, tokens: list[Token]) -> None:
        self.tokens = tokens
        self.index = 0

    def is_eoi(self) -> bool:
        return self.index >= len(self.tokens)

    def next(self) -> Token | None:
        self.index += 1
        return None if self.is_eoi() else self.tokens[self.index]

    def peek(self) -> Token | None:
        return self.tokens[self.index + 1] if self.has_next() else None

    def has_next(self):
        return self.index + 1 < len(self.tokens)


def parse_section(previous_span: Span, it: TokenIterator) -> (any, Span):
    entries = {}
    last_span = previous_span

    while (t := it.peek()) and t.ty != JsonToken.TT_RBRACKET:
        last_span = t.location
        key, value, span = parse_field(t.location, it)

        if not (c := it.next()):
            raise Error(BuiltinErrors.UNEXPECTED_EOI, span, ErrorContext(["'}'", "','"], "EOI"))

        entries[key] = value

        match c.ty:
            case JsonToken.TT_RBRACKET:
                return entries, c.location
            case JsonToken.TT_COMMA:
                continue

        raise Error("Syntax error", c.location, ErrorContext(["'}'", "','"], c.ty))

    raise Error(BuiltinErrors.UNEXPECTED_EOI, last_span, ErrorContext(["field"], "EOI"))


def parse_value(previous_span: Span, it: TokenIterator) -> (any, Span):
    if not (token := it.next()):
        raise Error(BuiltinErrors.UNEXPECTED_EOI, previous_span,
                    ErrorContext(["int", "float", "string", "section"], "EOI"))

    match token.ty:
        case TokenType.TT_STR | TokenType.TT_INT | TokenType.TT_FLOAT:
            return token.value, token.location

        case JsonToken.TT_LBRACKET:
            return parse_section(token.location, it)

    raise Error("Syntax error", previous_span, ErrorContext(["int, float", "string", "section"], token.ty))


def parse_field(previous_span: Span, it: TokenIterator) -> (str, any, Span):
    if not (key := it.next()):
        raise Error(BuiltinErrors.UNEXPECTED_EOI, previous_span, ErrorContext(["key"], "EOI"))

    if not (colon := it.next()):
        raise Error(BuiltinErrors.UNEXPECTED_EOI, key.location, ErrorContext(["colon"], "EOI"))

    value, span = parse_value(colon.location, it)
    return key.value, value, span


def main() -> None:
    lexer = Lexer([JSONSymbolRule(), StringRule(), NumberRule()])
    text = input("Enter JSON: ")

    try:
        tokens = lexer.lex(text)
        print(tokens)

        if tokens:
            entries = parse_section(tokens[0].location, TokenIterator(tokens))
            print(f"Parsed entries: {entries}")

    except Error as err:
        err.pretty_print(text)


if __name__ == "__main__":
    main()
