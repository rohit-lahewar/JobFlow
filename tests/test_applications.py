from datetime import date
from app.models import Application, Note
from app.extensions import db


def test_create_application(auth_client_a, app, user_a):
    """Test creating an application via form."""
    response = auth_client_a.post('/applications/new', data={
        'company_name': 'Netflix',
        'job_title': 'Senior Python Engineer',
        'location': 'Los Gatos, CA',
        'employment_type': 'Full Time',
        'work_mode': 'Remote',
        'salary': '$190,000',
        'job_url': 'https://netflix.com/jobs/123',
        'application_date': '2026-10-01',
        'status': 'Applied',
        'priority': 'High',
        'recruiter_name': 'Sarah Connor',
        'recruiter_email': 'sconnor@netflix.com',
        'job_description': 'Core streaming infrastructure.',
        'notes': 'Referred by engineer.'
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b'created successfully' in response.data

    with app.app_context():
        application = Application.query.filter_by(company_name='Netflix').first()
        assert application is not None
        assert application.user_id == user_a.id
        assert application.job_title == 'Senior Python Engineer'
        assert application.status == 'Applied'
        assert application.priority == 'High'


def test_view_application_detail(auth_client_a, app, user_a):
    """Test viewing an application detail page."""
    with app.app_context():
        app_record = Application(
            user_id=user_a.id,
            company_name='Spotify',
            job_title='Backend Developer',
            status='Applied',
            priority='Medium'
        )
        db.session.add(app_record)
        db.session.commit()
        app_id = app_record.id

    response = auth_client_a.get(f'/applications/{app_id}')
    assert response.status_code == 200
    assert b'Spotify' in response.data
    assert b'Backend Developer' in response.data


def test_edit_application(auth_client_a, app, user_a):
    """Test updating application details."""
    with app.app_context():
        app_record = Application(
            user_id=user_a.id,
            company_name='Uber',
            job_title='Software Engineer',
            status='Applied',
            priority='Medium'
        )
        db.session.add(app_record)
        db.session.commit()
        app_id = app_record.id

    response = auth_client_a.post(f'/applications/{app_id}/edit', data={
        'company_name': 'Uber Technologies',
        'job_title': 'Staff Software Engineer',
        'location': 'San Francisco, CA',
        'employment_type': 'Full Time',
        'work_mode': 'Hybrid',
        'application_date': '2026-10-01',
        'status': 'Interview',
        'priority': 'High'
    }, follow_redirects=True)

    assert response.status_code == 200

    with app.app_context():
        updated = db.session.get(Application, app_id)
        assert updated.company_name == 'Uber Technologies'
        assert updated.job_title == 'Staff Software Engineer'
        assert updated.status == 'Interview'


def test_delete_application(auth_client_a, app, user_a):
    """Test deleting an application."""
    with app.app_context():
        app_record = Application(
            user_id=user_a.id,
            company_name='To Be Deleted Corp',
            job_title='Intern',
            status='Applied'
        )
        db.session.add(app_record)
        db.session.commit()
        app_id = app_record.id

    response = auth_client_a.post(f'/applications/{app_id}/delete', follow_redirects=True)
    assert response.status_code == 200

    with app.app_context():
        assert db.session.get(Application, app_id) is None


def test_search_and_filter_applications(auth_client_a, app, user_a):
    """Test searching by company and filtering by status."""
    with app.app_context():
        app1 = Application(user_id=user_a.id, company_name='Apple', job_title='iOS Backend', status='Applied', priority='High')
        app2 = Application(user_id=user_a.id, company_name='Microsoft', job_title='Cloud SWE', status='Interview', priority='Medium')
        app3 = Application(user_id=user_a.id, company_name='Meta', job_title='Data Engineer', status='Offer', priority='High')
        db.session.add_all([app1, app2, app3])
        db.session.commit()

    # Search for "Apple"
    res1 = auth_client_a.get('/applications/?search=Apple')
    assert b'Apple' in res1.data
    assert b'Microsoft' not in res1.data

    # Filter for status="Interview"
    res2 = auth_client_a.get('/applications/?status=Interview')
    assert b'Microsoft' in res2.data
    assert b'Apple' not in res2.data

    # Filter for priority="High"
    res3 = auth_client_a.get('/applications/?priority=High')
    assert b'Apple' in res3.data
    assert b'Meta' in res3.data
    assert b'Microsoft' not in res3.data


def test_add_and_delete_note(auth_client_a, app, user_a):
    """Test adding a note to an application and deleting it."""
    with app.app_context():
        app_record = Application(user_id=user_a.id, company_name='Twilio', job_title='Platform Engineer')
        db.session.add(app_record)
        db.session.commit()
        app_id = app_record.id

    # Add Note
    res = auth_client_a.post(f'/applications/{app_id}/notes', data={
        'content': 'Recruiter mentioned system design is focused on distributed queues.'
    }, follow_redirects=True)
    assert res.status_code == 200

    with app.app_context():
        note = Note.query.filter_by(application_id=app_id).first()
        assert note is not None
        assert 'distributed queues' in note.content
        note_id = note.id

    # Delete Note
    del_res = auth_client_a.post(f'/applications/{app_id}/notes/{note_id}/delete', follow_redirects=True)
    assert del_res.status_code == 200

    with app.app_context():
        assert db.session.get(Note, note_id) is None

