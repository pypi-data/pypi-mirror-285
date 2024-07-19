# tests/test_sample.py
import unittest
from llms import some_function  # Import the function you want to test from your module

class TestSample(unittest.TestCase):

    def test_some_function(self):
        result = some_function()
        self.assertEqual(result, expected_value)

if __name__ == '__main__':
    unittest.main()
