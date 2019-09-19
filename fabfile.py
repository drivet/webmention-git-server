import os
from fabric import task
from fabric.transfer import Transfer

image = 'desmondrivet/webmention-git-server:master'
name = 'webmention-git-server'
testport = 3131
port = 3132


env = ['ME', 'GITHUB_REPO', 'GITHUB_USERNAME', 'GITHUB_PASSWORD',
       'WEBMENTION_FOLDER']


def all_env_cmd():
    return ' && '.join([env_cmd(e) for e in env])


def env_cmd(e):
    return 'export ' + e + '="' + os.environ[e] + '"'


def docker_env_params():
    return ' '.join([f'-e {e}' for e in env])


@task(hosts=["dcr@desmondrivet.com"])
def deploytest(c):
    Transfer(c).put('docker-compose.yml', '/tmp')
    c.run(f'docker pull {image}')
    c.run(f'{all_env_cmd()} && ' +
          f'docker-compose -f /tmp/docker-compose.yml up -d')


@task
def deploy(c):
    c.run(f'docker pull {image}')
    c.run(f'docker stop {name}', warn=True)
    c.run(f'docker run --name {name} -p {port}:3031 ' +
          f'--rm -d {image}')
