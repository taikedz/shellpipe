import unittest

import shellpipe.tokenizer as TK

class TokenizerTester(unittest.TestCase):

    def test_parse_normal(self):
        self.assertEqual( TK.parse("a b") , ["a", "b"] )

    def test_parse_quoted(self):
        self.assertEqual(TK.parse("a 'b c' 'de'"+' "e f" g') , ["a", "b c", "de", "e f", "g"] )

    def test_parse_quotedspace(self):
        self.assertEqual(TK.parse('a"b c"d') , ["ab cd"])
        self.assertEqual(TK.parse("a'b c'") , ["ab c"])

    def test_parse_escaping(self):
        self.assertEqual(TK.parse(r"a\ b"), ["a b"])
        self.assertEqual(TK.parse(r"a\\ b"), ["a\\","b"])

    def test_parse_embedded_quote(self):
        self.assertEqual(TK.parse('''"it's a commit"'''), ["it's a commit"])
        self.assertEqual(TK.parse("""'My "true" commit'"""), ['My "true" commit'])


if __name__ == "__main__":
    unittest.main()
