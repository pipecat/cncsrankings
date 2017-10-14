from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_cache import Cache
from config import config

db = SQLAlchemy()
cache = Cache(config={
                    'CACHE_TYPE': 'simple',      
                })

def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    cache.init_app(app)

    db.init_app(app)

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from .api_1_0 import api as api_blueprint
    app.register_blueprint(api_blueprint, url_prefix='/api/v1.0')

    return app