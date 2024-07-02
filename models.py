from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), unique=False, nullable=False)
    email = db.Column(db.String(50), unique=True, nullable=False)
    dnd_end_time = db.Column(db.DateTime, unique=False, nullable=False)
    dnd_start_time = db.Column(db.DateTime, unique=False, nullable=False)
    preferred_timezone = db.Column(db.String(10), unique=False, nullable=False)
    meetings = db.relationship('Meetings', back_populates='users', cascade="all, delete-orphan")

class Meetings(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    meeting_type = db.Column(db.String, unique=False, nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)
    timezone = db.Column(db.String(20), nullable=False)
    notification_interval = db.Column(db.String(20), nullable=False)
    users = db.relationship('Users', back_populates='meetings')