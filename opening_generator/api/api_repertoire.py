import chess
from flask import Blueprint, jsonify, request

from opening_generator.api.api_position import get_board_by_fen, get_position_by_board, get_color
from opening_generator.db import db_session
from opening_generator.exceptions import InvalidRequestException
from opening_generator.models import User, Position
from opening_generator.services.position_service import position_service
from opening_generator.services.repertoire_service import repertoire_service
from opening_generator.services.auth_service import auth_service

repertoire_bp = Blueprint('repertoire', __name__, url_prefix='/api/repertoire')


def get_request_arguments(args):
    move: str = args.get('move')

    board: chess.Board = get_board_by_fen(args)
    user = db_session.query(User).first()
    position: Position = get_position_by_board(board)

    color = get_color(args=args)

    return dict(move=move, color=color, position=position, user=user, depth=board.fullmove_number)


@repertoire_bp.route('/', methods=["GET"])
def get_user_repertoire():
    claims = auth_service.get_user_claims(request.headers.get('Authorization'))
    args = get_request_arguments(request.args)

    moves = repertoire_service.get_repertoire_moves(args['position'], args['user'], args['color'], args['depth'])
    return jsonify(message=f"Repertoire retrieved correctly.", data=moves, success=True), 200


@repertoire_bp.route('/', methods=["POST"])
def create_user_repertoire():
    initial_position = position_service.retrieve_initial_position()
    user = db_session.query(User).first()
    repertoire_service.create_user_repertoire(position=initial_position, user=user)
    return jsonify(message=f"Repertoire created correctly.", data={}, success=True), 201


@repertoire_bp.route('/', methods=["PUT"])
def edit_user_repertoire():
    args = get_request_arguments(request.args)

    moves = repertoire_service.update_user_repertoire(args['position'], args['user'], args['color'], args['move'])
    if len(moves) == 0:
        return jsonify(message=f"Repertoire could not be updated. Try with another move.",
                       data={}, success=False), 400
    moves = repertoire_service.get_repertoire_moves(args['position'], args['user'], args['color'], args['depth'])
    return jsonify(message=f"Repertoire updated correctly after {args['position'].fen}.",
                   data=moves, success=True), 200


@repertoire_bp.route('/rival', methods=["PUT"])
def add_rival_move():
    args = get_request_arguments(request.args)

    if not args['move']:
        raise InvalidRequestException(description="Please provide a rival move to add")

    moves = repertoire_service.add_rival_move_to_repertoire(args['position'], args['user'], args['color'], args['move'])

    return jsonify(message=f"Repertoire updated correctly after {args['position'].fen}.",
                   data=len(moves), success=True), 201


@repertoire_bp.route('/rival', methods=["DELETE"])
def remove_rival_move():
    args = get_request_arguments(request.args)

    if not args['move']:
        raise InvalidRequestException(description="Please provide a rival move to remove")

    moves = repertoire_service.remove_rival_move_from_repertoire(args['position'], args['user'], args['color'],
                                                                 args['move'])

    return jsonify(message=f"Move {args['move']} deleted correctly from user repertoire.",
                   data=len(moves), success=True), 200


@repertoire_bp.route('/', methods=["PATCH"])
def add_variant_to_repertoire():
    args = get_request_arguments(request.args)
    repertoire_service.add_variant_to_repertoire(args['position'], args['user'], args['color'])
    moves = repertoire_service.get_repertoire_moves(args['position'], args['user'], args['color'], args['depth'])
    return jsonify(message=f"Variant added correctly after {args['position'].fen}.",
                   data=moves, success=True), 200
