from typing import List

import chess
from flask import request, abort, jsonify, Blueprint

from opening_generator.models import User, Style, NextLine
from opening_generator.models.line import Line
from opening_generator.services.line_service import line_service
from opening_generator.services.pgn_service import pgn_service
from opening_generator.services.picker_service import picker_service

pos = Blueprint('position', __name__, url_prefix='/position')

user = User(user_id=1, first_name='Emanuel', email='a', rating=1800)
style = Style(user_id=1, popularity=0, fashion=0, risk=0)
user.style = style


def get_board_by_fen(args):
    fen: str = args.get("fen")
    if not fen:
        abort(400, description="Fen not provided")
    try:
        board: chess.Board = chess.Board(fen)
    except ValueError:
        abort(400, description="Invalid FEN provided")
    return board


def get_position_by_board(board: chess.Board):
    position: Line = line_service.get_line(board=board)
    if not position:
        abort(404, description="Position not found in database")
    return position


@pos.route('/lines', methods=["GET"])
def get_variations():
    args = request.args

    board: chess.Board = get_board_by_fen(args)

    position: Line = get_position_by_board(board)

    color = args.get("color", "WHITE").upper() == "WHITE"

    variations = picker_service.pick_variations(board=board, current_position=position, color=color, user=user)
    return jsonify(message="Variations calculated correctly.", data=variations, success=True), 200


@pos.route('/stats', methods=["GET"])
def get_stats():
    args = request.args

    board: chess.Board = get_board_by_fen(args)

    position: Line = get_position_by_board(board)

    stats = dict(total_games=position.total_games,
                 white_wins=position.white_wins,
                 black_wins=position.black_wins,
                 draws=position.draws,
                 year=position.average_year,
                 average_elo=position.average_elo)

    return jsonify(message="Stats retrieved correctly.", data=stats, success=True), 200


@pos.route('/moves', methods=["GET"])
def get_moves():
    args = request.args

    board: chess.Board = get_board_by_fen(args)

    position: Line = get_position_by_board(board)

    next_moves: List[str] = line_service.get_next_moves_as_san(line=position, board=board)

    return jsonify(message="Next moves retrieved correctly.", data=next_moves, success=True), 200


@pos.route('/moves/stats', methods=["GET"])
def get_next_moves_stats():
    args = request.args

    board: chess.Board = get_board_by_fen(args)

    position: Line = get_position_by_board(board)

    next_moves: List[NextLine] = position.next_moves

    moves_stats = {}

    for move in next_moves:
        position: Line = line_service.get_line_by_id(line_id=move.next_line_id)
        moves_stats[move.move] = dict(total_games=position.total_games,
                                      white_wins=position.white_wins,
                                      black_wins=position.black_wins,
                                      draws=position.draws,
                                      year=position.average_year,
                                      average_elo=position.average_elo)

    return jsonify(message="Next moves stats retrieved correctly.", data=moves_stats, success=True), 200


@pos.route('/games', methods=["POST"])
def load_games():
    games = pgn_service.load_games()
    lines = line_service.save_lines(games)
    return jsonify(message=f"Loaded positions correctly.", data=dict(total=len(lines)), success=True), 200
