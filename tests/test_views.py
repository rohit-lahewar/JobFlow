"""
Tests for main user dashboard, analytics, and landing views.
"""
from app.models import Application
from app.extensions import db


def test_landing_page(client):
    """Test public landing page loads with marketing hero and CTA."""
    res = client.get('/')
    assert res.status_code == 200
    assert b'Manage Your Job Search' in res.data
    assert b'Get Started' in res.data


def test_dashboard_authenticated(auth_client_a, app, user_a):
    """Test dashboard metrics and charts rendering for authenticated user."""
    with app.app_context():
        app1 = Application(user_id=user_a.id, company_name='Figma', job_title='Frontend Lead', status='Interview')
        app2 = Application(user_id=user_a.id, company_name='Vercel', job_title='Fullstack', status='Offer')
        db.session.add_all([app1, app2])
        db.session.commit()

    res = auth_client_a.get('/dashboard/')
    assert res.status_code == 200
    assert b'Welcome back' in res.data
    assert b'Figma' in res.data
    assert b'Total Apps' in res.data


def test_analytics_authenticated(auth_client_a, app, user_a):
    """Test analytics view calculates rates and renders charts."""
    with app.app_context():
        app1 = Application(user_id=user_a.id, company_name='Datadog', job_title='Site Reliability', status='Interview')
        db.session.add(app1)
        db.session.commit()

    res = auth_client_a.get('/analytics/')
    assert res.status_code == 200
    assert b'Pipeline Analytics' in res.data
    assert b'Interview Rate' in res.data
    assert b'Offer Rate' in res.data
