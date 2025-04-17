from models import Transaction, db
from datetime import datetime


def generate_transactions_report(filters):
    query = Transaction.query

    # Применение фильтров
    if filters.get('sender_bank'):
        query = query.filter(Transaction.sender_bank.ilike(f"%{filters['sender_bank']}%"))
    if filters.get('recipient_bank'):
        query = query.filter(Transaction.recipient_bank.ilike(f"%{filters['recipient_bank']}%"))
    if filters.get('status'):
        query = query.filter(Transaction.status == filters['status'])
    if filters.get('inn'):
        query = query.filter(Transaction.recipient_inn == filters['inn'])
    if filters.get('transaction_type'):
        query = query.filter(Transaction.transaction_type == filters['transaction_type'])
    if filters.get('category'):
        query = query.filter(Transaction.category == filters['category'])

    # Фильтрация по дате
    if filters.get('start_date'):
        start_date = datetime.strptime(filters['start_date'], '%d.%m.%Y')
        query = query.filter(Transaction.operation_date >= start_date)
    if filters.get('end_date'):
        end_date = datetime.strptime(filters['end_date'], '%d.%m.%Y')
        query = query.filter(Transaction.operation_date <= end_date)

    # Фильтрация по сумме
    if filters.get('min_amount'):
        query = query.filter(Transaction.amount >= float(filters['min_amount']))
    if filters.get('max_amount'):
        query = query.filter(Transaction.amount <= float(filters['max_amount']))

    transactions = query.all()
    return [t.to_dict() for t in transactions]


def generate_dashboard_data(filters):
    query = Transaction.query

    # Фильтрация по дате
    if filters.get('start_date'):
        start_date = datetime.strptime(filters['start_date'], '%d.%m.%Y')
        query = query.filter(Transaction.operation_date >= start_date)
    if filters.get('end_date'):
        end_date = datetime.strptime(filters['end_date'], '%d.%m.%Y')
        query = query.filter(Transaction.operation_date <= end_date)

    transactions = query.all()

    # Статистика по количеству транзакций
    transaction_count = len(transactions)

    # Динамика по типам транзакций
    income_count = sum(1 for t in transactions if t.transaction_type == 'Поступление')
    outcome_count = sum(1 for t in transactions if t.transaction_type == 'Списание')

    # Суммы поступлений и списаний
    income_amount = sum(float(t.amount) for t in transactions if t.transaction_type == 'Поступление')
    outcome_amount = sum(float(t.amount) for t in transactions if t.transaction_type == 'Списание')

    # Статистика по статусам
    status_stats = {}
    for t in transactions:
        status_stats[t.status] = status_stats.get(t.status, 0) + 1

    # Статистика по банкам
    sender_banks = {}
    recipient_banks = {}
    for t in transactions:
        if t.sender_bank:
            sender_banks[t.sender_bank] = sender_banks.get(t.sender_bank, 0) + 1
        if t.recipient_bank:
            recipient_banks[t.recipient_bank] = recipient_banks.get(t.recipient_bank, 0) + 1

    # Статистика по категориям
    categories = {}
    for t in transactions:
        if t.category:
            categories[t.category] = categories.get(t.category, 0) + 1

    return {
        'transaction_count': transaction_count,
        'income_count': income_count,
        'outcome_count': outcome_count,
        'income_amount': income_amount,
        'outcome_amount': outcome_amount,
        'status_stats': status_stats,
        'sender_banks': sender_banks,
        'recipient_banks': recipient_banks,
        'categories': categories
    }