import chess
from flask import Blueprint, request, jsonify

from opening_generator.api.api_position import get_board_by_fen, get_position_by_board
from opening_generator.exceptions import InvalidRequestException
from opening_generator.models import User, Style, Position
from opening_generator.services.user_service import user_service

user_bp = Blueprint("user", __name__, url_prefix="/api/user")


@user_bp.route("", methods=["POST"])
def create_user():
    body = request.json

    email = body.get("email")
    first_name = body.get("first_name")
    last_name = body.get("last_name")

    if not email:
        raise InvalidRequestException(description="Missing email")

    if not first_name:
        raise InvalidRequestException(description="Missing first name")

    if not last_name:
        raise InvalidRequestException(description="Missing last name")

    user_service.create_user(first_name=first_name, last_name=last_name, email=email)
    return jsonify(message="User created correctly", success=True), 201


@user_bp.route("", methods=["PUT"])
def update_user():
    body = request.json

    if not body:
        raise InvalidRequestException(description="Missing style")

    user: User = user_service.get_user()

    first_name = body.get("first_name")
    last_name = body.get("last_name")
    age = body.get("age")
    playing_since = body.get("playing_since")

    user_service.update_user(
        user=user,
        first_name=first_name,
        last_name=last_name,
        age=age,
        playing_since=playing_since,
    )

    popularity = body.get("popularity")
    fashion = body.get("fashion")
    risk = body.get("risk")
    rating = body.get("rating")

    if None not in [popularity, fashion, risk, rating]:
        user_service.update_user_style(
            user=user, popularity=popularity, fashion=fashion, risk=risk, rating=rating
        )
    return jsonify(message="User updated correctly", success=True), 200


@user_bp.route("", methods=["GET"])
def get_user():
    user: User = user_service.get_user()
    style: Style = user.style
    data = dict(
        user=dict(
            first_name=user.first_name,
            last_name=user.last_name,
            email=user.email,
            age=user.age,
            playing_since=user.playing_since,
        ),
        style=dict(
            popularity=style.popularity,
            fashion=style.fashion,
            risk=style.risk,
            rating=style.rating,
        ),
    )

    return jsonify(message="User retrieved correctly", data=data, success=True), 200


@user_bp.route("/favorite", methods=["PUT"])
def add_favorite_move():
    body = request.json

    if not body:
        raise InvalidRequestException(description="Missing request body")

    move = body.get("move")

    if not move:
        raise InvalidRequestException(description="Missing favorite move")
    board: chess.Board = get_board_by_fen(body)

    user: User = user_service.get_user()
    position: Position = get_position_by_board(board)

    user_service.add_favorite_move(user=user, position=position, move_san=move)

    return jsonify(message="Favorite move added correctly", data={}, success=True), 200


@user_bp.route("/message", methods=["POST"])
def save_user_message():
    body = request.json

    if not body:
        raise InvalidRequestException(description="Missing request body")

    message = body.get("message")
    email = body.get("email")
    name = body.get("name")
    rating = body.get("rating")

    if None in [message, email, name]:
        raise InvalidRequestException(description="Missing mandatory fields")

    user_service.save_user_message(
        message=message, email=email, name=name, rating=rating
    )

    return jsonify(message="User message saved correctly", data={}, success=True), 200
