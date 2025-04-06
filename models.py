from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, Float, Boolean, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship

db = SQLAlchemy()

# 筆記和標籤的多對多關係表
note_tags = db.Table('note_tags',
    Column('note_id', Integer, ForeignKey('note.id'), primary_key=True),
    Column('tag_id', Integer, ForeignKey('tag.id'), primary_key=True)
)

# 記帳模組 - 收支表
class Transaction(db.Model):
    __tablename__ = 'transaction'
    id = Column(Integer, primary_key=True)
    user_id = Column(String(50), nullable=False, index=True)  # LINE 用戶 ID
    amount = Column(Float, nullable=False)
    category_id = Column(Integer, ForeignKey('category.id'))
    account_id = Column(Integer, ForeignKey('account.id'))
    transaction_date = Column(DateTime, default=datetime.utcnow)
    note = Column(Text)
    is_expense = Column(Boolean, default=True)  # True = 支出, False = 收入
    created_at = Column(DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'amount': self.amount,
            'category': self.category.name if self.category else None,
            'account': self.account.name if self.account else None,
            'transaction_date': self.transaction_date.strftime('%Y-%m-%d %H:%M'),
            'note': self.note,
            'is_expense': self.is_expense,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M')
        }

# 記帳模組 - 類別管理表
class Category(db.Model):
    __tablename__ = 'category'
    id = Column(Integer, primary_key=True)
    user_id = Column(String(50), nullable=False, index=True)  # LINE 用戶 ID
    name = Column(String(50), nullable=False)
    icon = Column(String(50))  # 圖標代碼
    is_expense = Column(Boolean, default=True)  # 支出類別還是收入類別
    transactions = relationship('Transaction', backref='category', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'icon': self.icon,
            'is_expense': self.is_expense
        }

# 記帳模組 - 帳戶管理表
class Account(db.Model):
    __tablename__ = 'account'
    id = Column(Integer, primary_key=True)
    user_id = Column(String(50), nullable=False, index=True)  # LINE 用戶 ID
    name = Column(String(50), nullable=False)
    balance = Column(Float, default=0.0)
    currency = Column(String(3), default='TWD')
    account_type = Column(String(20))  # 現金、信用卡、儲蓄帳戶等
    transactions = relationship('Transaction', backref='account', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'balance': self.balance,
            'currency': self.currency,
            'account_type': self.account_type
        }

# 記事模組 - 筆記表
class Note(db.Model):
    __tablename__ = 'note'
    id = Column(Integer, primary_key=True)
    user_id = Column(String(50), nullable=False, index=True)  # LINE 用戶 ID
    title = Column(String(100), nullable=False)
    content = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    tags = relationship('Tag', secondary=note_tags, lazy='subquery',
                        backref=db.backref('notes', lazy=True))

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'content': self.content,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M'),
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M'),
            'tags': [tag.name for tag in self.tags]
        }

# 記事模組 - 標籤表
class Tag(db.Model):
    __tablename__ = 'tag'
    id = Column(Integer, primary_key=True)
    user_id = Column(String(50), nullable=False, index=True)  # LINE 用戶 ID
    name = Column(String(50), nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name
        }

# 記事模組 - 提醒事項表
class Reminder(db.Model):
    __tablename__ = 'reminder'
    id = Column(Integer, primary_key=True)
    user_id = Column(String(50), nullable=False, index=True)  # LINE 用戶 ID
    content = Column(String(200), nullable=False)
    reminder_time = Column(DateTime, nullable=False)
    repeat_type = Column(String(20))  # none, daily, weekly, monthly
    is_completed = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'content': self.content,
            'reminder_time': self.reminder_time.strftime('%Y-%m-%d %H:%M'),
            'repeat_type': self.repeat_type,
            'is_completed': self.is_completed,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M')
        } 