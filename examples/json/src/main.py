from typing import Tuple

from src.soliz.error import Error, ErrorContext, BuiltinErrors
from src.soliz.impls import StringRule, NumberRule, TokenType, EolRule, SpaceRule
from src.soliz.lex import Lexer, Rule, Context
from src.soliz.tokens import Token, Span


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
        self.token = tokens[0] if tokens else None
        self.index = 0

    def advance(self) -> None:
        self.index += 1
        self.token = None if self.index >= len(self.tokens) else self.tokens[self.index]

    def next(self) -> Token | None:
        self.advance()
        return self.token

    def advance_not_eoi(self, expected: list[str]) -> None:
        previous_span = self.token.location
        self.advance()

        if not self.token:
            raise Error(BuiltinErrors.UNEXPECTED_EOI, previous_span, ErrorContext(expected, "EOI"))

    def has_next(self):
        return self.index + 1 < len(self.tokens)


def parse_section(it: TokenIterator) -> dict[str, any]:
    if it.token.ty != JsonToken.TT_LBRACKET:
        raise Error("Syntax error", it.token.location, ErrorContext(["'{'"], it.token.ty))

    entries = {}

    while it.has_next():
        it.advance()

        if it.token.ty == JsonToken.TT_RBRACKET:
            return entries

        key, value = parse_field(it)
        entries[key] = value

        it.advance_not_eoi(["'}'", "','"])

        match it.token.ty:
            case JsonToken.TT_RBRACKET:
                return entries

            case JsonToken.TT_COMMA:
                continue

            case _:
                break

    raise Error("Syntax error", it.token.location, ErrorContext(["field", "'}'"], it.token.ty))


def parse_value(it: TokenIterator) -> any:
    it.advance_not_eoi(["int", "float", "string", "section"])

    match it.token.ty:
        case TokenType.TT_STR | TokenType.TT_INT | TokenType.TT_FLOAT:
            return it.token.value

        case JsonToken.TT_LBRACKET:
            return parse_section(it)

    raise Error("Syntax error", it.token.location, ErrorContext(["int, float", "string", "section"], it.token.ty))


def parse_field(it: TokenIterator) -> (str, any, Span):
    if it.token.ty != TokenType.TT_STR:
        raise Error("Syntax error", it.token.location, ErrorContext(["string"], it.token.ty))

    key = it.token.value
    it.advance_not_eoi(["colon"])

    if it.token.ty != JsonToken.TT_COLON:
        raise Error("Syntax error", it.token.location, ErrorContext(["':'"], it.token.ty))

    value = parse_value(it)
    return key, value


def main() -> None:
    lexer = Lexer([SpaceRule(True), EolRule(), JSONSymbolRule(), StringRule(), NumberRule()])
    text = input("Enter JSON: ")

    try:
        res = lexer.lex(text)
        res.discard_types(TokenType.TT_SPACE, TokenType.TT_EOL)

        print(res.tokens)

        if res.tokens:
            entries = parse_section(TokenIterator(res.tokens))
            print(f"Parsed entries: {entries}")

    except Error as err:
        err.pretty_print(text)


if __name__ == "__main__":
    main()
