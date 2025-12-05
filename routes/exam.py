from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, Exam, Question, ExamSession, Answer, User
from datetime import datetime, timedelta
from services.ai_detector import detect_ai_content

exam_bp = Blueprint('exam', __name__)

@exam_bp.route('/available', methods=['GET'])
@jwt_required()
def get_available_exams():
    """Get assigned exam for candidate"""
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    
    result = []
    
    # Only show assigned exam
    if user.assigned_exam_id:
        exam = Exam.query.get(user.assigned_exam_id)
        if exam and exam.is_active:
            # Check if candidate has already taken this exam
            existing_session = ExamSession.query.filter_by(
                exam_id=exam.id,
                candidate_id=user_id
            ).first()
            
            result.append({
                'id': exam.id,
                'title': exam.title,
                'description': exam.description,
                'duration_minutes': exam.duration_minutes,
                'question_count': len(exam.questions),
                'passing_score': exam.passing_score,
                'already_taken': existing_session is not None,
                'proctoring_enabled': {
                    'tab_detection': exam.enable_tab_detection,
                    'copy_paste_prevention': exam.enable_copy_paste_prevention,
                    'video_monitoring': exam.enable_video_monitoring,
                    'ai_detection': exam.enable_ai_detection
                }
            })
    
    return jsonify(result), 200

@exam_bp.route('/<int:exam_id>/start', methods=['POST'])
@jwt_required()
def start_exam(exam_id):
    """Start an exam session"""
    user_id = int(get_jwt_identity())
    exam = Exam.query.get_or_404(exam_id)
    
    if not exam.is_active:
        return jsonify({'error': 'This exam is not currently active'}), 400
    
    # Check if already taken
    existing = ExamSession.query.filter_by(
        exam_id=exam_id,
        candidate_id=user_id
    ).first()
    
    if existing:
        return jsonify({'error': 'You have already taken this exam'}), 400
    
    # Create new session
    session = ExamSession(
        exam_id=exam_id,
        candidate_id=user_id,
        started_at=datetime.utcnow()
    )
    
    db.session.add(session)
    db.session.commit()
    
    # Get questions (without correct answers for MCQ)
    questions = []
    for q in sorted(exam.questions, key=lambda x: x.order):
        question_data = {
            'id': q.id,
            'question_type': q.question_type,
            'question_text': q.question_text,
            'points': q.points,
            'order': q.order
        }
        
        if q.question_type == 'mcq':
            question_data['options'] = q.options
        else:
            question_data['max_words'] = q.max_words
        
        questions.append(question_data)
    
    return jsonify({
        'session_id': session.id,
        'exam_title': exam.title,
        'duration_minutes': exam.duration_minutes,
        'started_at': session.started_at.isoformat() + 'Z',
        'questions': questions,
        'proctoring_settings': {
            'tab_detection': exam.enable_tab_detection,
            'copy_paste_prevention': exam.enable_copy_paste_prevention,
            'video_monitoring': exam.enable_video_monitoring,
            'ai_detection': exam.enable_ai_detection
        }
    }), 201

@exam_bp.route('/session/<int:session_id>/answer', methods=['POST'])
@jwt_required()
def submit_answer(session_id):
    """Submit an answer to a question"""
    user_id = int(get_jwt_identity())
    session = ExamSession.query.get_or_404(session_id)
    
    # Verify session belongs to user
    if session.candidate_id != user_id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    if session.status != 'in_progress':
        return jsonify({'error': 'Session is not active'}), 400
    
    data = request.get_json()
    question_id = data['question_id']
    question = Question.query.get_or_404(question_id)
    
    # Check if answer already exists
    existing_answer = Answer.query.filter_by(
        session_id=session_id,
        question_id=question_id
    ).first()
    
    if existing_answer:
        # Update existing answer
        answer = existing_answer
    else:
        # Create new answer
        answer = Answer(
            session_id=session_id,
            question_id=question_id
        )
    
    # Process based on question type
    if question.question_type == 'mcq':
        answer.selected_option = data['selected_option']
        # Auto-grade MCQ
        if answer.selected_option == question.correct_answer:
            answer.score = question.points
        else:
            answer.score = 0
    else:  # open_ended
        answer.answer_text = data['answer_text']
        
        # AI detection for open-ended answers
        if session.exam.enable_ai_detection and answer.answer_text:
            ai_result = detect_ai_content(answer.answer_text)
            answer.is_ai_generated = ai_result['is_ai_generated']
            answer.ai_confidence = ai_result['confidence']
            answer.ai_analysis = ai_result['analysis']
    
    if not existing_answer:
        db.session.add(answer)
    
    db.session.commit()
    
    return jsonify({
        'message': 'Answer saved successfully',
        'answer_id': answer.id
    }), 200

@exam_bp.route('/session/<int:session_id>/submit', methods=['POST'])
@jwt_required()
def submit_exam(session_id):
    """Submit the entire exam"""
    user_id = int(get_jwt_identity())
    session = ExamSession.query.get_or_404(session_id)
    
    # Verify session belongs to user
    if session.candidate_id != user_id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    if session.status != 'in_progress':
        return jsonify({'error': 'Session already submitted'}), 400
    
    # Calculate total score
    total_score = 0
    total_possible = 0
    
    for answer in session.answers:
        if answer.score is not None:
            total_score += answer.score
        total_possible += answer.question.points
    
    session.total_score = total_score
    session.percentage = (total_score / total_possible * 100) if total_possible > 0 else 0
    session.submitted_at = datetime.utcnow()
    session.status = 'completed'
    
    # Flag if too many violations
    if session.suspicious_activity_count > 5 or session.tab_switches > 10:
        session.status = 'flagged'
    
    db.session.commit()
    
    return jsonify({
        'message': 'Exam submitted successfully',
        'total_score': session.total_score,
        'percentage': session.percentage,
        'status': session.status
    }), 200

@exam_bp.route('/session/<int:session_id>/status', methods=['GET'])
@jwt_required()
def get_session_status(session_id):
    """Get current session status"""
    user_id = int(get_jwt_identity())
    session = ExamSession.query.get_or_404(session_id)
    
    # Verify session belongs to user
    if session.candidate_id != user_id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    return jsonify({
        'session_id': session.id,
        'status': session.status,
        'started_at': session.started_at.isoformat(),
        'submitted_at': session.submitted_at.isoformat() if session.submitted_at else None,
        'answers_submitted': len(session.answers),
        'total_questions': len(session.exam.questions)
    }), 200

@exam_bp.route('/my-results', methods=['GET'])
@jwt_required()
def get_my_results():
    """Get all exam results for current user"""
    user_id = int(get_jwt_identity())
    sessions = ExamSession.query.filter_by(candidate_id=user_id).all()
    
    results = []
    for session in sessions:
        results.append({
            'exam_title': session.exam.title,
            'started_at': session.started_at.isoformat(),
            'submitted_at': session.submitted_at.isoformat() if session.submitted_at else None,
            'status': session.status,
            'total_score': session.total_score,
            'percentage': session.percentage,
            'passing_score': session.exam.passing_score,
            'passed': session.percentage >= session.exam.passing_score if session.percentage else False
        })
    
    return jsonify(results), 200
