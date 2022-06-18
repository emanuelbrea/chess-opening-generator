from flask import Blueprint, jsonify, request

from opening_generator.db import db_session
from opening_generator.db.repertoire_dao import repertoire_dao
from opening_generator.models import User
from opening_generator.services.picker_service import picker_service
from opening_generator.services.position_service import position_service

repertoire_bp = Blueprint('repertoire', __name__, url_prefix='/repertoire')


@repertoire_bp.route('/', methods=["GET"])
def get_user_repertoire():
    args = request.args

    repertoire = []
    return jsonify(message=f"Repertoire retrieved correctly.", data=repertoire, success=True), 200


@repertoire_bp.route('/', methods=["POST"])
def create_user_repertoire():
    initial_position = position_service.retrieve_initial_position()
    user = db_session.query(User).first()
    moves = picker_service.pick_variations(initial_position, user, True)
    repertoire_dao.create_repertoire(user=user, color=True, moves=moves)
    moves = picker_service.pick_variations(initial_position, user, False)
    repertoire_dao.create_repertoire(user=user, color=False, moves=moves)
    return jsonify(message=f"Repertoire created correctly.", data=len(moves), success=True), 200
