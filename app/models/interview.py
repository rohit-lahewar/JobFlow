from datetime import datetime, timezone
from app.extensions import db


class Interview(db.Model):
    """Interview model representing an interview round for a specific application."""
    __tablename__ = 'interviews'

    ROUNDS = [
        'Online Assessment',
        'Technical Round 1',
        'Technical Round 2',
        'Managerial Round',
        'HR Round',
        'Final Round'
    ]

    TYPES = ['Online', 'Phone', 'In Person']

    STATUSES = ['Scheduled', 'Completed', 'Cancelled', 'Rescheduled', 'Passed', 'Failed']

    id = db.Column(db.Integer, primary_key=True)
    application_id = db.Column(db.Integer, db.ForeignKey('applications.id', ondelete='CASCADE'), nullable=False, index=True)

    interview_date = db.Column(db.Date, nullable=False, index=True)
    start_time = db.Column(db.String(20), nullable=True)  # e.g., "14:30" or "02:30 PM"
    round_name = db.Column(db.String(100), default='Technical Round 1', nullable=False)
    interview_type = db.Column(db.String(50), default='Online', nullable=False)

    meeting_link = db.Column(db.String(500), nullable=True)
    interviewer = db.Column(db.String(150), nullable=True)
    status = db.Column(db.String(50), default='Scheduled', nullable=False, index=True)
    notes = db.Column(db.Text, nullable=True)

    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    def to_dict(self):
        """Serialize interview for REST API responses."""
        return {
            'id': self.id,
            'application_id': self.application_id,
            'company_name': self.application.company_name if self.application else None,
            'job_title': self.application.job_title if self.application else None,
            'interview_date': self.interview_date.isoformat() if self.interview_date else None,
            'start_time': self.start_time,
            'round_name': self.round_name,
            'interview_type': self.interview_type,
            'meeting_link': self.meeting_link,
            'interviewer': self.interviewer,
            'status': self.status,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

    @property
    def status_badge_class(self):
        mapping = {
            'Scheduled': 'badge-interview-scheduled',
            'Completed': 'badge-interview-completed',
            'Cancelled': 'badge-interview-cancelled',
            'Rescheduled': 'badge-interview-rescheduled',
            'Passed': 'badge-interview-passed',
            'Failed': 'badge-interview-failed'
        }
        return mapping.get(self.status, 'badge-secondary')

    def __repr__(self):
        return f"<Interview id={self.id} round='{self.round_name}' date='{self.interview_date}'>"
