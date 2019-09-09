from fabric import task

image = 'desmondrivet/webmention-git-server:master'
testvolume = '/var/local/webmention-test'
volume = '/var/local/webmention'
name = 'webmention-git-server'
testport = 3131
port = 3132


@task
def deploytest(c):
    c.run(f'docker pull {image}')
    c.run(f'docker stop {name}', warn=True)
    c.run(f'docker run --name {name} -p {testport}:3031 ' +
          f'-v {testvolume}:{volume} --rm -d {image}')


@task
def deploy(c):
    c.run(f'docker pull {image}')
    c.run(f'docker stop {name}', warn=True)
    c.run(f'docker run --name {name} -p {port}:3031 ' +
          f'-v {volume}:{volume} --rm -d {image}')
