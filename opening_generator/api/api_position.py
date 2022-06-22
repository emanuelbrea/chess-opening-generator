from typing import List

import chess
from flask import request, jsonify, Blueprint

from opening_generator.exceptions import InvalidRequestException
from opening_generator.models import Position
from opening_generator.services.position_service import position_service

pos_bp = Blueprint('position', __name__, url_prefix='/position')


def get_board_by_fen(args):
    fen: str = args.get("fen")
    if not fen:
        raise InvalidRequestException(description="FEN not provided")
    try:
        board: chess.Board = chess.Board(fen)
        return board
    except ValueError:
        raise InvalidRequestException(description="Invalid FEN provided")


def get_position_by_board(board: chess.Board):
    position: Position = position_service.get_position(board=board)
    if not position:
        raise InvalidRequestException(description="Position not found in database")
    return position


def get_color(args):
    color = args.get("color", "WHITE").upper()
    if color not in ("WHITE", "BLACK"):
        raise InvalidRequestException(description="Invalid color provided")
    return color == "WHITE"


@pos_bp.route('/stats', methods=["GET"])
def get_stats():
    args = request.args

    board: chess.Board = get_board_by_fen(args)

    position: Position = get_position_by_board(board)

    stats = dict(total_games=position.total_games,
                 white_wins=position.white_wins,
                 black_wins=position.black_wins,
                 draws=position.draws,
                 year=position.average_year,
                 average_elo=position.average_elo)
    return jsonify(message="Stats retrieved correctly.", data=stats, success=True), 200


@pos_bp.route('/moves', methods=["GET"])
def get_moves():
    args = request.args

    board: chess.Board = get_board_by_fen(args)

    position: Position = get_position_by_board(board)

    next_moves: List[str] = position_service.get_next_moves(position=position)

    return jsonify(message="Next moves retrieved correctly.", data=next_moves, success=True), 200


@pos_bp.route('/moves/stats', methods=["GET"])
def get_next_moves_stats():
    args = request.args

    board: chess.Board = get_board_by_fen(args)

    position: Position = get_position_by_board(board)

    moves_stats = position_service.get_next_moves_stats(position=position)

    return jsonify(message="Next moves stats retrieved correctly.", data=moves_stats, success=True), 200
