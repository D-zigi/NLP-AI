"""
Blueprint
for routes and views for the flask application.
"""
import requests
from flask import Blueprint, make_response, render_template, redirect, url_for, request, abort
from .errors import errors
from .gemini_api.chat import list_model_names, DEFAULT_MODEL

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

@main.route('/credits')
def credits_page():
    """
    opens 'credits' page
    (provides the app with the credits page)
    """
    return render_template('credits.html')

@main.route('/webuilder', methods=['GET', 'POST'])
def webuilder():
    """
    opens 'webuilder' page
    (provides the app with the webuilder page)
    """
    if request.method == 'GET':
        return render_template('webuilder.html')

    elif request.method == 'POST':
        return render_template('webuilder.html')
        # url = request.form['url']
        # response = requests.get(url)
        # soup = BeautifulSoup(response.content, 'html.parser')
        # title = soup.title.string
        # return render_template('webuilder.html', title=title, url=url)

@main.route('/chatbot', methods=['GET', 'POST'])
def chat():
    """
    opens 'chatbot' page
    (provides the app with the chatbot page)
    """
    models = set(list_model_names())
    models.add(DEFAULT_MODEL)

    response = make_response(
        render_template(
            'chatbot.html', 
            models=models,
            default_model = DEFAULT_MODEL
        )
    )
    response.headers['Cache-Control'] = 'public, max-age=3600'
    response.headers['Vary'] = 'User-Agent'

    return response
