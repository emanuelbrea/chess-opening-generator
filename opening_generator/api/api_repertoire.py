import chess
from flask import Blueprint, jsonify, request

from opening_generator.api.api_position import get_board_by_fen, get_position_by_board, get_color
from opening_generator.db import db_session
from opening_generator.exceptions import InvalidRequestException
from opening_generator.models import User, Position
from opening_generator.services.position_service import position_service
from opening_generator.services.repertoire_service import repertoire_service

repertoire_bp = Blueprint('repertoire', __name__, url_prefix='/repertoire')


@repertoire_bp.route('/', methods=["GET"])
def get_user_repertoire():
    args = request.args
    board: chess.Board = get_board_by_fen(args)
    color = get_color(args)

    user = db_session.query(User).first()
    position: Position = get_position_by_board(board)

    moves = repertoire_service.get_repertoire_moves(position, user, color)
    return jsonify(message=f"Repertoire retrieved correctly.", data=moves, success=True), 200


@repertoire_bp.route('/', methods=["POST"])
def create_user_repertoire():
    initial_position = position_service.retrieve_initial_position()
    user = db_session.query(User).first()
    repertoire_service.create_user_repertoire(position=initial_position, user=user)
    return jsonify(message=f"Repertoire created correctly.", data={}, success=True), 201


@repertoire_bp.route('/', methods=["PUT"])
def edit_user_repertoire():
    args = request.args
    new_move: str = args.get('new_move')

    board: chess.Board = get_board_by_fen(args)
    user = db_session.query(User).first()
    position: Position = get_position_by_board(board)

    color = get_color(args=args)

    moves = repertoire_service.update_user_repertoire(position, user, color, new_move)
    if len(moves) == 0:
        return jsonify(message=f"Repertoire could not be updated. Try with another move.",
                       data={}, success=False), 400
    return jsonify(message=f"Repertoire updated correctly after {position.fen}.",
                   data=len(moves), success=True), 200


@repertoire_bp.route('/rival', methods=["PUT"])
def add_rival_move():
    args = request.args
    move: str = args.get('move')

    if not move:
        raise InvalidRequestException(description="Please provide a rival move to add")

    board: chess.Board = get_board_by_fen(args)
    user = db_session.query(User).first()
    position: Position = get_position_by_board(board)

    color = get_color(args=args)

    moves = repertoire_service.add_rival_move_to_repertoire(position, user, color, move)

    return jsonify(message=f"Repertoire updated correctly after {position.fen}.",
                   data=len(moves), success=True), 201


@repertoire_bp.route('/rival', methods=["DELETE"])
def remove_rival_move():
    args = request.args
    move: str = args.get('move')

    if not move:
        raise InvalidRequestException(description="Please provide a rival move to remove")

    board: chess.Board = get_board_by_fen(args)
    user = db_session.query(User).first()
    position: Position = get_position_by_board(board)

    color = get_color(args=args)

    moves = repertoire_service.remove_rival_move_from_repertoire(position, user, color, move)

    return jsonify(message=f"Move {move} deleted correctly from user repertoire.",
                   data=len(moves), success=True), 200
