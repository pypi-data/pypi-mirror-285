import unittest

from utilset import string


class TestString(unittest.TestCase):

    def test_concat(self):
        self.assertEqual(string.concat("a", "b", "c"), "abc")

    def test_md5(self):
        self.assertEqual(string.md5("abc"), "900150983cd24fb0d6963f7d28e17f72")

    def test_is_empty(self):
        self.assertFalse(string.is_empty("abc"))
        self.assertTrue(string.is_empty(""))
        self.assertTrue(string.is_empty(None))


if __name__ == '__main__':
    unittest.main()