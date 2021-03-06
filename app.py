from os.path import join, dirname
import os
from datetime import datetime
from urllib.parse import urlparse
import flask
import flask_sqlalchemy
import flask_socketio
from flask_socketio import join_room, leave_room
from dotenv import load_dotenv
import bot

# set up flask app, db, and socket
app = flask.Flask(__name__)

app.static_folder = 'static'

socketio = flask_socketio.SocketIO(app)
socketio.init_app(app, cors_allowed_origins="*")

dotenv_path = join(dirname(__file__), 'sql.env')
load_dotenv(dotenv_path)

database_uri = os.environ['DATABASE_URL']

app.config['SQLALCHEMY_DATABASE_URI'] = database_uri

db = flask_sqlalchemy.SQLAlchemy()

def init_db(init_app):
    db.init_app(init_app)
    db.app = init_app
    db.create_all()
    db.session.commit()


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
        return '<ChatLog username: %s \n message: %s \n timestamp: %s>'\
            %(self.username, self.message, self.timestamp)


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


LAST_EMITTED_TIMESTAMP = 0


# on connect join room and emit active users
@socketio.on('connect')
def on_connect():
    serverid = get_serverid()
    join_room( serverid )
    print('Someone connected!', serverid)

    emit_users_active()

# on disconnect leave room ->
# if user was logged in, emit user status and delete from activeusers table
@socketio.on('disconnect')
def on_disconnect():
    this_serverid = get_serverid()
    leave_room( this_serverid )
    print ('Someone disconnected!', this_serverid)

    if logged_on(this_serverid):
        user_chat_status( get_username( this_serverid ) + " has left the chat." )
        ActiveUsers.query.filter_by(serverid=this_serverid).delete()
        db.session.commit()
        print("deleted user")

    emit_users_active()


# checks activeusers table for serverid
def logged_on(this_serverid):
    print( ActiveUsers.query.filter_by(serverid=this_serverid).first() )
    if ActiveUsers.query.filter_by(serverid=this_serverid).first() is None:
        return False
    return True


# get new google user & commit info to db,
# emit user auth, name, active users, chat log, and user status
@socketio.on('new google user')
def get_google_user(data):

    try:
        email = data['email']
        image = data['image']
    except:
        return

    serverid = get_serverid()
    timestamp = datetime.now().strftime("%Y/%m/%d %H:%M:%S")
    username = email.split('@')[0]
    auth = "Google"

    db.session.add(ActiveUsers(username, auth, serverid, image, timestamp))
    db.session.commit()

    socketio.emit('user auth channel', {'auth':True}, room=serverid)
    emit_users_active()
    socketio.emit('username channel', {'username':username}, room=serverid)
    emit_chat_log(0, serverid)
    user_chat_status( username + " has joined the chat." )


# returns flask server id
def get_serverid():
    return flask.request.sid


# gets username from active users db
def get_username( this_serverid ):
    user_info = ActiveUsers.query.filter_by(serverid=this_serverid).first()
    return user_info.username


# updates and emits # of users from db table
def emit_users_active():
    data = ActiveUsers.query.all()
    users_active = len(data)
    socketio.emit('active users channel', {'users':users_active})


# emits message if user joins/leaves (uses modified chat log channel)
def user_chat_status(string):
    data = {'username':"", 'message':string, 'timestamp':""}
    socketio.emit('chat log channel', {'chat_log': data, 'timestamp':""})


# queries db for messages after timestamp
def get_chat_log(timestamp):
    global LAST_EMITTED_TIMESTAMP
    output = []

    if timestamp == 0:
        query = ChatLog.query.all()
    else:
        query = ChatLog.query.filter(ChatLog.timestamp > timestamp).all()

    for entry in query:
        dict_entry = {}
        dict_entry['username'] = entry.username
        dict_entry['auth'] = entry.auth
        dict_entry['icon'] = entry.icon
        dict_entry['message'] = entry.message
        dict_entry['timestamp'] = str(entry.timestamp)
        dict_entry['message_type'] = entry.message_type
        output.append(dict_entry)

    if len(output) != 0:  # updates last emitted timestamp
        LAST_EMITTED_TIMESTAMP = output[-1]['timestamp']

    return output


# saves message from client in db & checks if bot command
@socketio.on('message channel')
def save_message(data):
    this_username = get_username( get_serverid() )

    try:
        message = data['mssg']
    except:
        print("Could not recieve message from", this_username)
        message_recieve_fail(this_username)

    print("Recieved message from", this_username)
    timestamp = datetime.now().strftime("%Y/%m/%d %H:%M:%S")
    message_type = handle_links(message)
    user_info = ActiveUsers.query.filter_by(username = this_username).first()

    try:
        db.session.add(ChatLog(this_username, user_info.auth, \
            user_info.icon, message, timestamp, message_type))
        db.session.commit()
    except:
        print("Could not recieve message from", this_username)
        message_recieve_fail(this_username)

    if message[0:2] == "!!":
        bot_command(message)

    emit_chat_log()


# returns message type
# got this directly from
# https://stackoverflow.com/questions/7160737/how-to-validate-a-url-in-python-malformed-or-not
def handle_links(message):
    if len(message.split(" ")) > 1:
        return "text"

    result = urlparse(message)

    if not all([result.scheme, result.netloc, result.path]):
        return "text"

    path = result.path
    if path.endswith(".jpg") or path.endswith(".jpeg") or \
        path.endswith(".png") or path.endswith(".gif"):
        return "image"

    return "link"


# sends err mssg with empty user and time
def message_recieve_fail(username):
    string = "ERROR: Message from " + username + " failed to send."

    data = {'username':"", 'message':string, 'timestamp':""}
    socketio.emit('chat log channel', {'chat_log': data, 'timestamp':""})


# emits chat log and timestamp (if chat log not empty)
def emit_chat_log(specified_time=None, room=None):
    global LAST_EMITTED_TIMESTAMP
    timestamp = ""

    if specified_time is None:
        timestamp = LAST_EMITTED_TIMESTAMP
    else:
        timestamp = specified_time

    chat_log = get_chat_log( timestamp )

    if len(chat_log) == 0:
        return

    if room is None:
        socketio.emit('chat log channel', {'chat_log':chat_log, 'timestamp':LAST_EMITTED_TIMESTAMP})
    else:
        socketio.emit('chat log channel', {'chat_log':chat_log, \
            'timestamp':LAST_EMITTED_TIMESTAMP}, room=room)

    print("emitted chat log of length", len(chat_log))
    print(chat_log)


# gets bot reply and saves
def bot_command(message):
    reply = handle_bot(message)
    if reply is None:
        return
    bot_save_message(reply)


# calls appropriate function to execute and saves message
def handle_bot(message):
    bot_commands = ['!! about', '!! help', '!! translate', '!! spotify', '!! time']

    message_arr = message.split()

    # if no command given
    if len(message_arr) == 1:
        return None

    command = message_arr[1]


    if command == 'about':
        return bot.bot_about()

    elif command == 'help':
        return bot.bot_help(bot_commands)

    elif command == 'translate':
        temp = message_arr[2:len(message_arr)]
        translate_string = " ".join(temp)
        return bot.bot_translate(translate_string)

    elif command == 'spotify':
        temp = message_arr[2:len(message_arr)]
        artist = " ".join(temp)
        return bot.bot_spotify(artist)

    elif command == 'time':
        this_username = get_username( get_serverid() )
        user_info = ActiveUsers.query.filter_by(username = this_username).first()
        return bot.bot_time( user_info.timestamp )

    else:
        return bot.bot_unknown(command)

# saves bot message to db and emits chat
def bot_save_message(mssg):
    username = "chit-chat-bot"
    auth = "Bot"
    icon = "./static/boticon.jpg"
    message = mssg
    timestamp = datetime.now().strftime("%Y/%m/%d %H:%M:%S")

    db.session.add(ChatLog(username, auth, icon, message, timestamp, "bot"))
    db.session.commit()

    emit_chat_log()

@app.route('/')
def hello():
    return flask.render_template('index.html')

if __name__ == '__main__':
    init_db(app)
    socketio.run(
        app,
        host=os.getenv('IP', '0.0.0.0'),
        port=int(os.getenv('PORT', 8080)),
        debug=True
    )
    