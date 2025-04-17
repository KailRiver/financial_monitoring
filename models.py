from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import event
from datetime import datetime

db = SQLAlchemy()


class TransactionStatus:
    NEW = 'Новая'
    CONFIRMED = 'Подтвержденная'
    PROCESSING = 'В обработке'
    CANCELLED = 'Отменена'
    COMPLETED = 'Платеж выполнен'
    DELETED = 'Платеж удален'
    REFUND = 'Возврат'

    @classmethod
    def all_statuses(cls):
        return [
            cls.NEW, cls.CONFIRMED, cls.PROCESSING,
            cls.CANCELLED, cls.COMPLETED, cls.DELETED, cls.REFUND
        ]

    @classmethod
    def non_editable_statuses(cls):
        return [
            cls.CONFIRMED, cls.PROCESSING,
            cls.CANCELLED, cls.COMPLETED, cls.DELETED, cls.REFUND
        ]

    @classmethod
    def non_deletable_statuses(cls):
        return [
            cls.CONFIRMED, cls.PROCESSING,
            cls.CANCELLED, cls.COMPLETED, cls.REFUND
        ]


class Transaction(db.Model):
    __tablename__ = 'transactions'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    entity_type = db.Column(db.String(20), nullable=False)  # Физическое/Юридическое лицо
    operation_date = db.Column(db.DateTime, nullable=False)
    transaction_type = db.Column(db.String(20), nullable=False)  # Поступление/Списание
    comment = db.Column(db.String(500))
    amount = db.Column(db.Numeric(15, 5), nullable=False)
    status = db.Column(db.String(20), nullable=False)
    sender_bank = db.Column(db.String(100))
    account = db.Column(db.String(50))
    recipient_bank = db.Column(db.String(100))
    recipient_inn = db.Column(db.String(12))
    recipient_account = db.Column(db.String(50))
    category = db.Column(db.String(50))
    recipient_phone = db.Column(db.String(20))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __init__(self, **kwargs):
        super(Transaction, self).__init__(**kwargs)
        self.validate_status(self.status)

    @classmethod
    def validate_status(cls, status):
        if status not in TransactionStatus.all_statuses():
            raise ValueError(f"Недопустимый статус: {status}. Допустимые значения: {TransactionStatus.all_statuses()}")

    def to_dict(self):
        return {
            'id': self.id,
            'entity_type': self.entity_type,
            'operation_date': self.operation_date.strftime('%d.%m.%Y'),
            'transaction_type': self.transaction_type,
            'comment': self.comment,
            'amount': float(self.amount),
            'status': self.status,
            'sender_bank': self.sender_bank,
            'account': self.account,
            'recipient_bank': self.recipient_bank,
            'recipient_inn': self.recipient_inn,
            'recipient_account': self.recipient_account,
            'category': self.category,
            'recipient_phone': self.recipient_phone
        }


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    transactions = db.relationship('Transaction', backref='user', lazy=True)

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)


def init_db(app):
    db.init_app(app)
    with app.app_context():
        db.create_all()