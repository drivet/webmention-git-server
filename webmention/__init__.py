import logging

from flask import Flask
from webmention.webmention import webmention_bp


app = Flask(__name__)
app.register_blueprint(webmention_bp, url_prefix='/')
app.logger.setLevel(logging.INFO)
