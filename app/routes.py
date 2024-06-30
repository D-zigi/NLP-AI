"""
Blueprint
for routes and views for the flask application.
"""
from flask import Blueprint, render_template, redirect, url_for, request, abort
import requests
from .errors import errors
from .geminiAPI.chat import list_model_names, DEFAULT_MODEL

main = Blueprint("main", __name__)

main.register_blueprint(errors)

@main.route('/')
def base():
    """
    opens base page for the application
    """
    return redirect(url_for('main.chat'))
    return render_template('base.html')

@main.route('/about')
def about():
    """
    opens 'about' page
    (provides the app with the about page)
    """
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return render_template('about.html')
    else:
        abort(403)

@main.route('/visualization')
def visualization():
    """
    opens 'visualization' page
    (provides the app with the visualization page)
    """
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return render_template('visualization.html')
    else:
        abort(403)


@main.route('/chatbot', methods=['GET', 'POST'])
def chat():
    """
    opens 'chatbot' page
    (provides the app with the chatbot page)
    """
    models = set(list_model_names())
    models.add(DEFAULT_MODEL)

    return render_template(
        'chatbot.html', 
        models=models,
        default_model = DEFAULT_MODEL
    )
