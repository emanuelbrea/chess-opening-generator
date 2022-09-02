from flask import Blueprint, request, jsonify

from opening_generator.exceptions import InvalidRequestException
from opening_generator.models import User
from opening_generator.services.user_service import user_service

user_bp = Blueprint('user', __name__, url_prefix='/api/user')


@user_bp.route('', methods=["POST"])
def create_user():
    body = request.json

    email = body.get('email')
    first_name = body.get('first_name')

    if not email:
        raise InvalidRequestException(description="Missing email")

    if not first_name:
        raise InvalidRequestException(description="Missing first name")

    user_service.create_user(first_name=first_name, email=email)
    return jsonify(message="User created correctly", success=True), 201


@user_bp.route('/style', methods=["POST"])
def create_user_style():
    user: User = user_service.get_user()
    body = request.json

    popularity = body.get('popularity')
    fashion = body.get('fashion')
    risk = body.get('risk')
    rating = body.get('rating')

    if None in [popularity, fashion, risk, rating]:
        raise InvalidRequestException(description="Missing style")

    user_service.create_user_style(user=user, popularity=popularity, fashion=fashion, risk=risk, rating=rating)
    return jsonify(message="User style created correctly", success=True), 201
