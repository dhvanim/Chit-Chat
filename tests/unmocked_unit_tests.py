import unittest
from os.path import dirname, join
import sys
sys.path.append(join(dirname(__file__), "../"))
import app
import bot

KEY_INPUT = "input"
KEY_EXPECTED = "expected"

class HandleLinksTestCase(unittest.TestCase):
    def setUp(self):
        self.success_test_params = [
            {
                KEY_INPUT: "https",
                KEY_EXPECTED: "text"
            },
            {
                KEY_INPUT: "https://docs.python.org/2/library/unittest.html",
                KEY_EXPECTED: "link"
            },
            {
                KEY_INPUT: "https://static.boredpanda.com/blog/wp-content/uploads/2019/12/5e04ab9720e95_nrh43dai3hfy__700.jpg",
                KEY_EXPECTED: "image"
            }
        ]
        
        self.failure_test_params = [
            {
                KEY_INPUT: "https://docs.python.org/2/library/unittest.html hello!",
                KEY_EXPECTED: "link"
            },
            {
                KEY_INPUT: "https://docs.python.org/2/library/unittest.html",
                KEY_EXPECTED: "text"
            },
            {
                KEY_INPUT: "https://www.sciencemag.org/sites/default/files/styles/article_main_large/public/butterfly_16x9_0.jpg?itok=jZ3DYvGK",
                KEY_EXPECTED: "link"
            }
        ]
    
    def test_handle_links_success(self):
        for test in self.success_test_params:
            response = app.handle_links(test[KEY_INPUT])
            expected = test[KEY_EXPECTED]
            
            self.assertEqual(response, expected)
    
    def test_handle_links_failure(self):
        for test in self.failure_test_params:
            response = app.handle_links(test[KEY_INPUT])
            expected = test[KEY_EXPECTED]
            
            self.assertNotEqual(response, expected)

class HandleBotTestCase(unittest.TestCase):
    def setUp(self):
        self.success_test_params = [
        {
            KEY_INPUT: "!! about",
            KEY_EXPECTED: "Hi guys! My name is chit-chat-bot and I'm here to help! Type '!! help' to learn more :-))"
        }, 
        {
            KEY_INPUT: "!!",
            KEY_EXPECTED: None
        }, 
        {
            KEY_INPUT: "!! !",
            KEY_EXPECTED: "( !!  ! ) Command unknown. Type '!! help' for a list of commands :p"
        } 
        ]
        
        self.failure_test_params = [
        {
            KEY_INPUT: "!! help",
            KEY_EXPECTED: "Here are a list of commands you can ask me: "
        }, 
        {
            KEY_INPUT: "!!",
            KEY_EXPECTED: "( !! ) Command unknown. Type '!! help' for a list of commands :p"
        } 
        ]
        
    def test_handle_bot_success(self):
        for test in self.success_test_params:
            response = app.handle_bot(test[KEY_INPUT])
            expected = test[KEY_EXPECTED]
            
            self.assertEqual(response, expected)
    
    def test_handle_bot_failure(self):
        for test in self.failure_test_params:
            response = app.handle_bot(test[KEY_INPUT])
            expected = test[KEY_EXPECTED]
            
            self.assertNotEqual(response, expected)


if __name__ == '__main__':
    unittest.main()