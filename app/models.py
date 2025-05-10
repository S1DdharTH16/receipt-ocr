from . import db
from datetime import datetime

class ReceiptFile(db.Model):
    __tablename__ = 'receipt_file'

    id = db.Column(db.Integer, primary_key=True)
    file_name = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(512), nullable=False)
    is_valid = db.Column(db.Boolean, default=False)
    invalid_reason = db.Column(db.String(255), nullable=True)
    is_processed = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Receipt(db.Model):
    __tablename__ = 'receipt'

    id = db.Column(db.Integer, primary_key=True)
    purchased_at = db.Column(db.DateTime, nullable=True)
    merchant_name = db.Column(db.String(255), nullable=True)
    total_amount = db.Column(db.Float, nullable=True)
    file_path = db.Column(db.String(512), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
