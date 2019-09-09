from invoke import task


@task
def run(c):
    c.run('python -m main')


@task
def test(c):
    c.run('nosetests')


@task
def dlogin(c):
    c.run('echo "$DOCKER_PASS" | ' +
          'docker login --username $DOCKER_USER --password-stdin')


@task
def dbuild(c):
    c.run('docker image build -t ' +
          'desmondrivet/webmention-git-server:$CIRCLE_BRANCH .')


@task
def dpush(c):
    c.run('docker push desmondrivet/webmention-git-server:$CIRCLE_BRANCH')
