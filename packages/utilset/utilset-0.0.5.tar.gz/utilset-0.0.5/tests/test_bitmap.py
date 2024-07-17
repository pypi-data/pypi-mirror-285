import unittest

from utilset import Bitmap


class TestBitmap(unittest.TestCase):

    def test_bitmap(self):
        bm = Bitmap.Bitmap(10)
        bm.set(2)
        bm.set(7)
        self.assertTrue(bm.test(2))
        self.assertFalse(bm.test(3))


if __name__ == "__main__":
    unittest.main()
