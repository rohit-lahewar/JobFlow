from datetime import datetime, timezone
from app.extensions import db


class Note(db.Model):
    """Note model for capturing ongoing reflections, interview prep, or recruiter notes."""
    __tablename__ = 'notes'

    id = db.Column(db.Integer, primary_key=True)
    application_id = db.Column(db.Integer, db.ForeignKey('applications.id', ondelete='CASCADE'), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)

    content = db.Column(db.Text, nullable=False)

    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    def to_dict(self):
        """Serialize note for JSON responses."""
        return {
            'id': self.id,
            'application_id': self.application_id,
            'user_id': self.user_id,
            'author_name': self.author.name if self.author else 'User',
            'content': self.content,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

    def __repr__(self):
        return f"<Note id={self.id} app_id={self.application_id} user_id={self.user_id}>"
