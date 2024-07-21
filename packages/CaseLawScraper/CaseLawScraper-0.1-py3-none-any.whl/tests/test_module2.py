import unittest
from CaseLawScraper.module2 import hello_world

class TestModule2(unittest.TestCase):
    def test_hello_world(self):
        self.assertIsNone(hello_world())

if __name__ == '__main__':
    unittest.main()
