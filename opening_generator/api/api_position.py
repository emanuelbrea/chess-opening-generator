from typing import List

import chess
from flask import request, abort, jsonify, Blueprint

from opening_generator.db import eco_code_dao
from opening_generator.db.line_dao import line_dao
from opening_generator.models.line import Line
from opening_generator.services.eco_code_service import eco_service
from opening_generator.services.line_service import line_service
from opening_generator.services.pgn_service import pgn_service

pos = Blueprint('position', __name__, url_prefix='/position')


# @pos.route('/lines', methods=["GET"])
# def get_variations():
#     args = request.args
#
#     fen: str = args.get("fen")
#     if not fen:
#         abort(400, description="Fen not provided")
#
#     try:
#         board = chess.Board(fen)
#     except ValueError:
#         abort(400, description="Invalid FEN provided")
#
#     depth = int(args.get("depth", 3))
#     color = args.get("color", "WHITE").upper() == "WHITE"
#
#     pgn = Pgn.get_instance()
#     position= pgn.load_position_from_book(board=board)
#
#     if not position:
#         abort(404, description="Position not found in database")
#
#     picker = Picker(pgn)
#     variations = picker.pick_variations(board=board, current_position=position, color=color, depth=depth)
#     return jsonify(message="Variations calculated correctly.", data=variations, success=True), 200


@pos.route('/stats', methods=["GET"])
def get_stats():
    args = request.args

    fen = args.get("fen")
    if not fen:
        abort(400, description="Fen not provided")

    try:
        chess.Board(fen)
    except ValueError:
        abort(400, description="Invalid FEN provided")

    position: Line = line_dao.get_line_by_position(fen=fen)
    if not position:
        abort(404, description="Position not found in database")

    stats = dict(total_games=position.total_games,
                 white_wins=position.white_wins,
                 black_wins=position.black_wins,
                 draws=position.draws,
                 year=position.last_year,
                 average_elo=position.average_elo)

    return jsonify(message="Stats retrieved correctly.", data=stats, success=True), 200


@pos.route('/moves', methods=["GET"])
def get_moves():
    args = request.args

    fen = args.get("fen")
    if not fen:
        abort(400, description="Fen not provided")

    try:
        chess.Board(fen=fen)
    except ValueError:
        abort(400, description="Invalid FEN provided")

    position: Line = line_dao.get_line_by_position(fen=fen)

    if not position:
        abort(404, description="Position not found in database")

    next_moves: List[str] = line_service.get_next_moves(line=position)

    return jsonify(message="Next moves retrieved correctly.", data=next_moves, success=True), 200


@pos.route('/moves/stats', methods=["GET"])
def get_next_moves_stats():
    args = request.args

    fen = args.get("fen")
    if not fen:
        abort(400, description="Fen not provided")

    try:
        board = chess.Board(fen=fen)
    except ValueError:
        abort(400, description="Invalid FEN provided")

    position: Line = line_dao.get_line_by_position(fen=fen)

    if not position:
        abort(404, description="Position not found in database")

    next_moves: List[str] = line_service.get_next_moves(line=position)

    moves_stats = {}

    for move in next_moves:
        board.push_san(san=move)
        position: Line = line_dao.get_line_by_position(fen=board.fen())
        moves_stats[move] = dict(total_games=position.total_games,
                                 white_wins=position.white_wins,
                                 black_wins=position.black_wins,
                                 draws=position.draws,
                                 year=position.last_year,
                                 average_elo=position.average_elo)

        board.pop()

    return jsonify(message="Next moves stats retrieved correctly.", data=moves_stats, success=True), 200


@pos.route('/games', methods=["POST"])
def load_games():
    games = pgn_service.load_games()
    line_dao.save_lines(games)
    return jsonify(message=f"Loaded {len(games)} positions correctly.", data={}, success=True), 200


@pos.route('/eco', methods=["POST"])
def load_eco_codes():
    eco_codes = eco_service.load_eco_codes()
    eco_code_dao.add_eco_codes(ecos=eco_codes)
    return jsonify(message=f"Loaded {len(eco_codes)} eco codes correctly.", data={}, success=True), 200
