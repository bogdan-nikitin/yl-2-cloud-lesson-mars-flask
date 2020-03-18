from flask_wtf import FlaskForm

from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms import IntegerField
from wtforms.validators import DataRequired, EqualTo, ValidationError

from data.users import User
from data import db_session

import operator


def user_in_table_validator(form, field):
    session = db_session.create_session()
    user = session.query(User).filter(User.id == field.data).first()
    if not user:
        raise ValidationError('There is no such user')


def collaborators_validator(form, field):
    if not field.data:
        return
    try:
        ids = set(map(int, field.data.split(',')))
    except ValueError:
        raise ValidationError("Invalid collaborators' ids")
    if form.teamLeader.data in ids:
        raise ValidationError("Team leader can't be collaborator")
    session = db_session.create_session()
    users = set(map(operator.itemgetter(0),
                    session.query(User.id).filter(User.id.in_(ids)).all()))
    nonexistent_users = ids - users
    if nonexistent_users:
        raise ValidationError(f'There is no such users: '
                              f'{", ".join(map(str, nonexistent_users))}')


def members_validator(form, field):
    if not field.data:
        return
    try:
        ids = set(map(int, field.data.split(',')))
    except ValueError:
        raise ValidationError("Invalid members' ids")
    session = db_session.create_session()
    users = set(map(operator.itemgetter(0),
                    session.query(User.id).filter(User.id.in_(ids)).all()))
    nonexistent_users = ids - users
    if nonexistent_users:
        raise ValidationError(f'There is no such users: '
                              f'{", ".join(map(str, nonexistent_users))}')
    if form.chief.data in ids:
        raise ValidationError("Chief can't be member")


class LoginForm(FlaskForm):
    email = StringField('Login / email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    rememberMe = BooleanField('Remember me')
    submit = SubmitField('Sign in')


class RegisterForm(FlaskForm):
    email = StringField('Login / email', validators=[DataRequired()])
    password = PasswordField('Password')
    repeatPassword = PasswordField('Repeat password',
                                   validators=[DataRequired(),
                                               EqualTo('password')])
    surname = StringField('Surname', validators=[DataRequired()])
    name = StringField('Name', validators=[DataRequired()])
    age = IntegerField('Age', validators=[DataRequired()])
    position = StringField('Position', validators=[DataRequired()])
    speciality = StringField('Speciality', validators=[DataRequired()])
    address = StringField('Address', validators=[DataRequired()])
    cityFrom = StringField('City From')
    submit = SubmitField('Submit')


class AddJobForm(FlaskForm):
    job = StringField('Job Title', validators=[DataRequired()])
    teamLeader = IntegerField('Team Leader id',
                              validators=[DataRequired(),
                                          user_in_table_validator])
    workSize = IntegerField('Work Size', validators=[DataRequired()])
    collaborators = StringField('Collaborators',
                                validators=[collaborators_validator])
    category = IntegerField('Hazard Category')
    isFinished = BooleanField('Is job finished?')
    submit = SubmitField('Submit')


class AddDepartment(FlaskForm):
    title = StringField('Department Title', validators=[DataRequired()])
    chief = IntegerField('Chief',
                         validators=[DataRequired(), user_in_table_validator])
    members = StringField('Members', validators=[members_validator])
    email = StringField('Email', validators=[DataRequired()])
    submit = SubmitField('Submit')