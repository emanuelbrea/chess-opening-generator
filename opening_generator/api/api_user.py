from flask import Blueprint, request, jsonify

from opening_generator.exceptions import InvalidRequestException
from opening_generator.services.user_service import user_service

user_bp = Blueprint('user', __name__, url_prefix='/user')


@user_bp.route('/', methods=["POST"])
def create_user():
    body = request.json

    email = body.get('email')
    first_name = body.get('first_name')

    if not email:
        raise InvalidRequestException(description="Missing email")

    if not first_name:
        raise InvalidRequestException(description=f"Missing first name.")

    user_service.create_user(first_name=first_name, email=email)
    return jsonify(message="User created correctly", success=True), 201
