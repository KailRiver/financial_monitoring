from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
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

    def to_dict(self):
        return {
            'id': self.id,
            'entity_type': self.entity_type,
            'operation_date': self.operation_date.strftime('%d.%m.%Y'),
            'transaction_type': self.transaction_type,
            'comment': self.comment,
            'amount': str(self.amount),
            'status': self.status,
            'sender_bank': self.sender_bank,
            'account': self.account,
            'recipient_bank': self.recipient_bank,
            'recipient_inn': self.recipient_inn,
            'recipient_account': self.recipient_account,
            'category': self.category,
            'recipient_phone': self.recipient_phone
        }