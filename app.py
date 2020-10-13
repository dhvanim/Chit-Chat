from os.path import join, dirname
from dotenv import load_dotenv
import os
import flask
import flask_sqlalchemy
import flask_socketio
from flask_socketio import join_room, leave_room
from datetime import datetime
import requests
import random
import bot

# set up flask app, db, and socket
app = flask.Flask(__name__)

app.static_folder = 'static'

socketio = flask_socketio.SocketIO(app)
socketio.init_app(app, cors_allowed_origins="*")

dotenv_path = join(dirname(__file__), 'sql.env')
load_dotenv(dotenv_path)

sql_user = os.environ['SQL_USER']
sql_pwd = os.environ['SQL_PASSWORD']
dbuser = os.environ['USER']

database_uri = 'postgresql://{}:{}@localhost/postgres'.format(sql_user,sql_pwd)

app.config['SQLALCHEMY_DATABASE_URI'] = database_uri

db = flask_sqlalchemy.SQLAlchemy(app)
db.init_app(app)
db.app = app



### ### ### ### ### ### ### ### ### ### ### ### ###
''' temporary until i can fix the import issue '''

# temp table - delete later
class TestTable(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    testmessage = db.Column(db.String(280))
    
    def __init__(self, m):
        self.testmessage = m
    
    def __repr__(self):
        return '<TestTable message: %s>' % self.testmessage 

# chat log table with userid, message, timestamp
class ChatLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    userid = db.Column(db.String(280), nullable=False)
    message = db.Column(db.String(280))
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
        
    def __init__(self, u, m, t):
        self.userid = u
        self.message = m
        self.timestamp = t
        
    def __repr__(self):
        return '<ChatLog userid: %s \n message: %s \n timestamp: %s>' %(self.userid, self.message, self.timestamp)

# users table with userid and status
class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    userid = db.Column(db.String(20), unique=True)
    active = db.Column(db.Boolean())
    
    def __init__(self, u, a):
        self.userid = u
        self.active = a
    
    def __repr__(self):
        return '<Users %s: %s>' %(self.userid, self.active)

''' end of temp fix '''
### ### ### ### ### ### ### ### ### ### ### ### ###

db.create_all()
db.session.commit()

# global variables
users_active = 0
users_time = {} # userid:join time
lastEmittedTimeStamp = {} # userid:lastemittedtime


# on connect
# (1) update active users; (2) save user join time; 
# (3) send username to client; (4) emit chat log and (5) new user mssg
@socketio.on('connect')
def on_connect():
    
    socketio.emit('connected', {'test': 'Connected'})
    
    global users_time
    userid = get_username()
    print('Someone connected!', userid)

    update_users_active(1) # 1
    users_time[userid] = datetime.now() # 2
    send_username() # 3
    EMIT_CHAT_LOG() # 4
    user_chat_status( str(userid) + " has joined the chat." ) # 5


# on disconnect
# (1) update active users; (2) user left mssg
@socketio.on('disconnect')
def on_disconnect():
    userid = get_username()
    print ('Someone disconnected!', userid)
    
    update_users_active(-1) # 1
    user_chat_status( str(userid) + " has left the chat." ) # 2
    
    
def get_username():
    return flask.request.sid


def send_username():
    userid = get_username()
    socketio.emit('username channel', {'userid':userid})


def update_users_active(update):
    global users_active
    users_active += update
    
    socketio.emit('active users channel', {'users':users_active})
    
    
# emits message if user joins/leaves (uses modified chat log channel)
def user_chat_status(string):
    socketio.emit('chat log channel', {'chat_log':[ {'userid':"",'message':string,'timestamp':""} ], 'timestamp':""})


# returns last timestamp value from global dict
def get_lastEmittedTimeStamp():
    global lastEmittedTimeStamp
    user = str(get_username())
    
    if user not in lastEmittedTimeStamp:
        lastEmittedTimeStamp[user] = 0
    
    return lastEmittedTimeStamp[user]   
    
    
# queries db for messages after timestamp
def get_chat_log(timestamp):
    global lastEmittedTimeStamp
    user = get_username()
    output = []

    if timestamp == 0:
        query = ChatLog.query.all()
    else:
        query = ChatLog.query.filter(ChatLog.timestamp > timestamp).all()
    
    for entry in query:
        d = {}
        d['userid'] = entry.userid
        d['message'] = entry.message
        d['timestamp'] = str(entry.timestamp)
        output.append(d)
    
    # updates last emitted timestamp
    if len(output) != 0:
        for users in lastEmittedTimeStamp:
            lastEmittedTimeStamp[users] = output[-1]['timestamp']
    
    return output, lastEmittedTimeStamp[user]


# saves message from client in db & checks if bot command
@socketio.on('message channel')
def save_message(data):
    
    userid = get_username()
    message = data['mssg']
    timestamp = datetime.now().strftime("%Y/%m/%d %H:%M:%S")
    
    print("Recieved message from: ", userid)
    
    db.session.add(ChatLog(userid, message, timestamp))
    db.session.commit()
    
    if message[0:2] == "!!":
        handle_bot(message)
    
    EMIT_CHAT_LOG()
    
    
# emits chat log and timestamp, if chat log not empty
def EMIT_CHAT_LOG():
    global lastEmittedTimeStamp
    
    chat_log, timestamp = get_chat_log(get_lastEmittedTimeStamp())
    
    if len(chat_log) == 0:
        return
    
    socketio.emit('chat log channel', {'chat_log':chat_log, 'timestamp':timestamp})
    
    print("emitted chat log of length", len(chat_log))

    
# calls appropriate function to execute and saves message
def handle_bot(message):
    global users_time
    bot_commands = ['!! about', '!! help', '!! translate', '!! spotify', '!! time']

    message_arr = message.split()
    
    # if no command given
    if (len(message_arr) == 1):
        return
    
    command = message_arr[1]
    
    print("recieved bot command", command)
    
    reply = ""
    
    if (command == 'about'):
        reply = bot.bot_about()
        
    elif (command == 'help'):
        reply = bot.bot_help(bot_commands)
        
    elif (command == 'translate'):
        temp = message_arr[2:len(message_arr)]
        translate_string = " ".join(temp)
        reply = bot.bot_translate(translate_string)
        
    elif (command == 'spotify'):
        temp = message_arr[2:len(message_arr)]
        artist = " ".join(temp)
        reply = bot.bot_spotify(artist)
        
    elif (command == 'time'):
        reply = bot.bot_time( users_time[get_username()] )
        
    else:
        reply = bot.bot_unknown(command)
    
    bot_save_message(reply)
  
  
# saves bot message to db and emits chat
def bot_save_message(message):
    userid = "chit-chat-bot"
    message = message
    timestamp = datetime.now().strftime("%Y/%m/%d %H:%M:%S")
    
    db.session.add(ChatLog(userid, message, timestamp))
    db.session.commit()
    
    EMIT_CHAT_LOG()
    

@app.route('/')
def hello():
    return flask.render_template('index.html')

if __name__ == '__main__': 
    socketio.run(
        app,
        host=os.getenv('IP', '0.0.0.0'),
        port=int(os.getenv('PORT', 8080)),
        debug=True
    )