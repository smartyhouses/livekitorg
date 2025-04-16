from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime
import secrets

db = SQLAlchemy()

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    room_id = db.Column(db.String(64), unique=True, nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    referral_code_id = db.Column(db.Integer, db.ForeignKey('referral_code.id'))
    
    def __repr__(self):
        return f'<User {self.username}>'

class ReferralCode(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(16), unique=True, nullable=False)
    is_used = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    used_at = db.Column(db.DateTime)
    used_by = db.relationship('User', backref='referral_code', uselist=False)
    
    @staticmethod
    def generate_code():
        """Generate a random 8-character referral code"""
        return secrets.token_hex(4)  # 8 characters
    
    def __repr__(self):
        return f'<ReferralCode {self.code}>'