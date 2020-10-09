from os.path import join, dirname
from dotenv import load_dotenv
import os
import flask
import flask_sqlalchemy
import flask_socketio
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
    userid = db.Column(db.String(20), nullable=False)
    message = db.Column(db.String(280))
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
        
    def __init__(self, u, m, t):
        self.userid = u
        self.message = m
        self.timestamp = t
        
    def __repr__(self):
        return '<ChatLog user: %s \n message: %s \n timestamp: %s>' % self.userid, self.message, self.timestamp 

# users table with userid and status
class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    userid = db.Column(db.String(20), unique=True)
    active = db.Column(db.Boolean())
    
    def __init__(self, u, a):
        self.userid = u
        self.active = a
    
    def __repr__(self):
        return '<Users %s: %s>' % self.userid, self.active

''' end of temp fix '''

db.create_all()
db.session.commit()

users_active = 0

def update_users_active(update):
    global users_active
    users_active += update
    
    socketio.emit('active users channel', {'users':users_active})
    print(users_active)

def send_username():
    username = flask.request.sid
    
    socketio.emit('get username channel', {'username': username})
    print(username)

@socketio.on('connect')
def on_connect():
    print('Someone connected!')
    
    update_users_active(1)
    send_username()
    
    socketio.emit('connected', {
        'test': 'Connected'
    })

@socketio.on('disconnect')
def on_disconnect():
    
    update_users_active(-1)
    
    print ('Someone disconnected!')
    
@socketio.on('test socket')
def on_test(data):
    
    db.session.add(TestTable(data['mssg']))
    db.session.commit()
    
    print(data)

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