from os.path import join, dirname
from dotenv import load_dotenv
import os
import flask
import flask_sqlalchemy
import flask_socketio
from flask_socketio import join_room, leave_room
from datetime import datetime

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


''' temporary until i can fix the import issue '''

CHAT_LOG_CHANNEL = 'chat log channel'

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


db.create_all()
db.session.commit()

# uses global variable to update active users
users_active = 0
def update_users_active(update):
    global users_active
    users_active += update
    
    socketio.emit('active users channel', {'users':users_active})

# global dict w user's and last timestamp
lastEmittedTimeStamp = {}
def get_lastEmittedTimeStamp():
    global lastEmittedTimeStamp
    user = str(flask.request.sid)
    
    if user not in lastEmittedTimeStamp:
        lastEmittedTimeStamp[user] = 0
    
    print(lastEmittedTimeStamp)
    return lastEmittedTimeStamp[user]
    
# returns chat log after given timestamp
def get_chat_log(timestamp):
    global lastEmittedTimeStamp
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
        user = flask.request.sid
        lastEmittedTimeStamp[user] = output[-1]['timestamp']
    
    return output

# emits chat log, does not if empty
def emit_chat_log():
    chat_log = get_chat_log(get_lastEmittedTimeStamp())
    
    if len(chat_log) == 0:
        return
    
    socketio.emit('chat log channel', {'chat_log':chat_log})
    print("emitted chat log")
    print(chat_log)

# recieves message from client and saves to db
@socketio.on('send message channel')
def save_message(data):
    
    userid = flask.request.sid
    message = data['mssg']
    timestamp = str(datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
    
    db.session.add(ChatLog(userid, message, timestamp))
    db.session.commit()
    
    print("got message from client")
    print(userid, message, timestamp)
    
    emit_chat_log()

# on connect: update active users
@socketio.on('connect')
def on_connect():
    print('Someone connected!')
    
    socketio.emit('connected', {'test': 'Connected'})
    
    update_users_active(1)
    emit_chat_log()

# on disconnect: update active users
@socketio.on('disconnect')
def on_disconnect():
    print ('Someone disconnected!')
    
    update_users_active(-1)

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