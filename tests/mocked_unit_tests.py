import unittest
import unittest.mock as mock
from os.path import dirname, join
import sys
sys.path.append(join(dirname(__file__), "../"))
import app
import bot
import json


KEY_INPUT = "input"
KEY_EXPECTED = "expected"

class MockedSocket(unittest.TestCase):
    def emit(self, channel, data):
        client = app.socketio.test_client(app.app)
        client.get_received()
        client.emit(channel, data)
        
        return channel, data
    
    def emit_assert_called_with(self,channel, data):
        emitted_info = self.emit(channel, data)
        
        self.assertEqual(emitted_info[0], channel)
        self.assertEqual(emitted_info[1], data)
        
EXPECTED_CHANNEL = "expected channel"
EXPECTED_DATA = "expected data"

class EmitUsersActiveTest(unittest.TestCase):
    
    def setUp(self):
        self.success_test_params = [
            {
                KEY_INPUT: self.mocked_active_users_query(),
                KEY_EXPECTED: {
                    EXPECTED_CHANNEL: "active users channel",
                    EXPECTED_DATA: {"users":2}
                }
            }
        ]
    
    def mocked_active_users_query(self):
        return [4, 4]
    
    @mock.patch('app.socketio.emit')
    def test_emit_users_active_success(self, mocked_socket):

        for test in self.success_test_params:
            
            with mock.patch("app.ActiveUsers.query.all", self.mocked_active_users_query):
                app.emit_users_active()
                
            expected = test[KEY_EXPECTED]
            mocked_socket.assert_called_once_with( expected[EXPECTED_CHANNEL], expected[EXPECTED_DATA] )
            

class UserChatStatusTest(unittest.TestCase):
    def setUp(self):
        self.success_test_params = [
            {
                KEY_INPUT: "hello",
                KEY_EXPECTED: {
                    EXPECTED_CHANNEL: "chat log channel",
                    EXPECTED_DATA: {'chat_log': {'username':"", 'message':"hello", 'timestamp':""}, 'timestamp':""}
                }
            }]
      
    @mock.patch('app.socketio.emit')
    def test_emit_users_active_success(self, mocked_socket):
        for test in self.success_test_params:
            
            app.user_chat_status( test[KEY_INPUT] )
                
            expected = test[KEY_EXPECTED]
            mocked_socket.assert_called_once_with( expected[EXPECTED_CHANNEL], expected[EXPECTED_DATA] )

'''
class BotSpotifyTest(unittest.TestCase):
    def setUp(self):
        self.success_test_params = [
        {
            KEY_INPUT: "omar apollo",
            KEY_EXPECTED: []
        }
        ]
        
        self.failure_test_params = []
    
    def test_handle_links_success(self):
        return
    
'''
class BotTranslateTest(unittest.TestCase):
    def setUp(self):
        self.success_test_params = [
            {
                KEY_INPUT: "morse",
                KEY_EXPECTED: "-- --- .-. ... ."
            },
        ]
        self.failure_test_params = []
      
    def mocked_translate_response(self, url, params):
        class MockResponse:
            def __init__(self, json_data):
                self.json_data = json_data
            
            def json(self):
                return self.json_data
                
        return MockResponse({'success': {'total':1}, 'contents':{'translated': "-- --- .-. ... ."}})
            
        
        
    def test_bot_translate_success(self):
        for test in self.success_test_params:
            
            with mock.patch("app.requests.get", self.mocked_translate_response):
                    translated = bot.bot_translate(test[KEY_INPUT])
            
            expected = test[KEY_EXPECTED]
            
            self.assertEqual(expected, translated)
            
            
    

 

if __name__ == '__main__':
    unittest.main()