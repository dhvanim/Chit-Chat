import unittest
import unittest.mock as mock
from os.path import dirname, join
import sys
sys.path.append(join(dirname(__file__), "../"))
import app
import bot
import alchemy_mock


KEY_INPUT = "input"
KEY_EXPECTED = "expected"
KEY_QUERY = "query"
KEY_RESPONSE = "get_response"

EXPECTED_CHANNEL = "expected channel"
EXPECTED_DATA = "expected data"


class EmitUsersActiveTest(unittest.TestCase):
    
    def setUp(self):
        self.success_test_params = [
            {
                KEY_QUERY: ["<ActiveUsers 1", "<ActiveUsers 2"],
                KEY_EXPECTED: {
                    EXPECTED_CHANNEL: "active users channel",
                    EXPECTED_DATA: {"users":2}
                }
            }
        ]
            
    
    @mock.patch('app.socketio.emit')
    def test_emit_users_active_success(self, mocked_socket):

        for test in self.success_test_params:
            
            mocked_active = mock.MagicMock()
            mocked_active.query.all.return_value = [3, 4]
            
            with mock.patch("app.ActiveUsers", mocked_active):
                
                app.emit_users_active()
                
            expected = test[KEY_EXPECTED]
            mocked_socket.assert_called_once_with( expected[EXPECTED_CHANNEL], expected[EXPECTED_DATA] )
    
class GetUsernameTest(unittest.TestCase):
    def setUp(self):
        self.success_test_params = [
            {
                KEY_INPUT: 1234,
                KEY_EXPECTED: "jan3apples"
            },
        ]

    def test_get_username(self):
        for test in self.success_test_params:
            
            mocked_users = mock.MagicMock()
            mocked_users.query.filter_by.return_value.first.return_value.username = test[KEY_EXPECTED]
            
            with mock.patch("app.ActiveUsers", mocked_users):
                response = app.get_username(test[KEY_INPUT])
            
            self.assertEqual(response, test[KEY_EXPECTED])
            

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


class BotSpotifyTest(unittest.TestCase):
    def setUp(self):
        self.success_test_params = [
        {
            KEY_INPUT: "omar apollo",
            KEY_EXPECTED: "You should listen to the song Ignorin' by Omar Apollo!! It's one of my favorites :D"
        },
        {
            KEY_INPUT: " ",
            KEY_EXPECTED: "Sorry! No artist found :-("
        },
        {
            KEY_INPUT: 2,
            KEY_EXPECTED: "Sorry! Connection error :-("
        }
        ]
    
    def mocked_access_token(self):
        return "temptoken"
    
    def mocked_spotify_get_request(self, url, headers, params):
        response_mock = mock.Mock()
        response_mock.json.return_value = { 'artists':{'total':1, 'items':[{'id':"fakeid", 'name': "Omar Apollo"}] }, 'tracks':[{'name': "Ignorin'"}] }
        response_mock.status_code = 200
        
        if 'q' in params and params['q'] == " ":
            response_mock.json.return_value ={ 'artists':{'total':0, 'items':[{}]}, 'tracks':[{'name': ""}] }
        
        if 'q' in params and params['q'] == 2:
            response_mock.status_code = 500
        
        return response_mock
    
    @mock.patch('bot.spotify_get_access_token')
    def test_bot_spotify_success(self, mocked_access_token):
        mocked_access_token = self.mocked_access_token
        
        for test in self.success_test_params:
            with mock.patch('bot.requests.get', self.mocked_spotify_get_request):
                response = bot.bot_spotify( test[KEY_INPUT] )
            self.assertEqual(test[KEY_EXPECTED], response)


class BotTranslateTest(unittest.TestCase):
    def setUp(self):
        self.success_test_params = [
            {
                KEY_INPUT: "morse",
                KEY_EXPECTED: "-- --- .-. ... ."
            },
            {
                KEY_INPUT: 3,
                KEY_EXPECTED: "Sorry! Could not translate :-("
            }
        ]
        self.failure_test_params = [
            {
                KEY_INPUT: "",
                KEY_EXPECTED: ""
            }
        ]
      
    def mocked_translate_response(self, url, params):
        response_mock = mock.Mock()
        if params["text"] == "morse":
            response_mock.json.return_value = {'success': {'total':1}, 'contents':{'translated': "-- --- .-. ... ."}}
        else:
            response_mock.json.return_value = {'success': {'total':0}, 'contents':{'translated': ""}}
        
        return response_mock
        
    def test_bot_translate_success(self):
        for test in self.success_test_params:
            
            with mock.patch("app.requests.get", self.mocked_translate_response):
                    translated = bot.bot_translate(test[KEY_INPUT])
            expected = test[KEY_EXPECTED]
            
            self.assertEqual(expected, translated)
    
    def test_bot_translate_failure(self):
        for test in self.failure_test_params:
            with mock.patch("app.requests.get", self.mocked_translate_response):
                    translated = bot.bot_translate(test[KEY_INPUT])
            expected = test[KEY_EXPECTED]
            
            self.assertNotEqual(expected, translated)
            
    

 

if __name__ == '__main__':
    unittest.main()