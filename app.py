from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from config import Config
from models import db, User
import os

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Initialize extensions
    db.init_app(app)
    CORS(app, resources={
        r"/api/*": {
            "origins": "*",
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"],
            "expose_headers": ["Content-Type", "Authorization"]
        }
    })
    jwt = JWTManager(app)
    migrate = Migrate(app, db)
    
    # JWT error handlers
    @jwt.unauthorized_loader
    def unauthorized_callback(callback):
        print(f"DEBUG JWT Unauthorized: {callback}")
        return jsonify({'error': 'Missing or invalid token', 'detail': str(callback)}), 401
    
    @jwt.invalid_token_loader
    def invalid_token_callback(callback):
        print(f"DEBUG JWT Invalid Token: {callback}")
        return jsonify({'error': 'Invalid token', 'detail': str(callback)}), 422
    
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        print(f"DEBUG JWT Expired: {jwt_header}, {jwt_payload}")
        return jsonify({'error': 'Token has expired'}), 401
    
    @jwt.revoked_token_loader
    def revoked_token_callback(jwt_header, jwt_payload):
        print(f"DEBUG JWT Revoked: {jwt_header}, {jwt_payload}")
        return jsonify({'error': 'Token has been revoked'}), 401
    
    # Create upload directories
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(app.config['RECORDING_FOLDER'], exist_ok=True)
    
    # Register blueprints
    from routes.auth import auth_bp
    from routes.admin import admin_bp
    from routes.exam import exam_bp
    from routes.proctoring import proctoring_bp
    
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(admin_bp, url_prefix='/api/admin')
    app.register_blueprint(exam_bp, url_prefix='/api/exam')
    app.register_blueprint(proctoring_bp, url_prefix='/api/proctoring')
    
    # Create tables and admin user
    with app.app_context():
        db.create_all()
        create_admin_user(app)
    
    @app.route('/')
    def index():
        return jsonify({
            'message': 'Exam Proctoring System API',
            'version': '1.0.0',
            'endpoints': {
                'auth': '/api/auth',
                'admin': '/api/admin',
                'exam': '/api/exam',
                'proctoring': '/api/proctoring'
            }
        })
    
    @app.route('/recordings/<path:filename>')
    def serve_recording(filename):
        """Serve video recordings"""
        from flask import send_from_directory
        return send_from_directory(app.config['RECORDING_FOLDER'], filename)
    
    return app

def create_admin_user(app):
    """Create default admin user if not exists"""
    admin = User.query.filter_by(email=app.config['ADMIN_EMAIL']).first()
    if not admin:
        admin = User(
            email=app.config['ADMIN_EMAIL'],
            full_name='System Administrator',
            is_admin=True
        )
        admin.set_password(app.config['ADMIN_PASSWORD'])
        db.session.add(admin)
        db.session.commit()
        print(f"Admin user created: {app.config['ADMIN_EMAIL']}")

# Create app instance for Gunicorn
app = create_app()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
