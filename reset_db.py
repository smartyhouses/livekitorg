"""
Database Reset Script for LiveKit Voice Agent

This script completely resets the database by:
1. Deleting the SQLite database file
2. Creating a new database with the updated schema
3. Adding an admin user

Usage:
    python reset_db.py

WARNING: This will delete ALL existing user data!
"""

import os
import sys
import time
from datetime import datetime
from flask import Flask
from werkzeug.security import generate_password_hash
from config import Config

def reset_database():
    try:
        # Confirm reset
        confirm = input("WARNING: This will delete ALL existing user data. Type 'yes' to continue: ")
        if confirm.lower() != 'yes':
            print("Database reset cancelled.")
            sys.exit(0)
        
        # Get database path from config
        db_path = os.path.join('instance', 'app.db')
        absolute_path = os.path.abspath(db_path)
        
        # Delete existing database file if it exists
        if os.path.exists(db_path):
            print(f"Deleting existing database at {absolute_path}...")
            os.remove(db_path)
            print("Database file deleted.")
            
        # Small delay to ensure file operations complete
        time.sleep(1)
            
        # Create fresh Flask app
        app = Flask(__name__)
        app.config.from_object(Config)
        
        # Import db and models after database file is deleted
        from database import db, User
        db.init_app(app)
        
        with app.app_context():
            # Create all tables
            print("Creating new database with updated schema...")
            db.create_all()
            
            # Create admin user
            print("Creating admin user...")
            admin = User(
                username='admin',
                password_hash=generate_password_hash('admin123'),
                is_admin=True,
                is_activated=True,
                room_id='admin-room',
                created_at=datetime.utcnow()
            )
            db.session.add(admin)
            db.session.commit()
            
            print("Database reset complete!")
            print("\nDefault admin credentials:")
            print("Username: admin")
            print("Password: admin123")
            print("\nIMPORTANT: Change the admin password in production!")
        
    except Exception as e:
        print(f"Error during database reset: {e}")
        print("Database reset failed.")
        sys.exit(1)

if __name__ == '__main__':
    reset_database()