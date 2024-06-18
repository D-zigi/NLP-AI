"""
Blueprint
for handling errors
"""
from flask import Blueprint, render_template

errors = Blueprint('errors', __name__)

@errors.app_errorhandler(404)
def page_not_found(error):
    """
    if page not found,
    returns 404 alternate page
    """
    return render_template(
        'error.html',
        error_code = 404,
        error_message = "Page Not Found"
    ), 404
