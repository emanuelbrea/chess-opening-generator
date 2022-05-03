from typing import List

import chess
from flask import request, abort, jsonify, Blueprint

from opening_generator.pgn import Pgn
from opening_generator.picker import Picker
from opening_generator.position import Position

pos = Blueprint('position', __name__, url_prefix='/position')


@pos.route('/lines', methods=["GET"])
def get_variations():
    args = request.args

    fen: str = args.get("fen")
    if not fen:
        abort(400, description="Fen not provided")

    try:
        board = chess.Board(fen)
    except ValueError:
        abort(400, description="Invalid FEN provided")

    depth = int(args.get("depth", 3))
    color = args.get("color", "WHITE").upper() == "WHITE"

    pgn = Pgn.get_instance()
    position: Position = pgn.load_position_from_book(board=board)

    if not position:
        abort(404, description="Position not found in database")

    picker = Picker(pgn)
    variations = picker.pick_variations(board=board, current_position=position, color=color, depth=depth)
    return jsonify(message="Variations calculated correctly.", data=variations, success=True), 200


@pos.route('/stats', methods=["GET"])
def get_stats():
    args = request.args

    fen = args.get("fen")
    if not fen:
        abort(400, description="Fen not provided")

    try:
        board = chess.Board(fen)
    except ValueError:
        abort(400, description="Invalid FEN provided")

    pgn = Pgn.get_instance()
    position: Position = pgn.load_position_from_book(board=board)
    if not position:
        abort(404, description="Position not found in database")

    moves: List[chess.Move] = position.next_moves
    stats = {}
    for move in moves:
        board.push(move)
        position: Position = pgn.load_position_from_book(board=board)
        board.pop()
        stats[board.san(move)] = {
            'games': position.total_games,
            'score': position.white_percentage_win,
            'average_rating': position.elo,
            'last_played': position.year
        }

    return jsonify(message="Stats retrieved correctly.", data=stats, success=True), 200
