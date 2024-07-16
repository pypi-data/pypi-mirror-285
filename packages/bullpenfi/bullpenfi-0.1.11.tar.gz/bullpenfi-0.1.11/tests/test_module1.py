import unittest
from bullpenfi.ping import example_function, restricted_function


class TestExampleFunction(unittest.TestCase):
    def test_example_function(self):
        api_key = "your-valid-api-key-1"
        self.assertEqual(example_function(api_key), "Hello, PyPI!")

    def test_restricted_function(self):
        api_key = "your-valid-api-key-1"
        self.assertEqual(restricted_function(api_key), "This is a restricted function")


if __name__ == "__main__":
    unittest.main()
