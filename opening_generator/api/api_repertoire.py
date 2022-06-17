from flask import Blueprint, jsonify, request

from opening_generator.models import User, Style
from opening_generator.services.opening_tree_service import opening_tree_service
from opening_generator.services.picker_service import picker_service

repertoire_bp = Blueprint('repertoire', __name__, url_prefix='/repertoire')

user = User(user_id=1, first_name='Emanuel', email='a', rating=1800)
style = Style(user_id=1, popularity=0, fashion=0, risk=0)
user.style = style


@repertoire_bp.route('/', methods=["GET"])
def get_user_repertoire():
    args = request.args

    moves = args.get('moves')

    moves = moves.split(",")

    repertoire = []
    return jsonify(message=f"Repertoire retrieved correctly.", data=repertoire, success=True), 200


@repertoire_bp.route('/', methods=["POST"])
def create_user_repertoire():
    variation = opening_tree_service.get_variation([])
    lines = picker_service.pick_variation(color=True, depth=5, user=user, current_position=variation)
    # repertoire = Repertoire(color=True, user=user)
    # db_session.add(repertoire)
    # db_session.commit()
    return jsonify(message=f"Repertoire created correctly.", data=len(lines), success=True), 200
