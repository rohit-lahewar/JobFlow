from datetime import datetime, date
from functools import wraps
from flask import Blueprint, request, jsonify, current_app
from flask_login import current_user
from flask_wtf.csrf import validate_csrf, ValidationError, CSRFError
from app.extensions import db
from app.models import User, Application, Interview

api_bp = Blueprint('api', __name__)


def api_auth_required(f):
    """
    Decorator for REST API endpoints ensuring authentication and CSRF protection.

    Authentication mechanisms:
    1. HTTP Basic Auth (email/password) for programmatic / non-browser REST clients.
       Because HTTP Basic Auth requires explicit credentials and does not rely on ambient
       browser cookies, it is not susceptible to cross-site request forgery.
    2. Session-based browser authentication (current_user.is_authenticated).
       When authenticating via ambient browser session cookies, state-changing requests
       (POST, PUT, PATCH, DELETE) MUST provide a valid CSRF token (via the 'X-CSRFToken'
       or 'X-CSRF-Token' header, form data, or JSON payload) so session-based browser clients
       cannot bypass CSRF protection.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # 1. Check HTTP Basic Auth credentials first (programmatic clients)
        auth = request.authorization
        if auth and auth.username and auth.password:
            user = User.query.filter_by(email=auth.username.lower().strip()).first()
            if user and user.check_password(auth.password):
                return f(user, *args, **kwargs)

        # 2. Check active session (browser-based clients)
        if current_user.is_authenticated:
            # Enforce CSRF protection on state-changing methods for session-authenticated clients
            if request.method in ['POST', 'PUT', 'PATCH', 'DELETE'] and current_app.config.get('WTF_CSRF_ENABLED', True):
                token = (
                    request.headers.get('X-CSRFToken') or
                    request.headers.get('X-CSRF-Token') or
                    request.form.get('csrf_token') or
                    (request.is_json and request.get_json(silent=True) and request.get_json(silent=True).get('csrf_token'))
                )
                try:
                    validate_csrf(token)
                except (ValidationError, CSRFError) as e:
                    error_msg = str(e.description if hasattr(e, 'description') else e) or 'CSRF token is missing or invalid.'
                    return jsonify({
                        'success': False,
                        'error': 'CSRF Error',
                        'message': error_msg
                    }), 400

            return f(current_user, *args, **kwargs)

        # 3. Return 401 Unauthorized JSON response if unauthenticated
        return jsonify({
            'success': False,
            'error': 'Unauthorized',
            'message': 'Valid session or Basic Authentication credentials required.'
        }), 401

    return decorated_function


# =====================================================================
# APPLICATIONS ENDPOINTS
# =====================================================================

@api_bp.route('/applications', methods=['GET'])
@api_auth_required
def get_applications(user):
    """GET /api/applications - List all applications for the authenticated user."""
    status_filter = request.args.get('status')
    priority_filter = request.args.get('priority')

    query = Application.query.filter_by(user_id=user.id)
    if status_filter and status_filter in Application.STATUSES:
        query = query.filter_by(status=status_filter)
    if priority_filter and priority_filter in Application.PRIORITIES:
        query = query.filter_by(priority=priority_filter)

    applications = query.order_by(Application.application_date.desc()).all()
    return jsonify({
        'success': True,
        'count': len(applications),
        'data': [app.to_dict() for app in applications]
    }), 200


@api_bp.route('/applications', methods=['POST'])
@api_auth_required
def create_application(user):
    """POST /api/applications - Create a new application."""
    data = request.get_json(silent=True)
    if not data:
        return jsonify({'success': False, 'error': 'Bad Request', 'message': 'JSON payload required.'}), 400

    company_name = data.get('company_name', '').strip()
    job_title = data.get('job_title', '').strip()

    if not company_name or not job_title:
        return jsonify({
            'success': False,
            'error': 'Validation Error',
            'message': 'company_name and job_title are required fields.'
        }), 400

    # Parse application date
    app_date = date.today()
    if data.get('application_date'):
        try:
            app_date = datetime.strptime(data['application_date'], '%Y-%m-%d').date()
        except ValueError:
            return jsonify({'success': False, 'error': 'Validation Error', 'message': 'Invalid date format for application_date. Use YYYY-MM-DD.'}), 400

    status = data.get('status', 'Applied')
    if status not in Application.STATUSES:
        return jsonify({'success': False, 'error': 'Validation Error', 'message': f"status must be one of {Application.STATUSES}"}), 400

    priority = data.get('priority', 'Medium')
    if priority not in Application.PRIORITIES:
        return jsonify({'success': False, 'error': 'Validation Error', 'message': f"priority must be one of {Application.PRIORITIES}"}), 400

    employment_type = data.get('employment_type', 'Full Time')
    if employment_type not in Application.EMPLOYMENT_TYPES:
        return jsonify({'success': False, 'error': 'Validation Error', 'message': f"employment_type must be one of {Application.EMPLOYMENT_TYPES}"}), 400

    work_mode = data.get('work_mode', 'Remote')
    if work_mode not in Application.WORK_MODES:
        return jsonify({'success': False, 'error': 'Validation Error', 'message': f"work_mode must be one of {Application.WORK_MODES}"}), 400

    application = Application(
        user_id=user.id,
        company_name=company_name,
        job_title=job_title,
        location=data.get('location'),
        employment_type=employment_type,
        work_mode=work_mode,
        salary=data.get('salary'),
        job_url=data.get('job_url'),
        application_date=app_date,
        status=status,
        priority=priority,
        recruiter_name=data.get('recruiter_name'),
        recruiter_email=data.get('recruiter_email'),
        job_description=data.get('job_description'),
        notes=data.get('notes')
    )

    db.session.add(application)
    db.session.commit()

    return jsonify({
        'success': True,
        'message': 'Application created successfully.',
        'data': application.to_dict()
    }), 201


@api_bp.route('/applications/<int:id>', methods=['GET'])
@api_auth_required
def get_application(user, id):
    """GET /api/applications/<id> - Retrieve a single application with authorization check."""
    application = Application.query.filter_by(id=id).first()
    if not application:
        return jsonify({'success': False, 'error': 'Not Found', 'message': f"Application with ID {id} not found."}), 404

    # Strict isolation check
    if application.user_id != user.id:
        return jsonify({'success': False, 'error': 'Forbidden', 'message': 'You do not have access to this application.'}), 403

    return jsonify({
        'success': True,
        'data': application.to_dict()
    }), 200


@api_bp.route('/applications/<int:id>', methods=['PUT'])
@api_auth_required
def update_application(user, id):
    """PUT /api/applications/<id> - Update an application."""
    application = Application.query.filter_by(id=id).first()
    if not application:
        return jsonify({'success': False, 'error': 'Not Found', 'message': f"Application with ID {id} not found."}), 404

    if application.user_id != user.id:
        return jsonify({'success': False, 'error': 'Forbidden', 'message': 'You do not have access to this application.'}), 403

    data = request.get_json(silent=True)
    if not data:
        return jsonify({'success': False, 'error': 'Bad Request', 'message': 'JSON payload required.'}), 400

    if 'company_name' in data:
        if not data['company_name'].strip():
            return jsonify({'success': False, 'error': 'Validation Error', 'message': 'company_name cannot be empty.'}), 400
        application.company_name = data['company_name'].strip()

    if 'job_title' in data:
        if not data['job_title'].strip():
            return jsonify({'success': False, 'error': 'Validation Error', 'message': 'job_title cannot be empty.'}), 400
        application.job_title = data['job_title'].strip()

    if 'location' in data:
        application.location = data['location']
    if 'salary' in data:
        application.salary = data['salary']
    if 'job_url' in data:
        application.job_url = data['job_url']
    if 'recruiter_name' in data:
        application.recruiter_name = data['recruiter_name']
    if 'recruiter_email' in data:
        application.recruiter_email = data['recruiter_email']
    if 'job_description' in data:
        application.job_description = data['job_description']
    if 'notes' in data:
        application.notes = data['notes']

    if 'status' in data:
        if data['status'] not in Application.STATUSES:
            return jsonify({'success': False, 'error': 'Validation Error', 'message': f"status must be one of {Application.STATUSES}"}), 400
        application.status = data['status']

    if 'priority' in data:
        if data['priority'] not in Application.PRIORITIES:
            return jsonify({'success': False, 'error': 'Validation Error', 'message': f"priority must be one of {Application.PRIORITIES}"}), 400
        application.priority = data['priority']

    if 'employment_type' in data:
        if data['employment_type'] not in Application.EMPLOYMENT_TYPES:
            return jsonify({'success': False, 'error': 'Validation Error', 'message': f"employment_type must be one of {Application.EMPLOYMENT_TYPES}"}), 400
        application.employment_type = data['employment_type']

    if 'work_mode' in data:
        if data['work_mode'] not in Application.WORK_MODES:
            return jsonify({'success': False, 'error': 'Validation Error', 'message': f"work_mode must be one of {Application.WORK_MODES}"}), 400
        application.work_mode = data['work_mode']

    if 'application_date' in data:
        try:
            application.application_date = datetime.strptime(data['application_date'], '%Y-%m-%d').date()
        except ValueError:
            return jsonify({'success': False, 'error': 'Validation Error', 'message': 'Invalid date format for application_date. Use YYYY-MM-DD.'}), 400

    db.session.commit()
    return jsonify({
        'success': True,
        'message': 'Application updated successfully.',
        'data': application.to_dict()
    }), 200


@api_bp.route('/applications/<int:id>', methods=['DELETE'])
@api_auth_required
def delete_application(user, id):
    """DELETE /api/applications/<id> - Delete an application and its child entities."""
    application = Application.query.filter_by(id=id).first()
    if not application:
        return jsonify({'success': False, 'error': 'Not Found', 'message': f"Application with ID {id} not found."}), 404

    if application.user_id != user.id:
        return jsonify({'success': False, 'error': 'Forbidden', 'message': 'You do not have access to this application.'}), 403

    db.session.delete(application)
    db.session.commit()
    return jsonify({
        'success': True,
        'message': f"Application with ID {id} and associated records deleted."
    }), 200


# =====================================================================
# INTERVIEWS ENDPOINTS
# =====================================================================

@api_bp.route('/interviews', methods=['GET'])
@api_auth_required
def get_interviews(user):
    """GET /api/interviews - List all interviews for the authenticated user."""
    interviews = (
        Interview.query.join(Application)
        .filter(Application.user_id == user.id)
        .order_by(Interview.interview_date.desc())
        .all()
    )
    return jsonify({
        'success': True,
        'count': len(interviews),
        'data': [iv.to_dict() for iv in interviews]
    }), 200


@api_bp.route('/interviews', methods=['POST'])
@api_auth_required
def create_interview(user):
    """POST /api/interviews - Create a new interview round for one of the user's applications."""
    data = request.get_json(silent=True)
    if not data:
        return jsonify({'success': False, 'error': 'Bad Request', 'message': 'JSON payload required.'}), 400

    application_id = data.get('application_id')
    if not application_id:
        return jsonify({'success': False, 'error': 'Validation Error', 'message': 'application_id is required.'}), 400

    # Strict authorization: Verify application belongs to user
    application = Application.query.filter_by(id=application_id).first()
    if not application:
        return jsonify({'success': False, 'error': 'Not Found', 'message': f"Application with ID {application_id} not found."}), 404

    if application.user_id != user.id:
        return jsonify({'success': False, 'error': 'Forbidden', 'message': 'Cannot schedule interview for an application you do not own.'}), 403

    # Date validation
    date_str = data.get('interview_date')
    if not date_str:
        return jsonify({'success': False, 'error': 'Validation Error', 'message': 'interview_date is required.'}), 400
    try:
        iv_date = datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        return jsonify({'success': False, 'error': 'Validation Error', 'message': 'Invalid date format. Use YYYY-MM-DD.'}), 400

    round_name = data.get('round_name', 'Technical Round 1')
    interview_type = data.get('interview_type', 'Online')
    status = data.get('status', 'Scheduled')

    interview = Interview(
        application_id=application.id,
        interview_date=iv_date,
        start_time=data.get('start_time'),
        round_name=round_name,
        interview_type=interview_type,
        meeting_link=data.get('meeting_link'),
        interviewer=data.get('interviewer'),
        status=status,
        notes=data.get('notes')
    )
    db.session.add(interview)

    if application.status in ['Applied', 'Shortlisted']:
        application.status = 'Interview'

    db.session.commit()

    return jsonify({
        'success': True,
        'message': 'Interview created successfully.',
        'data': interview.to_dict()
    }), 201


@api_bp.route('/interviews/<int:id>', methods=['GET'])
@api_auth_required
def get_interview(user, id):
    """GET /api/interviews/<id> - Retrieve an interview with authorization check."""
    interview = Interview.query.filter_by(id=id).first()
    if not interview:
        return jsonify({'success': False, 'error': 'Not Found', 'message': f"Interview with ID {id} not found."}), 404

    if interview.application.user_id != user.id:
        return jsonify({'success': False, 'error': 'Forbidden', 'message': 'You do not have access to this interview.'}), 403

    return jsonify({
        'success': True,
        'data': interview.to_dict()
    }), 200


@api_bp.route('/interviews/<int:id>', methods=['PUT'])
@api_auth_required
def update_interview(user, id):
    """PUT /api/interviews/<id> - Update an interview."""
    interview = Interview.query.filter_by(id=id).first()
    if not interview:
        return jsonify({'success': False, 'error': 'Not Found', 'message': f"Interview with ID {id} not found."}), 404

    if interview.application.user_id != user.id:
        return jsonify({'success': False, 'error': 'Forbidden', 'message': 'You do not have access to this interview.'}), 403

    data = request.get_json(silent=True)
    if not data:
        return jsonify({'success': False, 'error': 'Bad Request', 'message': 'JSON payload required.'}), 400

    if 'interview_date' in data:
        try:
            interview.interview_date = datetime.strptime(data['interview_date'], '%Y-%m-%d').date()
        except ValueError:
            return jsonify({'success': False, 'error': 'Validation Error', 'message': 'Invalid date format. Use YYYY-MM-DD.'}), 400

    if 'start_time' in data:
        interview.start_time = data['start_time']
    if 'round_name' in data:
        interview.round_name = data['round_name']
    if 'interview_type' in data:
        interview.interview_type = data['interview_type']
    if 'meeting_link' in data:
        interview.meeting_link = data['meeting_link']
    if 'interviewer' in data:
        interview.interviewer = data['interviewer']
    if 'status' in data:
        if data['status'] not in Interview.STATUSES:
            return jsonify({'success': False, 'error': 'Validation Error', 'message': f"status must be one of {Interview.STATUSES}"}), 400
        interview.status = data['status']
    if 'notes' in data:
        interview.notes = data['notes']

    db.session.commit()
    return jsonify({
        'success': True,
        'message': 'Interview updated successfully.',
        'data': interview.to_dict()
    }), 200


@api_bp.route('/interviews/<int:id>', methods=['DELETE'])
@api_auth_required
def delete_interview(user, id):
    """DELETE /api/interviews/<id> - Delete an interview."""
    interview = Interview.query.filter_by(id=id).first()
    if not interview:
        return jsonify({'success': False, 'error': 'Not Found', 'message': f"Interview with ID {id} not found."}), 404

    if interview.application.user_id != user.id:
        return jsonify({'success': False, 'error': 'Forbidden', 'message': 'You do not have access to this interview.'}), 403

    db.session.delete(interview)
    db.session.commit()
    return jsonify({
        'success': True,
        'message': f"Interview with ID {id} deleted successfully."
    }), 200
