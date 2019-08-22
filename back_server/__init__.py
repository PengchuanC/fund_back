import warnings

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from back_server.config import config


warnings.filterwarnings("ignore")
db = SQLAlchemy()


def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    db.init_app(app)

    from .app.main import main as blue
    app.register_blueprint(blue)

    return app
