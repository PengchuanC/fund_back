import warnings

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_cache import Cache

from back_server.config import config


warnings.filterwarnings("ignore")
db = SQLAlchemy()
cache = Cache(with_jinja2_ext=False)


def create_app(config_name):
    app = Flask(__name__)
    CORS(app, supports_credentials=True)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    db.init_app(app)
    cache.init_app(app)

    from .app.routes import main as blue
    from .app.routes.news import news
    app.register_blueprint(blue)
    app.register_blueprint(news, url_prefix="/api/news")

    from .app.routes.apiv1 import rest
    app.register_blueprint(rest, url_prefix="/api/v1/news")

    return app
