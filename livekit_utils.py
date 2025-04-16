import os
import json
import hmac
import base64
import time
from hashlib import sha256
from datetime import datetime, timedelta

def generate_token(room_name, participant_name, ttl_seconds=3600):
    """
    Generate a LiveKit access token for a user using manual JWT construction
    to ensure compatibility with any LiveKit version.
    
    Args:
        room_name: Name of the LiveKit room
        participant_name: Name of the participant (username)
        ttl_seconds: Time-to-live in seconds (default 1 hour)
    
    Returns:
        str: JWT token for LiveKit access
    """
    api_key = os.environ.get('LIVEKIT_API_KEY')
    api_secret = os.environ.get('LIVEKIT_API_SECRET')
    
    if not api_key or not api_secret:
        raise ValueError("LiveKit API key and secret are required")
    
    # Create JWT header
    header = {
        "alg": "HS256",
        "typ": "JWT"
    }
    
    # Set expiration time
    now = int(time.time())
    exp = now + ttl_seconds
    
    # Create JWT payload with standard claims
    payload = {
        "iss": api_key,                # Issuer - API key
        "nbf": now,                    # Not before - current time
        "exp": exp,                    # Expiration time
        "sub": participant_name,       # Subject - participant identity
        "video": {                     # Video grants
            "room": room_name,         # Room name
            "roomJoin": True,          # Permission to join room
            "canPublish": True,        # Permission to publish tracks
            "canSubscribe": True,      # Permission to subscribe to others
            "canPublishData": True     # Permission to publish data
        },
        "name": participant_name       # Participant name for display
    }
    
    # Encode header and payload as base64
    header_bytes = json.dumps(header).encode()
    encoded_header = base64.urlsafe_b64encode(header_bytes).decode().rstrip('=')
    
    payload_bytes = json.dumps(payload).encode()
    encoded_payload = base64.urlsafe_b64encode(payload_bytes).decode().rstrip('=')
    
    # Create signature
    message = f"{encoded_header}.{encoded_payload}"
    signature = hmac.new(
        api_secret.encode(),
        message.encode(),
        sha256
    ).digest()
    encoded_signature = base64.urlsafe_b64encode(signature).decode().rstrip('=')
    
    # Create JWT token
    token = f"{message}.{encoded_signature}"
    
    return token

def create_room(room_name):
    """
    Create a LiveKit room (or ensure it exists)
    
    Args:
        room_name: Name of the LiveKit room to create
    
    Returns:
        bool: True if successful
    """
    # This would typically use the LiveKit server API
    # For now, we'll just return True since rooms are created automatically
    # when tokens are used
    return True