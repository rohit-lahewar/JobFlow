from datetime import date
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.extensions import db
from app.models import Interview, Application
from app.forms import InterviewForm

interviews_bp = Blueprint('interviews', __name__)


def get_user_application_choices():
    """Returns application tuple choices (id, label) strictly belonging to the current user."""
    apps = Application.query.filter_by(user_id=current_user.id).order_by(Application.company_name.asc()).all()
    return [(app.id, f"{app.company_name} — {app.job_title}") for app in apps]


@interviews_bp.route('/')
@login_required
def index():
    """Interviews overview page categorized into Upcoming, Completed, and Cancelled/Other."""
    user_id = current_user.id
    today = date.today()

    # Query all user interviews through application join
    base_query = Interview.query.join(Application).filter(Application.user_id == user_id)

    upcoming_interviews = (
        base_query.filter(
            Interview.status.in_(['Scheduled', 'Rescheduled']),
            Interview.interview_date >= today
        )
        .order_by(Interview.interview_date.asc(), Interview.start_time.asc())
        .all()
    )

    completed_interviews = (
        base_query.filter(Interview.status.in_(['Completed', 'Passed', 'Failed']))
        .order_by(Interview.interview_date.desc())
        .all()
    )

    cancelled_interviews = (
        base_query.filter(Interview.status == 'Cancelled')
        .order_by(Interview.interview_date.desc())
        .all()
    )

    all_interviews = base_query.order_by(Interview.interview_date.desc()).all()

    return render_template(
        'interviews/index.html',
        upcoming=upcoming_interviews,
        completed=completed_interviews,
        cancelled=cancelled_interviews,
        all_interviews=all_interviews,
        statuses=Interview.STATUSES
    )


@interviews_bp.route('/new', methods=['GET', 'POST'])
@login_required
def create():
    """Schedule a new interview round."""
    form = InterviewForm()
    choices = get_user_application_choices()

    if not choices:
        flash('You must create a job application first before scheduling an interview.', 'warning')
        return redirect(url_for('applications.create'))

    form.application_id.choices = choices

    # Pre-select application if passed via query param (e.g., from Application Detail page)
    preselected_app_id = request.args.get('application_id', type=int)
    if request.method == 'GET' and preselected_app_id:
        if any(c[0] == preselected_app_id for c in choices):
            form.application_id.data = preselected_app_id

    if form.validate_on_submit():
        # Verify the application belongs to the current user
        application = Application.query.filter_by(
            id=form.application_id.data,
            user_id=current_user.id
        ).first_or_404()

        interview = Interview(
            application_id=application.id,
            interview_date=form.interview_date.data,
            start_time=form.start_time.data.strip() if form.start_time.data else None,
            round_name=form.round_name.data,
            interview_type=form.interview_type.data,
            meeting_link=form.meeting_link.data.strip() if form.meeting_link.data else None,
            interviewer=form.interviewer.data.strip() if form.interviewer.data else None,
            status=form.status.data,
            notes=form.notes.data.strip() if form.notes.data else None
        )
        db.session.add(interview)

        # Automatically update the application status to 'Interview' if it's currently 'Applied' or 'Shortlisted'
        if application.status in ['Applied', 'Shortlisted']:
            application.status = 'Interview'

        try:
            db.session.commit()
            flash(f"Interview for '{application.company_name}' scheduled successfully.", 'success')
            return redirect(url_for('interviews.index'))
        except Exception:
            db.session.rollback()
            flash('Error scheduling interview.', 'danger')

    return render_template('interviews/form.html', form=form, title='Schedule Interview', is_edit=False)


@interviews_bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit(id):
    """Edit interview round details."""
    interview = (
        Interview.query.join(Application)
        .filter(Interview.id == id, Application.user_id == current_user.id)
        .first_or_404()
    )

    form = InterviewForm(obj=interview)
    form.application_id.choices = get_user_application_choices()

    if form.validate_on_submit():
        # Verify selected application also belongs to user
        app = Application.query.filter_by(
            id=form.application_id.data,
            user_id=current_user.id
        ).first_or_404()

        interview.application_id = app.id
        interview.interview_date = form.interview_date.data
        interview.start_time = form.start_time.data.strip() if form.start_time.data else None
        interview.round_name = form.round_name.data
        interview.interview_type = form.interview_type.data
        interview.meeting_link = form.meeting_link.data.strip() if form.meeting_link.data else None
        interview.interviewer = form.interviewer.data.strip() if form.interviewer.data else None
        interview.status = form.status.data
        interview.notes = form.notes.data.strip() if form.notes.data else None

        try:
            db.session.commit()
            flash('Interview details updated successfully.', 'success')
            return redirect(url_for('interviews.index'))
        except Exception:
            db.session.rollback()
            flash('Error updating interview.', 'danger')

    return render_template(
        'interviews/form.html',
        form=form,
        title=f"Edit Interview: {interview.round_name}",
        is_edit=True,
        interview=interview
    )


@interviews_bp.route('/<int:id>/delete', methods=['POST'])
@login_required
def delete(id):
    """Delete an interview with strict ownership authorization."""
    interview = (
        Interview.query.join(Application)
        .filter(Interview.id == id, Application.user_id == current_user.id)
        .first_or_404()
    )

    db.session.delete(interview)
    try:
        db.session.commit()
        flash('Interview deleted successfully.', 'info')
    except Exception:
        db.session.rollback()
        flash('Error deleting interview.', 'danger')

    return redirect(request.referrer or url_for('interviews.index'))


@interviews_bp.route('/<int:id>/status', methods=['POST'])
@login_required
def update_status(id):
    """Quick update of interview status."""
    interview = (
        Interview.query.join(Application)
        .filter(Interview.id == id, Application.user_id == current_user.id)
        .first_or_404()
    )

    new_status = request.form.get('status', '').strip()
    if new_status in Interview.STATUSES:
        interview.status = new_status
        db.session.commit()
        flash(f"Interview marked as {new_status}.", 'success')
    else:
        flash('Invalid status value.', 'warning')

    return redirect(request.referrer or url_for('interviews.index'))
