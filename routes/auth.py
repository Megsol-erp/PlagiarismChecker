from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from models import db, User

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    """Register a new candidate"""
    data = request.get_json()
    
    # Validate input
    if not all(k in data for k in ['email', 'password', 'full_name']):
        return jsonify({'error': 'Missing required fields'}), 400
    
    # Check if user exists
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Email already registered'}), 400
    
    # Create new user
    user = User(
        email=data['email'],
        full_name=data['full_name'],
        is_admin=False
    )
    user.set_password(data['password'])
    
    db.session.add(user)
    db.session.commit()
    
    return jsonify({
        'message': 'Registration successful',
        'user': {
            'id': user.id,
            'email': user.email,
            'full_name': user.full_name
        }
    }), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    """Login for both admin and candidates"""
    data = request.get_json()
    
    if not all(k in data for k in ['email', 'password']):
        return jsonify({'error': 'Missing email or password'}), 400
    
    user = User.query.filter_by(email=data['email']).first()
    
    if not user or not user.check_password(data['password']):
        return jsonify({'error': 'Invalid credentials'}), 401
    
    access_token = create_access_token(
        identity=str(user.id),
        additional_claims={'is_admin': user.is_admin}
    )
    
    print(f"DEBUG: Created token for user {user.id}: {access_token[:50]}...")
    
    return jsonify({
        'access_token': access_token,
        'user': {
            'id': user.id,
            'email': user.email,
            'full_name': user.full_name,
            'is_admin': user.is_admin
        }
    }), 200

@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    """Get current user details"""
    # Debug logging
    from flask import request as flask_request
    print(f"DEBUG: Headers: {dict(flask_request.headers)}")
    print(f"DEBUG: Authorization header: {flask_request.headers.get('Authorization')}")
    
    user_id = int(get_jwt_identity())
    print(f"DEBUG: User ID from token: {user_id}")
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    return jsonify({
        'id': user.id,
        'email': user.email,
        'full_name': user.full_name,
        'is_admin': user.is_admin
    }), 200

@auth_bp.route('/candidate/apply', methods=['POST'])
def candidate_apply():
    """Candidate application without password - generates auto-login token"""
    data = request.get_json()
    
    # Validate required fields
    required_fields = ['email', 'full_name', 'phone', 'position_applied', 'qualification', 'experience_years']
    if not all(k in data for k in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400
    
    # Check if user exists
    existing_user = User.query.filter_by(email=data['email']).first()
    if existing_user:
        return jsonify({'error': 'Email already registered. Please contact admin.'}), 400
    
    # Create new candidate without password
    user = User(
        email=data['email'],
        full_name=data['full_name'],
        phone=data.get('phone'),
        position_applied=data.get('position_applied'),
        qualification=data.get('qualification'),
        experience_years=data.get('experience_years'),
        current_organization=data.get('current_organization'),
        linkedin_url=data.get('linkedin_url'),
        portfolio_url=data.get('portfolio_url'),
        is_admin=False
    )
    
    db.session.add(user)
    db.session.commit()
    
    # Create access token for auto-login
    access_token = create_access_token(
        identity=str(user.id),
        additional_claims={'is_admin': False}
    )
    
    return jsonify({
        'message': 'Application submitted successfully',
        'access_token': access_token,
        'user': {
            'id': user.id,
            'email': user.email,
            'full_name': user.full_name
        }
    }), 201
