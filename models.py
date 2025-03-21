from app import db
from datetime import datetime, timezone

# Модель для пользователя
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(200), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    tasks = db.relationship('Task', backref='user', lazy=True)  # Связь с задачами

# Модель для задач
class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(200))
    completed = db.Column(db.Boolean, default=False)
    date = db.Column(db.Date, default=lambda: datetime.now(timezone.utc).date())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # Связь с пользователем
    tracked_by = db.relationship('User', secondary='task_tracking', backref='tracked_tasks')  # Отслеживание задач
    

    responsible = db.Column(db.String(100))
    region = db.Column(db.String(100))
    priority = db.Column(db.String(50))
# Таблица для отслеживания задач
task_tracking = db.Table(
    'task_tracking',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('task_id', db.Integer, db.ForeignKey('task.id'), primary_key=True)
)