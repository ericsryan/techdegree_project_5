from flask_wtf import FlaskForm
from wtforms import DateField, PasswordField, StringField, TextAreaField
from wtforms.validators import (DataRequired, Email, EqualTo, Length, Regexp,
                                ValidationError)

from models import User


def name_exists(form, field):
    if User.select().where(User.username == field.data).exists():
        raise ValidationError("User with that name already exists.")


def email_exists(form, field):
    if User.select().where(User.username == field.data).exists():
        raise ValidationError("User with that email already exists")


class RegisterForm(FlaskForm):
    username = StringField(
        'Username',
        validators=[
            DataRequired(),
            Regexp(
                r'^[a-zA-Z0-9_]+$',
                message=("Username should be one word, letters, numbers/ "
                         "and underscores only.")
            ),
            name_exists
        ])
    email = StringField(
        'Email',
        validators=[
            DataRequired(),
            Email(),
            email_exists
        ])
    password = PasswordField(
        'Password',
        validators=[
            DataRequired(),
            Length(min=8),
            EqualTo('password2', message='Passwords must match')
        ])
    password2 = PasswordField(
        'Confirm Password',
        validators=[DataRequired()]
    )


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])


class Entry(FlaskForm):
    timestamp = DateField('Date', format='%m-%d-%Y')
    time_spent = StringField('Time Spent', validators=[DataRequired()])
    learned = TextAreaField('What I Learned:', validators=[DataRequired()])
    resources = TextAreaField('Resources to Remember: (Optional)')
