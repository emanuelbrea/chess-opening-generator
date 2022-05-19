from flask import Flask

from opening_generator.api import api_position
from opening_generator.db import init_db, db_session
from opening_generator.db.eco_code_dao import add_eco_codes
from opening_generator.db.user_dao import create_user
from opening_generator.pgn import Pgn


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)

    if test_config is None:
        app.config.from_object('config.Config')
    else:
        app.config.from_mapping(test_config)

    with app.app_context():
        init_db()

    app.register_blueprint(api_position.pos)

    # Pgn()

    # add_eco_codes()
    return app

    @app.teardown_appcontext
    def shutdown_session(exception=None):
        db_session.remove()
