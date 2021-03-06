"""Routes for application pages."""

from flask import Blueprint, render_template, redirect, url_for
from flask_login import current_user, login_required, logout_user

# Blueprint Configuration
main_bp = Blueprint(
    'main_bp', __name__
)

@main_bp.route('/', methods=['GET'])
@login_required
def home():
    """Logged-in User Dashboard."""
    return render_template(
        'home.html.j2',
        current_user=current_user
    )

@main_bp.route("/logout")
@login_required
def logout():
    """User log-out logic."""
    logout_user()
    return redirect(url_for('auth_bp.login'))
