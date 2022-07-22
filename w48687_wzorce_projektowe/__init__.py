"""
The flask application package.
"""

from flask import Flask, render_template, url_for, request, redirect
from flask_mysqldb import MySQL
from flask_sqlalchemy import SQLAlchemy 
from datetime import datetime
from collections.abc import Iterable, Iterator
from abc import ABC, ABCMeta, abstractmethod
import functools
import copy
import csv
import pandas as pd
from dataclasses import dataclass
from tabulate import tabulate




app = Flask(__name__)


""" CONFIG """

global undo
undo = False

# temporary config for SQLAlchemy
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///database.db'
db = SQLAlchemy(app)

# MySQL config to be replaced

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'flask'
 
mysql = MySQL(app)


""" CONFIG END """


""" klasa todo """

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



"""" Command """

class Command(ABC):
    """
    The Command interface declares a method for executing a command.
    """
    @abstractmethod
    def execute(self) -> None:
        pass
    def undo(self) -> None:
        pass


class EditTaskCommand(Command):
    def __init__(self, old_task, new_task):
        #self._from = from_name.content
        #self._to = to_name.content
        self.o_id = old_task.id
        # old task
        self.o_content = old_task.content
        
        self.o_description = old_task.description
        self.o_owner = old_task.owner
        self.o_duedate = old_task.duedate
        self.o_priority = old_task.priority
        self.o_progress = old_task.progress
        self.o_date_created = old_task
        # new task
        self.n_id = new_task.id        
        self.n_content = new_task.content       
        self.n_description = new_task.description
        self.n_owner = new_task.owner
        self.n_duedate = new_task.duedate
        self.n_priority = new_task.priority
        self.n_progress = new_task.progress
        self.n_date_created = new_task.date_created
        

    def execute(self):
        undo = True
        print(f"File renamed from '{self.o_content}' to '{self.n_content}' and undo = {undo}")
     


    def undo(self):
        print(f"Undo: File renamed from '{self.n_content}' to '{self.o_content}' and old ID: {self.o_id}")
        task_to_edit = Todo.query.get_or_404(self.o_id)
        task_to_edit.content = self.o_content
        task_to_edit.description = self.o_description
        task_to_edit.duedate = self.o_duedate
        task_to_edit.owner = self.o_owner
        task_to_edit.priority = self.o_priority
        task_to_edit.progress = self.o_progress
        try:
            #db.session.delete(task_to_delete)
            db.session.commit()
            #print(f"usunieto task {task_to_delete}")
            return redirect('/worker')
        except:
            return 'Wystapil problem przy usuwaniu zadania'
        undo = False

class DeleteTaskCommand(Command):
    def __init__(self, from_name, to_name):
        self._from = from_name.content
        self._to = to_name.content

    def execute(self):
        print(f"File renamed from '{self._from}' to '{self._to}'")


    def undo(self):
        print(f"Undo: File renamed from '{self._to}' to '{self._from}'")



class History(object):
    def __init__(self):
        self._commands = list()

    def execute(self, command):
        self._commands.append(command)
        command.execute()

    def undo(self):
        self._commands.pop().undo()




""" Command """


""" Sinlgeton """

class Singleton:

    def __init__(self, cls):
        self._cls = cls

    def Instance(self):
        try:
            return self._instance
        except AttributeError:
            self._instance = self._cls()
            return self._instance

    def __call__(self):
        raise TypeError('Singletons must be accessed through `Instance()`.')

    def __instancecheck__(self, inst):
        return isinstance(inst, self._cls)


@Singleton
class DBConnection(object):

    def __init__(self):
        """Initialize your database connection here."""
        # Creating a connection cursor
        # cursor = mysql.connection._instance()
 
        #Executing SQL Statements
        # cursor.execute(''' CREATE TABLE table_name(field1, field2...) ''')
        # cursor.execute(''' INSERT INTO table_name VALUES(v1,v2...) ''')
        # cursor.execute(''' DELETE FROM table_name WHERE condition ''')
 
        #Saving the Actions performed on the DB
        # mysql.connection.commit()
 
        #Closing the cursor
        # cursor.close()


        pass

    def __str__(self):
        return 'Database connection object'

""" Singleton """

""" Builder 


class ReadCSV(metaclass=ABCMeta):
    "CSV reader interface"

    @staticmethod
    @abstractmethod
    def get_filename():
        "Get filename"
    @staticmethod
    @abstractmethod
    def get_delimiter():
        "Get delimiter"
    @staticmethod
    @abstractmethod
    def get_encoding():
        "Get encoding"

    @staticmethod
    @abstractmethod
    def get_result():
        "Return the parameters"

class ReadTasksCSV(ReadCSV):
    "CSV reader for tasks."
    def __init__(self):
        self.product = ReadParameters()
    def get_filename(self):
        self.product.parameters.append('dict.csv')
        return self
    def get_delimiter(self):
        self.product.parameters.append(';')
        return self
    def get_encoding(self):
        self.product.parameters.append('UTF-8')
        return self
    def get_result(self):
        return self.product

class ReadParameters():
    "List of parameters for read"
    def __init__(self):
        self.parameters = []


class CSVReader:
    "The Director, building a complex representation."
    @staticmethod
    def read():
        "Constructs final parameters list"
        return ReadTasksCSV()\
        .get_filename()\
        .get_delimiter()\
        .get_encoding()\
        .get_result()







""" Builder - end """


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
        #print(f"usunieto task {task_to_delete}")
        return redirect('/worker')
    except:
        return 'Wystapil problem przy usuwaniu zadania'

@app.route('/worker/update/<int:id>', methods=['GET', 'POST'])
def update(id):
    task = Todo.query.get_or_404(id)
    task_to_be_edited = copy.deepcopy(task)
    print(task)

    if request.method == 'POST':
        task.content = request.form['content']
        task.description = request.form['description']
        task.duedate = request.form['duedate']
        task.owner = request.form['owner']
        task.priority = request.form['priority']
        task.progress = request.form['progress']

        try:
            db.session.commit()
            print(f"Edytowano task ")
            history.execute(EditTaskCommand(task_to_be_edited, task))
            return redirect('/worker')
        except:
            return 'Wystapil problem przy edytowaniu zadania'

    else:
        return render_template('update.html', task=task)

@app.route('/worker/undo')
def undo():
    
    try:
        history.undo()
        return redirect('/worker')
    except:
        return 'Wystapil problem przy usuwaniu zadania'


@app.route('/about')
def about():
    return render_template(
        'about.html',
        title='About',
        year=datetime.now().year,
        message='Informacje o projekcie'
    )



""" execution """
history = History()

"""

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

"""


# kod sprawdzajacy czy dwa polaczenia sa ta sama instancja 


c1 = DBConnection.Instance()
c2 = DBConnection.Instance()
print("Id of c1 : {}".format(str(id(c1))))
print("Id of c2 : {}".format(str(id(c1))))

print("c1 is c2 ? " + str(c1 is c2))

# read tasks from CSV

#data = (ReadTasksCSV('dict.csv').withChunksize(10_1000).withDelimiter(',').withEncoding('UTF-8'))
#print(data.withDelimiter)

#data = ReadTasksCSV('dict.csv').withChunksize(10_1000).withDelimiter(',').withEncoding('UTF-8').withHeader(7).withNames('Task name,Task description,Task owner,Created at,Priority,Progress,Due dat').withNaValues('n/a'))

# Builder client
data = CSVReader.read()
print(data.parameters)

segment_data = pd.read_csv(data.parameters[0])
print(segment_data)
