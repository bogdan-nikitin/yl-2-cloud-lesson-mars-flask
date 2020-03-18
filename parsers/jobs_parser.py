from flask_restful import reqparse
import datetime
from general import UserArgType


post_parser = reqparse.RequestParser()
post_parser.add_argument('jobs_id', type=int)
post_parser.add_argument('team_leader', required=True, type=UserArgType)
post_parser.add_argument('job', required=True)
post_parser.add_argument('work_size', required=True, type=int)
post_parser.add_argument('collaborators', type=UserArgType, action='append')
post_parser.add_argument('start_date',
                         type=datetime.datetime,
                         default=datetime.datetime.now)
post_parser.add_argument('end_date', type=datetime.datetime)
post_parser.add_argument('is_finished',
                         required=True,
                         type=bool,
                         store_missing=False)
post_parser.add_argument('categories_levels',
                         required=True,
                         type=int,
                         action='append')

put_parser = reqparse.RequestParser()
put_parser.add_argument('team_leader', type=UserArgType, store_missing=False)
put_parser.add_argument('job', store_missing=False)
put_parser.add_argument('work_size', type=int, store_missing=False)
put_parser.add_argument('collaborators',
                        type=UserArgType,
                        action='append',
                        store_missing=False)
put_parser.add_argument('start_date',
                        type=datetime.datetime,
                        store_missing=False)
put_parser.add_argument('end_date',
                        type=datetime.datetime,
                        store_missing=False)
put_parser.add_argument('is_finished', type=bool, store_missing=False)
put_parser.add_argument('categories_levels',
                        type=int,
                        action='append',
                        store_missing=False)
