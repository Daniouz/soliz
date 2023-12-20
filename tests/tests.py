from src.soliz.error import Error
from src.soliz.lex import Lexer
from src.soliz.impls import StringRule, NumberRule, TokenType

import unittest


class TestBuiltinLex(unittest.TestCase):
    def test_tt_string(self) -> None:
        lexer = Lexer([StringRule()])
        token = lexer.lex(""" "Hello, sir!" """)[0]

        self.assertEqual(token.ty, TokenType.TT_STR)
        self.assertEqual(token.value, "Hello, sir!")

        self.assertRaises(Error, lambda: lexer.lex(""" "tes"""))

    def test_tt_numbers(self) -> None:
        lexer = Lexer([NumberRule()])
        tokens = lexer.lex(""" 4.5 8 -4.1""")

        self.assertEqual(tokens[0].value, 4.5)
        self.assertEqual(tokens[1].value, 8)
        self.assertEqual(tokens[2].value, -4.1)


if __name__ == '__main__':
    unittest.main()
