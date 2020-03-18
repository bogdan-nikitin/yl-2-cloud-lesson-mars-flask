from tests.tester import *


tester = create_tester()


@tester
@test_correct
@print_result
def test_put_correct():
    params = {
        'surname': 'Ivanov edited',
        'name': 'Ivan',
        'age': 20,
        'position': 'Colonist',
        'speciality': 'Specialist',
        'address': 'module_1',
        'password': '12345',
        'email': 'ivanov_edited@mars.org'
    }
    with managed_user() as user_id:
        print_get(f'/api/v2/users/{user_id}')
        result = server_put(f'/api/v2/users/{user_id}', params)
        print_get(f'/api/v2/users/{user_id}')
    return result


@tester
@test_server_error
@print_result
def test_delete_correct():
    id_for_test = 999
    params = {
        'surname': 'Ivanov',
        'name': 'Ivan',
        'age': 20,
        'position': 'Colonist',
        'speciality': 'Specialist',
        'address': 'module_1',
        'password': '12345',
        'email': 'ivanov1@mars.org',
        'id': id_for_test
    }
    server_post('/api/v2/users/', params)
    return server_delete(f'/api/v2/users/{id_for_test}')


@tester
@test_incorrect
@print_result
def test_delete_wrong_id():
    id_for_test = -1
    return server_delete(f'/api/v2/users/{id_for_test}')


@tester
@test_expected('users')
@print_result
def test_post_correct():
    params = {
        'surname': 'Ivanov',
        'name': 'Ivan',
        'age': 20,
        'position': 'Colonist',
        'speciality': 'Specialist',
        'address': 'module_1',
        'password': '12345',
        'email': 'ivanov@mars.org'
    }
    server_post('/api/v2/users/', params)
    return server_get('/api/v2/users')


@tester
@test_incorrect
@print_result
def test_post_wrong_arg_type():
    params = {
        'surname': 'Ivanov',
        'name': 'Ivan',
        'age': 'twenty',
        'position': 'Colonist',
        'speciality': 'Specialist',
        'address': 'module_1',
        'password': '12345',
        'email': 'ivanov@mars.org'
    }
    server_post('/api/v2/users/', params)
    return server_get('/api/v2/users/')


@tester
@test_expected('user')
@print_result
def test_get_one_user():
    return server_get('/api/v2/users/1')


@tester
@test_expected('users')
@print_result
def test_get_users():
    return server_get('/api/v2/users')


@tester
@test_server_error
@print_result
def test_get_wrong_id():
    return server_get('/api/v2/users/5')


tester()
