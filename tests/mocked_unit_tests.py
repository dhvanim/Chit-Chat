import unittest
import app
import bot

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