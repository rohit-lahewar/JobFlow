from datetime import datetime, date, timezone
from app.extensions import db


class Application(db.Model):
    """Application model representing a job application created by a user."""
    __tablename__ = 'applications'

    # Valid choices for consistency across models, forms, and API
    EMPLOYMENT_TYPES = ['Full Time', 'Internship', 'Part Time', 'Contract']
    WORK_MODES = ['Remote', 'Hybrid', 'On-site']
    STATUSES = ['Applied', 'Shortlisted', 'Interview', 'Offer', 'Rejected', 'Withdrawn']
    PRIORITIES = ['Low', 'Medium', 'High']

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)

    company_name = db.Column(db.String(150), nullable=False, index=True)
    job_title = db.Column(db.String(150), nullable=False, index=True)
    location = db.Column(db.String(150), nullable=True)

    employment_type = db.Column(db.String(50), default='Full Time', nullable=False)
    work_mode = db.Column(db.String(50), default='Remote', nullable=False)
    salary = db.Column(db.String(100), nullable=True)
    job_url = db.Column(db.String(500), nullable=True)

    application_date = db.Column(db.Date, default=date.today, nullable=False, index=True)
    status = db.Column(db.String(50), default='Applied', nullable=False, index=True)
    priority = db.Column(db.String(50), default='Medium', nullable=False, index=True)

    recruiter_name = db.Column(db.String(100), nullable=True)
    recruiter_email = db.Column(db.String(120), nullable=True)

    job_description = db.Column(db.Text, nullable=True)
    notes = db.Column(db.Text, nullable=True)

    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    # Relationships
    interviews = db.relationship(
        'Interview',
        backref='application',
        lazy=True,
        cascade='all, delete-orphan',
        order_by='Interview.interview_date.asc()'
    )
    followups = db.relationship(
        'FollowUp',
        backref='application',
        lazy=True,
        cascade='all, delete-orphan',
        order_by='FollowUp.followup_date.asc()'
    )
    notes_list = db.relationship(
        'Note',
        backref='application',
        lazy=True,
        cascade='all, delete-orphan',
        order_by='Note.created_at.desc()'
    )

    def to_dict(self):
        """Serialize model for REST API responses."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'company_name': self.company_name,
            'job_title': self.job_title,
            'location': self.location,
            'employment_type': self.employment_type,
            'work_mode': self.work_mode,
            'salary': self.salary,
            'job_url': self.job_url,
            'application_date': self.application_date.isoformat() if self.application_date else None,
            'status': self.status,
            'priority': self.priority,
            'recruiter_name': self.recruiter_name,
            'recruiter_email': self.recruiter_email,
            'job_description': self.job_description,
            'notes': self.notes,
            'interviews_count': len(self.interviews),
            'followups_count': len(self.followups),
            'notes_count': len(self.notes_list),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

    @property
    def status_badge_class(self):
        mapping = {
            'Applied': 'badge-status-applied',
            'Shortlisted': 'badge-status-shortlisted',
            'Interview': 'badge-status-interview',
            'Offer': 'badge-status-offer',
            'Rejected': 'badge-status-rejected',
            'Withdrawn': 'badge-status-withdrawn'
        }
        return mapping.get(self.status, 'badge-secondary')

    @property
    def priority_badge_class(self):
        mapping = {
            'Low': 'badge-priority-low',
            'Medium': 'badge-priority-medium',
            'High': 'badge-priority-high'
        }
        return mapping.get(self.priority, 'badge-secondary')

    def __repr__(self):
        return f"<Application id={self.id} company='{self.company_name}' role='{self.job_title}' status='{self.status}'>"
