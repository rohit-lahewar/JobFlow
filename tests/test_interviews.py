from datetime import date, timedelta
from app.models import Application, Interview
from app.extensions import db


def test_create_interview(auth_client_a, app, user_a):
    """Test creating an interview round for an application."""
    with app.app_context():
        app_record = Application(
            user_id=user_a.id,
            company_name='Airbnb',
            job_title='Infrastructure Engineer',
            status='Applied'
        )
        db.session.add(app_record)
        db.session.commit()
        app_id = app_record.id

    tomorrow = (date.today() + timedelta(days=1)).strftime('%Y-%m-%d')
    response = auth_client_a.post('/interviews/new', data={
        'application_id': app_id,
        'round_name': 'Technical Round 1',
        'interview_type': 'Online',
        'interview_date': tomorrow,
        'start_time': '2:00 PM EST',
        'meeting_link': 'https://meet.google.com/test-room',
        'interviewer': 'Alice Smith',
        'status': 'Scheduled',
        'notes': 'Algorithms and architecture.'
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b'scheduled successfully' in response.data

    with app.app_context():
        iv = Interview.query.filter_by(application_id=app_id).first()
        assert iv is not None
        assert iv.round_name == 'Technical Round 1'
        assert iv.interviewer == 'Alice Smith'
        # Automatic promotion of application to 'Interview' status
        assert iv.application.status == 'Interview'


def test_edit_and_delete_interview(auth_client_a, app, user_a):
    """Test updating and deleting an interview."""
    with app.app_context():
        app_record = Application(user_id=user_a.id, company_name='Reddit', job_title='SWE')
        db.session.add(app_record)
        db.session.commit()
        app_id = app_record.id

        iv = Interview(
            application_id=app_id,
            interview_date=date.today(),
            round_name='Online Assessment',
            status='Scheduled'
        )
        db.session.add(iv)
        db.session.commit()
        iv_id = iv.id

    # Edit status to Completed
    response = auth_client_a.post(f'/interviews/{iv_id}/edit', data={
        'application_id': app_id,
        'round_name': 'Online Assessment',
        'interview_type': 'Online',
        'interview_date': date.today().strftime('%Y-%m-%d'),
        'status': 'Completed'
    }, follow_redirects=True)

    assert response.status_code == 200
    with app.app_context():
        updated_iv = db.session.get(Interview, iv_id)
        assert updated_iv.status == 'Completed'

    # Delete interview
    del_response = auth_client_a.post(f'/interviews/{iv_id}/delete', follow_redirects=True)
    assert del_response.status_code == 200
    with app.app_context():
        assert db.session.get(Interview, iv_id) is None
