from datetime import datetime
import os
from flask import Flask
from extensions import db, migrate, scheduler
from apscheduler.schedulers.background import BackgroundScheduler

def create_app():
    app = Flask(__name__)
    
    # Конфигурация
    app.secret_key = os.environ.get('SECRET_KEY') or 'your-secret-key'
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL') or 'sqlite:///individualtaskmanager.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SCHEDULER_API_ENABLED'] = True

    # Инициализация расширений
    db.init_app(app)
    migrate.init_app(app, db)
    
    # Регистрация компонентов
    with app.app_context():
        from routes import bp
        app.register_blueprint(bp)
        db.create_all()
        setup_scheduler(app)
    
    return app

def setup_scheduler(app):
    from models import Reminder

    def check_reminders():
        with app.app_context():
            try:
                now = datetime.now()
                reminders = Reminder.query.filter(
                    Reminder.reminder_date <= now,
                    Reminder.sent == False
                ).all()
                
                for reminder in reminders:
                    reminder.sent = True
                    db.session.commit()
            except Exception as e:
                app.logger.error(f"Error in reminder check: {str(e)}")
                db.session.rollback()

    if not scheduler.running:
        scheduler.add_job(
            func=check_reminders,
            trigger='interval',
            minutes=1,
            id='reminder_check_job',
            replace_existing=True
        )
        try:
            scheduler.start()
        except:
            pass

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), debug=True)