# LiveKit Voice Agent Web Interface

This web application provides a user interface for interacting with a LiveKit voice agent. It includes user authentication with a referral code system, admin dashboard for managing users and referral codes, and a real-time voice and text interface.

## Features

- User authentication (login/register) with referral code system
- Admin dashboard for managing referral codes and users
- Voice and text interaction with LiveKit agent
- Real-time communication using LiveKit WebRTC

## Installation

1. Clone the repository:
```
git clone <repository-url>
cd <repository-directory>
```

2. Install dependencies:
```
pip install -r requirements.txt
```

3. Set up environment variables:
Create a `.env` file with the following variables:
```
DEEPGRAM_API_KEY=your-deepgram-api-key
OPENAI_API_KEY=your-openai-api-key
CARTESIA_API_KEY=your-cartesia-api-key
LIVEKIT_URL=your-livekit-url
LIVEKIT_API_KEY=your-livekit-api-key
LIVEKIT_API_SECRET=your-livekit-api-secret
FLASK_SECRET_KEY=your-flask-secret-key
```

## Running the Application

Start the Flask application:
```
python app.py
```

The server will start at `http://127.0.0.1:5000/`.

## Usage

1. Admin Setup:
   - Log in with the default admin account (username: `admin`, password: `admin123`)
   - Generate referral codes in the admin dashboard
   - Share referral codes with users who need access

2. User Registration:
   - Navigate to the registration page
   - Register with a valid referral code

3. Interacting with the Voice Agent:
   - After logging in, go to the interaction page
   - Click "Connect" to establish a LiveKit connection
   - Use the microphone button to speak, or type messages in the text input

## Project Structure

```
livekitorg/
├── app.py                 # Main Flask application
├── config.py              # Configuration settings
├── database.py            # SQLite database models
├── livekit_utils.py       # LiveKit token generation utilities
├── main.py                # Original voice agent code
├── requirements.txt       # Python dependencies
├── .env                   # Environment variables (not versioned)
├── static/                # Static assets
│   ├── css/               # CSS stylesheets
│   └── js/                # JavaScript files
├── templates/             # Jinja2 templates
│   ├── admin/             # Admin dashboard templates
│   └── ...                # Other templates
└── routes/                # Flask route blueprints
    ├── admin.py           # Admin routes
    ├── api.py             # API endpoints
    └── auth.py            # Authentication routes
```

## Security Considerations

- Change the default admin password immediately after first login
- Use HTTPS in production
- Regularly rotate LiveKit API keys
- Set proper permissions for the database file