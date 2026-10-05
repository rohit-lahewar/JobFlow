from flask_wtf import FlaskForm
from wtforms import (
    StringField, PasswordField, BooleanField, SubmitField,
    SelectField, TextAreaField, DateField, URLField, EmailField
)
from wtforms.validators import (
    DataRequired, Email, EqualTo, Length, Optional, URL, ValidationError
)
from datetime import date
from app.models import User, Application, Interview, FollowUp


class RegistrationForm(FlaskForm):
    """User registration form with email uniqueness check and password confirmation."""
    name = StringField('Full Name', validators=[
        DataRequired(message='Please provide your full name.'),
        Length(min=2, max=100, message='Name must be between 2 and 100 characters.')
    ])
    email = EmailField('Email Address', validators=[
        DataRequired(message='Please provide a valid email address.'),
        Email(message='Invalid email format.'),
        Length(max=120)
    ])
    password = PasswordField('Password', validators=[
        DataRequired(message='Password is required.'),
        Length(min=6, message='Password must be at least 6 characters long.')
    ])
    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(message='Please confirm your password.'),
        EqualTo('password', message='Passwords must match.')
    ])
    submit = SubmitField('Create Account')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data.lower().strip()).first()
        if user:
            raise ValidationError('This email is already registered. Please log in instead.')


class LoginForm(FlaskForm):
    """User login form with remember me option."""
    email = EmailField('Email Address', validators=[
        DataRequired(message='Please enter your email.'),
        Email(message='Invalid email format.')
    ])
    password = PasswordField('Password', validators=[
        DataRequired(message='Please enter your password.')
    ])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Log In')


class ApplicationForm(FlaskForm):
    """Form to create or edit a job application."""
    company_name = StringField('Company Name', validators=[
        DataRequired(message='Company name is required.'),
        Length(max=150)
    ])
    job_title = StringField('Job Title / Role', validators=[
        DataRequired(message='Job title is required.'),
        Length(max=150)
    ])
    location = StringField('Location', validators=[
        Optional(),
        Length(max=150)
    ])
    employment_type = SelectField(
        'Employment Type',
        choices=[(item, item) for item in Application.EMPLOYMENT_TYPES],
        default='Full Time',
        validators=[DataRequired()]
    )
    work_mode = SelectField(
        'Work Mode',
        choices=[(item, item) for item in Application.WORK_MODES],
        default='Remote',
        validators=[DataRequired()]
    )
    salary = StringField('Salary / Compensation', validators=[
        Optional(),
        Length(max=100)
    ])
    job_url = URLField('Job Listing URL', validators=[
        Optional(),
        URL(require_tld=False, message='Please enter a valid URL (e.g. https://...)'),
        Length(max=500)
    ])
    application_date = DateField('Application Date', default=date.today, validators=[
        DataRequired(message='Please provide the application date.')
    ])
    status = SelectField(
        'Status',
        choices=[(item, item) for item in Application.STATUSES],
        default='Applied',
        validators=[DataRequired()]
    )
    priority = SelectField(
        'Priority',
        choices=[(item, item) for item in Application.PRIORITIES],
        default='Medium',
        validators=[DataRequired()]
    )
    recruiter_name = StringField('Recruiter / Contact Name', validators=[
        Optional(),
        Length(max=100)
    ])
    recruiter_email = EmailField('Recruiter Email', validators=[
        Optional(),
        Email(message='Invalid email address.'),
        Length(max=120)
    ])
    job_description = TextAreaField('Job Description', validators=[Optional()])
    notes = TextAreaField('Initial Notes / Strategy', validators=[Optional()])
    submit = SubmitField('Save Application')


class InterviewForm(FlaskForm):
    """Form to schedule or update an interview round."""
    application_id = SelectField('Related Job Application', coerce=int, validators=[
        DataRequired(message='Please select a job application.')
    ])
    round_name = SelectField(
        'Interview Round',
        choices=[(item, item) for item in Interview.ROUNDS],
        default='Technical Round 1',
        validators=[DataRequired()]
    )
    interview_type = SelectField(
        'Interview Type',
        choices=[(item, item) for item in Interview.TYPES],
        default='Online',
        validators=[DataRequired()]
    )
    interview_date = DateField('Interview Date', default=date.today, validators=[
        DataRequired(message='Interview date is required.')
    ])
    start_time = StringField('Time / Timezone', validators=[
        Optional(),
        Length(max=20)
    ])
    meeting_link = URLField('Meeting Link / Location', validators=[
        Optional(),
        Length(max=500)
    ])
    interviewer = StringField('Interviewer(s) Name / Title', validators=[
        Optional(),
        Length(max=150)
    ])
    status = SelectField(
        'Status',
        choices=[(item, item) for item in Interview.STATUSES],
        default='Scheduled',
        validators=[DataRequired()]
    )
    notes = TextAreaField('Preparation / Feedback Notes', validators=[Optional()])
    submit = SubmitField('Save Interview')


class FollowUpForm(FlaskForm):
    """Form to schedule and manage application follow-ups."""
    application_id = SelectField('Related Job Application', coerce=int, validators=[
        DataRequired(message='Please select a job application.')
    ])
    followup_date = DateField('Follow-Up Date', default=date.today, validators=[
        DataRequired(message='Follow-up date is required.')
    ])
    followup_type = SelectField(
        'Channel / Method',
        choices=[(item, item) for item in FollowUp.TYPES],
        default='Email',
        validators=[DataRequired()]
    )
    status = SelectField(
        'Status',
        choices=[(item, item) for item in FollowUp.STATUSES],
        default='Pending',
        validators=[DataRequired()]
    )
    notes = TextAreaField('Follow-up Message / Notes', validators=[Optional()])
    submit = SubmitField('Save Follow-Up')


class NoteForm(FlaskForm):
    """Form for adding notes to an application."""
    content = TextAreaField('Note Content', validators=[
        DataRequired(message='Note content cannot be empty.')
    ])
    submit = SubmitField('Add Note')


class ProfileUpdateForm(FlaskForm):
    """Form to update user profile information."""
    name = StringField('Full Name', validators=[
        DataRequired(message='Please enter your name.'),
        Length(min=2, max=100)
    ])
    email = EmailField('Email Address', validators=[
        DataRequired(message='Please enter your email.'),
        Email(message='Invalid email format.')
    ])
    submit = SubmitField('Update Profile')


class ChangePasswordForm(FlaskForm):
    """Form to update user account password."""
    current_password = PasswordField('Current Password', validators=[
        DataRequired(message='Please enter your current password.')
    ])
    new_password = PasswordField('New Password', validators=[
        DataRequired(message='Please enter a new password.'),
        Length(min=6, message='New password must be at least 6 characters.')
    ])
    confirm_new_password = PasswordField('Confirm New Password', validators=[
        DataRequired(message='Please confirm your new password.'),
        EqualTo('new_password', message='New passwords must match.')
    ])
    submit = SubmitField('Change Password')
