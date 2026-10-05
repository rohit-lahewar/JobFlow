import os
import pytest
from app import create_app
from app.extensions import db
from app.models import User, Application, Interview, FollowUp, Note


@pytest.fixture(scope='function')
def app():
    """Function-scoped test Flask application with fresh in-memory SQLite schema."""
    _app = create_app('testing')
    with _app.app_context():
        db.create_all()
    yield _app
    with _app.app_context():
        db.session.remove()
        db.drop_all()


@pytest.fixture(scope='function')
def client(app):
    """An unauthenticated, fresh test client for each test function."""
    return app.test_client()


@pytest.fixture
def user_a(app):
    """Creates primary test user (User A)."""
    with app.app_context():
        user = User(name='User A', email='usera@example.com')
        user.set_password('Password123!')
        db.session.add(user)
        db.session.commit()
        db.session.refresh(user)
        db.session.expunge(user)
        return user


@pytest.fixture
def user_b(app):
    """Creates secondary test user (User B) for isolation testing."""
    with app.app_context():
        user = User(name='User B', email='userb@example.com')
        user.set_password('Password123!')
        db.session.add(user)
        db.session.commit()
        db.session.refresh(user)
        db.session.expunge(user)
        return user


@pytest.fixture
def auth_client_a(app, user_a):
    """Isolated test client authenticated as User A using Flask-Login session transaction."""
    client = app.test_client()
    with client.session_transaction() as sess:
        sess['_user_id'] = str(user_a.id)
        sess['_fresh'] = True
    return client


@pytest.fixture
def auth_client_b(app, user_b):
    """Isolated test client authenticated as User B using Flask-Login session transaction."""
    client = app.test_client()
    with client.session_transaction() as sess:
        sess['_user_id'] = str(user_b.id)
        sess['_fresh'] = True
    return client
