from tests.tester import *


tester = create_tester()


@tester
@test_correct
@print_result
def test_put_correct():
    params = {
        'job': 'Test put correct',
        'team_leader': 1,
        'work_size': 15,
        'categories_levels': '1',
        'is_finished': True
    }
    with managed_job() as jobs_id:
        print_get(f'/api/v2/jobs/{jobs_id}')
        result = server_put(f'/api/v2/jobs/{jobs_id}', params)
        print_get(f'/api/v2/jobs/{jobs_id}')
    return result


@tester
@test_incorrect
@print_result
def test_put_wrong_id():
    return server_put('/api/v2/jobs/-1')


@tester
@test_server_error
@print_result
def test_put_wrong_args_types():
    params = {
        'job': 5,
        'team_leader': 'first',
        'work_size': 'fifteen',
        'collaborators': [1, 2],
        'categories_levels': [1, 2],
        'is_finished': 'True'
    }
    with managed_job() as jobs_id:
        print_get(f'/api/v2/jobs/{jobs_id}')
        result = server_put(f'/api/v2/jobs/{jobs_id}', params)
        print_get(f'/api/v2/jobs/{jobs_id}')
    return result


@tester
@test_server_error
@print_result
def test_delete_correct():
    id_for_test = 999
    params = {
        'job': 'Test delete',
        'team_leader': 1,
        'work_size': 15,
        'collaborators': '',
        'categories_levels': '1',
        'is_finished': True,
        'jobs_id': id_for_test
    }
    server_post('/api/v2/jobs/', params)
    return server_delete(f'/api/v2/jobs/{id_for_test}')


@tester
@test_incorrect
@print_result
def test_delete_wrong_id():
    id_for_test = -1
    return server_delete(f'/api/v2/jobs/{id_for_test}')


@tester
@test_expected('jobs')
@print_result
def test_post_correct():
    params = {
        'job': 'Test post correct',
        'team_leader': 1,
        'work_size': 15,
        'collaborators': '',
        'categories_levels': '1',
        'is_finished': True
    }
    server_post('/api/v2/jobs/', params)
    return server_get('/api/v2/jobs')


@tester
@test_server_error
@print_result
def test_post_wrongs_args_type():
    params = {
        'job': 5,
        'team_leader': 'first',
        'work_size': 'fifteen',
        'collaborators': [1, 2],
        'categories_levels': [1, 2],
        'is_finished': 'True'
    }
    return server_post('/api/v2/jobs/', params)


@tester
@test_expected('jobs')
@print_result
def test_get_one_jobs():
    return server_get('/api/v2/jobs/1')


@tester
@test_expected('jobs')
@print_result
def test_get_jobs():
    return server_get('/api/v2/jobs')


@tester
@test_incorrect
@print_result
def test_get_wrong_id():
    return server_get('/api/v2/jobs/-1')


tester()
