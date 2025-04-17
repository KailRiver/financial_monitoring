from flask import Flask, render_template, request, session, redirect, url_for, flash, g, Response
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import os
from functools import wraps
from datetime import datetime
import io
import csv
from reports import generate_transactions_report, generate_dashboard_data

app = Flask(__name__)
app.secret_key = 'your-very-secret-key-12345'
app.config['DATABASE'] = os.path.join(os.path.dirname(__file__), 'finance.db')
app.config['UPLOAD_FOLDER'] = 'static/uploads'


# Инициализация базы данных
def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(app.config['DATABASE'])
        g.db.row_factory = sqlite3.Row

        cursor = g.db.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                entity_type TEXT,
                operation_date TEXT,
                transaction_type TEXT,
                amount REAL,
                status TEXT,
                sender_bank TEXT,
                account TEXT,
                recipient_bank TEXT,
                recipient_inn TEXT,
                recipient_account TEXT,
                category TEXT,
                recipient_phone TEXT,
                comment TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(user_id) REFERENCES users(id)
            )
        ''')

        cursor.execute("SELECT username FROM users WHERE username = 'admin'")
        if not cursor.fetchone():
            cursor.execute(
                "INSERT INTO users (username, password) VALUES (?, ?)",
                ('admin', generate_password_hash('admin123'))
            )

        g.db.commit()

    return g.db


def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()


app.teardown_appcontext(close_db)


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in'):
            flash('Пожалуйста, войдите в систему', 'warning')
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)

    return decorated_function


@app.route('/')
def index():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    return redirect(url_for('dashboard'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()

        user = db.execute(
            'SELECT * FROM users WHERE username = ?', (username,)
        ).fetchone()

        if user and check_password_hash(user['password'], password):
            session['logged_in'] = True
            session['user_id'] = user['id']
            session['username'] = user['username']
            flash('Вы успешно вошли в систему!', 'success')
            return redirect(url_for('dashboard'))

        flash('Неверное имя пользователя или пароль', 'error')

    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        if password != confirm_password:
            flash('Пароли не совпадают', 'error')
            return render_template('register.html')

        if len(password) < 8:
            flash('Пароль должен содержать минимум 8 символов', 'error')
            return render_template('register.html')

        db = get_db()
        try:
            cursor = db.execute(
                'INSERT INTO users (username, password) VALUES (?, ?)',
                (username, generate_password_hash(password))
            )
            db.commit()

            session['logged_in'] = True
            session['user_id'] = cursor.lastrowid
            session['username'] = username

            flash('Регистрация прошла успешно! Добро пожаловать!', 'success')
            return redirect(url_for('dashboard'))

        except sqlite3.IntegrityError:
            flash('Это имя пользователя уже занято', 'error')

    return render_template('register.html')


@app.route('/dashboard')
@login_required
def dashboard():
    db = get_db()

    stats = {
        'total_count': 0,
        'total_income': 0.0,
        'total_expense': 0.0,
        'confirmed_count': 0
    }

    try:
        stats_result = db.execute('''
            SELECT 
                COUNT(*) as total_count,
                COALESCE(SUM(CASE WHEN transaction_type = 'Поступление' THEN amount ELSE 0 END), 0) as total_income,
                COALESCE(SUM(CASE WHEN transaction_type = 'Списание' THEN amount ELSE 0 END), 0) as total_expense,
                COALESCE(SUM(CASE WHEN status = 'Подтвержденная' THEN 1 ELSE 0 END), 0) as confirmed_count
            FROM transactions
            WHERE user_id = ?
        ''', (session['user_id'],)).fetchone()

        if stats_result:
            stats.update(dict(stats_result))
    except sqlite3.Error as e:
        flash(f'Ошибка при получении статистики: {str(e)}', 'error')

    recent_transactions = []
    try:
        recent_transactions = db.execute('''
            SELECT * FROM transactions 
            WHERE user_id = ?
            ORDER BY operation_date DESC
            LIMIT 5
        ''', (session['user_id'],)).fetchall()
    except sqlite3.Error as e:
        flash(f'Ошибка при получении транзакций: {str(e)}', 'error')

    return render_template('dashboard.html',
                           username=session['username'],
                           stats=stats,
                           transactions=recent_transactions)


@app.route('/transactions')
@login_required
def transactions():
    db = get_db()
    transactions_list = []
    try:
        transactions_list = db.execute('''
            SELECT * FROM transactions 
            WHERE user_id = ?
            ORDER BY operation_date DESC
        ''', (session['user_id'],)).fetchall()
    except sqlite3.Error as e:
        flash(f'Ошибка при получении списка транзакций: {str(e)}', 'error')

    return render_template('transactions.html', transactions=transactions_list)


@app.route('/transactions/add', methods=['GET', 'POST'])
@login_required
def add_transaction():
    if request.method == 'POST':
        try:
            amount = float(request.form['amount'])
            if amount <= 0:
                flash('Сумма должна быть положительным числом', 'error')
                return render_template('add_transaction.html')
        except ValueError:
            flash('Некорректная сумма', 'error')
            return render_template('add_transaction.html')

        db = get_db()
        try:
            db.execute(
                '''
                INSERT INTO transactions (
                    user_id, entity_type, operation_date, transaction_type,
                    amount, status, sender_bank, account, recipient_bank,
                    recipient_inn, recipient_account, category, recipient_phone, comment
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''',
                (
                    session['user_id'],
                    request.form['entity_type'],
                    request.form['operation_date'],
                    request.form['transaction_type'],
                    amount,
                    request.form['status'],
                    request.form.get('sender_bank', ''),
                    request.form.get('account', ''),
                    request.form.get('recipient_bank', ''),
                    request.form.get('recipient_inn', ''),
                    request.form.get('recipient_account', ''),
                    request.form.get('category', ''),
                    request.form.get('recipient_phone', ''),
                    request.form.get('comment', '')
                )
            )
            db.commit()
            flash('Транзакция успешно добавлена', 'success')
            return redirect(url_for('transactions'))
        except sqlite3.Error as e:
            flash(f'Ошибка при добавлении транзакции: {str(e)}', 'error')

    return render_template('add_transaction.html')


@app.route('/transactions/edit/<int:transaction_id>', methods=['GET', 'POST'])
@login_required
def edit_transaction(transaction_id):
    db = get_db()

    if request.method == 'POST':
        try:
            amount = float(request.form['amount'])
            if amount <= 0:
                flash('Сумма должна быть положительным числом', 'error')
                return redirect(url_for('edit_transaction', transaction_id=transaction_id))
        except ValueError:
            flash('Некорректная сумма', 'error')
            return redirect(url_for('edit_transaction', transaction_id=transaction_id))

        try:
            db.execute(
                '''
                UPDATE transactions SET
                    entity_type = ?,
                    operation_date = ?,
                    transaction_type = ?,
                    amount = ?,
                    status = ?,
                    sender_bank = ?,
                    account = ?,
                    recipient_bank = ?,
                    recipient_inn = ?,
                    recipient_account = ?,
                    category = ?,
                    recipient_phone = ?,
                    comment = ?
                WHERE id = ? AND user_id = ?
                ''',
                (
                    request.form['entity_type'],
                    request.form['operation_date'],
                    request.form['transaction_type'],
                    amount,
                    request.form['status'],
                    request.form.get('sender_bank', ''),
                    request.form.get('account', ''),
                    request.form.get('recipient_bank', ''),
                    request.form.get('recipient_inn', ''),
                    request.form.get('recipient_account', ''),
                    request.form.get('category', ''),
                    request.form.get('recipient_phone', ''),
                    request.form.get('comment', ''),
                    transaction_id,
                    session['user_id']
                )
            )
            db.commit()
            flash('Транзакция успешно обновлена', 'success')
            return redirect(url_for('transactions'))
        except sqlite3.Error as e:
            flash(f'Ошибка при обновлении транзакции: {str(e)}', 'error')

    transaction = db.execute(
        'SELECT * FROM transactions WHERE id = ? AND user_id = ?',
        (transaction_id, session['user_id'])
    ).fetchone()

    if not transaction:
        flash('Транзакция не найдена', 'error')
        return redirect(url_for('transactions'))

    return render_template('edit_transaction.html', transaction=transaction)


@app.route('/transactions/delete/<int:transaction_id>', methods=['POST'])
@login_required
def delete_transaction(transaction_id):
    db = get_db()
    try:
        db.execute(
            'DELETE FROM transactions WHERE id = ? AND user_id = ?',
            (transaction_id, session['user_id'])
        )
        db.commit()
        flash('Транзакция успешно удалена', 'success')
    except sqlite3.Error as e:
        flash(f'Ошибка при удалении транзакции: {str(e)}', 'error')

    return redirect(url_for('transactions'))


@app.route('/reports')
@login_required
def reports():
    filters = {
        'sender_bank': request.args.get('sender_bank'),
        'recipient_bank': request.args.get('recipient_bank'),
        'start_date': request.args.get('start_date'),
        'end_date': request.args.get('end_date'),
        'status': request.args.get('status'),
        'inn': request.args.get('inn'),
        'min_amount': request.args.get('min_amount'),
        'max_amount': request.args.get('max_amount'),
        'transaction_type': request.args.get('transaction_type'),
        'category': request.args.get('category')
    }

    db = get_db()
    transactions_list = []
    try:
        query = '''
            SELECT * FROM transactions 
            WHERE user_id = ?
        '''
        params = [session['user_id']]

        if filters['sender_bank']:
            query += ' AND sender_bank LIKE ?'
            params.append(f"%{filters['sender_bank']}%")

        if filters['recipient_bank']:
            query += ' AND recipient_bank LIKE ?'
            params.append(f"%{filters['recipient_bank']}%")

        if filters['status']:
            query += ' AND status = ?'
            params.append(filters['status'])

        if filters['inn']:
            query += ' AND recipient_inn = ?'
            params.append(filters['inn'])

        if filters['transaction_type']:
            query += ' AND transaction_type = ?'
            params.append(filters['transaction_type'])

        if filters['category']:
            query += ' AND category = ?'
            params.append(filters['category'])

        if filters['start_date']:
            query += ' AND operation_date >= ?'
            params.append(filters['start_date'])

        if filters['end_date']:
            query += ' AND operation_date <= ?'
            params.append(filters['end_date'])

        if filters['min_amount']:
            query += ' AND amount >= ?'
            params.append(float(filters['min_amount']))

        if filters['max_amount']:
            query += ' AND amount <= ?'
            params.append(float(filters['max_amount']))

        query += ' ORDER BY operation_date DESC'

        transactions_list = db.execute(query, tuple(params)).fetchall()
    except sqlite3.Error as e:
        flash(f'Ошибка при получении списка транзакций: {str(e)}', 'error')

    return render_template('report.html',
                           report_data=transactions_list,
                           filters=filters)


@app.route('/reports/export/csv')
@login_required
def export_csv():
    filters = {
        'sender_bank': request.args.get('sender_bank'),
        'recipient_bank': request.args.get('recipient_bank'),
        'start_date': request.args.get('start_date'),
        'end_date': request.args.get('end_date'),
        'status': request.args.get('status'),
        'inn': request.args.get('inn'),
        'min_amount': request.args.get('min_amount'),
        'max_amount': request.args.get('max_amount'),
        'transaction_type': request.args.get('transaction_type'),
        'category': request.args.get('category')
    }

    db = get_db()
    transactions_list = []
    try:
        query = '''
            SELECT * FROM transactions 
            WHERE user_id = ?
        '''
        params = [session['user_id']]

        # Применяем те же фильтры, что и в reports()
        if filters['sender_bank']:
            query += ' AND sender_bank LIKE ?'
            params.append(f"%{filters['sender_bank']}%")

        # ... остальные фильтры ...

        query += ' ORDER BY operation_date DESC'

        transactions_list = db.execute(query, tuple(params)).fetchall()
    except sqlite3.Error as e:
        flash(f'Ошибка при получении списка транзакций: {str(e)}', 'error')
        return redirect(url_for('reports'))

    # Создаем CSV файл
    output = io.StringIO()
    writer = csv.writer(output)

    # Заголовки
    writer.writerow([
        'ID', 'Дата операции', 'Тип транзакции', 'Сумма', 'Статус',
        'Банк отправителя', 'Счет', 'Банк получателя', 'ИНН получателя',
        'Счет получателя', 'Категория', 'Телефон получателя', 'Комментарий'
    ])

    # Данные
    for transaction in transactions_list:
        writer.writerow([
            transaction['id'],
            transaction['operation_date'],
            transaction['transaction_type'],
            transaction['amount'],
            transaction['status'],
            transaction['sender_bank'],
            transaction['account'],
            transaction['recipient_bank'],
            transaction['recipient_inn'],
            transaction['recipient_account'],
            transaction['category'],
            transaction['recipient_phone'],
            transaction['comment']
        ])

    output.seek(0)

    return Response(
        output,
        mimetype="text/csv",
        headers={"Content-disposition": "attachment; filename=transactions_report.csv"}
    )


@app.route('/logout')
def logout():
    session.clear()
    flash('Вы вышли из системы', 'info')
    return redirect(url_for('login'))


if __name__ == '__main__':
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])

    with app.app_context():
        get_db()  # Создаем БД и таблицы

    app.run(debug=True)