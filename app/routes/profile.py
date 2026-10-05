from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.extensions import db
from app.models import User
from app.forms import ProfileUpdateForm, ChangePasswordForm

profile_bp = Blueprint('profile', __name__)


@profile_bp.route('/', methods=['GET', 'POST'])
@login_required
def index():
    """User profile management and password change."""
    profile_form = ProfileUpdateForm(name=current_user.name, email=current_user.email)
    password_form = ChangePasswordForm()

    # Determine which form was submitted based on the submit button name
    if 'submit_profile' in request.form and profile_form.validate_on_submit():
        new_email = profile_form.email.data.lower().strip()
        # Check if email is already taken by another user
        existing_user = User.query.filter(User.email == new_email, User.id != current_user.id).first()
        if existing_user:
            flash('This email address is already in use by another account.', 'danger')
        else:
            current_user.name = profile_form.name.data.strip()
            current_user.email = new_email
            db.session.commit()
            flash('Profile details updated successfully.', 'success')
            return redirect(url_for('profile.index'))

    if 'submit_password' in request.form and password_form.validate_on_submit():
        if not current_user.check_password(password_form.current_password.data):
            flash('Current password entered is incorrect.', 'danger')
        else:
            current_user.set_password(password_form.new_password.data)
            db.session.commit()
            flash('Your password has been updated securely.', 'success')
            return redirect(url_for('profile.index'))

    return render_template(
        'profile/index.html',
        profile_form=profile_form,
        password_form=password_form
    )
