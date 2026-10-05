from datetime import datetime, timezone
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app.extensions import db, login_manager


class User(UserMixin, db.Model):
    """User model representing a JobFlow registered user."""
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    # Relationships
    applications = db.relationship('Application', backref='user', lazy=True, cascade='all, delete-orphan')
    user_notes = db.relationship('Note', backref='author', lazy=True, cascade='all, delete-orphan')

    def set_password(self, password):
        """Hashes the user password using werkzeug security."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Verifies the hashed password."""
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        """Returns user representation without sensitive fields."""
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

    def __repr__(self):
        return f"<User id={self.id} email='{self.email}'>"


@login_manager.user_loader
def load_user(user_id):
    """Flask-Login callback to reload the user object from the user ID stored in the session."""
    return db.session.get(User, int(user_id))
