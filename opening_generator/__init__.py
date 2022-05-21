from flask import Flask

from opening_generator.api import api_position
from opening_generator.db import init_db, db_session


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)

    if test_config is None:
        app.config.from_object('config.DevConfig')
    else:
        app.config.from_mapping(test_config)

    with app.app_context():
        init_db()

    app.register_blueprint(api_position.pos)

    return app

    @app.teardown_appcontext
    def shutdown_session(exception=None):
        db_session.remove()
