from flask import Flask, render_template, request, redirect, url_for, session, flash
from app import app, db
from models import User, Task, task_tracking
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timezone
from collections import defaultdict

# Главная страница
@app.route('/')
def index():
    if not is_authenticated():
        return redirect(url_for('login'))

    user = User.query.get(session['user_id'])
    if not user:
        flash('Пользователь не найден')
        return redirect(url_for('logout'))

    tasks = Task.query.filter_by(user_id=session['user_id'], completed=False).order_by(Task.date).all()
    grouped_tasks = defaultdict(list)
    for task in tasks:
        if task.date:
            grouped_tasks[task.date].append(task)
            

    return render_template('index.html', grouped_tasks=grouped_tasks, current_user=user)

# Регистрация
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        new_user = User(username=username, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('register.html')

# Логин
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            return redirect(url_for('index'))
        else:
            flash('Неверное имя пользователя или пароль')
            return redirect(url_for('login'))
    return render_template('login.html')

# Выход
@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('login'))

# Проверка аутентификации
def is_authenticated():
    return 'user_id' in session

# Выполненные задачи
@app.route('/completed_tasks')
def completed_tasks():
    if not is_authenticated():
        return redirect(url_for('login'))
    user = User.query.get(session['user_id'])
    if not user:
        flash('Пользователь не найден')
        return redirect(url_for('logout'))

    tasks = Task.query.filter_by(user_id=session['user_id'], completed=True).all()
    return render_template('completed_tasks.html', tasks=tasks, current_user=user)

# Поиск задач
@app.route('/search', methods=['GET'])
def search_tasks():
    if not is_authenticated():
        return redirect(url_for('login'))

    query = request.args.get('query', '').strip()
    if not query:
        return redirect(url_for('index'))

    tasks = Task.query.filter(
        (Task.title.ilike(f'%{query}%')) | (Task.description.ilike(f'%{query}%')),
        Task.user_id == session['user_id']
    ).all()

    return render_template('search_results.html', tasks=tasks, query=query, current_user=User.query.get(session['user_id']))

# Поиск выполненных задач
@app.route('/search_completed', methods=['GET'])
def search_completed_tasks():
    if not is_authenticated():
        return redirect(url_for('login'))

    query = request.args.get('query', '').strip()
    if not query:
        return redirect(url_for('completed_tasks'))
    tasks = Task.query.filter(
        (Task.title.ilike(f'%{query}%')) | (Task.description.ilike(f'%{query}%')),
        Task.user_id == session['user_id'],
        Task.completed == True
    ).all()

    return render_template('search_completed_results.html', tasks=tasks, query=query, current_user=User.query.get(session['user_id']))

# Добавление задачи
@app.route('/add', methods=['POST'])
def add_task():
    if not is_authenticated():
        return redirect(url_for('login'))

    title = request.form.get('title')
    description = request.form.get('description')
    date_str = request.form.get('date')
    date = datetime.strptime(date_str, '%Y-%m-%d').date() if date_str else datetime.now(timezone.utc).date()

    responsible = request.form.get('responsible')
    region = request.form.get('region')
    priority = request.form.get('priority')
    

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

    return redirect(url_for('index'))

# Удаление задачи
@app.route('/delete/<int:id>')
def delete_task(id):
    if not is_authenticated():
        return redirect(url_for('login'))
    task = Task.query.get_or_404(id)
    db.session.delete(task)
    db.session.commit()
    return redirect(url_for('index'))

# Завершение задачи
@app.route('/complete/<int:id>')
def complete_task(id):
    if not is_authenticated():
        return redirect(url_for('login'))
    task = Task.query.get_or_404(id)
    task.completed = not task.completed
    db.session.commit()
    return redirect(url_for('index'))

# Отслеживание задачи
@app.route('/toggle_tracking/<int:task_id>', methods=['POST'])
def toggle_tracking(task_id):
    if not is_authenticated():
        return redirect(url_for('login'))
    task = Task.query.get(task_id)
    user = User.query.get(session['user_id'])
    if task and user:
        if task in user.tracked_tasks:
            user.tracked_tasks.remove(task)
        else:
            user.tracked_tasks.append(task)
        db.session.commit()
    return redirect(url_for('index'))

@app.route('/edit/<int:task_id>', methods=['GET', 'POST'])
def edit_task(task_id):
    if not is_authenticated():
        return redirect(url_for('login'))

    task = Task.query.get_or_404(task_id)

    if request.method == 'POST':
        # Обновляем данные задачи
        task.title = request.form.get('title')
        task.description = request.form.get('description')
        date_str = request.form.get('date')
        task.date = datetime.strptime(date_str, '%Y-%m-%d').date() if date_str else datetime.now(timezone.utc).date()
        task.responsible = request.form.get('responsible')
        task.region = request.form.get('region')
        task.priority = request.form.get('priority')

        db.session.commit()
        flash('Задача успешно обновлена', 'success')
        return redirect(url_for('index'))

    # Если метод GET, отображаем форму редактирования
    return render_template('edit_task.html', task=task)