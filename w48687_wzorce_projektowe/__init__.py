"""
The flask application package.
"""

from flask import Flask, render_template, url_for, request, redirect
from flask_sqlalchemy import SQLAlchemy 
from ged4py import GedcomReader
from ged4py.model import Individual
from tabulate import tabulate
import sys
import csv
import time
import pandas as pd
from datetime import datetime



app = Flask(__name__)

import w48687_wzorce_projektowe.views

app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///database.db'
db = SQLAlchemy(app)

""" definicje klas """

class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(200), nullable=False)
    description = db.Column(db.String(200), nullable=True)
    duedate = db.Column(db.String(10), nullable=True)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return '<Task %r>' % self.id




""" views """


@app.route('/')
@app.route('/home')
def home():
    return render_template(
        'index.html',
        title='Task manager',
        year=datetime.now().year,
    )

@app.route('/worker', methods=['POST', 'GET'])
def worker():
    if request.method == 'POST':
        task_content = request.form['content']
        #new_task = Todo(content=task_content)
        task_description = request.form['description']
        task_duedate = request.form['duedate']
        new_task = Todo(content=task_content, description=task_description, duedate=task_duedate)
         

        try:
            db.session.add(new_task)
            db.session.commit()
            return redirect('/worker')
        except:
            return 'Wystapil problem przy dodawaniu zadania'

    else:
        tasks = Todo.query.order_by(Todo.date_created).all()
        return render_template('worker.html', tasks=tasks, title='Task manager',
        year=datetime.now().year,
        message='Manage your tasks easly')



@app.route('/worker/delete/<int:id>')
def delete(id):
    task_to_delete = Todo.query.get_or_404(id)

    try:
        db.session.delete(task_to_delete)
        db.session.commit()
        return redirect('/worker')
    except:
        return 'Wystapil problem przy usuwaniu zadania'

@app.route('/worker/update/<int:id>', methods=['GET', 'POST'])
def update(id):
    task = Todo.query.get_or_404(id)

    if request.method == 'POST':
        task.content = request.form['content']
        task.description = request.form['description']
        task.duedate = request.form['duedate']

        try:
            db.session.commit()
            return redirect('/worker')
        except:
            return 'Wystapil problem przy edytowaniu zadania'

    else:
        return render_template('update.html', task=task)


@app.route('/about')
def about():
    return render_template(
        'about.html',
        title='About',
        year=datetime.now().year,
        message='Informacje o projekcie'
    )




