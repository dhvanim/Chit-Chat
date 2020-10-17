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
import datamuse

# set up flask app, db, and socket
app = flask.Flask(__name__)

app.static_folder = 'static'

socketio = flask_socketio.SocketIO(app)
socketio.init_app(app, cors_allowed_origins="*")

dotenv_path = join(dirname(__file__), 'sql.env')
load_dotenv(dotenv_path)

database_uri = os.environ['DATABASE_URL']

app.config['SQLALCHEMY_DATABASE_URI'] = database_uri

db = flask_sqlalchemy.SQLAlchemy(app)
db.init_app(app)
db.app = app


## database tables ##

# chat log table with userid, message, timestamp
class ChatLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    userid = db.Column(db.String(280), nullable=False)
    message = db.Column(db.String(280))
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    message_type = db.Column(db.String(10))
        
    def __init__(self, u, m, t, mt):
        self.userid = u
        self.message = m
        self.timestamp = t
        self.message_type = mt
        
    def __repr__(self):
        return '<ChatLog userid: %s \n message: %s \n timestamp: %s \n message_type %s>' %(self.userid, self.message, self.timestamp, self.message_type)

### ### ### ### ### ### 

db.create_all()
db.session.commit()

# generates list of usernames
datamuse.generate_names()

# global variables
users_active = 0
users_time = {} # userid:join time
last_emitted_timestamp = 0 # userid:lastemittedtime
usernames_dict = {}


# on connect
# (1) update active users; (2) save user join time; 
# (3) send username to client; (4) emit chat log and (5) new user mssg
@socketio.on('connect')
def on_connect():
    
    socketio.emit('connected', {'test': 'Connected'})
    
    global users_time
    global usernames_dict
    
    userid = get_userid()
    create_username(userid)
    
    print('Someone connected!', userid)

    update_users_active(1) # 1
    users_time[userid] = datetime.now() # 2
    send_username() # 3
    EMIT_CHAT_LOG(0) # 4
    user_chat_status( usernames_dict[ userid ] + " has joined the chat." ) # 5


# on disconnect
# (1) update active users; (2) user left mssg; (3) remove user from global vars
@socketio.on('disconnect')
def on_disconnect():
    userid = get_userid()
    print ('Someone disconnected!', userid)
    
    update_users_active(-1) # 1
    user_chat_status( usernames_dict[ userid ] + " has left the chat." ) # 2
    
    # 3
    usernames_dict.pop(userid, None)
    users_time.pop(userid, None)
    
    
# greturns flask server id    
def get_userid():
    return flask.request.sid


# creates and saves username using array from datamuse mod
def create_username(userid):
    global usernames_dict
    
    # if all names taken, will just use userid
    if (len(datamuse.usernames) == 0):
        usernames_dict[userid] = str(userid)
        return
    
    name = random.choice( datamuse.usernames )
    usernames_dict[userid] = name
    
    datamuse.usernames.remove(name)


# sends username to client
def send_username():
    global usernames_dict
    
    userid = get_userid()
    name = usernames_dict[ userid ]
    socketio.emit('username channel', {'username':name})


# updates and emits # of users
def update_users_active(update):
    global users_active
    
    users_active += update
    socketio.emit('active users channel', {'users':users_active})
    
    
# emits message if user joins/leaves (uses modified chat log channel)
def user_chat_status(string):
    data = {'userid':"", 'message':string, 'timestamp':"", 'message_type':"status"}
    socketio.emit('chat log channel', {'chat_log': data, 'timestamp':""})

    
# queries db for messages after timestamp
def get_chat_log(timestamp):
    global last_emitted_timestamp
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
        d['message_type'] = entry.message_type
        output.append(d)
    
    if (len(output) != 0):  # updates last emitted timestamp
        last_emitted_timestamp = output[-1]['timestamp']
    
    return output


# saves message from client in db & checks if bot command
@socketio.on('message channel')
def save_message(data):
    global usernames_dict
    
    userid = get_userid()
    username = usernames_dict[ userid ]
    
    try:
        message = data['mssg']
    except:
        print("Could not recieve message")
        message_recieve_fail(username)
        
    timestamp = datetime.now().strftime("%Y/%m/%d %H:%M:%S")
    
    message_type = handle_links(message)
    
    print("Recieved message from: ", userid, username)
    
    db.session.add(ChatLog(username, message, timestamp, message_type))
    db.session.commit()
    
    if message[0:2] == "!!":
        handle_bot(message)
    
    EMIT_CHAT_LOG()
    
    
# returns message type
def handle_links(message):
    if (message.startswith('http://')) or (message.startswith('https://')):
        if (message.endswith('.jpg') or message.endswith('.jpeg') or message.endswith('.png') or message.endswith('.gif')):
            return "image"
        return "link"
        
    return "text"


# sends err mssg with empty user and time
def message_recieve_fail(userid):
    string = "ERROR: Message from " + usernames_dict[userid] + " failed to send."
    
    data = {'userid':"", 'message':string, 'timestamp':"", 'message_type':"status"}
    socketio.emit('chat log channel', {'chat_log': data, 'timestamp':""})
    
    
# emits chat log and timestamp, if chat log not empty
def EMIT_CHAT_LOG(specified_time=None):
    global last_emitted_timestamp
    timestamp = ""
    
    if specified_time == None:
        timestamp = last_emitted_timestamp
    else:
        timestamp = specified_time
    
    chat_log = get_chat_log( timestamp )
    
    if len(chat_log) == 0:
        return
    
    socketio.emit('chat log channel', {'chat_log':chat_log, 'timestamp':last_emitted_timestamp})
    
    print("emitted chat log of length", len(chat_log))
    print(chat_log)

    
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
        reply = bot.bot_time( users_time[get_userid()] )
        
    else:
        reply = bot.bot_unknown(command)
    
    bot_save_message(reply)
  
  
# saves bot message to db and emits chat
def bot_save_message(message):
    userid = "chit-chat-bot"
    message = message
    timestamp = datetime.now().strftime("%Y/%m/%d %H:%M:%S")
    
    db.session.add(ChatLog(userid, message, timestamp, "bot"))
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