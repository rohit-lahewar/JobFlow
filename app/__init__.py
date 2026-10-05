import os
from datetime import datetime, timezone
from flask import Flask, render_template, jsonify, request
from config import config_by_name
from app.extensions import db, migrate, login_manager, csrf


def create_app(config_name='development'):
    """Application factory for JobFlow."""
    app = Flask(
        __name__,
        template_folder=os.path.join(os.path.dirname(__file__), 'templates'),
        static_folder=os.path.join(os.path.dirname(__file__), 'static')
    )

    # Load configuration
    app.config.from_object(config_by_name.get(config_name, config_by_name['default']))

    # Initialize extensions with the application
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    csrf.init_app(app)

    # Register blueprints
    from app.routes.auth import auth_bp
    from app.routes.dashboard import dashboard_bp
    from app.routes.applications import applications_bp
    from app.routes.interviews import interviews_bp
    from app.routes.followups import followups_bp
    from app.routes.analytics import analytics_bp
    from app.routes.profile import profile_bp
    from app.routes.api import api_bp

    # Exempt api_bp from global form CSRF check so programmatic clients (e.g. Basic Auth)
    # can authenticate without CSRF tokens. Session-based clients are protected in api_auth_required.
    csrf.exempt(api_bp)

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp, url_prefix='/dashboard')
    app.register_blueprint(applications_bp, url_prefix='/applications')
    app.register_blueprint(interviews_bp, url_prefix='/interviews')
    app.register_blueprint(followups_bp, url_prefix='/followups')
    app.register_blueprint(analytics_bp, url_prefix='/analytics')
    app.register_blueprint(profile_bp, url_prefix='/profile')
    app.register_blueprint(api_bp, url_prefix='/api')

    # Register global template context processors
    @app.context_processor
    def inject_global_template_vars():
        return {
            'current_year': datetime.now(timezone.utc).year,
            'app_name': 'JobFlow'
        }

    # Custom Error Handlers
    register_error_handlers(app)

    return app


def register_error_handlers(app):
    """Registers custom error handlers returning either HTML or JSON based on request path."""

    def is_api_request():
        return request.path.startswith('/api/') or request.headers.get('Accept') == 'application/json'

    from flask_wtf.csrf import CSRFError

    @app.errorhandler(CSRFError)
    def handle_csrf_error(error):
        if is_api_request():
            return jsonify({
                'success': False,
                'error': 'CSRF Error',
                'message': str(error.description if hasattr(error, 'description') else error) or 'CSRF token is missing or invalid.'
            }), 400
        return render_template('errors/400.html', error=error), 400

    @app.errorhandler(400)
    def bad_request(error):
        if is_api_request():
            return jsonify({'success': False, 'error': 'Bad Request', 'message': str(error.description if hasattr(error, 'description') else error)}), 400
        return render_template('errors/400.html', error=error), 400

    @app.errorhandler(401)
    def unauthorized(error):
        if is_api_request():
            return jsonify({'success': False, 'error': 'Unauthorized', 'message': 'Authentication required to access this resource.'}), 401
        return render_template('errors/401.html', error=error), 401

    @app.errorhandler(403)
    def forbidden(error):
        if is_api_request():
            return jsonify({'success': False, 'error': 'Forbidden', 'message': 'You do not have permission to access this resource.'}), 403
        return render_template('errors/403.html', error=error), 403

    @app.errorhandler(404)
    def not_found(error):
        if is_api_request():
            return jsonify({'success': False, 'error': 'Not Found', 'message': 'The requested resource was not found.'}), 404
        return render_template('errors/404.html', error=error), 404

    @app.errorhandler(500)
    def internal_server_error(error):
        # Roll back any aborted database transactions
        try:
            db.session.rollback()
        except Exception:
            pass

        app.logger.error(f"Internal Server Error: {error}")
        if is_api_request():
            return jsonify({'success': False, 'error': 'Internal Server Error', 'message': 'An unexpected server error occurred.'}), 500
        return render_template('errors/500.html', error=error), 500
