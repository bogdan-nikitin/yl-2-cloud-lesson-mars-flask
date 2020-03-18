from flask import Blueprint, jsonify, request
from data import db_session
from data.jobs import Jobs
from flask_login import login_required, current_user
import operator
from data.users import User
from general import get_category


RULES = ('-user', '-categories', 'categories_levels')


blueprint = Blueprint('jobs_api', __name__, template_folder='templates')


@blueprint.route('/api/jobs')
def get_jobs():
    session = db_session.create_session()
    jobs = session.query(Jobs).all()
    return jsonify(
        {
            'jobs': [item.to_dict(rules=RULES) for item in jobs]
         }
    )


@blueprint.route('/api/jobs/<int:job_id>')
def get_one_jobs(job_id):
    session = db_session.create_session()
    job = session.query(Jobs).filter(Jobs.id == job_id).first()
    if not job:
        return jsonify({'error': 'Not found'})
    return jsonify(job.to_dict(rules=RULES))


# Обработчик неверного типа добавил в main.py


def get_collaborators(request_json):
    collaborators = request_json['collaborators']
    team_leader = request_json['team_leader']
    if not collaborators:
        return set()
    try:
        ids = set(map(int, collaborators))
    except ValueError:
        raise Exception('Wrong collaborators format')
    if team_leader in ids:
        raise Exception("Team leader can't be collaborator")
    session = db_session.create_session()
    users = set(map(operator.itemgetter(0),
                    session.query(User.id).filter(User.id.in_(ids)).all()))
    nonexistent_users = ids - users
    if nonexistent_users:
        raise Exception(f'There is no such users: '
                        f'{", ".join(map(str, nonexistent_users))}')
    return ids


def get_categories(request_json):
    try:
        categories_levels = set(map(int, request_json['categories_levels']))
    except ValueError:
        raise Exception('Wrong categories format')
    categories = []
    for level in categories_levels:
        categories += [get_category(level)]
    return categories


@blueprint.route('/api/jobs', methods=['POST'])
def create_jobs():
    if not request.json:
        return jsonify({'error': 'Empty request'})
    elif not all(key in request.json for key in
                 ['job', 'team_leader', 'work_size', 'collaborators',
                  'categories_levels']):
        return jsonify({'error': 'Bad request'})
    session = db_session.create_session()
    ids = list(map(operator.itemgetter(0), session.query(Jobs.id).all()))
    if request.json.get('id') in ids:
        return jsonify({'error': 'Id already exists'})
    try:
        collaborators = get_collaborators(request.json)
    except Exception as e:
        return jsonify({'error': str(e)})
    jobs = Jobs(job=request.json['job'],
                team_leader=request.json['team_leader'],
                work_size=request.json['work_size'],
                collaborators=', '.join(map(str, collaborators)),
                start_date=request.json.get('start_date'),
                end_date=request.json.get('end_date'),
                is_finished=request.json.get('is_finished'),
                id=request.json.get('id'))
    try:
        categories = get_categories(request.json)
    except Exception as e:
        return jsonify({'error': str(e)})
    jobs.categories.extend(categories)
    jobs.author = request.json['team_leader']
    session.add(session.merge(jobs))
    session.commit()
    return jsonify({'success': 'OK'})


@blueprint.route('/api/jobs/<int:jobs_id>', methods=["DELETE"])
def delete_jobs(jobs_id):
    session = db_session.create_session()
    jobs = session.query(Jobs).filter(Jobs.id == jobs_id).first()
    if not jobs:
        return jsonify({'error': "Id doesn't exist"})
    session.delete(jobs)
    session.commit()
    return jsonify({'success': 'OK'})


@blueprint.route('/api/jobs/<int:jobs_id>', methods=["PUT"])
def put_jobs(jobs_id):
    session = db_session.create_session()
    jobs = session.query(Jobs).filter(Jobs.id == jobs_id).first()
    if not jobs:
        return jsonify({'error': "Id doesn't exist"})
    if not request.json:
        return jsonify({'error': 'Empty request'})
    fields = ['team_leader', 'job', 'work_size', 'start_date', 'end_date',
              'is_finished']
    for key in set(request.json.keys()) & set(fields):
        jobs.__setattr__(key, request.json[key])
    if request.json.get('id'):
        ids = list(map(operator.itemgetter(0), session.query(Jobs.id).all()))
        if request.json.get('id') in ids:
            return jsonify({'error': 'Id already exists'})
    if request.json.get('collaborators'):
        try:
            collaborators = get_collaborators(request.json)
            jobs.collaborators = ', '.join(map(str, collaborators))
        except Exception as e:
            return jsonify({'error': str(e)})
    if request.json.get('categories_levels'):
        try:
            categories = get_categories(request.json)
            jobs.categories.clear()
            categories = [session.merge(category) for category in categories]
            jobs.categories.extend(categories)
        except Exception as e:
            return jsonify({'error': str(e)})
    jobs.author = jobs.team_leader
    session.commit()
    return jsonify({'success': 'OK'})


