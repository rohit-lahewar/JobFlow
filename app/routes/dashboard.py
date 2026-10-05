from flask import Blueprint, render_template
from flask_login import login_required, current_user
from app.services.analytics_service import AnalyticsService

dashboard_bp = Blueprint('dashboard', __name__)


@dashboard_bp.route('/')
@login_required
def index():
    """Renders the main dashboard for the authenticated user."""
    user_id = current_user.id
    metrics = AnalyticsService.get_dashboard_summary(user_id)
    status_distribution = AnalyticsService.get_status_distribution(user_id)
    monthly_timeline = AnalyticsService.get_monthly_timeline(user_id, months=6)

    return render_template(
        'dashboard/index.html',
        metrics=metrics,
        status_chart=status_distribution,
        monthly_chart=monthly_timeline
    )
