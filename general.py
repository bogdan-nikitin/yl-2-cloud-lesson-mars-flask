from data import db_session
from data.category import Category
from requests import get


def get_category(level):
    session = db_session.create_session()
    category = session.query(Category).filter(Category.level == level).first()
    if not category:
        category = Category(level=level)
        session.add(category)
        session.commit()
    return category


class UserArgType:
    def __new__(cls, user_id):
        json_response = get(
            f'http://127.0.0.1:5000//api/v2/users/{user_id}'
        ).json()
        if 'user' in json_response:
            return int(user_id)
        raise Exception('There is no such user')

