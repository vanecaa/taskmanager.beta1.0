import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

# Инициализация Flask
app = Flask(__name__)
app.secret_key = 'gdkfjngdf-dfgdggnd!-sdfsn12-jegnsgseg-sgeegseg'  # Замените на секретный ключ из переменных окружения
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///individualtaskmanager.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Инициализация базы данных
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Импорт маршрутов после инициализации app и db
from routes import *

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
    