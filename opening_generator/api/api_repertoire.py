import chess
from flask import Blueprint, jsonify, request, abort

from opening_generator import Position
from opening_generator.api.api_position import get_board_by_fen, get_position_by_board
from opening_generator.db import db_session
from opening_generator.db.repertoire_dao import repertoire_dao
from opening_generator.models import User
from opening_generator.services.picker_service import picker_service
from opening_generator.services.position_service import position_service
from opening_generator.services.repertoire_service import repertoire_service

repertoire_bp = Blueprint('repertoire', __name__, url_prefix='/repertoire')


@repertoire_bp.route('/', methods=["GET"])
def get_user_repertoire():
    args = request.args
    board: chess.Board = get_board_by_fen(args)
    user = db_session.query(User).first()
    position: Position = get_position_by_board(board)

    color = args.get("color", "WHITE").upper()
    color = color == "WHITE"

    moves = repertoire_service.get_repertoire_moves(position, user, color)
    return jsonify(message=f"Repertoire retrieved correctly.", data=moves, success=True), 200


@repertoire_bp.route('/', methods=["POST"])
def create_user_repertoire():
    initial_position = position_service.retrieve_initial_position()
    user = db_session.query(User).first()
    moves = picker_service.pick_variations(initial_position, user, True)
    repertoire_dao.create_repertoire(user=user, color=True, moves=moves)
    moves = picker_service.pick_variations(initial_position, user, False)
    repertoire_dao.create_repertoire(user=user, color=False, moves=moves)
    return jsonify(message=f"Repertoire created correctly.", data=len(moves), success=True), 200
