from flask_wtf import FlaskForm
from wtforms import DateField, PasswordField, StringField, TextAreaField
from wtforms.validators import (DataRequired, Email, EqualTo, Length, Regexp,
                                ValidationError)

from models import User


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])


class EntryForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    timestamp = DateField('Date (MM/DD/YYYY)', format='%m/%d/%Y')
    time_spent = StringField('Time Spent', validators=[DataRequired()])
    learned = TextAreaField('What I Learned:', validators=[DataRequired()])
    resources = TextAreaField('Resources to Remember: (Optional)')


class TagForm(FlaskForm):
    tag = StringField('New Tag', validators=[DataRequired()])
