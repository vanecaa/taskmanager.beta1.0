from datetime import datetime, timezone
from app import db

class User(db.Model):
    __tablename__ = 'user'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    
    def __repr__(self):
        return f'<User {self.username}>'

task_tracking = db.Table(
    'task_tracking',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), primary_key=True),
    db.Column('task_id', db.Integer, db.ForeignKey('task.id', ondelete='CASCADE'), primary_key=True)
)

class Task(db.Model):
    __tablename__ = 'task'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(200))
    completed = db.Column(db.Boolean, default=False)
    date = db.Column(db.Date, default=lambda: datetime.now(timezone.utc).date())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    responsible = db.Column(db.String(100))
    region = db.Column(db.String(100))
    priority = db.Column(db.String(50))
    
    author = db.relationship('User', backref=db.backref('tasks', cascade='all, delete-orphan'))
    tracked_by = db.relationship('User', secondary=task_tracking, backref='tracked_tasks')

class Reminder(db.Model):
    __tablename__ = 'reminder'
    
    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.Integer, db.ForeignKey('task.id', ondelete='CASCADE'), nullable=False)
    reminder_date = db.Column(db.DateTime, nullable=False)
    sent = db.Column(db.Boolean, default=False)
    
    task = db.relationship('Task', backref=db.backref('reminders', cascade='all, delete-orphan'))