import unittest

from utilset import email


class TestEmail(unittest.TestCase):

    def test_is_valid(self):
        self.assertTrue(email.is_valid("user@puresai.com"))
        self.assertFalse(email.is_valid("user@puresai."))
        self.assertFalse(email.is_valid("user@puresai.com."))
        self.assertFalse(email.is_valid("puresai.com"))
        self.assertTrue(email.is_valid("user@13sai.com"))


if __name__ == '__main__':
    unittest.main()