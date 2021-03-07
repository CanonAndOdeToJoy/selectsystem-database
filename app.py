from flask import Flask, render_template, request, url_for, flash, redirect
from flask_sqlalchemy import SQLAlchemy
import click
from flask_login import login_user, LoginManager, UserMixin, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:xsSZD0420@localhost:3306/selectsystem?utf8mb4'
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = False
app.config['SECRET_KEY'] = '123456'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['FLASK_DEBUG'] = True
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view= 'slogin'


class Studentinf(db.Model):
    __tablename = 'studentinf'
    sid = db.Column(db.String(10), primary_key=True)
    name = db.Column(db.String(20))
    introduce = db.Column(db.String(200))
    phone = db.Column(db.String(20))


class Teacherinf(db.Model):
    __tablename = 'teacherinf'
    tid = db.Column(db.String(10), primary_key=True)
    name = db.Column(db.String(20))
    title = db.Column(db.String(20))
    introduce = db.Column(db.String(200))
    address = db.Column(db.String(50))
    email = db.Column(db.String(50))


class Student(db.Model, UserMixin):
    __tablename__ = 'student'
    id = db.Column(db.Integer, primary_key=True)
    sid = db.Column(db.String(10), db.ForeignKey('studentinf.sid'))
    spassword = db.Column(db.String(128))

    def set_password(self, spassword):
        self.spassword = generate_password_hash(spassword)

    def validate_password(self, spassword):
        return check_password_hash(self.spassword, spassword)


class Teacher(db.Model, UserMixin):
    __tablename__ = 'teacher'
    id = db.Column(db.Integer, primary_key=True)
    tid = db.Column(db.String(10), db.ForeignKey('teacherinf.tid'))
    tpassword = db.Column(db.String(128))

    def set_password(self, tpassword):
        self.tpassword = generate_password_hash(tpassword)

    def validate_password(self, tpassword):
        return check_password_hash(self.tpassword, tpassword)


class Schoice(db.Model):
    __tablename__ = 'schoice'
    id = db.Column(db.String(10), db.ForeignKey('studentinf.sid'), primary_key=True)
    firstchoice = db.Column(db.String(10)) #####
    secondchoice = db.Column(db.String(10))


class Tchoice(db.Model):
    __tablename = 'tchoice'
    sid = db.Column(db.String(10), db.ForeignKey('studentinf.sid'), primary_key=True)
    tid = db.Column(db.String(10), db.ForeignKey('teacherinf.tid'), primary_key=True)
    isfirst = db.Column(db.Integer)


class Final(db.Model):
    __tablename = 'final'
    sid = db.Column(db.String(10), db.ForeignKey('studentinf.sid'), primary_key=True)
    tid = db.Column(db.String(10), db.ForeignKey('teacherinf.tid'), primary_key=True)


@app.cli.command()
@click.option('--drop', is_flag=True, help='Create after drop.')
def initdb(drop):
    """Initialize the database."""
    if drop:  # 判断是否输入了选项
        db.drop_all()
    db.create_all()
    click.echo('Initialized database.')


@app.cli.command()
@click.option('--sid', prompt=True, help='The id used to login.')
@click.option('--password', prompt=True, hide_input=False, confirmation_prompt=True, help='The password used to login.')
def admin(sid, password):
    """Create user."""
    db.create_all()
    student = Student.query.filter_by(sid=sid).first()
    if student is not None:
        click.echo('Updating user...')
        student.set_password(password)
    else:
        click.echo('Creating user..')
        student = Student(sid=sid, spassword='0')
        student.set_password(password)
        db.session.add(student)
    db.session.commit()
    click.echo('Done.')


@login_manager.user_loader
def load_user(student_sid):
    student= Student.query.get(int(student_sid))
    return student


@app.context_processor
def inject_user():
    if not current_user.is_authenticated:
        student = []
    else:
        student = Student.query.filter_by(sid=current_user.sid).first()
    stu = Student.query.first()
    return dict(stu=student)


@app.route('/')
def index():
    if not current_user.is_authenticated:
        tea = []
    else:
        tea = Teacher.query.all()
    return render_template('index.html', teachers=tea)


@app.route('/tlogin', methods=['GET', 'POST'])
def slogin():
    if request.method == 'POST':
        sid = request.form['sid']
        spassword = request.form['password']
        if not sid or not spassword:
            flash('Invalid input')
            return redirect(url_for('slogin'))

        student = Student.query.filter_by(sid=sid).first()
        if sid == student.sid and student.validate_password(spassword):
            login_user(student)
            flash('Login success.')
            return redirect(url_for('index'))
        flash('Invalid username or password.')
        return redirect(url_for('slogin'))
    return render_template('slogin.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Goodbye.')
    return redirect(url_for('index'))


@app.errorhandler(404)
def page_not_found(e):
    stu = Student.query.first()
    return render_template('404.html'), 404


@app.route('/schoice', methods=['GET', 'POST'])
@login_required
def schoice():
    if request.method == 'POST':
        firstchoice = request.form.get('firstchoice')
        secondchoice = request.form.get('secondchoice')
        if not firstchoice or not secondchoice:
            flash('Invalid input.')
            return redirect(url_for('index'))
        sc = Schoice.query.filter_by(id=current_user.sid).first()
        if sc is not None:
            sc.firstchoice = firstchoice
            sc.secondchoice = secondchoice
        else:
            sc = Schoice(id=current_user.sid, firstchoice=firstchoice, secondchoice=secondchoice)
            db.session.add(sc)
        db.session.commit()
        flash('Item created.')
        return redirect(url_for('index'))
    stu = Student.query.filter_by(sid=current_user.sid).first()
    tea = Teacher.query.all()
    return render_template('schoice.html', teachers=tea)


@app.route('/shome')
@login_required
def stuhome():
    tutor = Final.query.filter_by(sid=current_user.sid).first()
    return render_template('stuhome.html', tutor=tutor)
