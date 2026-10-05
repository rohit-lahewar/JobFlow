from flask import Blueprint, render_template
from flask_login import login_required, current_user
from app.services.analytics_service import AnalyticsService

analytics_bp = Blueprint('analytics', __name__)


@analytics_bp.route('/')
@login_required
def index():
    """Renders comprehensive conversion and timeline analytics using Chart.js."""
    analytics_data = AnalyticsService.get_comprehensive_analytics(current_user.id)
    return render_template('analytics/index.html', analytics=analytics_data)
