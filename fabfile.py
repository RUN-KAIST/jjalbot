from fabric import task
import os


DEPLOY_HOST = 'run.kaist.ac.kr'
DEPLOY_AUTH = os.environ.get('DEPLOY_AUTH')
DEPLOY_USER = os.environ.get('DEPLOY_USER')
DEPLOY_PORT = os.environ.get('DEPLOY_PORT')
DEPLOY_KEY = os.environ.get('DEPLOY_KEY')

PROJECT_HOME = '$HOME/jjalbot'
ANACONDA_BIN = '$HOME/anaconda3/bin'
POETRY_BIN = '$HOME/.poetry/bin'
SUDO_PASS = os.environ.get('SUDO_PASS')

DEPLOY_CONFIG = {
    'host': DEPLOY_HOST,
    'user': DEPLOY_USER,
    'port': DEPLOY_PORT,
    'connect_kwargs': {
        DEPLOY_AUTH: DEPLOY_KEY
    }
}


@task(hosts=[DEPLOY_CONFIG])
def hello(c):
    c.run('echo hello')


def _update(c, branch='master'):
    c.run('git fetch -p origin')
    c.run('git checkout {}'.format(branch))
    c.run('git merge origin/{}'.format(branch))
    c.run('{}/poetry install -E pgsql --no-dev'.format(POETRY_BIN))


@task(hosts=[DEPLOY_CONFIG])
def update(c, branch='master'):
    with c.cd(PROJECT_HOME):
        with c.prefix('source {}/activate jjalbot'.format(ANACONDA_BIN)):
            _update(c, branch)


@task(hosts=[DEPLOY_CONFIG])
def check(c, branch='master'):
    with c.cd(PROJECT_HOME):
        with c.prefix('source {}/activate jjalbot'.format(ANACONDA_BIN)):
            _update(c, branch)
            c.run('./manage.py check --deploy --fail-level WARNING --settings=jjalbot.settings.production')


@task(hosts=[DEPLOY_CONFIG])
def deploy(c, branch='master'):
    with c.cd(PROJECT_HOME):
        with c.prefix('source {}/activate jjalbot'.format(ANACONDA_BIN)):
            _update(c, branch)
            c.run('./manage.py migrate --noinput --settings=jjalbot.settings.production')
            c.run('./manage.py collectstatic --noinput --settings=jjalbot.settings.production')

    c.sudo('reload jjalbot', password=SUDO_PASS)
    c.sudo('/etc/init.d/celeryd restart', password=SUDO_PASS)
