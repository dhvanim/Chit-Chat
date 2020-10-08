import flask_sqlalchemy
from app import db
from datetime import datetime

class Test():
    def __init__(self, a):
        self.a = a

class TestTable(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    testmessage = db.Column(db.String(20))
    
    def __init__(self, a):
        self.testmessage = a
    
    def __repr__(self):
        return '<TestTable message: %s>' % self.testmessage 

# chat log table with userid, message, timestamp
class ChatLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    userid = db.Column(db.String(20), nullable=False)
    message = db.Column(db.String(280))
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
        
    def __repr__(self):
        return '<ChatLog message: %s>' % self.message 

# users table with userid and status
class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    userid = db.Column(db.String(20), unique=True)
    active = db.Column(db.Boolean())
    
    def __repr__(self):
        return '<Users %s: %s>' % self.userid, self.active