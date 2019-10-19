import hashlib
import os
import json
from urllib.parse import urlparse
from github import Github, GithubException.UnknownObjectException

import mf2py
from flask import request, Response, Blueprint
from flask import current_app as app
from ronkyuu import findMentions, discoverEndpoint
from redis import Redis
from fakeredis import FakeStrictRedis
from rq import Queue

webmention_bp = Blueprint('webmention_bp', __name__)


@webmention_bp.route('/', methods=['POST'], strict_slashes=False)
def handle_root():
    source = request.form['source']
    target = request.form['target']

    if source == target:
        return Response(response='source URL is the same as target URL',
                        status=400)

    if not target.startswith(os.environ['ME']):
        return Response(response='webmentions not supported on target domain',
                        status=400)

    if not discoverEndpoint(target)[1]:
        return Response(response='target URL does not support webmentions',
                        status=400)

    q = queue()
    q.enqueue(process_webmention, source, target)
    return Response(status=202)


def queue():
    if app.config.get('TESTING', True):
        return Queue(is_async=False, connection=FakeStrictRedis())
    else:
        return Queue(connection=Redis.from_url(redis_url()))


def redis_url():
    return os.environ.get('REDIS_URL') or 'redis://'


def process_webmention(source, target):
    # find mention in source
    result = findMentions(source, target)

    if result['status'] != 200:
        raise Exception('error fetching source')

    if not result['refs']:
        raise Exception('target not found in source')

    parsed = mf2parse(source)
    webmention = {
        'sourceUrl': source,
        'targetUrl': target,
        'parsedSource': parsed
    }
    r = commit_file(commit_url(source, target), json.dumps(webmention))
    if r.status_code != 201:
        raise Exception(f'failed to post {commit_url} to github: ' +
                        f'{r.status_code}, {r.text}')


def commit_url(source, target):
    wmpath = webmention_path(source, target)
    if not wmpath.startswith('/'):
        wmpath = '/' + wmpath
    return repo_url_root() + wmpath


def repo_url_root():
    repo = os.environ['GITHUB_REPO']
    return f'https://api.github.com/repos/{repo}/contents'


def webmention_path(source, target):
    folder = webmention_folder(target)
    filename = hashlib.md5(source.encode()).hexdigest()
    return os.path.join(folder, filename + '.wm')


def webmention_folder(target):
    path = extract_path(target)
    if path.startswith('/'):
        path = path[1:]
    return os.path.join(os.environ['WEBMENTION_FOLDER'], path)


def extract_path(target):
    path = urlparse(target).path
    return path.rsplit('.', 1)[0]


def mf2parse(source):
    return mf2py.Parser(url=source).to_dict()


def commit_file(filename, content):
    g = Github(os.environ['GITHUB_USERNAME'], os.environ['GITHUB_PASSWORD'])
    repo = g.get_repo(reponame())
    try:
        contents = repo.get_contents(filename)
        repo.update_file(filename, "update of {filename}",
                         content, contents.sha)
    except GithubException.UnknownObjectException as e:
        pass
    
    return requests.put(url, auth=(os.environ['GITHUB_USERNAME'],
                                   os.environ['GITHUB_PASSWORD']),
                        data=json.dumps({'message': 'post to ' + url,
                                         'content': c}))

def reponame():
    user = os.environ['GITHUB_USERNAME']
    repo = os.environ['GITHUB_REPO']
    return f'{user}/{repo}'
