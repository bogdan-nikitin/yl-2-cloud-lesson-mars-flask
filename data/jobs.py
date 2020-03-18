import sqlalchemy as sa
import sqlalchemy.orm as orm
import datetime
from .db_session import SqlAlchemyBase
from sqlalchemy_serializer import SerializerMixin


class Jobs(SqlAlchemyBase, SerializerMixin):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    __tablename__ = 'jobs'

    id = sa.Column(sa.Integer,
                   autoincrement=True,
                   primary_key=True,
                   name='id')
    author = sa.Column(sa.Integer,
                       sa.ForeignKey('users.id'),
                       nullable=True)
    team_leader = sa.Column(sa.Integer,
                            sa.ForeignKey('users.id'))
    job = sa.Column(sa.String, nullable=True)
    work_size = sa.Column(sa.Integer, nullable=True)
    collaborators = sa.Column(sa.String, nullable=True)
    start_date = sa.Column(sa.DateTime,
                           nullable=True,
                           default=datetime.datetime.now)
    end_date = sa.Column(sa.DateTime, nullable=True)
    is_finished = sa.Column(sa.Boolean, nullable=True, default=False)
    user = orm.relation('User', foreign_keys='Jobs.author')
    categories = orm.relation('Category',
                              secondary='association',
                              backref='Jobs')

    def categories_levels(self):
        return [category.level for category in self.categories]

    def __repr__(self):
        return f'<Job> {self.job}'
