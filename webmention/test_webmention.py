import hashlib
from webmention import app
from webmention.webmention import commit_url

app.config['REPO_URL_ROOT'] = 'https://api.github.com/test'
app.config['WEBMENTION_FOLDER'] = 'webmentions_go_here'


def test_commit_url():
    with app.app_context():
        sourceUrl = 'http://example.com/source'
        targetUrl = 'http://target.com/stuff'

        url = commit_url(sourceUrl, targetUrl)

        sourceHash = hashlib.md5(sourceUrl.encode()).hexdigest()
        assert url == f'https://api.github.com/test/' + \
            f'webmentions_go_here/stuff/{sourceHash}.wm'
