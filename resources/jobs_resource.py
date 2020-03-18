from flask_restful import abort, Resource
from data import db_session
from data.jobs import Jobs
from flask import jsonify
from parsers.jobs_parser import post_parser, put_parser
from general import get_category
import datetime


RULES = ('-user', '-categories', 'categories_levels')


def get_categories(categories_levels):
    return list(map(get_category, categories_levels))


def abort_if_job_not_found(job_id):
    session = db_session.create_session()
    jobs = session.query(Jobs).get(job_id)
    if not jobs:
        abort(404, message=f'Job {job_id} not found')


def set_collaborators(jobs, args):
    collaborators = args['collaborators']
    if jobs.team_leader in collaborators:
        raise Exception("Team leader can't be collaborator")
    jobs.collaborators = ','.join(map(str, collaborators))


def set_categories(jobs, args, session):
    jobs.categories.clear()
    categories = get_categories(args['categories_levels'])
    categories = [session.merge(category) for category in categories]
    jobs.categories.extend(categories)
    session.commit()


class JobsResource(Resource):
    @staticmethod
    def get(jobs_id):
        abort_if_job_not_found(jobs_id)
        session = db_session.create_session()
        job = session.query(Jobs).get(jobs_id)
        return jsonify({'jobs': job.to_dict(rules=RULES)})

    @staticmethod
    def delete(jobs_id):
        abort_if_job_not_found(jobs_id)
        session = db_session.create_session()
        jobs = session.query(Jobs).get(jobs_id)
        session.delete(jobs)
        session.commit()
        return jsonify({'success': 'OK'})

    @staticmethod
    def put(jobs_id):
        abort_if_job_not_found(jobs_id)
        args = put_parser.parse_args()
        session = db_session.create_session()
        jobs = session.query(Jobs).get(jobs_id)
        jobs.id = args.get('jobs_id', jobs.id)
        jobs.team_leader = args.get('team_leader', jobs.team_leader)
        jobs.job = args.get('job', jobs.job)
        jobs.work_size = args.get('work_size', jobs.work_size)
        jobs.start_date = args.get('start_date', jobs.start_date)
        if args.get('collaborators'):
            try:
                set_collaborators(jobs, args)
            except Exception as e:
                return jsonify({'error': str(e)})
        is_finished = args.get('is_finished')
        if is_finished:
            if not jobs.is_finished and is_finished:
                jobs.end_date = datetime.datetime.now()
            elif jobs.is_finished and not is_finished:
                jobs.end_date = None
            jobs.is_finished = is_finished
        jobs.end_date = args.get('end_date', jobs.end_date)
        if args.get('categories_levels'):
            set_categories(jobs, args, session)
        session.commit()
        return jsonify({'success': 'OK'})


class JobsListResource(Resource):
    @staticmethod
    def get():
        session = db_session.create_session()
        jobs = session.query(Jobs).all()
        return jsonify(
            {
                'jobs': [item.to_dict(rules=RULES) for item in jobs]
            }
        )

    @staticmethod
    def post():
        args = post_parser.parse_args()
        session = db_session.create_session()
        jobs = Jobs(
             team_leader=args['team_leader'],
             job=args['job'],
             work_size=args['work_size'],
             start_date=args.get('start_date', datetime.datetime.now()),
             end_date=args.get('end_date')
        )
        jobs.author = jobs.team_leader
        jobs_id = args.get('jobs_id')
        if jobs_id:
            jobs.id = jobs_id
        if not jobs.end_date and jobs.is_finished:
            jobs.end_date = datetime.datetime.now()
        if args.get('collaborators'):
            try:
                set_collaborators(jobs, args)
            except Exception as e:
                return jsonify({'error': str(e)})
        else:
            jobs.collaborators = ''
        set_categories(jobs, args, session)
        session.add(session.merge(jobs))
        session.commit()
        return jsonify({'success': 'OK'})
