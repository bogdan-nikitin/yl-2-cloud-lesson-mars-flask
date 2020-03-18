import sqlalchemy as sa
import sqlalchemy.orm as orm
from .db_session import SqlAlchemyBase
from sqlalchemy_serializer import SerializerMixin


class Departments(SqlAlchemyBase, SerializerMixin):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    __tablename__ = 'departments'

    id = sa.Column(sa.Integer,
                   autoincrement=True,
                   primary_key=True,
                   name='id')
    author = sa.Column(sa.Integer,
                       sa.ForeignKey('users.id'))
    title = sa.Column(sa.String,
                      nullable=True)
    chief = sa.Column(sa.Integer,
                      sa.ForeignKey('users.id'))
    members = sa.Column(sa.String,
                        nullable=True)
    email = sa.Column(sa.String,
                      sa.ForeignKey('users.email'))
    user = orm.relation('User', foreign_keys='Departments.author')

