from datetime import datetime, timezone
from app.extensions import db


class FollowUp(db.Model):
    """FollowUp model representing a scheduled communication follow-up for an application."""
    __tablename__ = 'followups'

    TYPES = ['Email', 'Phone', 'LinkedIn', 'Other']
    STATUSES = ['Pending', 'Completed', 'Cancelled']

    id = db.Column(db.Integer, primary_key=True)
    application_id = db.Column(db.Integer, db.ForeignKey('applications.id', ondelete='CASCADE'), nullable=False, index=True)

    followup_date = db.Column(db.Date, nullable=False, index=True)
    followup_type = db.Column(db.String(50), default='Email', nullable=False)
    status = db.Column(db.String(50), default='Pending', nullable=False, index=True)
    notes = db.Column(db.Text, nullable=True)

    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    def to_dict(self):
        """Serialize follow-up for API responses."""
        return {
            'id': self.id,
            'application_id': self.application_id,
            'company_name': self.application.company_name if self.application else None,
            'job_title': self.application.job_title if self.application else None,
            'followup_date': self.followup_date.isoformat() if self.followup_date else None,
            'followup_type': self.followup_type,
            'status': self.status,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

    @property
    def status_badge_class(self):
        mapping = {
            'Pending': 'badge-warning',
            'Completed': 'badge-success',
            'Cancelled': 'badge-secondary'
        }
        return mapping.get(self.status, 'badge-secondary')

    def __repr__(self):
        return f"<FollowUp id={self.id} type='{self.followup_type}' date='{self.followup_date}'>"
