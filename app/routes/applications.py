from flask import Blueprint, render_template, redirect, url_for, flash, request, abort, jsonify
from flask_login import login_required, current_user
from app.extensions import db
from app.models import Application, Note, Interview, FollowUp
from app.forms import ApplicationForm, NoteForm
from app.services.application_service import ApplicationService

applications_bp = Blueprint('applications', __name__)


@applications_bp.route('/')
@login_required
def index():
    """List applications with search, multi-field filtering, sorting, and pagination."""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)

    filters = {
        'search': request.args.get('search', ''),
        'status': request.args.get('status', ''),
        'priority': request.args.get('priority', ''),
        'employment_type': request.args.get('employment_type', ''),
        'work_mode': request.args.get('work_mode', ''),
        'start_date': request.args.get('start_date', ''),
        'end_date': request.args.get('end_date', ''),
        'sort': request.args.get('sort', 'newest')
    }

    pagination = ApplicationService.get_filtered_applications(
        user_id=current_user.id,
        filters=filters,
        page=page,
        per_page=per_page
    )

    return render_template(
        'applications/index.html',
        pagination=pagination,
        applications=pagination.items,
        filters=filters,
        statuses=Application.STATUSES,
        priorities=Application.PRIORITIES,
        employment_types=Application.EMPLOYMENT_TYPES,
        work_modes=Application.WORK_MODES
    )


@applications_bp.route('/new', methods=['GET', 'POST'])
@login_required
def create():
    """Create a new job application."""
    form = ApplicationForm()
    if form.validate_on_submit():
        application = Application(
            user_id=current_user.id,
            company_name=form.company_name.data.strip(),
            job_title=form.job_title.data.strip(),
            location=form.location.data.strip() if form.location.data else None,
            employment_type=form.employment_type.data,
            work_mode=form.work_mode.data,
            salary=form.salary.data.strip() if form.salary.data else None,
            job_url=form.job_url.data.strip() if form.job_url.data else None,
            application_date=form.application_date.data,
            status=form.status.data,
            priority=form.priority.data,
            recruiter_name=form.recruiter_name.data.strip() if form.recruiter_name.data else None,
            recruiter_email=form.recruiter_email.data.strip() if form.recruiter_email.data else None,
            job_description=form.job_description.data.strip() if form.job_description.data else None,
            notes=form.notes.data.strip() if form.notes.data else None
        )
        db.session.add(application)
        try:
            db.session.commit()
            flash(f"Application for '{application.job_title}' at '{application.company_name}' created successfully!", 'success')
            return redirect(url_for('applications.detail', id=application.id))
        except Exception as e:
            db.session.rollback()
            flash('Error saving application. Please try again.', 'danger')

    return render_template('applications/form.html', form=form, title='Add New Application', is_edit=False)


@applications_bp.route('/<int:id>')
@login_required
def detail(id):
    """View detailed information about a single application, including its timeline, interviews, followups, and notes."""
    # Strict authorization check: Only the owning user can view this application
    application = Application.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    note_form = NoteForm()

    return render_template(
        'applications/detail.html',
        application=application,
        note_form=note_form,
        timeline_stages=['Applied', 'Shortlisted', 'Interview', 'Offer', 'Rejected']
    )


@applications_bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit(id):
    """Edit an existing job application."""
    # Strict authorization check
    application = Application.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    form = ApplicationForm(obj=application)

    if form.validate_on_submit():
        application.company_name = form.company_name.data.strip()
        application.job_title = form.job_title.data.strip()
        application.location = form.location.data.strip() if form.location.data else None
        application.employment_type = form.employment_type.data
        application.work_mode = form.work_mode.data
        application.salary = form.salary.data.strip() if form.salary.data else None
        application.job_url = form.job_url.data.strip() if form.job_url.data else None
        application.application_date = form.application_date.data
        application.status = form.status.data
        application.priority = form.priority.data
        application.recruiter_name = form.recruiter_name.data.strip() if form.recruiter_name.data else None
        application.recruiter_email = form.recruiter_email.data.strip() if form.recruiter_email.data else None
        application.job_description = form.job_description.data.strip() if form.job_description.data else None
        application.notes = form.notes.data.strip() if form.notes.data else None

        try:
            db.session.commit()
            flash(f"Application for '{application.company_name}' updated successfully.", 'success')
            return redirect(url_for('applications.detail', id=application.id))
        except Exception:
            db.session.rollback()
            flash('Error updating application. Please check input values.', 'danger')

    return render_template(
        'applications/form.html',
        form=form,
        title=f"Edit Application: {application.company_name}",
        is_edit=True,
        application=application
    )


@applications_bp.route('/<int:id>/delete', methods=['POST'])
@login_required
def delete(id):
    """Delete an application and all its cascading records (interviews, followups, notes)."""
    application = Application.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    company = application.company_name

    db.session.delete(application)
    try:
        db.session.commit()
        flash(f"Application for '{company}' has been deleted.", 'info')
    except Exception:
        db.session.rollback()
        flash('Failed to delete application.', 'danger')

    return redirect(url_for('applications.index'))


@applications_bp.route('/<int:id>/status', methods=['POST'])
@login_required
def update_status(id):
    """Quick update of application status directly from listing or detail."""
    application = Application.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    new_status = request.form.get('status', '').strip()

    if new_status in Application.STATUSES:
        application.status = new_status
        db.session.commit()
        flash(f"Status for '{application.company_name}' changed to {new_status}.", 'success')
    else:
        flash('Invalid status provided.', 'warning')

    return redirect(request.referrer or url_for('applications.detail', id=id))


@applications_bp.route('/<int:id>/notes', methods=['POST'])
@login_required
def add_note(id):
    """Add a new note to an application."""
    application = Application.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    form = NoteForm()

    if form.validate_on_submit():
        note = Note(
            application_id=application.id,
            user_id=current_user.id,
            content=form.content.data.strip()
        )
        db.session.add(note)
        db.session.commit()
        flash('Note added successfully.', 'success')
    else:
        flash('Note content cannot be empty.', 'warning')

    return redirect(url_for('applications.detail', id=id))


@applications_bp.route('/<int:app_id>/notes/<int:note_id>/delete', methods=['POST'])
@login_required
def delete_note(app_id, note_id):
    """Delete a note with user authorization check."""
    application = Application.query.filter_by(id=app_id, user_id=current_user.id).first_or_404()
    note = Note.query.filter_by(id=note_id, application_id=application.id, user_id=current_user.id).first_or_404()

    db.session.delete(note)
    db.session.commit()
    flash('Note deleted.', 'info')
    return redirect(url_for('applications.detail', id=app_id))
