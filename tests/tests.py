from src.soliz.error import Error
from src.soliz.lex import Lexer
from src.soliz.impls import StringRule, NumberRule, TokenType, SpaceRule

import unittest


class TestBuiltinLex(unittest.TestCase):
    def test_tt_string(self) -> None:
        lexer = Lexer([SpaceRule(), StringRule()])
        token = lexer.lex(""" "Hello, sir!" """).tokens[1]

        self.assertEqual(token.ty, TokenType.TT_STRING)
        self.assertEqual(token.value, "Hello, sir!")

        self.assertRaises(Error, lambda: lexer.lex(""" "tes"""))

    def test_tt_numbers(self) -> None:
        lexer = Lexer([SpaceRule(), NumberRule()])
        tokens = lexer.lex(""" 4.5 8 -4.1""").tokens

        self.assertEqual(tokens[1].value, 4.5)
        self.assertEqual(tokens[3].value, 8)
        self.assertEqual(tokens[5].value, -4.1)


if __name__ == '__main__':
    unittest.main()
