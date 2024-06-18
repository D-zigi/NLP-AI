"""
Blueprint
for routes and views for the flask application.
"""
from flask import Blueprint, render_template, redirect, url_for, request
import markdown
import requests

main = Blueprint("main", __name__)

from .errors import errors
main.register_blueprint(errors)

@main.route('/')
def about():
    """
    opens 'about' page
    """
    return render_template('about.html')

@main.route('/chat', methods=['GET', 'POST'])
def chat(message=None):
    if request.method == 'GET':
        """
        opens 'chat' page
        """
        return render_template('chat.html')
    if request.method == 'POST':
        pass
