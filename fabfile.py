# -*- coding: utf-8 -*-

from collections import defaultdict

from fabric.api import run, env, execute, task, cd, settings


env.roledefs = {
    'root@qa': ['root@newbuy-qa-wechat01'],
    'root@prod': ['root@newbuy-prod-wechat01'],
    'wechat@qa': ['wechat@newbuy-qa-wechat01'],
    'wechat@prod': ['wechat@newbuy-prod-wechat01']
}
env.key_filename = '~/.ssh/id_rsa'

level_map = defaultdict(lambda: [], {
    'master': ['prod'],
    'dev': ['qa']
})

remote_path = 'git@newbuy-dev:common/wechat.git'
code_dir = '/home/wechat/service'


@task
def ship(branch, commit):
    root_roles = ['root@%s' % level for level in level_map[branch]]
    user_roles = ['wechat@%s' % level for level in level_map[branch]]

    # 0. Local jobs
    print 'Start local jobs...'

    if root_roles and user_roles:
        # 1. Pre-deploy
        print 'Start deploying.....'

        # 2. Deploy
        sync_result = execute(sync_repo, remote_path, commit, code_dir, roles=user_roles)
        if check_all_success(sync_result):
            # Restart service
            reload_result = execute(reload_service, roles=root_roles)
            if check_all_success(reload_result):
                if run_test():
                    print 'Awesome!'
                    return_code = 0
                else:
                    print 'Fail to pass test!'
                    return_code = 13
            else:
                print 'Fail to reload service!'
                return_code = 12
        else:
            print 'Fail to sync code!'
            return_code = 11

        # 3. Post-deploy
        if return_code != 0:
            print 'No good! Start rolling back!'
            # Rollback
            sync_result2 = {}
            for host, info in sync_result.iteritems():
                if info['old_commit']:
                    sync_result2.update(execute(sync_repo, remote_path, info['old_commit'], code_dir, host=host))
                else:
                    print 'No commit to rollback on %s' % host
            if check_all_success(sync_result2):
                # Restart service
                reload_result = execute(reload_service, roles=root_roles)
                if check_all_success(reload_result):
                    if run_test():
                        print 'Rollback: OK!'
                    else:
                        print 'Rollback: Fail to pass test!'
                        return_code = 23
                else:
                    print 'Rollback: Fail to reload service!'
                    return_code = 22
            else:
                print 'Rollback: Fail to sync code!'
                return_code = 21
    else:
        return_code = 0
    exit(return_code)


def sync_repo(remote, commit, directory):
    with cd(directory):
        with settings(warn_only=True):
            r1 = run('git rev-parse HEAD')
            if r1.failed:
                print 'Fail to parse HEAD!'
                return {'error': 1, 'old_commit': ''}
            r2 = run('git reset --hard && '
                     'git clean -fdx && '
                     'git remote set-url origin %s && '
                     'git fetch origin && '
                     'git checkout %s' % (remote, commit))
            if r2.failed:
                return {'error': 2, 'old_commit': r1.stdout}
            else:
                return {'error': 0, 'old_commit': r1.stdout}


def reload_service():
    with settings(warn_only=True):
        result = run('supervisorctl restart wechat:')
        if result.failed:
            return {'error': 1}
        else:
            return {'error': 0}


def check_all_success(result):
    return sum([p['error'] for p in result.values()]) == 0


def run_test():
    # Do nothing
    return True
