import unittest

from utilset import list


class TestList(unittest.TestCase):

    def test_unique(self):
        l = [1, 2, 1, 3]
        list.unique(l)
        self.assertEqual(list.unique(l), [1, 2, 3])

    def test_unique(self):
        l = [1, 2, 1, 3]

        self.assertEqual(list.get(l, 2), 1)
        self.assertEqual(list.get(l, 12), '')
        self.assertEqual(list.get(l, 12, 0), 0)


if __name__ == '__main__':
    unittest.main()