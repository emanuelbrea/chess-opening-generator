from typing import List

import chess
from flask import request, jsonify, Blueprint, Response

from opening_generator.exceptions import InvalidRequestException
from opening_generator.models import Position
from opening_generator.services.position_service import position_service

pos_bp = Blueprint('position', __name__, url_prefix='/api/position')


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

    stats = position_service.get_position_stats(position=position)
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


@pos_bp.route('/svg', methods=["GET"])
def get_position_svg():
    args = request.args

    move_san = args.get('move')

    board: chess.Board = get_board_by_fen(args)

    position: Position = get_position_by_board(board)

    color = get_color(args=args)

    position_svg = position_service.get_position_svg(position=position, move=move_san, color=color)

    if not position_svg:
        return jsonify(message=f"Move {move_san} is not valid in this position.", data={}, success=False), 400

    return Response(position_svg, mimetype='image/svg+xml'), 200

