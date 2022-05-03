from flask import Flask

from opening_generator.api import api_position
from opening_generator.pgn import Pgn


def create_app():
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev'
    )

    app.register_blueprint(api_position.pos)
    Pgn()

    return app
