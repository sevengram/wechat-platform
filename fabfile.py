# -*- coding: utf-8 -*-

from collections import defaultdict

from fabric.api import run, env, execute, task, cd


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
    # Do nothing

    if root_roles and user_roles:
        # 1. Pre-deploy
        # Do nothing

        # 2. Deploy
        old_commit_map = execute(sync_repo, remote_path, commit, code_dir, roles=user_roles)
        execute(reload_service, roles=root_roles)

        # 3. Post-deploy
        if run_test():
            print 'Awesome!'
        else:
            print 'No good! Start rolling back!'
            # Rollback
            for host, commit in old_commit_map.iteritems():
                execute(sync_repo, remote_path, commit, code_dir, host=host)
            execute(reload_service, roles=root_roles)
            if run_test():  # Re-test
                print 'Rollback OK!'
            else:
                print 'Danger!! Fail to rollback!'


def sync_repo(remote, commit, directory):
    with cd(directory):
        old_commit = run('git rev-parse HEAD')
        run('git reset --hard && git clean -fdx && git remote set-url origin %s' % remote)
        run('git fetch origin && git checkout %s' % commit)
        return old_commit


def reload_service():
    run('supervisorctl restart wechat:')


def run_test():
    # Do nothing
    return True