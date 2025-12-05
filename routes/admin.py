from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt, get_jwt_identity
from models import db, Exam, Question, ExamSession, User, Answer, ProctoringViolation
from datetime import datetime
from functools import wraps

admin_bp = Blueprint('admin', __name__)

def admin_required(fn):
    """Decorator to check if user is admin"""
    @wraps(fn)
    @jwt_required()
    def wrapper(*args, **kwargs):
        user_id = int(get_jwt_identity())
        user = User.query.get(user_id)
        if not user or not user.is_admin:
            return jsonify({'error': 'Admin access required'}), 403
        return fn(*args, **kwargs)
    return wrapper

@admin_bp.route('/exams', methods=['GET'])
@admin_required
def get_exams():
    """Get all exams (admin only)"""
    exams = Exam.query.all()
    return jsonify([{
        'id': exam.id,
        'title': exam.title,
        'description': exam.description,
        'duration_minutes': exam.duration_minutes,
        'is_active': exam.is_active,
        'question_count': len(exam.questions),
        'created_at': exam.created_at.isoformat()
    } for exam in exams]), 200

@admin_bp.route('/exams/<int:exam_id>', methods=['GET'])
@admin_required
def get_exam(exam_id):
    """Get single exam with questions (admin only)"""
    exam = Exam.query.get_or_404(exam_id)
    
    questions = [{
        'id': q.id,
        'question_type': q.question_type,
        'question_text': q.question_text,
        'points': q.points,
        'order': q.order,
        'options': q.options if q.question_type == 'mcq' else None,
        'correct_answer': q.correct_answer if q.question_type == 'mcq' else None,
        'max_words': q.max_words if q.question_type == 'open_ended' else None,
        'sample_answer': q.sample_answer if q.question_type == 'open_ended' else None
    } for q in sorted(exam.questions, key=lambda x: x.order)]
    
    return jsonify({
        'id': exam.id,
        'title': exam.title,
        'description': exam.description,
        'duration_minutes': exam.duration_minutes,
        'passing_score': exam.passing_score,
        'is_active': exam.is_active,
        'questions': questions,
        'created_at': exam.created_at.isoformat()
    }), 200

@admin_bp.route('/exams', methods=['POST'])
@admin_required
def create_exam():
    """Create a new exam"""
    data = request.get_json()
    
    exam = Exam(
        title=data['title'],
        description=data.get('description', ''),
        duration_minutes=data['duration_minutes'],
        passing_score=data.get('passing_score', 60.0),
        enable_tab_detection=data.get('enable_tab_detection', True),
        enable_copy_paste_prevention=data.get('enable_copy_paste_prevention', True),
        enable_video_monitoring=data.get('enable_video_monitoring', True),
        enable_ai_detection=data.get('enable_ai_detection', True),
        created_by=int(get_jwt_identity())
    )
    
    db.session.add(exam)
    db.session.commit()
    
    return jsonify({
        'message': 'Exam created successfully',
        'exam_id': exam.id
    }), 201

@admin_bp.route('/exams/<int:exam_id>', methods=['PUT'])
@admin_required
def update_exam(exam_id):
    """Update an exam"""
    exam = Exam.query.get_or_404(exam_id)
    data = request.get_json()
    
    exam.title = data.get('title', exam.title)
    exam.description = data.get('description', exam.description)
    exam.duration_minutes = data.get('duration_minutes', exam.duration_minutes)
    exam.passing_score = data.get('passing_score', exam.passing_score)
    exam.is_active = data.get('is_active', exam.is_active)
    
    db.session.commit()
    
    return jsonify({'message': 'Exam updated successfully'}), 200

@admin_bp.route('/exams/<int:exam_id>', methods=['DELETE'])
@admin_required
def delete_exam(exam_id):
    """Delete an exam"""
    from models import ProctoringViolation, Answer
    exam = Exam.query.get_or_404(exam_id)
    
    try:
        # Get all sessions for this exam
        sessions = ExamSession.query.filter_by(exam_id=exam_id).all()
        session_ids = [s.id for s in sessions]
        
        # Delete in proper order to avoid foreign key violations
        if session_ids:
            # 1. Delete proctoring violations first
            for session_id in session_ids:
                ProctoringViolation.query.filter_by(session_id=session_id).delete()
            db.session.flush()
            
            # 2. Delete answers
            for session_id in session_ids:
                Answer.query.filter_by(session_id=session_id).delete()
            db.session.flush()
            
            # 3. Delete sessions
            for session in sessions:
                db.session.delete(session)
            db.session.flush()
        
        # 4. Delete the exam (this will cascade to questions)
        db.session.delete(exam)
        db.session.commit()
        
        return jsonify({'message': 'Exam deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        print(f"Error deleting exam: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': 'Failed to delete exam', 'detail': str(e)}), 500

@admin_bp.route('/exams/<int:exam_id>/questions', methods=['POST'])
@admin_required
def add_question(exam_id):
    """Add a question to an exam"""
    exam = Exam.query.get_or_404(exam_id)
    data = request.get_json()
    
    question = Question(
        exam_id=exam_id,
        question_type=data['question_type'],
        question_text=data['question_text'],
        points=data.get('points', 1),
        order=data.get('order', len(exam.questions) + 1)
    )
    
    if data['question_type'] == 'mcq':
        question.options = data['options']
        question.correct_answer = data['correct_answer']
    else:  # open_ended
        question.max_words = data.get('max_words')
        question.sample_answer = data.get('sample_answer')
    
    db.session.add(question)
    db.session.commit()
    
    return jsonify({
        'message': 'Question added successfully',
        'question_id': question.id
    }), 201

@admin_bp.route('/questions/<int:question_id>', methods=['PUT'])
@admin_required
def update_question(question_id):
    """Update a question"""
    question = Question.query.get_or_404(question_id)
    data = request.get_json()
    
    question.question_text = data.get('question_text', question.question_text)
    question.points = data.get('points', question.points)
    question.order = data.get('order', question.order)
    
    if question.question_type == 'mcq':
        question.options = data.get('options', question.options)
        question.correct_answer = data.get('correct_answer', question.correct_answer)
    else:
        question.max_words = data.get('max_words', question.max_words)
        # sample_answer is optional for open-ended
    
    db.session.commit()
    
    return jsonify({'message': 'Question updated successfully'}), 200

@admin_bp.route('/questions/<int:question_id>', methods=['DELETE'])
@admin_required
def delete_question(question_id):
    """Delete a question"""
    question = Question.query.get_or_404(question_id)
    db.session.delete(question)
    db.session.commit()
    
    return jsonify({'message': 'Question deleted successfully'}), 200

@admin_bp.route('/sessions', methods=['GET'])
@admin_required
def get_all_sessions():
    """Get all exam sessions"""
    sessions = ExamSession.query.all()
    
    return jsonify([{
        'id': session.id,
        'exam_title': session.exam.title,
        'candidate_name': session.candidate.full_name,
        'candidate_email': session.candidate.email,
        'started_at': session.started_at.isoformat(),
        'submitted_at': session.submitted_at.isoformat() if session.submitted_at else None,
        'status': session.status,
        'total_score': session.total_score,
        'percentage': session.percentage,
        'tab_switches': session.tab_switches,
        'copy_attempts': session.copy_attempts,
        'paste_attempts': session.paste_attempts,
        'suspicious_activity_count': session.suspicious_activity_count
    } for session in sessions]), 200

@admin_bp.route('/sessions/<int:session_id>', methods=['GET'])
@admin_required
def get_session_details(session_id):
    """Get detailed session information"""
    session = ExamSession.query.get_or_404(session_id)
    
    answers = [{
        'question_id': answer.question_id,
        'question_text': answer.question.question_text,
        'question_type': answer.question.question_type,
        'answer_text': answer.answer_text,
        'selected_option': answer.selected_option,
        'correct_answer': answer.question.correct_answer if answer.question.question_type == 'mcq' else None,
        'is_ai_generated': answer.is_ai_generated,
        'ai_confidence': answer.ai_confidence,
        'ai_analysis': answer.ai_analysis,
        'score': answer.score,
        'points': answer.question.points
    } for answer in session.answers]
    
    violations = [{
        'id': v.id,
        'violation_type': v.violation_type,
        'description': v.description,
        'timestamp': v.timestamp.isoformat(),
        'severity': v.severity
    } for v in session.violations]
    
    return jsonify({
        'id': session.id,
        'exam_title': session.exam.title,
        'candidate_name': session.candidate.full_name,
        'candidate_email': session.candidate.email,
        'started_at': session.started_at.isoformat(),
        'submitted_at': session.submitted_at.isoformat() if session.submitted_at else None,
        'status': session.status,
        'total_score': session.total_score,
        'percentage': session.percentage,
        'video_recording_path': session.video_recording_path,
        'proctoring_stats': {
            'tab_switches': session.tab_switches,
            'copy_attempts': session.copy_attempts,
            'paste_attempts': session.paste_attempts,
            'suspicious_activity_count': session.suspicious_activity_count
        },
        'answers': answers,
        'violations': violations
    }), 200

@admin_bp.route('/candidates', methods=['GET'])
@admin_required
def get_candidates():
    """Get all registered candidates"""
    candidates = User.query.filter_by(is_admin=False).all()
    
    return jsonify([{
        'id': user.id,
        'email': user.email,
        'full_name': user.full_name,
        'phone': user.phone,
        'position_applied': user.position_applied,
        'qualification': user.qualification,
        'experience_years': user.experience_years,
        'current_organization': user.current_organization,
        'assigned_exam_id': user.assigned_exam_id,
        'assigned_exam_title': user.assigned_exam.title if user.assigned_exam else None,
        'created_at': user.created_at.isoformat(),
        'exams_taken': len(user.exams_taken)
    } for user in candidates]), 200

@admin_bp.route('/candidates/<int:candidate_id>/assign-exam', methods=['POST'])
@admin_required
def assign_exam_to_candidate(candidate_id):
    """Assign an exam to a candidate"""
    data = request.get_json()
    exam_id = data.get('exam_id')
    
    if not exam_id:
        return jsonify({'error': 'exam_id is required'}), 400
    
    candidate = User.query.get_or_404(candidate_id)
    exam = Exam.query.get_or_404(exam_id)
    
    if candidate.is_admin:
        return jsonify({'error': 'Cannot assign exam to admin user'}), 400
    
    candidate.assigned_exam_id = exam_id
    db.session.commit()
    
    return jsonify({
        'message': 'Exam assigned successfully',
        'candidate': candidate.full_name,
        'exam': exam.title
    }), 200
