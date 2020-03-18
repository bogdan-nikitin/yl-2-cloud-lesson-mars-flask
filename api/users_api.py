from flask import Blueprint, jsonify, request
from data import db_session
import datetime
import operator
from data.users import User


RULES = ('-jobs', '-departments', '-hashed_password')


blueprint = Blueprint('users_api', __name__, template_folder='templates')


@blueprint.route('/api/users')
def get_users():
    session = db_session.create_session()
    users = session.query(User).all()
    return jsonify(
        {
            'users': [item.to_dict(rules=RULES) for item in users]
         }
    )


@blueprint.route('/api/users/<int:user_id>')
def get_one_users(user_id):
    session = db_session.create_session()
    user = session.query(User).filter(User.id == user_id).first()
    if not user:
        return jsonify({'error': 'Not found'})
    return jsonify(user.to_dict(rules=RULES))


# Обработчик неверного типа добавил в main.py


@blueprint.route('/api/users/', methods=['POST'])
def create_users():
    if not request.json:
        return jsonify({'error': 'Empty request'})
    fields = ['surname', 'name', 'age', 'position', 'speciality', 'address',
              'email']
    if not all(key in request.json for key in fields + ['password']):
        return jsonify({'error': 'Bad request'})
    session = db_session.create_session()
    if user_id := request.json.get('id'):
        ids = list(map(operator.itemgetter(0), session.query(User.id).all()))
        if user_id in ids:
            return jsonify({'error': 'Id already exists'})
    user = User(id=user_id)
    for key in set(fields + ['city_from']) & set(request.json.keys()):
        user.__setattr__(key, request.json[key])
    user.set_password(request.json['password'])
    session.add(session.merge(user))
    session.commit()
    return jsonify({'success': 'OK'})


@blueprint.route('/api/users/<int:users_id>', methods=["DELETE"])
def delete_users(users_id):
    session = db_session.create_session()
    users = session.query(User).filter(User.id == users_id).first()
    if not users:
        return jsonify({'error': "Id doesn't exist"})
    session.delete(users)
    session.commit()
    return jsonify({'success': 'OK'})


@blueprint.route('/api/users/<int:users_id>', methods=["PUT"])
def put_users(users_id):
    session = db_session.create_session()
    users = session.query(User).filter(User.id == users_id).first()
    if not users:
        return jsonify({'error': "Id doesn't exist"})
    if not request.json:
        return jsonify({'error': 'Empty request'})
    fields = ['surname', 'name', 'age', 'position', 'speciality', 'address',
              'email']
    for key in set(request.json.keys()) & set(fields + ['city_from']):
        users.__setattr__(key, request.json[key])
    if (password := request.json.get('password')) is not None:
        users.set_password(password)
    users.modified_date = datetime.datetime.now()
    session.commit()
    return jsonify({'success': 'OK'})
