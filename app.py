from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
import click
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:xsSZD0420@localhost:3306/selectsystem?utf8mb4'
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
app.config['SECRET_KEY'] = '123456'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['FLASK_DEBUG'] = True
db = SQLAlchemy(app)


class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20))


class Teacher(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(20))
    name = db.Column(db.String(20))


@app.cli.command()
@click.option('--drop', is_flag=True, help='Create after drop.')
def initdb(drop):
    """Initialize the database."""
    if drop:  # 判断是否输入了选项
        db.drop_all()
    db.create_all()
    click.echo('Initialized database.')


@app.context_processor
def inject_user():
    stu = Student.query.first()
    return dict(stu=stu)


@app.route('/')
def index():
    stu = Student.query.first()
    tea = Teacher.query.all()
    return render_template('index.html', teachers=tea)


@app.errorhandler(404)
def page_not_found(e):
    stu = Student.query.first()
    return render_template('404.html'), 404
