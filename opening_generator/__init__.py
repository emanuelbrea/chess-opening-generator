import logging

from flask import Flask


def create_app(test_config=None):
    logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(name)s - %(asctime)s - %(message)s')
    app = Flask(__name__, instance_relative_config=True)

    if test_config is None:
        app.config.from_object('config.DevConfig')
    else:
        app.config.from_mapping(test_config)

    from opening_generator.db import init_db, db_session
    init_db()

    from opening_generator.api.api_eco import eco_bp
    from opening_generator.api.api_repertoire import repertoire_bp
    from opening_generator.api.api_position import pos_bp
    from opening_generator.api.api_user import user_bp
    app.register_blueprint(eco_bp)
    app.register_blueprint(repertoire_bp)
    app.register_blueprint(pos_bp)
    app.register_blueprint(user_bp)

    from opening_generator.exceptions import InvalidRequestException
    from opening_generator.exceptions import handle_invalid_request_exception
    app.register_error_handler(InvalidRequestException, handle_invalid_request_exception)

    @app.teardown_appcontext
    def shutdown_session(exception=None):
        db_session.remove()

    @app.after_request
    def after_request(response):
        header = response.headers
        header['Access-Control-Allow-Origin'] = '*'
        header['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, PATCH, OPTIONS'
        header['Access-Control-Allow-Headers'] = "*"
        return response

    return app
