from datetime import date, timedelta
from app.models import Application, FollowUp
from app.extensions import db


def test_create_and_complete_followup(auth_client_a, app, user_a):
    """Test scheduling and marking a follow-up as completed."""
    with app.app_context():
        app_record = Application(user_id=user_a.id, company_name='Discord', job_title='Backend Developer')
        db.session.add(app_record)
        db.session.commit()
        app_id = app_record.id

    # Create follow-up
    res = auth_client_a.post('/followups/new', data={
        'application_id': app_id,
        'followup_date': date.today().strftime('%Y-%m-%d'),
        'followup_type': 'Email',
        'status': 'Pending',
        'notes': 'Thank recruiter for initial call.'
    }, follow_redirects=True)

    assert res.status_code == 200

    with app.app_context():
        fu = FollowUp.query.filter_by(application_id=app_id).first()
        assert fu is not None
        assert fu.status == 'Pending'
        fu_id = fu.id

    # Mark complete
    complete_res = auth_client_a.post(f'/followups/{fu_id}/complete', follow_redirects=True)
    assert complete_res.status_code == 200

    with app.app_context():
        assert db.session.get(FollowUp, fu_id).status == 'Completed'


def test_edit_followup(auth_client_a, app, user_a):
    """Test editing an existing follow-up."""
    with app.app_context():
        app_record = Application(user_id=user_a.id, company_name='Slack', job_title='Fullstack Engineer')
        db.session.add(app_record)
        db.session.commit()
        app_id = app_record.id

        fu = FollowUp(
            application_id=app_id,
            followup_date=date.today(),
            followup_type='Email',
            status='Pending',
            notes='Initial note'
        )
        db.session.add(fu)
        db.session.commit()
        fu_id = fu.id

    tomorrow = (date.today() + timedelta(days=1)).strftime('%Y-%m-%d')
    res = auth_client_a.post(f'/followups/{fu_id}/edit', data={
        'application_id': app_id,
        'followup_date': tomorrow,
        'followup_type': 'LinkedIn',
        'status': 'Pending',
        'notes': 'Sent message on LinkedIn.'
    }, follow_redirects=True)

    assert res.status_code == 200

    with app.app_context():
        updated_fu = db.session.get(FollowUp, fu_id)
        assert updated_fu.followup_type == 'LinkedIn'
        assert updated_fu.notes == 'Sent message on LinkedIn.'


def test_delete_followup(auth_client_a, app, user_a):
    """Test deleting a follow-up."""
    with app.app_context():
        app_record = Application(user_id=user_a.id, company_name='Spotify', job_title='Data Engineer')
        db.session.add(app_record)
        db.session.commit()
        app_id = app_record.id

        fu = FollowUp(
            application_id=app_id,
            followup_date=date.today(),
            followup_type='Phone',
            status='Pending'
        )
        db.session.add(fu)
        db.session.commit()
        fu_id = fu.id

    res = auth_client_a.post(f'/followups/{fu_id}/delete', follow_redirects=True)
    assert res.status_code == 200

    with app.app_context():
        assert db.session.get(FollowUp, fu_id) is None
