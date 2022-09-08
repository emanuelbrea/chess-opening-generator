import chess
from flask import Blueprint, jsonify, request

from opening_generator.api.api_position import (
    get_board_by_fen,
    get_position_by_board,
    get_color,
)
from opening_generator.exceptions import InvalidRequestException
from opening_generator.models import Position, User
from opening_generator.services.position_service import position_service
from opening_generator.services.repertoire_service import repertoire_service
from opening_generator.services.user_service import user_service

repertoire_bp = Blueprint("repertoire", __name__, url_prefix="/api/repertoire")


def get_request_arguments(args):
    move: str = args.get("move")

    board: chess.Board = get_board_by_fen(args)
    position: Position = get_position_by_board(board)

    color = get_color(args=args)

    return dict(move=move, color=color, position=position, depth=board.fullmove_number)


@repertoire_bp.route("", methods=["GET"])
def get_user_repertoire():
    user: User = user_service.get_user()
    args = get_request_arguments(request.args)

    moves = repertoire_service.get_repertoire_moves(
        args["position"], user, args["color"], args["depth"]
    )
    return (
        jsonify(message=f"Repertoire retrieved correctly.", data=moves, success=True),
        200,
    )


@repertoire_bp.route("/info", methods=["GET"])
def get_user_repertoire_info():
    user: User = user_service.get_user()

    info = repertoire_service.get_user_repertoire_info(user=user)

    return (
        jsonify(
            message=f"Repertoire info retrieved correctly.", data=info, success=True
        ),
        200,
    )


@repertoire_bp.route("", methods=["POST"])
def create_user_repertoire():
    body = request.json

    color = body.get("color").upper()
    if color not in ("WHITE", "BLACK"):
        raise InvalidRequestException(description="Invalid color provided")

    user: User = user_service.get_user()
    initial_position = position_service.retrieve_initial_position()
    repertoire_service.create_user_repertoire(position=initial_position, user=user, color=color == "WHITE")
    return jsonify(message=f"Repertoire created correctly.", data={}, success=True), 201


@repertoire_bp.route("", methods=["PUT"])
def edit_user_repertoire():
    user: User = user_service.get_user()
    args = get_request_arguments(request.args)

    moves = repertoire_service.update_user_repertoire(
        args["position"], user, args["color"], args["move"]
    )
    if len(moves) == 0:
        return (
            jsonify(
                message=f"Repertoire could not be updated. Try with another move.",
                data={},
                success=False,
            ),
            400,
        )
    moves = repertoire_service.get_repertoire_moves(
        args["position"], user, args["color"], args["depth"]
    )
    return (
        jsonify(
            message=f"Repertoire updated correctly after {args['position'].fen}.",
            data=moves,
            success=True,
        ),
        200,
    )


@repertoire_bp.route("/rival", methods=["PUT"])
def add_rival_move():
    user: User = user_service.get_user()
    args = get_request_arguments(request.args)

    if not args["move"]:
        raise InvalidRequestException(description="Please provide a rival move to add")

    moves = repertoire_service.add_rival_move_to_repertoire(
        args["position"], user, args["color"], args["move"]
    )

    return (
        jsonify(
            message=f"Repertoire updated correctly after {args['position'].fen}.",
            data=len(moves),
            success=True,
        ),
        201,
    )


@repertoire_bp.route("/rival", methods=["DELETE"])
def remove_rival_move():
    user: User = user_service.get_user()
    args = get_request_arguments(request.args)

    if not args["move"]:
        raise InvalidRequestException(
            description="Please provide a rival move to remove"
        )

    moves = repertoire_service.remove_rival_move_from_repertoire(
        args["position"], user, args["color"], args["move"]
    )

    return (
        jsonify(
            message=f"Move {args['move']} deleted correctly from user repertoire.",
            data=len(moves),
            success=True,
        ),
        200,
    )


@repertoire_bp.route("", methods=["PATCH"])
def add_variant_to_repertoire():
    user: User = user_service.get_user()
    args = get_request_arguments(request.args)
    repertoire_service.add_variant_to_repertoire(args["position"], user, args["color"])
    moves = repertoire_service.get_repertoire_moves(
        args["position"], user, args["color"], args["depth"]
    )
    return (
        jsonify(
            message=f"Variant added correctly after {args['position'].fen}.",
            data=moves,
            success=True,
        ),
        200,
    )
