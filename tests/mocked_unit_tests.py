import unittest
import unittest.mock as mock
from os.path import dirname, join
import sys
sys.path.append(join(dirname(__file__), "../"))
import app
import bot

from datetime import datetime
from alchemy_mock.mocking import UnifiedAlchemyMagicMock

KEY_INPUT = "input"
KEY_EXPECTED = "expected"
KEY_QUERY = "query"
KEY_RESPONSE = "response"
KEY_TIME = "time"
KEY_ROOM = "room"

EXPECTED_CHANNEL = "channel"
EXPECTED_DATA = "data"
EXPECTED_ROOM = "room"


class LoggedOnTest(unittest.TestCase):
    def setUp(self):
        self.success_test_params = [
            {
                KEY_INPUT: "1234",
                KEY_EXPECTED: True
            },
            {
                KEY_INPUT: "",
                KEY_EXPECTED: False
            }
        ]
    
    def test_logged_on(self):
        
        mocked_activeusersquery = mock.MagicMock()
        
        for test in self.success_test_params:
            if test[KEY_INPUT] == "":
                mocked_activeusersquery.query.filter_by.return_value.first.return_value = None
                
            with mock.patch("app.ActiveUsers", mocked_activeusersquery):
                app.logged_on(test[KEY_INPUT])

class EmitChatLogTest(unittest.TestCase):
    def setUp(self):
        self.success_test_params = [
            {
                KEY_INPUT: {
                    KEY_TIME: None,
                    KEY_ROOM: None
                },
                KEY_EXPECTED: {
                    EXPECTED_CHANNEL: "chat log channel",
                    EXPECTED_DATA: {'chat_log': ["mock", "2", "2"], 'timestamp':0},
                }
            },
            {
                KEY_INPUT: {
                    KEY_TIME: datetime.now(),
                    KEY_ROOM: None
                },
                KEY_EXPECTED: {
                    EXPECTED_CHANNEL: None,
                    EXPECTED_DATA: None,
                }
            },
            {
                KEY_INPUT: {
                    KEY_TIME: None,
                    KEY_ROOM: 2345
                },
                KEY_EXPECTED: {
                    EXPECTED_CHANNEL: "chat log channel",
                    EXPECTED_DATA: {'chat_log': ["mock", "2", "2"], 'timestamp':0},
                    EXPECTED_ROOM: 2345
                }
            },
        ]
        
    def mocked_get_chat_log(self, timestamp):
        mocked_log = mock.MagicMock()
        if timestamp == None:
            mocked_log.return_value = ["mock", "2", "2"]
        else:
            mocked_log.return_value = []
        return mocked_log
    
    @mock.patch('app.socketio.emit')
    def test_emit_chat_log(self, mocked_socket):
        for test in self.success_test_params:
            mocked_socket.reset_mock()
            mocked_log = self.mocked_get_chat_log(test[KEY_INPUT][KEY_TIME])
            
            with mock.patch("app.get_chat_log", mocked_log):
                app.emit_chat_log(test[KEY_INPUT][KEY_TIME], test[KEY_INPUT][KEY_ROOM])
            
            expected = test[KEY_EXPECTED]
            
            if test[KEY_INPUT][KEY_TIME] == None:
                if EXPECTED_ROOM in expected:
                    mocked_socket.assert_called_once_with( expected[EXPECTED_CHANNEL], expected[EXPECTED_DATA], room=expected[EXPECTED_ROOM] )
                else:
                    mocked_socket.assert_called_once_with( expected[EXPECTED_CHANNEL], expected[EXPECTED_DATA])

    
class GetChatLogTest(unittest.TestCase):
    def setUp(self):
        self.success_test_params = [
            {
                KEY_INPUT: 0,
                KEY_EXPECTED: [{
                    "username" : "jane3apples",
                    "auth": "Google",
                    "icon": "httpiconpic",
                    "message" :"hey guys what's up",
                    "timestamp": "08.23.99",
                    "message_type": "text"
                }]
            }
        ]
    
    def mocked_entry(self):
        entry = mock.MagicMock()
        entry.username = "jane3apples"
        entry.auth = "Google"
        entry.icon = "httpiconpic"
        entry.message = "hey guys what's up"
        entry.timestamp = "08.23.99"
        entry.message_type = "text"
        return entry
        
    def mocked_get_log(self):
        mocked_log = mock.MagicMock()
        mock_entry = self.mocked_entry()
        mocked_log.query.all.return_value = [mock_entry]
        
        return mocked_log
    
    def test_get_chat_log_success(self):
        for test in self.success_test_params:
            
            mocked_log = self.mocked_get_log()
            with mock.patch("app.ChatLog", mocked_log):
                output = app.get_chat_log( test[KEY_INPUT] )
            
            self.assertEqual(output, test[KEY_EXPECTED])
  
class SaveMessageTest(unittest.TestCase):
    def setUp(self):
        self.success_test_params = [
            {
                KEY_INPUT: {
                    "mssg": "hello"
                },
                KEY_EXPECTED: {
                    "username" : "jane3apples",
                    "auth": "Google",
                    "icon": "httpiconpic",
                    "message" :"hello",
                    "timestamp": "08.23.99",
                    "message_type": "text"
                }
            }
        ]
        
    def mock_get_serverid(self):
        mock_id = mock.MagicMock()
        mock_id.return_value = "1234"
        return mock_id
        
    def mock_username(self):
        mock_user = mock.MagicMock()
        mock_user.return_value = "jane3apples"
        return mock_user
        
    def mock_get_userinfo(self):
        mocked_userinfo = mock.MagicMock()
        mock_user = mock.MagicMock()
        mock_user.auth = "Google"
        mock_user.icon = "httpiconpic"
        mocked_userinfo.query.filter_by.return_value.first.return_value = mock_user
        return mocked_userinfo
        
    
    @mock.patch('app.get_serverid')
    @mock.patch('app.get_username')
    @mock.patch('app.ActiveUsers')
    @mock.patch('app.ChatLog')
    @mock.patch('app.db.session')
    @mock.patch('app.emit_chat_log')
    def test_save_message(self, mock_serverid, mock_user, mocked_activeusersquery, mocked_chatlog, mocked_dbsession, mocked_emitchatlog):
        
        mock_serverid = self.mock_get_serverid()
        mock_user = self.mock_username()
        mocked_activeusersquery = self.mock_get_userinfo()
        mocked_chatlog = mock.create_autospec(app.ChatLog)
        mocked_dbsession = UnifiedAlchemyMagicMock()
        mocked_dbsession.add(mocked_chatlog(username="", auth="", icon="", message="", timestamp="", message_type=""))
        
        mocked_emitchatlog = mock.MagicMock()
        
        for test in self.success_test_params:
            app.save_message( test[KEY_INPUT] )
            
            add = test[KEY_EXPECTED]
            mocked_dbsession.add.assert_called()
    
class EmitUsersActiveTest(unittest.TestCase):
    
    def setUp(self):
        self.success_test_params = [
            {
                KEY_QUERY: ["<ActiveUsers 1>", "<ActiveUsers 2>"],
                KEY_EXPECTED: {
                    EXPECTED_CHANNEL: "active users channel",
                    EXPECTED_DATA: {"users":2}
                }
            }
        ]
    
    def mock_get_active_users(self):
        mocked_active = mock.MagicMock()
        mocked_active.query.all.return_value = [3, 4]
        return mocked_active
        
    @mock.patch('app.socketio.emit')
    def test_emit_users_active_success(self, mocked_socket):

        for test in self.success_test_params:
            
            mocked_active = self.mock_get_active_users()
            with mock.patch("app.ActiveUsers", mocked_active):
                
                app.emit_users_active()
                
            expected = test[KEY_EXPECTED]
            mocked_socket.assert_called_once_with( expected[EXPECTED_CHANNEL], expected[EXPECTED_DATA] )
    

class MessageRecieveFailTest(unittest.TestCase):
    
    def setUp(self):
        self.success_test_params = [
            {
                KEY_INPUT: "jan3apples",
                KEY_EXPECTED: {
                    EXPECTED_CHANNEL: "chat log channel",
                    EXPECTED_DATA: {"username":"", 'message':"ERROR: Message from jan3apples failed to send.", "timestamp":""}
                }
            }
        ]
        
    @mock.patch('app.socketio.emit')
    def test_emit_users_active_success(self, mocked_socket):

        for test in self.success_test_params:
            
            app.message_recieve_fail(test[KEY_INPUT])
                
            expected = test[KEY_EXPECTED]
            data = {'chat log': expected[EXPECTED_DATA], 'timestamp':""}
            mocked_socket.assert_called_once()

    
class GetUsernameTest(unittest.TestCase):
    def setUp(self):
        self.success_test_params = [
            {
                KEY_INPUT: 1234,
                KEY_EXPECTED: "jan3apples"
            },
        ]
    
    def mock_get_users(self):
        mocked_users = mock.MagicMock()
        mocked_users.query.filter_by.return_value.first.return_value.username = "jan3apples"
        return mocked_users    

    def test_get_username_success(self):
        for test in self.success_test_params:
            
            mocked_users = self.mock_get_users()
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

class BotSaveMessageTest(unittest.TestCase):
    def setUp(self):
        self.success_test_params = [
            {
                KEY_INPUT: "test bot message"
            }
        ]
        
    @mock.patch('app.db.session')
    @mock.patch('app.ChatLog')
    @mock.patch('app.emit_chat_log')
    def test_bot_save_message(self, mocked_dbsession, mocked_chatlog, mocked_emitchatlog):
        
        mocked_dbsession = UnifiedAlchemyMagicMock()
        mocked_chatlog = mock.create_autospec(app.ChatLog)
        mocked_dbsession.add(mocked_chatlog())
        mocked_emitchatlog = mock.MagicMock()
        
        for test in self.success_test_params:
            app.bot_save_message( test[KEY_INPUT] )
            
            mocked_dbsession.add.assert_called()

class HandleBotTest(unittest.TestCase):
    def setUp(self):
        self.success_test_params = [
            {
                KEY_INPUT: "!! translate hello there",
                KEY_EXPECTED: ".... . .-.. .-.. --- / - .... . .-. ."
            },
            {
                KEY_INPUT: "!! spotify omar",
                KEY_EXPECTED: "You should listen to the song Ignorin' by Omar Apollo!! It's one of my favorites :D"
            },
            {
                KEY_INPUT: "!! time",
                KEY_EXPECTED: "You have been online for approximately 11 seconds and 3434 microseconds :o"
            }
        ]
        
    def mock_translate(self):
        translate = mock.MagicMock()
        translate.return_value = ".... . .-.. .-.. --- / - .... . .-. ."
        return translate
    
    def mock_spotify(self):
        spotify = mock.MagicMock()
        spotify.return_value = "You should listen to the song Ignorin' by Omar Apollo!! It's one of my favorites :D"
        return spotify
    
    def mock_time(self):
        time = mock.MagicMock()
        time.return_value = "You have been online for approximately 11 seconds and 3434 microseconds :o"
        return time
    
    def mock_server(self):
        server = mock.MagicMock()
        server.return_value = "1234"
        return server
        
    def mock_username(self):
        username = mock.MagicMock()
        username.return_value = "jane3apples"
        return username
        
    def mock_active_users_query(self):
        mocked_users = mock.MagicMock()
        time = mock.MagicMock()
        time.timestamp = "2020"
        mocked_users.query.filter_by.return_value.first.return_value = time
        return mocked_users
    
    def test_handle_bot(self):
        
        mocked_translate = self.mock_translate()
        mocked_spotify = self.mock_spotify()
        mocked_time = self.mock_time()
        mocked_serverid = self.mock_server()
        mocked_username = self.mock_username()
        mocked_activeusersquery = self.mock_active_users_query()
        
        for test in self.success_test_params:
            with mock.patch("app.bot.bot_translate", mocked_translate),\
            mock.patch("app.bot.bot_spotify", mocked_spotify),\
            mock.patch("app.bot.bot_time", mocked_time),\
            mock.patch("app.get_serverid", mocked_serverid),\
            mock.patch("app.get_username", mocked_username),\
            mock.patch("app.ActiveUsers", mocked_activeusersquery):
                
                response = app.handle_bot(test[KEY_INPUT])
                
                self.assertEqual(response, test[KEY_EXPECTED])
                
            
            
class BotCommandNoneTest(unittest.TestCase):
    def setUp(self):
        self.success_test_params = [
            {
                KEY_INPUT: "!! nope",
                KEY_EXPECTED: None
            },
        ]
    
    def mocked_handle_bot(self, message):
            return None
        
    def test_bot_command_success(self):
        for test in self.success_test_params:
            
            with mock.patch("app.handle_bot", self.mocked_handle_bot):
                with mock.patch("app.bot_save_message", self.mocked_handle_bot):
                    response = app.bot_command( test[KEY_INPUT] )
            
            self.assertEqual(response, test[KEY_EXPECTED])
            

class BotTimeResponseTest(unittest.TestCase):
    def setUp(self):
        self.success_test_params = [
            {
                KEY_INPUT: datetime(2020, 10, 21, 18, 52, 10, 534278),
                KEY_EXPECTED: "You have been online for approximately 9529 hours, 1 minutes, 1 seconds and 1 microseconds :o"
            }
        ]
    
    def mock_get_current_time(self):
        mock_dt = mock.MagicMock()
        mock_dt.now.return_value = datetime(2021, 11, 22, 19, 53, 11, 534279)
        return mock_dt

    def test_bot_time_response(self):
        for test in self.success_test_params:
            
            mock_dt = self.mock_get_current_time()
            with mock.patch("bot.datetime", mock_dt):
                response = bot.bot_time(test[KEY_INPUT])
            self.assertEqual(response, test[KEY_EXPECTED])


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
            
            with mock.patch("bot.requests.get", self.mocked_translate_response):
                    translated = bot.bot_translate(test[KEY_INPUT])
            expected = test[KEY_EXPECTED]
            
            self.assertEqual(expected, translated)
    
    def test_bot_translate_failure(self):
        for test in self.failure_test_params:
            with mock.patch("bot.requests.get", self.mocked_translate_response):
                    translated = bot.bot_translate(test[KEY_INPUT])
            expected = test[KEY_EXPECTED]
            
            self.assertNotEqual(expected, translated)
            
    

 

if __name__ == '__main__':
    unittest.main()