import unittest
from vivid import hello_world

class TestVivid(unittest.TestCase):
    def test_hello_world(self):
        self.assertIsNone(hello_world())

if __name__ == '__main__':
    unittest.main()
 
