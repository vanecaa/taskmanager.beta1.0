from flask import Blueprint, jsonify, render_template, request, redirect, url_for, session, flash
from extensions import db
from models import Reminder, Task, User, task_tracking
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timezone
from collections import defaultdict
from sqlalchemy.exc import IntegrityError


bp = Blueprint('main', __name__)


# Главная страница
@bp.route('/')
def index():
    if not is_authenticated():
        return redirect(url_for('main.login'))

    user = User.query.get(session['user_id'])
    if not user:
        flash('Пользователь не найден')
        return redirect(url_for('main.logout'))

    tasks = Task.query.filter_by(user_id=session['user_id'], completed=False).order_by(Task.date).all()
    grouped_tasks = defaultdict(list)
    
    for task in tasks:
        if task.date:
            grouped_tasks[task.date].append(task)
    
    # Преобразуем defaultdict в обычный dict для шаблона
    grouped_tasks = dict(grouped_tasks)
    
    return render_template('index.html', 
                         grouped_tasks=grouped_tasks, 
                         current_user=user,
                         enumerate=enumerate) 

# Регистрация
@bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        if not all([username, email, password]):
            flash('Все поля обязательны для заполнения!', 'error')
            return redirect(url_for('main.register'))
            
        if User.query.filter_by(username=username).first():
            flash('Это имя пользователя уже занято', 'error')
            return redirect(url_for('main.register'))
            
        if User.query.filter_by(email=email).first():
            flash('Этот email уже используется', 'error')
            return redirect(url_for('main.register'))
        
        try:
            hashed_password = generate_password_hash(password)
            new_user = User(
                username=username,
                email=email,
                password=hashed_password
            )
            db.session.add(new_user)
            db.session.commit()
            flash('Регистрация успешна! Теперь вы можете войти.', 'success')
            return redirect(url_for('main.login'))
        except Exception as e:
            db.session.rollback()
            flash(f'Ошибка регистрации: {str(e)}', 'error')
            return redirect(url_for('main.register'))
    
    return render_template('register.html')

# Логин
@bp.route('/login', methods=['GET', 'POST'])

def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            return redirect(url_for('main.index'))
        else:
            flash('Неверное имя пользователя или пароль')
            return redirect(url_for('main.login'))
    return render_template('login.html')

# Выход
@bp.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('main.login'))

# Проверка аутентификации
def is_authenticated():
    return 'user_id' in session

# Выполненные задачи
@bp.route('/completed_tasks')
def completed_tasks():
    if not is_authenticated():
        return redirect(url_for('main.login'))
    user = User.query.get(session['user_id'])
    if not user:
        flash('Пользователь не найден')
        return redirect(url_for('main.logout'))

    tasks = Task.query.filter_by(user_id=session['user_id'], completed=True).all()
    return render_template('completed_tasks.html', tasks=tasks, current_user=user)

# Поиск задач
@bp.route('/search', methods=['GET'])
def search_tasks():
    if not is_authenticated():
        return redirect(url_for('main.login'))

    query = request.args.get('query', '').strip()
    if not query:
        return redirect(url_for('main.index'))

    tasks = Task.query.filter(
        (Task.title.ilike(f'%{query}%')) | (Task.description.ilike(f'%{query}%')),
        Task.user_id == session['user_id']
    ).all()

    return render_template('search_results.html', tasks=tasks, query=query, current_user=User.query.get(session['user_id']))

# Поиск выполненных задач
@bp.route('/search_completed', methods=['GET'])
def search_completed_tasks():
    if not is_authenticated():
        return redirect(url_for('main.login'))

    query = request.args.get('query', '').strip()
    if not query:
        return redirect(url_for('main.completed_tasks'))
    tasks = Task.query.filter(
        (Task.title.ilike(f'%{query}%')) | (Task.description.ilike(f'%{query}%')),
        Task.user_id == session['user_id'],
        Task.completed == True
    ).all()

    return render_template('search_completed_results.html', tasks=tasks, query=query, current_user=User.query.get(session['user_id']))


# Добавление задачи
@bp.route('/add', methods=['POST'])
def add_task():
    if not is_authenticated():
        return redirect(url_for('main.login'))

    try:
        # Получаем данные из формы
        title = request.form.get('title')
        description = request.form.get('description')
        date_str = request.form.get('date')
        responsible = request.form.get('responsible')
        region = request.form.get('region')
        priority = request.form.get('priority')
        
        # Проверяем обязательные поля
        if not title:
            flash('Название задачи обязательно!', 'error')
            return redirect(url_for('main.index'))
            
        # Преобразуем дату
        date = datetime.strptime(date_str, '%Y-%m-%d').date() if date_str else datetime.now(timezone.utc).date()
        
        # Создаем задачу
        new_task = Task(
            title=title,
            description=description,
            date=date,
            user_id=session['user_id'],
            responsible=responsible,
            region=region,
            priority=priority
        )
        
        db.session.add(new_task)
        db.session.commit()
        flash('Задача успешно добавлена!', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Ошибка при добавлении задачи: {str(e)}', 'error')
    
    return redirect(url_for('main.index'))

# Удаление задачи
@bp.route('/delete/<int:id>')
def delete_task(id):
    if not is_authenticated():
        return redirect(url_for('main.login'))
    task = Task.query.get_or_404(id)
    db.session.delete(task)
    db.session.commit()
    return redirect(url_for('main.index'))

# Завершение задачи
@bp.route('/complete/<int:id>')
def complete_task(id):
    if not is_authenticated():
        return redirect(url_for('main.login'))
    task = Task.query.get_or_404(id)
    task.completed = not task.completed
    db.session.commit()
    return redirect(url_for('main.index'))

# Отслеживание задачи
@bp.route('/toggle_tracking/<int:task_id>', methods=['POST'])
def toggle_tracking(task_id):
    if not is_authenticated():
        return redirect(url_for('main.login'))
    task = Task.query.get(task_id)
    user = User.query.get(session['user_id'])
    if task and user:
        if task in user.tracked_tasks:
            user.tracked_tasks.remove(task)
        else:
            user.tracked_tasks.append(task)
        db.session.commit()
    return redirect(url_for('main.index'))

#Проверка напоминаний
@bp.route('/check_reminders')
def check_reminders():
    if not is_authenticated():
        return jsonify({'success': False})
    
    now = datetime.now()
    reminders = Reminder.query.filter(
        Reminder.reminder_date <= now,
        Reminder.sent == False,
        Reminder.task.has(user_id=session['user_id'])
    ).all()
    
    return jsonify([{
        'id': r.id,
        'title': r.task.title,
        'description': r.task.description,
        'date': r.reminder_date.isoformat()
    } for r in reminders])


#Установить напоминание
@bp.route('/set_reminder', methods=['POST'])
def set_reminder():
    if not is_authenticated():
        return jsonify({'success': False, 'error': 'Not authenticated'}), 401
    
    try:
        task_id = request.form.get('task_id')
        reminder_date_str = request.form.get('reminder_date')
        
        if not task_id or not reminder_date_str:
            return jsonify({'success': False, 'error': 'Missing required fields'}), 400
        
        try:
            reminder_date = datetime.strptime(reminder_date_str, '%Y-%m-%dT%H:%M')
        except ValueError:
            return jsonify({'success': False, 'error': 'Invalid date format'}), 400
        
        task = Task.query.get(task_id)
        if not task or task.user_id != session['user_id']:
            return jsonify({'success': False, 'error': 'Task not found or access denied'}), 403
        
        # Удаляем старые напоминания для этой задачи
        Reminder.query.filter_by(task_id=task_id).delete()
        
        new_reminder = Reminder(
            task_id=task_id,
            reminder_date=reminder_date,
            sent=False
        )
        
        db.session.add(new_reminder)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Напоминание успешно установлено',
            'reminder_id': new_reminder.id
        })
        
    except IntegrityError: 
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': 'Database integrity error'
        }), 500
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': f'Произошла ошибка: {str(e)}'
        }), 500
    

#Получение активных напоминаний
@bp.route('/get_active_reminders')
def get_active_reminders():
    reminders = Reminder.query.filter(
        Reminder.sent == False,
        Reminder.task.has(user_id=session['user_id'])
    ).join(Task).all()
    
    return jsonify({
        'reminders': [{
            'id': r.id,
            'title': r.task.title,
            'description': r.task.description,
            'date': r.reminder_date.isoformat()  # или .strftime('%Y-%m-%d %H:%M')
        } for r in reminders]
    })


@bp.route('/mark_reminder_shown/<int:reminder_id>', methods=['POST'])
def mark_reminder_shown(reminder_id):
    """Пометить напоминание как показанное"""
    if not is_authenticated():
        return jsonify({'success': False, 'error': 'Not authenticated'}), 401
    
    try:
        reminder = Reminder.query.get(reminder_id)
        if not reminder or reminder.task.user_id != session['user_id']:
            return jsonify({'success': False, 'error': 'Reminder not found or access denied'}), 404
        
        reminder.sent = True
        db.session.commit()
        return jsonify({'success': True})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': f'Error marking reminder: {str(e)}'
        }), 500




#Редактирование задачи
@bp.route('/edit/<int:task_id>', methods=['GET', 'POST'])
def edit_task(task_id):
    if not is_authenticated():
        return redirect(url_for('main.login'))

    task = Task.query.get_or_404(task_id)
    
    # Проверяем, что задача принадлежит текущему пользователю
    if task.user_id != session['user_id']:
        flash('У вас нет прав для редактирования этой задачи', 'error')
        return redirect(url_for('main.index'))

    if request.method == 'POST':
        try:
            task.title = request.form.get('title')
            task.description = request.form.get('description')
            date_str = request.form.get('date')
            task.date = datetime.strptime(date_str, '%Y-%m-%d').date() if date_str else task.date
            task.responsible = request.form.get('responsible')
            task.region = request.form.get('region')
            task.priority = request.form.get('priority')
            
            db.session.commit()
            flash('Задача успешно обновлена', 'success')
            return redirect(url_for('main.index'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Ошибка при обновлении задачи: {str(e)}', 'error')
    
    return render_template('edit_task.html', task=task)

# Маршрут для завершения задачи (из JavaScript)
@bp.route('/complete_task/<int:task_id>', methods=['POST'])
def complete_task_js(task_id):
    if not is_authenticated():
        return jsonify({'success': False, 'error': 'Not authenticated'}), 401
    task = Task.query.get_or_404(task_id)
    if task.user_id != session['user_id']:
        return jsonify({'success': False, 'error': 'Access denied'}), 403
    try:
        task.completed = True
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

# Маршрут для удаления задачи (из JavaScript)
@bp.route('/delete_task/<int:task_id>', methods=['DELETE'])
def delete_task_js(task_id):
    if not is_authenticated():
        return jsonify({'success': False, 'error': 'Not authenticated'}), 401
    task = Task.query.get_or_404(task_id)
    if task.user_id != session['user_id']:
        return jsonify({'success': False, 'error': 'Access denied'}), 403
    try:
        db.session.delete(task)
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500