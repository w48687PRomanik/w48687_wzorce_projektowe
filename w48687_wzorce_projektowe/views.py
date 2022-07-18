"""
Routes and views for the flask application.
"""

from datetime import datetime
from flask import render_template
from w48687_wzorce_projektowe import app

@app.route('/')
@app.route('/home')
def home():
    """Renders the home page."""
    return render_template(
        'index.html',
        title='Home Page',
        year=datetime.now().year,
    )

@app.route('/worker')
def worker():
    """Renders the contact page."""
    return render_template(
        'worker.html',
        title='Application',
        year=datetime.now().year,
        message='Manipulate GEDcom files'
    )

@app.route('/about')
def about():
    """Renders the about page."""
    return render_template(
        'about.html',
        title='About',
        year=datetime.now().year,
        message='Your application description page.'
    )


