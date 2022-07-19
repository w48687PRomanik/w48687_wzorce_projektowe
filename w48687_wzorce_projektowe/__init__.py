"""
The flask application package.
"""

from flask import Flask, render_template, url_for, request, redirect
from flask_sqlalchemy import SQLAlchemy 
from datetime import datetime
from collections.abc import Iterable, Iterator
from abc import ABCMeta, abstractmethod
import functools




app = Flask(__name__)

import w48687_wzorce_projektowe.views
import w48687_wzorce_projektowe.module

app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///database.db'
db = SQLAlchemy(app)

""" definicje klas """

class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(200), nullable=False)
    description = db.Column(db.String(200), nullable=True)
    owner = db.Column(db.String(50), nullable=True)
    duedate = db.Column(db.String(10), nullable=True)
    priority = db.Column(db.String(10), nullable=True)
    progress = db.Column(db.Integer, nullable=True)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return '<Task %r>' % self.id
     


""" Kompozyt - grupowanie taskow"""

class IComponent(metaclass=ABCMeta):
    """
    A component interface describing the common
    fields and methods of leaves and composites
    """
    reference_to_parent = None
    @staticmethod
    @abstractmethod
    def method():
        "A method each Leaf and composite container should implement"
    @staticmethod
    @abstractmethod
    def detach():
        "Called before a task is attached to a task group"

class Task(IComponent):
    "A task can be added to a task group, but not a task"
    def method(self):
        parent_id = (id(self.reference_to_parent)
        if self.reference_to_parent is not None else None)
        print(
            f"<Task>\t\tid:{id(self)}\tParent:\t{parent_id}"
        )

    def detach(self):
        "Detaching this task from its parent task group"
        if self.reference_to_parent is not None:
            self.reference_to_parent.delete(self)

class TaskGroup(IComponent):
    "A task group can contain tasks and other task groups"
    def __init__(self):
        self.components = []
    def method(self):
        parent_id = (id(self.reference_to_parent)
            if self.reference_to_parent is not None else None)
        print(
            f"<Task_group>\tid:{id(self)}\tParent:\t{parent_id}\t"
            f"Components:{len(self.components)}")
        for component in self.components:
            component.method()
    
    def attach(self, component):
        """
        Detach leaf/composite from any current parent reference and
        then set the parent reference to this composite (self)
        """
        component.detach()
        component.reference_to_parent = self
        self.components.append(component)
    def delete(self, component):
        "Removes task/task group from this task group self.components"
        self.components.remove(component)
    def detach(self):
        "Detaching this task group from its parent composite"
        if self.reference_to_parent is not None:
            self.reference_to_parent.delete(self)
            self.reference_to_parent = None

""" Kompozyt """



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
        task_owner = request.form['owner']
        task_priority = request.form['priority']
        task_progress = request.form['progress']

        new_task = Todo(content=task_content, description=task_description, duedate=task_duedate, owner = task_owner, priority=task_priority, progress = task_progress)
         

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
        task.owner = request.form['owner']
        task.priority = request.form['priority']
        task.progress = request.form['progress']

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



""" execution """


TASK_A = Task()
TASK_B = Task()
TASK_GROUP_1 = TaskGroup()
TASK_GROUP_2 = TaskGroup()
print(f"TASK_A\t\tid:{id(TASK_A)}")
print(f"TASK_B\t\tid:{id(TASK_B)}")
print(f"TASK_GROUP_1\tid:{id(TASK_GROUP_1)}")
print(f"TASK_GROUP_2\tid:{id(TASK_GROUP_2)}")
# Attach LEAF_A to COMPOSITE_1
TASK_GROUP_1.attach(TASK_A)
# Instead, attach LEAF_A to COMPOSITE_2
TASK_GROUP_2.attach(TASK_A)
# Attach COMPOSITE1 to COMPOSITE_2
TASK_GROUP_2.attach(TASK_GROUP_1)
print()
TASK_B.method() # not in any composites
TASK_GROUP_2.method() # COMPOSITE_2 contains both COMPOSITE_1 and LEAF_A


