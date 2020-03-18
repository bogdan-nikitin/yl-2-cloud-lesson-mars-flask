import os

from flask_login import login_user, login_required, logout_user, current_user
from flask_login.login_manager import LoginManager

from flask_restful import Api
from resources import users_resource, jobs_resource

from flask import Flask, url_for, redirect, render_template, abort
from flask import make_response, jsonify

from data.category import Category
from data.users import User
from data.jobs import Jobs
from data.departments import Departments

import datetime
import requests

from api import jobs_api, users_api

import urllib.parse as urlparse
from urllib.parse import urlencode

from forms import *

from general import get_category

from data import db_session


PORT = 5000
SERVER = 'http://127.0.0.1'
STATIC_API_SERVER = 'https://static-maps.yandex.ru/1.x/'
GEOCODER_API_SERVER = 'https://geocode-maps.yandex.ru/1.x/'

GEOCODER_API_KEY = "40d1649f-0493-4b70-98ba-98533de7710b"


# Конфигурация приложения
app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'

app.register_blueprint(jobs_api.blueprint)
app.register_blueprint(users_api.blueprint)

api = Api(app)
api.add_resource(users_resource.UsersResource, '/api/v2/users/<int:user_id>')
api.add_resource(users_resource.UsersListResource, '/api/v2/users')
api.add_resource(jobs_resource.JobsResource, '/api/v2/jobs/<int:jobs_id>')
api.add_resource(jobs_resource.JobsListResource, '/api/v2/jobs/')

login_manager = LoginManager()
login_manager.init_app(app)
# Конец кофнигурации


@login_manager.user_loader
def load_user(user_id):
    session = db_session.create_session()
    return session.query(User).get(user_id)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/')


def get_css():
    return url_for('static', filename='css/style.css')


@app.route('/login', methods=['POST', 'GET'])
def login():
    form = LoginForm()
    param = {
        'css': get_css(),
        'form': form,
        'title': 'Log in'
    }
    if form.validate_on_submit():
        session = db_session.create_session()
        user = session.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.rememberMe.data)
            return redirect('/')
        else:
            return render_template('login.html',
                                   **param,
                                   message='There is no such user')
    return render_template('login.html', **param)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    param = {
        'css': get_css(),
        'form': form,
        'title': 'Authorization'
    }
    if form.validate_on_submit():
        session = db_session.create_session()
        if session.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', **param,
                                   message='This user already exists')
        user = User(surname=form.surname.data,
                    name=form.name.data,
                    age=form.age.data,
                    position=form.position.data,
                    speciality=form.speciality.data,
                    address=form.address.data,
                    email=form.email.data,
                    city_from=form.cityFrom.data)

        user.set_password(form.password.data)
        session.add(user)
        session.commit()
        return redirect('/')
    return render_template('register.html', **param)


def get_collaborators(form):
    if form.collaborators.data.strip():
        return set(map(int, form.collaborators.data.split(',')))
    return set()


def get_members(form):
    if form.members.data.strip():
        return set(map(int, form.members.data.split(',')))
    return set()


@app.route('/add_job', methods=['POST', 'GET'])
@login_required
def add_job():
    template = 'add_job.html'
    form = AddJobForm()
    param = {
        'css': get_css(),
        'title': 'Adding a job',
        'form': form
    }
    if form.validate_on_submit():

        session = db_session.create_session()
        team_leader = form.teamLeader.data

        collaborators = get_collaborators(form)

        job = Jobs(team_leader=team_leader,
                   job=form.job.data,
                   work_size=form.workSize.data,
                   collaborators=','.join(map(str, collaborators)),
                   is_finished=form.isFinished.data,
                   author=current_user.id)
        if form.isFinished.data:
            job.end_date = datetime.datetime.now()

        if form.category.data:
            job.categories.append(get_category(form.category.data))

        job = session.merge(job)
        session.add(job)
        session.commit()
        return redirect('/')
    return render_template(template, **param)


def get_job(session, job_id):
    job = session.query(Jobs).filter(Jobs.id == job_id).first()
    if not job:
        abort(404)
    elif current_user.id not in [1, job.author]:
        abort(403)
    return job


def get_department(session, department_id):
    department = session.query(Departments).filter(
        Departments.id == department_id).first()
    if not department:
        abort(404)
    elif current_user.id not in [1, department.author]:
        abort(403)
    return department


@app.route('/edit_job/<int:id_>', methods=['POST', 'GET'])
def edit_job(id_):
    template = 'add_job.html'
    session = db_session.create_session()
    job = get_job(session, id_)
    form = AddJobForm()
    param = {
        'css': get_css(),
        'form': form,
        'title': 'Editing a job'
    }
    if form.validate_on_submit():
        session = db_session.create_session()

        collaborators = get_collaborators(form)
        prev_is_finished = job.is_finished
        job.team_leader = form.teamLeader.data
        job.work_size = form.workSize.data
        job.collaborators = ','.join(map(str, collaborators))
        job.is_finished = form.isFinished.data
        job.job = form.job.data
        if form.isFinished.data:
            job.end_date = datetime.datetime.now()
        elif not form.isFinished.data and prev_is_finished:
            job.end_date = None
        category = session.merge(get_category(form.category.data))
        job = session.merge(job)
        if job.categories:
            job.categories[0] = category
        else:
            job.categories.append(category)
        session.commit()
        return redirect('/')
    else:
        if job.categories:
            form.category.data = job.categories[0].level
        form.teamLeader.data = job.team_leader
        form.workSize.data = job.work_size
        form.collaborators.data = job.collaborators
        form.isFinished.data = job.is_finished
        form.job.data = job.job
    return render_template(template, **param)


@app.route('/del_job/<int:id_>')
@login_required
def del_job(id_):
    session = db_session.create_session()
    job = get_job(session, id_)
    session.delete(job)
    session.commit()
    return redirect('/')


@app.route('/departments')
def departments():
    session = db_session.create_session()
    param = {
        'css': get_css(),
        'title': 'List of departments',
        'User': User,
        'session': session,
        'departments': session.query(Departments).all()
    }
    return render_template('departments.html', **param)


@app.route('/add_department', methods=['POST', 'GET'])
def add_department():
    template = 'add_department.html'
    form = AddDepartment()
    param = {
        'css': get_css(),
        'title': 'Adding a Department',
        'form': form
    }
    if form.validate_on_submit():
        session = db_session.create_session()

        members = get_members(form)

        department = Departments(author=current_user.id,
                                 title=form.title.data,
                                 chief=form.chief.data,
                                 members=', '.join(map(str, members)),
                                 email=form.email.data)
        session.add(department)
        session.commit()
        return redirect('/departments')

    return render_template(template, **param)


@app.route('/edit_department/<int:id_>', methods=['POST', 'GET'])
def edit_department(id_):
    template = 'add_department.html'
    form = AddDepartment()
    param = {
        'css': get_css(),
        'title': 'Editing a Department',
        'form': form
    }
    session = db_session.create_session()
    department = get_department(session, id_)
    if form.validate_on_submit():
        session = db_session.create_session()

        members = get_members(form)

        department.title = form.title.data
        department.chief = form.chief.data
        department.members = ', '.join(map(str, members))
        department.email = form.email.data

        session.commit()
        return redirect('/departments')
    else:
        form.title.data = department.title
        form.chief.data = department.chief
        form.members.data = department.members
        form.email.data = department.email

    return render_template(template, **param)


@app.route('/del_department/<int:id_>')
def del_department(id_):
    session = db_session.create_session()
    department = get_department(session, id_)
    session.delete(department)
    session.commit()
    return redirect('/departments')


@app.route('/')
def index():
    session = db_session.create_session()
    param = {
        'jobs': session.query(Jobs).all(),
        'css': get_css(),
        'title': 'Work log',
        'session': session,
        'User': User
    }
    return render_template('works_log.html', **param)


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


@app.route('/users_show/<int:user_id>')
def users_show(user_id):
    try:
        users_response = requests.get(f'{SERVER}:{PORT}/api/users/{user_id}')
        users_response_json = users_response.json()
        city = users_response_json['city_from']
        geocoder_params = {
            'apikey': GEOCODER_API_KEY,
            'geocode': city,
            'format': 'json'
        }
        geocoder_response = requests.get(GEOCODER_API_SERVER,
                                         params=geocoder_params)
        geocoder_response_json = geocoder_response.json()
        pos = geocoder_response_json["response"]["GeoObjectCollection"][
            "featureMember"][0]["GeoObject"]["Point"]["pos"]
        static_params = {
            'll': pos.replace(' ', ','),
            'l': 'sat',
            'z': 13
        }

        url_parts = list(urlparse.urlparse(STATIC_API_SERVER))
        query = dict(urlparse.parse_qsl(url_parts[4]))
        query.update(static_params)

        url_parts[4] = urlencode(query)
        city_img_src = urlparse.urlunparse(url_parts)
    except Exception as e:
        abort(404)
        return str(e)
    param = {
        'css': get_css(),
        'city_img_src': city_img_src,
        'user': users_response_json
    }
    return render_template('users_show.html', **param)


if __name__ == '__main__':
    db_session.global_init('db/martians.db')
    app.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5000)))

