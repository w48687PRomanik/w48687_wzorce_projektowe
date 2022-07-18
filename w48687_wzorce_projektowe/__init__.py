"""
The flask application package.
"""

from flask import Flask
from w48687_wzorce_projektowe import module
from flask_sqlalchemy import SQLAlchemy # baza SQL Lite



app = Flask(__name__)

import w48687_wzorce_projektowe.views

app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///gedcom.db'
db = SQLAlchemy(app)
