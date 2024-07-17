import unittest

from utilset import dict


class TestFile(unittest.TestCase):

    def test_value_is_empty(self):
        d = {"a": 1}
        self.assertFalse(dict.value_is_empty(d, "a"))
        self.assertTrue(dict.value_is_empty(d, "b"))


if __name__ == '__main__':
    unittest.main()