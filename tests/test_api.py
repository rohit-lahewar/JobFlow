import json
import base64
from datetime import date
from flask_wtf.csrf import generate_csrf
from app.models import Application, Interview
from app.extensions import db


def test_api_unauthorized_access(client):
    """Test API rejects unauthenticated requests with 401 JSON."""
    res = client.get('/api/applications')
    assert res.status_code == 401
    data = res.get_json()
    assert data['success'] is False
    assert 'Unauthorized' in data['error']


def test_api_create_and_get_applications(auth_client_a, app, user_a):
    """Test POST and GET /api/applications endpoints."""
    payload = {
        'company_name': 'Anthropic',
        'job_title': 'Research Engineer',
        'location': 'San Francisco, CA',
        'employment_type': 'Full Time',
        'work_mode': 'Hybrid',
        'salary': '$220,000',
        'status': 'Applied',
        'priority': 'High'
    }

    # POST /api/applications
    post_res = auth_client_a.post(
        '/api/applications',
        data=json.dumps(payload),
        content_type='application/json'
    )
    assert post_res.status_code == 201
    post_data = post_res.get_json()
    assert post_data['success'] is True
    assert post_data['data']['company_name'] == 'Anthropic'
    app_id = post_data['data']['id']

    # GET /api/applications/<id>
    get_res = auth_client_a.get(f'/api/applications/{app_id}')
    assert get_res.status_code == 200
    get_data = get_res.get_json()
    assert get_data['success'] is True
    assert get_data['data']['job_title'] == 'Research Engineer'

    # GET /api/applications list
    list_res = auth_client_a.get('/api/applications')
    assert list_res.status_code == 200
    list_data = list_res.get_json()
    assert list_data['count'] == 1


def test_api_validation_errors(auth_client_a):
    """Test API validation errors return 400 Bad Request."""
    # Missing required fields
    res = auth_client_a.post(
        '/api/applications',
        data=json.dumps({'location': 'Remote'}),
        content_type='application/json'
    )
    assert res.status_code == 400
    assert 'company_name and job_title' in res.get_json()['message']

    # Invalid status
    invalid_status_payload = {
        'company_name': 'Test Corp',
        'job_title': 'Dev',
        'status': 'NotAValidStatus'
    }
    res_status = auth_client_a.post(
        '/api/applications',
        data=json.dumps(invalid_status_payload),
        content_type='application/json'
    )
    assert res_status.status_code == 400


def test_api_user_isolation(auth_client_a, auth_client_b, app, user_a, user_b):
    """Test that User B cannot access User A's application via REST API (returns 403 Forbidden)."""
    with app.app_context():
        app_a = Application(user_id=user_a.id, company_name='A Corp', job_title='Eng')
        db.session.add(app_a)
        db.session.commit()
        app_a_id = app_a.id

    # User B tries GET /api/applications/<app_a_id>
    res = auth_client_b.get(f'/api/applications/{app_a_id}')
    assert res.status_code == 403
    assert res.get_json()['error'] == 'Forbidden'

    # User B tries PUT /api/applications/<app_a_id>
    put_res = auth_client_b.put(
        f'/api/applications/{app_a_id}',
        data=json.dumps({'company_name': 'Hijacked'}),
        content_type='application/json'
    )
    assert put_res.status_code == 403

    # User B tries DELETE /api/applications/<app_a_id>
    del_res = auth_client_b.delete(f'/api/applications/{app_a_id}')
    assert del_res.status_code == 403


def test_api_update_and_delete_application(auth_client_a, app, user_a):
    """Test PUT and DELETE /api/applications/<id>."""
    with app.app_context():
        app_record = Application(user_id=user_a.id, company_name='Figma', job_title='Frontend Dev')
        db.session.add(app_record)
        db.session.commit()
        app_id = app_record.id

    # Update
    update_res = auth_client_a.put(
        f'/api/applications/{app_id}',
        data=json.dumps({'status': 'Offer', 'salary': '$160,000'}),
        content_type='application/json'
    )
    assert update_res.status_code == 200
    assert update_res.get_json()['data']['status'] == 'Offer'

    # Delete
    del_res = auth_client_a.delete(f'/api/applications/{app_id}')
    assert del_res.status_code == 200

    # Verify 404 after deletion
    get_after_del = auth_client_a.get(f'/api/applications/{app_id}')
    assert get_after_del.status_code == 404


def test_api_interview_endpoints(auth_client_a, app, user_a):
    """Test /api/interviews CRUD operations."""
    with app.app_context():
        app_record = Application(user_id=user_a.id, company_name='Vercel', job_title='Fullstack SWE')
        db.session.add(app_record)
        db.session.commit()
        app_id = app_record.id

    # Create interview via API
    iv_payload = {
        'application_id': app_id,
        'round_name': 'Technical Round 1',
        'interview_type': 'Online',
        'interview_date': '2026-10-15',
        'start_time': '11:00 AM PST',
        'meeting_link': 'https://meet.google.com/test'
    }
    create_res = auth_client_a.post('/api/interviews', data=json.dumps(iv_payload), content_type='application/json')
    assert create_res.status_code == 201
    iv_id = create_res.get_json()['data']['id']

    # Get interview
    get_res = auth_client_a.get(f'/api/interviews/{iv_id}')
    assert get_res.status_code == 200
    assert get_res.get_json()['data']['round_name'] == 'Technical Round 1'

    # Update interview
    update_res = auth_client_a.put(f'/api/interviews/{iv_id}', data=json.dumps({'status': 'Completed'}), content_type='application/json')
    assert update_res.status_code == 200
    assert update_res.get_json()['data']['status'] == 'Completed'

    # Delete interview
    del_res = auth_client_a.delete(f'/api/interviews/{iv_id}')
    assert del_res.status_code == 200


def test_api_session_csrf_protection(app, user_a):
    """
    Test REST API CSRF architecture:
    1. Session-authenticated state-changing requests without CSRF token are blocked with 400.
    2. Session-authenticated read-only requests (GET) succeed without CSRF token.
    3. Session-authenticated state-changing requests with X-CSRFToken header succeed.
    4. HTTP Basic Auth clients do not require CSRF token for state-changing requests.
    """
    app.config['WTF_CSRF_ENABLED'] = True
    try:
        client = app.test_client()

        # Log in via session
        with client.session_transaction() as sess:
            sess['_user_id'] = str(user_a.id)
            sess['_fresh'] = True

        payload = json.dumps({
            'company_name': 'CSRF Protected Inc',
            'job_title': 'Security Engineer',
            'status': 'Applied',
            'priority': 'High'
        })

        # 1. State-changing POST without CSRF token must fail with 400
        res_no_csrf = client.post('/api/applications', data=payload, content_type='application/json')
        assert res_no_csrf.status_code == 400
        data_no_csrf = res_no_csrf.get_json()
        assert data_no_csrf['success'] is False
        assert data_no_csrf['error'] == 'CSRF Error'

        # 2. GET (safe method) succeeds without CSRF token
        res_get = client.get('/api/applications')
        assert res_get.status_code == 200

        # 3. State-changing POST with valid X-CSRFToken header succeeds
        with app.test_request_context():
            from flask import session
            with client.session_transaction() as sess:
                session.update(sess)
                token = generate_csrf()
                sess['csrf_token'] = session['csrf_token']

        res_with_csrf = client.post(
            '/api/applications',
            data=payload,
            content_type='application/json',
            headers={'X-CSRFToken': token}
        )
        assert res_with_csrf.status_code == 201

        # 4. HTTP Basic Auth client without CSRF token succeeds
        unauth_client = app.test_client()
        basic_header = {
            'Authorization': 'Basic ' + base64.b64encode(b'usera@example.com:Password123!').decode('utf-8')
        }
        res_basic = unauth_client.post(
            '/api/applications',
            data=json.dumps({
                'company_name': 'Basic Auth Corp',
                'job_title': 'DevOps Engineer',
                'status': 'Applied',
                'priority': 'Medium'
            }),
            content_type='application/json',
            headers=basic_header
        )
        assert res_basic.status_code == 201

    finally:
        app.config['WTF_CSRF_ENABLED'] = False

