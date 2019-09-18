import os
import hashlib
from webmention import app
from webmention.webmention import commit_url, process_webmention
from unittest.mock import patch, MagicMock


app.config['TESTING'] = True
os.environ['GITHUB_REPO'] = 'drivet/a_github_repo'
os.environ['WEBMENTION_FOLDER'] = 'webmentions_go_here'
os.environ['ME'] = 'http://thisisme.com'


def test_commit_url():
    with app.app_context():
        sourceUrl = 'http://example.com/source'
        targetUrl = 'http://target.com/stuff'

        url = commit_url(sourceUrl, targetUrl)

        sourceHash = hashlib.md5(sourceUrl.encode()).hexdigest()
        assert url == f'https://api.github.com/repos/drivet/a_github_repo/' + \
            f'contents/webmentions_go_here/stuff/{sourceHash}.wm'


def test_source_must_be_different_from_target():
    with app.app_context():
        client = app.test_client()
        rv = client.post('/', data={
            'source': 'http://example.com',
            'target': 'http://example.com',
        })
        assert rv.status_code == 400


def test_target_must_be_for_website():
    with app.app_context():
        client = app.test_client()
        rv = client.post('/', data={
            'source': 'http://example.com',
            'target': 'http://thisisnotme.com',
        })
        assert rv.status_code == 400


@patch('webmention.webmention.discoverEndpoint')
def test_target_must_support_webmentions(discover_mock):
    discover_mock.return_value = (200, None)
    with app.app_context():
        client = app.test_client()
        rv = client.post('/', data={
            'source': 'http://example.com',
            'target': 'http://thisisme.com',
        })
        assert rv.status_code == 400


@patch('webmention.webmention.discoverEndpoint')
@patch('webmention.webmention.queue')
def test_returns_202_when_successful(qmock, discover_mock):
    discover_mock.return_value = (200, 'http://webmention.com')
    qmock.return_value = MagicMock()
    with app.app_context():
        client = app.test_client()
        rv = client.post('/', data={
            'source': 'http://example.com',
            'target': 'http://thisisme.com',
        })
        assert rv.status_code == 202


@patch('webmention.webmention.mf2parse')
@patch('webmention.webmention.findMentions')
@patch('webmention.webmention.commit_file')
def test_process_webmention_commits_file(commit_mock, find_mock, mf2_mock):
    find_mock.return_value = {
        'status': 200,
        'refs': ['http://example.com/stuff']
    }

    class Response:
        pass
    r = Response()
    r.status_code = 201
    commit_mock.return_value = r

    mf2_mock.return_value = {'stuff': 'blah'}

    with app.app_context():
        process_webmention('http://commit_url.com',
                           'http://example.com',
                           'http://thisisme.com')
        contents = '{"sourceUrl": "http://example.com", "targetUrl": "http://thisisme.com", "parsedSource": {"stuff": "blah"}}'
        commit_mock.assert_called_with('http://commit_url.com', contents)
