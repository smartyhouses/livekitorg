from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime
import uuid

db = SQLAlchemy()

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=True)  # Nullable for pre-created accounts
    room_id = db.Column(db.String(64), unique=True, nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    is_activated = db.Column(db.Boolean, default=False)  # Track if account has been activated
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    
    @staticmethod
    def generate_room_id():
        """Generate a unique room ID for a user"""
        return f"room-{str(uuid.uuid4())}"
    
    def __repr__(self):
        return f'<User {self.username}>'

# Note: ReferralCode model has been removed as it's no longer needed