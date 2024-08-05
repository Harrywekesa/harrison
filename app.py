from flask import Flask, render_template, request, redirect, url_for, session, flash, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField, SelectField, FloatField, FileField
from wtforms.validators import DataRequired, Email, EqualTo
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['UPLOAD_FOLDER'] = 'static/uploads'
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)

class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    level = db.Column(db.String(50), nullable=False)
    category = db.Column(db.String(100), nullable=False)

class Resource(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    is_free = db.Column(db.Boolean, default=False)
    file_path = db.Column(db.String(200), nullable=False)
    price = db.Column(db.Float, nullable=True)
    course = db.relationship('Course', backref=db.backref('resources', lazy=True))

from forms import LoginForm, RegistrationForm, CourseForm, ResourceForm

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and check_password_hash(user.password, form.password.data):
            session['user_id'] = user.id
            session['is_admin'] = user.is_admin
            flash('Login successful!', 'success')
            return redirect(url_for('admin_dashboard' if user.is_admin else 'home'))
        else:
            flash('Login failed. Check your email and password.', 'danger')
    return render_template('login.html', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data)
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
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
def admin_dashboard():
    if 'user_id' not in session or not session.get('is_admin'):
        flash('Unauthorized access!', 'danger')
        return redirect(url_for('login'))
    return render_template('admin/dashboard.html')

@app.route('/courses')
def courses():
    courses = Course.query.all()
    return render_template('courses.html', courses=courses)

@app.route('/course/<int:id>')
def course_detail(id):
    course = Course.query.get_or_404(id)
    resources = Resource.query.filter_by(course_id=id).all()
    return render_template('course_detail.html', course=course, resources=resources)

@app.route('/resource/<int:id>')
def resource_detail(id):
    resource = Resource.query.get_or_404(id)
    return render_template('resource_detail.html', resource=resource)

@app.route('/resource/download/<int:id>')
def resource_download(id):
    resource = Resource.query.get_or_404(id)
    if resource.is_free or 'user_id' in session:
        return send_from_directory(app.config['UPLOAD_FOLDER'], resource.file_path, as_attachment=True)
    else:
        flash('Please log in to download this resource.', 'danger')
        return redirect(url_for('login'))

@app.route('/admin/dashboard')
def admin_dashboard():
    if 'user_id' not in session or not User.query.get(session['user_id']).is_admin:
        flash('Unauthorized access!', 'danger')
        return redirect(url_for('login'))
    return render_template('admin/dashboard.html')

@app.route('/admin/add_course', methods=['GET', 'POST'])
def add_course():
    if 'user_id' not in session or not User.query.get(session['user_id']).is_admin:
        flash('Unauthorized access!', 'danger')
        return redirect(url_for('login'))
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
def add_resource():
    if 'user_id' not in session or not User.query.get(session['user_id']).is_admin:
        flash('Unauthorized access!', 'danger')
        return redirect(url_for('login'))
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
