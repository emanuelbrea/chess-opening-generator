import logging

from flask import Flask


def create_app(test_config=None):
    logging.basicConfig(level=logging.INFO, format='%(levelname)s %(asctime)s %(message)s')
    app = Flask(__name__, instance_relative_config=True)

    if test_config is None:
        app.config.from_object('config.DevConfig')
    else:
        app.config.from_mapping(test_config)

    from opening_generator.db import init_db, db_session
    with app.app_context():
        init_db()

    from opening_generator.api.api_move import move_bp
    from opening_generator.api.api_eco import eco
    app.register_blueprint(move_bp)
    app.register_blueprint(eco)

    from opening_generator.tree.opening_tree import OpeningTree
    opening_tree = OpeningTree()
    opening_tree.retrieve_initial_position()

    return app

    @app.teardown_appcontext
    def shutdown_session(exception=None):
        db_session.remove()
