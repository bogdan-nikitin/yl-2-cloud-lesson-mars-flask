import sqlalchemy as sa
import sqlalchemy.orm as orm
from .db_session import SqlAlchemyBase


association_table = sa.Table('association', SqlAlchemyBase.metadata,
                             sa.Column('jobs',
                                       sa.Integer,
                                       sa.ForeignKey('jobs.id')),
                             sa.Column('category',
                                       sa.Integer,
                                       sa.ForeignKey('category.id')))


class Category(SqlAlchemyBase):
    __tablename__ = 'category'
    id = sa.Column(sa.Integer, autoincrement=True, primary_key=True)
    level = sa.Column(sa.Integer, nullable=True)
