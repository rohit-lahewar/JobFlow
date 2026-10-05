from app.models import User


def test_user_registration(client, app):
    """Test standard user registration flow."""
    response = client.post('/register', data={
        'name': 'John Doe',
        'email': 'john@example.com',
        'password': 'SecretPassword123!',
        'confirm_password': 'SecretPassword123!'
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b'Account created successfully' in response.data

    with app.app_context():
        user = User.query.filter_by(email='john@example.com').first()
        assert user is not None
        assert user.name == 'John Doe'
        assert user.password_hash != 'SecretPassword123!'  # Never plaintext!
        assert user.check_password('SecretPassword123!') is True


def test_duplicate_email_registration_prevented(client, user_a):
    """Test that duplicate email registration is rejected."""
    response = client.post('/register', data={
        'name': 'Impostor',
        'email': user_a.email,  # duplicate
        'password': 'AnotherPassword!',
        'confirm_password': 'AnotherPassword!'
    }, follow_redirects=True)

    assert b'already registered' in response.data


def test_password_mismatch_registration(client):
    """Test registration when passwords do not match."""
    response = client.post('/register', data={
        'name': 'Jane Doe',
        'email': 'jane@example.com',
        'password': 'PasswordOne1!',
        'confirm_password': 'PasswordTwo2!'
    }, follow_redirects=True)

    assert b'Passwords must match' in response.data


def test_login_valid_credentials(client, user_a):
    """Test login with valid email and password."""
    response = client.post('/login', data={
        'email': user_a.email,
        'password': 'Password123!'
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b'Welcome back' in response.data
    assert b'Dashboard' in response.data


def test_login_invalid_credentials(client, user_a):
    """Test login with incorrect password."""
    response = client.post('/login', data={
        'email': user_a.email,
        'password': 'WrongPassword!'
    }, follow_redirects=True)

    assert b'Invalid email or password' in response.data


def test_logout(auth_client_a):
    """Test user logout."""
    response = auth_client_a.get('/logout', follow_redirects=True)
    assert response.status_code == 200
    assert b'logged out' in response.data
