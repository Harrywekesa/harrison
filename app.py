from flask import Flask, render_template, request, redirect, url_for, session, flash, send_from_directory
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField, SelectField, FloatField, FileField
from wtforms.validators import DataRequired, Email, EqualTo
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os
from functools import wraps
from flask import abort
from flask_migrate import Migrate
from db import db  # Import the db instance from db.py
from models import User, Course, Resource

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['UPLOAD_FOLDER'] = 'static/uploads'

db.init_app(app)  # Initialize the db with the app
migrate = Migrate(app, db)  # Initialize Migrate

# Forms
class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Login')

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    is_admin = BooleanField('Register as Admin')
    submit = SubmitField('Register')

class CourseForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired()])
    level = StringField('Level', validators=[DataRequired()])
    category = StringField('Category', validators=[DataRequired()])
    submit = SubmitField('Add Course')

class ResourceForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired()])
    course_id = SelectField('Course', coerce=int, validators=[DataRequired()])
    is_free = BooleanField('Free')
    file = FileField('File', validators=[DataRequired()])
    price = FloatField('Price')
    submit = SubmitField('Add Resource')

# Routes
@app.route('/')
def home():
    courses = Course.query.all()
    return render_template('home.html', courses=courses)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and check_password_hash(user.password, form.password.data):
            session['user_id'] = user.id
            session['is_admin'] = user.is_admin
            flash('Login successful!', 'success')
            return redirect(url_for('admin_dashboard') if user.is_admin else url_for('home'))
        else:
            flash('Login failed. Check your email and password.', 'danger')
    return render_template('login.html', form=form)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'danger')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session or not session.get('is_admin'):
            flash('Unauthorized access!', 'danger')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data)
        user = User(username=form.username.data, email=form.email.data, password=hashed_password, is_admin=form.is_admin.data)
        db.session.add(user)
        db.session.commit()
        flash('Registration successful! You can now log in.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('is_admin', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('home'))

@app.route('/admin/dashboard')
@admin_required
def admin_dashboard():
    return render_template('admin/dashboard.html')

@app.route('/admin/users')
@admin_required
def admin_users():
    users = User.query.all()
    return render_template('admin/users.html', users=users)

@app.route('/admin/user/<int:id>/suspend', methods=['POST'])
@admin_required
def suspend_user(id):
    user = User.query.get_or_404(id)
    # Implement your suspend logic here
    flash(f'User {user.username} has been suspended.', 'info')
    return redirect(url_for('admin_users'))

@app.route('/admin/user/<int:id>/remove', methods=['POST'])
@admin_required
def remove_user(id):
    user = User.query.get_or_404(id)
    db.session.delete(user)
    db.session.commit()
    flash(f'User {user.username} has been removed.', 'info')
    return redirect(url_for('admin_users'))

@app.route('/admin/user/<int:id>/logs')
@admin_required
def user_logs(id):
    user = User.query.get_or_404(id)
    # Fetch and display the user's activity logs here
    logs = []  # Replace with actual log fetching logic
    return render_template('admin/user_logs.html', user=user, logs=logs)

@app.route('/courses')
def courses():
    courses = Course.query.all()
    return render_template('courses.html', courses=courses)

@app.route('/course/<int:id>')
@login_required
def course_detail(id):
    course = Course.query.get_or_404(id)
    resources = Resource.query.filter_by(course_id=id).all()
    return render_template('course_detail.html', course=course, resources=resources)

@app.route('/resource/<int:id>')
@login_required
def resource_detail(id):
    resource = Resource.query.get_or_404(id)
    return render_template('resource_detail.html', resource=resource)

@app.route('/resource/download/<int:id>')
@login_required
def resource_download(id):
    resource = Resource.query.get_or_404(id)
    if resource.is_free or 'user_id' in session:
        return send_from_directory(app.config['UPLOAD_FOLDER'], resource.file_path, as_attachment=True)
    else:
        flash('Please log in to download this resource.', 'danger')
        return redirect(url_for('login'))

@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'Course': Course, 'Resource': Resource}

@app.route('/admin/add_course', methods=['GET', 'POST'])
@admin_required
def add_course():
    form = CourseForm()
    if form.validate_on_submit():
        course = Course(
            title=form.title.data,
            description=form.description.data,
            level=form.level.data,
            category=form.category.data
        )
        db.session.add(course)
        db.session.commit()
        flash('Course added successfully!', 'success')
        return redirect(url_for('admin_dashboard'))
    return render_template('admin/add_course.html', form=form)

@app.route('/admin/add_resource', methods=['GET', 'POST'])
@admin_required
def add_resource():
    form = ResourceForm()
    form.course_id.choices = [(course.id, course.title) for course in Course.query.all()]
    if form.validate_on_submit():
        if 'file' not in request.files:
            flash('No file part', 'danger')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('No selected file', 'danger')
            return redirect(request.url)
        if file:
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            resource = Resource(
                title=form.title.data,
                description=form.description.data,
                course_id=form.course_id.data,
                is_free=form.is_free.data,
                file_path=filename,
                price=form.price.data
            )
            db.session.add(resource)
            db.session.commit()
            flash('Resource added successfully!', 'success')
            return redirect(url_for('admin_dashboard'))
    return render_template('admin/add_resource.html', form=form)

if __name__ == '__main__':
    app.run(debug=True)
