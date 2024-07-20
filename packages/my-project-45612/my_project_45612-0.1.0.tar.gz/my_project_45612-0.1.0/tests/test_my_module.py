
import unittest
from my_project import my_module

class TestMyModule(unittest.TestCase):
    def test_example(self):
        self.assertEqual(my_module.example_function(), expected_output)

if __name__ == '__main__':
    unittest.main()