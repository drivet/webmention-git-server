import os
from fabric import task
from fabric.transfer import Transfer

branch = os.environ['CIRCLE_BRANCH']

if branch == 'master':
    port = 3132
else:
    port = 3131

os.environ['PORT'] = port

image = f'desmondrivet/webmention-git-server:{branch}'
name = 'webmention-git-server'

env = ['ME', 'GITHUB_REPO', 'GITHUB_USERNAME', 'GITHUB_PASSWORD',
       'WEBMENTION_FOLDER']

extra = ['CIRCLE_BRANCH', 'PORT']


def all_env_cmd():
    return ' && '.join([env_cmd(e) for e in env + extra])


def env_cmd(e):
    return 'export ' + e + '="' + os.environ[e] + '"'


@task(hosts=["dcr@desmondrivet.com"])
@task
def deploy(c):
    Transfer(c).put('docker-compose.yml', '/tmp')
    c.run(f'docker pull {image}')
    c.run(f'{all_env_cmd()} && ' +
          f'docker-compose -f /tmp/docker-compose.yml up -d')
