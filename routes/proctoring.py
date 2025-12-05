from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, ExamSession, ProctoringViolation
from datetime import datetime
import base64
import os

proctoring_bp = Blueprint('proctoring', __name__)

@proctoring_bp.route('/violation', methods=['POST'])
@jwt_required()
def report_violation():
    """Report a proctoring violation"""
    user_id = int(get_jwt_identity())
    data = request.get_json()
    
    session_id = data.get('session_id')
    session = ExamSession.query.get_or_404(session_id)
    
    # Verify session belongs to user
    if session.candidate_id != user_id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    violation_type = data.get('violation_type')
    
    # Create violation record
    violation = ProctoringViolation(
        session_id=session_id,
        violation_type=violation_type,
        description=data.get('description', ''),
        severity=data.get('severity', 'medium')
    )
    
    # Update session counters
    if violation_type == 'tab_switch':
        session.tab_switches += 1
    elif violation_type == 'copy':
        session.copy_attempts += 1
    elif violation_type == 'paste':
        session.paste_attempts += 1
    
    session.suspicious_activity_count += 1
    
    # Save screenshot if provided
    if 'screenshot' in data:
        screenshot_data = data['screenshot']
        if screenshot_data.startswith('data:image'):
            # Extract base64 data
            header, encoded = screenshot_data.split(',', 1)
            screenshot_bytes = base64.b64decode(encoded)
            
            # Save to file
            filename = f"violation_{session_id}_{datetime.utcnow().timestamp()}.png"
            filepath = os.path.join('recordings', filename)
            
            with open(filepath, 'wb') as f:
                f.write(screenshot_bytes)
            
            violation.screenshot_path = filepath
    
    db.session.add(violation)
    db.session.commit()
    
    return jsonify({
        'message': 'Violation recorded',
        'violation_id': violation.id,
        'total_violations': session.suspicious_activity_count
    }), 201

@proctoring_bp.route('/session/<int:session_id>/violations', methods=['GET'])
@jwt_required()
def get_violations(session_id):
    """Get all violations for a session"""
    user_id = int(get_jwt_identity())
    session = ExamSession.query.get_or_404(session_id)
    
    # Verify session belongs to user or user is admin
    if session.candidate_id != user_id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    violations = [{
        'id': v.id,
        'violation_type': v.violation_type,
        'description': v.description,
        'timestamp': v.timestamp.isoformat(),
        'severity': v.severity
    } for v in session.violations]
    
    return jsonify(violations), 200

@proctoring_bp.route('/heartbeat', methods=['POST'])
@jwt_required()
def heartbeat():
    """Periodic heartbeat to ensure candidate is still present"""
    data = request.get_json()
    session_id = data.get('session_id')
    
    session = ExamSession.query.get_or_404(session_id)
    
    # Could add more sophisticated presence detection here
    # For now, just acknowledge
    
    return jsonify({
        'status': 'ok',
        'session_active': session.status == 'in_progress'
    }), 200

@proctoring_bp.route('/update-stats', methods=['POST'])
@jwt_required()
def update_stats():
    """Update proctoring statistics for a session"""
    user_id = int(get_jwt_identity())
    data = request.get_json()
    
    session_id = data.get('session_id')
    session = ExamSession.query.get_or_404(session_id)
    
    # Verify session belongs to user
    if session.candidate_id != user_id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    # Update stats if provided
    if 'tab_switches' in data:
        session.tab_switches = data['tab_switches']
    if 'copy_attempts' in data:
        session.copy_attempts = data['copy_attempts']
    if 'paste_attempts' in data:
        session.paste_attempts = data['paste_attempts']
    
    db.session.commit()
    
    return jsonify({'message': 'Stats updated successfully'}), 200

@proctoring_bp.route('/upload-recording', methods=['POST'])
@jwt_required()
def upload_recording():
    """Upload video recording for a session"""
    user_id = int(get_jwt_identity())
    
    if 'video' not in request.files:
        return jsonify({'error': 'No video file provided'}), 400
    
    video = request.files['video']
    session_id = request.form.get('session_id')
    
    session = ExamSession.query.get_or_404(session_id)
    
    # Verify session belongs to user
    if session.candidate_id != user_id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    # Create recordings directory if it doesn't exist
    recordings_dir = os.path.join(os.getcwd(), 'recordings')
    os.makedirs(recordings_dir, exist_ok=True)
    
    # Save video file
    filename = f"session_{session_id}_recording.webm"
    filepath = os.path.join(recordings_dir, filename)
    video.save(filepath)
    
    # Store filepath in session
    session.video_recording_path = filepath
    db.session.commit()
    
    print(f"Video recording saved: {filepath}")
    
    return jsonify({
        'message': 'Recording uploaded successfully',
        'filepath': filepath
    }), 200
