from datetime import date
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.extensions import db
from app.models import FollowUp, Application
from app.forms import FollowUpForm

followups_bp = Blueprint('followups', __name__)


def get_user_application_choices():
    """Returns application choices strictly for the logged-in user."""
    apps = Application.query.filter_by(user_id=current_user.id).order_by(Application.company_name.asc()).all()
    return [(app.id, f"{app.company_name} — {app.job_title}") for app in apps]


@followups_bp.route('/')
@login_required
def index():
    """List of all follow-ups partitioned into Pending/Due, Completed, and All."""
    user_id = current_user.id
    today = date.today()

    base_query = FollowUp.query.join(Application).filter(Application.user_id == user_id)

    pending_followups = (
        base_query.filter(FollowUp.status == 'Pending')
        .order_by(FollowUp.followup_date.asc())
        .all()
    )

    completed_followups = (
        base_query.filter(FollowUp.status == 'Completed')
        .order_by(FollowUp.followup_date.desc())
        .all()
    )

    all_followups = base_query.order_by(FollowUp.followup_date.asc()).all()

    return render_template(
        'followups/index.html',
        pending=pending_followups,
        completed=completed_followups,
        all_followups=all_followups,
        today=today
    )


@followups_bp.route('/new', methods=['GET', 'POST'])
@login_required
def create():
    """Schedule a new follow-up."""
    form = FollowUpForm()
    choices = get_user_application_choices()

    if not choices:
        flash('Please create an application first before scheduling a follow-up.', 'warning')
        return redirect(url_for('applications.create'))

    form.application_id.choices = choices

    preselected_app_id = request.args.get('application_id', type=int)
    if request.method == 'GET' and preselected_app_id:
        if any(c[0] == preselected_app_id for c in choices):
            form.application_id.data = preselected_app_id

    if form.validate_on_submit():
        application = Application.query.filter_by(
            id=form.application_id.data,
            user_id=current_user.id
        ).first_or_404()

        followup = FollowUp(
            application_id=application.id,
            followup_date=form.followup_date.data,
            followup_type=form.followup_type.data,
            status=form.status.data,
            notes=form.notes.data.strip() if form.notes.data else None
        )
        db.session.add(followup)
        try:
            db.session.commit()
            flash(f"Follow-up for '{application.company_name}' scheduled for {followup.followup_date}.", 'success')
            return redirect(url_for('followups.index'))
        except Exception:
            db.session.rollback()
            flash('Error scheduling follow-up.', 'danger')

    return render_template('followups/form.html', form=form, title='Schedule Follow-Up', is_edit=False)


@followups_bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit(id):
    """Edit follow-up record."""
    followup = (
        FollowUp.query.join(Application)
        .filter(FollowUp.id == id, Application.user_id == current_user.id)
        .first_or_404()
    )

    form = FollowUpForm(obj=followup)
    form.application_id.choices = get_user_application_choices()

    if form.validate_on_submit():
        app = Application.query.filter_by(
            id=form.application_id.data,
            user_id=current_user.id
        ).first_or_404()

        followup.application_id = app.id
        followup.followup_date = form.followup_date.data
        followup.followup_type = form.followup_type.data
        followup.status = form.status.data
        followup.notes = form.notes.data.strip() if form.notes.data else None

        try:
            db.session.commit()
            flash('Follow-up updated successfully.', 'success')
            return redirect(url_for('followups.index'))
        except Exception:
            db.session.rollback()
            flash('Error updating follow-up.', 'danger')

    return render_template(
        'followups/form.html',
        form=form,
        title=f"Edit Follow-Up for {followup.application.company_name}",
        is_edit=True,
        followup=followup
    )


@followups_bp.route('/<int:id>/delete', methods=['POST'])
@login_required
def delete(id):
    """Delete a follow-up with user authorization check."""
    followup = (
        FollowUp.query.join(Application)
        .filter(FollowUp.id == id, Application.user_id == current_user.id)
        .first_or_404()
    )

    db.session.delete(followup)
    try:
        db.session.commit()
        flash('Follow-up deleted.', 'info')
    except Exception:
        db.session.rollback()
        flash('Error deleting follow-up.', 'danger')

    return redirect(request.referrer or url_for('followups.index'))


@followups_bp.route('/<int:id>/complete', methods=['POST'])
@login_required
def mark_completed(id):
    """Mark a pending follow-up as completed."""
    followup = (
        FollowUp.query.join(Application)
        .filter(FollowUp.id == id, Application.user_id == current_user.id)
        .first_or_404()
    )

    followup.status = 'Completed'
    db.session.commit()
    flash(f"Follow-up for '{followup.application.company_name}' marked as completed.", 'success')
    return redirect(request.referrer or url_for('followups.index'))
