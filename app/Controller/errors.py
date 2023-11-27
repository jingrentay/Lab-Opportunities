from flask import Blueprint,render_template
from app.Model.models import db

bp_errors = Blueprint('errors', __name__)

# ================================================================
#   Name:           Errors
#   Description:    404 and 500 Error handlers
#   Last Changed:   10/26/21
#   Changed By:     Reagan Kelley
#   Change Details: Initial implementation of errors.py (taken from smile project)
#=================================================================

@bp_errors.errorhandler(404)
def not_found_error(error):
    return render_template('404error.html'), 404

@bp_errors.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500error.html'), 500