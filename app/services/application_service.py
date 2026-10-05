from datetime import datetime
from sqlalchemy import or_, desc, asc, case
from app.models import Application


class ApplicationService:
    """Service to handle application search, dynamic multi-field filtering, sorting, and pagination."""

    @staticmethod
    def get_filtered_applications(user_id, filters, page=1, per_page=10):
        """
        Executes real database query with user isolation, multi-field search,
        status/priority/type/work-mode filters, date range, and sorting.
        """
        query = Application.query.filter(Application.user_id == user_id)

        # 1. Search Query (Company, Job Title, Location)
        search = filters.get('search', '').strip()
        if search:
            search_pattern = f"%{search}%"
            query = query.filter(
                or_(
                    Application.company_name.ilike(search_pattern),
                    Application.job_title.ilike(search_pattern),
                    Application.location.ilike(search_pattern)
                )
            )

        # 2. Status Filter
        status = filters.get('status', '').strip()
        if status and status in Application.STATUSES:
            query = query.filter(Application.status == status)

        # 3. Priority Filter
        priority = filters.get('priority', '').strip()
        if priority and priority in Application.PRIORITIES:
            query = query.filter(Application.priority == priority)

        # 4. Employment Type Filter
        emp_type = filters.get('employment_type', '').strip()
        if emp_type and emp_type in Application.EMPLOYMENT_TYPES:
            query = query.filter(Application.employment_type == emp_type)

        # 5. Work Mode Filter
        work_mode = filters.get('work_mode', '').strip()
        if work_mode and work_mode in Application.WORK_MODES:
            query = query.filter(Application.work_mode == work_mode)

        # 6. Date Range Filters (start_date, end_date)
        start_date_str = filters.get('start_date', '').strip()
        if start_date_str:
            try:
                start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
                query = query.filter(Application.application_date >= start_date)
            except ValueError:
                pass

        end_date_str = filters.get('end_date', '').strip()
        if end_date_str:
            try:
                end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
                query = query.filter(Application.application_date <= end_date)
            except ValueError:
                pass

        # 7. Sorting
        sort_by = filters.get('sort', 'newest').strip()
        if sort_by == 'oldest':
            query = query.order_by(asc(Application.application_date), asc(Application.id))
        elif sort_by == 'company_asc':
            query = query.order_by(asc(Application.company_name))
        elif sort_by == 'company_desc':
            query = query.order_by(desc(Application.company_name))
        elif sort_by == 'priority':
            # Priority order: High (3), Medium (2), Low (1)
            priority_order = case(
                (Application.priority == 'High', 3),
                (Application.priority == 'Medium', 2),
                (Application.priority == 'Low', 1),
                else_=0
            )
            query = query.order_by(desc(priority_order), desc(Application.application_date))
        else:  # 'newest' default
            query = query.order_by(desc(Application.application_date), desc(Application.id))

        # Paginate results
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        return pagination
