import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    # Flask configuration
    SECRET_KEY = os.environ.get('FLASK_SECRET_KEY', 'dev-secret-key-change-in-production')
    
    # Database configuration
    SQLALCHEMY_DATABASE_URI = 'sqlite:///app.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # LiveKit configuration
    LIVEKIT_URL = os.environ.get('LIVEKIT_URL', '')
    LIVEKIT_API_KEY = os.environ.get('LIVEKIT_API_KEY', '')
    LIVEKIT_API_SECRET = os.environ.get('LIVEKIT_API_SECRET', '')