from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(db.Model):
    """User model for admin and candidates"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255))
    full_name = db.Column(db.String(100), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Application fields for candidates
    phone = db.Column(db.String(20))
    position_applied = db.Column(db.String(200))
    qualification = db.Column(db.String(200))  # Educational qualification
    experience_years = db.Column(db.Integer)
    current_organization = db.Column(db.String(200))
    linkedin_url = db.Column(db.String(255))
    portfolio_url = db.Column(db.String(255))
    
    # Exam assignment
    assigned_exam_id = db.Column(db.Integer, db.ForeignKey('exams.id'))
    
    # Relationships
    exams_taken = db.relationship('ExamSession', backref='candidate', lazy=True)
    assigned_exam = db.relationship('Exam', foreign_keys=[assigned_exam_id])
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        if not self.password_hash:
            return False
        return check_password_hash(self.password_hash, password)


class Exam(db.Model):
    """Exam model"""
    __tablename__ = 'exams'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    duration_minutes = db.Column(db.Integer, nullable=False)
    passing_score = db.Column(db.Float, default=60.0)
    is_active = db.Column(db.Boolean, default=True)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Proctoring settings
    enable_tab_detection = db.Column(db.Boolean, default=True)
    enable_copy_paste_prevention = db.Column(db.Boolean, default=True)
    enable_video_monitoring = db.Column(db.Boolean, default=True)
    enable_ai_detection = db.Column(db.Boolean, default=True)
    
    # Relationships
    questions = db.relationship('Question', backref='exam', lazy=True, cascade='all, delete-orphan')
    sessions = db.relationship('ExamSession', backref='exam', lazy=True, cascade='all, delete-orphan')


class Question(db.Model):
    """Question model"""
    __tablename__ = 'questions'
    
    id = db.Column(db.Integer, primary_key=True)
    exam_id = db.Column(db.Integer, db.ForeignKey('exams.id'), nullable=False)
    question_type = db.Column(db.String(20), nullable=False)  # 'mcq' or 'open_ended'
    question_text = db.Column(db.Text, nullable=False)
    points = db.Column(db.Integer, default=1)
    order = db.Column(db.Integer, default=0)
    
    # MCQ specific fields
    options = db.Column(db.JSON)  # List of options for MCQ
    correct_answer = db.Column(db.String(10))  # For MCQ: 'A', 'B', 'C', 'D'
    
    # Open-ended specific fields
    max_words = db.Column(db.Integer)
    sample_answer = db.Column(db.Text)  # For reference
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class ExamSession(db.Model):
    """Exam session tracking"""
    __tablename__ = 'exam_sessions'
    
    id = db.Column(db.Integer, primary_key=True)
    exam_id = db.Column(db.Integer, db.ForeignKey('exams.id'), nullable=False)
    candidate_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Session details
    started_at = db.Column(db.DateTime, default=datetime.utcnow)
    submitted_at = db.Column(db.DateTime)
    status = db.Column(db.String(20), default='in_progress')  # in_progress, completed, flagged
    
    # Proctoring data
    tab_switches = db.Column(db.Integer, default=0)
    copy_attempts = db.Column(db.Integer, default=0)
    paste_attempts = db.Column(db.Integer, default=0)
    suspicious_activity_count = db.Column(db.Integer, default=0)
    video_recording_path = db.Column(db.String(500))
    
    # Scoring
    total_score = db.Column(db.Float)
    percentage = db.Column(db.Float)
    
    # Relationships
    answers = db.relationship('Answer', backref='session', lazy=True, cascade='all, delete-orphan')
    violations = db.relationship('ProctoringViolation', backref='session', lazy=True, cascade='all, delete-orphan')


class Answer(db.Model):
    """Student answers"""
    __tablename__ = 'answers'
    
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey('exam_sessions.id'), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey('questions.id'), nullable=False)
    
    answer_text = db.Column(db.Text)  # For open-ended
    selected_option = db.Column(db.String(10))  # For MCQ
    
    # AI detection results
    is_ai_generated = db.Column(db.Boolean)
    ai_confidence = db.Column(db.Float)
    ai_analysis = db.Column(db.Text)
    
    score = db.Column(db.Float)
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship
    question = db.relationship('Question', backref='answers')


class ProctoringViolation(db.Model):
    """Proctoring violations log"""
    __tablename__ = 'proctoring_violations'
    
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey('exam_sessions.id'), nullable=False)
    
    violation_type = db.Column(db.String(50), nullable=False)  # tab_switch, copy, paste, no_face, multiple_faces
    description = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    severity = db.Column(db.String(20), default='medium')  # low, medium, high
    
    # Optional screenshot or frame capture
    screenshot_path = db.Column(db.String(255))
