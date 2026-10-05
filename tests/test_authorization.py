from datetime import date
from app.models import Application, Interview, FollowUp, Note
from app.extensions import db


def test_unauthenticated_access_blocked(client):
    """Test that unauthenticated requests to protected pages are redirected to login."""
    protected_urls = [
        '/dashboard/',
        '/applications/',
        '/applications/new',
        '/interviews/',
        '/interviews/new',
        '/followups/',
        '/analytics/',
        '/profile/'
    ]
    for url in protected_urls:
        response = client.get(url, follow_redirects=False)
        assert response.status_code == 302
        assert '/login' in response.headers.get('Location', '')


def test_user_data_isolation_application(auth_client_a, auth_client_b, app, user_a, user_b):
    """
    Test strict user isolation:
    User B must NEVER be able to view, edit, or delete User A's application.
    """
    with app.app_context():
        app_a = Application(
            user_id=user_a.id,
            company_name='Secret Company A',
            job_title='Confidential Role',
            status='Applied'
        )
        db.session.add(app_a)
        db.session.commit()
        app_a_id = app_a.id

    # 1. User A can view their own application
    res_a = auth_client_a.get(f'/applications/{app_a_id}')
    assert res_a.status_code == 200
    assert b'Secret Company A' in res_a.data

    # 2. User B attempts to VIEW User A's application by changing the ID in the URL
    res_b_view = auth_client_b.get(f'/applications/{app_a_id}')
    assert res_b_view.status_code == 404

    # 3. User B attempts to EDIT User A's application
    res_b_edit = auth_client_b.post(f'/applications/{app_a_id}/edit', data={
        'company_name': 'Hacked Company',
        'job_title': 'Hacked Role',
        'application_date': '2026-10-01',
        'status': 'Applied',
        'priority': 'Low'
    })
    assert res_b_edit.status_code == 404

    # Verify the application was not altered in the database
    with app.app_context():
        original = db.session.get(Application, app_a_id)
        assert original.company_name == 'Secret Company A'

    # 4. User B attempts to DELETE User A's application
    res_b_delete = auth_client_b.post(f'/applications/{app_a_id}/delete')
    assert res_b_delete.status_code == 404

    # Verify the application still exists
    with app.app_context():
        assert db.session.get(Application, app_a_id) is not None


def test_user_data_isolation_interviews_and_followups(auth_client_a, auth_client_b, app, user_a, user_b):
    """
    Test that User B cannot access or modify User A's interviews or follow-ups.
    """
    with app.app_context():
        app_a = Application(user_id=user_a.id, company_name='Meta', job_title='SWE')
        db.session.add(app_a)
        db.session.commit()

        iv_a = Interview(
            application_id=app_a.id,
            interview_date=date.today(),
            round_name='System Design',
            status='Scheduled'
        )
        fu_a = FollowUp(
            application_id=app_a.id,
            followup_date=date.today(),
            followup_type='Email',
            status='Pending'
        )
        note_a = Note(
            application_id=app_a.id,
            user_id=user_a.id,
            content='User A confidential notes'
        )
        db.session.add_all([iv_a, fu_a, note_a])
        db.session.commit()
        app_a_id = app_a.id
        iv_id = iv_a.id
        fu_id = fu_a.id
        note_id = note_a.id

    # User B tries to edit User A's interview
    res_iv = auth_client_b.post(f'/interviews/{iv_id}/edit', data={'status': 'Completed'})
    assert res_iv.status_code == 404

    # User B tries to delete User A's interview
    res_del_iv = auth_client_b.post(f'/interviews/{iv_id}/delete')
    assert res_del_iv.status_code == 404

    # User B tries to mark complete User A's follow-up
    res_fu = auth_client_b.post(f'/followups/{fu_id}/complete')
    assert res_fu.status_code == 404

    # User B tries to delete User A's note
    res_del_note = auth_client_b.post(f'/applications/{app_a_id}/notes/{note_id}/delete')
    assert res_del_note.status_code == 404


