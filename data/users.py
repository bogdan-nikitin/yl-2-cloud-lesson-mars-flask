import sqlalchemy as sa
import datetime
import sqlalchemy.orm as orm
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from .db_session import SqlAlchemyBase
from sqlalchemy_serializer import SerializerMixin


class User(SqlAlchemyBase, UserMixin, SerializerMixin):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    __tablename__ = 'users'

    id = sa.Column(sa.Integer,
                   primary_key=True,
                   autoincrement=True,
                   name='id')
    surname = sa.Column(sa.String,
                        nullable=True)
    name = sa.Column(sa.String,
                     nullable=True)
    age = sa.Column(sa.Integer,
                    nullable=True)
    position = sa.Column(sa.Integer,
                         nullable=True)
    speciality = sa.Column(sa.String,
                           nullable=True)
    address = sa.Column(sa.String,
                        nullable=True)
    email = sa.Column(sa.String,
                      unique=True,
                      index=True)
    hashed_password = sa.Column(sa.String)
    modified_date = sa.Column(sa.DateTime,
                              default=datetime.datetime.now)
    jobs = orm.relation('Jobs',
                        back_populates='user',
                        foreign_keys='Jobs.author')
    departments = orm.relation('Departments',
                               back_populates='user',
                               foreign_keys='Departments.author')
    city_from = sa.Column(sa.String, nullable=True)

    def __repr__(self):
        return f'<Colonist> {self.id} {self.surname} {self.name}'

    def set_password(self, password):
        self.hashed_password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.hashed_password, password)
