import unittest

from utilset import file


class TestFile(unittest.TestCase):

    def test_get_content_line(self):
        file.save_content("test.log", "puresai")
        self.assertEqual(file.get_content_line("test.log"), "puresai")


if __name__ == '__main__':
    unittest.main()