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
from flask_mail import Mail, Message
from itsdangerous import URLSafeTimedSerializer

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['UPLOAD_FOLDER'] = 'static/uploads'
<<<<<<< HEAD
app.config['ADMIN_EMAIL'] = 'harrisonwekesa09@gmail.com.com'  # Add your admin email here
=======
>>>>>>> harrison/main

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
<<<<<<< HEAD
            if not user.is_verified:
                flash('Please verify your email address before logging in.', 'danger')
                return redirect(url_for('login'))
            if user.is_suspended:
                flash(f'Your account has been suspended. Please contact the admin at {app.config["ADMIN_EMAIL"]}.', 'danger')
                return redirect(url_for('login'))
=======
>>>>>>> harrison/main
            session['user_id'] = user.id
            session['is_admin'] = user.is_admin
            flash('Login successful!', 'success')
            return redirect(url_for('admin_dashboard') if user.is_admin else url_for('home'))
        else:
            flash('Login failed. Check your email and password.', 'danger')
    return render_template('login.html', form=form)

<<<<<<< HEAD
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'danger')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

=======
>>>>>>> harrison/main
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session or not session.get('is_admin'):
            flash('Unauthorized access!', 'danger')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

<<<<<<< HEAD
# Flask-Mail configuration
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_USERNAME'] = 'harrisonwekesa09@gmail.com'
app.config['MAIL_PASSWORD'] = 'nsmz fpzu oytg egij'
app.config['MAIL_DEFAULT_SENDER'] = 'harrisonwekesa09@gmail.com'

mail = Mail(app)
s = URLSafeTimedSerializer(app.config['SECRET_KEY'])

=======
>>>>>>> harrison/main
@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data)
<<<<<<< HEAD
        user = User(username=form.username.data, email=form.email.data, password=hashed_password, is_admin=False)
        db.session.add(user)
        db.session.commit()

        # Generate a verification token
        token = s.dumps(user.email, salt='email-confirm')

        # Send the verification email
        confirm_url = url_for('confirm_email', token=token, _external=True)
        html = render_template('email/verify_email.html', confirm_url=confirm_url)
        subject = "Please confirm your email"
        send_email(user.email, subject, html)

        flash('Registration successful! Please verify your email address.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

def send_email(to, subject, template):
    msg = Message(subject, recipients=[to], html=template)
    mail.send(msg)

@app.route('/confirm/<token>')
def confirm_email(token):
    try:
        email = s.loads(token, salt='email-confirm', max_age=3600)  # Token is valid for 1 hour
    except:
        flash('The confirmation link is invalid or has expired.', 'danger')
        return redirect(url_for('login'))

    user = User.query.filter_by(email=email).first_or_404()
    if user.is_verified:
        flash('Account already verified. Please log in.', 'success')
    else:
        user.is_verified = True
        db.session.commit()
        flash('You have confirmed your account. Thanks!', 'success')
    return redirect(url_for('login'))

=======
        user = User(username=form.username.data, email=form.email.data, password=hashed_password, is_admin=form.is_admin.data)
        db.session.add(user)
        db.session.commit()
        flash('Registration successful! You can now log in.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

>>>>>>> harrison/main
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
<<<<<<< HEAD

@app.route('/admin/users')
@admin_required
def admin_users():
    users = User.query.all()
    return render_template('admin/users.html', users=users)

@app.route('/admin/user/<int:id>/suspend', methods=['POST'])
@admin_required
def suspend_user(id):
    user = User.query.get_or_404(id)
    user.is_suspended = True
    db.session.commit()
    flash(f'User {user.username} has been suspended.', 'info')
    return redirect(url_for('admin_users'))

@app.route('/admin/user/<int:id>/unsuspend', methods=['POST'])
@admin_required
def unsuspend_user(id):
    user = User.query.get_or_404(id)
    user.is_suspended = False
    db.session.commit()
    flash(f'User {user.username} has been unsuspended.', 'info')
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
=======
@app.route('/courses')

>>>>>>> harrison/main
def courses():
    courses = Course.query.all()
    return render_template('courses.html', courses=courses)

@app.route('/course/<int:id>')
<<<<<<< HEAD
@login_required
=======
>>>>>>> harrison/main
def course_detail(id):
    course = Course.query.get_or_404(id)
    resources = Resource.query.filter_by(course_id=id).all()
    return render_template('course_detail.html', course=course, resources=resources)

@app.route('/resource/<int:id>')
<<<<<<< HEAD
@login_required
=======
>>>>>>> harrison/main
def resource_detail(id):
    resource = Resource.query.get_or_404(id)
    return render_template('resource_detail.html', resource=resource)

@app.route('/resource/download/<int:id>')
<<<<<<< HEAD
@login_required
=======
>>>>>>> harrison/main
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
