from flask import jsonify, Blueprint, request

from opening_generator.models import User, Style
from opening_generator.services.opening_tree_service import opening_tree_service

move_bp = Blueprint('move', __name__, url_prefix='/move')

user = User(user_id=1, first_name='Emanuel', email='a', rating=1800)
style = Style(user_id=1, popularity=0, fashion=0, risk=0)
user.style = style


@move_bp.route('/', methods=["GET"])
def get_variant():
    args = request.args

    moves = args.get('moves')

    moves = moves.split(",")
    position = opening_tree_service.get_variation(moves)

    stats = dict(total_games=position.total_games,
                 white_wins=position.white_wins,
                 black_wins=position.black_wins,
                 draws=position.draws,
                 year=position.average_year,
                 average_elo=position.average_elo)

    return jsonify(message=f"Loaded position correctly.", data=stats, success=True), 200


@move_bp.route('/next', methods=["GET"])
def get_next_moves():
    args = request.args

    moves = args.get('moves')

    moves = moves.split(",")
    position = opening_tree_service.get_variation(moves)
    result = []
    for move in position.next_moves:
        result.append(move.move)

    return jsonify(message=f"Next moves retrieved correctly.", data=result, success=True), 200


@move_bp.route('/next/stats', methods=["GET"])
def get_next_stats():
    args = request.args

    moves = args.get('moves')

    moves = moves.split(",")
    position = opening_tree_service.get_variation(moves)
    result = {}
    for move in position.next_moves:
        result[move.move] = dict(total_games=move.total_games,
                                 white_wins=move.white_wins,
                                 black_wins=move.black_wins,
                                 draws=move.draws,
                                 year=move.average_year,
                                 average_elo=move.average_elo)

    return jsonify(message=f"Next moves stats retrieved correctly.", data=result, success=True), 200
