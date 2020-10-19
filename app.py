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
    username = db.Column(db.String(280), nullable=False)
    auth = db.Column(db.String(20))
    icon = db.Column(db.String(280))
    message = db.Column(db.String(280))
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.now())
    message_type = db.Column(db.String(10))
        
    def __init__(self, u, a, i, m, t, mt):
        self.username = u
        self.auth = a
        self.icon = i
        self.message = m
        self.timestamp = t
        self.message_type = mt
        
    def __repr__(self):
        return '<ChatLog username: %s \n message: %s \n timestamp: %s>' %(self.username, self.message, self.timestamp)


class ActiveUsers(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(280))
    auth = db.Column(db.String(280))
    serverid = db.Column(db.String(280))
    icon = db.Column(db.String(280))
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.now())
    
    def __init__(self, u, a, s, i, t):
        self.username = u
        self.auth = a
        self.serverid = s
        self.icon = i
        self.timestamp = t
        
    def __repr__(self):
        return '<Users username: %s \n serverid: %s>' %(self.username, self.serverid)

    
### ### ### ### ### ### 

db.create_all()
db.session.commit()


last_emitted_timestamp = 0 # userid:lastemittedtime


# on connect emit active users
@socketio.on('connect')
def on_connect():
    serverid = get_serverid()
    print('Someone connected!', serverid)
    emit_users_active()
    

# on disconnect --> if user was logged in, emit user status and delete from activeusers table
@socketio.on('disconnect')
def on_disconnect():
    this_serverid = get_serverid()
    print ('Someone disconnected!', this_serverid)
    
    if logged_on(this_serverid):
        user_chat_status( get_username( this_serverid ) + " has left the chat." ) # 2
        
        print("on disconnect delete user info")
        ActiveUsers.query.filter_by(serverid=this_serverid).delete()
        db.session.commit()
        print("deleted")
    
    emit_users_active() # 1


# checks activeusers table for serverid
def logged_on(this_serverid):
    if ( ActiveUsers.query.filter_by(serverid=this_serverid).first() == None ):
        return False
    return True
    
    
# get new google user & commit info to db, 
# emit user auth, name, active users, chat log, and user status
@socketio.on('new google user')
def get_google_user(data):
    email = data['email']
    image = data['image']
    
    serverid = get_serverid()
    timestamp = datetime.now().strftime("%Y/%m/%d %H:%M:%S")
    username = email.split('@')[0]
    auth = "Google"
    
    print("sent username")
    
    db.session.add(ActiveUsers(username, auth, serverid, image, timestamp))
    db.session.commit()
    
    socketio.emit('user auth channel', {'auth':True})
    emit_users_active()
    socketio.emit('username channel', {'username':username})
    EMIT_CHAT_LOG(0) # 4
    user_chat_status( username + " has joined the chat." ) # 5
    
    
# returns flask server id    
def get_serverid():
    return flask.request.sid


# gets username from active users db
def get_username( this_serverid ):
    
    user_info = ActiveUsers.query.filter_by(serverid=this_serverid).first()
    print("get username user info")
    print(user_info)
    return user_info.username


# updates and emits # of users
def emit_users_active():
    data = ActiveUsers.query.all()
    users_active = len(data)
    socketio.emit('active users channel', {'users':users_active})
    
    
# emits message if user joins/leaves (uses modified chat log channel)
def user_chat_status(string):
    data = {'username':"", 'auth':"", 'message':string, 'timestamp':"", 'message_type':"status"}
    
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
        d['username'] = entry.username
        d['auth'] = entry.auth
        d['icon'] = entry.icon
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
    this_username = get_username( get_serverid() )
    
    try:
        message = data['mssg']
    except:
        print("Could not recieve message")
        message_recieve_fail(this_username)
        
    timestamp = datetime.now().strftime("%Y/%m/%d %H:%M:%S")
    message_type = handle_links(message)

    print("Recieved message from: ", this_username)
    user_info = ActiveUsers.query.filter_by(username = this_username).first()
    print("save message user info")
    print(user_info)
    db.session.add(ChatLog(this_username, user_info.auth, user_info.icon, message, timestamp, message_type))

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
def message_recieve_fail(username):
    string = "ERROR: Message from " + username + " failed to send."

    data = {'username':"", 'auth':"", 'message':string, 'timestamp':"", 'message_type':"status"}
    socketio.emit('chat log channel', {'chat_log': data, 'timestamp':""})
    
    
# emits chat log and timestamp (if chat log not empty)
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
        this_username = get_username( get_serverid() )
        user_info = ActiveUsers.query.filter_by(username = this_username).first()
        reply = bot.bot_time( user_info.timestamp  )
        
    else:
        reply = bot.bot_unknown(command)
    
    bot_save_message(reply)
  
  
# saves bot message to db and emits chat
def bot_save_message(message):
    username = "chit-chat-bot"
    auth = "Bot"
    icon = "./static/boticon.jpg"
    message = message
    timestamp = datetime.now().strftime("%Y/%m/%d %H:%M:%S")

    db.session.add(ChatLog(username, auth, icon, message, timestamp, "bot"))
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