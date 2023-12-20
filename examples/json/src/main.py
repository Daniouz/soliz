from typing import Tuple

from src.soliz.error import Error
from src.soliz.impls import StringRule, NumberRule
from src.soliz.lex import Lexer, Rule, Context
from src.soliz.tokens import Token


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


if __name__ == "__main__":
    main()
