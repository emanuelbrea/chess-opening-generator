import logging

from flask import jsonify


class InvalidRequestException(Exception):
    def __init__(self, description):
        super(InvalidRequestException, self).__init__(description)
        self.description = description


class UserException(InvalidRequestException):
    def __init__(self, description):
        super(UserException, self).__init__(description)
        self.description = description


def handle_invalid_request_exception(error: InvalidRequestException):
    logging.getLogger(__name__).exception(error.description)
    return (
        jsonify(
            message="Invalid request", description=error.description, success=False
        ),
        400,
    )
