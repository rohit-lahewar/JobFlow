from datetime import date, datetime, timedelta
from collections import defaultdict
from app.extensions import db
from app.models import Application, Interview, FollowUp


class AnalyticsService:
    """Service to handle dashboard metrics, status distributions, and conversion analytics."""

    @staticmethod
    def get_dashboard_summary(user_id):
        """Calculates core KPI metrics for a user's dashboard."""
        user_apps = Application.query.filter_by(user_id=user_id)

        total_apps = user_apps.count()
        shortlisted_count = user_apps.filter_by(status='Shortlisted').count()
        interview_status_count = user_apps.filter_by(status='Interview').count()
        offer_count = user_apps.filter_by(status='Offer').count()
        rejected_count = user_apps.filter_by(status='Rejected').count()
        withdrawn_count = user_apps.filter_by(status='Withdrawn').count()

        # Active applications are those still ongoing
        active_apps = user_apps.filter(
            Application.status.in_(['Applied', 'Shortlisted', 'Interview'])
        ).count()

        # Total individual interview rounds conducted/scheduled
        total_interviews = (
            Interview.query.join(Application)
            .filter(Application.user_id == user_id)
            .count()
        )

        today = date.today()

        # Upcoming interviews (scheduled on or after today)
        upcoming_interviews = (
            Interview.query.join(Application)
            .filter(
                Application.user_id == user_id,
                Interview.interview_date >= today,
                Interview.status.in_(['Scheduled', 'Rescheduled'])
            )
            .order_by(Interview.interview_date.asc(), Interview.start_time.asc())
            .limit(5)
            .all()
        )

        # Follow-ups due (pending, date within next 7 days or overdue)
        due_followups = (
            FollowUp.query.join(Application)
            .filter(
                Application.user_id == user_id,
                FollowUp.status == 'Pending'
            )
            .order_by(FollowUp.followup_date.asc())
            .limit(5)
            .all()
        )

        # Recent applications
        recent_applications = (
            Application.query.filter_by(user_id=user_id)
            .order_by(Application.created_at.desc())
            .limit(5)
            .all()
        )

        return {
            'total_applications': total_apps,
            'active_applications': active_apps,
            'shortlisted': shortlisted_count,
            'interviews': interview_status_count,
            'total_interviews': total_interviews,
            'offers': offer_count,
            'rejected': rejected_count,
            'withdrawn': withdrawn_count,
            'upcoming_interviews': upcoming_interviews,
            'due_followups': due_followups,
            'recent_applications': recent_applications
        }

    @staticmethod
    def get_status_distribution(user_id):
        """Returns distribution of application statuses."""
        apps = Application.query.filter_by(user_id=user_id).all()
        counts = {status: 0 for status in Application.STATUSES}
        for app in apps:
            if app.status in counts:
                counts[app.status] += 1
            else:
                counts[app.status] = 1

        return {
            'labels': list(counts.keys()),
            'data': list(counts.values())
        }

    @staticmethod
    def get_monthly_timeline(user_id, months=6):
        """Returns monthly application counts for the past N months."""
        today = date.today()
        # Generate list of past N months in chronological order
        month_keys = []
        month_labels = []

        # Find starting month
        current_year = today.year
        current_month = today.month

        for i in range(months - 1, -1, -1):
            m = current_month - i
            y = current_year
            while m <= 0:
                m += 12
                y -= 1
            month_keys.append((y, m))
            dt = date(y, m, 1)
            month_labels.append(dt.strftime('%b %Y'))

        apps = Application.query.filter_by(user_id=user_id).all()
        counts = defaultdict(int)
        for app in apps:
            if app.application_date:
                key = (app.application_date.year, app.application_date.month)
                counts[key] += 1

        data = [counts.get(k, 0) for k in month_keys]

        return {
            'labels': month_labels,
            'data': data
        }

    @staticmethod
    def get_comprehensive_analytics(user_id):
        """Generates all analytics data including conversion rates, comparisons, and charts."""
        apps = Application.query.filter_by(user_id=user_id).all()
        total_apps = len(apps)

        interviews = (
            Interview.query.join(Application)
            .filter(Application.user_id == user_id)
            .all()
        )
        total_interviews = len(interviews)

        offers = sum(1 for a in apps if a.status == 'Offer')
        rejections = sum(1 for a in apps if a.status == 'Rejected')
        shortlisted = sum(1 for a in apps if a.status == 'Shortlisted')

        # Conversion Rates
        # Applications that reached interview stage
        apps_with_interviews = len(set(i.application_id for i in interviews)) or sum(1 for a in apps if a.status in ['Interview', 'Offer'])
        interview_rate = round((apps_with_interviews / total_apps * 100), 1) if total_apps > 0 else 0.0
        offer_rate = round((offers / total_apps * 100), 1) if total_apps > 0 else 0.0
        rejection_rate = round((rejections / total_apps * 100), 1) if total_apps > 0 else 0.0

        # Status distribution
        status_dist = AnalyticsService.get_status_distribution(user_id)

        # Monthly application timeline
        monthly_apps = AnalyticsService.get_monthly_timeline(user_id, months=6)

        # Monthly interview counts
        today = date.today()
        month_keys = []
        month_labels = []
        current_year = today.year
        current_month = today.month

        for i in range(5, -1, -1):
            m = current_month - i
            y = current_year
            while m <= 0:
                m += 12
                y -= 1
            month_keys.append((y, m))
            month_labels.append(date(y, m, 1).strftime('%b %Y'))

        interview_counts = defaultdict(int)
        for iv in interviews:
            if iv.interview_date:
                key = (iv.interview_date.year, iv.interview_date.month)
                interview_counts[key] += 1
        monthly_interviews_data = [interview_counts.get(k, 0) for k in month_keys]

        # Work Mode Distribution
        work_modes = {mode: 0 for mode in Application.WORK_MODES}
        for a in apps:
            if a.work_mode in work_modes:
                work_modes[a.work_mode] += 1

        # Priority Distribution
        priorities = {p: 0 for p in Application.PRIORITIES}
        for a in apps:
            if a.priority in priorities:
                priorities[a.priority] += 1

        return {
            'total_applications': total_apps,
            'total_interviews': total_interviews,
            'apps_with_interviews': apps_with_interviews,
            'offers': offers,
            'rejections': rejections,
            'shortlisted': shortlisted,
            'interview_rate': interview_rate,
            'offer_rate': offer_rate,
            'rejection_rate': rejection_rate,
            'status_distribution': status_dist,
            'monthly_applications': monthly_apps,
            'monthly_interviews': {
                'labels': month_labels,
                'data': monthly_interviews_data
            },
            'work_mode_distribution': {
                'labels': list(work_modes.keys()),
                'data': list(work_modes.values())
            },
            'priority_distribution': {
                'labels': list(priorities.keys()),
                'data': list(priorities.values())
            }
        }
