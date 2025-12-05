# Exam Proctoring & Plagiarism Detection System

A comprehensive web-based exam proctoring system with advanced anti-cheating features including AI content detection, video monitoring, tab switching detection, and copy/paste prevention.

## Features

### For Administrators
- **Exam Management**: Create, edit, and manage exams
- **Question Bank**: Add MCQ and open-ended questions
- **Live Monitoring**: Track candidate sessions in real-time
- **Violation Reports**: View detailed proctoring violations
- **Results Dashboard**: Analyze candidate performance
- **Configurable Proctoring**: Enable/disable specific proctoring features per exam

### For Candidates
- **Secure Exam Environment**: Fullscreen mode with proctoring
- **Multiple Question Types**: MCQ and open-ended questions
- **Auto-Save**: Answers saved automatically
- **Timer**: Countdown timer with warnings
- **Results**: View exam scores and feedback

### Anti-Cheating Features
- ✅ **Tab Switching Detection**: Detects when candidates leave the exam tab
- ✅ **Copy/Paste Prevention**: Blocks clipboard operations
- ✅ **Video Monitoring**: Webcam recording throughout the exam
- ✅ **AI Content Detection**: Analyzes open-ended answers for AI-generated content
- ✅ **Fullscreen Enforcement**: Requires fullscreen mode during exam
- ✅ **Right-Click Disabled**: Prevents context menu access
- ✅ **DevTools Prevention**: Blocks common developer tool shortcuts
- ✅ **Face Detection**: Monitors presence of candidate (configurable)

## Tech Stack

### Backend
- **Flask**: Python web framework
- **SQLAlchemy**: ORM for database operations
- **JWT**: Secure authentication
- **OpenAI API**: AI content detection
- **Flask-CORS**: Cross-origin resource sharing

### Frontend
- **Pure HTML/CSS/JavaScript**: No framework dependencies
- **WebRTC**: Webcam access
- **Fullscreen API**: Fullscreen enforcement
- **Visibility API**: Tab switching detection

## Installation

### Prerequisites
- Python 3.8+
- Virtual environment (recommended)
- OpenAI API key (optional, for AI detection)

### Setup

1. **Activate your virtual environment**:
```bash
source ~/venv/bin/activate
```

2. **Install dependencies**:
```bash
cd /media/banaibor/Projects/resGov/PlagarismChecker
pip install -r requirements.txt
```

3. **Configure environment variables**:
```bash
cp .env.example .env
```

Edit `.env` file with your settings:
```
SECRET_KEY=your-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-here
OPENAI_API_KEY=your-openai-api-key  # Optional
ADMIN_EMAIL=admin@example.com
ADMIN_PASSWORD=your-secure-password
```

4. **Initialize the database**:
```bash
python app.py
```

The database will be created automatically on first run.

## Running the Application

### Development Mode
```bash
source ~/venv/bin/activate
python app.py
```

The server will start on `http://localhost:5000`

### Production Mode
```bash
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

## Usage

### Access Points

1. **Main Login**: `http://localhost:5000/static/index.html`
2. **Admin Dashboard**: Login as admin, automatically redirected
3. **Candidate Dashboard**: Login as candidate, automatically redirected

### Default Admin Credentials
- **Email**: admin@example.com (or as configured in .env)
- **Password**: admin123 (or as configured in .env)

### Creating an Exam (Admin)

1. Login as admin
2. Click "Create New Exam"
3. Fill in exam details:
   - Title, description, duration
   - Passing score
   - Enable/disable proctoring features
4. Add questions:
   - Click "Questions" button on the exam
   - Add MCQ or open-ended questions
   - Set points for each question

### Taking an Exam (Candidate)

1. Register/Login as candidate
2. View available exams on dashboard
3. Click "Start Exam"
4. Grant webcam and fullscreen permissions
5. Answer questions
6. Submit exam before time expires

## API Endpoints

### Authentication
- `POST /api/auth/register` - Register new candidate
- `POST /api/auth/login` - Login
- `GET /api/auth/me` - Get current user

### Admin
- `GET /api/admin/exams` - List all exams
- `POST /api/admin/exams` - Create exam
- `PUT /api/admin/exams/<id>` - Update exam
- `DELETE /api/admin/exams/<id>` - Delete exam
- `POST /api/admin/exams/<id>/questions` - Add question
- `GET /api/admin/sessions` - View all sessions
- `GET /api/admin/sessions/<id>` - Session details

### Exam
- `GET /api/exam/available` - List available exams
- `POST /api/exam/<id>/start` - Start exam session
- `POST /api/exam/session/<id>/answer` - Submit answer
- `POST /api/exam/session/<id>/submit` - Submit exam
- `GET /api/exam/my-results` - Get candidate results

### Proctoring
- `POST /api/proctoring/violation` - Report violation
- `GET /api/proctoring/session/<id>/violations` - Get violations
- `POST /api/proctoring/heartbeat` - Keep-alive ping

## Security Features

### Authentication
- JWT-based authentication
- Password hashing with bcrypt
- Role-based access control (admin/candidate)

### Proctoring
- Violation tracking and reporting
- Screenshot capture on violations
- Session flags for suspicious activity
- Automatic exam submission on time expiry

### Data Protection
- SQL injection prevention via ORM
- CORS configuration
- Input validation and sanitization

## AI Content Detection

The system uses two methods for AI detection:

1. **OpenAI API** (if API key provided):
   - GPT-4 based analysis
   - High accuracy detection
   - Detailed reasoning

2. **Pattern-Based Detection** (fallback):
   - Sentence length analysis
   - Grammar patterns
   - Common AI phrases detection
   - Paragraph uniformity checks

## Customization

### Proctoring Settings
Each exam can have different proctoring settings:
- Tab switching detection: ON/OFF
- Copy/paste prevention: ON/OFF
- Video monitoring: ON/OFF
- AI content detection: ON/OFF

### Scoring
- MCQ questions: Auto-graded
- Open-ended: Manual grading + AI detection flag
- Configurable passing score per exam

## Troubleshooting

### Webcam Not Working
- Ensure browser has camera permissions
- Try using HTTPS in production
- Check if camera is being used by another app

### Tab Detection Not Working
- Works only in fullscreen mode
- Some browsers may have different behaviors
- Check browser console for errors

### AI Detection Not Working
- Verify OpenAI API key is set correctly
- Falls back to pattern detection if API unavailable
- Check API quota and billing

## Future Enhancements

- [ ] Advanced face recognition with TensorFlow.js
- [ ] Multiple face detection (prevent proxy test-takers)
- [ ] Eye tracking for attention monitoring
- [ ] Audio monitoring for voice detection
- [ ] Screen recording playback for admins
- [ ] Mobile app support
- [ ] Integration with LMS platforms
- [ ] Advanced analytics and reporting
- [ ] Question pool and randomization
- [ ] Bulk candidate import

## License

MIT License - feel free to use and modify for your organization.

## Support

For issues and questions, please create an issue in the repository or contact the administrator.

## Credits

Built with Flask, SQLAlchemy, and modern web technologies for secure online examination.
