from flask import Flask
from logging.config import dictConfig

app = Flask(__name__)
app.config.from_object("standards.config.Config")
dictConfig(app.config.get('LOGGING_CONFIG', {}))

from standards.api import api_bp  # noqa
app.register_blueprint(api_bp, url_prefix='/api/')
