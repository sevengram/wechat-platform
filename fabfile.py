from fabric.api import *
from fabric.operations import put
from fabric.contrib.project import rsync_project
import datetime
import uuid

# env.hosts = ['iscls']
# env.user = 'web'
# env.use_ssh_config = True
# env.key_filename = '~/.ssh/id_rsa'
env.colorize_errors = True


def deploy(name):
    print "Hello %s" % name

# @task(alias='dc')
# def deploy_compiled_code():
#     rsync_project('/home/web/projects/iscls', exclude=['.DS_Store', '.idea', '__pycache__',
#                                                        '.git', '.gitignore',
#                                                        '.sass-cache', 'compass',
#                                                        'bower_components',
#                                                        '*.pyc', 'fabfile.py', 'simple_db.bin'])
#
#
# @task(alias='i')
# def install_python_library():
#     put('meta/dependency/python/requirements.txt', '.')
#     with prefix('workon web'):
#         run('pip install -r requirements.txt')
#     run('rm requirements.txt')
#
# @task(alias='dn')
# def deploy_nginx_site_config():
#     put('meta/dependency/nginx/nginx.conf', '/etc/nginx/', use_sudo=True)
#     put('meta/dependency/nginx/metaroll.conf', '/etc/nginx/sites-enabled/', use_sudo=True)
#
# @task(alias='rn')
# def restart_nginx():
#     sudo('service nginx restart')
#
# @task(alias='ds')
# def deploy_supervisor_config():
#     put('meta/dependency/supervisor/iscls.conf', '/etc/supervisor/conf.d/', use_sudo=True)
#
# @task(alias='rs')
# def restart_supervisor():
#     sudo('supervisorctl reread')
#     sudo('supervisorctl update')
#     sudo('supervisorctl restart iscls')
#
# @task(alias='ccp')
# def compile_compass():
#     local('compass compile compass')
#
#
# @task(alias='dds')
# def deploy_database_script():
#     put('meta/service/database_backup.py', 'projects/iscls/metaroll/')
#
#
# @task(alias='bd')
# def backup_database():
#     today = str(datetime.date.today())
#     suffix = str(uuid.uuid4())[:5]
#     get('projects/iscls/metaroll/simple_db.bin', '~/backup/db-{}-{}.bin'.format(today, suffix))
#
#
# @task(alias='sd')
# def restore_database():
#     local('ls')
