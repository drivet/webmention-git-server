import os
import logging

from flask import Flask
from webmention.webmention import webmention_bp


def get_root():
    if 'WEBMENTION_ROOT' in os.environ:
        return os.environ['WEBMENTION_ROOT']
    else:
        my_path = os.path.abspath(os.path.dirname(__file__))
        return os.path.join(my_path, '../run')


app = Flask(__name__)
app.config.from_json(get_root() + '/settings.json')
app.register_blueprint(webmention_bp, url_prefix='/')
app.logger.setLevel(logging.INFO)
