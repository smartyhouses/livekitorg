from flask import Blueprint, jsonify, request, current_app
from flask_login import current_user, login_required
import os
import traceback
from livekit_utils import generate_token, create_room
from datetime import datetime

api_bp = Blueprint('api', __name__)

@api_bp.route('/token', methods=['GET'])
@login_required
def get_token():
    """
    Generate a LiveKit token for the current logged-in user
    
    Returns:
        JSON with token and room information
    """
    # Use the user's assigned room ID from the database
    room_name = current_user.room_id
    
    # Ensure the room exists (LiveKit creates it if needed, but we could use admin API here)
    create_room(room_name)
    
    try:
        # Generate token with the user's information
        token = generate_token(
            room_name=room_name,
            participant_name=current_user.username,
            ttl_seconds=3600  # 1 hour token
        )
        
        livekit_url = os.environ.get('LIVEKIT_URL', '')
        
        # Check that URL is properly formatted (must start with wss:// or ws://)
        if not livekit_url.startswith('wss://') and not livekit_url.startswith('ws://'):
            current_app.logger.warning(f"LiveKit URL format may be invalid: {livekit_url}")
        
        return jsonify({
            'success': True,
            'token': token,
            'room': room_name,
            'username': current_user.username,
            'livekit_url': livekit_url
        })
    
    except Exception as e:
        error_traceback = traceback.format_exc()
        current_app.logger.error(f"Token generation failed: {str(e)}\n{error_traceback}")
        
        return jsonify({
            'success': False,
            'error': str(e),
            'details': error_traceback
        }), 500

@api_bp.route('/heartbeat', methods=['POST'])
@login_required
def heartbeat():
    """
    Simple heartbeat endpoint to maintain session activity
    
    Returns:
        JSON confirmation
    """
    return jsonify({
        'success': True,
        'timestamp': datetime.utcnow().isoformat(),
        'user': current_user.username,
        'room': current_user.room_id
    })

@api_bp.route('/disconnect', methods=['POST'])
@login_required
def disconnect():
    """
    Record user disconnect (optional, could be used for analytics)
    
    Returns:
        JSON confirmation
    """
    # Here you could record the disconnect event if needed
    
    return jsonify({
        'success': True,
        'message': 'Disconnect recorded'
    })