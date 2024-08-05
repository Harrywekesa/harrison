from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField, SelectField, FloatField, FileField
from wtforms.validators import DataRequired, Email, EqualTo

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
    submit = SubmitField('Register')

class CourseForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired()])
    level = SelectField('Level', choices=[('4', 'Level 4'), ('5', 'Level 5'), ('6', 'Level 6')], validators=[DataRequired()])
    category = SelectField('Category', choices=[('ICT', 'Information Communication Technology'), ('CS', 'Computer Science'), ('Cyber Security', 'Cyber Security')], validators=[DataRequired()])
    submit = SubmitField('Add Course')

class ResourceForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired()])
    course_id = SelectField('Course', coerce=int, validators=[DataRequired()])
    is_free = BooleanField('Free Resource')
    file = FileField('Upload File', validators=[DataRequired()])
    price = FloatField('Price')
    submit = SubmitField('Add Resource')
