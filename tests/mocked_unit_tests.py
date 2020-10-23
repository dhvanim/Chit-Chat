import unittest
from os.path import dirname, join
import sys
sys.path.append(join(dirname(__file__), "../"))
import app
import bot

KEY_INPUT = "input"
KEY_EXPECTED = "expected"

class MockedTestCase(unittest.TestCase):
    def setUp(self):
        self.success_test_params = []
        
        self.failure_test_params = []
    
    def test_handle_links_success(self):
        return
    
    def test_handle_links_failure(self):
        return

if __name__ == '__main__':
    unittest.main()