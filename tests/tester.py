from pprint import pprint
import contextlib
from requests import get, put, post, delete

SERVER = 'http://127.0.0.1:5000/'


class WrongResultException(Exception):
    def __init__(self, expected, got):
        super().__init__(f'Error. Expected {expected}, got {got}')


def from_server(action):
    def execute_action(address, params=None):
        return action(f'{SERVER}{address}', json=params).json()
    return execute_action


@contextlib.contextmanager
def managed_job(params=None):
    jobs_id = None
    try:
        jobs_id = 999
        request_params = {
            'job': 'Test post correct',
            'team_leader': 1,
            'work_size': 15,
            'categories_levels': '1',
            'is_finished': True,
            'jobs_id': jobs_id
        }
        if params:
            for k, v in params.items():
                request_params[k] = v
        server_post('/api/v2/jobs/', request_params)
        yield jobs_id
    finally:
        delete(f'{SERVER}/api/v2/jobs/{jobs_id}')


@contextlib.contextmanager
def managed_user(params=None):
    user_id = 999
    try:
        request_params = {
            'surname': 'Ivanov',
            'name': 'Ivan',
            'age': 20,
            'position': 'Colonist',
            'speciality': 'Specialist',
            'address': 'module_1',
            'password': '12345',
            'email': f'test{user_id}@mars.org',
            'user_id': user_id
        }
        if params:
            for k, v in params.items():
                request_params[k] = v
        a = server_post('/api/v2/users', request_params)
        yield user_id
    finally:
        server_delete(f'/api/v2/users/{user_id}')


def print_request_json_result(func):
    def new_func(address, params=None):
        print(from_server(func)(address, params))
    new_func.__name__ = func.__name__
    return new_func


def jobs_list():
    return get(f'{SERVER}/api/jobs').json()


def users_list():
    return get(f'{SERVER}/api/v2/users').json()


def print_jobs():
    try:
        print(f'Jobs: {jobs_list()}')
    except Exception as e:
        print(f'Could not get the list of jobs. An error occurred: {e}')


def print_users():
    try:
        print(f'Users: {users_list()}')
    except Exception as e:
        print(f'Could not get the list of users. An error occurred: {e}')


def create_tester(after=None):
    funcs = []
    errors_count = 0
    failed_funcs = []

    def test(func=None):
        nonlocal funcs, errors_count, failed_funcs

        if func is None:
            print(f'TESTS FILE: {__file__}')
            print('Starting tests...')
            print()

            for test_function in funcs:
                test_function()

            print('Tests completed')
            if errors_count:
                print(f'{errors_count} errors occurred in '
                      f'{", ".join(failed_funcs)}')
            else:
                print('No errors occurred')
            errors_count = 0
            return

        def test_func():
            nonlocal errors_count, failed_funcs
            print(f'Running {func.__name__}...')
            try:
                func()
            except Exception as e:
                errors_count += 1
                failed_funcs += [func.__name__]
                print(f'During the execution of {func.__name__}, '
                      f'an error occurred: {e}')
                print(f'{func.__name__} execution is stopped')
            else:
                print(f'Successful completion: {func.__name__}')
            if after:
                after()
            print()

        funcs += [test_func]

    return test


def test_expected(expected):

    def test_expected_func(func):
        def new_func():
            result = func()
            if expected not in result:
                raise WrongResultException(expected, ', '.join(result.keys()))
            return result

        new_func.__name__ = func.__name__
        return new_func

    return test_expected_func


def print_result(func):

    def decorated():
        result = func()
        pprint(result)
        return result

    decorated.__name__ = func.__name__
    return decorated


test_correct = test_expected('success')
test_incorrect = test_expected('error')
test_server_error = test_expected('message')

print_get = print_request_json_result(get)
print_post = print_request_json_result(post)
print_delete = print_request_json_result(delete)
print_put = print_request_json_result(put)

server_get = from_server(get)
server_post = from_server(post)
server_put = from_server(put)
server_delete = from_server(delete)
