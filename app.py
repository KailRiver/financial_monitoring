from flask import Flask, render_template, request, session, redirect, url_for, flash, g, Response
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import os
from functools import wraps
from datetime import datetime
import io
import csv
from io import BytesIO

app = Flask(__name__)
app.secret_key = 'your-very-secret-key-12345'
app.config['DATABASE'] = os.path.join(os.path.dirname(__file__), 'finance.db')
app.config['UPLOAD_FOLDER'] = 'static/uploads'

# Константы статусов
STATUS_CHOICES = [
    'Новая',
    'Подтвержденная',
    'В обработке',
    'Отменена',
    'Платеж выполнен',
    'Платеж удален',
    'Возврат'
]

NON_EDITABLE_STATUSES = [
    'Подтвержденная',
    'В обработке',
    'Отменена',
    'Платеж выполнен',
    'Платеж удален',
    'Возврат'
]

NON_DELETABLE_STATUSES = [
    'Подтвержденная',
    'В обработке',
    'Отменена',
    'Платеж выполнен',
    'Возврат'
]


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
                status TEXT CHECK(status IN ('Новая', 'Подтвержденная', 'В обработке', 'Отменена', 
                                      'Платеж выполнен', 'Платеж удален', 'Возврат')),
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


def get_filtered_transactions(filters, user_id):
    db = get_db()
    query = 'SELECT * FROM transactions WHERE user_id = ?'
    params = [user_id]

    if filters.get('sender_bank'):
        query += ' AND sender_bank LIKE ?'
        params.append(f"%{filters['sender_bank']}%")

    if filters.get('recipient_bank'):
        query += ' AND recipient_bank LIKE ?'
        params.append(f"%{filters['recipient_bank']}%")

    if filters.get('status'):
        query += ' AND status = ?'
        params.append(filters['status'])

    if filters.get('inn'):
        query += ' AND recipient_inn = ?'
        params.append(filters['inn'])

    if filters.get('transaction_type'):
        query += ' AND transaction_type = ?'
        params.append(filters['transaction_type'])

    if filters.get('category'):
        query += ' AND category = ?'
        params.append(filters['category'])

    if filters.get('start_date'):
        query += ' AND operation_date >= ?'
        params.append(filters['start_date'])

    if filters.get('end_date'):
        query += ' AND operation_date <= ?'
        params.append(filters['end_date'])

    if filters.get('min_amount'):
        query += ' AND amount >= ?'
        params.append(float(filters['min_amount']))

    if filters.get('max_amount'):
        query += ' AND amount <= ?'
        params.append(float(filters['max_amount']))

    query += ' ORDER BY operation_date DESC'
    return db.execute(query, tuple(params)).fetchall()


@app.route('/')
def index():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    return redirect(url_for('dashboard'))


@app.route('/dashboard')
@login_required
def dashboard():
    stats = {
        'total_count': 0,
        'confirmed_count': 0,
        'total_income': 0,
        'total_expense': 0
    }

    try:
        db = get_db()
        stats['total_count'] = db.execute(
            'SELECT COUNT(*) FROM transactions WHERE user_id = ?',
            (session['user_id'],)
        ).fetchone()[0]

        stats['confirmed_count'] = db.execute(
            'SELECT COUNT(*) FROM transactions WHERE user_id = ? AND status = ?',
            (session['user_id'], 'Подтвержденная')
        ).fetchone()[0]

        income = db.execute(
            'SELECT SUM(amount) FROM transactions WHERE user_id = ? AND transaction_type = ?',
            (session['user_id'], 'Поступление')
        ).fetchone()[0]
        stats['total_income'] = income if income else 0

        expense = db.execute(
            'SELECT SUM(amount) FROM transactions WHERE user_id = ? AND transaction_type = ?',
            (session['user_id'], 'Списание')
        ).fetchone()[0]
        stats['total_expense'] = expense if expense else 0

        transactions = db.execute(
            'SELECT * FROM transactions WHERE user_id = ? ORDER BY operation_date DESC LIMIT 5',
            (session['user_id'],)
        ).fetchall()

    except sqlite3.Error as e:
        flash(f'Ошибка при загрузке данных: {str(e)}', 'error')
        transactions = []

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

    return render_template('dashboard.html',
                           username=session.get('username', 'Пользователь'),
                           stats=stats,
                           transactions=transactions,
                           filters=filters,
                           status_choices=STATUS_CHOICES,
                           show_navigation=True)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        if len(username) < 4:
            flash('Имя пользователя должно содержать не менее 4 символов', 'error')
            return redirect(url_for('register'))

        if len(password) < 6:
            flash('Пароль должен содержать не менее 6 символов', 'error')
            return redirect(url_for('register'))

        if password != confirm_password:
            flash('Пароли не совпадают', 'error')
            return redirect(url_for('register'))

        try:
            db = get_db()
            db.execute(
                "INSERT INTO users (username, password) VALUES (?, ?)",
                (username, generate_password_hash(password))
            )
            db.commit()
            flash('Регистрация прошла успешно. Теперь вы можете войти.', 'success')
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash('Пользователь с таким именем уже существует', 'error')
            return redirect(url_for('register'))
        except sqlite3.Error as e:
            flash(f'Ошибка при регистрации: {str(e)}', 'error')
            return redirect(url_for('register'))

    return render_template('register.html', show_navigation=False)


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
            flash('Вы успешно вошли в систему', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Неверное имя пользователя или пароль', 'error')

    return render_template('login.html', show_navigation=False)


@app.route('/logout')
def logout():
    session.clear()
    flash('Вы вышли из системы', 'info')
    return redirect(url_for('login'))


@app.route('/transactions')
@login_required
def transactions():
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

    try:
        transactions_list = get_filtered_transactions(filters, session['user_id'])
    except sqlite3.Error as e:
        flash(f'Ошибка при получении списка транзакций: {str(e)}', 'error')
        transactions_list = []

    return render_template('transactions.html',
                           transactions=transactions_list,
                           filters=filters,
                           status_choices=STATUS_CHOICES,
                           non_editable_statuses=NON_EDITABLE_STATUSES,
                           non_deletable_statuses=NON_DELETABLE_STATUSES,
                           show_navigation=True)


@app.route('/add-transaction', methods=['GET', 'POST'])
@login_required
def add_transaction():
    if request.method == 'POST':
        try:
            db = get_db()
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
                    float(request.form['amount']),
                    'Новая',
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

    return render_template('add_transaction.html',
                           status_choices=STATUS_CHOICES,
                           show_navigation=True)


@app.route('/edit-transaction/<int:transaction_id>', methods=['GET', 'POST'])
@login_required
def edit_transaction(transaction_id):
    db = get_db()
    transaction = db.execute(
        'SELECT * FROM transactions WHERE id = ? AND user_id = ?',
        (transaction_id, session['user_id'])
    ).fetchone()

    if not transaction:
        flash('Транзакция не найдена', 'error')
        return redirect(url_for('transactions'))

    if transaction['status'] in NON_EDITABLE_STATUSES:
        flash('Редактирование запрещено для данной транзакции', 'error')
        return redirect(url_for('transactions'))

    if request.method == 'POST':
        try:
            db.execute(
                '''
                UPDATE transactions SET
                    entity_type = ?,
                    operation_date = ?,
                    transaction_type = ?,
                    amount = ?,
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
                    float(request.form['amount']),
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

    return render_template('edit_transaction.html',
                           transaction=transaction,
                           status_choices=STATUS_CHOICES,
                           show_navigation=True)


@app.route('/delete-transaction/<int:transaction_id>', methods=['POST'])
@login_required
def delete_transaction(transaction_id):
    db = get_db()
    transaction = db.execute(
        'SELECT * FROM transactions WHERE id = ? AND user_id = ?',
        (transaction_id, session['user_id'])
    ).fetchone()

    if not transaction:
        flash('Транзакция не найдена', 'error')
        return redirect(url_for('transactions'))

    if transaction['status'] in NON_DELETABLE_STATUSES:
        flash('Удаление запрещено для данной транзакции', 'error')
        return redirect(url_for('transactions'))

    try:
        db.execute(
            'UPDATE transactions SET status = ? WHERE id = ?',
            ('Платеж удален', transaction_id)
        )
        db.commit()
        flash('Транзакция помечена как удаленная', 'success')
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

    try:
        transactions_list = get_filtered_transactions(filters, session['user_id'])
    except sqlite3.Error as e:
        flash(f'Ошибка при получении списка транзакций: {str(e)}', 'error')
        transactions_list = []

    return render_template('report.html',
                           report_data=transactions_list,
                           filters=filters,
                           status_choices=STATUS_CHOICES,
                           show_navigation=True)


@app.route('/reports/export/csv')
@login_required
def export_csv():
    # Получаем те же фильтры, что и на странице отчетов
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

    try:
        transactions_list = get_filtered_transactions(filters, session['user_id'])
    except sqlite3.Error as e:
        flash(f'Ошибка при получении списка транзакций: {str(e)}', 'error')
        return redirect(url_for('reports'))

    # Создаем CSV в памяти
    output = io.StringIO()
    writer = csv.writer(output, delimiter=';')

    # Заголовки CSV
    writer.writerow([
        'ID', 'Дата операции', 'Тип лица', 'Тип транзакции',
        'Сумма', 'Статус', 'Банк отправителя', 'Счет',
        'Банк получателя', 'ИНН получателя', 'Счет получателя',
        'Категория', 'Телефон получателя', 'Комментарий'
    ])

    # Данные
    for transaction in transactions_list:
        writer.writerow([
            transaction['id'],
            transaction['operation_date'],
            transaction['entity_type'],
            transaction['transaction_type'],
            str(transaction['amount']).replace('.', ','),
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

    # Генерируем имя файла с датой
    filename = f"transactions_report_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.csv"

    # Возвращаем файл для скачивания
    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename={filename}",
            "Content-type": "text/csv; charset=utf-8"
        }
    )


@app.route('/reports/export/excel')
@login_required
def export_excel():
    try:
        import pandas as pd
    except ImportError:
        flash('Для экспорта в Excel требуется установка pandas', 'error')
        return redirect(url_for('reports'))

    # Получаем те же фильтры, что и на странице отчетов
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

    try:
        transactions_list = get_filtered_transactions(filters, session['user_id'])
    except sqlite3.Error as e:
        flash(f'Ошибка при получении списка транзакций: {str(e)}', 'error')
        return redirect(url_for('reports'))

    try:
        # Подготавливаем данные для Excel
        data = []
        for transaction in transactions_list:
            data.append({
                'ID': transaction['id'],
                'Дата операции': transaction['operation_date'],
                'Тип лица': transaction['entity_type'],
                'Тип транзакции': transaction['transaction_type'],
                'Сумма': transaction['amount'],
                'Статус': transaction['status'],
                'Банк отправителя': transaction['sender_bank'],
                'Счет': transaction['account'],
                'Банк получателя': transaction['recipient_bank'],
                'ИНН получателя': transaction['recipient_inn'],
                'Счет получателя': transaction['recipient_account'],
                'Категория': transaction['category'],
                'Телефон получателя': transaction['recipient_phone'],
                'Комментарий': transaction['comment']
            })

        # Создаем DataFrame
        df = pd.DataFrame(data)

        # Создаем Excel файл в памяти
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Транзакции', index=False)

        output.seek(0)

        # Генерируем имя файла с датой
        filename = f"transactions_report_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.xlsx"

        # Возвращаем файл для скачивания
        return Response(
            output.getvalue(),
            mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={
                "Content-Disposition": f"attachment; filename={filename}",
                "Content-type": "application/vnd.ms-excel; charset=utf-8"
            }
        )

    except Exception as e:
        flash(f'Ошибка при создании Excel файла: {str(e)}', 'error')
        return redirect(url_for('reports'))


if __name__ == '__main__':
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])

    with app.app_context():
        get_db()

    app.run(debug=True)