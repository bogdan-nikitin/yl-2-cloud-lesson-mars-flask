from flask_restful import abort, Resource
from data import db_session
from data.users import User
from flask import jsonify
from parsers.users_parser import post_parser, put_parser
import datetime


RULES = ('-jobs', '-departments', '-hashed_password')


def abort_if_user_not_found(user_id):
    session = db_session.create_session()
    users = session.query(User).get(user_id)
    if not users:
        abort(404, message=f'User {user_id} not found')


class UsersResource(Resource):
    @staticmethod
    def get(user_id):
        abort_if_user_not_found(user_id)
        session = db_session.create_session()
        user = session.query(User).get(user_id)
        return jsonify({'user': user.to_dict(rules=RULES)})

    @staticmethod
    def delete(user_id):
        abort_if_user_not_found(user_id)
        session = db_session.create_session()
        users = session.query(User).get(user_id)
        session.delete(users)
        session.commit()
        return jsonify({'success': 'OK'})

    @staticmethod
    def put(user_id):
        abort_if_user_not_found(user_id)
        args = put_parser.parse_args()
        session = db_session.create_session()
        user = session.query(User).get(user_id)
        user.surname = args.get('surname', user.surname)
        user.name = args.get('name', user.name)
        user.age = args.get('age', user.age)
        user.position = args.get('position', user.position)
        user.speciality = args.get('speciality', user.speciality)
        user.address = args.get('address', user.address)
        user.email = args.get('email', user.email)
        password = args.get('password')
        if password:
            user.set_password(password)
        user.modified_date = datetime.datetime.now()
        session.commit()
        return jsonify({'success': 'OK'})


class UsersListResource(Resource):
    @staticmethod
    def get():
        session = db_session.create_session()
        users = session.query(User).all()
        return jsonify(
            {
                'users': [item.to_dict(rules=RULES) for item in users]
            }
        )

    @staticmethod
    def post():
        args = post_parser.parse_args()
        session = db_session.create_session()
        user = User(
            surname=args['surname'],
            name=args['name'],
            age=args['age'],
            position=args['position'],
            speciality=args['speciality'],
            address=args['address'],
            email=args['email'],
            city_from=args.get('city_from'),
            id=args.get('user_id')
        )
        user.set_password(args['password'])
        session.add(user)
        session.commit()
        return jsonify({'success': 'OK'})
