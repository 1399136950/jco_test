import unittest


class TestSub(unittest.TestCase):
    def setUp(self):
        print("test case start")

    def tearDown(self):
        print("test case end")

    def test_sub(self):
        self.assertEqual(2-3, -1)

    def test_sub2(self):
        self.assertEqual(4+7, 5)


if __name__ == '__main__':
    unittest.main()
