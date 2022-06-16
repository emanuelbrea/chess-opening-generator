from flask import jsonify, Blueprint, request

from opening_generator.models import User, Style
from opening_generator.services.opening_tree_service import OpeningTreeService

move_bp = Blueprint('move', __name__, url_prefix='/move')

user = User(user_id=1, first_name='Emanuel', email='a', rating=1800)
style = Style(user_id=1, popularity=0, fashion=0, risk=0)
user.style = style


@move_bp.route('/', methods=["GET"])
def get_variant():
    args = request.args

    moves = args.get('moves')

    moves = moves.split(",")
    opening_tree = OpeningTreeService()
    position = opening_tree.get_variation(moves)

    stats = dict(total_games=position.total_games,
                 white_wins=position.white_wins,
                 black_wins=position.black_wins,
                 draws=position.draws,
                 year=position.average_year,
                 average_elo=position.average_elo)

    return jsonify(message=f"Loaded positions correctly.", data=stats, success=True), 200
